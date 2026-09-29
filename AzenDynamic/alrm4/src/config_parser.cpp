#include "config_parser.hpp"
#include "utils.hpp"

#include <fstream>
#include <sstream>

namespace alrm {

namespace {

// 去掉首尾空白（含 \r \n \t 空格）
std::string trim(const std::string& s) {
    const char* ws = " \t\r\n";
    const auto begin = s.find_first_not_of(ws);
    if (begin == std::string::npos) return "";
    const auto end = s.find_last_not_of(ws);
    return s.substr(begin, end - begin + 1);
}

} // anonymous namespace

bool ConfigParser::load(const std::string& path) {
    std::ifstream file(path);
    if (!file.is_open()) {
        log(LogLevel::ERROR, "无法打开配置文件: " + path);
        return false;
    }

    std::string line;
    while (std::getline(file, line)) {
        // 去掉行尾 \r（CRLF 兼容）
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }

        line = trim(line);

        // 跳过空行与注释
        if (line.empty() || line[0] == '#') {
            continue;
        }

        // 按第一个 '=' 切分
        const auto pos = line.find('=');
        if (pos == std::string::npos) {
            continue;
        }

        std::string key = trim(line.substr(0, pos));
        std::string value = trim(line.substr(pos + 1));

        if (key == "BATTERY_LOW") {
            config_.battery_low = std::stoi(value);
        } else if (key == "BATTERY_CRITICAL") {
            config_.battery_critical = std::stoi(value);
        } else if (key == "TEMP_WARN") {
            config_.temp_warn = std::stoi(value);
        } else if (key == "TEMP_CRITICAL") {
            config_.temp_critical = std::stoi(value);
        } else if (key == "SCAN_INTERVAL") {
            config_.scan_interval = std::stoi(value);
        } else if (key == "ENABLE_APP_NAP") {
            config_.enable_app_nap = (value == "true" || value == "1");
        } else if (key == "CPU_THRESHOLD") {
            config_.cpu_threshold = std::stoi(value);
        } else if (key == "FREEZE_TIMEOUT") {
            config_.freeze_timeout = std::stoi(value);
        } else if (key == "WHITELIST") {
            config_.whitelist.clear();
            if (!value.empty()) {
                for (auto& item : split(value, ',')) {
                    const std::string t = trim(item);
                    if (!t.empty()) {
                        config_.whitelist.push_back(t);
                    }
                }
            }
        } else if (key == "VERBOSE") {
            config_.verbose = (value == "true" || value == "1");
        } else {
            log(LogLevel::WARN, "未知配置项: " + key);
        }
    }

    log(LogLevel::INFO, "配置加载完成: " + path);
    return true;
}

} // namespace alrm
