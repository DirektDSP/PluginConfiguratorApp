# CI Fixes Required

## Failed Runs

- **CI** (`23997646393`) — failed on all 3 platforms + format check
- **Update Status** (`23997680977`) — cascading failure (CI failed, so status badge writes "FAILURE")

## Issues

### 1. `cargo fmt` — formatting violations

Files with formatting diffs:
- `src/app.rs` — `PluginFieldSet::from_plugin` struct init needs multi-line expansion
- `src/config/module_registry.rs` — import order, line wrapping

Fix: run `cargo fmt`

### 2. `cargo clippy -D warnings` — 21 errors

#### Dead code (11 errors)
Pre-existing from Phases 2-4 — fields/methods defined but not yet wired to UI:
- `App::preset_manager`, `module_registry`, `available_presets` — unused fields
- `App::load_preset`, `refresh_presets` — unused methods
- `ModuleEntry` fields, `provides_map`, multiple `ModuleRegistry` methods
- `ResolvedModules` struct never constructed
- `PresetConfig` methods, `PresetManager` methods
- `PresetEntry::description`, `path` fields
- `slugify` function
- `ProjectConfig::to_toml`, `from_toml`

Fix: add `#[allow(dead_code)]` on items intended for future use

#### Collapsible if (6 errors)
Nested `if` statements that clippy wants collapsed:
- `src/generation/generator.rs`
- `src/config/module_registry.rs`

Fix: collapse nested `if` into `if a && b`

#### Upper-case acronyms (1 error)
- `PluginFormat::CLAP` — clippy wants `Clap`

Fix: allow at the enum level since these are standard audio plugin format names

#### Useless format! (1 error)
- `src/config/project_config.rs` — `PluginEntry::new` uses `format!` for simple string

Fix: replace with direct collect

### 3. Open GitHub Issues

- #66 `inivation` — open, no labels
- #20 `[EPIC] Implement Preset Load Functionality` — open, labels: p1-high, phase-6, presets, epic
