# action.py
import subprocess
import shutil
import re
import os
import glob
import configparser


def _run(cmd: list[str], timeout: int = 5) -> tuple[bool, str]:
    """执行命令，返回 (成功?, 输出或错误)。"""
    try:
        out = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, timeout=timeout
        ).decode().strip()
        return True, out
    except subprocess.CalledProcessError as e:
        return False, e.output.decode().strip() if e.output else str(e)
    except FileNotFoundError:
        return False, f"命令不存在: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return False, "命令超时"


def _run_input(cmd: list[str], stdin_text: str, timeout: int = 30) -> tuple[bool, str]:
    """执行命令，并把 stdin_text 喂给它的标准输入。

    用于传递密码这类敏感信息：走 stdin 不会出现在进程参数里，
    同机其他用户执行 `ps` 时看不到。
    """
    try:
        proc = subprocess.run(
            cmd, input=stdin_text, capture_output=True, text=True, timeout=timeout
        )
        return proc.returncode == 0, (proc.stdout + proc.stderr).strip()
    except FileNotFoundError:
        return False, f"命令不存在: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return False, "命令超时"


# ---------- 亮度 ----------

def brightness_available() -> bool:
    return shutil.which("brightnessctl") is not None


def brightness_get() -> int:
    ok, out = _run(["brightnessctl", "get"])
    if not ok:
        return 50
    try:
        cur = int(out)
    except ValueError:
        return 50
    ok, max_out = _run(["brightnessctl", "max"])
    if not ok:
        return 50
    try:
        return int(cur / int(max_out) * 100)
    except (ValueError, ZeroDivisionError):
        return 50


def brightness_set(percent: int):
    _run(["brightnessctl", "set", f"{percent}%"])


# ---------- 音量 ----------

def volume_available() -> bool:
    return shutil.which("wpctl") is not None or shutil.which("pactl") is not None


def volume_get() -> int:
    if shutil.which("wpctl"):
        ok, out = _run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"])
        if ok:
            try:
                return int(float(out.split()[-1]) * 100)
            except (ValueError, IndexError):
                pass
    if shutil.which("pactl"):
        ok, out = _run(["pactl", "get-sink-volume", "@DEFAULT_SINK@"])
        if ok:
            for token in out.split():
                if token.endswith("%"):
                    try:
                        return int(token.rstrip("%"))
                    except ValueError:
                        pass
    return 50


def volume_set(percent: int):
    if shutil.which("wpctl"):
        _run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{percent}%"])
    elif shutil.which("pactl"):
        _run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{percent}%"])


# ---------- 主题 / 配色 / 图标 / 光标 ----------

def theme_list_lookandfeel() -> list[str]:
    ok, out = _run(["plasma-apply-lookandfeel", "--list"])
    if not ok:
        return []
    result = []
    for line in out.splitlines():
        line = line.strip()
        if line and not line.startswith(" "):
            result.append(line.split()[0])
    return result


def theme_apply_lookandfeel(name: str) -> bool:
    ok, _ = _run(["plasma-apply-lookandfeel", "--apply", name])
    return ok


def theme_apply_colorscheme(name: str) -> bool:
    ok, _ = _run(["plasma-apply-colorscheme", name])
    return ok


def theme_apply_icontheme(name: str) -> bool:
    ok, _ = _run(["plasma-apply-icontheme", name])
    return ok


def theme_apply_cursortheme(name: str) -> bool:
    ok, _ = _run(["plasma-apply-cursortheme", name])
    return ok


# ---------- 壁纸 ----------

def wallpaper_available() -> bool:
    return shutil.which("plasma-apply-wallpaperimage") is not None


def wallpaper_apply(image_path: str, fill_mode: str = "preserveAspectCrop") -> bool:
    ok, _ = _run(
        ["plasma-apply-wallpaperimage", "--fill-mode", fill_mode, image_path],
        timeout=10,
    )
    return ok


def wallpaper_current_guess() -> str:
    path = os.path.expanduser("~/.config/plasma-org.kde.plasma.desktop-appletsrc")
    if not os.path.exists(path):
        return ""
    try:
        cfg = configparser.ConfigParser(strict=False)
        cfg.read(path, encoding="utf-8")
        for section in cfg.sections():
            if "Wallpaper" in section and "Image" in section:
                for key in ("Image", "wallpaper"):
                    if cfg.has_option(section, key):
                        val = cfg.get(section, key)
                        if val and val.startswith("/"):
                            return val
    except Exception:
        pass
    return ""


# ---------- WiFi ----------

def wifi_available() -> bool:
    return shutil.which("nmcli") is not None


