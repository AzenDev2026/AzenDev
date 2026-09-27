#!/usr/bin/env bash
# 启动 KDE Settings Shell。窗口关闭即退出。
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# 1. 选一个可用的 python：优先项目内的虚拟环境，其次系统 python3
if [ -x "$PROJECT_DIR/myenv/bin/python3" ]; then
    PY="$PROJECT_DIR/myenv/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
    PY="$(command -v python3)"
else
    echo "ERROR: 找不到 python3，请先安装 Python 3.10 或更高版本。" >&2
    exit 1
fi

# 2. 检查 PyQt6。必须放在重定向日志之前，否则用户看不到这条报错。
if ! "$PY" -c "import PyQt6" >/dev/null 2>&1; then
    echo "ERROR: 缺少 PyQt6 依赖。" >&2
    echo "       请运行: $PY -m pip install -r \"$PROJECT_DIR/requirements.txt\"" >&2
    exit 1
fi

# 3. 之后才把输出写进日志，避免在项目目录里生成 launch.log
LOG_DIR="${XDG_STATE_HOME:-$HOME/.local/state}"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/kde-setting-shell.log"
exec > "$LOG" 2>&1

echo "=== $(date) ==="
echo "PY=$PY"
echo "PROJECT_DIR=$PROJECT_DIR"

echo "Starting main.py..."
exec "$PY" "$PROJECT_DIR/main.py" "$@"
