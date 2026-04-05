# DirektDSP Plugin Configurator - Reimplementation Plan

## Context

The original Python/PySide6 GUI app (archived to `archive/python-version`) was over-engineered: it cloned a template, then did extensive string substitution and code modification to generate plugin projects. The new approach shifts complexity into the **PluginTemplate** repo's CMake system, so the generator's job is minimal: clone, write a config file, selectively init submodules, done.

The user also wants a **common implementation layer** across plugins to enable Kilohearts-style multi-plugin hosts and better modularization of the ecosystem (PedalSuite, future multi-plugin apps).

## Decisions

- **Language**: Rust (ratatui + crossterm)
- **Config format**: TOML for project.toml and presets
- **Scope**: PluginTemplate repo + TUI app built together
- **Common layer**: Headers only in Phase 1 (interfaces, no host implementation)

---

## Architecture Overview

Two deliverables:
1. **PluginTemplate repo** — a smart, config-driven JUCE plugin template with CMake-level module toggling
2. **TUI app** — a Rust terminal UI that walks the user through configuration and generates projects from the template

### The Key Design Shift

**Old**: Generator clones template → modifies CMakeLists.txt, substitutes variables in source files, edits includes
**New**: Generator clones template → writes `project.toml` + `cmake-local/options.cmake` → CMake reads config at configure time

The template is always a valid, buildable project. The generator only writes data files, never touches CMake or C++ source.

---

## Part 1: PluginTemplate Repository

### Directory Layout

```
PluginTemplate/
├── CMakeLists.txt                  # Root — reads project.toml, toggles modules
├── VERSION
├── project.toml                    # Project identity (written by generator)
├── JUCE/                           # Submodule
├── cmake/                          # Submodule (pamplejuce cmake helpers)
├── cmake-local/
│   ├── ReadProjectConfig.cmake     # TOML parser → CMake variables
│   ├── ModuleSystem.cmake          # Conditional add_subdirectory per module
│   ├── MultiPlugin.cmake           # Multi-plugin orchestration
│   ├── CommonLayer.cmake           # Common implementation layer setup
│   ├── PedalMoonbase.cmake         # Per-pedal moonbase (from PedalSuite)
│   └── options.cmake               # Generated: CACHE variable overrides
├── modules/                        # All optional modules as submodules
│   ├── moonbase_JUCEClient/
│   ├── melatonin_inspector/
│   ├── clap-juce-extensions/
│   ├── DirektDSP_GUI/
│   ├── cycfi_q/
│   └── cycfi_infra/
├── common/                         # Common Implementation Layer (C++ headers)
│   ├── CMakeLists.txt
│   ├── IPluginProcessor.h
│   ├── IPluginState.h
│   ├── IPluginUI.h
│   ├── PluginBus.h
│   └── PluginDescriptor.h
├── source/                         # Single-plugin source tree
│   ├── PluginProcessor.h/cpp
│   ├── PluginEditor.h/cpp
│   └── DSP/
├── plugins/                        # Multi-plugin subdirectories (generated)
│   └── <PluginName>/
│       ├── CMakeLists.txt
│       ├── source/
│       ├── assets/
│       └── moonbase_api_config.json
├── assets/
├── packaging/
├── tests/
├── benchmarks/
├── scripts/
│   ├── setup.sh / setup.ps1
│   └── build.sh / build.ps1
├── .github/workflows/
├── .gitmodules
└── .clang-format
```

### Root CMakeLists.txt Pattern

```cmake
cmake_minimum_required(VERSION 3.25)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake-local")

include(PamplejuceVersion)
include(CPM)
include(PamplejuceMacOS)
include(JUCEDefaults)

# Read project.toml → sets PROJ_NAME, PROJ_COMPANY_NAME, PROJ_FORMATS, etc.
include(ReadProjectConfig)
read_project_config("${CMAKE_CURRENT_SOURCE_DIR}/project.toml")

# Load generated option defaults (if they exist)
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/cmake-local/options.cmake")
    include("${CMAKE_CURRENT_SOURCE_DIR}/cmake-local/options.cmake")
endif()

project(${PROJ_NAME} VERSION ${CURRENT_VERSION})

# Module toggle options
option(ENABLE_MOONBASE         "Moonbase licensing"          OFF)
option(ENABLE_MELATONIN        "Melatonin Inspector"         ON)
option(ENABLE_CLAP             "CLAP format"                 ON)
option(ENABLE_DIREKTDSP_GUI    "DirektDSP GUI framework"     OFF)
option(ENABLE_CYCFI_Q          "cycfi::Q DSP library"        OFF)
option(ENABLE_COMMON_LAYER     "Common implementation layer"  ON)

add_subdirectory(JUCE)

include(ModuleSystem)
setup_modules()  # Conditionally add_subdirectory per enabled module

if(ENABLE_COMMON_LAYER)
    add_subdirectory(common)
endif()

# Single-plugin vs multi-plugin path
if(PROJ_IS_MULTI_PLUGIN)
    include(MultiPlugin)
    foreach(PLUGIN_DIR IN LISTS PROJ_PLUGINS)
        add_subdirectory("plugins/${PLUGIN_DIR}")
    endforeach()
else()
    # Standard single-plugin (follows Chasm/Pamplejuce pattern)
    juce_add_plugin("${PROJ_NAME}" ...)
    # ... SharedCode, conditional linking, Assets, Tests, Benchmarks
endif()
```

