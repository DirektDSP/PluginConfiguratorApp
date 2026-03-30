# PluginConfiguratorApp UI Revamp Plan

## Overview

Revamp the PluginConfiguratorApp UI to provide a more intuitive, lifecycle-based workflow with both Quick Start (wizard mode) and Advanced configuration options for experienced developers.

---

## Architecture

### Plugin Lifecycle-Based Tabs (4 tabs)

1. **Define** - Concept and identity of the plugin
2. **Configure** - Build options and project setup
3. **Implement** - Feature selection and templates
4. **Generate** - Summary review and project generation

---

## Tab Details

### Tab 1: Define

**Concept and identity of the plugin**

**Core Fields (always visible):**
- Plugin Type Selection (Audio FX / Instrument / Utility)
- Project Name (internal, no spaces)
- Product Name (display name in DAWs)
- Company Name (default: DirektDSP)
- Version (default: 1.0.0)

**Quick Start Toggle:**
- ON = Wizard mode (prefilled defaults, simpler interface)
- OFF = Advanced mode (all options exposed)

**Advanced Fields (only visible when Quick Start OFF):**
- Custom template repository URL
- Manufacturer Code (4 chars, auto-generated)
- Plugin Code (4 chars, auto-generated)
- Bundle ID (auto-format: com.{company}.{project})

**Behavior:**
- Auto-populates derived fields (bundle ID, product name) based on project name
- Plugin code can be auto-generated but also custom
- File tree preview updates in real-time on ALL tabs
- Preview immediately reflects configuration changes (size, layout, included files)

---

### Tab 2: Configure

**Build options and project setup**

**Core Fields (always visible):**
- Plugin Formats:
  - Standandalone checkbox
  - VST3 checkbox (default checked)
  - AU checkbox (default checked)
  - AUv3 checkbox
  - CLAP checkbox (default checked)
- Output Directory (browse button + path display)
- Minimum one format requirement enforced

**Progressive Disclosure Triggers:**

When **AU** is selected:
- Show AU-specific options (AudioComponentDescription fields)
- Show AU versioning options

When **CLAP** is selected:
- Show CLAP extension options
- Show CLAP features configuration

When **AUv3** is selected:
- Show iOS/macOS platform selection
- Show AUv3-specific build options

**Advanced Fields (only visible when Quick Start OFF):**
- **CI/CD Configuration:**
  - Enable GitHub Actions checkbox
  - Target branch selection (main, develop, master, etc.)
  - CI builds format selection
- **Code Signing Options:**
  - Enable code signing checkbox
  - Windows: Azure Trusted Signing checkbox
  - macOS: Developer ID checkbox
  - macOS: Notarization checkbox
- **CMake Configuration:**
  - Custom CMake flags text area
  - Module selection checkboxes (JUCE modules)
- **Branch Configuration:**
  - Use JUCE develop branch checkbox
  - JUCE version pinning option

**Inline Validation:**
- Output directory must exist or be writeable
- At least one format must be selected
- Branch names validated if enabled

---

### Tab 3: Implement

**Feature selection and templates**

**DSP Template Selection:**
Dropdown with options:
- "Simple Gain Plugin" - basic in/out gain only
- "EQ Plugin" - includes filters (High/Low Pass) from PluginTemplate
- "Reverb/Delay Plugin" - includes allpass chain, Haas effect
- "Full DSP Suite" - all PluginTemplate DSP modules (ChasmDSP)
- "Start from scratch" - minimal processor, no DSP components

Each template updates file tree preview.

**UI Template Selection:**
Dropdown with options:
- "Minimal UI" - basic controls only (standard JUCE widgets)
- "Standard UI" - with knobs, sliders, preset panel
- "Advanced UI" - custom components, animated backgrounds, RasterKnob
- "Start from scratch" - minimal editor, no custom components

Each template updates file tree preview.

**Optional Modules** (progressively disclosed):

**Always Visible:**
- ✓ Moonbase Licensing checkbox
  - When checked: reveal license type dropdown, grace period setting
- ✓ Melatonin Inspector checkbox
  - When checked: show "debug mode only" checkbox
- ✓ Preset Management checkbox
  - When checked: reveal format dropdown (XML/JSON/Binary), storage location

