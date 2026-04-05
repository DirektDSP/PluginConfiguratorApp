use std::path::{Path, PathBuf};
use std::sync::mpsc;

use color_eyre::{Result, eyre::eyre};

use crate::config::module_registry::ModuleRegistry;
use crate::config::preset::GenerationConfig;
use crate::config::project_config::ProjectConfig;

use super::cmake_configurator;
use super::git_ops;
use super::toml_writer;

/// A progress message sent from the generator to the TUI.
#[derive(Debug, Clone)]
pub enum GenerationMessage {
    /// A log line.
    Log(String),
    /// Progress update (0.0 to 1.0).
    Progress(f64),
    /// Generation completed successfully.
    Done,
    /// Generation failed with an error message.
    Error(String),
}

/// Inputs needed to run the generation pipeline.
pub struct GenerationInput {
    pub config: ProjectConfig,
    pub generation: GenerationConfig,
    pub output_dir: PathBuf,
    pub module_registry: Option<ModuleRegistry>,
}

/// Run the full generation pipeline, sending progress updates through the channel.
///
/// Steps:
/// 1. Validate output directory
/// 2. Clone template
/// 3. Selective submodule init
/// 4. Write project.toml
/// 5. Write options.cmake
/// 6. Run setup script (optional)
/// 7. Clean git history + fresh init (optional)
///
/// On failure, removes the partial output directory (rollback).
pub fn run(input: GenerationInput, tx: mpsc::Sender<GenerationMessage>) {
    let result = run_inner(&input, &tx);
    match result {
        Ok(()) => {
            let _ = tx.send(GenerationMessage::Progress(1.0));
            let _ = tx.send(GenerationMessage::Done);
        }
        Err(e) => {
            let _ = tx.send(GenerationMessage::Log(format!("ERROR: {e}")));
            // Rollback: remove partial output
            if input.output_dir.exists() {
                let _ = tx.send(GenerationMessage::Log(
                    "Rolling back — removing partial output directory...".into(),
                ));
                if let Err(rm_err) = std::fs::remove_dir_all(&input.output_dir) {
                    let _ = tx.send(GenerationMessage::Log(format!(
                        "Warning: rollback failed: {rm_err}"
                    )));
                }
            }
            let _ = tx.send(GenerationMessage::Error(e.to_string()));
        }
    }
}

fn run_inner(input: &GenerationInput, tx: &mpsc::Sender<GenerationMessage>) -> Result<()> {
    let output = &input.output_dir;
    let config = &input.config;
    let gen_cfg = &input.generation;

    // Step 1: Validate output directory
    send(tx, "Validating output directory...");
    if output.exists() {
        return Err(eyre!(
            "Output directory already exists: {}",
            output.display()
        ));
    }
    if let Some(parent) = output.parent()
        && !parent.exists()
    {
        return Err(eyre!(
            "Parent directory does not exist: {}",
            parent.display()
        ));
    }
    progress(tx, 0.05);

    // Step 2: Clone template
    send(
        tx,
        &format!("Cloning template from {}...", gen_cfg.template_url),
    );
    git_ops::clone_template(&gen_cfg.template_url, &gen_cfg.template_branch, output)?;
    send(tx, "Template cloned successfully.");
    progress(tx, 0.25);

    // Step 3: Selective submodule init
    send(tx, "Initializing submodules...");
    let submodule_paths = collect_submodule_paths(config, &input.module_registry);
    if submodule_paths.is_empty() {
        send(tx, "No submodules to initialize.");
    } else {
        let path_refs: Vec<&str> = submodule_paths.iter().map(|s| s.as_str()).collect();
        send(
            tx,
            &format!(
                "Initializing {} submodule(s): {}",
                path_refs.len(),
                path_refs.join(", ")
            ),
        );
        git_ops::init_submodules(output, &path_refs)?;
        send(tx, "Submodules initialized.");
    }
    progress(tx, 0.50);

    // Step 4: Write project.toml
    send(tx, "Writing project.toml...");
    toml_writer::write_project_toml(config, output)?;
    send(tx, "project.toml written.");
    progress(tx, 0.60);

    // Step 5: Write options.cmake
    send(tx, "Writing cmake-local/options.cmake...");
    cmake_configurator::write_options_cmake(&config.modules, &config.build, output)?;
    send(tx, "options.cmake written.");
    progress(tx, 0.65);

    // Step 5.5: Scaffold multi-plugin directories (if multi_plugin)
    if config.project.multi_plugin && !config.project.plugins.is_empty() {
        send(
            tx,
            &format!(
                "Scaffolding {} plugin directories...",
                config.project.plugins.len()
            ),
        );
        scaffold_multi_plugin_dirs(config, output)?;
        send(tx, "Multi-plugin directories scaffolded.");
    }
    progress(tx, 0.75);

    // Step 6: Run setup script (optional)
    if gen_cfg.run_setup_script {
        send(tx, "Running setup script...");
        run_setup_script(output)?;
        send(tx, "Setup script completed.");
    }
    progress(tx, 0.85);

    // Step 7: Clean git history + fresh init (optional)
    if gen_cfg.init_git {
        send(tx, "Reinitializing git repository...");
        git_ops::reinit_git(output)?;
        send(tx, "Fresh git repository initialized.");
    }
    progress(tx, 0.95);

    send(tx, &format!("Project generated at: {}", output.display()));

    Ok(())
}

