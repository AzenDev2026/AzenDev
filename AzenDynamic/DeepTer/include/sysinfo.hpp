#pragma once
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
#include <array>
#include <memory>
#include <cstdio>
#include <unistd.h>
#include <pwd.h>
#include <sys/utsname.h>
#include <sys/statvfs.h>
#include <ifaddrs.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <chrono>
#include <thread>

namespace deepter {

// ── 工具：字节转人类可读 ─────────────────────────────────
inline std::string bytes_to_human(double b) {
    const char* units[] = {"B", "KB", "MB", "GB", "TB", "PB"};
    int i = 0;
    while (b >= 1024.0 && i < 5) { b /= 1024.0; ++i; }
    std::ostringstream oss;
    oss.precision(1);
    oss << std::fixed << b << " " << units[i];
    return oss.str();
}

// ── 工具：去掉首尾空白 ───────────────────────────────────
inline std::string shell_trim(const std::string& s) {
    const char* ws = " \t\r\n";
    size_t b = s.find_first_not_of(ws);
    if (b == std::string::npos) return "";
    size_t e = s.find_last_not_of(ws);
    return s.substr(b, e - b + 1);
}

// ── 工具：执行命令取输出（popen）─────────────────────────
inline std::string run_pipe(const std::string& cmd) {
    std::string result;
    std::unique_ptr<FILE, int(*)(FILE*)> pipe(popen((cmd + " 2>/dev/null").c_str(), "r"), pclose);
    if (!pipe) return "";
    std::array<char, 256> buf{};
    while (fgets(buf.data(), buf.size(), pipe.get())) result += buf.data();
    return shell_trim(result);
}

// ── OS ───────────────────────────────────────────────────
inline std::string os_name() {
    std::ifstream f("/etc/os-release");
    std::string line;
    while (std::getline(f, line)) {
        if (line.rfind("PRETTY_NAME=", 0) == 0) {
            std::string v = line.substr(12);
            if (!v.empty() && v.front() == '"') v.erase(0, 1);
            if (!v.empty() && v.back()  == '"') v.pop_back();
            return v;
        }
    }
    struct utsname u{};
    if (uname(&u) == 0) return std::string(u.sysname);
    return "Unknown";
}

inline std::string kernel_version() {
    struct utsname u{};
    if (uname(&u) == 0) return std::string(u.release);
    return "Unknown";
}

inline std::string arch_name() {
    struct utsname u{};
    if (uname(&u) == 0) return std::string(u.machine);
    return "Unknown";
}

inline std::string uptime_str() {
    std::ifstream f("/proc/uptime");
    double sec = 0.0;
    if (f >> sec) {
        long total = static_cast<long>(sec);
        long days  = total / 86400;
        long hours = (total % 86400) / 3600;
        long mins  = (total % 3600) / 60;
        std::ostringstream oss;
        oss << days << " days, " << hours << " hours, " << mins << " minutes";
        return oss.str();
    }
    return "Unknown";
}

// ── CPU ──────────────────────────────────────────────────
inline std::string cpu_name() {
    std::ifstream f("/proc/cpuinfo");
    std::string line;
    while (std::getline(f, line)) {
        if (line.rfind("model name", 0) == 0) {
            auto pos = line.find(':');
            if (pos != std::string::npos) return shell_trim(line.substr(pos + 1));
        }
    }
    return "Unknown";
}

inline int cpu_cores() {
    return static_cast<int>(sysconf(_SC_NPROCESSORS_ONLN));
}

inline std::string cpu_usage() {
    auto read_stat = [](long long& idle, long long& total) {
        std::ifstream f("/proc/stat");
        std::string cpu;
        long long user, nice, sys, i, iowait, irq, softirq, steal;
        f >> cpu >> user >> nice >> sys >> i >> iowait >> irq >> softirq >> steal;
        idle  = i + iowait;
        total = user + nice + sys + i + iowait + irq + softirq + steal;
    };
    long long idle1, total1, idle2, total2;
    read_stat(idle1, total1);
    std::this_thread::sleep_for(std::chrono::milliseconds(200));
    read_stat(idle2, total2);
    long long dt = total2 - total1;
    long long di = idle2 - idle1;
    if (dt <= 0) return "0.0%";
    double usage = 100.0 * (dt - di) / dt;
    std::ostringstream oss; oss.precision(1); oss << std::fixed << usage << "%";
    return oss.str();
}

// ── 内存 ─────────────────────────────────────────────────
struct MemInfo { double total = 0, used = 0, available = 0; int percent = 0; };
inline MemInfo memory_info() {
    MemInfo m;
    std::ifstream f("/proc/meminfo");
    std::string key, unit; long long val;
    long long total = 0, available = 0;
    while (f >> key >> val) {
        if (key == "MemTotal:")     total = val;
        if (key == "MemAvailable:") { available = val; break; }
        std::getline(f, unit);
    }
    if (total > 0) {
        m.total     = static_cast<double>(total) * 1024.0;
        m.available = static_cast<double>(available) * 1024.0;
        m.used      = m.total - m.available;
        m.percent   = static_cast<int>(100.0 * m.used / m.total);
    }
    return m;
}

// ── 磁盘 ─────────────────────────────────────────────────
struct DiskInfo { std::string device, mount, total, used, free; int percent = 0; };
inline DiskInfo disk_info() {
    DiskInfo d;
    struct statvfs st{};
    if (statvfs("/", &st) == 0) {
        double total = static_cast<double>(st.f_blocks) * st.f_frsize;
        double free  = static_cast<double>(st.f_bavail) * st.f_frsize;
        double used  = total - free;
        d.device  = "/";
        d.mount   = "/";
        d.total   = bytes_to_human(total);
        d.used    = bytes_to_human(used);
        d.free    = bytes_to_human(free);
        d.percent = total > 0 ? static_cast<int>(100.0 * used / total) : 0;
    }
    return d;
}

// ── 网络 ─────────────────────────────────────────────────
inline std::string net_ip() {
    struct ifaddrs* ifa = nullptr;
    std::string result = "Unknown";
    if (getifaddrs(&ifa) == 0) {
        for (struct ifaddrs* p = ifa; p; p = p->ifa_next) {
            if (!p->ifa_addr || p->ifa_addr->sa_family != AF_INET) continue;
            if (std::string(p->ifa_name) == "lo") continue;
            char buf[INET_ADDRSTRLEN];
            auto* sin = reinterpret_cast<sockaddr_in*>(p->ifa_addr);
            if (inet_ntop(AF_INET, &sin->sin_addr, buf, sizeof(buf))) {
                result = buf; break;
            }
        }
        freeifaddrs(ifa);
    }
    return result;
}

inline std::string net_mac() {
    std::string mac = run_pipe("cat /sys/class/net/*/address | grep -v '^00:00:00:00:00:00$' | head -n1");
    return mac.empty() ? "Unknown" : mac;
}

inline std::string host_name() {
    char buf[256] = {0};
    if (gethostname(buf, sizeof(buf) - 1) == 0) return std::string(buf);
    return "Unknown";
}

// ── 用户 ─────────────────────────────────────────────────
inline std::string current_user() {
    const char* u = getenv("USER");
    if (u && *u) return std::string(u);
    struct passwd* pw = getpwuid(getuid());
    return pw ? std::string(pw->pw_name) : "Unknown";
}

inline std::string home_dir() {
    const char* h = getenv("HOME");
    return h ? std::string(h) : "/";
}

inline std::string shell_path() {
    const char* s = getenv("SHELL");
    return s ? std::string(s) : "/bin/sh";
}

} // namespace deepter