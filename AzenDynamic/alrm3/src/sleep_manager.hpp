// SPDX-License-Identifier: GPL-3.0
// Copyright (C) 2026 白企 Whitent / Azen Project
//
// Azen Project - alrm3 睡眠管理器

#pragma once

#include <string>
#include <vector>

#include "config_parser.hpp"

namespace azen {
namespace alrm3 {

/**
 * @brief 睡眠模式
 */
enum class SleepMode {
    S2IDLE,     // 浅睡眠(s2idle)
    DEEP,       // 深度睡眠(ACPI S3)
    HIBERNATE,  // 休眠
    UNKNOWN
};

/**
 * @brief 睡眠管理器
 */
class SleepManager {
public:
    explicit SleepManager(const Config& config);
    ~SleepManager();

    /**
     * @brief 进入浅睡眠(s2idle)
     */
    bool enable_s2idle();

    /**
     * @brief 进入深度睡眠(ACPI S3)
     */
    bool enable_deep_sleep();

    /**
     * @brief 进入休眠
     */
    bool enable_hibernate();

    /**
     * @brief 获取系统支持的睡眠模式
     */
    std::vector<std::string> get_supported_modes() const;

    /**
     * @brief 根据当前电源/温度状态自动应用睡眠策略
     */
    bool apply_config();

private:
    Config config_;
    bool prefer_deep_ = false;

    // 读取 sysfs 中的电源状态
    bool on_battery() const;
    int read_temperature() const;
};

}  // namespace alrm3
}  // namespace azen