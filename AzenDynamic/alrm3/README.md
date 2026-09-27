# ALRM 3 — Azen Laptop Resources Management

ALRM (Azen Laptop Resources Management) is a system-level resource
management technology for laptops. It reduces background process
activity and manages system sleep behavior.

Version 3 is a C++17 rewrite of the original Python implementation,
offering lower resource usage and faster response times.

---

## Requirements

- Linux with systemd
- gcc 9+ or clang 10+
- GLib 2.0 development headers
- libsystemd development headers

Install dependencies:

**Arch Linux**

```bash
sudo pacman -S base-devel cmake glib2 systemd-libs
```

**Debian / Ubuntu**

```bash
sudo apt install build-essential cmake libglib2.0-dev libsystemd-dev
```

---

## Build

```bash
git clone https://github.com/AzenDev2026/AzenDev.git
cd AzenDev/AzenDynamic/alrm3
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
```

## Install

```bash
sudo make install
sudo mkdir -p /etc/azen
sudo cp ../config/Azen-ALRM.conf /etc/azen/
sudo cp ../systemd/azen-alrm.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now azen-alrm.service
```

> There is no `deploy_alrm.sh` in this directory, and none is needed — the
> steps above are the supported install path. (A deploy script only exists
> for ALPRM, at `AzenDynamic/alprm(test)/deploy_alprm.sh`.)

---

## Configuration

Config file: `/etc/azen/Azen-ALRM.conf`

| Option | Values | Description |
|--------|--------|-------------|
| `SYSTEM_MODE` | `energy-saver`, `balanced`, `performance` | Operating mode |
| `ENABLE_APP_NAP` | `true`, `false` | Enable App Nap |
| `SCAN_INTERVAL` | integer (seconds) | Process scan interval |
| `FREEZE_TIMEOUT` | integer (seconds) | Auto-thaw timeout |
| `CPU_THRESHOLD` | integer (percent) | Skip processes above this usage |
| `WHITELIST_APPS` | comma-separated | Never frozen |

Apply changes:

```bash
sudo systemctl restart azen-alrm.service
```

---

## Common commands

**Service**

```bash
sudo systemctl start   azen-alrm.service   # start
sudo systemctl stop    azen-alrm.service   # stop
sudo systemctl restart azen-alrm.service   # restart
sudo systemctl enable  azen-alrm.service   # enable at boot
sudo systemctl disable azen-alrm.service   # disable at boot
sudo systemctl status  azen-alrm.service   # status
```

**Logs**

```bash
sudo journalctl -u azen-alrm.service -f        # live
sudo journalctl -u azen-alrm.service -n 100    # most recent 100 lines
sudo journalctl -u azen-alrm.service -b        # since this boot
```

**Inspection**

```bash
sudo nano /etc/azen/Azen-ALRM.conf                          # edit config
cat /sys/power/mem_sleep                                    # current sleep mode
cat /sys/power/state                                        # supported sleep states
systemctl --user list-units --type=scope --state=running    # running app scopes
systemctl --user status <scope-name>                        # inspect one scope
```

**Update**

```bash
cd AzenDev
git pull
cd AzenDynamic/alrm3
make clean && make
sudo make install
sudo systemctl restart azen-alrm.service
```

**Uninstall**

```bash
sudo systemctl disable --now azen-alrm.service
sudo rm /etc/systemd/system/azen-alrm.service
sudo rm /usr/local/bin/alrm
sudo rm -rf /etc/azen
sudo systemctl daemon-reload
```

---

## Sleep mode

ALRM configures sleep through `/sys/power/mem_sleep`:

| Value | Meaning |
|-------|---------|
| `s2idle` | Modern Standby, used by most laptops from roughly 2020 onwards |
| `deep` | Traditional ACPI S3, used by older laptops |

ALRM 3 uses `s2idle` for **every** mode and power state. `deep` is only
used as a last-resort fallback on hardware that does not advertise
`s2idle` at all, because forcing `deep` on recent laptops can leave the
machine unable to resume. See [WARNING.md](WARNING.md) for the full story
of the 2026-09-25 defect.

---

## License

GPLv3 — see [../../LICENSE](../../LICENSE)
