#ifndef ALRM_SLEEP_MANAGER_HPP
#define ALRM_SLEEP_MANAGER_HPP

#include "config_parser.hpp"
#include <string>
#include <vector>

namespace alrm {

class SleepManager {
public:
    SleepManager(const Config& config);

    // 切换到深度睡眠模式（deep / ACPI S3）
    // 注意：部分机型会合盖黑屏无法唤醒，详见同目录 WARNING.md，仅作最后手段
    bool enable_deep_sleep();

    // 切换到浅睡眠模式（s2idle / Modern Standby）
    bool enable_s2idle();

    // 安全入口：优先 s2idle，仅当硬件不支持时才回退到 deep
    bool enable_safe_sleep();

    // 根据配置自动选择（统一走 enable_safe_sleep）
    bool apply_config();

    // 获取当前睡眠模式
    std::string get_current_mode();

    // 检查硬件支持
    std::vector<std::string> get_supported_modes();

private:
    Config config_;
    bool switch_mode(const std::string& mode);
};

} // namespace alrm

#endif
