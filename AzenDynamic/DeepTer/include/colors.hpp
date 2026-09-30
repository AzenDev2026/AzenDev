#pragma once

#include <ftxui/dom/elements.hpp>
#include <ftxui/screen/color.hpp>
#include <string>
#include <vector>

namespace deepter {

// ---- 主色板（Logo 与界面统一取色） ----
inline ftxui::Color LOGO_TOP_FT()    { return ftxui::Color::RGB(0, 200, 255); }   // 青
inline ftxui::Color LOGO_MID_FT()    { return ftxui::Color::RGB(120, 90, 255); }  // 紫
inline ftxui::Color LOGO_BOTTOM_FT() { return ftxui::Color::RGB(255, 90, 200); }  // 粉

inline ftxui::Color TEXT_FT()  { return ftxui::Color::RGB(220, 220, 220); }
inline ftxui::Color WARN_FT()  { return ftxui::Color::RGB(255, 200, 60);  }
inline ftxui::Color ERR_FT()   { return ftxui::Color::RGB(255, 80, 80);   }
inline ftxui::Color OK_FT()    { return ftxui::Color::RGB(90, 220, 130);  }

// ---- 强调色命名空间（terminal.hpp 里 color::accent() 用它） ----
namespace color {

    // 界面强调色：取 Logo 顶部色，和标题保持一致
    inline ftxui::Color accent() { return LOGO_TOP_FT(); }

    // 顺手补几个常用别名，后续想用直接用
    inline ftxui::Color text()   { return TEXT_FT(); }
    inline ftxui::Color warn()   { return WARN_FT(); }
    inline ftxui::Color error()  { return ERR_FT();  }
    inline ftxui::Color ok()     { return OK_FT();   }

} // namespace color

// ---- 旧的调色板接口（保留兼容，别删，别的地方可能还在用） ----
inline std::vector<ftxui::Color> palette() {
    return {
        LOGO_TOP_FT(), LOGO_MID_FT(), LOGO_BOTTOM_FT(),
        TEXT_FT(), WARN_FT(), ERR_FT(), OK_FT()
    };
}

inline bool is_valid_color(const std::string& name) {
    return name == "accent" || name == "text" || name == "warn"
        || name == "error"  || name == "ok"
        || name == "logo_top" || name == "logo_mid" || name == "logo_bottom";
}

// 把名字映射成 ftxui::Color
inline ftxui::Color fg_by_name(const std::string& name) {
    if (name == "accent")      return color::accent();
    if (name == "text")        return color::text();
    if (name == "warn")        return color::warn();
    if (name == "error")       return color::error();
    if (name == "ok")          return color::ok();
    if (name == "logo_top")    return LOGO_TOP_FT();
    if (name == "logo_mid")    return LOGO_MID_FT();
    if (name == "logo_bottom") return LOGO_BOTTOM_FT();
    return TEXT_FT(); // 兜底
}

// named_colors()：给补全 / 帮助用的一份名单
inline std::vector<std::string> named_colors() {
    return { "accent", "text", "warn", "error", "ok",
             "logo_top", "logo_mid", "logo_bottom" };
}

} // namespace deepter