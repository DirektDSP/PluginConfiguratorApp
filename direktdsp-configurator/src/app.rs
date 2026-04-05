use std::sync::mpsc;

use crate::config::module_registry::ModuleRegistry;
use crate::config::preset::{PresetEntry, PresetManager};
use crate::config::project_config::ProjectConfig;
use crate::generation::generator::GenerationMessage;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Screen {
    Welcome,
    ProjectInfo,
    Formats,
    Modules,
    MultiPlugin,
    BuildOptions,
    Review,
    Generate,
}

impl Screen {
    /// All screens in order, including the conditional MultiPlugin screen.
    pub const ALL: &[Screen] = &[
        Screen::Welcome,
        Screen::ProjectInfo,
        Screen::Formats,
        Screen::Modules,
        Screen::MultiPlugin,
        Screen::BuildOptions,
        Screen::Review,
        Screen::Generate,
    ];

    /// Active screens given whether multi-plugin mode is enabled.
    pub fn active_screens(multi_plugin: bool) -> Vec<Screen> {
        Screen::ALL
            .iter()
            .filter(|s| **s != Screen::MultiPlugin || multi_plugin)
            .copied()
            .collect()
    }

    pub fn title(&self) -> &'static str {
        match self {
            Screen::Welcome => "Welcome",
            Screen::ProjectInfo => "Project Info",
            Screen::Formats => "Plugin Formats",
            Screen::Modules => "Modules",
            Screen::MultiPlugin => "Multi-Plugin",
            Screen::BuildOptions => "Build Options",
            Screen::Review => "Review",
            Screen::Generate => "Generate",
        }
    }

    pub fn index_in(&self, screens: &[Screen]) -> usize {
        screens.iter().position(|s| s == self).unwrap_or(0)
    }
}

pub struct App {
    pub screen: Screen,
    pub config: ProjectConfig,
    pub should_quit: bool,
    pub status_message: Option<String>,

    // Phase 3: Config & Preset system (used in Phase 6 CLI mode)
    #[allow(dead_code)]
    pub preset_manager: Option<PresetManager>,
    #[allow(dead_code)]
    pub module_registry: Option<ModuleRegistry>,
    #[allow(dead_code)]
    pub available_presets: Vec<PresetEntry>,

    // Per-screen state
    pub welcome: WelcomeState,
    pub project_info: ProjectInfoState,
    pub formats: FormatsState,
    pub modules: ModulesState,
    pub multi_plugin: MultiPluginState,
    pub build_options: BuildOptionsState,
    pub generate: GenerateState,
}

#[derive(Debug, Default)]
pub struct WelcomeState {
    pub selected: usize, // 0=New, 1=Load Preset, 2=Recent
}

#[derive(Debug, Default)]
pub struct ProjectInfoState {
    pub focused_field: usize,
    pub fields: Vec<TextFieldState>,
}

#[derive(Debug, Default, Clone)]
pub struct TextFieldState {
    pub label: String,
    pub value: String,
    pub cursor: usize,
    pub error: Option<String>,
}

#[derive(Debug, Default)]
pub struct FormatsState {
    pub selected: usize,
}

#[derive(Debug, Default)]
pub struct ModulesState {
    pub selected: usize,
}

#[derive(Debug, Default)]
pub struct MultiPluginState {
    /// Currently selected plugin index in the list (or the "Add" button position).
    pub selected: usize,
    /// Which field within the selected plugin is focused (None = plugin list navigation).
    pub editing_field: Option<usize>,
    /// Per-plugin field states (parallel to config.project.plugins).
    pub plugin_fields: Vec<PluginFieldSet>,
}

/// Editable fields for a single plugin entry.
#[derive(Debug, Clone)]
pub struct PluginFieldSet {
    pub fields: Vec<TextFieldState>,
}

impl PluginFieldSet {
    pub fn from_plugin(p: &crate::config::project_config::PluginEntry) -> Self {
        Self {
            fields: vec![
                TextFieldState {
                    label: "Name".into(),
                    value: p.name.clone(),
                    ..Default::default()
                },
                TextFieldState {
                    label: "Product Name".into(),
                    value: p.product_name.clone(),
                    ..Default::default()
                },
                TextFieldState {
                    label: "Bundle ID".into(),
                    value: p.bundle_id.clone(),
                    ..Default::default()
                },
                TextFieldState {
                    label: "Plugin Code (4 chars)".into(),
                    value: p.plugin_code.clone(),
                    ..Default::default()
                },
                TextFieldState {
                    label: "CLAP Features".into(),
                    value: p.clap_features.clone(),
                    ..Default::default()
                },
            ],
        }
    }