**Advanced Features (when Quick Start OFF):**
- State Management / Undo History checkbox
- A/B Comparison Feature checkbox
- Custom GUI Framework checkbox
- Logging Framework checkbox
- GPU Audio checkbox (TODO: will add later) - disabled with tooltip "Coming Soon"

**Progressive Disclosure:**
Each checkbox that reveals additional options should expand/collapse smoothly.

**Advanced Toggle Button (always visible):**
- "Show Advanced Options ▼" when collapsed
- "Hide Advanced Options ▲" when expanded
- Reveals non-critical features (Logging, Custom GUI, GPU Audio)

---

### Tab 4: Generate

**Summary review of all selections**

**Summary Sections:**

```
PROJECT METADATA
  Name: MyGreatPlugin
  Product: My Great Plugin
  Company: DirektDSP
  Version: 1.0.0
  Bundle ID: com.direktdsp.mygreatplugin
  Type: Audio FX Plugin
  Manufacturer Code: Ddsp
  Plugin Code: P001

BUILD CONFIGURATION
  Formats: VST3, AU, CLAP
  Output: /Users/dev/projects/MyGreatPlugin
  Code Signing: Disabled
  CI/CD: GitHub Actions (main branch)

DSP TEMPLATE
  Standard Audio FX
    ✓ Input/Output Gain
    ✓ High/Low Pass Filters
    ✓ Stereo Enhancer
    ✓ Limiter

UI TEMPLATE
  Standard UI
    ✓ Custom knobs and sliders
    ✓ Preset panel
    ✓ Animated background

MODULES
  ✓ Moonbase Licensing
    Type: Commercial
    Grace Period: 14 days
  ✓ Melatonin Inspector
    Debug Mode Only: Yes
  ✓ Preset Management
    Format: XML
  □ State Management
  □ A/B Comparison
  □ GPU Audio  [TODO - Feature not yet implemented]

FILE TREE PREVIEW
  [Collapsed tree showing final structure]
```

**Validation Status:**
- Green checkmarks for all valid sections
- Red warnings for incomplete/invalid sections
- Overall status: "All configurations valid ✓" or "2 issues to fix ❌"

**Action Buttons:**
- **Generate Project** - primary action, disabled if validation fails
- **Back to Edit** - returns to previous tab
- **Save as Preset** - saves current configuration

**Generation Progress:**
Once "Generate Project" is clicked:
- Show progress bar with step-by-step updates
  - Cloning template repository...
  - Fetching submodules...
  - Applying configuration...
  - Generating files...
  - Initializing Git repository...
  - Creating initial commit...
- Show log output in scrollable text area
- Success message:
  ```
  ✅ Project generated successfully!
  Location: /Users/dev/projects/MyGreatPlugin

  [Open in IDE]  [Open in Finder]  [Close]
  ```

---

## Quick Start Flow

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 QUICK START
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Fill in the basics, we'll handle the rest.

Plugin Name: [MyGreatPlugin          ]
Company:     [DirektDSP              ]

Plugin Type: ◉ Audio FX  ○ Instrument  ○ Utility

             ┌─────────────────────────────────┐
             │  What we'll set up for you:     │
             ├─────────────────────────────────┤
             │  ✓ VST3, AU, CLAP formats       │
             │  ✓ Standard DSP template        │
             │  ✓ Preset management included   │
             │  ✓ Melatonin Inspector enabled  │
             │  ✓ CI/CD workflow ready         │
             │  ✓ Output: ~/projects/plugins/  │
             └─────────────────────────────────┘

   [ Review & Generate ]     [ Switch to Advanced Mode ]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Quick Start Behavior

**When Quick Start is enabled:**
- Prefills sensible defaults for all tabs:
  - Project metadata based on input
  - Formats: VST3, AU, CLAP (defaults)
  - DSP Template: "Standard Audio FX"
  - UI Template: "Standard UI"
  - Modules: Preset Management, Melatonin Inspector enabled
  - CI/CD: GitHub Actions enabled (main branch)
- Shows summary immediately (skip to Tab 4)
- Can click "Switch to Advanced Mode" to enable all options
- Can still customize on Tab 4 before generating

**Quick Start defaults should be configurable** via a preset file (`quick_start_defaults.json`), not hardcoded.

Additionally, include **hardcoded example presets** that ship with the app for immediate use:

