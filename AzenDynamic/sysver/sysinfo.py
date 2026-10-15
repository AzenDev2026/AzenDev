#!/usr/bin/env python3
"""
系统版本信息查看工具 (类似 Windows 的 winver)
- PyQt6 实现，原生 Wayland 支持
- 智能图片缩放（QLabel + scaled pixmap）
- 多语言支持
- 详细硬件信息
- conf.txt 支持多行系统名称
"""

import os
import sys
import platform
import locale
import subprocess
import re
import shutil
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QGridLayout, QPushButton, QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtGui import QPixmap, QFont, QPainter, QColor, QPen
from PyQt6.QtCore import Qt


# ============ 多语言翻译表 ============
TRANSLATIONS = {
    "zh_CN": {
        "title": "关于本系统", "os_name": "操作系统", "desktop": "桌面环境",
        "desktop_ver": "桌面版本", "kernel": "内核版本", "arch": "系统架构",
        "cpu": "处理器", "cpu_cores": "核心数", "memory": "内存",
        "gpu": "显卡", "disk": "磁盘", "motherboard": "主板",
        "bios": "BIOS", "hostname": "主机名", "uptime": "运行时间",
        "ok": "确定", "unknown": "未知", "hardware": "硬件型号",
    },
    "zh_TW": {
        "title": "關於本系統", "os_name": "作業系統", "desktop": "桌面環境",
        "desktop_ver": "桌面版本", "kernel": "核心版本", "arch": "系統架構",
        "cpu": "處理器", "cpu_cores": "核心數", "memory": "記憶體",
        "gpu": "顯示卡", "disk": "磁碟", "motherboard": "主機板",
        "bios": "BIOS", "hostname": "主機名", "uptime": "運行時間",
        "ok": "確定", "unknown": "未知", "hardware": "硬體型號",
    },
    "en_US": {
        "title": "About This System", "os_name": "OS", "desktop": "Desktop Environment",
        "desktop_ver": "Desktop Version", "kernel": "Kernel Version", "arch": "Architecture",
        "cpu": "Processor", "cpu_cores": "Cores", "memory": "Memory",
        "gpu": "Graphics", "disk": "Disk", "motherboard": "Motherboard",
        "bios": "BIOS", "hostname": "Hostname", "uptime": "Uptime",
        "ok": "OK", "unknown": "Unknown", "hardware": "Hardware Model",
    },
    "ja_JP": {
        "title": "システムについて", "os_name": "OS", "desktop": "デスクトップ環境",
        "desktop_ver": "デスクトップ版", "kernel": "カーネルバージョン", "arch": "アーキテクチャ",
        "cpu": "プロセッサ", "cpu_cores": "コア数", "memory": "メモリ",
        "gpu": "グラフィックス", "disk": "ディスク", "motherboard": "マザーボード",
        "bios": "BIOS", "hostname": "ホスト名", "uptime": "稼働時間",
        "ok": "OK", "unknown": "不明", "hardware": "ハードウェアモデル",
    },
    "ko_KR": {
        "title": "시스템 정보", "os_name": "OS", "desktop": "데스크톱 환경",
        "desktop_ver": "데스크톱 버전", "kernel": "커널 버전", "arch": "시스템 아키텍처",
        "cpu": "프로세서", "cpu_cores": "코어 수", "memory": "메모리",
        "gpu": "그래픽", "disk": "디스크", "motherboard": "메인보드",
        "bios": "BIOS", "hostname": "호스트 이름", "uptime": "가동 시간",
        "ok": "확인", "unknown": "알 수 없음", "hardware": "하드웨어 모델",
    },
    "de_DE": {
        "title": "Über dieses System", "os_name": "Betriebssystem", "desktop": "Desktop-Umgebung",
        "desktop_ver": "Desktop-Version", "kernel": "Kernel-Version", "arch": "Architektur",
        "cpu": "Prozessor", "cpu_cores": "Kerne", "memory": "Arbeitsspeicher",
        "gpu": "Grafik", "disk": "Festplatte", "motherboard": "Hauptplatine",
        "bios": "BIOS", "hostname": "Hostname", "uptime": "Betriebszeit",
        "ok": "OK", "unknown": "Unbekannt", "hardware": "Hardware-Modell",
    },
    "fr_FR": {
        "title": "À propos du système", "os_name": "Système", "desktop": "Environnement de bureau",
        "desktop_ver": "Version du bureau", "kernel": "Version du noyau", "arch": "Architecture",
        "cpu": "Processeur", "cpu_cores": "Cœurs", "memory": "Mémoire",
        "gpu": "Graphique", "disk": "Disque", "motherboard": "Carte mère",
        "bios": "BIOS", "hostname": "Nom d'hôte", "uptime": "Durée de fonctionnement",
        "ok": "OK", "unknown": "Inconnu", "hardware": "Modèle matériel",
    },
    "es_ES": {
        "title": "Acerca de este sistema", "os_name": "SO", "desktop": "Entorno de escritorio",
        "desktop_ver": "Versión del escritorio", "kernel": "Versión del kernel", "arch": "Arquitectura",
        "cpu": "Procesador", "cpu_cores": "Núcleos", "memory": "Memoria",
        "gpu": "Gráficos", "disk": "Disco", "motherboard": "Placa base",
        "bios": "BIOS", "hostname": "Nombre de host", "uptime": "Tiempo activo",
        "ok": "Aceptar", "unknown": "Desconocido", "hardware": "Modelo de hardware",
    },
    "ru_RU": {
        "title": "О системе", "os_name": "ОС", "desktop": "Рабочая среда",
        "desktop_ver": "Версия среды", "kernel": "Версия ядра", "arch": "Архитектура",
        "cpu": "Процессор", "cpu_cores": "Ядра", "memory": "Память",
        "gpu": "Графика", "disk": "Диск", "motherboard": "Материнская плата",
        "bios": "BIOS", "hostname": "Имя хоста", "uptime": "Время работы",
        "ok": "ОК", "unknown": "Неизвестно", "hardware": "Модель оборудования",
    },
    "pt_BR": {
        "title": "Sobre este sistema", "os_name": "SO", "desktop": "Ambiente de desktop",
        "desktop_ver": "Versão do desktop", "kernel": "Versão do kernel", "arch": "Arquitetura",
        "cpu": "Processador", "cpu_cores": "Núcleos", "memory": "Memória",
        "gpu": "Gráficos", "disk": "Disco", "motherboard": "Placa-mãe",
        "bios": "BIOS", "hostname": "Nome do host", "uptime": "Tempo ativo",
        "ok": "OK", "unknown": "Desconhecido", "hardware": "Modelo de hardware",
    },
}