/// Collect submodule paths that should be initialized based on config.
fn collect_submodule_paths(
    config: &ProjectConfig,
    registry: &Option<ModuleRegistry>,
) -> Vec<String> {
    let mut paths = vec!["JUCE".to_string(), "cmake".to_string()];

    // Map config module flags to submodule paths using the registry if available
    let module_flags: &[(&str, bool)] = &[
        ("moonbase", config.modules.moonbase),
        ("melatonin", config.modules.melatonin),
        ("clap", config.modules.clap),
        ("direktdsp_gui", config.modules.direktdsp_gui),
        ("cycfi_q", config.modules.cycfi_q),
    ];

    for &(config_key, enabled) in module_flags {
        if !enabled {
            continue;
        }
        // Try to get the submodule path from the registry
        if let Some(reg) = registry
            && let Some(registry_key) = ModuleRegistry::config_key_to_registry_key(config_key)
            && let Some(entry) = reg.get(registry_key)
        {
            paths.push(entry.submodule_path.clone());

            // Also init any transitive dependencies
            for dep_key in reg.dependencies_of(registry_key) {
                if let Some(dep_entry) = reg.get(&dep_key)
                    && !paths.contains(&dep_entry.submodule_path)
                {
                    paths.push(dep_entry.submodule_path.clone());
                }
            }
            continue;
        }

        // Fallback: hardcoded submodule paths when registry isn't available
        let fallback_path = match config_key {
            "moonbase" => "modules/moonbase_JUCEClient",
            "melatonin" => "modules/melatonin_inspector",
            "clap" => "modules/clap-juce-extensions",
            "direktdsp_gui" => "modules/DirektDSP_GUI",
            "cycfi_q" => "modules/cycfi_q",
            _ => continue,
        };
        paths.push(fallback_path.to_string());

        // cycfi_q always needs cycfi_infra
        if config_key == "cycfi_q" && !paths.contains(&"modules/cycfi_infra".to_string()) {
            paths.push("modules/cycfi_infra".to_string());
        }
    }

    paths
}

/// Run the platform-appropriate setup script.
fn run_setup_script(repo_dir: &Path) -> Result<()> {
    let (script, shell) = if cfg!(windows) {
        ("scripts/setup.ps1", "powershell")
    } else {
        ("scripts/setup.sh", "sh")
    };

    let script_path = repo_dir.join(script);
    if !script_path.exists() {
        // Not an error — setup script is optional in the template
        return Ok(());
    }

    let status = std::process::Command::new(shell)
        .arg(&script_path)
        .current_dir(repo_dir)
        .stdout(std::process::Stdio::null())
        .stderr(std::process::Stdio::null())
        .status()
        .map_err(|e| eyre!("Failed to run setup script: {e}"))?;

    if !status.success() {
        return Err(eyre!(
            "Setup script failed with exit code {}",
            status.code().unwrap_or(-1)
        ));
    }

    Ok(())
}