```json
{
  "formats": ["VST3", "AU", "CLAP"],
  "dsp_template": "Standard Audio FX",
  "ui_template": "Standard UI",
  "modules": {
    "preset_management": true,
    "melatonin_inspector": true,
    "presets_format": "XML"
  },
  "cicd": {
    "enabled": true,
    "branch": "main"
  },
  "output_directory": "~/projects/plugins/",
  "use_default_preset": "StandardAudioFX_Preset.xml"
}
```

**Example Presets (bundled with app):**

Located in `presets/examples/`:
- `StandardAudioFX_Preset.xml` - Full-featured FX plugin with VST3, AU, CLAP
- `Instrument_Preset.xml` - Virtual instrument with MIDI support
- `MinimalPlugin_Preset.xml` - Minimal VST3-only plugin for quick prototyping

These presets are hardcoded examples that users can load immediately or customize and save as their own presets.

---

## Advanced Toggle Behavior

### Implementation: Global Toggle on Tab 1

**Location:** Top-right of Tab 1 (Define)

**Behavior:**
- Single switch labeled "Quick Start" with two states:
  - **ON** (default): Simplified interface, prefilled defaults
  - **OFF**: All options exposed on all tabs
- Affects all tabs - switching updates all tabs' visibility states
- Should preserve user selections when switching between modes

**Preserve Selections When Switching:**
- When enabling Advanced (OFF), show all previously-selected values
- When disabling Advanced (ON), maintain core field values, reset advanced fields to defaults
- Use a "mode switch complete" notification to inform user

---

## Real-Time File Tree Preview

### Overview

A live file tree preview that updates in real-time across all tabs to show how configuration changes affect project size, structure, and layout.

### Placement

- **Always visible** on right side of application (persistent panel)
- Updates immediately when any configuration changes
- Shows project structure with icons (folders, source files, assets, etc.)

### Behavior

**Real-time Updates:**
- Changing plugin type → shows/hides relevant files (MIDI files for instruments)
- Selecting DSP template → adds/removes DSP file groups
- Selecting UI template → updates UI components folder
- Enabling modules → adds module-specific directories and files
- Changing formats → shows format-specific build files

**Visual Indicators:**
- Green checkmarks on files that will be generated
- Gray placeholder text for optional files
- Badge showing total file count and estimated size

**Example File Tree Display:**
```
📁 MyGreatPlugin/
  📄 CMakeLists.txt
  📄 README.md
  📄 LICENSE
  📄 .gitignore
  📁 source/
    📄 PluginProcessor.cpp      ✓
    📄 PluginProcessor.h        ✓
    📄 PluginEditor.cpp         ✓
    📄 PluginEditor.h           ✓
    📁 DSP/
      📄 ChasmDSP.h             ✓
      📁 Core/
        📄 ChasmDSPProcessor.h  ✓
      📁 Filters/
        📄 EQFilters.h          ✓
      📁 Effects/
        📄 StereoEnhancer.h     ✓
    📁 UI/
      📁 Components/
        📄 PresetPanel.h        ✓
        📄 RasterKnob.h         ✓
  📁 assets/
    📄 logo.png
    📄 background.png
  📁 modules/
    📁 melatonin_inspector/    ✓ (enabled)
    📁 moonbase_JUCEClient/    □ (disabled)
  📁 JUCE/                    [submodule]
  📁 tests/
    📄 PluginBasics.cpp         ✓

Total: 23 files (~1.2 MB)
```

### Tab-Specific Preview Features

**Tab 1 (Define):** Shows basic structure with placeholders
- Updates based on plugin type selection
- Shows minimal structure before detailed configuration

**Tab 2 (Configure):** Updates based on format selection
- Shows AU-specific files when AU enabled
- Shows CLAP extensions folder when CLAP enabled
- Shows CI/CD workflow files when GitHub Actions enabled

**Tab 3 (Implement):** Updates based on template/module selection
- Shows DSP files when DSP template selected
- Shows UI components when UI template selected
- Shows module directories when modules enabled

**Tab 4 (Generate):** Final preview summary
- Collapsed view of complete structure
- Highlight any files that will be excluded
- Show file count and estimated project size

### Performance Considerations

- Debounce updates to avoid excessive re-rendering (300ms delay)
- Cache file tree structure for quick updates
- Only update changed sections to maintain smooth scrolling
- Indicate loading state for complex template changes

