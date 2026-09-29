#include "app_nap.hpp"
#include "utils.hpp"
#include <algorithm>

namespace alrm {

AppNap::AppNap(const Config& config) : config_(config) {
    focus_history_.resize(3, "");
}

bool AppNap::is_whitelisted(const std::string& scope) {
    std::string lower = scope;
    std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);
    
    for (const auto& keyword : config_.whitelist) {
        std::string kw = keyword;
        std::transform(kw.begin(), kw.end(), kw.begin(), ::tolower);
        if (lower.find(kw) != std::string::npos) {
            return true;
        }
    }
    return false;
}

bool AppNap::detect_wake() {
    if (focus_history_.size() < 2) return false;
    
    // 上一次为空，这一次有值 → 刚唤醒
    if (focus_history_[focus_history_.size() - 2].empty() && 
        !focus_history_.back().empty()) {
        return true;
    }
    return false;
}

void AppNap::handle_focus_change(const std::string& current_scope) {
    // 如果当前应用被冻结，立即解冻
    if (!current_scope.empty() && monitor_.is_frozen(current_scope)) {
        monitor_.thaw_scope(current_scope);
    }
}

void AppNap::freeze_background_apps(const std::string& current_scope) {
    auto all_scopes = monitor_.get_all_scopes();
    
    for (const auto& scope : all_scopes) {
        // 跳过当前前台应用
        if (scope == current_scope) continue;
        
        // 跳过已冻结的
        if (monitor_.is_frozen(scope)) continue;
        
        // 跳过白名单
        if (is_whitelisted(scope)) continue;
        
        // 跳过 CPU 使用率高的应用
        double cpu = monitor_.get_cpu_usage(scope);
        if (cpu > config_.cpu_threshold) {
            log(LogLevel::DEBUG, "跳过 " + scope + " (CPU: " + 
                std::to_string(cpu) + "%)");
            continue;
        }
        
        // 执行冻结
        if (monitor_.freeze_scope(scope)) {
            monitor_.record_freeze(scope);
        }
    }
}

void AppNap::check_timeout() {
    // 检查超时的冻结应用，自动解冻
    // 这里简化处理：每次 tick 检查一次
    // 实际可以用独立线程或定时器
    auto all_scopes = monitor_.get_all_scopes();
    long long now = now_ms();
    
    for (const auto& scope : all_scopes) {
        if (monitor_.is_frozen(scope)) {
            long long freeze_time = monitor_.get_freeze_time(scope);
            if (freeze_time > 0 && 
                (now - freeze_time) > (config_.freeze_timeout * 1000LL)) {
                log(LogLevel::INFO, "超时自动解冻: " + scope);
                monitor_.thaw_scope(scope);
            }
        }
    }
}

void AppNap::tick() {
    // 性能模式检查
    if (config_.is_performance_mode()) {
        if (!focus_history_.empty() && !focus_history_.back().empty()) {
            log(LogLevel::INFO, "⚡ 性能模式，释放所有应用");
            release_all();
        }
        return;
    }
    
    // 应用冰封检查
    if (!config_.enable_app_nap) return;
    
    // 获取当前前台应用
    std::string current_scope = monitor_.get_current_scope();
    
    // 更新历史记录
    focus_history_.push_back(current_scope);
    if (focus_history_.size() > 3) {
        focus_history_.pop_front();
    }
    
    // 检测唤醒
    if (detect_wake()) {
        log(LogLevel::INFO, "🚀 检测到唤醒，批量恢复应用");
        release_all();
        return;
    }
    
    // 处理焦点切换
    if (current_scope != last_scope_) {
        handle_focus_change(current_scope);
        last_scope_ = current_scope;
    }
    
    // 冻结后台应用
    if (!current_scope.empty()) {
        freeze_background_apps(current_scope);
    }
    
    // 检查超时
    check_timeout();
}

void AppNap::release_all() {
    auto all_scopes = monitor_.get_all_scopes();
    for (const auto& scope : all_scopes) {
        if (monitor_.is_frozen(scope)) {
            monitor_.thaw_scope(scope);
        }
    }
}

} // namespace alrm