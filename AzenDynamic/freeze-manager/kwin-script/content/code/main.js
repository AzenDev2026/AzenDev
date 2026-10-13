// freeze-manager/contents/code/main.js

const SERVICE = "org.freeze.Manager";
const PATH = "/org/freeze/Manager";
const INTERFACE = "org.freeze.Manager";

function reportWindow(window, event) {
    const pid = window.pid;
    if (!pid || pid <= 0) return;

    // 判断“不可见”状态：最小化 或 不在当前桌面
    // KWin 中 shading 和发送到其他桌面也会导致 minimized 为 true
    const isHidden = window.minimized;

    const args = [pid, isHidden ? "hide" : "show"];

    callDBus(
        SERVICE, PATH, INTERFACE,
        "WindowStateChanged",
        args
    );
}

// 监听已存在的窗口
workspace.windowList().forEach(w => {
    if (!w.normalWindow) return;
    w.minimizedChanged.connect(() => reportWindow(w, "minimized"));
    w.desktopsChanged.connect(() => reportWindow(w, "desktop"));
});

// 监听新出现的窗口
workspace.windowAdded.connect(w => {
    if (!w.normalWindow) return;
    w.minimizedChanged.connect(() => reportWindow(w, "minimized"));
    w.desktopsChanged.connect(() => reportWindow(w, "desktop"));
});