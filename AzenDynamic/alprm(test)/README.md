# ALPRM Monitor

**Azen Laptop Power Resources Management — Monitoring Layer**

ALPRM Monitor is a **pure monitoring tool**. It does **not** interfere with
the system's sleep behavior. Its only purpose is to observe and record how
the system actually handles sleep events, providing real data for the future
ALPRM decision layer.

---

## 📖 What It Does

This tool listens to three types of events:

| Event | Source |
|-------|--------|
| Lid close / open | `/dev/input/event*` (`SW_LID`) |
| Power button press / release | `/dev/input/event*` (`KEY_POWER`) |
| System sleep request | D-Bus `org.freedesktop.login1.PrepareForSleep` |

All events are written with timestamps to `/etc/ALPRM_log/events.log`.

### What It Does NOT Do

- ❌ It does not block sleep
- ❌ It does not modify sleep behavior
- ❌ It does not freeze processes
- ❌ It does not switch sleep modes

It is **read-only** and safe to run.

---

## 🔧 Requirements

### Dependencies

- `gcc` — C compiler
- `libsystemd` — for D-Bus monitoring

### Install Dependencies

```bash
# Arch Linux
sudo pacman -S gcc systemd-libs

# Debian / Ubuntu
sudo apt install gcc libsystemd-dev

# Build
git clone https://github.com/AzenDev2026/AzenDev.git
cd "AzenDev/AzenDynamic/alprm(test)"

make

make clean

sudo ./alprm-monitor

(if successful,you will see this)
{
================================================
  ALPRM Monitor v0.1
  Azen Laptop Power Resources Management
  Monitoring Mode - No system interference
================================================
  Log file: /etc/ALPRM_log/events.log
  Press Ctrl+C to exit
================================================
}

(for view log)
sudo tail -f /etc/ALPRM_log/events.log

Test Events
Close the laptop lid → you should see Lid state changed: closed

Open the lid → you should see Lid state changed: open

Press the power button → you should see Power button pressed

Click "Sleep" in the system menu → you should see System is preparing to sleep

Install as a Systemd Service (Optional)
If you want ALPRM Monitor to run automatically at boot:

1. Install the binary
sudo make install

Install the systemd service
sudo cp systemd/alprm-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload

Enable and start the service
sudo systemctl enable --now alprm-monitor.service

Check the service status
sudo systemctl status alprm-monitor.service

View logs via journalctl
sudo journalctl -u alprm-monitor.service -f

Stop the service
sudo systemctl stop alprm-monitor.service

Disable the service
sudo systemctl disable alprm-monitor.service

Uninstall
sudo systemctl disable --now alprm-monitor.service
sudo rm /etc/systemd/system/alprm-monitor.service
sudo systemctl daemon-reload
sudo make uninstall

Log Format
Logs are written to /etc/ALPRM_log/events.log with this format:

text
[YYYY-MM-DD HH:MM:SS] [LEVEL] [MODULE] message

alprm-monitor/
├── Makefile                       Build configuration
├── README.md                      This file
├── src/
│   ├── main.c                     Entry point, epoll event loop
│   ├── logger.c / logger.h        Logging module
│   ├── lid_monitor.c / .h         Lid open/close detection
│   ├── power_button.c / .h        Power button detection
│   └── dbus_monitor.c / .h        D-Bus sleep request listener
└── systemd/
    └── alprm-monitor.service      Systemd service file

© 2026 Ziting Liang (Azen Project)
