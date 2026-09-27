#ifndef ALRM_APP_NAP_HPP
#define ALRM_APP_NAP_HPP

#include "config_parser.hpp"
#include "process_monitor.hpp"
#include <deque>

namespace alrm {

class AppNap {
public:
    AppNap(const Config& config);
    
    // 执行一次调度（核心逻辑）
    void tick();
    
    // 释放所有冻结的应用
    void release_all();
    
    // 检查是否刚唤醒
    bool detect_wake();
    
private:
    Config config_;
    ProcessMonitor monitor_;
    std::deque<std::string> focus_history_;
    std::string last_scope_;
    
    bool is_whitelisted(const std::string& scope);
    void handle_focus_change(const std::string& current_scope);
    void freeze_background_apps(const std::string& current_scope);
    void check_timeout();
};

} // namespace alrm

#endif