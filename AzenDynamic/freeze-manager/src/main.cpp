#include <systemd/sd-bus.h>
#include <chrono>
#include <unordered_map>
#include <iostream>
#include <fstream>
#include <csignal>
#include <sys/types.h>
#include <unistd.h>
#include "freezer.hpp"

struct WindowState {
    std::chrono::steady_clock::time_point hide_start;
    bool pending_freeze = false;
    bool frozen = false;
};

static std::unordered_map<pid_t, WindowState> g_states;
static CgroupFreezer g_freezer("freeze-manager");
constexpr auto FREEZE_DELAY = std::chrono::seconds(5);

static bool processAlive(pid_t pid) {
    return pid > 0 && (::kill(pid, 0) == 0 || errno == EPERM);
}

// D-Bus 方法调用回调
static int on_window_state(sd_bus_message* m, void* /*userdata*/,
                            sd_bus_error* /*ret_error*/) {
    int32_t pid;
    const char* action = nullptr;
    int r = sd_bus_message_read(m, "is", &pid, &action);
    if (r < 0) return r;

    auto now = std::chrono::steady_clock::now();
    auto& st = g_states[pid];

    std::string act = action ? action : "";

    if (act == "hide") {
        if (!st.pending_freeze && !st.frozen) {
            st.hide_start = now;
            st.pending_freeze = true;
        }
    } else if (act == "show") {
        st.pending_freeze = false;
        if (st.frozen) {
            g_freezer.thawTree(pid);
            st.frozen = false;
        }
    } else if (act == "close") {
        if (st.frozen) {
            g_freezer.thawTree(pid);
        }
        g_states.erase(pid);
        return sd_bus_reply_method_return(m, nullptr);
    }
    return sd_bus_reply_method_return(m, nullptr);
}

static const sd_bus_vtable manager_vtable[] = {
    SD_BUS_VTABLE_START(0),
    SD_BUS_METHOD("WindowStateChanged", "is", "", on_window_state,
                  SD_BUS_VTABLE_UNPRIVILEGED),
    SD_BUS_VTABLE_END
};

static void writeBusNameFile(const char* name) {
    std::ofstream f("/tmp/freeze-manager.busname", std::ios::trunc);
    if (f) f << name;
}

int main() {
    sd_bus* bus = nullptr;
    int r = sd_bus_open_user(&bus);
    if (r < 0) {
        std::cerr << "Failed to open user bus: " << strerror(-r) << "\n";
        return 1;
    }

    sd_bus_slot* slot = nullptr;
    r = sd_bus_add_object_vtable(bus, &slot,
        "/org/freeze/Manager",
        "org.freeze.Manager",
        manager_vtable,
        nullptr);
    if (r < 0) {
        std::cerr << "Failed to add vtable: " << strerror(-r) << "\n";
        sd_bus_unref(bus);
        return 1;
    }

    r = sd_bus_request_name(bus, "org.freeze.Manager", 0);
    if (r < 0) {
        std::cerr << "Failed to request name: " << strerror(-r) << "\n";
        sd_bus_slot_unref(slot);
        sd_bus_unref(bus);
        return 1;
    }

    // 获取唯一名并写入文件，供 KWin 脚本读取
    const char* unique = sd_bus_get_unique_name(bus);
    if (unique) {
        writeBusNameFile(unique);
    } else {
        writeBusNameFile("org.freeze.Manager");
    }

    // 主循环
    for (;;) {
        r = sd_bus_process(bus, nullptr);
        if (r < 0) {
            std::cerr << "sd_bus_process error: " << strerror(-r) << "\n";
            break;
        }
        if (r == 0) {
            sd_bus_wait(bus, 100000); // 100ms
        }

        auto now = std::chrono::steady_clock::now();
        for (auto it = g_states.begin(); it != g_states.end(); ) {
            pid_t pid = it->first;
            WindowState& st = it->second;

            if (st.pending_freeze && !st.frozen) {
                if (now - st.hide_start >= FREEZE_DELAY) {
                    if (!processAlive(pid)) {
                        it = g_states.erase(it);
                        continue;
                    }
                    if (g_freezer.freezeTree(pid)) {
                        st.frozen = true;
                        st.pending_freeze = false;
                    } else {
                        // 冻结失败，稍后重试但不再无限循环：清除 pending
                        // 避免持续写 cgroup.procs 失败
                        st.pending_freeze = false;
                    }
                }
            }
            ++it;
        }
    }

    sd_bus_slot_unref(slot);
    sd_bus_unref(bus);
    return 0;
}