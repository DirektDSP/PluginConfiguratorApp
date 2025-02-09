import uuid


# region template_cmake

# Variables



# endregion








def testerFunction():
    print("This is a test function")
    return True

def create_cmake_file(output_dir, variables):
    
    # Variables
    PROJECT_NAME = variables.get("PROJECT_NAME")
    PRODUCT_NAME = variables.get("PRODUCT_NAME")
    COMPANY_NAME = variables.get("COMPANY_NAME")
    MANUFACTURER_CODE = variables.get("MANUFACTURER_CODE")
    BUNDLE_ID = variables.get("BUNDLE_ID")
    PLUGIN_CODE = variables.get("PLUGIN_CODE")
    FORMATS = variables.get("FORMATS")
    VERSION = variables.get("VERSION")
    CMAKE_PROJECT_NAME = variables.get("CMAKE_PROJECT_NAME")
    JUCE_WEB_BROWSER = variables.get("JUCE_WEB_BROWSER")
    JUCE_USE_CURL = variables.get("JUCE_USE_CURL")
    JUCE_VST3_CAN_REPLACE_VST2 = variables.get("JUCE_VST3_CAN_REPLACE_VST2")
    MOONBASE = variables.get("MOONBASE")

    
    TEMPLATE_FILE = f"""cmake_minimum_required(VERSION 3.25)

# This tells cmake we have goodies in the /cmake folder
list(APPEND CMAKE_MODULE_PATH "${{CMAKE_CURRENT_SOURCE_DIR}}/cmake")
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
#   set(PROJECT_NAME "MyPlugin_v${{MAJOR_VERSION}}")
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
project(${{PROJECT_NAME}} VERSION ${{CURRENT_VERSION}})

# JUCE is setup as a submodule in the /JUCE folder
# Locally, you must run `git submodule update --init --recursive` once
# and later `git submodule update --remote --merge` to keep it up to date
# On Github Actions, this is done as a part of actions/checkout
add_subdirectory(JUCE)

{"add_subdirectory (modules/moonbase_JUCEClient)" if MOONBASE else ""} 

# TODO: CHANGE ME! This must match the product id in assets/moonbase_api_config.json
# see here for more info https://github.com/Moonbase-sh/moonbase_JUCEClient?tab=readme-ov-file#add-moonbaseclient-to-pluginprocessorh
# {f"MOONBASE_DECLARE_LICENSING (\"{COMPANY_NAME}\", \"{PROJECT_NAME}\", VERSION)" if MOONBASE else ""}

# Add CLAP format
add_subdirectory(modules/clap-juce-extensions EXCLUDE_FROM_ALL)

# Add any other modules you want modules here, before the juce_add_plugin call
# juce_add_module(modules/my_module)

# This adds the melatonin inspector module
add_subdirectory (modules/melatonin_inspector)

# See `docs/CMake API.md` in the JUCE repo for all config options
juce_add_plugin("${{PROJECT_NAME}}"
    # Icons for the standalone app
    ICON_BIG "${{CMAKE_CURRENT_SOURCE_DIR}}/packaging/icon.png"

    # Change me!
    COMPANY_NAME "${{COMPANY_NAME}}"
    BUNDLE_ID "${{BUNDLE_ID}}"

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
    FORMATS "${{FORMATS}}"

    # The name of your final executable
    # This is how it's listed in the DAW
    # This can be different from PROJECT_NAME and can have spaces!
    # You might want to use v${{MAJOR_VERSION}} here once you go to v2...
    PRODUCT_NAME "${{PRODUCT_NAME}}")

# This lets us use our code in both the JUCE targets and our Test target
# Without running into ODR violations
add_library(SharedCode INTERFACE)

clap_juce_extensions_plugin(TARGET "${{PROJECT_NAME}}"
    CLAP_ID "${{BUNDLE_ID}}"
    CLAP_FEATURES audio-effect)
	
# Link the moonbase_JUCEClient target to the Pamplejuce target
{f"target_link_libraries(\"{PROJECT_NAME}\" PRIVATE moonbase_JUCEClient)" if MOONBASE else ""}

# Enable fast math, C++20 and a few other target defaults
include(SharedCodeDefaults)


# Manually list all .h and .cpp files for the plugin
# If you are like me, you'll use globs for your sanity.
# Just ensure you employ CONFIGURE_DEPENDS so the build system picks up changes
# If you want to appease the CMake gods and avoid globs, manually add files like so:
# set(SourceFiles Source/PluginEditor.h Source/PluginProcessor.h Source/PluginEditor.cpp Source/PluginProcessor.cpp)
file(GLOB_RECURSE SourceFiles CONFIGURE_DEPENDS "${{CMAKE_CURRENT_SOURCE_DIR}}/source/*.cpp" "${{CMAKE_CURRENT_SOURCE_DIR}}/source/*.h")
target_sources(SharedCode INTERFACE ${{SourceFiles}})

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
    CMAKE_BUILD_TYPE="${{CMAKE_BUILD_TYPE}}"
    VERSION="${{CURRENT_VERSION}}"

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
target_link_libraries("${{PROJECT_NAME}}" PRIVATE SharedCode)

# IPP support, comment out to disable
include(PamplejuceIPP)

# Everything related to the tests target
include(Tests)

# A separate target for Benchmarks (keeps the Tests target fast)
include(Benchmarks)

# Output some config for CI (like our PRODUCT_NAME)
include(GitHubENV)
"""
    
    with open(f"{output_dir}/CMakeLists.txt", "w") as f:
        f.write(TEMPLATE_FILE)
        print("CMakeLists.txt file created")
        f.close()
    

def generate_plugin_id():
    # return a unique 4 character plugin id
    # they must begin with a capital letter.
    capitals = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    return capitals[uuid.uuid4().int % 26] + "".join([characters[uuid.uuid4().int % len(characters)] for i in range(3)])
