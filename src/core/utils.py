import os
import uuid
import random
import string
from pathlib import Path

def generate_plugin_id():
    """Generate a unique 4-character plugin ID
    
    JUCE plugin IDs must start with a capital letter.
    
    Returns:
        str: A 4-character ID starting with a capital letter
    """
    # First character must be a capital letter
    first_char = random.choice(string.ascii_uppercase)
    
    # Remaining characters can be any letter or number
    chars = string.ascii_letters + string.digits
    remaining_chars = ''.join(random.choice(chars) for _ in range(3))
    
    return first_char + remaining_chars

def create_cmake_file(output_dir, variables):
    """Create the CMakeLists.txt file with proper variable substitution
    
    Args:
        output_dir: Path to the output directory
        variables: Dictionary of variables for template substitution
    """
    # Template file path
    templates_dir = os.environ.get("TEMPLATES_DIR", "templates")
    template_path = Path(templates_dir) / "CMakeLists.txt.template"
    
    # Check if template exists
    if not template_path.exists():
        # Fall back to embedded template
        cmake_template = get_cmake_template()
    else:
        # Read template from file
        with open(template_path, 'r') as f:
            cmake_template = f.read()
    
    # Perform variable substitution
    for key, value in variables.items():
        cmake_template = cmake_template.replace(f"{{{key}}}", str(value))
    
    # Write the result
    cmake_path = Path(output_dir) / "CMakeLists.txt"
    with open(cmake_path, 'w') as f:
        f.write(cmake_template)

def create_gitignore_file(output_dir):
    """Create or update .gitignore file
    
    Args:
        output_dir: Path to the output directory
    """
    # Template file path
    templates_dir = os.environ.get("TEMPLATES_DIR", "templates")
    template_path = Path(templates_dir) / "gitignore.template"
    
    # Check if template exists
    if not template_path.exists():
        # Fall back to embedded template
        gitignore_template = get_gitignore_template()
    else:
        # Read template from file
        with open(template_path, 'r') as f:
            gitignore_template = f.read()
    
    # Write the result
    gitignore_path = Path(output_dir) / ".gitignore"
    with open(gitignore_path, 'w') as f:
        f.write(gitignore_template)

def create_readme_from_variables(output_dir, variables):
    """Create README.md file with variable substitution
    
    Args:
        output_dir: Path to the output directory
        variables: Dictionary of variables for template substitution
    """
    # Template file path
    templates_dir = os.environ.get("TEMPLATES_DIR", "templates")
    template_path = Path(templates_dir) / "README.md.template"
    
    # Check if template exists
    if not template_path.exists():
        # Fall back to embedded template
        readme_template = get_readme_template()
    else:
        # Read template from file
        with open(template_path, 'r') as f:
            readme_template = f.read()
    
    # Perform variable substitution
    for key, value in variables.items():
        readme_template = readme_template.replace(f"{{{key}}}", str(value))
    
    # Write the result
    readme_path = Path(output_dir) / "README.md"
    with open(readme_path, 'w') as f:
        f.write(readme_template)

def update_workflow_files(output_dir, variables):
    """Update GitHub workflow files with variable substitution
    
    Args:
        output_dir: Path to the output directory
        variables: Dictionary of variables for template substitution
    """
    # Workflow directory
    workflow_dir = Path(output_dir) / ".github" / "workflows"
    
    # Skip if directory doesn't exist
    if not workflow_dir.exists():
        return
    
    # Update each workflow file
    for workflow_file in workflow_dir.glob("*.yml"):
        with open(workflow_file, 'r') as f:
            content = f.read()
        
        # Only replace in the first line (name of the workflow)
        lines = content.split("\n")
        if lines and lines[0].startswith("name:"):
            lines[0] = f"name: {variables.get('PROJECT_NAME', 'Plugin')}"
            
            # Write the modified content back
            with open(workflow_file, 'w') as f:
                f.write("\n".join(lines))

# ------------------------
# Embedded templates
# ------------------------

