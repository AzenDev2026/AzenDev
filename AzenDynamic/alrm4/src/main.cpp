#include "config_parser.hpp"
#include "app_nap.hpp"
#include "utils.hpp"

#include <glib.h>
#include <csignal>
#include <memory>

using namespace alrm;

namespace {

std::unique_ptr<AppNap> g_app_nap;
GMainLoop* g_main_loop = nullptr;
Config g_config;

void signal_handler(int signum) {
    switch (signum) {
        case SIGUSR1:
            log(LogLevel::INFO, "收到 SIGUSR1，释放所有冻结应用");
            if (g_app_nap) g_app_nap->release_all();
            break;
        case SIGUSR2:
            log(LogLevel::INFO, "收到 SIGUSR2，重新加载配置");
            {
                ConfigParser parser;
                if (parser.load()) {
                    g_config = parser.get();
                }
            }
            break;
        case SIGINT:
        case SIGTERM:
            log(LogLevel::INFO, "收到退出信号，正在关闭...");
            if (g_app_nap) g_app_nap->release_all();
            if (g_main_loop) g_main_loop_quit(g_main_loop);
            break;
        default:
            break;
    }
}

gboolean tick_callback(gpointer /*data*/) {
    if (g_app_nap) {
        g_app_nap->tick();
    }
    return G_SOURCE_CONTINUE;
}

} // anonymous namespace

int main(int argc, char** argv) {
    (void)argc;
    (void)argv;

    log(LogLevel::INFO, "Azen ALRM v4.0.0 boot");

    // 加载配置
    ConfigParser parser;
    if (!parser.load()) {
        log(LogLevel::ERROR, "配置加载失败，使用默认配置");
    }
    g_config = parser.get();

    // 初始化 AppNap
    g_app_nap = std::make_unique<AppNap>(g_config);

    // 注册信号
    std::signal(SIGUSR1, signal_handler);
    std::signal(SIGUSR2, signal_handler);
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    // 主循环
    g_main_loop = g_main_loop_new(nullptr, FALSE);

    const guint interval_ms = static_cast<guint>(g_config.scan_interval * 1000);
    g_timeout_add(interval_ms, tick_callback, nullptr);

    log(LogLevel::INFO, "进入主循环，扫描间隔 " +
        std::to_string(g_config.scan_interval) + "s");

    g_main_loop_run(g_main_loop);

    // 清理
    if (g_app_nap) g_app_nap->release_all();
    g_main_loop_unref(g_main_loop);

    log(LogLevel::INFO, "Azen ALRM 已退出");
    return 0;
}
