// nvazen_sysinfo.cpp — NVazen/Azen TUI 系统信息面板
// 编译: g++ -std=c++17 -O2 -o nvazen_sysinfo nvazen_sysinfo.cpp -lncursesw
// 运行: ./nvazen_sysinfo   (按 q 退出)

#include <ncurses.h>

#include <clocale>
#include <cstring>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

#include <sys/statvfs.h>   // statvfs  — 硬盘
#include <sys/utsname.h>   // uname    — 内核
#include <unistd.h>        // sysconf / _SC_NPROCESSORS_ONLN / gethostname

// ─────────────────────────────────────────────────────────
//  分区一：sysinfo —— 只负责取数据，不碰任何界面
// ─────────────────────────────────────────────────────────
namespace sysinfo {

// 读取整个文件，失败返回空串
static std::string readFile(const std::string& path) {
    std::ifstream f(path);
    if (!f.is_open()) return "";
    std::stringstream ss;
    ss << f.rdbuf();
    return ss.str();
}

// 去掉首尾空白
static std::string trim(const std::string& s) {
    size_t b = s.find_first_not_of(" \t\r\n");
    if (b == std::string::npos) return "";
    size_t e = s.find_last_not_of(" \t\r\n");
    return s.substr(b, e - b + 1);
}

// 千位分隔符：1024 → 1,024
static std::string withCommas(long long v) {
    std::string s = std::to_string(v < 0 ? -v : v);
    std::string out;
    int cnt = 0;
    for (int i = (int)s.size() - 1; i >= 0; --i) {
        out.push_back(s[i]);
        if (++cnt % 3 == 0 && i != 0) out.push_back(',');
    }
    if (v < 0) out.push_back('-');
    std::reverse(out.begin(), out.end());
    return out;
}

// ── OS ────────────────────────────────────────────────
// 从 /etc/os-release 取 PRETTY_NAME，取不到退回 "Linux"
static std::string osName() {
    std::string data = readFile("/etc/os-release");
    if (data.empty()) return "Linux";
    std::istringstream iss(data);
    std::string line;
    while (std::getline(iss, line)) {
        if (line.rfind("PRETTY_NAME=", 0) == 0) {
            std::string v = line.substr(12);
            // 去掉包裹的引号
            if (!v.empty() && (v.front() == '"' || v.front() == '\''))
                v.erase(0, 1);
            if (!v.empty() && (v.back() == '"' || v.back() == '\''))
                v.pop_back();
            return trim(v);
        }
    }
    return "Linux";
}

// ── CPU 型号 ──────────────────────────────────────────
// 扫 /proc/cpuinfo 的 "model name"（x86）或 "Hardware"（ARM）
static std::string cpuModel() {
    std::string data = readFile("/proc/cpuinfo");
    if (data.empty()) return "Unknown";
    std::istringstream iss(data);
    std::string line;
    while (std::getline(iss, line)) {
        if (line.rfind("model name", 0) == 0 || line.rfind("Hardware", 0) == 0) {
            size_t colon = line.find(':');
            if (colon != std::string::npos)
                return trim(line.substr(colon + 1));
        }
    }
    return "Unknown";
}

// ── CPU 核心数 ────────────────────────────────────────
static int cpuCores() {
    long n = sysconf(_SC_NPROCESSORS_ONLN);
    return (n > 0) ? (int)n : 1;
}

// ── 内存 ──────────────────────────────────────────────
// 返回 {总量MiB, 已用MiB}
static void memInfo(long long& totalMiB, long long& usedMiB) {
    totalMiB = usedMiB = 0;
    std::string data = readFile("/proc/meminfo");
    if (data.empty()) return;
    long long total = 0, avail = 0;
    std::istringstream iss(data);
    std::string line;
    while (std::getline(iss, line)) {
        if (line.rfind("MemTotal:", 0) == 0) {
            std::sscanf(line.c_str(), "MemTotal: %lld kB", &total);
        } else if (line.rfind("MemAvailable:", 0) == 0) {
            std::sscanf(line.c_str(), "MemAvailable: %lld kB", &avail);
        }
    }
    totalMiB = total / 1024;
    usedMiB  = (total - avail) / 1024;
}

// ── 硬盘（根分区）────────────────────────────────────
// 返回 {总量GiB, 已用GiB, 使用百分比}
struct DiskInfo { long long totalGiB; long long usedGiB; int percent; };
static DiskInfo diskInfo() {
    DiskInfo d{0, 0, 0};
    struct statvfs st;
    if (statvfs("/", &st) != 0) return d;
    unsigned long long bsize = st.f_frsize ? st.f_frsize : st.f_bsize;
    unsigned long long total = bsize * st.f_blocks;
    unsigned long long avail = bsize * st.f_bavail;
    unsigned long long used  = total - (bsize * st.f_bfree);
    d.totalGiB = (long long)(total / (1024ULL * 1024 * 1024));
    d.usedGiB  = (long long)(used  / (1024ULL * 1024 * 1024));
    d.percent  = total ? (int)(used * 100 / total) : 0;
    return d;
}

// ── 内核版本 ──────────────────────────────────────────
static std::string kernelVersion() {
    struct utsname u;
    if (uname(&u) != 0) return "Unknown";
    return std::string(u.release);
}

// ── 桌面环境 ──────────────────────────────────────────
static std::string desktopEnv() {
    const char* de = std::getenv("XDG_CURRENT_DESKTOP");
    if (de && *de) return de;
    const char* ds = std::getenv("DESKTOP_SESSION");
    if (ds && *ds) return ds;
    return "None (CLI)";
}

// ── 主机名 ────────────────────────────────────────────
static std::string hostName() {
    char buf[256] = {0};
    if (gethostname(buf, sizeof(buf) - 1) != 0) return "Unknown";
    buf[sizeof(buf) - 1] = '\0';
    return std::string(buf);
}

} // namespace sysinfo

