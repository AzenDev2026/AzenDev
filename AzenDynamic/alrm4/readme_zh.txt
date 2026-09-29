================================================================
  ALRM v3 (Azen Laptop Resources Management)
  C++ Edition · 为 NVazen 2.0 打造
================================================================

  作者:   梁子珽 (Azen Project)
  版本:   3.0.0
  许可:   GPLv3
  官网:   https://azen.dev
  仓库:   https://github.com/AzenOS/Azen_dev

================================================================
  简介
================================================================

ALRM (Azen Laptop Resources Management) 是 Azen 项目开发的
笔记本资源管理技术，专为老款笔记本设计，目标是在 Linux 上
复刻 macOS 的续航与响应体验。

v3 版本将核心从 Python 重写为 C++，性能与内存占用大幅优化，
是 NVazen 2.0 的底层核心组件。

================================================================
  核心功能
================================================================

1. App Nap（应用冰封）
   - 自动检测后台非活跃应用
   - 通过 cgroup freezer 冻结进程
   - 释放 CPU 和内存，显著降低功耗
   - 切换到前台时立即恢复，用户无感知

2. Deep Sleep（深度睡眠）
   - 合盖时自动切换到 deep 睡眠模式
   - 切断大部分硬件供电（CPU、硬盘等）
   - 开盖时快速唤醒，兼顾省电与响应

3. Resource Optimization（资源优化）
   - 动态调整后台进程优先级
   - 智能跳过 CPU 占用高的应用
   - 支持白名单，关键应用永不冻结

================================================================
  技术特性
================================================================

  · 纯 C++17 实现，无 Python 依赖
  · 原生二进制，启动时间 < 50ms
  · 内存占用仅 2-3 MB
  · CPU 占用 < 0.1%
  · 基于 GLib 主循环，事件驱动
  · 与 systemd 深度集成
  · 安全加固（NoNewPrivileges / ProtectSystem）

================================================================
  编译方法
================================================================

依赖:
  Arch Linux:   sudo pacman -S cmake gcc glib2 systemd
  Debian/Ubuntu: sudo apt install cmake g++ libglib2.0-dev libsystemd-dev

编译:
  cd alrm3
  mkdir build && cd build
  cmake .. -DCMAKE_BUILD_TYPE=Release
  make -j$(nproc)

安装:
  sudo make install
  sudo mkdir -p /etc/azen
  sudo cp ../config/Azen-ALRM.conf /etc/azen/

================================================================
  使用方法
================================================================

1. 启动服务:
   sudo systemctl daemon-reload
   sudo systemctl enable --now azen-alrm.service

2. 查看状态:
   sudo systemctl status azen-alrm.service

3. 查看日志:
   sudo journalctl -u azen-alrm.service -f

4. 修改配置:
   sudo nano /etc/azen/Azen-ALRM.conf
   sudo systemctl restart azen-alrm.service

5. 停止服务:
   sudo systemctl stop azen-alrm.service

================================================================
  配置文件说明
================================================================

配置文件路径: /etc/azen/Azen-ALRM.conf

  SYSTEM_MODE          系统模式
                       energy-saver | balanced | performance

  ENABLE_APP_NAP       是否启用应用冰封
                       true | false

  SCAN_INTERVAL        扫描间隔（秒）
                       建议 5-10，太小会耗电

  FREEZE_TIMEOUT       冻结超时（秒）
                       超时后自动解冻，防止死锁

  CPU_THRESHOLD        CPU 使用率阈值（%）
                       高于此值不冻结该应用

  WHITELIST_APPS       白名单应用（逗号分隔）
                       这些应用永远不会被冻结

================================================================
  性能对比 (v2 Python vs v3 C++)
================================================================

  指标            v2 (Python)    v3 (C++)    提升
  -------------------------------------------------
  启动时间        ~500ms         ~50ms       10x
  内存占用        14 MB          2-3 MB      5x
  CPU 占用        0.5-1%         0.1%        5x
  响应延迟        ~100ms         ~10ms       10x
  二进制大小      N/A            ~200 KB     极小

================================================================
  目录结构
================================================================

  alrm3/
  ├── CMakeLists.txt              构建配置
  ├── README.txt                  本文件
  ├── config/
  │   └── Azen-ALRM.conf          配置文件
  ├── src/
  │   ├── main.cpp                主入口
  │   ├── app_nap.cpp/.hpp        App Nap 核心
  │   ├── sleep_manager.cpp/.hpp  睡眠管理
  │   ├── process_monitor.cpp/.hpp 进程监控
  │   ├── config_parser.cpp/.hpp  配置解析
  │   └── utils.cpp/.hpp          工具函数
  └── systemd/
      └── azen-alrm.service       服务文件

================================================================
  常见问题
================================================================

Q: 服务启动失败怎么办？
A: 查看日志: sudo journalctl -u azen-alrm.service -n 50
   常见原因: 配置文件路径错误、权限不足、依赖缺失

Q: 应用被冻结后无法唤醒？
A: 正常情况下切换到前台会自动解冻。
   如果异常，重启服务: sudo systemctl restart azen-alrm.service

Q: 睡眠模式切换无效？
A: 检查硬件是否支持: cat /sys/power/mem_sleep
   部分笔记本不支持 deep 模式，会自动回退到 s2idle

Q: 如何临时禁用 App Nap？
A: 修改配置文件 ENABLE_APP_NAP=false
   或直接: sudo systemctl stop azen-alrm.service

================================================================
  更新日志
================================================================

v3.0.0 (2026-09)
  · 从 Python 重写为 C++17
  · 性能提升 5-10 倍
  · 新增智能唤醒检测
  · 新增冻结超时保护
  · 新增 CPU 使用率过滤
  · 完整 systemd 集成
  · 安全加固

v2.0.0 (2026-08)
  · Python 版本
  · 实现 App Nap 基础功能
  · 实现睡眠模式切换

================================================================
  联系
================================================================

  Email:  zitingliang18@gmail.com
  GitHub: https://github.com/AzenOS/Azen_dev
  Website: https://azen.dev

================================================================
  © 2026 梁子珽 (Azen Project). Licensed under GPLv3.
================================================================