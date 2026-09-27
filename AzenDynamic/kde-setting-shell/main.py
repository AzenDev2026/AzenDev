# main.py
import sys
import os
import subprocess
import shutil
import configparser
import pwd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame, QButtonGroup,
    QGraphicsDropShadowEffect, QDialog, QSlider,
    QListWidget, QListWidgetItem, QLineEdit, QMessageBox,
    QCheckBox, QComboBox, QInputDialog, QFileDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QColor, QPixmap

from modules import CATEGORIES, NATIVE_KCM
from about_dialog import AboutSystemDialog, load_sysver
import style
import action
import i18n


# ---------- 主题模式 ----------

THEME_MODE_FILE = os.path.expanduser("~/.config/kde-settings-shell.theme")


def system_theme_is_dark() -> bool:
    try:
        cfg = configparser.ConfigParser()
        cfg.read(os.path.expanduser("~/.config/kdeglobals"))
        scheme = cfg.get("General", "ColorScheme", fallback="").lower()
        return "dark" in scheme
    except Exception:
        return True


def load_theme_mode() -> str:
    try:
        if os.path.exists(THEME_MODE_FILE):
            with open(THEME_MODE_FILE, "r") as f:
                val = f.read().strip()
                if val in ("auto", "light", "dark"):
                    return val
    except Exception:
        pass
    return "dark"


def save_theme_mode(mode: str):
    try:
        os.makedirs(os.path.dirname(THEME_MODE_FILE), exist_ok=True)
        with open(THEME_MODE_FILE, "w") as f:
            f.write(mode)
    except Exception:
        pass


def resolve_qss() -> str:
    mode = load_theme_mode()
    if mode == "light":
        return style.LIGHT_QSS
    if mode == "dark":
        return style.DARK_QSS
    return style.DARK_QSS if system_theme_is_dark() else style.LIGHT_QSS


def find_kcm_launcher():
    for cmd in ("systemsettings", "systemsettings5", "kcmshell6", "kcmshell5"):
        if shutil.which(cmd):
            return cmd
    return None