---

## Progressive Disclosure Use Cases

### 1. Plugin Type Selection
- **Instrument selected** → show:
  - Polyphony options (mono, polyphonic)
  - MIDI features
  - Keyboard/mouse input options
- **Audio FX selected** → show:
  - Wet/Dry mix checkbox
  - Latency compensation checkbox
  - Sidechain checkbox

### 2. Build Format Selection
- **AU enabled** → show:
  - AudioComponentDescription fields
  - AU version format setting
  - macOS platform specifics
- **AUv3 enabled** → show:
  - Target platform checkboxes (iOS, macOS)
  - AUv3 specific build options
- **CLAP enabled** → show:
  - CLAP extensions checklist
  - CLAP features configuration
  - Sample-accurate modulation options

### 3. Module Enabling
- **Moonbase checked** → reveal:
  - License type dropdown (Commercial, Trial, Free)
  - Grace period setting (number of days)
  - Offline activation checkbox
- **Preset Management checked** → reveal:
  - Format dropdown (XML, JSON, Binary)
  - Storage location dropdown (User Library, App Bundle, Custom)
  - Backup presets checkbox

### 4. DSP/UI Templates
- Selecting template updates file tree preview immediately
- "Start from scratch" shows minimal preview
- Template selection should show a brief description of what's included

---

## Inline Validation

### Real-time Feedback as User Types/Selects

#### Field-Level Validation

**Project Name:**
- `MyPlugin` ✅ (valid)
- `My Plugin` ❌ (no spaces allowed)
- `123Plugin` ❌ (must start with letter)
- `my_plugin` ✅ (underscores valid)

**Bundle ID:**
- `com.company.plugin` ✅ (valid format)
- `com..plugin` ❌ (invalid format)
- `my.plugin` ❌ (must start with com.company)

**Manufacturer Code:**
- `AbcD` ✅ (4 characters)
- `Ab` ❌ (must be 4 chars)
- `abc1` ✅ (letters and numbers)

**Plugin Code:**
- `P001` ✅ (4 characters, must have uppercase)
- `p002` ❌ (must have uppercase letter)
- `XYZA` ✅ (all valid)

**Output Directory:**
- `/Users/dev/projects` ✅ (valid, writeable)
- `/nonexistent/path` ❌ (directory does not exist)
- `/readonly/path` ❌ (not writeable)

#### Tab-Level Validation

**Footer on each tab shows:**
- `3 required fields remaining` when incomplete
- `Ready ✓` when tab is complete
- Click on status to see list of issues if any

#### Global Validation

**Status bar shows:**
- `3 tabs configured, ready to generate`
- `Tab 2 (Configure) has issues - 1 required field missing`

**Generate Button:**
- Disabled if any validation fails
- Shows tooltip listing all issues on hover

---

## Navigation & Workflow

### Tab Navigation
- Each tab has "Previous" and "Next" buttons at the bottom
- Tab can be changed directly via tab bar
- "Next" button validation: can't proceed if current tab invalid

### Quick Start Shortcut
- When Quick Start is ON with minimal fields filled:
  - "Review & Generate" button on Tab 1 jumps directly to Tab 4 (Generate)
  - Summary prefilled with intelligent defaults

### Mode Switching
- "Switch to Advanced Mode" on Quick Start screen:
  - Enables all options across all tabs
  - Maintains current selections
  - Shows notification: "Advanced mode enabled - all options now visible"
- Can switch back to Quick Start anytime from Tab 1

---

## Preset Management

### Preset System (Templates as Presets)

**Purpose:** Save and load common configurations as reusable templates

**Storage Location:**
- User presets: `~/.plugin_configurator/presets/` directory
- Example presets: `presets/examples/` directory (bundled with app)
- XML format for portability and version control

**Actions:**
- **Save as Preset** - available on all tabs via menu (File → Save as Preset)
- **Load Preset** - available on Tab 1 (Define) via "Load Template" button
- **Delete Preset** - in preset management dialog
- **Export Preset** - export to file for sharing
- **Import Preset** - import from file