def detect_language():
    candidates = []
    for env_var in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        val = os.environ.get(env_var, "")
        if val:
            candidates.append(val)
    try:
        loc = locale.getdefaultlocale()[0]
        if loc:
            candidates.append(loc)
    except Exception:
        pass
    for cand in candidates:
        if not cand:
            continue
        norm = cand.split(".")[0].split("@")[0].replace("-", "_")
        if not norm:
            continue
        if norm in TRANSLATIONS:
            return norm
        parts = norm.split("_")
        lang = parts[0].lower()
        if lang == "zh":
            region = parts[1].upper() if len(parts) > 1 else ""
            if region in ("TW", "HK", "MO") or "HANT" in norm.upper():
                return "zh_TW"
            return "zh_CN"
        for key in TRANSLATIONS:
            if key.lower().startswith(lang + "_"):
                return key
    return "en_US"


def configure_wayland():
    if platform.system() != "Linux":
        return
    if os.environ.get("QT_QPA_PLATFORM"):
        return
    session = os.environ.get("XDG_SESSION_TYPE", "").lower()
    wayland_display = os.environ.get("WAYLAND_DISPLAY", "")
    if session == "wayland" or wayland_display:
        os.environ["QT_QPA_PLATFORM"] = "wayland;xcb"


# ============ 工具函数 ============
def run(cmd, timeout=3):
    """执行命令，返回 stdout（失败返回空字符串）"""
    try:
        return subprocess.check_output(
            cmd, stderr=subprocess.DEVNULL, timeout=timeout
        ).decode("utf-8", errors="ignore").strip()
    except Exception:
        return ""


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    except Exception:
        return ""


def bytes_to_human(n):
    """字节转人类可读"""
    try:
        n = float(n)
    except Exception:
        return "未知"
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if n < 1024:
            return f"{n:.1f} {unit}" if unit != "B" else f"{int(n)} B"
        n /= 1024
    return f"{n:.1f} EB"


