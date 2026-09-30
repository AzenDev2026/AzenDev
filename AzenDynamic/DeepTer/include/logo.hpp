#pragma once

#include <ftxui/dom/elements.hpp>
#include <ftxui/screen/color.hpp>
#include <string>
#include <vector>

#include "colors.hpp"

namespace deepter {

// ---- Logo 原始文本（ASCII Art） ----
inline std::vector<std::string> raw_logo() {
    return {
        "  ██████╗ ███████╗███████╗██████╗ ",
        "  ██╔══██╗██╔════╝██╔════╝██╔══██╗",
        "  ██║  ██║█████╗  █████╗  ██████╔╝",
        "  ██║  ██║██╔══╝  ██╔══╝  ██╔═══╝ ",
        "  ██████╔╝███████╗███████╗██║     ",
        "  ╚═════╝ ╚══════╝╚══════╝╚═╝     ",
    };
}

// ---- 一行 Logo：文本 + 颜色 ----
struct LogoLine {
    std::string   text;
    ftxui::Color  color;
};

// ---- 上色后的 Logo ----
inline std::vector<LogoLine> colored_logo() {
    auto raw = raw_logo();
    std::vector<LogoLine> out;
    out.reserve(raw.size());

    const int n = static_cast<int>(raw.size());
    for (int i = 0; i < n; ++i) {
        ftxui::Color c;
        if (i < n / 3)         c = LOGO_TOP_FT();
        else if (i < 2 * n / 3) c = LOGO_MID_FT();
        else                    c = LOGO_BOTTOM_FT();
        out.push_back({ raw[i], c });
    }
    return out;
}

// ---- 组装成 FTXUI Element（terminal.hpp 里 logo_element() 用的就是它） ----
inline ftxui::Element logo_element() {
    using namespace ftxui;
    Elements lines;
    for (const auto& l : colored_logo()) {
        lines.push_back(text(l.text) | color(l.color));
    }
    return vbox(std::move(lines));
}

} // namespace deepter