// ─────────────────────────────────────────────────────────
//  分区二：ui —— 只负责画界面，不取任何数据
// ─────────────────────────────────────────────────────────
namespace ui {

// 画圆角框（直接画在 stdscr 上，不用子窗口）
static void roundedBox(int y, int x, int h, int w) {
    if (h < 2 || w < 2) return;
    // 四角
    mvaddch(y,         x,         ACS_ULCORNER);
    mvaddch(y,         x + w - 1, ACS_URCORNER);
    mvaddch(y + h - 1, x,         ACS_LLCORNER);
    mvaddch(y + h - 1, x + w - 1, ACS_LRCORNER);
    // 上下横边
    mvhline(y,         x + 1, ACS_HLINE, w - 2);
    mvhline(y + h - 1, x + 1, ACS_HLINE, w - 2);
    // 左右竖边
    mvvline(y + 1, x,         ACS_VLINE, h - 2);
    mvvline(y + 1, x + w - 1, ACS_VLINE, h - 2);
}

// 在框内某行写一行 "标签: 值"，标签加粗高亮
static void row(int y, int x, int innerW,
                const std::string& label, const std::string& value) {
    int labelW = 12;                       // 标签列宽
    attron(A_BOLD | COLOR_PAIR(1));
    mvprintw(y, x + 2, "%-*s", labelW, (label + ":").c_str());
    attroff(A_BOLD | COLOR_PAIR(1));

    std::string v = value;
    int maxV = innerW - labelW - 4;
    if (maxV < 1) maxV = 1;
    if ((int)v.size() > maxV) v = v.substr(0, maxV - 1) + "…";
    mvprintw(y, x + 2 + labelW, "%s", v.c_str());
}

// 进度条： [████████░░░░░░░░] 47%
static void bar(int y, int x, int width, int percent) {
    if (percent < 0)   percent = 0;
    if (percent > 100) percent = 100;
    int inner = width - 2;
    if (inner < 4) inner = 4;
    int filled = inner * percent / 100;

    attron(COLOR_PAIR(2));
    mvaddch(y, x, '[');
    for (int i = 0; i < inner; ++i)
        addch(i < filled ? ACS_CKBOARD : ' ');
    addch(']');
    attroff(COLOR_PAIR(2));

    attron(A_BOLD);
    mvprintw(y, x + width + 2, "%3d%%", percent);
    attroff(A_BOLD);
}

// 整体绘制：每次调用前先清屏，全部画完统一 refresh
static void draw() {
    erase();
    int rows, cols;
    getmaxyx(stdscr, rows, cols);

    // ── 终端太小，直接提示 ──
    if (rows < 14 || cols < 46) {
        mvprintw(0, 0, "Terminal too small (%dx%d). Need at least 46x14.", cols, rows);
        mvprintw(2, 0, "Press q to quit.");
        refresh();
        return;
    }

    // ── 标题 ──
    std::string title = " NVazen · System Info ";
    attron(A_BOLD | COLOR_PAIR(1));
    mvprintw(0, (cols - (int)title.size()) / 2, "%s", title.c_str());
    attroff(A_BOLD | COLOR_PAIR(1));

    // ── 采集数据 ──
    long long memTotal = 0, memUsed = 0;
    sysinfo::memInfo(memTotal, memUsed);
    sysinfo::DiskInfo disk = sysinfo::diskInfo();

    // ── 框尺寸：宽度自适应，最大 60 ──
    int boxW = cols - 6;
    if (boxW > 60) boxW = 60;
    if (boxW < 40) boxW = cols - 2;
    int innerW = boxW - 4;
    int boxX = (cols - boxW) / 2;
    int boxY = 2;

    // 行数：标题1 + 边框2 + 内容行数
    int contentRows = 10;
    int boxH = contentRows + 2;

    roundedBox(boxY, boxX, boxH, boxW);

    int y = boxY + 1;
    int x = boxX;

    row(y++, x, innerW, "Host",    sysinfo::hostName());
    row(y++, x, innerW, "OS",      sysinfo::osName());
    row(y++, x, innerW, "Kernel",  sysinfo::kernelVersion());
    row(y++, x, innerW, "Desktop", sysinfo::desktopEnv());

    std::string cpu = sysinfo::cpuModel();
    cpu += " (" + std::to_string(sysinfo::cpuCores()) + " cores)";
    row(y++, x, innerW, "CPU", cpu);

    // 内存 + 条
    {
        int pct = memTotal ? (int)(memUsed * 100 / memTotal) : 0;
        std::string v = sysinfo::withCommas(memUsed) + " / " +
                        sysinfo::withCommas(memTotal) + " MiB";
        row(y++, x, innerW, "Memory", v);
        bar(y, x + 2, innerW - 10, pct);
        y++;
    }

    // 硬盘 + 条
    {
        std::string v = sysinfo::withCommas(disk.usedGiB) + " / " +
                        sysinfo::withCommas(disk.totalGiB) + " GiB";
        row(y++, x, innerW, "Disk (/)", v);
        bar(y, x + 2, innerW - 10, disk.percent);
        y++;
    }

    // ── 底部提示 ──
    attron(A_DIM);
    mvprintw(rows - 1, 2, "q: quit   r: refresh");
    attroff(A_DIM);

    refresh();
}

} // namespace ui

