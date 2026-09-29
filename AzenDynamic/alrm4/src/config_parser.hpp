#pragma once

#include <string>
#include <cstdint>

namespace alrm {

struct Config {
    // 进程监控
    bool        monitor_enabled      = true;
    int         monitor_interval_sec = 5;

    // App Nap
    bool        app_nap_enabled      = true;
    int         app_nap_idle_sec     = 300;

    // 日志
    std::string log_path             = "/var/log/azen-alrm.log";
    bool        log_to_console       = true;
};

// 从配置文件加载配置
// 默认路径：/etc/azen/Azen-ALRM.conf
Config load(const std::string& path = "/etc/azen/Azen-ALRM.conf");

// 解析单行 key=value，成功返回 true
bool parseLine(const std::string& line, std::string& key, std::string& value);

// 去掉字符串两端的空白
std::string trim(const std::string& s);

} // namespace alrm