def wifi_enabled() -> bool:
    ok, out = _run(["nmcli", "radio", "wifi"])
    return ok and "enabled" in out


def wifi_set_enabled(on: bool):
    _run(["nmcli", "radio", "wifi", "on" if on else "off"])


def wifi_scan() -> list[dict]:
    _run(["nmcli", "device", "wifi", "rescan"], timeout=10)

    ok, out = _run(["nmcli", "-t", "-f",
                    "IN-USE,SSID,SIGNAL,SECURITY", "device", "wifi", "list"],
                   timeout=10)
    if not ok:
        return []

    seen = {}
    for line in out.splitlines():
        parts = line.replace("\\:", "\x00").split(":")
        if len(parts) < 4:
            continue
        in_use = parts[0].strip() == "*"
        ssid = parts[1].replace("\x00", ":").strip()
        try:
            signal = int(parts[2])
        except ValueError:
            signal = 0
        security = parts[3].strip()
        if not ssid:
            continue
        if ssid not in seen or signal > seen[ssid]["signal"]:
            seen[ssid] = {
                "ssid": ssid,
                "signal": signal,
                "security": security,
                "in_use": in_use,
            }
    return sorted(seen.values(), key=lambda x: x["signal"], reverse=True)


def wifi_connect(ssid: str, password: str = "") -> tuple[bool, str]:
    """连接 Wi-Fi。

    密码通过 stdin 交给 nmcli --ask，绝不作为命令行参数 ——
    否则密码会留在 argv 里，同机任何用户 `ps` 一下就能看到明文。
    """
    if not password:
        return _run(["nmcli", "device", "wifi", "connect", ssid], timeout=30)
    return _run_input(
        ["nmcli", "--ask", "device", "wifi", "connect", ssid],
        password + "\n",
        timeout=30,
    )


def wifi_disconnect(ssid: str):
    _run(["nmcli", "connection", "down", ssid])


# ---------- 蓝牙 ----------

def bluetooth_available() -> bool:
    return shutil.which("bluetoothctl") is not None


def bluetooth_powered() -> bool:
    ok, out = _run(["bluetoothctl", "show"])
    return ok and "Powered: yes" in out


def bluetooth_set_powered(on: bool):
    _run(["bluetoothctl", "power", "on" if on else "off"])


def bluetooth_scan(seconds: int = 8) -> list[dict]:
    ok, out = _run(
        ["bluetoothctl", "--timeout", str(seconds), "scan", "on"],
        timeout=seconds + 5,
    )
    devices = {}
    for line in out.splitlines():
        if "Device" not in line:
            continue
        parts = line.split("Device", 1)[1].strip().split(" ", 1)
        if len(parts) < 2:
            continue
        mac, name = parts[0], parts[1]
        devices[mac] = name
    return [{"mac": m, "name": n} for m, n in devices.items()]


def bluetooth_connect(mac: str) -> bool:
    ok, _ = _run(["bluetoothctl", "connect", mac], timeout=15)
    return ok


def bluetooth_paired_devices() -> list[dict]:
    ok, out = _run(["bluetoothctl", "devices", "Paired"])
    if not ok:
        return []
    result = []
    for line in out.splitlines():
        if not line.startswith("Device"):
            continue
        parts = line.split(" ", 2)
        if len(parts) >= 3:
            result.append({"mac": parts[1], "name": parts[2]})
    return result


# ---------- 夜间色温 ----------

def nightcolor_available() -> bool:
    for qdbus in ("qdbus6", "qdbus", "qdbus-qt6", "qdbus-qt5"):
        if shutil.which(qdbus):
            return True
    return False


def nightcolor_toggle() -> tuple[bool, str]:
    for qdbus in ("qdbus6", "qdbus", "qdbus-qt6", "qdbus-qt5"):
        if shutil.which(qdbus):
            ok, out = _run(
                [qdbus, "org.kde.kglobalaccel", "/component/kwin",
                 "invokeShortcut", "Toggle Night Color"],
                timeout=5,
            )
            return ok, out
    return False, "找不到 qdbus 命令"


# ---------- 显示 ----------

def display_available() -> bool:
    return shutil.which("kscreen-doctor") is not None