    pub fn to_plugin(&self) -> crate::config::project_config::PluginEntry {
        crate::config::project_config::PluginEntry {
            name: self.fields[0].value.clone(),
            product_name: self.fields[1].value.clone(),
            bundle_id: self.fields[2].value.clone(),
            plugin_code: self.fields[3].value.clone(),
            clap_features: self.fields[4].value.clone(),
        }
    }

    pub const FIELD_COUNT: usize = 5;
}

#[derive(Debug, Default)]
pub struct BuildOptionsState {
    pub selected: usize,
}

pub struct GenerateState {
    pub output_dir: String,
    pub output_dir_cursor: usize,
    pub editing_output_dir: bool,
    pub progress: f64,
    pub log: Vec<String>,
    pub running: bool,
    pub finished: bool,
    pub error: Option<String>,
    pub rx: Option<mpsc::Receiver<GenerationMessage>>,
}

impl Default for GenerateState {
    fn default() -> Self {
        Self {
            output_dir: default_output_dir(),
            output_dir_cursor: 0,
            editing_output_dir: true,
            progress: 0.0,
            log: Vec::new(),
            running: false,
            finished: false,
            error: None,
            rx: None,
        }
    }
}

fn default_output_dir() -> String {
    directories::UserDirs::new()
        .and_then(|d| d.home_dir().join("Projects").to_str().map(String::from))
        .unwrap_or_else(|| ".".into())
}

impl App {
    pub fn new() -> Self {
        // Initialize preset manager (non-fatal if it fails)
        let preset_manager = PresetManager::new().ok();
        let available_presets = preset_manager
            .as_ref()
            .and_then(|pm| pm.list().ok())
            .unwrap_or_default();

        // Load module registry from bundled resources
        let module_registry = Self::load_module_registry();

        let config = ProjectConfig::default();
        let project_info = ProjectInfoState {
            focused_field: 0,
            fields: vec![
                TextFieldState {
                    label: "Plugin Name".into(),
                    value: config.project.name.clone(),
                    ..Default::default()
                },
                TextFieldState {
                    label: "Product Name".into(),
                    value: config.project.product_name.clone(),
                    ..Default::default()
                },
                TextFieldState {
                    label: "Company Name".into(),
                    value: config.project.company_name.clone(),
                    ..Default::default()
                },
                TextFieldState {
                    label: "Bundle ID".into(),
                    value: config.project.bundle_id.clone(),
                    ..Default::default()
                },
                TextFieldState {
                    label: "Manufacturer Code (4 chars)".into(),
                    value: config.project.manufacturer_code.clone(),
                    ..Default::default()
                },
                TextFieldState {
                    label: "Plugin Code (4 chars)".into(),
                    value: config.project.plugin_code.clone(),
                    ..Default::default()
                },
                TextFieldState {
                    label: "Version".into(),
                    value: config.project.version.clone(),
                    ..Default::default()
                },
            ],
        };

        Self {
            screen: Screen::Welcome,
            config,
            should_quit: false,
            status_message: None,
            preset_manager,
            module_registry,
            available_presets,
            welcome: WelcomeState::default(),
            project_info,
            formats: FormatsState::default(),
            modules: ModulesState::default(),
            multi_plugin: MultiPluginState::default(),
            build_options: BuildOptionsState::default(),
            generate: GenerateState::default(),
        }
    }

    /// Load the module registry from the bundled resources/modules.toml.
    fn load_module_registry() -> Option<ModuleRegistry> {
        // Try relative to the executable first, then a few common paths
        let candidates = [
            std::env::current_exe()
                .ok()
                .and_then(|p| p.parent().map(|d| d.join("resources/modules.toml"))),
            Some(std::path::PathBuf::from("resources/modules.toml")),
        ];
        for candidate in candidates.into_iter().flatten() {
            if candidate.exists()
                && let Ok(reg) = ModuleRegistry::from_file(&candidate)
            {
                return Some(reg);
            }
        }
        None
    }

