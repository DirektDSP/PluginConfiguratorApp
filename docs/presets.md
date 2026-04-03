## Preset XML Schema

Presets are stored as XML with a single `<preset>` root element. They map directly to the
tab structure used by the application (`project_info`, `configuration`, `implementations`,
`user_experience`, and `development_workflow`). Each section contains simple elements with
string, integer, or boolean values.

### Schema Versioning

The `<preset>` element carries a `schema_version` attribute. This allows the application to
detect and handle format changes across releases. The current schema version is **1.0**.

When loading a preset file the application reads this attribute and defaults to `"1.0"` if
the attribute is absent (backwards-compatible with older preset files).

### Formal XSD Schema

A machine-readable W3C XML Schema Definition is bundled at:

```
src/resources/presets/preset_schema.xsd
```

The XSD can be used by XML-aware IDEs (VS Code, IntelliJ, etc.) and external validators to
check preset files before loading them into the application. Python code can validate files
programmatically using `PresetXSDValidator` from `core.preset_validator`:

```python
from core.preset_validator import PresetXSDValidator

validator = PresetXSDValidator()
ok, errors = validator.validate_file("path/to/my_preset.xml")
if not ok:
    print("\n".join(errors))
```

`validate_string(xml_content: str)` is also available for validating in-memory XML.

### Full Preset Example

```xml
<?xml version="1.0" encoding="utf-8"?>
<preset name="PresetName" schema_version="1.0">
  <meta>
    <description>Optional human-friendly description</description>
  </meta>
  <project_info>
    <template_name>Audio FX Plugin</template_name>
    <template_url>https://github.com/SeamusMullan/PluginTemplate.git</template_url>
    <project_name>MyPlugin</project_name>
    <product_name>My Plugin</product_name>
    <version>1.0.0</version>
    <company_name>DirektDSP</company_name>
    <bundle_id>com.direkt.myplugin</bundle_id>
    <manufacturer_code>DkFX</manufacturer_code>
    <plugin_code>DKFX</plugin_code>
    <output_directory>~/AudioPlugins/MyPlugin</output_directory>
  </project_info>
  <configuration>
    <standalone>true</standalone>
    <vst3>true</vst3>
    <au>true</au>
    <auv3>false</auv3>
    <clap>true</clap>
    <!-- Audio Unit component descriptor -->
    <au_component_type>aufx</au_component_type>
    <au_component_subtype>plug</au_component_subtype>
    <au_component_manufacturer>DkFX</au_component_manufacturer>
    <au_version>1.0.0</au_version>
    <!-- CLAP identifiers (comma-separated lists) -->
    <clap_extensions>note-ports,state</clap_extensions>
    <clap_features>audio-effect</clap_features>
    <!-- AUv3 target platform -->
    <auv3_platform>iOS</auv3_platform>
    <gui_width>1100</gui_width>
    <gui_height>700</gui_height>
    <resizable>true</resizable>
    <background_image></background_image>
    <code_signing>false</code_signing>
    <installer>false</installer>
    <default_bypass>false</default_bypass>
    <input_gain>true</input_gain>
    <output_gain>true</output_gain>
  </configuration>
  <implementations>
    <moonbase_licensing>false</moonbase_licensing>
    <melatonin_inspector>true</melatonin_inspector>
    <custom_gui_framework>false</custom_gui_framework>
    <logging_framework>true</logging_framework>
    <clap_builds>true</clap_builds>
    <preset_management>true</preset_management>
    <preset_format>XML</preset_format>
    <ab_comparison>true</ab_comparison>
    <state_management>true</state_management>
    <gpu_audio>false</gpu_audio>
  </implementations>
  <user_experience>
    <wizard>true</wizard>
    <preview>true</preview>
    <preset_management>true</preset_management>
  </user_experience>
  <development_workflow>
    <vcs>true</vcs>
    <testing>true</testing>
    <code_quality>true</code_quality>
    <validation_tools>true</validation_tools>
    <scaffolding>true</scaffolding>
  </development_workflow>
</preset>
```

### Schema Field Reference

#### `<preset>` attributes

| Attribute        | Required | Description                                          |
|------------------|----------|------------------------------------------------------|
| `name`           | No       | Human-readable preset display name.                  |
| `schema_version` | No       | Schema format version; defaults to `"1.0"`.          |

#### `<meta>` section (optional)

| Element       | Type   | Description                             |
|---------------|--------|-----------------------------------------|
| `description` | string | Free-text description of the preset.    |

#### `<project_info>` section

| Element              | Type   | Required* | Description                                       |
|----------------------|--------|-----------|---------------------------------------------------|
| `template_name`      | string |           | Display name of the JUCE project template.        |
| `template_url`       | string |           | Git URL of the project template repository.       |
| `project_name`       | string | yes       | CamelCase project identifier (no spaces).         |
| `product_name`       | string | yes       | Human-readable plugin display name.               |
| `version`            | string |           | Semantic version string, e.g. `1.0.0`.            |
| `company_name`       | string | yes       | Developer or studio name.                         |
| `bundle_id`          | string | yes       | Reverse-domain ID, e.g. `com.company.plugin`.     |
| `manufacturer_code`  | string | yes       | 4-character JUCE manufacturer code.               |
| `plugin_code`        | string |           | 4-character JUCE plugin code (auto-generated if empty). |
| `output_directory`   | string | yes       | Filesystem path for the generated project.        |