# ============ 硬件信息采集器 ============
class InfoCollector:
    def __init__(self, t):
        self.t = t
        self.unknown = t["unknown"]

    def collect(self):
        """返回有序的 (标签, 值) 列表"""
        system = platform.system()
        rows = []

        # 系统名称 / 版本
        self._add_os_rows(rows, system)

        # 硬件
        self._add_cpu_rows(rows, system)
        self._add_memory_rows(rows, system)
        self._add_gpu_rows(rows, system)
        self._add_disk_rows(rows, system)
        self._add_board_rows(rows, system)

        # 主机名 & 运行时间
        try:
            hostname = platform.node()
            if hostname:
                rows.append((self.t["hostname"], hostname))
        except Exception:
            pass

        uptime = self._get_uptime(system)
        if uptime:
            rows.append((self.t["uptime"], uptime))

        return rows

    # ---------- OS ----------
    def _add_os_rows(self, rows, system):
        if system == "Linux":
            desktop = os.environ.get("XDG_CURRENT_DESKTOP", "") or os.environ.get("DESKTOP_SESSION", "")
            if desktop:
                rows.append((self.t["desktop"], desktop))
                ver = self._linux_desktop_version(desktop)
                if ver:
                    rows.append((self.t["desktop_ver"], ver))
            rows.append((self.t["kernel"], platform.release() or self.unknown))
            rows.append((self.t["arch"], platform.machine() or self.unknown))
        elif system == "Windows":
            rows.append((self.t["os_name"], f"Windows {platform.release()}"))
            rows.append((self.t["kernel"], platform.version() or self.unknown))
            rows.append((self.t["arch"], platform.machine() or self.unknown))
        elif system == "Darwin":
            rows.append((self.t["os_name"], f"macOS {platform.mac_ver()[0]}"))
            rows.append((self.t["desktop"], "Aqua"))
            rows.append((self.t["kernel"], platform.release() or self.unknown))
            rows.append((self.t["arch"], platform.machine() or self.unknown))
        else:
            rows.append((self.t["kernel"], platform.release() or self.unknown))
            rows.append((self.t["arch"], platform.machine() or self.unknown))

    def _linux_desktop_version(self, desktop):
        d = desktop.upper()
        try:
            if "GNOME" in d:
                out = run(["gnome-shell", "--version"])
                if out:
                    return out
                return self._pkg_version("gnome-shell")
            elif "KDE" in d or "PLASMA" in d:
                out = run(["plasmashell", "--version"])
                if out:
                    return out
                return self._pkg_version("plasma-desktop")
            elif "XFCE" in d:
                return self._pkg_version("xfce4")
            elif "MATE" in d:
                return self._pkg_version("mate-desktop")
            elif "CINNAMON" in d:
                return self._pkg_version("cinnamon")
            elif "SWAY" in d:
                return run(["sway", "--version"]).splitlines()[0] if run(["sway", "--version"]) else ""
            elif "HYPRLAND" in d:
                return run(["hyprctl", "version"]).splitlines()[0] if run(["hyprctl", "version"]) else ""
        except Exception:
            pass
        return ""

    def _pkg_version(self, pkg):
        if shutil.which("dpkg"):
            out = run(["dpkg", "-s", pkg])
            m = re.search(r"Version:\s*(\S+)", out)
            if m:
                return m.group(1)
        if shutil.which("rpm"):
            out = run(["rpm", "-q", "--qf", "%{VERSION}", pkg])
            if out and "not installed" not in out:
                return out
        if shutil.which("pacman"):
            out = run(["pacman", "-Q", pkg])
            if out:
                return out.split()[-1] if " " in out else out
        return ""

    # ---------- CPU ----------
    def _add_cpu_rows(self, rows, system):
        cpu = self.unknown
        cores = ""

        if system == "Linux":
            # 从 /proc/cpuinfo 提取
            try:
                with open("/proc/cpuinfo") as f:
                    for line in f:
                        if line.startswith("model name"):
                            cpu = line.split(":", 1)[1].strip()
                            break
            except Exception:
                pass
            # 核心数：物理核心数（unique core id）
            try:
                core_ids = set()
                phys_id = 0
                with open("/proc/cpuinfo") as f:
                    cur_phys = 0
                    for line in f:
                        if line.startswith("physical id"):
                            cur_phys = line.split(":", 1)[1].strip()
                        elif line.startswith("core id"):
                            core_ids.add((cur_phys, line.split(":", 1)[1].strip()))
                if core_ids:
                    phys = len(core_ids)
                else:
                    phys = os.cpu_count() or 0
                log = os.cpu_count() or 0
                cores = f"{phys} 物理 / {log} 逻辑"
            except Exception:
                cores = f"{os.cpu_count() or 0}"
        elif system == "Windows":
            out = run(["wmic", "cpu", "get", "name"], timeout=5)
            lines = [l.strip() for l in out.splitlines() if l.strip()]
            if len(lines) > 1:
                cpu = lines[1]
            cores = str(os.cpu_count() or "")
        elif system == "Darwin":
            cpu = run(["sysctl", "-n", "machdep.cpu.brand_string"])
            if not cpu:
                cpu = platform.processor()
            cores = str(os.cpu_count() or "")

        rows.append((self.t["cpu"], cpu or self.unknown))
        if cores:
            rows.append((self.t["cpu_cores"], cores))

    # ---------- 内存 ----------
    def _add_memory_rows(self, rows, system):
        mem = ""
        if system == "Linux":
            try:
                with open("/proc/meminfo") as f:
                    for line in f:
                        if line.startswith("MemTotal:"):
                            kb = int(line.split()[1])
                            mem = bytes_to_human(kb * 1024)
                            break
            except Exception:
                pass
        elif system == "Windows":
            out = run(["wmic", "computersystem", "get", "TotalPhysicalMemory"], timeout=5)
            lines = [l.strip() for l in out.splitlines() if l.strip()]
            if len(lines) > 1 and lines[1].isdigit():
                mem = bytes_to_human(int(lines[1]))
        elif system == "Darwin":
            out = run(["sysctl", "-n", "hw.memsize"])
            if out.isdigit():
                mem = bytes_to_human(int(out))
        if mem:
            rows.append((self.t["memory"], mem))

    # ---------- GPU ----------
    def _add_gpu_rows(self, rows, system):
        gpus = []
        if system == "Linux":
            # 优先 lspci
            if shutil.which("lspci"):
                out = run(["lspci"])
                for line in out.splitlines():
                    if re.search(r"VGA compatible controller|3D controller|Display controller", line):
                        # 去掉前导 PCI 地址
                        desc = line.split(":", 2)[-1].strip()
                        gpus.append(desc)
            # 备选：drm
            if not gpus and os.path.isdir("/sys/class/drm"):
                for entry in os.listdir("/sys/class/drm"):
                    if entry.startswith("card") and "-" not in entry:
                        vendor_path = f"/sys/class/drm/{entry}/device/vendor"
                        dev_path = f"/sys/class/drm/{entry}/device/device"
                        v = read_file(vendor_path)
                        d = read_file(dev_path)
                        if v or d:
                            gpus.append(f"{v} {d}".strip())
        elif system == "Windows":
            out = run(["wmic", "path", "win32_videocontroller", "get", "name"], timeout=5)
            lines = [l.strip() for l in out.splitlines() if l.strip()]
            if len(lines) > 1:
                gpus = lines[1:]
        elif system == "Darwin":
            out = run(["system_profiler", "SPDisplaysDataType"], timeout=8)
            for line in out.splitlines():
                if "Chipset Model" in line:
                    gpus.append(line.split(":", 1)[1].strip())

        # 去重
        seen = set()
        uniq = []
        for g in gpus:
            if g not in seen:
                seen.add(g)
                uniq.append(g)

        for g in uniq[:3]:  # 最多显示3个
            rows.append((self.t["gpu"], g))

    # ---------- 磁盘 ----------
    def _add_disk_rows(self, rows, system):
        disks = []
        if system == "Linux":
            if shutil.which("lsblk"):
                out = run(["lsblk", "-d", "-n", "-o", "NAME,SIZE,MODEL"])
                for line in out.splitlines():
                    parts = line.split(None, 2)
                    if len(parts) >= 2:
                        name, size = parts[0], parts[1]
                        model = parts[2].strip() if len(parts) > 2 else ""
                        disks.append(f"/dev/{name}  {size}  {model}".strip())
        elif system == "Windows":
            out = run(["wmic", "diskdrive", "get", "model,size"], timeout=5)
            for line in out.splitlines()[1:]:
                line = line.strip()
                if not line:
                    continue
                m = re.match(r"(.+?)\s+(\d+)$", line)
                if m:
                    model = m.group(1).strip()
                    size = bytes_to_human(int(m.group(2)))
                    disks.append(f"{model}  {size}")
        elif system == "Darwin":
            out = run(["diskutil", "list"], timeout=5)
            for line in out.splitlines():
                if "disk" in line and "GB" in line or "TB" in line:
                    disks.append(line.strip())

        for d in disks[:4]:
            rows.append((self.t["disk"], d))

    # ---------- 主板 / BIOS ----------
    def _add_board_rows(self, rows, system):
        if system == "Linux":
            board_vendor = read_file("/sys/devices/virtual/dmi/id/board_vendor")
            board_name = read_file("/sys/devices/virtual/dmi/id/board_name")
            board_ver = read_file("/sys/devices/virtual/dmi/id/board_version")
            if board_name and board_name != "None":
                text = f"{board_vendor} {board_name}".strip()
                if board_ver and board_ver != "None":
                    text += f"  ({board_ver})"
                rows.append((self.t["motherboard"], text))

            bios_vendor = read_file("/sys/devices/virtual/dmi/id/bios_vendor")
            bios_ver = read_file("/sys/devices/virtual/dmi/id/bios_version")
            bios_date = read_file("/sys/devices/virtual/dmi/id/bios_date")
            if bios_ver and bios_ver != "None":
                text = f"{bios_vendor} {bios_ver}".strip()
                if bios_date and bios_date != "None":
                    text += f"  ({bios_date})"
                rows.append((self.t["bios"], text))

            # 产品型号（整机）
            product_name = read_file("/sys/devices/virtual/dmi/id/product_name")
            sys_vendor = read_file("/sys/devices/virtual/dmi/id/sys_vendor")
            if product_name and product_name != "None":
                rows.append((self.t["hardware"], f"{sys_vendor} {product_name}".strip()))
        elif system == "Windows":
            out = run(["wmic", "baseboard", "get", "manufacturer,product"], timeout=5)
            lines = [l.strip() for l in out.splitlines() if l.strip()]
            if len(lines) > 1:
                rows.append((self.t["motherboard"], lines[1]))
            out = run(["wmic", "bios", "get", "manufacturer,smbiosbiosversion"], timeout=5)
            lines = [l.strip() for l in out.splitlines() if l.strip()]
            if len(lines) > 1:
                rows.append((self.t["bios"], lines[1]))
        elif system == "Darwin":
            out = run(["system_profiler", "SPHardwareDataType"], timeout=8)
            for line in out.splitlines():
                if "Model Name" in line or "Model Identifier" in line:
                    rows.append((self.t["hardware"], line.split(":", 1)[1].strip()))

    # ---------- Uptime ----------
    def _get_uptime(self, system):
        if system == "Linux":
            try:
                with open("/proc/uptime") as f:
                    secs = float(f.read().split()[0])
                return self._format_uptime(secs)
            except Exception:
                return ""
        elif system == "Windows":
            out = run(["wmic", "os", "get", "lastbootuptime"], timeout=5)
            return ""  # 解析复杂，跳过
        elif system == "Darwin":
            out = run(["sysctl", "-n", "kern.boottime"])
            m = re.search(r"sec\s*=\s*(\d+)", out)
            if m:
                import time
                secs = time.time() - int(m.group(1))
                return self._format_uptime(secs)
        return ""

    def _format_uptime(self, secs):
        secs = int(secs)
        days, rem = divmod(secs, 86400)
        hours, rem = divmod(rem, 3600)
        mins = rem // 60
        parts = []
        if days:
            parts.append(f"{days}天")
        if hours:
            parts.append(f"{hours}小时")
        parts.append(f"{mins}分钟")
        return " ".join(parts)


