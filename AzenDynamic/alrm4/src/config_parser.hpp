#ifndef ALRM_CONFIG_PARSER_HPP
#define ALRM_CONFIG_PARSER_HPP

#include <string>
#include <vector>

namespace alrm {

struct Config {
    // 电池管理
    int battery_low = 20;
    int battery_critical = 10;

    // 温度管理
    int temp_warn = 75;
    int temp_critical = 85;

    // 调度
    int scan_interval = 5;

    // AppNap
    bool enable_app_nap = true;
    int cpu_threshold = 20;
    int freeze_timeout = 30;
    std::vector<std::string> whitelist;

    // 日志
    bool verbose = false;

    // 综合判断：是否处于性能模式
    bool is_performance_mode() const {
        return battery_low > 0 && battery_critical > 0;
    }
};

class ConfigParser {
public:
    ConfigParser() = default;

    // 加载配置文件，成功返回 true
    bool load(const std::string& path = "/etc/azen-alrm/Azen-ALRM.conf");

    // 获取解析结果
    const Config& get() const { return config_; }

private:
    Config config_;
};

} // namespace alrm

#endif // ALRM_CONFIG_PARSER_HPP
