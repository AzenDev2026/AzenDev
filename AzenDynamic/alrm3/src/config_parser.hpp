// SPDX-License-Identifier: GPL-3.0
// Copyright (C) 2026 白企 Whitent / Azen Project
//
// Azen Project - alrm3 配置文件解析器

#pragma once

#include <string>

namespace azen {
namespace alrm3 {

/**
 * @brief 配置结构体
 */
struct Config {
    // 电池阈值
    int battery_low = 20;       // 低电量阈值(%)
    int battery_critical = 10;  // 危险电量阈值(%)

    // 温度阈值(摄氏度)
    int temp_warn = 75;
    int temp_critical = 85;

    // 睡眠行为
    int sleep_delay = 5;        // 进入睡眠前的延迟(秒)
    bool prefer_deep_sleep = false;  // 是否优先 deep(S3) 睡眠

    // 日志
    bool verbose = false;
};

/**
 * @brief 配置文件解析器
 */
class ConfigParser {
public:
    ConfigParser();
    ~ConfigParser();

    /**
     * @brief 从文件加载配置
     * @param path 配置文件路径
     * @return 成功返回 true
     */
    bool load(const std::string& path);

    /**
     * @brief 获取配置
     */
    const Config& get() const { return config_; }

private:
    Config config_;
};

}  // namespace alrm3
}  // namespace azen