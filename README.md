# DirektDSP Plugin Configurator

A terminal UI application for creating and configuring audio plugin projects from the [PluginTemplate](https://github.com/DirektDSP/PluginTemplate) repository.

## Overview

The configurator walks you through project setup — name, formats, modules, build options — then generates a ready-to-build JUCE plugin project. It clones the template, writes a `project.toml` config, selectively initializes submodules, and scaffolds per-plugin directories for multi-plugin projects.

## Features

- **Config-driven generation** — writes `project.toml` + `options.cmake`, never modifies C++ or CMake source
- **Plugin formats** — VST3, AU, AUv3, CLAP, Standalone
- **Module system** — Moonbase licensing, Melatonin Inspector, CLAP extensions, DirektDSP GUI, cycfi::Q
- **Multi-plugin projects** — PedalSuite-style projects with multiple plugins sharing dependencies
- **Common implementation layer** — standard C++ interfaces for cross-plugin interop
- **Preset system** — save/load configuration presets
- **Selective submodule init** — only clones what you enable

## Installation

### Prerequisites

- Rust toolchain (1.85+)
- Git
- CMake 3.25+ (for building generated projects)

### Build from source

```bash
git clone https://github.com/DirektDSP/PluginConfiguratorApp.git
cd PluginConfiguratorApp/direktdsp-configurator
cargo build --release
```

The binary is at `target/release/direktdsp-configurator`.

## Usage

```bash
cd direktdsp-configurator
cargo run
```

### Navigation

| Key | Action |
|-----|--------|
| Ctrl+N | Next screen |
| Ctrl+P | Previous screen |
| Up/Down | Navigate items |
| Space/Enter | Toggle / select |
| Tab/Shift+Tab | Next/prev field (in editors) |
| q | Quit (from Welcome screen) |
| Ctrl+C | Quit (anywhere) |

### Screens

1. **Welcome** — New project, load preset, or recent
2. **Project Info** — Name, company, bundle ID, codes, version
3. **Formats** — Plugin format toggles + multi-plugin toggle
4. **Modules** — Enable/disable optional modules with dependency resolution
5. **Multi-Plugin** *(conditional)* — Add/remove/edit per-plugin metadata
6. **Build Options** — C++ standard, copy-after-build, IPP
7. **Review** — Configuration summary + file tree preview
8. **Generate** — Output directory, progress, log

## Generated Project Structure

### Single plugin

```
MyPlugin/
├── CMakeLists.txt
├── project.toml
├── source/
├── common/
├── modules/
├── assets/
├── tests/
└── scripts/
```

### Multi-plugin

```
MyProject/
├── CMakeLists.txt
├── project.toml
├── plugins/
│   ├── PluginA/
│   │   ├── CMakeLists.txt
│   │   ├── source/
│   │   └── assets/
│   └── PluginB/
│       ├── CMakeLists.txt
│       ├── source/
│       └── assets/
├── common/
├── modules/
└── scripts/
```

## License

MIT — see [LICENSE](LICENSE).