def display_list_outputs() -> list[dict]:
    ok, out = _run(["kscreen-doctor", "--outputs"])
    if not ok:
        return []
    outputs = []
    current = None
    for line in out.splitlines():
        line = line.rstrip()
        m = re.match(r"^(\d+)\s+(\S+)\s+(\w+)\s+(\w+)", line)
        if m:
            if current:
                outputs.append(current)
            current = {
                "id": m.group(1),
                "name": m.group(2),
                "enabled": m.group(3) == "enabled",
                "connected": m.group(4) == "connected",
            }
        elif current and "rotation:" in line.lower():
            for rot in ("none", "left", "right", "inverted"):
                if rot in line.lower():
                    current["rotation"] = rot
                    break
    if current:
        outputs.append(current)
    return outputs


def display_set_rotation(output_id: str, rotation: str) -> bool:
    ok, _ = _run(
        ["kscreen-doctor", f"output.{output_id}.rotation.{rotation}"],
        timeout=5,
    )
    return ok


# ---------- 电池 ----------

def battery_available() -> bool:
    return shutil.which("upower") is not None or shutil.which("acpi") is not None


def battery_info() -> dict | None:
    if shutil.which("upower"):
        ok, out = _run(["upower", "-e"])
        if ok:
            for line in out.splitlines():
                if "battery" in line.lower() or "BAT" in line:
                    ok2, info = _run(["upower", "-i", line.strip()])
                    if not ok2:
                        continue
                    result = {}
                    for ln in info.splitlines():
                        ln = ln.strip()
                        if ln.startswith("percentage:"):
                            result["percent"] = ln.split(":", 1)[1].strip()
                        elif ln.startswith("state:"):
                            result["status"] = ln.split(":", 1)[1].strip()
                        elif ln.startswith("time to empty:"):
                            result["time_remaining"] = ln.split(":", 1)[1].strip()
                        elif ln.startswith("time to full:"):
                            result["time_remaining"] = ln.split(":", 1)[1].strip()
                    if result:
                        return result
    if shutil.which("acpi"):
        ok, out = _run(["acpi", "-b"])
        if ok and "Battery" in out:
            m = re.search(r"(\d+)%", out)
            result = {"percent": f"{m.group(1)}%" if m else "未知"}
            if "Charging" in out:
                result["status"] = "charging"
            elif "Discharging" in out:
                result["status"] = "discharging"
            elif "Full" in out:
                result["status"] = "full"
            m2 = re.search(r"(\d+:\d+:\d+) remaining", out)
            if m2:
                result["time_remaining"] = m2.group(1)
            return result
    return None


# ---------- 键盘 / 鼠标 / 触摸屏（只读展示） ----------

def keyboard_current_layout() -> str:
    path = os.path.expanduser("~/.config/kxkbrc")
    if not os.path.exists(path):
        return "en"
    try:
        cfg = configparser.ConfigParser(strict=False)
        cfg.read(path, encoding="utf-8")
        return cfg.get("Layout", "LayoutList", fallback="en")
    except Exception:
        return "en"


def input_method_current() -> str:
    for var in ("GTK_IM_MODULE", "QT_IM_MODULE", "XMODIFIERS"):
        val = os.environ.get(var)
        if val:
            return val
    return "ibus"


def mouse_current_speed() -> str:
    path = os.path.expanduser("~/.config/kcminputrc")
    if not os.path.exists(path):
        return "0"
    try:
        cfg = configparser.ConfigParser(strict=False)
        cfg.read(path, encoding="utf-8")
        return cfg.get("Mouse", "PointerAcceleration", fallback="0")
    except Exception:
        return "0"


def touchpad_status() -> str:
    for p in glob.glob("/sys/class/input/event*/device/name"):
        try:
            with open(p, "r") as f:
                name = f.read().strip().lower()
                if "touchpad" in name or "synaptics" in name:
                    return "present"
        except OSError:
            continue
    return "absent"


def touchscreen_status() -> str:
    for p in glob.glob("/sys/class/input/event*/device/name"):
        try:
            with open(p, "r") as f:
                name = f.read().lower()
                if "touchscreen" in name or "touch screen" in name:
                    return "present"
        except OSError:
            continue
    return "absent"


# ---------- 系统更新 ----------

def detect_package_manager() -> str | None:
    for name in ("pacman", "apt", "dnf", "zypper", "apk"):
        if shutil.which(name):
            return name
    return None


def update_command() -> list[str] | None:
    pm = detect_package_manager()
    if pm == "pacman":
        return ["pkexec", "pacman", "-Syu"]
    if pm == "apt":
        return ["pkexec", "bash", "-c", "apt update && apt upgrade -y"]
    if pm == "dnf":
        return ["pkexec", "dnf", "upgrade", "-y"]
    if pm == "zypper":
        return ["pkexec", "zypper", "update"]
    if pm == "apk":
        return ["pkexec", "apk", "upgrade"]
    return None