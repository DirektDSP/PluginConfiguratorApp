use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProjectConfig {
    pub schema_version: String,
    pub project: ProjectInfo,
    pub modules: ModuleConfig,
    pub build: BuildConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProjectInfo {
    pub name: String,
    pub product_name: String,
    pub company_name: String,
    pub bundle_id: String,
    pub manufacturer_code: String,
    pub plugin_code: String,
    pub version: String,
    pub formats: Vec<PluginFormat>,
    pub clap_features: String,
    pub multi_plugin: bool,
    pub plugins: Vec<PluginEntry>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginEntry {
    pub name: String,
    pub product_name: String,
    pub bundle_id: String,
    pub plugin_code: String,
    pub clap_features: String,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[allow(clippy::upper_case_acronyms)]
pub enum PluginFormat {
    VST3,
    AU,
    AUv3,
    CLAP,
    Standalone,
}

impl PluginFormat {
    pub const ALL: &[PluginFormat] = &[
        PluginFormat::VST3,
        PluginFormat::AU,
        PluginFormat::AUv3,
        PluginFormat::CLAP,
        PluginFormat::Standalone,
    ];

    pub fn label(&self) -> &'static str {
        match self {
            PluginFormat::VST3 => "VST3",
            PluginFormat::AU => "AU",
            PluginFormat::AUv3 => "AUv3",
            PluginFormat::CLAP => "CLAP",
            PluginFormat::Standalone => "Standalone",
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModuleConfig {
    pub moonbase: bool,
    pub melatonin: bool,
    pub clap: bool,
    pub direktdsp_gui: bool,
    pub cycfi_q: bool,
    pub common_layer: bool,
}

pub struct ModuleInfo {
    pub key: &'static str,
    pub label: &'static str,
    pub description: &'static str,
}

impl ModuleConfig {
    pub const MODULES: &[ModuleInfo] = &[
        ModuleInfo {
            key: "moonbase",
            label: "Moonbase Licensing",
            description: "DRM/licensing via Moonbase.sh",
        },
        ModuleInfo {
            key: "melatonin",
            label: "Melatonin Inspector",
            description: "JUCE component inspector for debugging",
        },
        ModuleInfo {
            key: "clap",
            label: "CLAP Format",
            description: "CLAP plugin format via clap-juce-extensions",
        },
        ModuleInfo {
            key: "direktdsp_gui",
            label: "DirektDSP GUI",
            description: "DirektDSP shared GUI framework",
        },
        ModuleInfo {
            key: "cycfi_q",
            label: "cycfi::Q",
            description: "C++ DSP library (includes cycfi_infra)",
        },
        ModuleInfo {
            key: "common_layer",
            label: "Common Layer",
            description: "DirektDSP common implementation interfaces",
        },
    ];

    pub fn get(&self, key: &str) -> bool {
        match key {
            "moonbase" => self.moonbase,
            "melatonin" => self.melatonin,
            "clap" => self.clap,
            "direktdsp_gui" => self.direktdsp_gui,
            "cycfi_q" => self.cycfi_q,
            "common_layer" => self.common_layer,
            _ => false,
        }
    }

    pub fn set(&mut self, key: &str, value: bool) {
        match key {
            "moonbase" => self.moonbase = value,
            "melatonin" => self.melatonin = value,
            "clap" => self.clap = value,
            "direktdsp_gui" => self.direktdsp_gui = value,
            "cycfi_q" => self.cycfi_q = value,
            "common_layer" => self.common_layer = value,
            _ => {}
        }
    }

    pub fn toggle(&mut self, key: &str) {
        let current = self.get(key);
        self.set(key, !current);
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BuildConfig {
    pub cpp_standard: u32,
    pub copy_after_build: bool,
    pub ipp: bool,
}

pub struct CppStandardOption {
    pub value: u32,
    pub label: &'static str,
}

impl BuildConfig {
    pub const CPP_STANDARDS: &[CppStandardOption] = &[
        CppStandardOption {
            value: 17,
            label: "C++17",
        },
        CppStandardOption {
            value: 20,
            label: "C++20",
        },
        CppStandardOption {
            value: 23,
            label: "C++23",
        },
    ];

    pub fn cpp_standard_index(&self) -> usize {
        Self::CPP_STANDARDS
            .iter()
            .position(|s| s.value == self.cpp_standard)
            .unwrap_or(2)
    }
}

impl PluginEntry {
    pub fn new(name: &str, company: &str) -> Self {
        let lower = name.to_lowercase();
        Self {
            name: name.into(),
            product_name: name.into(),
            bundle_id: format!("com.{}.{}", company.to_lowercase(), lower),
            plugin_code: name
                .chars()
                .filter(|c| c.is_alphanumeric())
                .take(4)
                .collect(),
            clap_features: "audio-effect".into(),
        }
    }
}

impl Default for ProjectConfig {
    fn default() -> Self {
        Self {
            schema_version: "1.0".into(),
            project: ProjectInfo {
                name: "MyPlugin".into(),
                product_name: "My Plugin".into(),
                company_name: "DirektDSP".into(),
                bundle_id: "com.direktdsp.myplugin".into(),
                manufacturer_code: "Manu".into(),
                plugin_code: "MyPl".into(),
                version: "1.0.0".into(),
                formats: vec![
                    PluginFormat::VST3,
                    PluginFormat::AU,
                    PluginFormat::CLAP,
                    PluginFormat::Standalone,
                ],
                clap_features: "audio-effect".into(),
                multi_plugin: false,
                plugins: vec![],
            },
            modules: ModuleConfig {
                moonbase: false,
                melatonin: true,
                clap: true,
                direktdsp_gui: false,
                cycfi_q: false,
                common_layer: true,
            },
            build: BuildConfig {
                cpp_standard: 23,
                copy_after_build: true,
                ipp: false,
            },
        }
    }
}
