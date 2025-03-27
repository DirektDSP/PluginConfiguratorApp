# Plugin Configurator App

## Overview
A specialized application for creating and configuring audio plugin projects using custom GitHub template repositories. Inspired by JUCE's Projucer, this tool streamlines the setup process for developing professional audio plugins.

## Purpose
Plugin Configurator helps audio developers quickly bootstrap new plugin projects with the right architecture and build configurations. It handles the boilerplate setup so you can focus on creating your audio processing code.

## Key Features
- **Project Generation**: Create new audio plugin projects with proper CMake setup
- **Template Flexibility**: Use any compatible GitHub repository as your project template
- **Format Selection**: Configure support for VST3, AU, AUv3, CLAP, and Standalone formats
- **JUCE Integration**: Seamless setup of JUCE dependencies and modules
- **CMake Configuration**: Generates optimized build scripts for cross-platform development
- **Template Customization**: Save and reuse project configurations

## Template System
The configurator's flexibility comes from its template system:
- **Default Template**: Works with the [PluginTemplate](https://github.com/SeamusMullan/PluginTemplate.git) repository
- **Custom Templates**: Use any GitHub repository that follows our template structure
- **Fork & Customize**: Create your own template by forking our base template
- **Save Configurations**: Export your settings as XML for future projects

## Audio Plugin Project Structure
```
MyAudioPlugin/
├── source/
│   ├── PluginProcessor.cpp
│   ├── PluginProcessor.h
│   ├── PluginEditor.cpp
│   └── PluginEditor.h
├── assets/
│   └── icon.png
├── JUCE/
│   └── (JUCE submodule)
├── modules/
│   ├── clap-juce-extensions/
│   └── melatonin_inspector/
├── tests/
├── CMakeLists.txt
├── packaging/
└── .github/workflows/
```

## Creating Compatible Templates
To create a compatible template repository:
1. Fork the base PluginTemplate repository
2. Modify source files, assets, and other components
3. Maintain the CMake structure for variable substitution
4. Keep the submodule structure for JUCE and other dependencies
5. Use your custom template URL in the configurator

## Supported Plugin Formats
- **VST3** - Industry standard plugin format
- **AU/AUv3** - Apple's Audio Unit formats for macOS/iOS
- **CLAP** - Open plugin standard with modern features
- **Standalone** - Run your plugin as a standalone application

## Configuration Options
- Project name and metadata
- Company information
- Plugin formats to support
- JUCE module selection
- Build system options
- GitHub integration
- Testing framework setup

## Workflow

1. **Select Template**: Enter a compatible GitHub repository URL
2. **Create Project**: Define basic project parameters
3. **Configure Formats**: Select which plugin formats to support
4. **Select Extensions**: Add optional modules like Melatonin Inspector
5. **Generate**: Create the project structure with all required files
6. **Build**: Open in your IDE or build from command line

## Integration with Development Tools
- Support for modern IDEs (Visual Studio, Xcode, CLion)
- GitHub Actions workflow generation for CI/CD
- CMake-based build system for cross-platform development
- Installer packaging scripts

## Benefits for Audio Developers
- Reduce time spent on project setup
- Ensure consistent project structure
- Follow best practices for audio plugin development
- Focus on creating your DSP algorithms and UI
- Streamline cross-platform deployment
- Customize your starting point with different templates