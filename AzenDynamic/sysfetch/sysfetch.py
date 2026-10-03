#!/usr/bin/env python3
"""
sysfetch - 一个基于配置文件的系统信息展示工具
类似 hyfetch，但使用 conf.txt 自定义配置

配置文件格式:
{ascii-logo} : blue
/path/to/ascii.txt

{sys-info} :
/etc/os-release
"""

import os
import sys
import platform
import socket
import re
import subprocess
import glob
from pathlib import Path
from datetime import datetime

# 最大支持的 ASCII 行数
MAX_ASCII_LINES = 100

# ANSI 颜色代码
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'


# 16 种常用颜色名称 -> ANSI 转义序列
COLOR_MAP = {
    'black':        '\033[30m',
    'red':          '\033[31m',
    'green':        '\033[32m',
    'yellow':       '\033[33m',
    'blue':         '\033[34m',
    'magenta':      '\033[35m',
    'cyan':         '\033[36m',
    'white':        '\033[37m',
    'darkgray':     '\033[90m',
    'darkgrey':     '\033[90m',
    'lightred':     '\033[91m',
    'lightgreen':   '\033[92m',
    'lightyellow':  '\033[93m',
    'lightblue':    '\033[94m',
    'lightmagenta': '\033[95m',
    'lightcyan':    '\033[96m',
    'lightwhite':   '\033[97m',
    'gray':         '\033[90m',
    'grey':         '\033[90m',
    'purple':       '\033[35m',
    'lightpurple':  '\033[95m',
    'orange':       '\033[38;5;208m',
    'pink':         '\033[38;5;213m',
}

COLOR_RESET = '\033[0m'


class Config:
    def __init__(self):
        self.ascii_path = None
        self.ascii_color = None
        self.sysinfo_path = None


def parse_conf(conf_path):
    """
    解析 conf.txt 配置文件
    格式:
    {ascii-logo} : blue
    /path/to/ascii.txt

    {sys-info} :
    /etc/os-release

    段头行: {name} : [可选颜色]
    """
    config = Config()

    if not os.path.isfile(conf_path):
        print(f"{Colors.RED}[错误] 配置文件不存在: {conf_path}{Colors.RESET}")
        sys.exit(1)

    try:
        with open(conf_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"{Colors.RED}[错误] 无法读取配置文件: {e}{Colors.RESET}")
        sys.exit(1)

    # 统一换行符
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    lines = content.splitlines()

    # 段头：{name} : 后面可跟一个颜色名（可选）
    section_re = re.compile(r'^\s*\{([a-zA-Z0-9_\-]+)\}\s*:\s*([a-zA-Z]*)\s*$')

    state = None
    ascii_found = False
    sysinfo_found = False

    for lineno, raw_line in enumerate(lines, 1):
        line = raw_line

        # 去掉注释
        hash_pos = line.find('#')
        if hash_pos != -1:
            line = line[:hash_pos]

        line = line.rstrip()
        stripped = line.strip()

        if not stripped:
            continue

        # 段头
        m = section_re.match(stripped)
        if m:
            section_name = m.group(1)
            color_arg = m.group(2).strip().lower() if m.group(2) else ''

            if section_name == 'ascii-logo':
                state = 'ascii'
                ascii_found = True
                if color_arg:
                    if color_arg not in COLOR_MAP:
                        print(f"{Colors.RED}[错误] 第 {lineno} 行: 未知的颜色 '{color_arg}'。"
                              f"支持的颜色: {', '.join(sorted(set(COLOR_MAP.keys())))}{Colors.RESET}")
                        sys.exit(1)
                    config.ascii_color = color_arg
            elif section_name == 'sys-info':
                state = 'sysinfo'
                sysinfo_found = True
                if color_arg:
                    print(f"{Colors.RED}[错误] 第 {lineno} 行: {{sys-info}} 段头不能带颜色{Colors.RESET}")
                    sys.exit(1)
            else:
                print(f"{Colors.RED}[错误] 第 {lineno} 行: 未知的配置段 '{{{section_name}}}'"
                      f"，只允许 {{ascii-logo}} 或 {{sys-info}}{Colors.RESET}")
                sys.exit(1)
            continue

        # 路径行
        if state == 'ascii':
            if config.ascii_path is not None:
                print(f"{Colors.RED}[错误] 第 {lineno} 行: {{ascii-logo}} 段中出现了多个路径{Colors.RESET}")
                sys.exit(1)
            config.ascii_path = stripped
        elif state == 'sysinfo':
            if config.sysinfo_path is not None:
                print(f"{Colors.RED}[错误] 第 {lineno} 行: {{sys-info}} 段中出现了多个路径{Colors.RESET}")
                sys.exit(1)
            config.sysinfo_path = stripped
        else:
            print(f"{Colors.RED}[错误] 第 {lineno} 行: 内容 '{stripped}' 不属于任何配置段，"
                  f"请先声明 {{ascii-logo}} 或 {{sys-info}}{Colors.RESET}")
            sys.exit(1)

    if not ascii_found:
        print(f"{Colors.RED}[错误] 配置文件中缺少 {{ascii-logo}} 段{Colors.RESET}")
        sys.exit(1)
    if not sysinfo_found:
        print(f"{Colors.RED}[错误] 配置文件中缺少 {{sys-info}} 段{Colors.RESET}")
        sys.exit(1)
    if config.ascii_path is None:
        print(f"{Colors.RED}[错误] {{ascii-logo}} 段中未提供路径{Colors.RESET}")
        sys.exit(1)
    if config.sysinfo_path is None:
        print(f"{Colors.RED}[错误] {{sys-info}} 段中未提供路径{Colors.RESET}")
        sys.exit(1)

    return config


