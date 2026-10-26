// freeze-manager/contents/code/main.js

const SERVICE = "org.freeze.Manager";
const PATH = "/org/freeze/Manager";
const INTERFACE = "org.freeze.Manager";
const UNIQUE_NAME_FILE = "/tmp/freeze-manager.busname";

// 读取 C++ 端写出的唯一总线名；若文件不存在则回退到 well-known name
function getDestination() {
    try {
        const f = new File(UNIQUE_NAME_FILE);
        if (f.exists && f.readable) {
            const name = f.read().trim();
            if (name.length > 0) return name;
        }
    } catch (e) {
        // 忽略，回退
    }
    return SERVICE;
}

function isWindowVisible(window) {
    // 最小化直接视为不可见
    if (window.minimized) return false;

    // 在所有桌面上的窗口始终可见
    if (window.onAllDesktops) return true;

    // 判断窗口所在桌面是否包含当前桌面
    const current = workspace.currentDesktop;
    const desktops = window.desktops;
    if (!desktops || desktops.length === 0) return true;
    for (let i = 0; i < desktops.length; ++i) {
        if (desktops[i] === current) return true;
    }
    return false;
}

function reportWindow(window, reason) {
    const pid = window.pid;
    if (!pid || pid <= 0) return;

    const visible = isWindowVisible(window);
    const action = visible ? "show" : "hide";

    callDBus(
        getDestination(), PATH, INTERFACE,
        "WindowStateChanged",
        pid, action
    );
}

function attachWindow(w) {
    if (!w.normalWindow) return;

    w.minimizedChanged.connect(() => reportWindow(w, "minimized"));
    w.desktopsChanged.connect(() => reportWindow(w, "desktop"));

    // 窗口关闭时通知 C++ 侧清理状态
    w.closed.connect(() => {
        const pid = w.pid;
        if (!pid || pid <= 0) return;
        callDBus(
            getDestination(), PATH, INTERFACE,
            "WindowStateChanged",
            pid, "close"
        );
    });

    // 初始上报一次，确保服务端状态与现状一致
    reportWindow(w, "init");
}

// 监听已存在的窗口
workspace.windowList().forEach(attachWindow);

// 监听新出现的窗口
workspace.windowAdded.connect(attachWindow);