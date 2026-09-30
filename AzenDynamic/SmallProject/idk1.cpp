// nvazen_splash.cpp
// g++ -std=c++17 -O2 -o nvazen_splash nvazen_splash.cpp
// 纯 ANSI，无第三方依赖；Windows 建议在 Windows Terminal 下运行

#include <iostream>
#include <string>
#include <thread>
#include <chrono>
#include <vector>
#include <cmath>

using namespace std::chrono_literals;

// 256 色前景
static std::string fg(int r, int g, int b) {
    return "\033[38;2;" + std::to_string(r) + ";" + std::to_string(g) + ";" + std::to_string(b) + "m";
}
static const char* RST = "\033[0m";

// 圆角框 + 品牌字
static const std::vector<std::string> ART = {
    "╭──────────────────────────────╮",
    "│   N V a z e n   ™            │",
    "│   A zen  Linux  Architecture │",
    "╰──────────────────────────────╯",
};

int main() {
    std::cout << "\033[2J\033[H";           // 清屏
    std::cout << "\033[?25l";                // 隐藏光标

    double t = 0.0;
    for (int frame = 0; frame < 90; ++frame) {
        t += 0.08;
        // 呼吸色：蓝紫 → 青
        int r = (int)(70 + 60 * std::sin(t));
        int g = (int)(120 + 80 * std::sin(t + 1.2));
        int b = (int)(220 + 35 * std::sin(t + 2.4));

        std::cout << "\033[H";
        std::cout << fg(r, g, b);
        for (auto& line : ART) std::cout << "   " << line << "\n";
        std::cout << RST;

        // 进度条
        int width = 30;
        int fill = (frame * width) / 89;
        std::cout << "\n   ";
        std::cout << fg(90, 90, 110) << "[" << RST;
        std::cout << fg(r, g, b);
        for (int i = 0; i < width; ++i) std::cout << (i < fill ? "━" : " ");
        std::cout << RST << fg(90, 90, 110) << "]" << RST;
        std::cout << "  " << fg(200, 200, 220) << (frame * 100 / 89) << "%" << RST << "  ";

        std::this_thread::sleep_for(28ms);
    }

    std::cout << "\033[?25h\n";
    std::cout << fg(150, 200, 255) << "   ✓  Welcome back, Azen.\n" << RST;
    return 0;
}