def get_cmake_template():
    """Get the embedded CMakeLists.txt template"""
    return """cmake_minimum_required(VERSION 3.25)

# This tells cmake we have goodies in the /cmake folder
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
include (PamplejuceVersion)

# Modern concise way to add dependencies to your project
include (CPM)

# Configures universal binaries and decides which version of macOS to support
include(PamplejuceMacOS)

# Couple tweaks that IMO should be JUCE defaults
include(JUCEDefaults)

# Change me!
# This is the internal name of the project and the name of JUCE's shared code target
# Note: This cannot have spaces (it may be 2025, but you can't have it all!)
# Worry not, JUCE's PRODUCT_NAME can have spaces (and is what DAWs display)
set(PROJECT_NAME "{PROJECT_NAME}")

# Worry not, JUCE's PRODUCT_NAME can have spaces (and is what DAWs will display)
# You can also just have it be the same thing as PROJECT_NAME
# You may want to append the major version on the end of this (and PROJECT_NAME) ala:
#   set(PROJECT_NAME "MyPlugin_v${MAJOR_VERSION}")
# Doing so enables major versions to show up in IDEs and DAWs as separate plugins
# allowing you to change parameters and behavior without breaking existing user projects
set(PRODUCT_NAME "{PRODUCT_NAME}")

# Change me! Used for the MacOS bundle name and Installers
set(COMPANY_NAME "{COMPANY_NAME}")

# Change me! Used for the MacOS bundle identifier (and signing)
set(BUNDLE_ID "{BUNDLE_ID}")

# Change me! Set the plugin formats you want built
# Valid choices: AAX Unity VST VST3 AU AUv3 Standalone
set({FORMATS})

# For simplicity, the name of the CMake project is also the name of the target
project(${PROJECT_NAME} VERSION ${CURRENT_VERSION})

# JUCE is setup as a submodule in the /JUCE folder
# Locally, you must run `git submodule update --init --recursive` once
# and later `git submodule update --remote --merge` to keep it up to date
# On Github Actions, this is done as a part of actions/checkout
add_subdirectory(JUCE)

{MOONBASE_INCLUDE}

# TODO: CHANGE ME! This must match the product id in assets/moonbase_api_config.json
# see here for more info https://github.com/Moonbase-sh/moonbase_JUCEClient?tab=readme-ov-file#add-moonbaseclient-to-pluginprocessorh
{MOONBASE_LICENSING}

# Add CLAP format
add_subdirectory(modules/clap-juce-extensions EXCLUDE_FROM_ALL)

# Add any other modules you want modules here, before the juce_add_plugin call
# juce_add_module(modules/my_module)

# This adds the melatonin inspector module
add_subdirectory (modules/melatonin_inspector)

# See `docs/CMake API.md` in the JUCE repo for all config options
juce_add_plugin("${PROJECT_NAME}"
    # Icons for the standalone app
    ICON_BIG "${CMAKE_CURRENT_SOURCE_DIR}/packaging/icon.png"

    # Change me!
    COMPANY_NAME "${COMPANY_NAME}"
    BUNDLE_ID "${BUNDLE_ID}"

    # On MacOS, plugin is copied to /Users/yourname/Library/Audio/Plug-Ins/
    COPY_PLUGIN_AFTER_BUILD TRUE

    # Change me!
    # A four-character plugin id
    # First character MUST be uppercase for AU formats
    PLUGIN_MANUFACTURER_CODE {MANUFACTURER_CODE}

    # Change me!
    # A unique four-character plugin id
    # Note: this must have at least one upper-case character
    PLUGIN_CODE {PLUGIN_CODE}
    FORMATS "${FORMATS}"

    # The name of your final executable
    # This is how it's listed in the DAW
    # This can be different from PROJECT_NAME and can have spaces!
    # You might want to use v${MAJOR_VERSION} here once you go to v2...
    PRODUCT_NAME "${PRODUCT_NAME}")

# This lets us use our code in both the JUCE targets and our Test target
# Without running into ODR violations
add_library(SharedCode INTERFACE)

clap_juce_extensions_plugin(TARGET "${PROJECT_NAME}"
    CLAP_ID "${BUNDLE_ID}"
    CLAP_FEATURES audio-effect)
	
# Link the moonbase_JUCEClient target to the Pamplejuce target
{MOONBASE_LINKING}

# Enable fast math, C++20 and a few other target defaults
include(SharedCodeDefaults)


# Manually list all .h and .cpp files for the plugin
# If you are like me, you'll use globs for your sanity.
# Just ensure you employ CONFIGURE_DEPENDS so the build system picks up changes
# If you want to appease the CMake gods and avoid globs, manually add files like so:
# set(SourceFiles Source/PluginEditor.h Source/PluginProcessor.h Source/PluginEditor.cpp Source/PluginProcessor.cpp)
file(GLOB_RECURSE SourceFiles CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/source/*.cpp" "${CMAKE_CURRENT_SOURCE_DIR}/source/*.h")
target_sources(SharedCode INTERFACE ${SourceFiles})

# Adds a BinaryData target for embedding assets into the binary
include(Assets)

# Add the config for licensing to binaryData
# we dont need to do this since pamplejuce already does it automagically
# juce_add_binary_data(Assets SOURCES assets/moonbase_api_config.json)

# MacOS only: Cleans up folder and target organization on Xcode.
include(XcodePrettify)

# This is where you can set preprocessor definitions for JUCE and your plugin
target_compile_definitions(SharedCode
    INTERFACE

    # JUCE_WEB_BROWSER and JUCE_USE_CURL off by default
    JUCE_WEB_BROWSER={JUCE_WEB_BROWSER}  # If you set this to 1, add `NEEDS_WEB_BROWSER TRUE` to the `juce_add_plugin` call
    JUCE_USE_CURL={JUCE_USE_CURL}     # If you set this to 1, add `NEEDS_CURL TRUE` to the `juce_add_plugin` call
    JUCE_VST3_CAN_REPLACE_VST2={JUCE_VST3_CAN_REPLACE_VST2}

    # Uncomment if you are paying for a an Indie/Pro license or releasing under GPLv3
    # JUCE 8.0.0 and later no longer require a splash screen
    # JUCE_DISPLAY_SPLASH_SCREEN=0

    # lets the app known if we're Debug or Release
    CMAKE_BUILD_TYPE="${CMAKE_BUILD_TYPE}"
    VERSION="${CURRENT_VERSION}"

    # JucePlugin_Name is for some reason doesn't use the nicer PRODUCT_NAME
    PRODUCT_NAME_WITHOUT_VERSION="{PRODUCT_NAME}"
)

# Link to any other modules you added (with juce_add_module) here!
# Usually JUCE modules must have PRIVATE visibility
# See https://github.com/juce-framework/JUCE/blob/master/docs/CMake%20API.md#juce_add_module
# However, with Pamplejuce, you'll link modules to SharedCode with INTERFACE visibility
# This allows the JUCE plugin targets and the Tests target to link against it
target_link_libraries(SharedCode
    INTERFACE
    Assets
    melatonin_inspector
    juce_audio_utils
    juce_audio_processors
    juce_dsp
    juce_gui_basics
    juce_gui_extra
    juce::juce_recommended_config_flags
    juce::juce_recommended_lto_flags
    juce::juce_recommended_warning_flags)

# Link the JUCE plugin targets our SharedCode target
target_link_libraries("${PROJECT_NAME}" PRIVATE SharedCode)

# IPP support, comment out to disable
include(PamplejuceIPP)

# Everything related to the tests target
include(Tests)

# A separate target for Benchmarks (keeps the Tests target fast)
include(Benchmarks)

# Output some config for CI (like our PRODUCT_NAME)
include(GitHubENV)
"""

