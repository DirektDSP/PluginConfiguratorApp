use std::fs;
use std::path::{Path, PathBuf};

use chrono::{DateTime, Utc};
use color_eyre::{Result, eyre::eyre};
use serde::{Deserialize, Serialize};

use super::project_config::{BuildConfig, ModuleConfig, ProjectConfig, ProjectInfo};

/// Preset metadata — author, description, timestamps.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PresetMeta {
    pub name: String,
    pub description: String,
    pub author: String,
    pub created: DateTime<Utc>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub modified: Option<DateTime<Utc>>,
}

/// Generation-specific settings stored in presets but not in project.toml.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GenerationConfig {
    pub template_url: String,
    pub template_branch: String,
    pub init_git: bool,
    pub run_setup_script: bool,
}

impl Default for GenerationConfig {
    fn default() -> Self {
        Self {
            template_url: "https://github.com/DirektDSP/PluginTemplate.git".into(),
            template_branch: "main".into(),
            init_git: true,
            run_setup_script: true,
        }
    }
}

/// A preset is a superset of ProjectConfig with metadata and generation settings.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PresetConfig {
    pub schema_version: String,
    pub meta: PresetMeta,
    pub project: ProjectInfo,
    pub modules: ModuleConfig,
    pub build: BuildConfig,
    pub generation: GenerationConfig,
}

#[allow(dead_code)]
impl PresetConfig {
    /// Convert a ProjectConfig into a PresetConfig with the given metadata.
    pub fn from_project_config(config: &ProjectConfig, meta: PresetMeta) -> Self {
        Self {
            schema_version: config.schema_version.clone(),
            meta,
            project: config.project.clone(),
            modules: config.modules.clone(),
            build: config.build.clone(),
            generation: GenerationConfig::default(),
        }
    }

    /// Extract the ProjectConfig portion (drops meta + generation).
    pub fn to_project_config(&self) -> ProjectConfig {
        ProjectConfig {
            schema_version: self.schema_version.clone(),
            project: self.project.clone(),
            modules: self.modules.clone(),
            build: self.build.clone(),
        }
    }

    pub fn to_toml(&self) -> Result<String> {
        toml::to_string_pretty(self).map_err(|e| eyre!("Failed to serialize preset: {e}"))
    }

    pub fn from_toml(s: &str) -> Result<Self> {
        toml::from_str(s).map_err(|e| eyre!("Failed to parse preset: {e}"))
    }
}

/// Manages preset files in a directory (default: ~/.config/direktdsp-configurator/presets/).
#[derive(Debug)]
pub struct PresetManager {
    presets_dir: PathBuf,
}

#[allow(dead_code)]
impl PresetManager {
    /// Create a PresetManager using the platform-appropriate config directory.
    pub fn new() -> Result<Self> {
        let proj_dirs =
            directories::ProjectDirs::from("com", "direktdsp", "direktdsp-configurator")
                .ok_or_else(|| eyre!("Could not determine config directory"))?;
        let presets_dir = proj_dirs.config_dir().join("presets");
        fs::create_dir_all(&presets_dir)?;
        Ok(Self { presets_dir })
    }

    /// Create a PresetManager with a custom directory (for testing).
    pub fn with_dir(presets_dir: PathBuf) -> Result<Self> {
        fs::create_dir_all(&presets_dir)?;
        Ok(Self { presets_dir })
    }

    /// List all available presets (name, file path) sorted by name.
    pub fn list(&self) -> Result<Vec<PresetEntry>> {
        let mut entries = Vec::new();
        for entry in fs::read_dir(&self.presets_dir)? {
            let entry = entry?;
            let path = entry.path();
            if path.extension().is_some_and(|e| e == "toml") {
                match self.read_preset_meta(&path) {
                    Ok((name, description)) => {
                        entries.push(PresetEntry {
                            name,
                            description,
                            path,
                        });
                    }
                    Err(_) => continue, // Skip malformed presets
                }
            }
        }
        entries.sort_by(|a, b| a.name.cmp(&b.name));
        Ok(entries)
    }

    /// Load a preset from a file path.
    pub fn load(&self, path: &Path) -> Result<PresetConfig> {
        let content = fs::read_to_string(path)
            .map_err(|e| eyre!("Failed to read preset {}: {e}", path.display()))?;
        PresetConfig::from_toml(&content)
    }

    /// Save a preset to the presets directory. Filename is derived from the preset name.
    pub fn save(&self, preset: &PresetConfig) -> Result<PathBuf> {
        let filename = slugify(&preset.meta.name);
        let path = self.presets_dir.join(format!("{filename}.toml"));
        let content = preset.to_toml()?;
        fs::write(&path, &content)?;
        Ok(path)
    }

    /// Delete a preset file.
    pub fn delete(&self, path: &Path) -> Result<()> {
        fs::remove_file(path).map_err(|e| eyre!("Failed to delete preset: {e}"))
    }

    pub fn presets_dir(&self) -> &Path {
        &self.presets_dir
    }

    fn read_preset_meta(&self, path: &Path) -> Result<(String, String)> {
        let content = fs::read_to_string(path)?;
        let preset: PresetConfig = toml::from_str(&content)?;
        Ok((preset.meta.name, preset.meta.description))
    }
}

/// A listing entry for a preset (without loading the full config).
#[derive(Debug, Clone)]
#[allow(dead_code)]
pub struct PresetEntry {
    pub name: String,
    pub description: String,
    pub path: PathBuf,
}

/// Convert a preset name to a filesystem-safe slug.
#[allow(dead_code)]
fn slugify(name: &str) -> String {
    name.to_lowercase()
        .chars()
        .map(|c| if c.is_alphanumeric() { c } else { '_' })
        .collect::<String>()
        .trim_matches('_')
        .to_string()
}

#[allow(dead_code)]
impl ProjectConfig {
    pub fn to_toml(&self) -> Result<String> {
        toml::to_string_pretty(self).map_err(|e| eyre!("Failed to serialize config: {e}"))
    }

    pub fn from_toml(s: &str) -> Result<Self> {
        toml::from_str(s).map_err(|e| eyre!("Failed to parse config: {e}"))
    }
}
