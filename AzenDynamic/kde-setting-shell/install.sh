#!/usr/bin/env bash
# 一键安装 KDE Settings Shell:
#   1. 在项目目录里创建虚拟环境并安装依赖
#   2. 生成桌面项到 ~/.local/share/applications/
# 重复运行是安全的。
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$PROJECT_DIR/myenv"
APPS_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
DESKTOP_FILE="$APPS_DIR/kde-settings-shell.desktop"

echo "==> 项目目录: $PROJECT_DIR"

# ---- 1. 依赖 ----
if [ ! -x "$VENV/bin/python3" ]; then
    echo "==> 创建虚拟环境 myenv/"
    python3 -m venv "$VENV"
fi

echo "==> 安装 Python 依赖"
"$VENV/bin/python3" -m pip install -r "$PROJECT_DIR/requirements.txt"

# ---- 2. 桌面项 ----
echo "==> 生成桌面项: $DESKTOP_FILE"
mkdir -p "$APPS_DIR"
cat > "$DESKTOP_FILE" <<DESKTOPEOF
[Desktop Entry]
Type=Application
Name=系统设置
Name[en_US]=System Settings
Comment=KDE Settings Shell
Comment[en_US]=KDE Settings Shell
Exec="$PROJECT_DIR/launch.sh"
Icon=preferences-system
Terminal=false
Categories=Settings;System;Qt;
StartupNotify=true
StartupWMClass=KDE Settings Shell
DESKTOPEOF

chmod +x "$DESKTOP_FILE" "$PROJECT_DIR/launch.sh" "$PROJECT_DIR/install.sh"

echo
echo "✅ 安装完成"
echo "   • 在应用菜单里搜索「系统设置 / System Settings」"
echo "   • 或直接运行: $PROJECT_DIR/launch.sh"
echo "   • 运行日志:   ${XDG_STATE_HOME:-$HOME/.local/state}/kde-setting-shell.log"
