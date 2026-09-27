================================================================
  ALRM v3 (Azen Laptop Resources Management)
  C++ Edition · Built for NVazen 2.0
================================================================

  Author:   Ziting Liang (Azen Project)
  Version:  3.0.0
  License:  GPLv3
  Website:  https://azen.dev
  Repo:     https://github.com/AzenOS/Azen_dev

================================================================
  Overview
================================================================

ALRM (Azen Laptop Resources Management) is a laptop resource
management technology developed by the Azen Project. It is
designed specifically for older laptops, aiming to replicate
the battery life and responsiveness of macOS on Linux.

Version 3 is a complete rewrite of the core from Python to C++,
with significant improvements in performance and memory usage.
It serves as the underlying core component of NVazen 2.0.

================================================================
  Core Features
================================================================

1. App Nap
   - Automatically detects inactive background applications
   - Freezes processes via cgroup freezer
   - Frees CPU and memory, significantly reducing power draw
   - Instantly restores when switched to foreground, seamless

2. Deep Sleep
   - Automatically switches to deep sleep mode when lid closes
   - Cuts power to most hardware (CPU, disk, etc.)
   - Fast wake-up on lid open, balancing power saving and response

3. Resource Optimization
   - Dynamically adjusts background process priority
   - Intelligently skips applications with high CPU usage
   - Supports whitelist, critical apps are never frozen

================================================================
  Technical Highlights
================================================================

  · Pure C++17 implementation, no Python dependency
  · Native binary, startup time < 50ms
  · Memory footprint only 2-3 MB
  · CPU usage < 0.1%
  · GLib main loop, event-driven
  · Deep integration with systemd
  · Security hardening (NoNewPrivileges / ProtectSystem)

================================================================
  Build Instructions
================================================================

Dependencies:
  Arch Linux:    sudo pacman -S cmake gcc glib2 systemd
  Debian/Ubuntu: sudo apt install cmake g++ libglib2.0-dev libsystemd-dev

Build:
  cd alrm3
  mkdir build && cd build
  cmake .. -DCMAKE_BUILD_TYPE=Release
  make -j$(nproc)

Install:
  sudo make install
  sudo mkdir -p /etc/azen
  sudo cp ../config/Azen-ALRM.conf /etc/azen/

================================================================
  Usage
================================================================

1. Start the service:
   sudo systemctl daemon-reload
   sudo systemctl enable --now azen-alrm.service

2. Check status:
   sudo systemctl status azen-alrm.service

3. View logs:
   sudo journalctl -u azen-alrm.service -f

4. Modify configuration:
   sudo nano /etc/azen/Azen-ALRM.conf
   sudo systemctl restart azen-alrm.service

5. Stop the service:
   sudo systemctl stop azen-alrm.service

================================================================
  Configuration
================================================================

Config file path: /etc/azen/Azen-ALRM.conf

  SYSTEM_MODE          System mode
                       energy-saver | balanced | performance

  ENABLE_APP_NAP       Enable App Nap
                       true | false

  SCAN_INTERVAL        Scan interval (seconds)
                       Recommended 5-10, too small wastes power

  FREEZE_TIMEOUT       Freeze timeout (seconds)
                       Auto-thaw after timeout to prevent deadlock

  CPU_THRESHOLD        CPU usage threshold (%)
                       Applications above this are not frozen

  WHITELIST_APPS       Whitelisted apps (comma-separated)
                       These apps are never frozen

================================================================
  Performance Comparison (v2 Python vs v3 C++)
================================================================

  Metric          v2 (Python)   v3 (C++)     Improvement
  -------------------------------------------------
  Startup time    ~500ms        ~50ms        10x
  Memory usage    14 MB         2-3 MB       5x
  CPU usage       0.5-1%        0.1%         5x
  Response delay  ~100ms        ~10ms        10x
  Binary size     N/A           ~200 KB      Minimal

================================================================
  Directory Structure
================================================================

  alrm3/
  ├── CMakeLists.txt              Build configuration
  ├── README.txt                  This file
  ├── config/
  │   └── Azen-ALRM.conf          Configuration file
  ├── src/
  │   ├── main.cpp                Entry point
  │   ├── app_nap.cpp/.hpp        App Nap core
  │   ├── sleep_manager.cpp/.hpp  Sleep management
  │   ├── process_monitor.cpp/.hpp Process monitoring
  │   ├── config_parser.cpp/.hpp  Config parser
  │   └── utils.cpp/.hpp          Utilities
  └── systemd/
      └── azen-alrm.service       Service file

================================================================
  FAQ
================================================================

Q: Service fails to start, what should I do?
A: Check logs: sudo journalctl -u azen-alrm.service -n 50
   Common causes: wrong config path, insufficient permissions,
   missing dependencies

Q: Application won't wake up after being frozen?
A: Normally it auto-thaws when switched to foreground.
   If abnormal, restart: sudo systemctl restart azen-alrm.service

Q: Sleep mode switch has no effect?
A: Check hardware support: cat /sys/power/mem_sleep
   Some laptops don't support deep mode, will fallback to s2idle

Q: How to temporarily disable App Nap?
A: Set ENABLE_APP_NAP=false in config file
   Or: sudo systemctl stop azen-alrm.service

================================================================
  Changelog
================================================================

v3.0.0 (2026-09)
  · Rewritten from Python to C++17
  · 5-10x performance improvement
  · Added smart wake detection
  · Added freeze timeout protection
  · Added CPU usage filtering
  · Full systemd integration
  · Security hardening

v2.0.0 (2026-08)
  · Python version
  · Implemented basic App Nap
  · Implemented sleep mode switching

================================================================
  Contact
================================================================

  Email:   zitingliang18@gmail.com
  GitHub:  https://github.com/AzenOS/Azen_dev
  Website: https://azen.dev

================================================================
  © 2026 Ziting Liang (Azen Project). Licensed under GPLv3.
================================================================