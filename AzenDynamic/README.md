# Azen Dynamic           <img align="right" width="50" height="50" alt="office_blue_gradient" src="https://github.com/user-attachments/assets/600198a5-e274-454f-82bb-3d2c595635a0" />


Azen Dynamic is the software ecosystem branch of the Azen project.
It develops and maintains system-level tools and technologies that
improve performance, battery life, and usability on Linux laptops.

All projects under Azen Dynamic are open source and licensed under
GPLv3.

---

## Projects

| Project | Description | Status |
|---------|-------------|--------|
| **ALRM** | Azen Laptop Resources Management — App Nap, safe sleep-mode selection, resource optimization | Stable |
| **ALPRM** | Azen Laptop Power Resources Management — next-generation sleep stack replacement | In development |
| **AlreSearch** | System file search engine | Early test |
| **Wtml** | Winzer Terminal — a small terminal tool written in Python | Early test |
| **KDE Setting Shell** | Windows 11–style alternative settings UI for KDE Plasma | In development |

---

## ALRM — Azen Laptop Resources Management

ALRM is a system-level resource management technology for laptops.
It reduces background process activity and manages sleep behavior
to improve battery life and responsiveness.

Key features:

- **App Nap** — Freezes idle background applications
- **Safe sleep modes** — Selects a sleep mode the hardware can actually
  resume from, instead of forcing a fixed one
- **Resource Optimization** — Adjusts background process priority

Written in C++17. See [alrm3/README.md](alrm3/README.md) for details.

> **Deep sleep caveat:** the `deep` (ACPI S3) sleep mode can leave some
> laptops (e.g. Dell XPS 13) unable to resume. ALRM 3 therefore uses
> `s2idle` for every mode and power state, and only falls back to `deep`
> on hardware that does not support `s2idle` at all.
> Details: [alrm3/WARNING.md](alrm3/WARNING.md).

---

## ALPRM — Azen Laptop Power Resources Management

ALPRM is the next generation of ALRM. It aims to replace the
fragmented Linux sleep stack with a unified, Azen-controlled
power management framework.

Current progress:

- Monitoring Layer (C) — listens to lid, power button, and D-Bus sleep events
- Decision Layer (Rust) — state machine, permission checks, handoff logs
- Execution Layer (C + Rust) — process freezing, sleep mode switching, hardware control

See [alprm(test)/README.md](alprm(test)/README.md) for details.

---

## AlreSearch — System File Search Engine

AlreSearch is an early-stage search engine for system files. It is
designed to be fast and lightweight, with a focus on low resource
usage.

See [AlreSearch/readme.txt](AlreSearch/readme.txt) for details.

---

## Wtml — Winzer Terminal

Wtml (Winzer Terminal) is a small terminal tool written in Python. It is
currently in early development.

See [../Wtml/readme.txt](../Wtml/readme.txt) for details.

---

## KDE Setting Shell

A replacement shell for the native KDE Plasma system settings, written in
Python + PyQt6. It offers a cleaner, Windows 11–inspired interface while
keeping the underlying KDE functionality intact.

See [kde-setting-shell/README.md](kde-setting-shell/README.md) for details.

---

## Repository structure

    AzenDynamic/
    |-- README.md
    |-- alrm3/               ALRM 3 (C++17)
    |-- alprm(test)/         ALPRM prototype (C + Rust)
    |-- AlreSearch/          System file search engine (Java)
    |-- kde-setting-shell/   KDE settings replacement (Python + PyQt6)
    |-- SmallProject/        Small cross-language samples

`Wtml/` lives at the repository root, not inside `AzenDynamic/`.

---

## License

GPLv3 — see [../LICENSE](../LICENSE)

---

© 2026 白企 Whitent / Azen Project