    /// Load a preset into the current config, updating all UI state.
    #[allow(dead_code)]
    pub fn load_preset(&mut self, preset: &crate::config::preset::PresetConfig) {
        self.config = preset.to_project_config();
        // Re-sync project info fields from config
        let f = &mut self.project_info.fields;
        f[0].value = self.config.project.name.clone();
        f[1].value = self.config.project.product_name.clone();
        f[2].value = self.config.project.company_name.clone();
        f[3].value = self.config.project.bundle_id.clone();
        f[4].value = self.config.project.manufacturer_code.clone();
        f[5].value = self.config.project.plugin_code.clone();
        f[6].value = self.config.project.version.clone();
        // Re-sync multi-plugin state
        self.multi_plugin.plugin_fields = self
            .config
            .project
            .plugins
            .iter()
            .map(PluginFieldSet::from_plugin)
            .collect();
        self.multi_plugin.selected = 0;
        self.multi_plugin.editing_field = None;
    }

    /// Refresh the available presets list from disk.
    #[allow(dead_code)]
    pub fn refresh_presets(&mut self) {
        self.available_presets = self
            .preset_manager
            .as_ref()
            .and_then(|pm| pm.list().ok())
            .unwrap_or_default();
    }

    pub fn active_screens(&self) -> Vec<Screen> {
        Screen::active_screens(self.config.project.multi_plugin)
    }

    pub fn next_screen(&mut self) {
        // Sync fields back to config before leaving
        if self.screen == Screen::ProjectInfo {
            self.sync_project_info_to_config();
        }
        if self.screen == Screen::MultiPlugin {
            self.sync_multi_plugin_to_config();
        }
        let screens = self.active_screens();
        let i = self.screen.index_in(&screens);
        if let Some(&next) = screens.get(i + 1) {
            self.screen = next;
        }
    }

    pub fn prev_screen(&mut self) {
        if self.screen == Screen::ProjectInfo {
            self.sync_project_info_to_config();
        }
        if self.screen == Screen::MultiPlugin {
            self.sync_multi_plugin_to_config();
        }
        let screens = self.active_screens();
        let i = self.screen.index_in(&screens);
        if i > 0 {
            self.screen = screens[i - 1];
        }
    }

    pub fn sync_multi_plugin_to_config(&mut self) {
        self.config.project.plugins = self
            .multi_plugin
            .plugin_fields
            .iter()
            .map(|pf| pf.to_plugin())
            .collect();
    }

    pub fn add_plugin(&mut self) {
        let entry = crate::config::project_config::PluginEntry::new(
            &format!("Plugin{}", self.config.project.plugins.len() + 1),
            &self.config.project.company_name,
        );
        let field_set = PluginFieldSet::from_plugin(&entry);
        self.config.project.plugins.push(entry);
        self.multi_plugin.plugin_fields.push(field_set);
    }

    pub fn remove_plugin(&mut self, index: usize) {
        if index < self.config.project.plugins.len() {
            self.config.project.plugins.remove(index);
            self.multi_plugin.plugin_fields.remove(index);
            if self.multi_plugin.selected > 0
                && self.multi_plugin.selected >= self.config.project.plugins.len()
            {
                self.multi_plugin.selected = self.config.project.plugins.len();
            }
        }
    }

    fn sync_project_info_to_config(&mut self) {
        let f = &self.project_info.fields;
        self.config.project.name = f[0].value.clone();
        self.config.project.product_name = f[1].value.clone();
        self.config.project.company_name = f[2].value.clone();
        self.config.project.bundle_id = f[3].value.clone();
        self.config.project.manufacturer_code = f[4].value.clone();
        self.config.project.plugin_code = f[5].value.clone();
        self.config.project.version = f[6].value.clone();
    }

    /// Poll the generation channel for progress updates.
    /// Call this from the event loop when on the Generate screen.
    pub fn poll_generation(&mut self) {
        let Some(rx) = self.generate.rx.as_ref() else {
            return;
        };

        // Drain all available messages (non-blocking)
        while let Ok(msg) = rx.try_recv() {
            match msg {
                GenerationMessage::Log(line) => {
                    self.generate.log.push(line);
                }
                GenerationMessage::Progress(p) => {
                    self.generate.progress = p;
                }
                GenerationMessage::Done => {
                    self.generate.finished = true;
                    self.generate.running = false;
                    self.generate.rx = None;
                    return;
                }
                GenerationMessage::Error(e) => {
                    self.generate.error = Some(e);
                    self.generate.finished = true;
                    self.generate.running = false;
                    self.generate.rx = None;
                    return;
                }
            }
        }
    }
}