/// Scaffold per-plugin directories under `plugins/<Name>/` for multi-plugin projects.
fn scaffold_multi_plugin_dirs(config: &ProjectConfig, output: &Path) -> Result<()> {
    let plugins_dir = output.join("plugins");
    std::fs::create_dir_all(&plugins_dir)
        .map_err(|e| eyre!("Failed to create plugins/ directory: {e}"))?;

    for plugin in &config.project.plugins {
        let plugin_dir = plugins_dir.join(&plugin.name);
        let source_dir = plugin_dir.join("source");
        let assets_dir = plugin_dir.join("assets");

        std::fs::create_dir_all(&source_dir)
            .map_err(|e| eyre!("Failed to create {}/source/: {e}", plugin.name))?;
        std::fs::create_dir_all(&assets_dir)
            .map_err(|e| eyre!("Failed to create {}/assets/: {e}", plugin.name))?;

        // Write .gitkeep in assets
        std::fs::write(assets_dir.join(".gitkeep"), "")
            .map_err(|e| eyre!("Failed to write assets/.gitkeep: {e}"))?;

        // Write per-plugin CMakeLists.txt
        let cmake_content = generate_plugin_cmake(plugin, config);
        std::fs::write(plugin_dir.join("CMakeLists.txt"), &cmake_content)
            .map_err(|e| eyre!("Failed to write {}/CMakeLists.txt: {e}", plugin.name))?;

        // Write PluginProcessor.h/cpp
        std::fs::write(
            source_dir.join("PluginProcessor.h"),
            generate_processor_h(&plugin.name),
        )
        .map_err(|e| eyre!("Failed to write PluginProcessor.h: {e}"))?;

        std::fs::write(
            source_dir.join("PluginProcessor.cpp"),
            generate_processor_cpp(&plugin.name),
        )
        .map_err(|e| eyre!("Failed to write PluginProcessor.cpp: {e}"))?;

        // Write PluginEditor.h/cpp
        std::fs::write(
            source_dir.join("PluginEditor.h"),
            generate_editor_h(&plugin.name),
        )
        .map_err(|e| eyre!("Failed to write PluginEditor.h: {e}"))?;

        std::fs::write(
            source_dir.join("PluginEditor.cpp"),
            generate_editor_cpp(&plugin.name),
        )
        .map_err(|e| eyre!("Failed to write PluginEditor.cpp: {e}"))?;

        // Write moonbase config if enabled
        if config.modules.moonbase {
            let moonbase_config = generate_moonbase_config(plugin);
            std::fs::write(
                plugin_dir.join("moonbase_api_config.json"),
                &moonbase_config,
            )
            .map_err(|e| eyre!("Failed to write moonbase_api_config.json: {e}"))?;
        }
    }

    Ok(())
}

