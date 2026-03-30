## Preset XML Schema

Presets are stored as XML with a single `<preset>` root element. They map directly to the
tab structure used by the application (`project_info`, `configuration`, `implementations`,
`user_experience`, and `development_workflow`). Each section contains simple elements with
string, integer, or boolean values.

```xml
<?xml version="1.0" encoding="utf-8"?>
<preset name="PresetName">
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

### Validation Rules

- All five sections must be present.
- Required fields (project names, company identifiers, and `output_directory`) must not be
  empty.
- Types:
  - Booleans: `true`/`false` (case-insensitive)
  - Integers: whole numbers (GUI sizes)
  - Strings: everything else

### Bundled Example Presets

Three presets ship with the application and are installed automatically into the user
preset folder (`~/.plugin_configurator/presets`) on startup:

1. **StandardAudioFX_Preset.xml** — balanced audio effect defaults with preset management.
2. **Instrument_Preset.xml** — instrument-focused template with CLAP/AUv3 targets.
3. **MinimalPlugin_Preset.xml** — lightweight VST3-only scaffold with no optional modules.