def open_native_kcm(parent, module_name: str):
    launcher = find_kcm_launcher()
    if launcher is None:
        QMessageBox.warning(parent, i18n.t("apply_failed"),
                            "systemsettings / kcmshell not found")
        return
    try:
        subprocess.Popen(
            [launcher, module_name],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        QMessageBox.warning(parent, i18n.t("apply_failed"), str(e))


# ---------- 通用组件 ----------

class InfoRow(QFrame):
    """一行信息：左标签 + 右值。用于展示只读内容。"""

    def __init__(self, label: str, value: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("SettingCard")
        self.setFixedHeight(52)
        h = QHBoxLayout(self)
        h.setContentsMargins(16, 8, 16, 8)
        h.setSpacing(14)

        lbl = QLabel(label)
        lbl.setObjectName("CardTitle")
        h.addWidget(lbl)

        h.addStretch(1)

        self.val = QLabel(value)
        self.val.setObjectName("CardDesc")
        self.val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        h.addWidget(self.val)

    def set_value(self, value: str):
        self.val.setText(value)


class NativeButton(QPushButton):
    """页面底部的“打开原生设置”按钮。"""

    def __init__(self, parent_page, kcm_name: str, parent=None):
        super().__init__(i18n.t("open_native_settings"), parent)
        self.kcm_name = kcm_name
        self.setFixedHeight(36)
        self.clicked.connect(lambda: open_native_kcm(parent_page, self.kcm_name))


# ---------- 各分类 Page ----------

class BasePage(QWidget):
    """所有 Page 的基类。子类往 self.body 里加内容即可。"""

    def __init__(self, kcm_name: str, parent=None):
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # 标题
        title = QLabel(i18n.t(self.CATEGORY_KEY))
        title.setObjectName("CategoryTitle")
        outer.addWidget(title)

        subtitle = QLabel(i18n.t(self.CATEGORY_KEY + "_desc"))
        subtitle.setObjectName("CategorySubtitle")
        outer.addWidget(subtitle)

        # 滚动区
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.content = QWidget()
        self.body = QVBoxLayout(self.content)
        self.body.setContentsMargins(32, 0, 32, 32)
        self.body.setSpacing(8)
        self.scroll.setWidget(self.content)
        outer.addWidget(self.scroll, 1)

        # 底部按钮
        if kcm_name:
            btn_row = QHBoxLayout()
            btn_row.setContentsMargins(32, 0, 32, 20)
            btn_row.addStretch(1)
            btn_row.addWidget(NativeButton(self, kcm_name))
            outer.addLayout(btn_row)


class SystemPage(BasePage):
    CATEGORY_KEY = "system"

    def __init__(self, parent=None):
        super().__init__(NATIVE_KCM["page_system"], parent)

        # 关于本机（内联）
        cfg = load_sysver()
        about_row = QFrame()
        about_row.setObjectName("SettingCard")
        about_row.setFixedHeight(72)
        h = QHBoxLayout(about_row)
        h.setContentsMargins(16, 8, 16, 8)
        h.setSpacing(14)

        logo = QLabel()
        logo.setFixedSize(40, 40)
        logo.setObjectName("CardIcon")
        if cfg.valid and cfg.logo_path and os.path.exists(cfg.logo_path):
            pm = QPixmap(cfg.logo_path)
            if not pm.isNull():
                logo.setPixmap(pm.scaled(
                    40, 40,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                ))
        h.addWidget(logo)

        text_box = QVBoxLayout()
        text_box.setSpacing(2)
        t1 = QLabel(i18n.t("about"))
        t1.setObjectName("CardTitle")
        if cfg.valid:
            t2 = QLabel(cfg.name)
            t2.setObjectName("CardDesc")
        else:
            t2 = QLabel(i18n.t("config_error"))
            t2.setObjectName("CardDesc")
        text_box.addWidget(t1)
        text_box.addWidget(t2)
        h.addLayout(text_box, 1)

        detail_btn = QPushButton(i18n.t("details"))
        detail_btn.setFixedWidth(80)
        detail_btn.clicked.connect(lambda: AboutSystemDialog(self.window()).exec())
        h.addWidget(detail_btn)

        self.body.addWidget(about_row)

        # 只读展示：桌面环境版本、内核
        from about_dialog import _get_kde_version, _get_kernel
        self.body.addWidget(InfoRow(i18n.t("kde_version"), _get_kde_version()))
        self.body.addWidget(InfoRow(i18n.t("kernel"), _get_kernel()))

        self.body.addStretch(1)


class AppearancePage(BasePage):
    CATEGORY_KEY = "appearance"

    def __init__(self, parent=None):
        super().__init__(NATIVE_KCM["page_appearance"], parent)

        # 主题模式
        mode_row = QFrame()
        mode_row.setObjectName("SettingCard")
        mode_row.setFixedHeight(56)
        h = QHBoxLayout(mode_row)
        h.setContentsMargins(16, 8, 16, 8)
        h.addWidget(QLabel(i18n.t("theme_mode")))
        h.addStretch(1)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem(i18n.t("theme_dark"), "dark")
        self.mode_combo.addItem(i18n.t("theme_light"), "light")
        self.mode_combo.addItem(i18n.t("theme_auto"), "auto")
        cur = load_theme_mode()
        for i in range(self.mode_combo.count()):
            if self.mode_combo.itemData(i) == cur:
                self.mode_combo.setCurrentIndex(i)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_change)
        h.addWidget(self.mode_combo)
        self.body.addWidget(mode_row)

        # 语言
        lang_row = QFrame()
        lang_row.setObjectName("SettingCard")
        lang_row.setFixedHeight(56)
        h2 = QHBoxLayout(lang_row)
        h2.setContentsMargins(16, 8, 16, 8)
        h2.addWidget(QLabel(i18n.t("language")))
        h2.addStretch(1)

        self.lang_combo = QComboBox()
        for code, label in i18n.LANGS.items():
            self.lang_combo.addItem(label, code)
        cur_lang = i18n.get_language()
        for i in range(self.lang_combo.count()):
            if self.lang_combo.itemData(i) == cur_lang:
                self.lang_combo.setCurrentIndex(i)
        self.lang_combo.currentIndexChanged.connect(self._on_lang_change)
        h2.addWidget(self.lang_combo)
        self.body.addWidget(lang_row)

        # 全局主题（快捷切换）
        theme_row = QFrame()
        theme_row.setObjectName("SettingCard")
        theme_row.setFixedHeight(56)
        h3 = QHBoxLayout(theme_row)
        h3.setContentsMargins(16, 8, 16, 8)
        h3.addWidget(QLabel(i18n.t("global_theme")))
        h3.addStretch(1)
        theme_btn = QPushButton(i18n.t("change"))
        theme_btn.setFixedWidth(80)
        theme_btn.clicked.connect(self._pick_theme)
        h3.addWidget(theme_btn)
        self.body.addWidget(theme_row)

        # 壁纸
        wp_row = QFrame()
        wp_row.setObjectName("SettingCard")
        wp_row.setFixedHeight(56)
        h4 = QHBoxLayout(wp_row)
        h4.setContentsMargins(16, 8, 16, 8)
        h4.addWidget(QLabel(i18n.t("wallpaper")))
        h4.addStretch(1)
        wp_btn = QPushButton(i18n.t("change"))
        wp_btn.setFixedWidth(80)
        wp_btn.clicked.connect(self._pick_wallpaper)
        h4.addWidget(wp_btn)
        self.body.addWidget(wp_row)

        self.body.addStretch(1)

    def _on_mode_change(self):
        save_theme_mode(self.mode_combo.currentData())
        app = QApplication.instance()
        app.setStyleSheet(resolve_qss())

    def _on_lang_change(self):
        i18n.set_language(self.lang_combo.currentData())
        app = QApplication.instance()
        for w in app.topLevelWidgets():
            if isinstance(w, MainWindow):
                w.rebuild()
                break

    def _pick_theme(self):
        ThemeDialog(self.window()).exec()

    def _pick_wallpaper(self):
        WallpaperDialog(self.window()).exec()


class KeyboardPage(BasePage):
    CATEGORY_KEY = "keyboard"

    def __init__(self, parent=None):
        super().__init__(NATIVE_KCM["page_keyboard"], parent)
        self.body.addWidget(InfoRow(i18n.t("keyboard_layout"),
                                     action.keyboard_current_layout()))
        self.body.addWidget(InfoRow(i18n.t("input_method"),
                                     action.input_method_current()))
        self.body.addStretch(1)


class MousePage(BasePage):
    CATEGORY_KEY = "mouse"

    def __init__(self, parent=None):
        super().__init__(NATIVE_KCM["page_mouse"], parent)
        self.body.addWidget(InfoRow(i18n.t("mouse_settings"),
                                     action.mouse_current_speed()))
        self.body.addWidget(InfoRow(i18n.t("touchpad"),
                                     action.touchpad_status()))
        self.body.addStretch(1)


class TouchscreenPage(BasePage):
    CATEGORY_KEY = "touchscreen"

    def __init__(self, parent=None):
        super().__init__(NATIVE_KCM["page_touchscreen"], parent)
        self.body.addWidget(InfoRow(i18n.t("touchscreen_settings"),
                                     action.touchscreen_status()))
        self.body.addStretch(1)


class DisplayPage(BasePage):
    CATEGORY_KEY = "display"

    def __init__(self, parent=None):
        super().__init__(NATIVE_KCM["page_display"], parent)

        # 亮度
        self.body.addWidget(self._slider_row(
            i18n.t("brightness"), 1, 100,
            action.brightness_get, action.brightness_set,
            action.brightness_available,
        ))
        # 音量
        self.body.addWidget(self._slider_row(
            i18n.t("volume"), 0, 100,
            action.volume_get, action.volume_set,
            action.volume_available,
        ))

        # 夜间色温开关
        nc_row = QFrame()
        nc_row.setObjectName("SettingCard")
        nc_row.setFixedHeight(56)
        h = QHBoxLayout(nc_row)
        h.setContentsMargins(16, 8, 16, 8)
        h.addWidget(QLabel(i18n.t("nightcolor")))
        h.addStretch(1)
        nc_btn = QPushButton(i18n.t("toggle"))
        nc_btn.setFixedWidth(80)
        nc_btn.clicked.connect(self._toggle_nightcolor)
        h.addWidget(nc_btn)
        self.body.addWidget(nc_row)

        # 屏幕旋转
        rot_row = QFrame()
        rot_row.setObjectName("SettingCard")
        rot_row.setFixedHeight(56)
        h2 = QHBoxLayout(rot_row)
        h2.setContentsMargins(16, 8, 16, 8)
        h2.addWidget(QLabel(i18n.t("rotation")))
        h2.addStretch(1)
        rot_btn = QPushButton(i18n.t("change"))
        rot_btn.setFixedWidth(80)
        rot_btn.clicked.connect(self._pick_rotation)
        h2.addWidget(rot_btn)
        self.body.addWidget(rot_row)

        # 显示器信息
        for out in action.display_list_outputs():
            self.body.addWidget(InfoRow(
                out["name"],
                f"ID {out['id']} · {'connected' if out['connected'] else 'disconnected'}",
            ))

        self.body.addStretch(1)

    def _slider_row(self, label, lo, hi, getter, setter, available) -> QFrame:
        row = QFrame()
        row.setObjectName("SettingCard")
        row.setFixedHeight(64)
        h = QHBoxLayout(row)
        h.setContentsMargins(16, 8, 16, 8)
        h.addWidget(QLabel(label))
        h.addSpacing(14)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(lo, hi)
        if available():
            slider.setValue(getter())
            slider.valueChanged.connect(setter)
        else:
            slider.setEnabled(False)
        h.addWidget(slider, 1)
        return row

    def _toggle_nightcolor(self):
        ok, msg = action.nightcolor_toggle()
        if not ok:
            QMessageBox.warning(self, i18n.t("nightcolor"), msg)

    def _pick_rotation(self):
        DisplayRotationDialog(self.window()).exec()


class NetworkPage(BasePage):
    CATEGORY_KEY = "network"

    def __init__(self, parent=None):
        super().__init__(NATIVE_KCM["page_network"], parent)

        # WiFi 开关
        wifi_row = QFrame()
        wifi_row.setObjectName("SettingCard")
        wifi_row.setFixedHeight(56)
        h = QHBoxLayout(wifi_row)
        h.setContentsMargins(16, 8, 16, 8)
        h.addWidget(QLabel(i18n.t("wifi")))
        h.addStretch(1)
        self.wifi_check = QCheckBox(i18n.t("enable_wifi"))
        if action.wifi_available():
            self.wifi_check.setChecked(action.wifi_enabled())
            self.wifi_check.toggled.connect(action.wifi_set_enabled)
        else:
            self.wifi_check.setEnabled(False)
        h.addWidget(self.wifi_check)
        self.body.addWidget(wifi_row)

        # WiFi 列表（只读展示，双击连接）
        self.wifi_list = QListWidget()
        self.wifi_list.setFixedHeight(180)
        self.wifi_list.itemDoubleClicked.connect(self._wifi_connect)
        self.body.addWidget(self.wifi_list)
        self._refresh_wifi()

        # 蓝牙开关
        bt_row = QFrame()
        bt_row.setObjectName("SettingCard")
        bt_row.setFixedHeight(56)
        h2 = QHBoxLayout(bt_row)
        h2.setContentsMargins(16, 8, 16, 8)
        h2.addWidget(QLabel(i18n.t("bluetooth")))
        h2.addStretch(1)
        self.bt_check = QCheckBox(i18n.t("enable_bluetooth"))
        if action.bluetooth_available():
            self.bt_check.setChecked(action.bluetooth_powered())
            self.bt_check.toggled.connect(action.bluetooth_set_powered)
        else:
            self.bt_check.setEnabled(False)
        h2.addWidget(self.bt_check)
        self.body.addWidget(bt_row)

        # 已配对设备
        for dev in action.bluetooth_paired_devices():
            self.body.addWidget(InfoRow(dev["name"], dev["mac"]))

        self.body.addStretch(1)

    def _refresh_wifi(self):
        self.wifi_list.clear()
        if not action.wifi_available():
            self.wifi_list.addItem(i18n.t("not_found", cmd="nmcli"))
            return
        for net in action.wifi_scan():
            mark = "✓ " if net["in_use"] else ""
            lock = "🔒 " if net["security"] else ""
            item = QListWidgetItem(f"{mark}{lock}{net['ssid']}  ({net['signal']}%)")
            item.setData(Qt.ItemDataRole.UserRole, net)
            self.wifi_list.addItem(item)

    def _wifi_connect(self, item):
        net = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(net, dict):
            return
        password = ""
        if net.get("security"):
            password, ok = QInputDialog.getText(
                self, i18n.t("password_prompt"),
                i18n.t("password_for", ssid=net["ssid"]),
                QLineEdit.EchoMode.Password,
            )
            if not ok:
                return
        ok, msg = action.wifi_connect(net["ssid"], password)
        if not ok:
            QMessageBox.warning(self, i18n.t("connect_failed"), msg)
        self._refresh_wifi()


class UsersPage(BasePage):
    CATEGORY_KEY = "users"

    def __init__(self, parent=None):
        super().__init__(NATIVE_KCM["page_users"], parent)

        # 当前用户
        try:
            current = pwd.getpwuid(os.getuid())
            uname = current.pw_name
            fullname = current.pw_gecos.split(",")[0] or uname
            home = current.pw_dir
        except Exception:
            uname = fullname = home = i18n.t("unknown")

        user_row = QFrame()
        user_row.setObjectName("SettingCard")
        user_row.setFixedHeight(80)
        h = QHBoxLayout(user_row)
        h.setContentsMargins(16, 8, 16, 8)
        h.setSpacing(14)

        avatar = QLabel()
        avatar.setFixedSize(48, 48)
        avatar.setObjectName("CardIcon")
        pm = self._load_avatar(uname)
        if pm and not pm.isNull():
            avatar.setPixmap(pm.scaled(
                48, 48,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ))
        h.addWidget(avatar)

        text_box = QVBoxLayout()
        text_box.setSpacing(2)
        t1 = QLabel(fullname)
        t1.setObjectName("CardTitle")
        t2 = QLabel(f"{uname} · {home}")
        t2.setObjectName("CardDesc")
        text_box.addWidget(t1)
        text_box.addWidget(t2)
        h.addLayout(text_box, 1)
        self.body.addWidget(user_row)

        # 只读展示其他账户
        try:
            for u in pwd.getpwall():
                if u.pw_uid >= 1000 and u.pw_uid < 65534 and u.pw_name != uname:
                    name = u.pw_gecos.split(",")[0] or u.pw_name
                    self.body.addWidget(InfoRow(name, u.pw_name))
        except Exception:
            pass

        self.body.addStretch(1)

    def _load_avatar(self, username: str) -> QPixmap:
        """尝试从常见路径加载用户头像。"""
        candidates = [
            f"/var/lib/AccountsService/icons/{username}",
            os.path.expanduser(f"~/.face"),
            os.path.expanduser(f"~/.face.icon"),
        ]
        for p in candidates:
            if os.path.exists(p):
                pm = QPixmap(p)
                if not pm.isNull():
                    return pm
        return QPixmap()


class UpdatePage(BasePage):
    CATEGORY_KEY = "update"

    def __init__(self, parent=None):
        super().__init__(NATIVE_KCM["page_update"], parent)

        # 电池状态
        info = action.battery_info() if action.battery_available() else None
        if info:
            self.body.addWidget(InfoRow(
                i18n.t("battery"),
                info.get("percent", i18n.t("unknown")),
            ))
            status_map = {
                "charging": i18n.t("battery_charging"),
                "discharging": i18n.t("battery_discharging"),
                "full": i18n.t("battery_full"),
            }
            st = info.get("status", "")
            self.body.addWidget(InfoRow(
                i18n.t("battery_status"),
                status_map.get(st, st or i18n.t("unknown")),
            ))
            if info.get("time_remaining"):
                self.body.addWidget(InfoRow(
                    i18n.t("battery_time"),
                    info["time_remaining"],
                ))
        else:
            self.body.addWidget(InfoRow(i18n.t("battery"), i18n.t("no_battery")))

        # 包管理器
        pm = action.detect_package_manager() or i18n.t("unknown")
        self.body.addWidget(InfoRow(i18n.t("package_manager"), pm))

        # 立即更新按钮
        upd_row = QFrame()
        upd_row.setObjectName("SettingCard")
        upd_row.setFixedHeight(56)
        h = QHBoxLayout(upd_row)
        h.setContentsMargins(16, 8, 16, 8)
        h.addWidget(QLabel(i18n.t("software_update")))
        h.addStretch(1)
        upd_btn = QPushButton(i18n.t("run_update"))
        upd_btn.setFixedWidth(120)
        upd_btn.clicked.connect(lambda: run_update(self.window()))
        h.addWidget(upd_btn)
        self.body.addWidget(upd_row)

        self.body.addStretch(1)


# ---------- 辅助 Dialog（保留原有） ----------

class ThemeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(i18n.t("global_theme"))
        self.resize(420, 500)
        v = QVBoxLayout(self)
        v.setContentsMargins(20, 20, 20, 20)

        v.addWidget(QLabel(i18n.t("global_theme")))
        self.list = QListWidget()
        for name in action.theme_list_lookandfeel():
            self.list.addItem(name)
        self.list.itemDoubleClicked.connect(self.apply)
        v.addWidget(self.list, 1)

        hint = QLabel(i18n.t("double_click_apply"))
        hint.setStyleSheet("color: #888; font-size: 12px;")
        v.addWidget(hint)

    def apply(self, item):
        name = item.text()
        if not action.theme_apply_lookandfeel(name):
            QMessageBox.warning(self, i18n.t("apply_failed"), name)


class WallpaperDialog(QDialog):
    FILL_MODES = [
        ("preserveAspectCrop", "preserveAspectCrop"),
        ("preserveAspectFit",  "preserveAspectFit"),
        ("stretch",            "stretch"),
        ("tile",               "tile"),
        ("tileVertically",     "tileVertically"),
        ("tileHorizontally",   "tileHorizontally"),
        ("pad",                "pad"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(i18n.t("wallpaper"))
        self.resize(560, 540)

        self.current_path = action.wallpaper_current_guess()

        v = QVBoxLayout(self)
        v.setContentsMargins(20, 20, 20, 20)
        v.setSpacing(12)

        self.preview = QLabel(i18n.t("no_image"))
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setFixedHeight(260)
        self.preview.setStyleSheet(
            "background-color: palette(base);"
            "border: 1px solid palette(mid);"
            "border-radius: 8px;"
        )
        v.addWidget(self.preview)

        self.path_label = QLabel(self.current_path or "")
        self.path_label.setStyleSheet("color: #888; font-size: 12px;")
        self.path_label.setWordWrap(True)
        v.addWidget(self.path_label)

        if self.current_path and os.path.exists(self.current_path):
            self._update_preview(self.current_path)

        btn_row = QHBoxLayout()
        pick_btn = QPushButton(i18n.t("select_image"))
        pick_btn.clicked.connect(self.pick_image)
        btn_row.addWidget(pick_btn)

        btn_row.addWidget(QLabel(i18n.t("fill_mode")))
        self.mode_combo = QComboBox()
        for label, _val in self.FILL_MODES:
            self.mode_combo.addItem(label)
        btn_row.addWidget(self.mode_combo, 1)
        v.addLayout(btn_row)

        apply_btn = QPushButton(i18n.t("apply_wallpaper"))
        apply_btn.setFixedHeight(36)
        apply_btn.clicked.connect(self.apply_wallpaper)
        v.addWidget(apply_btn)

        if not action.wallpaper_available():
            warn = QLabel(i18n.t("not_found", cmd="plasma-apply-wallpaperimage"))
            warn.setStyleSheet("color: #c0392b;")
            v.addWidget(warn)
            apply_btn.setEnabled(False)

        v.addStretch(1)

    def _update_preview(self, path: str):
        pm = QPixmap(path)
        if pm.isNull():
            self.preview.setText(i18n.t("no_image"))
            return
        scaled = pm.scaled(
            self.preview.width() - 8,
            self.preview.height() - 8,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.preview.setPixmap(scaled)

    def pick_image(self):
        start_dir = os.path.dirname(self.current_path) if self.current_path else ""
        path, _ = QFileDialog.getOpenFileName(
            self, i18n.t("select_image"), start_dir,
            "Images (*.png *.jpg *.jpeg *.bmp *.webp *.svg);;All (*)",
        )
        if path:
            self.current_path = path
            self.path_label.setText(path)
            self._update_preview(path)

    def apply_wallpaper(self):
        if not self.current_path:
            QMessageBox.information(self, i18n.t("wallpaper"), i18n.t("pick_first"))
            return
        idx = self.mode_combo.currentIndex()
        mode = self.FILL_MODES[idx][1]
        if action.wallpaper_apply(self.current_path, mode):
            QMessageBox.information(self, i18n.t("wallpaper"), i18n.t("applied"))
            self.accept()
        else:
            QMessageBox.warning(self, i18n.t("wallpaper"), i18n.t("apply_failed"))


class DisplayRotationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(i18n.t("rotation"))
        self.resize(420, 320)
        v = QVBoxLayout(self)
        v.setContentsMargins(20, 20, 20, 20)

        if not action.display_available():
            v.addWidget(QLabel(i18n.t("not_found", cmd="kscreen-doctor")))
            return

        outputs = action.display_list_outputs()
        if not outputs:
            v.addWidget(QLabel(i18n.t("no_monitor")))
            return

        for out in outputs:
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{out['name']} (ID {out['id']})"))
            combo = QComboBox()
            combo.addItems(["none", "left", "right", "inverted"])
            current = out.get("rotation", "none")
            if current in ["none", "left", "right", "inverted"]:
                combo.setCurrentText(current)
            combo.currentTextChanged.connect(
                lambda rot, oid=out["id"]: action.display_set_rotation(oid, rot)
            )
            row.addWidget(combo, 1)
            v.addLayout(row)

        v.addStretch(1)


def run_update(parent=None):
    cmd = action.update_command()
    if cmd is None:
        QMessageBox.information(parent, i18n.t("software_update"),
                                "package manager not found")
        return
    terminal = None
    for t in ("konsole", "x-terminal-emulator", "gnome-terminal", "xterm"):
        if shutil.which(t):
            terminal = t
            break
    if terminal is None:
        QMessageBox.warning(parent, i18n.t("software_update"),
                            i18n.t("not_found", cmd="terminal"))
        return

    if terminal == "konsole":
        subprocess.Popen(["konsole", "-e", *cmd])
    elif terminal == "gnome-terminal":
        subprocess.Popen(["gnome-terminal", "--", *cmd])
    else:
        # 不要把 argv 用 " ".join 压成一个字符串交给终端重新分词：
        # 任何含空格的参数（带空格的 Wi-Fi SSID、路径等）都会被拆断。
        subprocess.Popen([terminal, "-e", *cmd])


# ---------- 侧边栏 ----------

class Sidebar(QWidget):
    def __init__(self, on_select, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(260)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title = QLabel(i18n.t("app_title"))
        title.setObjectName("SidebarTitle")
        layout.addWidget(title)

        self.group = QButtonGroup(self)
        self.group.setExclusive(True)

        for i, (cat_key, icon_name, _page) in enumerate(CATEGORIES):
            btn = QPushButton(f"  {i18n.t(cat_key)}")
            btn.setObjectName("NavButton")
            btn.setCheckable(True)
            btn.setIcon(QIcon.fromTheme(icon_name))
            btn.setIconSize(QSize(18, 18))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, idx=i: on_select(idx))
            self.group.addButton(btn, i)
            layout.addWidget(btn)

        layout.addStretch(1)
        self.group.button(0).setChecked(True)


# ---------- 页面映射 ----------

PAGE_CLASSES = {
    "page_system":      SystemPage,
    "page_appearance":  AppearancePage,
    "page_keyboard":    KeyboardPage,
    "page_mouse":       MousePage,
    "page_touchscreen": TouchscreenPage,
    "page_display":     DisplayPage,
    "page_network":     NetworkPage,
    "page_users":       UsersPage,
    "page_update":      UpdatePage,
}


# ---------- 主窗口 ----------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(i18n.t("app_title"))
        self.resize(1000, 680)
        self.setMinimumSize(820, 560)
        self._build()

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        h = QHBoxLayout(central)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        # 右侧容器（每次切换销毁重建）
        self.content_holder = QWidget()
        self.content_layout = QVBoxLayout(self.content_holder)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        self.sidebar = Sidebar(self.on_nav)

        h.addWidget(self.sidebar)
        h.addWidget(self.content_holder, 1)

        self.on_nav(0)

    def rebuild(self):
        self.setWindowTitle(i18n.t("app_title"))
        # 记住当前分类
        cur_idx = 0
        for i, (_k, _i, _p) in enumerate(CATEGORIES):
            if self.sidebar.group.button(i) and self.sidebar.group.button(i).isChecked():
                cur_idx = i
                break

        old_central = self.centralWidget()
        self._build()
        if old_central is not None:
            old_central.deleteLater()
        self.sidebar.group.button(cur_idx).setChecked(True)
        self.on_nav(cur_idx)

    def on_nav(self, idx: int):
        # 清空右侧
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        cat_key, icon_name, page_id = CATEGORIES[idx]
        PageCls = PAGE_CLASSES.get(page_id)
        if PageCls is None:
            placeholder = QLabel(f"Page not implemented: {page_id}")
            placeholder.setObjectName("CategoryTitle")
            self.content_layout.addWidget(placeholder)
            return
        page = PageCls(self.content_holder)
        self.content_layout.addWidget(page)


# ---------- 入口 ----------

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("KDE Settings Shell")

    i18n.set_language(i18n.detect_system_language())
    app.setStyleSheet(resolve_qss())

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()