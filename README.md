# NVazen™ / Azen™
<img width="569" height="192" alt="NVazentm" src="https://github.com/user-attachments/assets/d7e39495-6806-4b0c-b506-041ec9e2d632" />

<img width="2560" height="1600" alt="Screenshot_20260927_121833" src="https://github.com/user-attachments/assets/6ed1b153-f484-46c5-b375-0041c4f19e61" />

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Website](https://img.shields.io/badge/Website-azen.dev-brightgreen)](https://azen.dev)
[![GitHub](https://img.shields.io/badge/GitHub-AzenDev2026-black)](https://github.com/AzenDev2026/Azen_dev)

> A modern Linux distribution and software ecosystem for older laptops.

---

##  Organization Structure

Azen is a project under **白企 Whitent**, organized as follows:

```
白企 Whitent
│
└── Azen Project
    │
    ├── NVazen / Azen          ← Operating System
    │   (No sub-projects)
    │
    └── Azen Dynamic           ← Software Ecosystem
        ├── ALRM               (Azen Laptop Resources Management)
        ├── ALPRM              (Azen Laptop Power Resources Management)
        ├── AlreSearch         (System file search engine)
        └── Wtml               (Terminal tool)
```

| Layer | Name | Description |
|-------|------|-------------|
| Organization | **白企 Whitent** | The parent organization |
| Project | **Azen** | The main project |
| Product Line 1 | **NVazen / Azen** | Linux distribution based on Arch Linux |
| Product Line 2 | **Azen Dynamic** | Software ecosystem maintained by Azen |

---

##  What is Azen?

Azen is a project with two parts:

| Part | Description |
|------|-------------|
| **Azen OS / NVazen** | A Linux distribution based on Arch Linux, focused on elegance and performance |
| **Azen Dynamic** | Software ecosystem including ALRM, ALPRM, AlreSearch, and Wtml |

---

##  Latest Release

**NVazen 2.0lts.1H2609**

Built on Arch Linux, featuring:

- Upgraded ALRM technology (C++ edition)
- Modern UI with soft rounded corners
- Deep sleep & App Nap
- Privacy-first: no telemetry

---

##  Azen Dynamic

**Azen Dynamic** is the software distribution branch of the Azen project. All sub-projects under Azen Dynamic are maintained by the Azen team.

| Project | Description | Status |
|---------|-------------|--------|
| **ALRM** | Azen Laptop Resources Management — App Nap, Deep Sleep, Resource Optimization |  Stable |
| **ALPRM** | Azen Laptop Power Resources Management — next-gen sleep stack replacement |  In development |
| **AlreSearch** | System file search engine |  Early test |
| **Wtml** | Terminal tool for web template markup |  Early test |

### ALRM — Azen Laptop Resources Management

ALRM is our exclusive technology for older laptops:

- **App Nap** — Freezes idle background apps to save CPU & power
- **Deep Sleep** — Cuts hardware power on lid close, fast wake
- **Resource Optimization** — Dynamic priority for background processes

### ALPRM — Azen Laptop Power Resources Management

The next generation of ALRM, aiming to replace the system's sleep stack with a unified, Azen-controlled power management framework.

Current progress:

-  **Monitoring Layer (C)** — Listens to lid, power button, and D-Bus sleep events
-  **Execution Layer (C + Rust)** — Freeze processes, switch sleep modes, control hardware

---

##  Repository Structure

| Folder | Description |
|--------|-------------|
| `AzenDynamic/` | Software ecosystem (ALRM, ALPRM, AlreSearch, Wtml) |
| `AlreSearch/` | Alre search engine (early test) |
| `Wtml/` | Web template markup language |
| `assets/` | Project assets |
| `screenshot/` | Screenshots |
| `issues/` | Issue tracking |

---

##  License

GPLv3 — see [LICENSE](LICENSE)

---

##  Contact

-  Website: [azen.dev](https://azen.dev)
-  Email: zitingliang18@gmail.com
-  GitHub: [AzenDev2026/Azen_dev](https://github.com/AzenDev2026/Azen_dev)

---   README.md = update 13

**© 2026 白企 Whitent / Azen Project**
