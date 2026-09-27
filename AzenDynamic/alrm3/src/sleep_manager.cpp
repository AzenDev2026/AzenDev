// SPDX-License-Identifier: GPL-3.0
// Copyright (C) 2026 白企 Whitent / Azen Project
//
// Azen Project - alrm3 睡眠管理器

#include "sleep_manager.hpp"

#include <fstream>
#include <iostream>
#include <sstream>
#include <cstdlib>

namespace azen {
namespace alrm3 {

SleepManager::SleepManager(const Config& config)
    : config_(config), prefer_deep_(config.prefer_deep_sleep) {}

SleepManager::~SleepManager() {}

bool SleepManager::enable_s2idle() {
    std::cout << "💤 进入浅睡眠 (s2idle)..." << std::endl;
    int ret = std::system("echo s2idle | sudo tee /sys/power/mem_sleep > /dev/null");
    if (ret != 0) {
        std::cerr << "❌ 设置 s2idle 失败" << std::endl;
        return false;
    }
    return std::system("sudo systemctl suspend") == 0;
}

bool SleepManager::enable_deep_sleep() {
    std::cout << "💤 进入深度睡眠 (deep / ACPI S3)..." << std::endl;
    int ret = std::system("echo deep | sudo tee /sys/power/mem_sleep > /dev/null");
    if (ret != 0) {
        std::cerr << "❌ 设置深度睡眠失败（可能不受支持）" << std::endl;
        return false;
    }
    return std::system("sudo systemctl suspend") == 0;
}

bool SleepManager::enable_hibernate() {
    std::cout << "💤 进入休眠 (hibernate)..." << std::endl;
    return std::system("sudo systemctl hibernate") == 0;
}

std::vector<std::string> SleepManager::get_supported_modes() const {
    std::vector<std::string> modes;

    std::ifstream file("/sys/power/mem_sleep");
    if (!file.is_open()) {
        return modes;
    }

    std::string content;
    std::getline(file, content);

    // 例如: "s2idle [deep]"
    // 带 [] 的为当前生效模式
    bool in_bracket = false;
    std::string current;
    for (char c : content) {
        if (c == '[') {
            in_bracket = true;
            current.clear();
        } else if (c == ']') {
            in_bracket = false;
            if (!current.empty()) {
                modes.push_back(current);
            }
        } else if (in_bracket) {
            current.push_back(c);
        }
    }

    // 兜底：按空格切分全部模式
    modes.clear();
    std::istringstream iss(content);
    std::string token;
    while (iss >> token) {
        // 去掉 [] 标记
        std::string cleaned;
        for (char c : token) {
            if (c != '[' && c != ']') {
                cleaned.push_back(c);
            }
        }
        if (!cleaned.empty()) {
            modes.push_back(cleaned);
        }
    }

    return modes;
}

bool SleepManager::on_battery() const {
    std::ifstream file("/sys/class/power_supply/AC/online");
    if (!file.is_open()) {
        return false;
    }
    int online = 1;
    file >> online;
    return online == 0;  // 0 表示未接外接电源 => 电池供电
}

int SleepManager::read_temperature() const {
    std::ifstream file("/sys/class/thermal/thermal_zone0/temp");
    if (!file.is_open()) {
        return 0;
    }
    int millideg = 0;
    file >> millideg;
    return millideg / 1000;
}

bool SleepManager::apply_config() {
    const int temp = read_temperature();

    // 温度过高：强制进入睡眠以保护硬件
    if (temp >= config_.temp_critical) {
        std::cout << "🔥 温度过高 (" << temp << "°C)，强制进入睡眠" << std::endl;
        return prefer_deep_ ? enable_deep_sleep() : enable_s2idle();
    }

    // 温度偏高：节能模式
    if (temp >= config_.temp_warn) {
        std::cout << "⚡ 节能模式: 优先深度睡眠" << std::endl;
        return prefer_deep_ ? enable_deep_sleep() : enable_s2idle();
    }

    // 性能模式：温度正常，优先浅睡眠以快速唤醒
    if (temp < config_.temp_warn / 2) {
        std::cout << "⚡ 性能模式: 启用浅睡眠" << std::endl;
        return enable_s2idle();
    }

    // 平衡模式：根据电源状态决定
    if (on_battery()) {
        std::cout << "⚖️  电池供电，优先深度睡眠" << std::endl;
        return prefer_deep_ ? enable_deep_sleep() : enable_s2idle();
    }

    std::cout << "⚖️  外接电源，启用浅睡眠" << std::endl;
    return enable_s2idle();
}

}  // namespace alrm3
}  // namespace azen