# ============ 占位 logo ============
class PlaceholderLogo(QWidget):
    def __init__(self, size=96, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#4a90d9"))
        painter.setPen(QPen(QColor("#2c5f8d"), 2))
        painter.drawEllipse(4, 4, self.width() - 8, self.height() - 8)
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Sans", 14, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "OS")


# ============ 主窗口 ============
class SystemInfoApp(QWidget):
    LOGO_MAX_SIZE = 96

    def __init__(self):
        super().__init__()

        self.lang = detect_language()
        self.t = TRANSLATIONS.get(self.lang, TRANSLATIONS["en_US"])

        self.setWindowTitle(self.t["title"])
        self.resize(520, 640)  # 更大窗口容纳更多信息

        self.script_dir = Path(__file__).parent.resolve()

        self.custom_name_lines = self.read_conf()  # list of str 或 None
        self.info = self.collect_system_name()

        self.build_ui()

    # ---------- 解析 conf.txt（支持多行） ----------
    def read_conf(self):
        """
        支持格式：
            {sysver}:
            my-custom-OS
            version1

            {other}:
            ...

        返回 {sysver}: 之后到下一个 {xxx}: 或文件末尾之间的所有非空行。
        """
        conf_path = self.script_dir / "conf.txt"
        if not conf_path.exists():
            return None
        try:
            with open(conf_path, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
        except Exception as e:
            print(f"读取 conf.txt 失败: {e}")
            return None

        # 找 {sysver}: 的位置
        start = None
        for i, line in enumerate(lines):
            if line.strip().startswith("{sysver}"):
                start = i + 1
                break
        if start is None:
            return None

        # 收集到下一个 {xxx}: 之前
        result = []
        section_re = re.compile(r"^\s*\{[^}]+\}\s*:")
        for line in lines[start:]:
            if section_re.match(line):
                break
            stripped = line.strip()
            if stripped:
                result.append(stripped)
        return result if result else None

    # ---------- 系统名称 ----------
    def collect_system_name(self):
        if self.custom_name_lines:
            return "\n".join(self.custom_name_lines)
        return self.get_default_name()

    def get_default_name(self):
        if platform.system() == "Linux":
            for path in ["/etc/os-release", "/usr/lib/os-release"]:
                if os.path.exists(path):
                    try:
                        name = None
                        with open(path) as f:
                            for line in f:
                                if line.startswith("PRETTY_NAME="):
                                    return line.split("=", 1)[1].strip().strip('"')
                                if line.startswith("NAME=") and not name:
                                    name = line.split("=", 1)[1].strip().strip('"')
                        if name:
                            return name
                    except Exception:
                        pass
            return "Linux"
        elif platform.system() == "Windows":
            return f"Windows {platform.release()}"
        elif platform.system() == "Darwin":
            return f"macOS {platform.mac_ver()[0]}"
        return platform.system()

    # ---------- UI ----------
    def build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        # 用 ScrollArea 包裹内容，防止信息过多时窗口超出屏幕
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)

        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        # === 顶部: Logo + 系统名称 ===
        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)

        logo_widget = self.make_logo_widget()
        top_layout.addWidget(logo_widget, 0, Qt.AlignmentFlag.AlignTop)

        name_label = QLabel(self.info)
        name_font = QFont("Sans", 14)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setWordWrap(True)
        name_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        top_layout.addWidget(name_label, 1)

        main_layout.addLayout(top_layout)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #d0d0d0;")
        main_layout.addWidget(line)

        # === 信息区 ===
        info_layout = QGridLayout()
        info_layout.setHorizontalSpacing(15)
        info_layout.setVerticalSpacing(8)
        info_layout.setColumnStretch(1, 1)

        collector = InfoCollector(self.t)
        rows = collector.collect()

        for i, (label_text, value_text) in enumerate(rows):
            lbl = QLabel(f"{label_text}:")
            lbl.setStyleSheet("color: #555;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            lbl.setMinimumWidth(110)
            info_layout.addWidget(lbl, i, 0)

            val = QLabel(value_text)
            val.setWordWrap(True)
            val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            val.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            val.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            info_layout.addWidget(val, i, 1)

        main_layout.addLayout(info_layout)
        main_layout.addStretch(1)

        # === 按钮 ===
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        ok_btn = QPushButton(self.t["ok"])
        ok_btn.setFixedWidth(90)
        ok_btn.clicked.connect(self.close)
        btn_layout.addWidget(ok_btn)
        main_layout.addLayout(btn_layout)

    def make_logo_widget(self):
        logo_path = self.script_dir / "logo.png"
        if not logo_path.exists():
            return PlaceholderLogo(self.LOGO_MAX_SIZE)

        pixmap = QPixmap(str(logo_path))
        if pixmap.isNull():
            return PlaceholderLogo(self.LOGO_MAX_SIZE)

        scaled = pixmap.scaled(
            self.LOGO_MAX_SIZE,
            self.LOGO_MAX_SIZE,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        label = QLabel()
        label.setPixmap(scaled)
        label.setFixedSize(scaled.width(), scaled.height())
        label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        label.setScaledContents(False)
        return label


def main():
    configure_wayland()
    app = QApplication(sys.argv)
    window = SystemInfoApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()