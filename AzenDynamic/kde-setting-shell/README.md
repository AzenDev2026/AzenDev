# KDE Settings Shell

A Windows 11–style settings shell for KDE Plasma, written in Python + PyQt6.

> **⚠️ Early Development — Not Stable**
>
> This project is in early development. Features are incomplete, some may not
> work on your system, and the UI may change without notice. Not recommended
> for daily use yet.

---

## Features

- Windows 11–like UI
- Runs system commands in the background (`nmcli`, `brightnessctl`,
  `bluetoothctl`, `kscreen-doctor`, `plasma-apply-*`, …)
- Complex settings hand off to the native KDE KCM instead of
  reimplementing them
- Languages: Chinese, English, Japanese, French, German

---

## Requirements

- KDE Plasma 6 (Wayland or X11)
- Python 3.10+
- PyQt6
- System commands: `brightnessctl`, `wpctl`, `nmcli`, `bluetoothctl`,
  `kscreen-doctor`, `plasma-apply-lookandfeel`, `plasma-apply-wallpaperimage`,
  `qdbus6`, `upower` or `acpi`

Arch example:

```bash
sudo pacman -S brightnessctl wireplumber networkmanager bluez bluez-utils \
               kscreen plasma-workspace qt6-tools upower
```

---

## Install

Clone this repository, then run the installer from the `kde-setting-shell` directory:

```bash
git clone https://github.com/AzenDev2026/AzenDev.git
cd AzenDev/AzenDynamic/kde-setting-shell
chmod +x install.sh
./install.sh

`install.sh` creates the `myenv/` virtual environment, installs PyQt6, and
writes a desktop entry to `~/.local/share/applications/`. Re-running it is safe.

## Run

```bash
./launch.sh
```

…or pick **System Settings** from the application menu.

Runtime log: `~/.local/state/kde-setting-shell.log`

> `kde-settings-shell.desktop` in this directory is a **template only** — its
> `Exec=` path is a placeholder. Use `install.sh` to generate the working copy.

---

## Notes

- `sysver.txt` drives the "About this system" panel. Edit `logo_path`, `name`
  or `version code` there to rebrand it for your own build.
- The Wi-Fi password is handed to `nmcli` over stdin, never as a command line
  argument, so it does not show up in `ps`.

---

## License

GPLv3 — see [../../LICENSE](../../LICENSE).

Part of the NVazen / Azen ecosystem under 白企 Whitent.

© 2026 白企 Whitent / Azen Project