**Preset Dialog UI:**
```
┌─────────────────────────────────────────┐
│  Load Template                         │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐   │
│  │ Example Templates (Built-in)      │   │
│  ├──────────────────────────────────┤   │
│  │ 📄 StandardAudioFX_Preset.xml     │   │
│  │    VST3, AU, CLAP | EQ & Filters │   │
│  │ 📄 Instrument_Preset.xml          │   │
│  │    VST3 | Polyphonic + Presets    │   │
│  │ 📄 MinimalPlugin_Preset.xml       │   │
│  │    VST3 only | No extras          │   │
│  └──────────────────────────────────┘   │
│                                         │
│  ┌──────────────────────────────────┐   │
│  │ My Presets                        │   │
│  ├──────────────────────────────────┤   │
│  │ 📁 My Custom FX Setup            │   │
│  │ 📁 DirektDSP Standard Config     │   │
│  └──────────────────────────────────┘   │
│                                         │
│              [Load]  [Cancel]          │
└─────────────────────────────────────────┘
```

**Preset Content:**
Saves ALL settings from all tabs including:
- Metadata (project name, company, codes)
- Build configuration (formats, CI/CD)
- DSP/UI template selections
- Module enablements
- All advanced options

**Example Preset Files:**

`presets/examples/StandardAudioFX_Preset.xml`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<preset version="1.0">
  <name>Standard Audio FX</name>
  <description>Ready-to-use FX plugin with EQ, filters, and preset management</description>

  <define>
    <plugin_type>Audio FX</plugin_type>
    <company_name>DirektDSP</company_name>
    <version>1.0.0</version>
  </define>

  <configure>
    <formats>
      <format>VST3</format>
      <format>AU</format>
      <format>CLAP</format>
    </formats>
    <cicd>
      <enabled>true</enabled>
      <branch>main</branch>
    </cicd>
  </configure>

  <implement>
    <dsp_template>Standard Audio FX</dsp_template>
    <ui_template>Standard UI</ui_template>
    <modules>
      <module name="moonbase_licensing" enabled="false"/>
      <module name="melatonin_inspector" enabled="true"/>
      <module name="preset_management" enabled="true">
        <format>XML</format>
      </module>
      <module name="ab_comparison" enabled="false"/>
    </modules>
  </implement>
</preset>
```

`presets/examples/Instrument_Preset.xml`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<preset version="1.0">
  <name>Instrument Plugin</name>
  <description>Virtual instrument with preset management and MIDI support</description>

  <define>
    <plugin_type>Instrument</plugin_type>
    <company_name>DirektDSP</company_name>
    <version>1.0.0</version>
  </define>

  <configure>
    <formats>
      <format>VST3</format>
      <format>AU</format>
    </formats>
    <cicd>
      <enabled>true</enabled>
      <branch>develop</branch>
    </cicd>
  </configure>

  <implement>
    <dsp_template>Start from scratch</dsp_template>
    <ui_template>Standard UI</ui_template>
    <modules>
      <module name="moonbase_licensing" enabled="true"/>
      <module name="melatonin_inspector" enabled="true"/>
      <module name="preset_management" enabled="true">
        <format>JSON</format>
      </module>
    </modules>
  </implement>
</preset>
```

`presets/examples/MinimalPlugin_Preset.xml`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<preset version="1.0">
  <name>Minimal Plugin</name>
  <description>S bare-bones plugin with VST3 only, no extras</description>

  <define>
    <plugin_type>Audio FX</plugin_type>
    <company_name>DirektDSP</company_name>
    <version>1.0.0</version>
  </define>

  <configure>
    <formats>
      <format>VST3</format>
    </formats>
    <cicd>
      <enabled>false</enabled>
    </cicd>
  </configure>

  <implement>
    <dsp_template>Start from scratch</dsp_template>
    <ui_template>Minimal UI</ui_template>
    <modules>
      <module name="melatonin_inspector" enabled="true"/>
    </modules>
  </implement>