# ============================================================
# 下面这些函数保持之前版本不变
# ============================================================

def load_ascii(path):
    if not os.path.isfile(path):
        print(f"{Colors.RED}[错误] ASCII 文件不存在: {path}{Colors.RESET}")
        sys.exit(1)

    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
    except UnicodeDecodeError:
        try:
            with open(path, 'r', encoding='latin-1') as f:
                lines = f.read().splitlines()
        except Exception as e:
            print(f"{Colors.RED}[错误] 无法读取 ASCII 文件: {e}{Colors.RESET}")
            sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}[错误] 无法读取 ASCII 文件: {e}{Colors.RESET}")
        sys.exit(1)

    if len(lines) > MAX_ASCII_LINES:
        print(f"{Colors.RED}[错误] ASCII 文件超过 {MAX_ASCII_LINES} 行 "
              f"(实际 {len(lines)} 行)，不显示该 logo。{Colors.RESET}")
        sys.exit(1)

    return lines


def parse_os_release(path):
    if not os.path.isfile(path):
        print(f"{Colors.RED}[错误] 系统信息文件不存在: {path}{Colors.RESET}")
        sys.exit(1)

    info = {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, _, value = line.partition('=')
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    info[key] = value
    except Exception as e:
        print(f"{Colors.RED}[错误] 无法读取系统信息文件: {e}{Colors.RESET}")
        sys.exit(1)
    return info


def run_cmd(cmd, timeout=2):
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def get_user_host():
    user = os.environ.get('USER', os.environ.get('LOGNAME', 'unknown'))
    hostname = socket.gethostname()
    return user, hostname


def get_os_name(os_info):
    return os_info.get('PRETTY_NAME') or os_info.get('NAME') or platform.system()


def get_kernel():
    return platform.release()


def get_uptime():
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.read().split()[0])
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        parts.append(f"{minutes} min{'s' if minutes != 1 else ''}")
        return ", ".join(parts)
    except Exception:
        return None


def get_packages():
    parts = []
    if os.path.isdir('/var/lib/pacman/local'):
        try:
            count = len([d for d in os.listdir('/var/lib/pacman/local')
                         if os.path.isdir(os.path.join('/var/lib/pacman/local', d))])
            parts.append(f"{count} (pacman)")
        except Exception:
            pass
    if os.path.isfile('/var/lib/dpkg/status'):
        try:
            count = 0
            with open('/var/lib/dpkg/status', 'r') as f:
                for line in f:
                    if line.startswith('Package:'):
                        count += 1
            parts.append(f"{count} (dpkg)")
        except Exception:
            pass
    if os.path.isfile('/var/lib/rpm/rpmdb.sqlite') or os.path.isfile('/var/lib/rpm/Packages'):
        out = run_cmd("rpm -qa 2>/dev/null | wc -l")
        if out and out.isdigit():
            parts.append(f"{out} (rpm)")
    out = run_cmd("pip list 2>/dev/null | tail -n +3 | wc -l")
    if out and out.isdigit() and int(out) > 0:
        parts.append(f"{out} (pip)")
    if os.path.isdir('/var/lib/flatpak') or os.path.isdir(os.path.expanduser('~/.local/share/flatpak')):
        out = run_cmd("flatpak list --app 2>/dev/null | wc -l")
        if out and out.isdigit() and int(out) > 0:
            parts.append(f"{out} (flatpak)")
    if os.path.isdir('/snap'):
        out = run_cmd("snap list 2>/dev/null | tail -n +2 | wc -l")
        if out and out.isdigit() and int(out) > 0:
            parts.append(f"{out} (snap)")
    for sd in [os.path.expanduser('~/.steam/steam/steamapps'),
               os.path.expanduser('~/.local/share/Steam/steamapps')]:
        if os.path.isdir(sd):
            try:
                count = len(glob.glob(os.path.join(sd, 'appmanifest_*.acf')))
                if count > 0:
                    parts.append(f"{count} (steam)")
                break
            except Exception:
                pass
    return ", ".join(parts) if parts else None


