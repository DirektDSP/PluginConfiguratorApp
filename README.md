# Plugin Configurator App

A desktop application for creating and configuring audio plugin projects based on custom template repositories.

## Overview

Plugin Configurator is a tool designed for audio developers to quickly set up new plugin projects with proper structure and build configuration. It's inspired by JUCE's Projucer but focused on modern CMake-based workflows.

## Features

- Create new audio plugin projects with proper CMake configuration
- **Use any compatible GitHub template repository** as your project base
- Configure support for VST3, AU, AUv3, CLAP, and Standalone formats
- Set up GitHub Actions for CI/CD
- Include testing frameworks and optional modules
- Generate consistent, well-structured plugin projects
- Ship with ready-to-use configuration presets (see `docs/presets.md`)

## Template Compatibility

While the app works out of the box with our [PluginTemplate](https://github.com/SeamusMullan/PluginTemplate.git) repository, you can use any GitHub template that follows the same structure:

- CMake-based build system
- JUCE as a submodule
- Standard plugin source file organization
- Support for the same plugin formats

## Installation

### Prerequisites

- Python 3.8 or higher
- Git (for cloning the template and managing submodules)
- CMake 3.15 or higher (for building the generated projects)

### Method 1: Running from source

```bash
# Clone the repository
git clone https://github.com/SeamusMullan/PluginConfiguratorApp.git
cd PluginConfiguratorApp

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

### Method 2: Installation via pip

```bash
# Clone the repository
git clone https://github.com/SeamusMullan/PluginConfiguratorApp.git
cd PluginConfiguratorApp

# Install the package
pip install .

# Run the application
plugin-configurator
```

## Usage

1. Launch the application using one of the methods above
2. Enter the GitHub URL of your template repository (or use the default)
3. Enter basic project information:
   - Project Name: Internal name (no spaces)
   - Product Name: Display name in DAWs
   - Company Name: Your company
   - Bundle ID: Unique identifier for your plugin
   - Manufacturer Code: 4-character manufacturer code
4. Select output directory where your project will be created
5. Configure plugin formats and options in the Options panel
6. Click "Generate Project"
7. Open the generated project in your IDE and start developing!

## Configuration Options

### Plugin Formats

- VST3
- Audio Unit (AU)
- Audio Unit v3 (AUv3)
- CLAP
- Standalone Application

### Config Features

- Initialize Git Repository
- Include Melatonin Inspector (debugging UI)
- Moonbase Licensing
- CLAP Export Support
- Use JUCE Develop Branch
- XCode Prettify (for macOS development)

### JUCE Options

- Enable JUCE_USE_CURL
- Enable JUCE_WEB_BROWSER
- Enable JUCE_VST3_CAN_REPLACE_VST2

## Creating Compatible Template Repositories

To create a repository that works with this configurator:

1. Fork the [PluginTemplate](https://github.com/SeamusMullan/PluginTemplate.git) repository
2. Modify it to your needs while keeping the basic structure
3. Ensure your CMakeLists.txt can accept the same variables our configurator provides
4. Use your fork's URL in the configurator

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
