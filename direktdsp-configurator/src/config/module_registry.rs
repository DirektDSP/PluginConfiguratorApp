use std::collections::HashMap;
use std::fs;
use std::path::Path;

use color_eyre::{Result, eyre::eyre};
use petgraph::graph::{DiGraph, NodeIndex};
use petgraph::Direction;
use serde::Deserialize;

/// Raw representation of modules.toml on disk.
#[derive(Debug, Deserialize)]
struct ModulesFile {
    modules: HashMap<String, ModuleEntry>,
}

/// A single module entry from modules.toml.
#[derive(Debug, Clone, Deserialize)]
pub struct ModuleEntry {
    pub display_name: String,
    pub description: String,
    #[serde(default)]
    pub url: String,
    #[serde(default)]
    pub branch: String,
    pub cmake_option: String,
    pub submodule_path: String,
    pub cmake_target: String,
    #[serde(default)]
    pub provides: Vec<String>,
    #[serde(default)]
    pub requires: Vec<String>,
    #[serde(default)]
    pub conflicts: Vec<String>,
}

/// The module registry: parsed modules.toml + dependency graph.
#[derive(Debug)]
pub struct ModuleRegistry {
    modules: HashMap<String, ModuleEntry>,
    graph: DiGraph<String, ()>,
    node_map: HashMap<String, NodeIndex>,
    /// Maps a "provides" tag to the module key that provides it.
    provides_map: HashMap<String, String>,
}

impl ModuleRegistry {
    /// Parse a modules.toml file into a registry with a dependency graph.
    pub fn from_file(path: &Path) -> Result<Self> {
        let content = fs::read_to_string(path)
            .map_err(|e| eyre!("Failed to read modules.toml: {e}"))?;
        Self::from_toml(&content)
    }

    /// Parse modules.toml content directly.
    pub fn from_toml(content: &str) -> Result<Self> {
        let file: ModulesFile =
            toml::from_str(content).map_err(|e| eyre!("Failed to parse modules.toml: {e}"))?;

        let mut graph = DiGraph::new();
        let mut node_map = HashMap::new();
        let mut provides_map = HashMap::new();

        // Create nodes for each module
        for key in file.modules.keys() {
            let idx = graph.add_node(key.clone());
            node_map.insert(key.clone(), idx);
        }

        // Build provides map
        for (key, entry) in &file.modules {
            for tag in &entry.provides {
                provides_map.insert(tag.clone(), key.clone());
            }
        }

        // Add dependency edges: if module A requires tag T, and module B provides T,
        // then A depends on B (edge B → A means "B must be enabled for A").
        for (key, entry) in &file.modules {
            for req in &entry.requires {
                if let Some(provider_key) = provides_map.get(req) {
                    let from = node_map[provider_key];
                    let to = node_map[key];
                    graph.add_edge(from, to, ());
                }
            }
        }

        Ok(Self {
            modules: file.modules,
            graph,
            node_map,
            provides_map,
        })
    }

    /// Get a module entry by key.
    pub fn get(&self, key: &str) -> Option<&ModuleEntry> {
        self.modules.get(key)
    }

    /// Iterate all module keys.
    pub fn keys(&self) -> impl Iterator<Item = &String> {
        self.modules.keys()
    }

    /// Iterate all modules.
    pub fn iter(&self) -> impl Iterator<Item = (&String, &ModuleEntry)> {
        self.modules.iter()
    }

    /// Given a module key, return the keys of all modules it directly requires.
    pub fn dependencies_of(&self, key: &str) -> Vec<String> {
        let Some(&node) = self.node_map.get(key) else {
            return vec![];
        };
        self.graph
            .neighbors_directed(node, Direction::Incoming)
            .map(|n| self.graph[n].clone())
            .collect()
    }

    /// Resolve all transitive dependencies for a module.
    /// Returns the full set of module keys that must be enabled (including the module itself).
    pub fn resolve_dependencies(&self, key: &str) -> Vec<String> {
        let mut result = Vec::new();
        let mut visited = std::collections::HashSet::new();
        self.resolve_recursive(key, &mut result, &mut visited);
        result
    }

