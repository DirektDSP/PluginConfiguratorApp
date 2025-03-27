# Plugin Configurator App Implementation

## Architecture Overview

The Plugin Configurator App is designed specifically for creating and configuring audio plugin projects, similar to JUCE's Projucer but with a focus on modern CMake-based workflows and custom template repositories.

```
┌──────────────────┐      ┌─────────────────────┐      ┌──────────────────┐
│                  │      │                     │      │                  │
│  GUI Layer       │───→  │  Plugin Project     │───→  │  Template        │
│  (PyQt6)         │  ↑   │  Generator          │  ↑   │  Engine          │
│                  │  │   │                     │  │   │                  │
└──────────────────┘  │   └─────────────────────┘  │   └──────────────────┘
                      │                            │
                      └────────────────────────────┘
                              Configuration Flow
```

## Template Repository System

The app is built around a flexible template system:

- **Repository URL Input**: Users can specify any compatible GitHub repository
- **Default Template**: Falls back to [PluginTemplate](https://github.com/SeamusMullan/PluginTemplate.git) if none provided
- **Template Validation**: Checks if the provided repository has the required structure
- **Fork Detection**: Recognizes if a repository is a fork of the base template

### Template Compatibility Requirements

For a GitHub repository to work with the configurator:

1. **CMake Structure**: Must have a CMakeLists.txt that accepts variable substitution
2. **Submodule Organization**: Must use JUCE and other modules as submodules
3. **Source File Structure**: Must follow standard plugin source organization
4. **GitHub Workflow Files**: Should have compatible CI/CD workflow templates

## Technical Stack

- **GUI Framework**: PyQt6 for cross-platform UI
- **Template Engine**: String-based template system for generating CMake and source files
- **Version Control**: Git integration for repository initialization and submodule management
- **Build System**: CMake generation for modern cross-platform builds

## Core Components

### 1. GUI Layer

The interface is organized into logical sections for plugin configuration:

1. **Template Repository**: URL input for the GitHub template
2. **Project Settings**: Basic project information and output location
3. **Plugin Formats**: Selection of supported plugin formats (VST3, AU, CLAP, etc.)
4. **Extensions**: Optional components like Melatonin Inspector or Moonbase integration
5. **Build Options**: JUCE-specific build configurations
6. **Progress and Logging**: Feedback on project generation process

#### Main Window Layout

```
┌────────────────────────────────────────────────────────┐
│ Plugin Configurator                                ⊖ □ X │
│ ┌──────────────────────────────────────────────────┐ │
│ │               Project Information                 │ │
│ │ ┌─────────────────┐      ┌─────────────────────┐ │ │
│ │ │  Project Info   │      │      Options        │ │ │
│ │ │                 │      │                     │ │ │
│ │ │ Fork URL        │      │ Enabled Formats     │ │ │
│ │ │ Project Name    │      │ ☑ VST3  ☑ AU  ☑ CLAP│ │ │
│ │ │ Product Name    │      │                     │ │ │
│ │ │ Company Name    │      │ Extensions          │ │ │
│ │ │ Bundle ID       │      │ ☑ Melatonin         │ │ │
│ │ │ Manufacturer ID │      │ ☐ Moonbase          │ │ │
│ │ │                 │      │                     │ │ │
│ │ │ Output Directory│      │ JUCE Options        │ │ │
│ │ │ [Browse...]     │      │ ☐ Web Browser       │ │ │
│ │ └─────────────────┘      └─────────────────────┘ │ │
│ │                                                  │ │
│ │ [Generate Project]                               │ │
│ └──────────────────────────────────────────────────┘ │
│ ┌──────────────────────────────────────────────────┐ │
│ │               Progress                            │ │
│ │ [=========================================>  95%] │ │
│ │ ┌──────────────────────────────────────────────┐ │ │
│ │ │ > Cloning template...                         │ │ │
│ │ │ > Fetching submodules...                      │ │ │
│ │ │ > Configuring CMake...                        │ │ │
│ │ │ > Generating project files...                 │ │ │
│ │ └──────────────────────────────────────────────┘ │ │
│ └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

### 2. Plugin Project Generator

The core engine that manages the project generation process:

- **TemplateCloner**: Retrieves the specified template from GitHub
- **TemplateValidator**: Checks if the template is compatible
- **SubmoduleManager**: Handles JUCE and extension submodules
- **CMakeGenerator**: Creates customized CMakeLists.txt
- **SourceFileGenerator**: Sets up initial source files with proper naming
- **GitInitializer**: Creates a fresh Git repository

### 3. Template Engine

The template system handles file generation:

- **TextTemplateProcessor**: Processes text templates for README, CMake files
- **FileStructureGenerator**: Creates project directory structure
- **WorkflowGenerator**: Sets up GitHub Actions workflows

## Implementation Details

### Project Generation Workflow

1. **Template Acquisition**:
   - Clone the specified GitHub template repository
   - Validate template structure and compatibility
   - Reset Git history for a fresh start

2. **User Input Collection**:
   - Gather project metadata (name, company, etc.)
   - Select plugin formats to support
   - Choose optional extensions and modules

3. **Submodule Setup**:
   - Initialize required submodules (JUCE, etc.)
   - Add optional submodules as selected (Melatonin, etc.)

4. **Configuration Generation**:
   - Create customized CMakeLists.txt based on user options
   - Configure build settings for selected formats
   - Set up GitHub workflow files

5. **Project Finalization**:
   - Initialize new Git repository
   - Create initial commit
   - Generate README with project information

### Template Repository Handling

```python
def clone_template_repository(template_url, output_dir):
    """
    Clone the specified template repository and validate its structure.
    Falls back to default template if URL is invalid.
    """
    default_template = "https://github.com/SeamusMullan/PluginTemplate.git"
    
    try:
        # Attempt to clone the specified template
        subprocess.run(["git", "clone", template_url, output_dir], check=True)
        
        # Validate template structure
        if not is_valid_template(output_dir):
            raise ValueError("Invalid template structure")
            
    except Exception as e:
        # Clean up any partial clone
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
            
        # Fall back to default template
        subprocess.run(["git", "clone", default_template, output_dir], check=True)
        
    # Reset Git history to treat as a template
    git_dir = os.path.join(output_dir, ".git")
    if os.path.exists(git_dir):
        shutil.rmtree(git_dir)
```

```python
def is_valid_template(directory):
    """
    Check if the provided directory contains a valid template structure.
    """
    # Required files for a valid template
    required_files = [
        "CMakeLists.txt",
        ".github/workflows/build_and_test.yml",
        "source/PluginProcessor.cpp",
        "source/PluginProcessor.h",
        "source/PluginEditor.cpp",
        "source/PluginEditor.h"
    ]
    
    # Check if all required files exist
    for file in required_files:
        if not os.path.exists(os.path.join(directory, file)):
            return False
            
    return True
```

### CMake Generation

CMake is generated from templates with parameter substitution:

```python
def create_cmake_file(output_dir, variables: dict):
    """
    Generate a customized CMakeLists.txt file based on user selections.
    """
    template = read_template("cmake_template.txt")
    # Replace variables in template
    for key, value in variables.items():
        template = template.replace(f"{{{key}}}", str(value))
    
    # Write to output directory
    with open(f"{output_dir}/CMakeLists.txt", "w") as f:
        f.write(template)
```

### Submodule Management

```python
def setup_submodules(output_dir, submodules):
    """
    Configure and initialize Git submodules.
    """
    for submodule in submodules:
        if submodule["enabled"]:
            subprocess.run([
                "git", "submodule", "add", 
                submodule["url"], 
                submodule["path"]
            ], cwd=output_dir)
    
    # Initialize all submodules
    subprocess.run([
        "git", "submodule", "update", "--init", "--recursive"
    ], cwd=output_dir)
```

## Template Customization

### Creating a Custom Template

To create a custom template compatible with the configurator:

1. **Fork the Base Template**:
   ```
   git clone https://github.com/SeamusMullan/PluginTemplate.git my-custom-template
   cd my-custom-template
   git remote set-url origin https://github.com/yourusername/my-custom-template.git
   ```

2. **Customize Source Files**:
   - Modify the default plugin processor and editor classes
   - Add custom DSP algorithms or UI components
   - Include additional assets or resources

3. **Adjust CMake Configuration**:
   - Ensure variable placeholders remain intact (e.g., `{PROJECT_NAME}`)
   - Add any additional dependencies or modules
   - Configure default build options

4. **Push to GitHub**:
   ```
   git add .
   git commit -m "Customize plugin template"
   git push -u origin main
   ```

5. **Use in Configurator**:
   - Enter your repository URL in the Fork URL field
   - Proceed with project configuration

## Development Workflow

The application is built with a user-friendly workflow in mind:

1. **Template Selection**: Choose a compatible template repository
2. **Input Collection**: Easy-to-use form for project settings
3. **Validation**: Check inputs for correctness before proceeding
4. **Generation**: Clear progress indication during project creation
5. **Results**: Open folder or show success message when complete

## Testing Strategy

- **Unit Tests**: Test core generator functions
- **Integration Tests**: Verify template processing
- **Acceptance Tests**: Generate real projects and validate they build correctly
- **Template Compatibility Tests**: Validate various templates work correctly

## Future Enhancements

- **Template Marketplace**: Share and download specialized audio plugin templates
- **Plugin Presets**: Save configurations for different types of audio plugins
- **Build Integration**: Direct integration with build tools and IDEs
- **Template Rating System**: Community ratings for shared templates
- **Template Previews**: Preview template contents before generating
- **Local Template Support**: Use local directories as templates