def get_gitignore_template():
    """Get the embedded .gitignore template"""
    return """CMakeLists.txt.user
CMakeCache.txt
CMakeFiles
CMakeScripts
Makefile
cmake_install.cmake
install_manifest.txt
compile_commands.json
CTestTestfile.cmake
_deps
**/.DS_Store

# It's nice to have the Builds folder exist, to remind us where it is
Builds/*
!Builds/.gitkeep

# This should never exist
Install/*

# Running CTest makes a bunch o junk
Testing

# IDE config
.idea

# clion cmake builds
cmake-build-debug
cmake-build-release
cmake-build-relwithdebinfo
packaging/Output/*
/.vs
/Assets.dir
/Benchmarks.dir
/DawnCache
/GPUCache
/Debug
/Intel® VTune™ Profiler Results
/juce_binarydata_Assets
/juce_vst3_helper.dir
/Tests.dir
/x64
debug.log
*.filters
*.user
*.lib
/build
/Debug
/juce_binarydata_Assets
WebView2
"""

def get_readme_template():
    """Get the embedded README.md template"""
    return """# {plugin_name}

**{plugin_name}** is {plugin_description}. {plugin_overview}

---

## Features

{plugin_features}

---

## Installation

{installation_instructions}

---

## Usage

{usage_instructions}

---

## Additional Information

{additional_info}

---

## Roadmap

{roadmap}

---

## Feedback and Contributions

{feedback_instructions}

Enjoy using **{plugin_name}**!
"""