</preset>
```

---

## TODO Features to Remove/Document

### Features to Remove from UI (Now):

1. **Advanced Tab** - remove entirely (placeholder content)
2. **Batch Project Generation** - remove checkbox from UX tab
3. **Template Library Management** - remove checkbox from UX tab
4. **Project Creation Wizard UI** checkbox - confusing, remove

### Features to Document as TODO:

1. **GPU Audio (DSP Parallelization)** - keep checkbox but disabled with tooltip "Coming Soon"
2. **Custom GUI Framework** - keep as checkbox for now
3. **Logging Framework** - keep as checkbox for now
4. **Plugin Validation Tools Integration** - keep checkbox for now

### TODO Documentation Location:

**MkDocs Documentation Structure:**

Create a dedicated MkDocs environment in `docs/` directory for comprehensive documentation:

```
docs/
├── mkdocs.yml                    # MkDocs configuration
├── index.md                      # Home/Overview
├── user-guide/
│   ├── quick-start.md            # Quick Start guide
│   ├── configuration.md          # Configuration options
│   ├── presets.md                # Preset management
│   └── generating-projects.md    # Project generation
├── development/
│   ├── architecture.md           # System architecture
│   ├── contributing.md           # Contribution guide
│   └── building.md               # Build instructions
└── roadmap/
    ├── features.md               # Feature roadmap
    ├── known-issues.md           # Known issues
    └── changelog.md              # Changelog
```

**docs/roadmap/features.md structure:**
```markdown
# Feature Roadmap

## Priority: High
- [ ] Implement GPU Audio DSP parallelization
- [ ] Add plugin validation tools integration
- [ ] Complete logging framework implementation

## Priority: Medium
- [ ] Implement custom GUI framework components
- [ ] Add project scaffolding beyond README/LICENSE
- [ ] Add code quality checks in post-generation

## Priority: Low
- [ ] Batch project generation
- [ ] Template library management UI
- [ ] Analytics integration

## Backlog
- [ ] Crash reporting setup
- [ ] Performance benchmarking integration
```

**MkDocs configuration (docs/mkdocs.yml):**
```yaml
site_name: PluginConfiguratorApp Docs
site_description: Documentation for the PluginConfiguratorApp
site_author: DirektDSP

nav:
  - Home: index.md
  - Quick Start: quick-start.md
  - User Guide:
    - Configuration: configuration.md
    - Presets: presets.md
    - Generating Projects: generating-projects.md
  - Development:
    - Architecture: architecture.md
    - Contributing: contributing.md
    - Building: building.md
  - Roadmap:
    - Features: roadmap/features.md
    - Known Issues: roadmap/known-issues.md

theme:
  name: material
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: indigo
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: blue

plugins:
  - search
  - awesome-pages
```

---

## Code Architecture Improvements

### Base Tab Class

Create `BaseTab` class to reduce code duplication:

```python
class BaseTab(QWidget):
    """Base class for all widget tabs with common methods"""

    def __init__(self, parent=None):
        super().__init__(parent)

    def get_configuration(self) -> dict:
        """Get current configuration from this tab"""
        raise NotImplementedError

    def load_configuration(self, config: dict) -> None:
        """Load configuration into this tab"""
        raise NotImplementedError

    def validate(self) -> (bool, list):
        """
        Validate tab configurations
        Returns: (is_valid, error_messages)
        """
        raise NotImplementedError

    def reset(self) -> None:
        """Reset tab to default values"""
        raise NotImplementedError