def get_shell():
    shell = os.environ.get('SHELL', '')
    if not shell:
        return None
    name = os.path.basename(shell)
    ver = None
    if name == 'bash':
        out = run_cmd("bash --version 2>/dev/null | head -n1")
        if out:
            m = re.search(r'(\d+\.\d+\.\d+)', out)
            if m:
                ver = m.group(1)
    elif name == 'zsh':
        out = run_cmd("zsh --version 2>/dev/null")
        if out:
            m = re.search(r'(\d+\.\d+(\.\d+)?)', out)
            if m:
                ver = m.group(1)
    elif name == 'fish':
        out = run_cmd("fish --version 2>/dev/null")
        if out:
            m = re.search(r'(\d+\.\d+\.\d+)', out)
            if m:
                ver = m.group(1)
    return f"{name} {ver}" if ver else name


def get_resolution():
    out = run_cmd("xrandr 2>/dev/null | grep ' connected' | head -n1")
    if out:
        m = re.search(r'(\d+x\d+)', out)
        if m:
            return m.group(1)
    out = run_cmd("wlr-randr 2>/dev/null | grep -m1 'current'")
    if out:
        m = re.search(r'(\d+x\d+)', out)
        if m:
            return m.group(1)
    try:
        for card in glob.glob('/sys/class/drm/card*-*/modes'):
            with open(card) as f:
                first = f.readline().strip()
                if first:
                    return first
    except Exception:
        pass
    return None


def get_de():
    de = os.environ.get('XDG_CURRENT_DESKTOP') or os.environ.get('DESKTOP_SESSION')
    if not de:
        return None
    de = de.split(':')[0]
    session_type = os.environ.get('XDG_SESSION_TYPE', '')
    parts = [de]
    if session_type:
        parts.append(f"({session_type})")
    return " ".join(parts)


def get_wm():
    if os.environ.get('WAYLAND_DISPLAY'):
        out = run_cmd("ps -e -o comm= 2>/dev/null | grep -E '^(kwin_wayland|sway|Hyprland|gnome-shell|weston|river|wayfire)' | head -n1")
        if out:
            return out
    out = run_cmd("xprop -root _NET_SUPPORTING_WM_CHECK 2>/dev/null | awk '{print $NF}'")
    if out:
        wm = run_cmd(f"xprop -id {out} _NET_WM_NAME 2>/dev/null | cut -d'\"' -f2")
        if wm:
            return wm
    for wm in ['i3', 'bspwm', 'dwm', 'openbox', 'xfwm4', 'mutter', 'kwin_x11', 'awesome', 'qtile']:
        if run_cmd(f"pgrep -x {wm} 2>/dev/null"):
            return wm
    return None


def get_theme():
    theme = os.environ.get('GTK_THEME')
    if not theme:
        out = run_cmd("gsettings get org.gnome.desktop.interface gtk-theme 2>/dev/null")
        if out:
            theme = out.strip().strip("'")
    if not theme:
        for path in [os.path.expanduser('~/.config/gtk-3.0/settings.ini'),
                     os.path.expanduser('~/.config/gtk-4.0/settings.ini')]:
            if os.path.isfile(path):
                try:
                    with open(path) as f:
                        for line in f:
                            if line.startswith('gtk-theme-name'):
                                theme = line.split('=', 1)[1].strip()
                                break
                except Exception:
                    pass
            if theme:
                break
    return theme


def get_icons():
    out = run_cmd("gsettings get org.gnome.desktop.interface icon-theme 2>/dev/null")
    if out:
        return out.strip().strip("'")
    return None


def get_cursor():
    out = run_cmd("gsettings get org.gnome.desktop.interface cursor-theme 2>/dev/null")
    if out:
        return out.strip().strip("'")
    return None


