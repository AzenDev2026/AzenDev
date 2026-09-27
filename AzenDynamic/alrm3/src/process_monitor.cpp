#include "process_monitor.hpp"
#include "utils.hpp"
#include <regex>
#include <dirent.h>
#include <fstream>

namespace alrm {

ProcessMonitor::ProcessMonitor() {}

std::string ProcessMonitor::get_current_scope() {
    // 使用 gdbus 获取当前前台窗口的 PID
    std::string cmd = "gdbus call --session "
        "--dest org.gnome.Shell "
        "--object-path /org/gnome/Shell "
        "--method org.gnome.Shell.Eval "
        "\"global.display.focus_window ? global.display.focus_window.get_pid() : null\"";
    
    std::string result = exec_command(cmd);
    
    // 提取 PID（简化处理，实际需要解析返回值）
    std::regex pid_regex(R"(uint32 (\d+))");
    std::smatch match;
    if (!std::regex_search(result, match, pid_regex)) {
        return "";
    }
    
    int pid = std::stoi(match[1].str());
    
    // 读取 /proc/PID/cgroup 获取 scope
    std::string cgroup_path = "/proc/" + std::to_string(pid) + "/cgroup";
    std::string cgroup_content = read_file(cgroup_path);
    
    std::regex scope_regex(R"(app-gnome-[\w\-]+\.scope)");
    if (std::regex_search(cgroup_content, match, scope_regex)) {
        return match[0].str();
    }
    
    return "";
}

std::vector<std::string> ProcessMonitor::get_all_scopes() {
    std::vector<std::string> scopes;
    std::string output = exec_command(
        "systemctl --user list-units --type=scope --state=running --no-legend --no-pager"
    );
    
    std::istringstream stream(output);
    std::string line;
    while (std::getline(stream, line)) {
        if (line.find("app-gnome-") != std::string::npos && 
            line.find(".scope") != std::string::npos) {
            auto parts = split(line, ' ');
            if (!parts.empty()) {
                scopes.push_back(parts[0]);
            }
        }
    }
    return scopes;
}

double ProcessMonitor::get_cpu_usage(const std::string& app_name) {
    // 从 scope 名字提取应用名
    std::string process_name = app_name;
    size_t start = process_name.find("app-gnome-");
    if (start != std::string::npos) {
        process_name = process_name.substr(start + 10);
    }
    size_t end = process_name.find(".scope");
    if (end != std::string::npos) {
        process_name = process_name.substr(0, end);
    }
    
    // 使用 ps 获取 CPU 使用率
    std::string cmd = "ps -C " + process_name + " -o %cpu --no-headers 2>/dev/null | head -1";
    std::string result = exec_command(cmd);
    
    if (result.empty()) return 0.0;
    
    try {
        return std::stod(result);
    } catch (...) {
        return 0.0;
    }
}

bool ProcessMonitor::freeze_scope(const std::string& scope) {
    std::string cmd = "systemctl --user freeze " + scope + " 2>/dev/null";
    int ret = system(cmd.c_str());
    if (ret == 0) {
        frozen_set_.insert(scope);
        log(LogLevel::INFO, "❄️  冰封: " + scope);
        return true;
    }
    return false;
}

bool ProcessMonitor::thaw_scope(const std::string& scope) {
    std::string cmd = "systemctl --user thaw " + scope + " 2>/dev/null";
    int ret = system(cmd.c_str());
    if (ret == 0) {
        frozen_set_.erase(scope);
        freeze_records_.erase(scope);
        log(LogLevel::INFO, "🔥 解冻: " + scope);
        return true;
    }
    return false;
}

bool ProcessMonitor::is_frozen(const std::string& scope) {
    return frozen_set_.count(scope) > 0;
}

void ProcessMonitor::record_freeze(const std::string& scope) {
    freeze_records_[scope] = now_ms();
}

long long ProcessMonitor::get_freeze_time(const std::string& scope) {
    auto it = freeze_records_.find(scope);
    return (it != freeze_records_.end()) ? it->second : 0;
}

void ProcessMonitor::cleanup(const std::string& scope) {
    frozen_set_.erase(scope);
    freeze_records_.erase(scope);
}

} // namespace alrm