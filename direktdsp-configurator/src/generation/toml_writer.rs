use std::path::Path;

use color_eyre::{Result, eyre::eyre};
use serde::Serialize;

use crate::config::project_config::{BuildConfig, ModuleConfig, PluginFormat, ProjectConfig};

/// Write the project.toml file into the output directory.
///
/// The CMake TOML parser expects `plugins` as a flat string list (just names),
/// not as an array of tables. We serialize a CMake-friendly struct that flattens
/// `PluginEntry` to just the name strings.
pub fn write_project_toml(config: &ProjectConfig, output_dir: &Path) -> Result<()> {
    let cmake_config = CmakeFriendlyConfig::from(config);
    let content = toml::to_string_pretty(&cmake_config)
        .map_err(|e| eyre!("Failed to serialize project.toml: {e}"))?;
    let path = output_dir.join("project.toml");
    std::fs::write(&path, &content)
        .map_err(|e| eyre!("Failed to write project.toml: {e}"))?;
    Ok(())
}

/// A CMake-friendly version of ProjectConfig where `plugins` is Vec<String>.
#[derive(Serialize)]
struct CmakeFriendlyConfig {
    schema_version: String,
    project: CmakeFriendlyProject,
    modules: ModuleConfig,
    build: BuildConfig,
}

#[derive(Serialize)]
struct CmakeFriendlyProject {
    name: String,
    product_name: String,
    company_name: String,
    bundle_id: String,
    manufacturer_code: String,
    plugin_code: String,
    version: String,
    formats: Vec<PluginFormat>,
    clap_features: String,
    multi_plugin: bool,
    plugins: Vec<String>,
}

impl From<&ProjectConfig> for CmakeFriendlyConfig {
    fn from(config: &ProjectConfig) -> Self {
        let p = &config.project;
        Self {
            schema_version: config.schema_version.clone(),
            project: CmakeFriendlyProject {
                name: p.name.clone(),
                product_name: p.product_name.clone(),
                company_name: p.company_name.clone(),
                bundle_id: p.bundle_id.clone(),
                manufacturer_code: p.manufacturer_code.clone(),
                plugin_code: p.plugin_code.clone(),
                version: p.version.clone(),
                formats: p.formats.clone(),
                clap_features: p.clap_features.clone(),
                multi_plugin: p.multi_plugin,
                plugins: p.plugins.iter().map(|pe| pe.name.clone()).collect(),
            },
            modules: config.modules.clone(),
            build: config.build.clone(),
        }
    }
}
