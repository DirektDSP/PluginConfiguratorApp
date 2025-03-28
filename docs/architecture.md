# Purpose

Take a starting project, apply a set of defined changes to the project and then create it on the local device.

## Starting Project

<https://DirektDSP/PluginTemplate.git>

Based on PampleJuce by sudara.


## Modifications

implement in a xml file, when generating a new project, allow a config file to be saved as a preset config.

### Possible Modifications

#### Implementations

- Implementing Moonbase_Sh Licensing client
- Implementing Melatonin Inspector
- Implementing CLAP plugin Builds
- Implementing Preset Management System
- Implementing DSP Parallelization on GPU (GPU Audio)
- Implementing State Management/Undo History
- Implementing A/B Comparison Feature
- Implementing Logging Framework
- Implementing Custom GUI Framework

#### Configuration

- Build Settings / Exports (Standalone, VST3, AU) and CLAP if enabled above
- Plugin Metadata (Name, ID, Vendor, Version)
- GUI Settings (Width, Height, Resizable)
- Code Signing Options
- Custom Dependencies (list of new submodules to add)
- Installer Settings
- Custom UI Theme Options (BG Image, Slider Styles, Dropdowns, Etc.)
- DSP Feature Toggles (Default Bypass, In and Out gain)
- APVTS Generation
- Documentation Generation
- Test Framework Integration
- CI/CD Pipeline Configuration

#### User Experience

- Project Creation Wizard UI
- Real-time Preview of Configuration Choices
- Template Library Management
- Preset Configuration Management
- Batch Project Generation

#### Development Workflow

- Version Control Integration
- Automated Testing of Generated Projects
- Post-Generation Code Quality Checks
- Plugin Validation Tools Integration
- Project Scaffolding (README, License, etc.)

#### Advanced Features

- Custom Code Snippet Injection Points
- Post-Generation Scripts
- Multi-Platform Build Configuration
- Analytics Integration
- Crash Reporting Setup

## Architecture

### Application Components

- **Project Templating Engine**: Core system for applying transformations to template projects
- **Configuration Parser**: Reads and validates XML configuration files
- **Modification Manager**: Orchestrates the application of changes to the project
- **Preset System**: Saves and loads configuration presets
- **Project Generator**: Creates the final project on the local filesystem

### Data Flow

1. User selects base template or existing project
2. Configuration is defined (manual or from preset)
3. Modifications are validated for compatibility
4. Changes are applied to the project structure
5. Generated project is built and tested
6. Configuration can be saved as a preset

### Technical Implementation

- **Core Engine**: C++ for performance and direct filesystem access
- **GUI Layer**: JUCE framework for cross-platform UI
- **Config Format**: XML for storing modification rules
- **Templating System**: Token replacement and script execution
- **Plugin Testing**: Automated validation suite for generated projects

## Development Roadmap

### Phase 1: Core Functionality

- Project template loading
- Basic modifications system
- Command-line interface

### Phase 2: User Experience

- GUI implementation
- Preset management
- Real-time preview

### Phase 3: Advanced Features

- Extended modification capabilities
- Integration with build systems
- Plugin validation tools