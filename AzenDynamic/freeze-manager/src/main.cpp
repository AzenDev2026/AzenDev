#include <systemd/sd-bus.h>
#include <chrono>
#include <unordered_map>
#include <iostream>
#include "freezer.hpp"

struct WindowState {
    std::chrono::steady_clock::time_point hide_start;
    bool pending_freeze = false;
    bool frozen = false;
};

static std::unordered_map<pid_t, WindowState> g_states;
static CgroupFreezer g_freezer("freeze-manager");
constexpr auto FREEZE_DELAY = std::chrono::seconds(5);

// D-Bus 方法调用回调
static int on_window_state(sd_bus_message* m, void* userdata,
                            sd_bus_error* ret_error) {
    pid_t pid;
    const char* action;
    int r = sd_bus_message_read(m, "is", &pid, &action);
    if (r < 0) return r;

    auto now = std::chrono::steady_clock::now();
    auto& st = g_states[pid];

    if (std::string(action) == "hide") {
        if (!st.pending_freeze && !st.frozen) {
            st.hide_start = now;
            st.pending_freeze = true;
        }
    } else if (std::string(action) == "show") {
        st.pending_freeze = false;
        if (st.frozen) {
            g_freezer.thaw(pid);
            st.frozen = false;
        }
    }
    return sd_bus_reply_method_return(m, nullptr);
}

int main() {
    sd_bus* bus = nullptr;
    int r = sd_bus_open_user(&bus);
    if (r < 0) return 1;

    // 注册 D-Bus 对象和接口
    sd_bus_slot* slot = nullptr;
    sd_bus_add_object_vtable(bus, &slot,
        "/org/freeze/Manager",
        "org.freeze.Manager",
        nullptr,  // vtable 略，需要定义 WindowStateChanged 方法
        nullptr);

    // 请求服务名
    sd_bus_request_name(bus, "org.freeze.Manager", 0);

    // 主循环
    while (true) {
        sd_bus_process(bus, nullptr);
        sd_bus_wait(bus, 100000); // 100ms 超时，用于检查延迟冻结

        auto now = std::chrono::steady_clock::now();
        for (auto& [pid, st] : g_states) {
            if (st.pending_freeze && !st.frozen) {
                if (now - st.hide_start >= FREEZE_DELAY) {
                    if (g_freezer.freeze(pid)) {
                        st.frozen = true;
                        st.pending_freeze = false;
                    }
                }
            }
        }
    }

    sd_bus_unref(bus);
    return 0;
}