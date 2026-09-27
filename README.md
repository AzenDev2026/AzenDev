# NVazen™ / Azen™ 

<img width="2560" height="1600" alt="Screenshot_20260927_121833" src="https://github.com/user-attachments/assets/98df16ad-dfec-4bb9-b976-5e8aef64ed95" />


[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Website](https://img.shields.io/badge/Website-azen.dev-brightgreen)](https://azen.dev)
[![GitHub](https://img.shields.io/badge/GitHub-AzenDev2026-black)](https://github.com/AzenDev2026/Azen_dev)

> A modern Linux distribution and software ecosystem for older laptops.

---

## 🏛️ Organization Structure


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
| **Azen Linux / NVazen** | A Linux distribution based on Arch Linux, focused on elegance and performance |
| **Azen Dynamic** | Software ecosystem including ALRM, ALPRM, AlreSearch, Wtml, and KDE Setting Shell |

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
| **Wtml** | Terminal tool  |  Early test |
| **KDE Setting Shell** | Alternative settings UI for KDE Plasma with a Windows 11-inspired design |  In development |

### ALRM — Azen Laptop Resources Management

ALRM is our exclusive technology for older laptops:

- **App Nap** — Freezes idle background apps to save CPU & power
- **Deep Sleep** — Cuts hardware power on lid close, fast wake
- **Resource Optimization** — Dynamic priority for background processes

### ALPRM — Azen Laptop Power Resources Management

The next generation of ALRM, aiming to replace the system's sleep stack with a unified, Azen-controlled power management framework.

Current progress:

-  **Monitoring Layer (C)** — Listens to lid, power button, and D-Bus sleep events
-  **Decision Layer (Rust)** — State machine, permission checks, handoff logs
-  **Execution Layer (C + Rust)** — Freeze processes, switch sleep modes, control hardware

### KDE Setting Shell

A replacement shell for the native KDE Plasma system settings. It provides a cleaner, more modern interface inspired by Windows 11, while keeping the underlying KDE functionality intact.

---

##  Repository Structure

| Folder | Description |
|--------|-------------|
| `AzenDynamic/` | Software ecosystem (ALRM, ALPRM, AlreSearch, Wtml, KDE Setting Shell) |
| `AlreSearch/` | Alre search engine (early test) |
| `Wtml/` | terminal |
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

---

**© 2026 白企 Whitent / Azen Project**