def get_terminal():
    term = os.environ.get('TERM_PROGRAM')
    if not term:
        term = os.environ.get('TERM', 'unknown')
    return term


def get_cpu():
    try:
        name = None
        cores = 0
        freq = None
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('model name') and not name:
                    name = line.split(':', 1)[1].strip()
                elif line.startswith('processor'):
                    cores += 1
                elif line.startswith('cpu MHz') and not freq:
                    mhz = float(line.split(':', 1)[1].strip())
                    freq = mhz / 1000.0
        out = run_cmd("lscpu 2>/dev/null | grep 'CPU max MHz'")
        if out:
            m = re.search(r'([\d.]+)', out)
            if m:
                freq = float(m.group(1)) / 1000.0
        if name:
            name = re.sub(r'\s+', ' ', name)
            name = name.replace('(R)', '').replace('(TM)', '').replace(' CPU', '')
            name = re.sub(r'\s+', ' ', name).strip()
            name = re.sub(r'\s*@\s*[\d.]+GHz', '', name)
        parts = [name or "Unknown CPU"]
        if cores > 0:
            parts.append(f"({cores})")
        if freq:
            parts.append(f"@ {freq:.1f}GHz")
        return " ".join(parts)
    except Exception:
        return None


def get_gpu():
    gpus = []
    out = run_cmd("lspci 2>/dev/null | grep -iE 'vga|3d|display'")
    if out:
        for line in out.splitlines():
            m = re.search(r':\s*(.+)$', line)
            if m:
                gpu = m.group(1).strip()
                gpu = re.sub(r'\(rev [0-9a-f]+\)', '', gpu).strip()
                gpus.append(gpu)
    return "; ".join(gpus) if gpus else None


def get_memory():
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = {}
            for line in f:
                parts = line.split(':')
                if len(parts) == 2:
                    key = parts[0].strip()
                    val = parts[1].strip().split()[0]
                    meminfo[key] = int(val)
        total = meminfo.get('MemTotal', 0)
        available = meminfo.get('MemAvailable', meminfo.get('MemFree', 0))
        used = total - available
        if total > 0:
            used_gib = used / 1024 / 1024
            total_gib = total / 1024 / 1024
            percent = (used / total) * 100
            return f"{used_gib:.2f} GiB / {total_gib:.2f} GiB ({percent:.0f}%)"
    except Exception:
        pass
    return None


def get_network():
    try:
        if os.path.isdir('/sys/class/net'):
            for iface in os.listdir('/sys/class/net'):
                if iface == 'lo':
                    continue
                if os.path.isdir(f'/sys/class/net/{iface}/wireless'):
                    operstate = os.path.join('/sys/class/net', iface, 'operstate')
                    if os.path.isfile(operstate):
                        with open(operstate) as f:
                            if f.read().strip() == 'up':
                                return "Wifi"
                if iface.startswith(('en', 'eth')):
                    operstate = os.path.join('/sys/class/net', iface, 'operstate')
                    if os.path.isfile(operstate):
                        with open(operstate) as f:
                            if f.read().strip() == 'up':
                                return "Ethernet"
    except Exception:
        pass
    return None


def get_bios():
    try:
        vendor = version = date = None
        for attr, path in [('vendor', '/sys/class/dmi/id/bios_vendor'),
                           ('version', '/sys/class/dmi/id/bios_version'),
                           ('date', '/sys/class/dmi/id/bios_date')]:
            if os.path.isfile(path):
                with open(path) as f:
                    val = f.read().strip()
                    if attr == 'vendor':
                        vendor = val
                    elif attr == 'version':
                        version = val
                    else:
                        date = val
        if vendor or version:
            parts = []
            if vendor:
                parts.append(vendor)
            if version:
                parts.append(version)
            if date:
                parts.append(f"({date})")
            return " ".join(parts)
    except Exception:
        pass
    return None


def get_host():
    try:
        vendor = name = version = None
        for attr, path in [('vendor', '/sys/class/dmi/id/sys_vendor'),
                           ('name', '/sys/class/dmi/id/product_name'),
                           ('version', '/sys/class/dmi/id/product_version')]:
            if os.path.isfile(path):
                with open(path) as f:
                    val = f.read().strip()
                    if attr == 'vendor':
                        vendor = val
                    elif attr == 'name':
                        name = val
                    else:
                        version = val
        parts = []
        if vendor:
            parts.append(vendor)
        if name:
            parts.append(name)
        if version and version != name:
            parts.append(version)
        return " ".join(parts) if parts else None
    except Exception:
        pass
    return None