    fn resolve_recursive(
        &self,
        key: &str,
        result: &mut Vec<String>,
        visited: &mut std::collections::HashSet<String>,
    ) {
        if !visited.insert(key.to_string()) {
            return;
        }
        // Resolve deps first (depth-first)
        for dep in self.dependencies_of(key) {
            self.resolve_recursive(&dep, result, visited);
        }
        result.push(key.to_string());
    }

    /// Check if enabling a module would conflict with any currently-enabled modules.
    /// Returns a list of conflict descriptions.
    pub fn check_conflicts(&self, key: &str, enabled: &[String]) -> Vec<String> {
        let mut conflicts = Vec::new();
        let Some(entry) = self.modules.get(key) else {
            return conflicts;
        };

        for conflict_tag in &entry.conflicts {
            // Find if any enabled module provides this conflicting tag
            if let Some(provider) = self.provides_map.get(conflict_tag) {
                if enabled.contains(provider) {
                    let provider_name = self.modules.get(provider)
                        .map(|m| m.display_name.as_str())
                        .unwrap_or(provider);
                    conflicts.push(format!(
                        "{} conflicts with {} (both provide/conflict on '{}')",
                        entry.display_name, provider_name, conflict_tag
                    ));
                }
            }
        }
        conflicts
    }

    /// Given a set of enabled module keys, compute the full resolved set
    /// (auto-enabling dependencies) and return any warnings.
    pub fn resolve_enabled_set(&self, enabled: &[String]) -> ResolvedModules {
        let mut all_enabled = Vec::new();
        let mut auto_enabled = Vec::new();
        let mut warnings = Vec::new();

        for key in enabled {
            let deps = self.resolve_dependencies(key);
            for dep in &deps {
                if !enabled.contains(dep) && !auto_enabled.contains(dep) {
                    let dep_name = self.modules.get(dep)
                        .map(|m| m.display_name.as_str())
                        .unwrap_or(dep);
                    let key_name = self.modules.get(key)
                        .map(|m| m.display_name.as_str())
                        .unwrap_or(key);
                    auto_enabled.push(dep.clone());
                    warnings.push(format!(
                        "Auto-enabled '{}' (required by '{}')",
                        dep_name, key_name
                    ));
                }
            }
            for dep in deps {
                if !all_enabled.contains(&dep) {
                    all_enabled.push(dep);
                }
            }
        }

        // Check conflicts
        for key in &all_enabled {
            for conflict in self.check_conflicts(key, &all_enabled) {
                if !warnings.contains(&conflict) {
                    warnings.push(conflict);
                }
            }
        }

        ResolvedModules {
            enabled: all_enabled,
            auto_enabled,
            warnings,
        }
    }

    /// Map from the short config key (e.g. "clap") to the registry key (e.g. "clap_juce_extensions").
    /// This bridges the ModuleConfig field names to the modules.toml keys.
    pub fn config_key_to_registry_key(config_key: &str) -> Option<&'static str> {
        match config_key {
            "moonbase" => Some("moonbase_JUCEClient"),
            "melatonin" => Some("melatonin_inspector"),
            "clap" => Some("clap_juce_extensions"),
            "direktdsp_gui" => Some("DirektDSP_GUI"),
            "cycfi_q" => Some("cycfi_q"),
            "common_layer" => None, // Common layer isn't a submodule
            _ => None,
        }
    }
}

/// Result of dependency resolution.
#[derive(Debug, Clone)]
pub struct ResolvedModules {
    /// All modules that should be enabled (user-selected + auto-enabled deps).
    pub enabled: Vec<String>,
    /// Modules that were auto-enabled as dependencies.
    pub auto_enabled: Vec<String>,
    /// Warnings (auto-enable notices, conflict notices).
    pub warnings: Vec<String>,
}