### Module Registry (modules.toml)

Declares all available modules with metadata, dependencies, and conflicts. Read by both CMake and the TUI app:

```toml
[modules.moonbase_JUCEClient]
display_name = "Moonbase Licensing"
description = "DRM/licensing via Moonbase.sh"
cmake_option = "ENABLE_MOONBASE"
submodule_path = "modules/moonbase_JUCEClient"
cmake_target = "moonbase_JUCEClient"
provides = ["licensing"]
requires = []
conflicts = []

[modules.clap_juce_extensions]
display_name = "CLAP Format"
cmake_option = "ENABLE_CLAP"
submodule_path = "modules/clap-juce-extensions"
cmake_target = "clap_juce_extensions"
provides = ["clap"]
requires = []

# ... melatonin_inspector, DirektDSP_GUI, cycfi_q, cycfi_infra
```

### Common Implementation Layer (C++ Interfaces)

Standard interfaces in `common/` enabling plugin reuse across different host contexts:

- **`IPluginProcessor<T>`** — abstract DSP interface (prepare/process/release/reset)
- **`IPluginState`** — standardized state serialization (APVTS wrapper, serialize/deserialize)
- **`IPluginUI`** — UI embedding interface (createEditorComponent, getPreferredSize)
- **`PluginBus`** — inter-plugin pub/sub message bus
- **`PluginDescriptor`** — runtime metadata struct (name, version, category, channels)

These are an INTERFACE library (`DirektCommonLayer`) that plugins optionally link against.

---

## Part 2: TUI Application (Rust)

### Project Structure

```
direktdsp-configurator/
├── Cargo.toml
├── src/
│   ├── main.rs                     # Entry point, CLI args
│   ├── app.rs                      # State machine (screens, navigation)
│   ├── config/
│   │   ├── project_config.rs       # ProjectConfig serde types
│   │   ├── preset.rs               # Preset load/save/list
│   │   ├── module_registry.rs      # Module definitions + dep graph
│   │   └── schema.rs               # Schema versioning
│   ├── ui/
│   │   ├── app_ui.rs               # Root layout
│   │   ├── screens/
│   │   │   ├── welcome.rs          # New / Load Preset / Recent
│   │   │   ├── project_info.rs     # Name, company, bundle ID, codes
│   │   │   ├── formats.rs          # VST3, AU, AUv3, CLAP, Standalone
│   │   │   ├── modules.rs          # Module toggles w/ dep resolution
│   │   │   ├── multi_plugin.rs     # Add/remove plugins (conditional)
│   │   │   ├── build_options.rs    # C++ std, IPP, copy-after-build
│   │   │   ├── review.rs           # Summary + file tree preview
│   │   │   └── generate.rs         # Progress bar + log
│   │   └── widgets/
│   │       ├── text_input.rs
│   │       ├── checkbox_group.rs
│   │       ├── file_tree.rs
│   │       └── progress_bar.rs
│   ├── generation/
│   │   ├── generator.rs            # Pipeline orchestrator
│   │   ├── git_ops.rs              # Clone, selective submodule init
│   │   ├── toml_writer.rs          # Write project.toml
│   │   └── cmake_configurator.rs   # Write options.cmake
│   └── validation/
│       ├── project_validator.rs
│       └── module_validator.rs
├── tests/
└── resources/
    ├── modules.toml
    └── presets/
        ├── standard_fx.toml
        ├── instrument.toml
        └── minimal.toml
```

### Key Dependencies

- `ratatui` + `crossterm` — TUI framework
- `toml` + `serde` — config serialization
- `clap` (Rust) — CLI argument parsing
- `tokio` — async git operations
- `petgraph` — module dependency resolution
- `color-eyre` — error handling
- `directories` — XDG config paths
- `semver`, `regex` — validation

### TUI Flow

```
Welcome → Project Info → Formats → Modules → [Multi-Plugin] → Build Options → Review → Generate → Done
```

Navigation: `Tab`/`Shift+Tab` between fields, `Ctrl+N`/`Ctrl+P` between screens, `Ctrl+S` save preset, `q` quit.

### Configuration Format (project.toml)