def get_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_system_info(os_info):
    info = []
    os_name = get_os_name(os_info)
    if os_name:
        info.append(("OS", os_name))
    host = get_host()
    if host:
        info.append(("Host", host))
    kernel = get_kernel()
    if kernel:
        info.append(("Kernel", kernel))
    uptime = get_uptime()
    if uptime:
        info.append(("Uptime", uptime))
    packages = get_packages()
    if packages:
        info.append(("Packages", packages))
    shell = get_shell()
    if shell:
        info.append(("Shell", shell))
    resolution = get_resolution()
    if resolution:
        info.append(("Resolution", resolution))
    de = get_de()
    if de:
        info.append(("DE", de))
    wm = get_wm()
    if wm:
        info.append(("WM", wm))
    theme = get_theme()
    if theme:
        info.append(("Theme", theme))
    icons = get_icons()
    if icons:
        info.append(("Icons", icons))
    cursor = get_cursor()
    if cursor:
        info.append(("Cursor", cursor))
    terminal = get_terminal()
    if terminal:
        info.append(("Terminal", terminal))
    cpu = get_cpu()
    if cpu:
        info.append(("CPU", cpu))
    gpu = get_gpu()
    if gpu:
        info.append(("GPU", gpu))
    memory = get_memory()
    if memory:
        info.append(("Memory", memory))
    network = get_network()
    if network:
        info.append(("Network", network))
    bios = get_bios()
    if bios:
        info.append(("BIOS", bios))
    time_str = get_time()
    if time_str:
        info.append(("Time", time_str))
    return info


def display_width(s):
    ansi_re = re.compile(r'\033\[[0-9;]*m')
    s = ansi_re.sub('', s)
    w = 0
    for ch in s:
        code = ord(ch)
        if (0x1100 <= code <= 0x115F or
            0x2E80 <= code <= 0xA4CF or
            0xAC00 <= code <= 0xD7A3 or
            0xF900 <= code <= 0xFAFF or
            0xFE30 <= code <= 0xFE4F or
            0xFF00 <= code <= 0xFF60 or
            0xFFE0 <= code <= 0xFFE6 or
            0x20000 <= code <= 0x3FFFD):
            w += 2
        else:
            w += 1
    return w


def build_info_lines(info_pairs, user, hostname):
    lines = []
    lines.append(f"{Colors.CYAN}{user}{Colors.RESET}@{Colors.CYAN}{hostname}{Colors.RESET}")
    lines.append(f"{Colors.GRAY}{'-' * (len(user) + len(hostname) + 1)}{Colors.RESET}")
    max_label = max((len(label) for label, _ in info_pairs), default=0)
    for label, value in info_pairs:
        label_padded = label.ljust(max_label)
        lines.append(f"{Colors.YELLOW}{label_padded}{Colors.RESET}: {value}")
    return lines


def merge_output(ascii_lines, info_lines, ascii_color=None):
    color_prefix = COLOR_MAP.get(ascii_color, '') if ascii_color else ''
    color_suffix = COLOR_RESET if ascii_color else ''
    ascii_width = max((display_width(line) for line in ascii_lines), default=0)
    max_lines = max(len(ascii_lines), len(info_lines))
    output = []
    for i in range(max_lines):
        ascii_part = ascii_lines[i] if i < len(ascii_lines) else ''
        pad = ascii_width - display_width(ascii_part)
        ascii_part_padded = ascii_part + ' ' * max(pad, 0)
        if color_prefix:
            ascii_part_colored = f"{color_prefix}{ascii_part_padded}{color_suffix}"
        else:
            ascii_part_colored = ascii_part_padded
        info_part = info_lines[i] if i < len(info_lines) else ''
        if info_part:
            output.append(f"{ascii_part_colored}   {info_part}")
        else:
            output.append(ascii_part_colored.rstrip())
    return output


def main():
    script_dir = Path(__file__).resolve().parent
    conf_path = script_dir / 'conf.txt'

    config = parse_conf(str(conf_path))

    ascii_lines = load_ascii(config.ascii_path)
    os_info = parse_os_release(config.sysinfo_path)

    user, hostname = get_user_host()
    info_pairs = get_system_info(os_info)
    info_lines = build_info_lines(info_pairs, user, hostname)

    print()
    for line in merge_output(ascii_lines, info_lines, config.ascii_color):
        print(line)
    print()


if __name__ == '__main__':
    main()