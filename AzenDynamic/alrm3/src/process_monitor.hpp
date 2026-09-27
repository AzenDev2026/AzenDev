#ifndef ALRM_PROCESS_MONITOR_HPP
#define ALRM_PROCESS_MONITOR_HPP

#include <string>
#include <vector>
#include <unordered_set>
#include <unordered_map>

namespace alrm {

struct ScopeInfo {
    std::string name;
    long long freeze_time;
    bool is_frozen;
};

class ProcessMonitor {
public:
    ProcessMonitor();
    
    // 获取当前前台应用的 scope
    std::string get_current_scope();
    
    // 获取所有运行中的应用 scope
    std::vector<std::string> get_all_scopes();
    
    // 获取应用的 CPU 使用率
    double get_cpu_usage(const std::string& app_name);
    
    // 冻结应用
    bool freeze_scope(const std::string& scope);
    
    // 解冻应用
    bool thaw_scope(const std::string& scope);
    
    // 检查是否被冻结
    bool is_frozen(const std::string& scope);
    
    // 记录冻结时间
    void record_freeze(const std::string& scope);
    long long get_freeze_time(const std::string& scope);
    
    // 清理记录
    void cleanup(const std::string& scope);
    
private:
    std::unordered_map<std::string, long long> freeze_records_;
    std::unordered_set<std::string> frozen_set_;
};

} // namespace alrm

#endif