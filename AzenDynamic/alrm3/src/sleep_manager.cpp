#include "sleep_manager.hpp"
#include "utils.hpp"

#include <algorithm>

namespace alrm {

SleepManager::SleepManager(const Config& config) : config_(config) {}

std::vector<std::string> SleepManager::get_supported_modes() {
    std::string content = read_file("/sys/power/mem_sleep");
    if (content.empty()) return {};

    // 格式形如 "[s2idle] deep"，方括号内是当前正在使用的模式
    std::vector<std::string> modes;
    for (auto& part : split(content, ' ')) {
        part.erase(std::remove(part.begin(), part.end(), '['), part.end());
        part.erase(std::remove(part.begin(), part.end(), ']'), part.end());
        part.erase(std::remove(part.begin(), part.end(), '\n'), part.end());
        part.erase(std::remove(part.begin(), part.end(), '\r'), part.end());
        if (part.empty()) continue;
        // 去重：同一个模式在列表里只保留一次
        if (std::find(modes.begin(), modes.end(), part) == modes.end()) {
            modes.push_back(part);
        }
    }

    return modes;
}

std::string SleepManager::get_current_mode() {
    std::string content = read_file("/sys/power/mem_sleep");
    auto start = content.find('[');
    auto end = content.find(']');
    if (start != std::string::npos && end != std::string::npos && end > start) {
        return content.substr(start + 1, end - start - 1);
    }
    return "unknown";
}

bool SleepManager::switch_mode(const std::string& mode) {
    auto supported = get_supported_modes();
    if (std::find(supported.begin(), supported.end(), mode) == supported.end()) {
        log(LogLevel::WARN, "模式 " + mode + " 不被硬件支持");
        return false;
    }

    if (get_current_mode() == mode) {
        log(LogLevel::DEBUG, "已经处于 " + mode + " 模式");
        return true;
    }

    if (write_file("/sys/power/mem_sleep", mode)) {
        log(LogLevel::INFO, "✅ 睡眠模式切换: " + mode);
        return true;
    }

    log(LogLevel::ERROR, "切换睡眠模式失败");
    return false;
}

// 注意：deep (ACPI S3) 在 Dell XPS 13 等机型上会导致合盖后黑屏且无法唤醒，
// 详见同目录 WARNING.md。因此 deep 只能作为最后手段，不能用作默认值。
bool SleepManager::enable_deep_sleep() {
    return switch_mode("deep");
}

bool SleepManager::enable_s2idle() {
    return switch_mode("s2idle");
}

// 统一的安全入口：优先 s2idle，只有硬件确实不支持时才回退到 deep。
bool SleepManager::enable_safe_sleep() {
    auto supported = get_supported_modes();
    bool has_s2idle = std::find(supported.begin(), supported.end(), "s2idle") != supported.end();
    bool has_deep = std::find(supported.begin(), supported.end(), "deep") != supported.end();

    if (has_s2idle) {
        return enable_s2idle();
    }
    if (has_deep) {
        log(LogLevel::WARN,
            "本机不支持 s2idle，只能回退到 deep —— 存在合盖黑屏风险，详见 WARNING.md");
        return enable_deep_sleep();
    }
    log(LogLevel::ERROR, "未在 /sys/power/mem_sleep 中找到可用的睡眠模式");
    return false;
}

bool SleepManager::apply_config() {
    // 节能 / 平衡 / 性能，以及电池 / 外接电源，全部统一走 enable_safe_sleep()。
    // 旧实现在「平衡模式 + 电池供电」时仍然调用 deep，导致黑屏缺陷只修了一半。
    if (config_.is_energy_saver()) {
        log(LogLevel::INFO, "⚡ 节能模式: 启用浅睡眠 (s2idle)");
    } else if (config_.is_performance_mode()) {
        log(LogLevel::INFO, "⚡ 性能模式: 启用浅睡眠 (s2idle)");
    } else {
        std::string bat_status = read_file("/sys/class/power_supply/BAT0/status");
        if (bat_status.find("Discharging") != std::string::npos) {
            log(LogLevel::INFO, "⚖️  电池供电，启用浅睡眠 (s2idle)");
        } else {
            log(LogLevel::INFO, "⚖️  外接电源，启用浅睡眠 (s2idle)");
        }
    }

    return enable_safe_sleep();
}

} // namespace alrm
