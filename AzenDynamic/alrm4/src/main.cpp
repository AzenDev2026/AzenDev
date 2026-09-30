#include "config_parser.hpp"
#include "app_nap.hpp"
#include "utils.hpp"

#include <glib.h>

#include <csignal>
#include <memory>
#include <string>

using namespace alrm;

namespace {

std::unique_ptr<AppNap> g_app_nap;
GMainLoop* g_main_loop = nullptr;
Config g_config;

}  // namespace

static void signal_handler(int signum) {
    if (signum == SIGUSR1) {
        log(LogLevel::INFO, "收到 SIGUSR1，重新加载配置");
        g_config = load();
        if (g_app_nap) {
            g_app_nap->release_all();
        }
        g_app_nap = std::make_unique<AppNap>(g_config);
    } else if (signum == SIGUSR2) {
        log(LogLevel::INFO, "收到 SIGUSR2，立即释放所有 App Nap");
        g_config = load();
        if (g_app_nap) {
            g_app_nap->release_all();
        }
    } else if (signum == SIGINT || signum == SIGTERM) {
        log(LogLevel::INFO, "收到退出信号，准备关闭");
        if (g_main_loop) {
            g_main_loop_quit(g_main_loop);
        }
    }
}

static gboolean tick_callback(gpointer /*data*/) {
    if (!g_app_nap) {
        return TRUE;
    }
    if (g_config.app_nap_enabled) {
        g_app_nap->tick();
    }
    return TRUE;
}

int main(int /*argc*/, char** /*argv*/) {
    log(LogLevel::INFO, "Azen ALRM v4.0.0 boot");

    g_config = load();
    g_app_nap = std::make_unique<AppNap>(g_config);

    std::signal(SIGUSR1, signal_handler);
    std::signal(SIGUSR2, signal_handler);
    std::signal(SIGINT,  signal_handler);
    std::signal(SIGTERM, signal_handler);

    g_main_loop = g_main_loop_new(nullptr, FALSE);

    const guint interval_ms =
        static_cast<guint>(g_config.monitor_interval_sec * 1000);
    g_timeout_add(interval_ms, tick_callback, nullptr);

    log(LogLevel::INFO, "进入主循环，扫描间隔 "
        + std::to_string(g_config.monitor_interval_sec) + "s");

    g_main_loop_run(g_main_loop);

    if (g_app_nap) {
        g_app_nap->release_all();
    }
    g_main_loop_unref(g_main_loop);

    log(LogLevel::INFO, "Azen ALRM 已退出");
    return 0;
}