fn generate_plugin_cmake(
    plugin: &crate::config::project_config::PluginEntry,
    config: &ProjectConfig,
) -> String {
    let name = &plugin.name;
    let product = &plugin.product_name;
    let company = &config.project.company_name;
    let bundle = &plugin.bundle_id;
    let code = &plugin.plugin_code;
    let mfr_code = &config.project.manufacturer_code;
    let cpp_std = config.build.cpp_standard;

    let formats: String = config
        .project
        .formats
        .iter()
        .map(|f| f.label().to_string())
        .collect::<Vec<_>>()
        .join(" ");

    let mut cmake = format!(
        r#"set(PEDAL_NAME "{name}")
set(PRODUCT_NAME "{product}")
set(COMPANY_NAME "{company}")
set(BUNDLE_ID "{bundle}")
set(FORMATS {formats})

juce_add_plugin("${{PEDAL_NAME}}"
    ICON_BIG "${{CMAKE_SOURCE_DIR}}/packaging/icon.png"
    COMPANY_NAME "${{COMPANY_NAME}}"
    BUNDLE_ID "${{BUNDLE_ID}}"
    COPY_PLUGIN_AFTER_BUILD {copy_after_build}
    PLUGIN_MANUFACTURER_CODE {mfr_code}
    PLUGIN_CODE {code}
    FORMATS "${{FORMATS}}"
    PRODUCT_NAME "${{PRODUCT_NAME}}")

# Per-plugin SharedCode library
add_library(${{PEDAL_NAME}}_SharedCode INTERFACE)
"#,
        copy_after_build = if config.build.copy_after_build {
            "TRUE"
        } else {
            "FALSE"
        },
    );

    // CLAP extension
    if config.modules.clap {
        cmake.push_str(&format!(
            r#"
clap_juce_extensions_plugin(TARGET "${{PEDAL_NAME}}"
    CLAP_ID "${{BUNDLE_ID}}"
    CLAP_FEATURES {clap_features})
"#,
            clap_features = plugin.clap_features,
        ));
    }

    // Moonbase
    if config.modules.moonbase {
        cmake.push_str(
            r#"
# Per-plugin moonbase config generation + linking
pedal_setup_moonbase(
    TARGET "${PEDAL_NAME}"
    CONFIG_JSON "${CMAKE_CURRENT_SOURCE_DIR}/moonbase_api_config.json")
"#,
        );
    }

    // SharedCode setup + source files
    cmake.push_str(&format!(
        r#"
include(MultiPlugin)
setup_plugin_shared_code(${{PEDAL_NAME}}_SharedCode {cpp_std})

# Source files
file(GLOB_RECURSE SourceFiles CONFIGURE_DEPENDS
    "${{CMAKE_CURRENT_SOURCE_DIR}}/source/*.cpp"
    "${{CMAKE_CURRENT_SOURCE_DIR}}/source/*.h")
target_include_directories(${{PEDAL_NAME}}_SharedCode INTERFACE "${{CMAKE_CURRENT_SOURCE_DIR}}/source")
target_sources(${{PEDAL_NAME}}_SharedCode INTERFACE ${{SourceFiles}})

# Assets / BinaryData
setup_plugin_assets(${{PEDAL_NAME}} "${{CMAKE_CURRENT_SOURCE_DIR}}/assets")

target_compile_definitions(${{PEDAL_NAME}}_SharedCode
    INTERFACE
    JUCE_WEB_BROWSER=0
    JUCE_USE_CURL=0
    JUCE_VST3_CAN_REPLACE_VST2=0
    CMAKE_BUILD_TYPE="${{CMAKE_BUILD_TYPE}}"
    VERSION="${{CURRENT_VERSION}}"
    PRODUCT_NAME_WITHOUT_VERSION="${{PEDAL_NAME}}")

get_plugin_link_libraries(_PLUGIN_LIBS)

target_link_libraries(${{PEDAL_NAME}}_SharedCode INTERFACE ${{_PLUGIN_LIBS}})
target_link_libraries("${{PEDAL_NAME}}" PRIVATE ${{PEDAL_NAME}}_SharedCode)
"#,
    ));

    cmake
}

fn generate_processor_h(name: &str) -> String {
    format!(
        r#"#pragma once

#include <juce_audio_processors/juce_audio_processors.h>

class {name}Processor : public juce::AudioProcessor
{{
public:
    {name}Processor();
    ~{name}Processor() override;

    void prepareToPlay(double sampleRate, int samplesPerBlock) override;
    void releaseResources() override;
    void processBlock(juce::AudioBuffer<float>&, juce::MidiBuffer&) override;

    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override {{ return true; }}

    const juce::String getName() const override {{ return "{name}"; }}
    bool acceptsMidi() const override {{ return false; }}
    bool producesMidi() const override {{ return false; }}
    double getTailLengthSeconds() const override {{ return 0.0; }}

    int getNumPrograms() override {{ return 1; }}
    int getCurrentProgram() override {{ return 0; }}
    void setCurrentProgram(int) override {{}}
    const juce::String getProgramName(int) override {{ return {{}}; }}
    void changeProgramName(int, const juce::String&) override {{}}

    void getStateInformation(juce::MemoryBlock& destData) override;
    void setStateInformation(const void* data, int sizeInBytes) override;

private:
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR({name}Processor)
}};
"#,
    )
}