```toml
schema_version = "1.0"

[project]
name = "MyPlugin"
product_name = "My Plugin"
company_name = "DirektDSP"
bundle_id = "com.direktdsp.myplugin"
manufacturer_code = "Manu"
plugin_code = "MyPl"
version = "1.0.0"
formats = ["VST3", "AU", "CLAP", "Standalone"]
clap_features = "audio-effect"
multi_plugin = false
plugins = []

[modules]
moonbase = false
melatonin = true
clap = true
direktdsp_gui = false
cycfi_q = false
common_layer = true

[build]
cpp_standard = 23
copy_after_build = true
ipp = false
```

### Preset Format (superset of project.toml + metadata)

```toml
schema_version = "1.0"

[meta]
name = "Standard Audio FX"
description = "Balanced audio FX starting point"
created = "2026-04-04T12:00:00Z"
author = "Seamus"

[project]
# ... same as project.toml

[modules]
# ... same

[build]
# ... same

[generation]
template_url = "https://github.com/DirektDSP/PluginTemplate.git"
template_branch = "main"
init_git = true
run_setup_script = true
```

### Generation Pipeline

1. **Validate** — re-run all validators on complete config
2. **Clone** — `git clone --depth 1 <template_url> <output_dir>`
3. **Selective submodule init** — only init submodules for enabled modules + JUCE + cmake
4. **Write project.toml** — from the config model
5. **Write cmake-local/options.cmake** — CMake CACHE variable overrides
6. **Scaffold multi-plugin dirs** (if multi_plugin) — per-plugin CMakeLists.txt, source/, assets/
7. **Run setup script** — platform-appropriate setup.sh/setup.ps1
8. **Clean git history** — remove template .git, init fresh repo
9. **Rollback on failure** — remove partial output directory

---

## Part 3: Multi-Plugin Support

When `multi_plugin = true`, the template uses the PedalSuite pattern:
- Root CMake handles shared deps (JUCE, modules)
- `plugins/<Name>/CMakeLists.txt` per plugin with own `juce_add_plugin()`, SharedCode, assets
- Per-plugin moonbase config via `PedalMoonbase.cmake`
- Common layer shared across all plugins in the project

Preset format extends with `[[plugin]]` array-of-tables for per-plugin overrides (name, bundle_id, plugin_code, clap_features).

---

## Implementation Phases

### Phase 1: PluginTemplate Repository
- Create repo with config-driven CMake
- Implement ReadProjectConfig.cmake, ModuleSystem.cmake
- Port Chasm single-plugin pattern + PedalSuite multi-plugin pattern
- Create common/ implementation layer headers
- Template source files, scripts, CI/CD
- **Verify**: hand-write project.toml, cmake configure + build succeeds

### Phase 2: TUI Scaffold
- Rust project setup with ratatui
- Screen navigation state machine
- All screens with validated inputs (no generation logic yet)
- **Verify**: navigate all screens, enter data, see validation

### Phase 3: Config & Preset System
- ProjectConfig serde types, TOML round-trip
- PresetManager (load/save/list from ~/.config/direktdsp-configurator/)
- Module registry with petgraph dependency resolution
- Bundle starter presets
- **Verify**: load preset, modify, save, reload

### Phase 4: Generation Pipeline
- git_ops, toml_writer, cmake_configurator
- Generator orchestrator with async progress
- Wire to Generate screen
- **Verify**: generate single-plugin project, cmake + build succeeds

### Phase 5: Multi-Plugin Support
- Multi-Plugin TUI screen
- Per-plugin directory scaffolding
- MultiPlugin.cmake + PedalMoonbase
- **Verify**: generate 2-plugin project, both build

### Phase 6: Polish & Distribution
- CLI mode (non-interactive `--preset X --output Y`)
- Cross-compile for macOS/Windows/Linux
- CI/CD for the configurator itself
- Documentation

---

## Key Reference Files

- `/home/seamu/Coding/1_Repos/DirektDSP/Chasm/CMakeLists.txt` — single-plugin CMake pattern
- `/home/seamu/Coding/1_Repos/DirektDSP/PedalSuite/CMakeLists.txt` — multi-plugin root pattern
- `/home/seamu/Coding/1_Repos/DirektDSP/PedalSuite/Pneumatica/CMakeLists.txt` — per-plugin pattern
- `/home/seamu/Coding/1_Repos/DirektDSP/DirektDSP_GUI/CMakeLists.txt` — shared GUI module pattern

## Verification Plan

After each phase:
1. **Template**: Create project.toml by hand → `cmake -B build` → `cmake --build build` → plugin binary exists
2. **TUI**: Run app → navigate all screens → enter valid/invalid data → validation works
3. **Presets**: Round-trip TOML load/save → no data loss
4. **Generation**: TUI generate → output dir has correct structure → cmake build succeeds
5. **Multi-plugin**: Generate 2-plugin project → both plugins build → both produce binaries
