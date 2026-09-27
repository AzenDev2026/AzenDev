// SPDX-License-Identifier: GPL-3.0
// Copyright (C) 2026 白企 Whitent / Azen Project
//
// Azen Project - alrm3 配置文件解析器

#include "config_parser.hpp"

#include <fstream>
#include <string>
#include <algorithm>
#include <cctype>

namespace azen {
namespace alrm3 {

namespace {

// 去除首尾空白
std::string trim(const std::string& s) {
    auto begin = s.begin();
    auto end = s.end();
    while (begin != end && std::isspace(static_cast<unsigned char>(*begin))) {
        ++begin;
    }
    while (begin != end && std::isspace(static_cast<unsigned char>(*(end - 1)))) {
        --end;
    }
    return std::string(begin, end);
}

}  // namespace

ConfigParser::ConfigParser() {}

ConfigParser::~ConfigParser() {}

bool ConfigParser::load(const std::string& path) {
    std::ifstream file(path);
    if (!file.is_open()) {
        return false;
    }

    std::string line;
    while (std::getline(file, line)) {
        // 去掉行尾的 \r（兼容 CRLF）
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }

        std::string trimmed = trim(line);

        // 跳过空行和注释
        if (trimmed.empty() || trimmed[0] == '#') {
            continue;
        }

        // 解析 KEY=VALUE
        auto pos = trimmed.find('=');
        if (pos == std::string::npos) {
            continue;
        }

        std::string key = trim(trimmed.substr(0, pos));
        std::string value = trim(trimmed.substr(pos + 1));

        if (key == "BATTERY_LOW") {
            config_.battery_low = std::stoi(value);
        } else if (key == "BATTERY_CRITICAL") {
            config_.battery_critical = std::stoi(value);
        } else if (key == "TEMP_WARN") {
            config_.temp_warn = std::stoi(value);
        } else if (key == "TEMP_CRITICAL") {
            config_.temp_critical = std::stoi(value);
        } else if (key == "SLEEP_DELAY") {
            config_.sleep_delay = std::stoi(value);
        } else if (key == "PREFER_DEEP_SLEEP") {
            config_.prefer_deep_sleep = (value == "true");
        } else if (key == "VERBOSE") {
            config_.verbose = (value == "true");
        }
    }

    return true;
}

}  // namespace alrm3
}  // namespace azen