fn generate_processor_cpp(name: &str) -> String {
    format!(
        r#"#include "PluginProcessor.h"
#include "PluginEditor.h"

{name}Processor::{name}Processor()
    : AudioProcessor(BusesProperties()
          .withInput("Input", juce::AudioChannelSet::stereo(), true)
          .withOutput("Output", juce::AudioChannelSet::stereo(), true))
{{
}}

{name}Processor::~{name}Processor() {{}}

void {name}Processor::prepareToPlay(double /*sampleRate*/, int /*samplesPerBlock*/) {{}}

void {name}Processor::releaseResources() {{}}

void {name}Processor::processBlock(juce::AudioBuffer<float>& buffer, juce::MidiBuffer& /*midiMessages*/)
{{
    juce::ScopedNoDenormals noDenormals;
    auto totalNumInputChannels = getTotalNumInputChannels();
    auto totalNumOutputChannels = getTotalNumOutputChannels();

    for (auto i = totalNumInputChannels; i < totalNumOutputChannels; ++i)
        buffer.clear(i, 0, buffer.getNumSamples());
}}

juce::AudioProcessorEditor* {name}Processor::createEditor()
{{
    return new {name}Editor(*this);
}}

void {name}Processor::getStateInformation(juce::MemoryBlock& /*destData*/) {{}}

void {name}Processor::setStateInformation(const void* /*data*/, int /*sizeInBytes*/) {{}}

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{{
    return new {name}Processor();
}}
"#,
    )
}

fn generate_editor_h(name: &str) -> String {
    format!(
        r#"#pragma once

#include "PluginProcessor.h"
#include <juce_gui_basics/juce_gui_basics.h>

class {name}Editor : public juce::AudioProcessorEditor
{{
public:
    explicit {name}Editor({name}Processor&);
    ~{name}Editor() override;

    void paint(juce::Graphics&) override;
    void resized() override;

private:
    {name}Processor& processorRef;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR({name}Editor)
}};
"#,
    )
}

fn generate_editor_cpp(name: &str) -> String {
    format!(
        r#"#include "PluginEditor.h"

{name}Editor::{name}Editor({name}Processor& p)
    : AudioProcessorEditor(&p), processorRef(p)
{{
    setSize(400, 300);
}}

{name}Editor::~{name}Editor() {{}}

void {name}Editor::paint(juce::Graphics& g)
{{
    g.fillAll(getLookAndFeel().findColour(juce::ResizableWindow::backgroundColourId));
    g.setColour(juce::Colours::white);
    g.setFont(15.0f);
    g.drawFittedText("{name}", getLocalBounds(), juce::Justification::centred, 1);
}}

void {name}Editor::resized() {{}}
"#,
    )
}

fn generate_moonbase_config(plugin: &crate::config::project_config::PluginEntry) -> String {
    format!(
        r#"{{
  "product_id": "{}",
  "bundle_id": "{}",
  "api_key": "YOUR_API_KEY_HERE"
}}
"#,
        plugin.name.to_lowercase(),
        plugin.bundle_id,
    )
}

fn send(tx: &mpsc::Sender<GenerationMessage>, msg: &str) {
    let _ = tx.send(GenerationMessage::Log(msg.to_string()));
}

fn progress(tx: &mpsc::Sender<GenerationMessage>, value: f64) {
    let _ = tx.send(GenerationMessage::Progress(value));
}
