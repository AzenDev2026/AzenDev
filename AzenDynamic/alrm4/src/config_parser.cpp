#include "config_parser.hpp"

#include <fstream>
#include <sstream>
#include <algorithm>
#include <cctype>

namespace alrm {

std::string trim(const std::string& s) {
    auto begin = s.begin();
    while (begin != s.end() && std::isspace(static_cast<unsigned char>(*begin))) {
        ++begin;
    }
    auto end = s.end();
    while (end != begin && std::isspace(static_cast<unsigned char>(*(end - 1)))) {
        --end;
    }
    return std::string(begin, end);
}

bool parseLine(const std::string& line, std::string& key, std::string& value) {
    std::string trimmed = trim(line);

    // 空行或注释
    if (trimmed.empty() || trimmed[0] == '#') {
        return false;
    }

    auto pos = trimmed.find('=');
    if (pos == std::string::npos) {
        return false;
    }

    key   = trim(trimmed.substr(0, pos));
    value = trim(trimmed.substr(pos + 1));
    return !key.empty();
}

Config load(const std::string& path) {
    Config cfg;

    std::ifstream file(path);
    if (!file.is_open()) {
        // 配置文件缺失时直接返回默认值
        return cfg;
    }

    std::string line;
    while (std::getline(file, line)) {
        std::string key, value;
        if (!parseLine(line, key, value)) {
            continue;
        }

        if (key == "monitor_enabled") {
            cfg.monitor_enabled = (value == "true" || value == "1");
        } else if (key == "monitor_interval_sec") {
            cfg.monitor_interval_sec = std::stoi(value);
        } else if (key == "app_nap_enabled") {
            cfg.app_nap_enabled = (value == "true" || value == "1");
        } else if (key == "app_nap_idle_sec") {
            cfg.app_nap_idle_sec = std::stoi(value);
        } else if (key == "log_path") {
            cfg.log_path = value;
        } else if (key == "log_to_console") {
            cfg.log_to_console = (value == "true" || value == "1");
        }
    }

    return cfg;
}

} // namespace alrm