// ─────────────────────────────────────────────────────────
//  main
// ─────────────────────────────────────────────────────────
int main() {
    // 让宽字符 / UTF-8 正常显示
    setlocale(LC_ALL, "");

    // TERM=dumb 之类不支持光标移动的终端，直接退出
    const char* term = std::getenv("TERM");
    if (term && std::strcmp(term, "dumb") == 0) {
        std::fprintf(stderr, "TERM=dumb is not supported. Try: export TERM=xterm-256color\n");
        return 1;
    }

    initscr();
    if (!has_colors()) {
        endwin();
        std::fprintf(stderr, "This terminal does not support colors.\n");
        return 1;
    }

    cbreak();
    noecho();
    keypad(stdscr, TRUE);
    curs_set(0);          // 隐藏光标

    start_color();
    use_default_colors();
    init_pair(1, COLOR_CYAN,  -1);   // 标题 / 标签
    init_pair(2, COLOR_GREEN, -1);   // 进度条

    ui::draw();

    // 主循环：按键 → 需要时重画
    bool running = true;
    while (running) {
        int ch = getch();
        switch (ch) {
            case 'q':
            case 'Q':
                running = false;
                break;
            case 'r':
            case 'R':
            case KEY_RESIZE:      // 终端尺寸变化 → 重画
                ui::draw();
                break;
            default:
                break;
        }
    }

    endwin();
    return 0;
}
