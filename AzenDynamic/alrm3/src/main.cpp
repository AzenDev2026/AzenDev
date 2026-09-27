#include <iostream>
#include <csignal>
#include <glib.h>
#include "config_parser.hpp"
#include "app_nap.hpp"
#include "sleep_manager.hpp"
#include "utils.hpp"

using namespace alrm;

// 全局对象（用于信号处理）
static AppNap* g_app_nap = nullptr;
static SleepManager* g_sleep_mgr = nullptr;
static GMainLoop* g_main_loop = nullptr;
static Config g_config;

void signal_handler(int sig) {
    if (sig == SIGUSR1) {
        log(LogLevel::INFO, "📴 收到合盖信号");
        if (g_app_nap) g_app_nap->release_all();  // 先释放所有
    } else if (sig == SIGUSR2) {
        log(LogLevel::INFO, "📱 收到开盖信号");
        // 开盖后不做事，让下一轮 tick 自动恢复
    } else if (sig == SIGINT || sig == SIGTERM) {
        log(LogLevel::INFO, "🛑 收到退出信号，清理中...");
        if (g_app_nap) g_app_nap->release_all();
        if (g_main_loop) g_main_loop_quit(g_main_loop);
    }
}

gboolean tick_callback(gpointer data) {
    if (g_app_nap) {
        g_app_nap->tick();
    }
    return G_SOURCE_CONTINUE;
}

int main(int argc, char* argv[]) {
    // 注册信号处理
    signal(SIGUSR1, signal_handler);
    signal(SIGUSR2, signal_handler);
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // 加载配置
    std::string config_path = "/etc/azen/Azen-ALRM.conf";
    if (argc > 1) {
        config_path = argv[1];
    }
    g_config = Config::load(config_path);
    
    log(LogLevel::INFO, "==============================================");
    log(LogLevel::INFO, " ALRM (Azen Laptop Resources Management) v2.0");
    log(LogLevel::INFO, " 纯 C++ 实现 · 高性能 · 低内存占用");
    log(LogLevel::INFO, "==============================================");
    
    // 初始化睡眠管理
    g_sleep_mgr = new SleepManager(g_config);
    g_sleep_mgr->apply_config();
    
    // 初始化 App Nap
    g_app_nap = new AppNap(g_config);
    
    // 创建主循环
    g_main_loop = g_main_loop_new(nullptr, FALSE);
    
    // 设置定时器
    guint interval_ms = g_config.scan_interval * 1000;
    g_timeout_add(interval_ms, tick_callback, nullptr);
    
    log(LogLevel::INFO, "扫描间隔: " + std::to_string(g_config.scan_interval) + " 秒");
    log(LogLevel::INFO, "守护进程已启动，等待调度...");
    
    // 运行
    g_main_loop_run(g_main_loop);
    
    // 清理
    delete g_app_nap;
    delete g_sleep_mgr;
    g_main_loop_unref(g_main_loop);
    
    return 0;
}