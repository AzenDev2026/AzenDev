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
| **ALRM** | Azen Laptop Resources Management — App Nap, Deep Sleep, Resource Optimization | Stable |
| **ALPRM** | Azen Laptop Power Resources Management — next-generation sleep stack replacement | In development |
| **AlreSearch** | System file search engine | Early test |
| **Wtml** | Terminal tool for web template markup | Early test |

---

## ALRM — Azen Laptop Resources Management

ALRM is a system-level resource management technology for laptops.
It reduces background process activity and manages sleep behavior
to improve battery life and responsiveness.

Key features:

- **App Nap** — Freezes idle background applications
- **Deep Sleep** — Configures system sleep mode based on hardware
- **Resource Optimization** — Adjusts background process priority

Written in C++17. See [ALRM/README.md](ALRM/README.md) for details.

---

## ALPRM — Azen Laptop Power Resources Management

ALPRM is the next generation of ALRM. It aims to replace the
fragmented Linux sleep stack with a unified, Azen-controlled
power management framework.

Current progress:

- Monitoring Layer (C) — listens to lid, power button, and D-Bus sleep events
- Decision Layer (Rust) — state machine, permission checks, handoff logs
- Execution Layer (C + Rust) — process freezing, sleep mode switching, hardware control

See [ALPRM/README.md](ALPRM/README.md) for details.

---

## AlreSearch — System File Search Engine

AlreSearch is an early-stage search engine for system files. It is
designed to be fast and lightweight, with a focus on low resource
usage.

See [AlreSearch/README.md](AlreSearch/README.md) for details.

---

## Wtml — Terminal Tool

Wtml is a terminal-based tool. It is
currently in early development.

See [Wtml/README.md](Wtml/README.md) for details.

---

## Repository Structure
AzenDynamic/
├── README.md
├── alrm3
├── kde-setting-shell
├── alprm(test)
├── AlreSearch/
└── Wtml/

---

## License

GPLv3 — see [LICENSE](../LICENSE)

---

© 2026 白企 Whitent / Azen Project