```

All tabs inherit from `BaseTab` and implement required methods.

### Configuration Manager Singleton

Centralized configuration management:

```python
class ConfigurationManager:
    """Singleton for managing app-wide configuration"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.config = {}
        self.quick_start_mode = True
        self.validation_errors = []

    def update_config(self, tab_name: str, config: dict):
        """Update configuration from a tab"""
        self.config[tab_name] = config

    def get_full_config(self) -> dict:
        """Get complete configuration from all tabs"""
        return self.config

    def toggle_quick_start(self, enabled: bool):
        """Toggle quick start mode"""
        self.quick_start_mode = enabled

    def validate_all(self) -> (bool, list):
        """Validate all tabs"""
        # Implementation
        pass
```

### Quick Start Defaults Manager

```python
class QuickStartDefaults:
    """Loads and manages quick start default configuration"""

    DEFAULTS_PATH = "~/.plugin_configurator/quick_start_defaults.json"

    @classmethod
    def load_defaults(cls) -> dict:
        """Load defaults from JSON file"""
        # Implementation
        pass

    @classmethod
    def save_defaults(cls, defaults: dict) -> None:
        """Save defaults to JSON file"""
        # Implementation
        pass

    @classmethod
    def get_factory_defaults(cls) -> dict:
        """Get hardcoded factory defaults"""
        return {
            "formats": ["VST3", "AU", "CLAP"],
            "dsp_template": "Standard Audio FX",
            # ...
        }
```

---

## Implementation Priorities

### Phase 1: Core Reorganization (High Priority)
- [ ] Create 4 new tabs with proper content
- [ ] Implement BaseTab base class
- [ ] Implement ConfigurationManager singleton
- [ ] Move existing code to new structure
- [ ] Remove Advanced tab, clean up placeholder features

### Phase 2: Quick Start Mode (High Priority)
- [ ] Implement Quick Start toggle on Tab 1
- [ ] Create Quick Start defaults JSON file
- [ ] Implement defaults loading and application
- [ ] Implement "Review & Generate" shortcut
- [ ] Implement mode switching with state preservation

### Phase 3: Progressive Disclosure (Medium Priority)
- [ ] Implement accordion-style expanders for module options
- [ ] Implement format-specific disclosure (AU, CLAP)
- [ ] Implement plugin type disclosure (Instrument vs FX)

### Phase 4: Inline Validation (Medium Priority)
- [ ] Implement field-level validation utilities
- [ ] Add visual feedback (green/red indicators)
- [ ] Implement tab-level validation status
- [ ] Add validation tooltips to Generate button

### Phase 5: Summary Page (Medium Priority)
- [ ] Implement summary sections
- [ ] Add file tree preview summary
- [ ] Implement Generate button with progress tracking
- [ ] Add success message with IDE/Finder buttons

### Phase 6: Preset Management (Low Priority)
- [ ] Implement preset file format XML
- [ ] Implement save/load functionality
- [ ] Create preset management dialog
- [ ] Add preset directory management

---

## Design System & Styling

### Color Palette (Nord-inspired)

**Light Theme:**
- Primary: `#5e81ac` (Nord Blue)
- Success: `#a3be8c` (Nord Green)
- Error: `#bf616a` (Nord Red)
- Warning: `#ebcb8b` (Nord Yellow)
- Background: `#eceff4` (Nord Lightest)
- Surface: `#ffffff`

**Dark Theme:**
- Primary: `#81a1c1` (Nord Blue Light)
- Success: `#a3be8c` (Nord Green)
- Error: `#bf616a` (Nord Red)
- Warning: `#ebcb8b` (Nord Yellow)
- Background: `#2e3440` (Nord Darkest)
- Surface: `#3b4252` (Nord Dark)

### Typography

- Headings: `font-weight: bold; font-size: 14px;`
- Labels: `font-size: 12px;`
- Help text: `font-size: 10px; color: #88c0d0;`
- Error text: `font-size: 11px; color: #bf616a;`

### Spacing

- Section spacing: 16px vertical
- Field spacing: 12px vertical
- Form padding: 24px
- Button padding: 8px 16px

---

## Success Metrics

After revamp:

1. **Time to generate plugin** (Quick Start): < 3 minutes
2. **Time to generate complex plugin** (Advanced): < 10 minutes
3. **Field validation rate**: > 95% of errors caught inline
4. **User satisfaction**: Survey after 1 month of use
5. **Configuration reuse**: Track preset save/load frequency

---

## Questions Resolved

| Question | Resolution |
|----------|------------|
| DSP/UI templates as presets or actual templates? | Implement templates as XML preset files that users can save and reuse |
| Quick Start defaults configuration? | External JSON file (`quick_start_defaults.json`) with hardcoded example presets in `presets/examples/` |
| TODO features documentation? | Dedicated MkDocs environment in `docs/` folder with comprehensive documentation roadmap |
| Quick Start/Advanced mode state preservation? | Maintain user selections when switching modes (nothing gets lost) |
| File tree preview location? | Persistent panel visible on ALL tabs, showing real-time updates throughout configuration |

---

## End of Plan

Last Updated: March 13, 2026
Status: Ready for Implementation

## Key Changes from Original Plan

Based on additional stakeholder feedback:

1. **Templates as Presets** - DSP/UI templates are now XML preset files (not hardcoded configurations)
2. **Example Presets** - Ship with 3 hardcoded example presets for immediate use
3. **MkDocs Documentation** - Replaced TODO.md with comprehensive MkDocs documentation structure
4. **Mode State Preservation** - Confirmed: switching between Quick Start/Advanced preserves all selections
5. **Real-Time File Tree** - Enhanced: now persistent across all tabs showing size/layout impact in real-time