#### `<configuration>` section

| Element                    | Type    | Default           | Description                                        |
|----------------------------|---------|-------------------|----------------------------------------------------|
| `standalone`               | boolean | `false`           | Build a standalone application target.             |
| `vst3`                     | boolean | `true`            | Build a VST3 target.                               |
| `au`                       | boolean | `true`            | Build an Audio Unit (AU) target.                   |
| `auv3`                     | boolean | `false`           | Build an AUv3 target.                              |
| `clap`                     | boolean | `true`            | Build a CLAP target.                               |
| `au_component_type`        | string  | `aufx`            | Four-char AU component type code.                  |
| `au_component_subtype`     | string  | `plug`            | Four-char AU component subtype code.               |
| `au_component_manufacturer`| string  | `Ddsp`            | Four-char AU manufacturer code.                    |
| `au_version`               | string  | `1.0.0`           | AU bundle version string.                          |
| `clap_extensions`          | string  | `note-ports,state`| Comma-separated CLAP extension identifiers.        |
| `clap_features`            | string  | `audio-effect`    | Comma-separated CLAP feature identifiers.          |
| `auv3_platform`            | string  | `iOS`             | Target platform for AUv3 (`iOS` or `macOS`).      |
| `gui_width`                | integer | `800`             | Default plugin window width in pixels (> 0).       |
| `gui_height`               | integer | `600`             | Default plugin window height in pixels (> 0).      |
| `resizable`                | boolean | `false`           | Allow the plugin window to be resized.             |
| `background_image`         | string  | *(empty)*         | Path to an optional background image asset.        |
| `code_signing`             | boolean | `false`           | Enable macOS/iOS code signing.                     |
| `installer`                | boolean | `false`           | Generate an installer package.                     |
| `default_bypass`           | boolean | `false`           | Start with the plugin bypassed.                    |
| `input_gain`               | boolean | `false`           | Include an input gain stage.                       |
| `output_gain`              | boolean | `false`           | Include an output gain stage.                      |

#### `<implementations>` section

| Element                | Type    | Default | Description                                             |
|------------------------|---------|---------|---------------------------------------------------------|
| `moonbase_licensing`   | boolean | `false` | Integrate Moonbase licensing module.                    |
| `melatonin_inspector`  | boolean | `false` | Include Melatonin component inspector.                  |
| `custom_gui_framework` | boolean | `false` | Use a custom GUI framework instead of JUCE defaults.    |
| `logging_framework`    | boolean | `false` | Add structured logging support.                         |
| `clap_builds`          | boolean | `false` | Configure CLAP-specific build scripts.                  |
| `preset_management`    | boolean | `false` | Enable built-in preset management.                      |
| `preset_format`        | string  | *(empty)*| Preset serialisation format: `XML`, `Binary`, or empty. |
| `ab_comparison`        | boolean | `false` | Include A/B comparison functionality.                   |
| `state_management`     | boolean | `false` | Enable explicit plugin state management.                |
| `gpu_audio`            | boolean | `false` | Enable GPU Audio processing integration.                |

#### `<user_experience>` section

| Element            | Type    | Default | Description                                |
|--------------------|---------|---------|--------------------------------------------|
| `wizard`           | boolean | `false` | Show a setup wizard on first launch.       |
| `preview`          | boolean | `false` | Enable in-app audio preview functionality. |
| `preset_management`| boolean | `false` | Show preset management UI controls.        |

#### `<development_workflow>` section

| Element            | Type    | Default | Description                                     |
|--------------------|---------|---------|-------------------------------------------------|
| `vcs`              | boolean | `false` | Initialise a Git repository.                    |
| `testing`          | boolean | `false` | Add a unit-test scaffold.                       |
| `code_quality`     | boolean | `false` | Configure linting and formatting tools.         |
| `validation_tools` | boolean | `false` | Include static analysis and sanitiser builds.   |
| `scaffolding`      | boolean | `false` | Generate project scaffolding scripts.           |

*Required fields are enforced at the Python semantic-validation level (not by XSD structure
alone), because the XSD marks all elements as optional to allow partial presets to be loaded
with defaults filled in by `ConfigManager`.

### Validation Rules

- All five sections (`project_info`, `configuration`, `implementations`, `user_experience`,
  `development_workflow`) must be present.
- Required fields (project names, company identifiers, and `output_directory`) must not be
  empty strings.
- Types:
  - **Booleans**: `true`/`false` (case-insensitive; `1`/`0`/`yes`/`no`/`on`/`off` also
    accepted when loading).
  - **Integers**: whole positive numbers (GUI dimensions).
  - **Strings**: everything else.
- Two-layer validation is applied on every load and save:
  1. **XSD structural validation** via `PresetXSDValidator` (element names, nesting, types).
  2. **Semantic validation** via `ConfigManager.validate_config` (required fields, value
     constraints).

### Bundled Example Presets

Three presets ship with the application and are installed automatically into the user
preset folder (`~/.plugin_configurator/presets`) on startup:

1. **StandardAudioFX_Preset.xml** — balanced audio effect defaults with preset management.
2. **Instrument_Preset.xml** — instrument-focused template with CLAP/AUv3 targets.
3. **MinimalPlugin_Preset.xml** — lightweight VST3-only scaffold with no optional modules.

