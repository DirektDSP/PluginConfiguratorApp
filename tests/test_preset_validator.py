"""Tests for the XSD-based preset validator (PresetXSDValidator)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from core.config_manager import ConfigManager
from core.preset_validator import PresetXSDValidator

if TYPE_CHECKING:
    from pathlib import Path

# ---------------------------------------------------------------------------
# Minimal valid preset XML
# ---------------------------------------------------------------------------

VALID_PRESET_XML = """\
<?xml version="1.0" encoding="utf-8"?>
<preset name="TestPreset" schema_version="1.0">
  <meta>
    <description>A valid test preset.</description>
  </meta>
  <project_info>
    <project_name>TestPlugin</project_name>
    <product_name>Test Plugin</product_name>
    <version>1.0.0</version>
    <company_name>TestCo</company_name>
    <bundle_id>com.test.plugin</bundle_id>
    <manufacturer_code>TEST</manufacturer_code>
    <plugin_code>TPLU</plugin_code>
    <output_directory>/tmp/TestPlugin</output_directory>
  </project_info>
  <configuration>
    <standalone>false</standalone>
    <vst3>true</vst3>
    <au>false</au>
    <auv3>false</auv3>
    <clap>false</clap>
    <gui_width>800</gui_width>
    <gui_height>600</gui_height>
    <resizable>false</resizable>
    <background_image></background_image>
    <code_signing>false</code_signing>
    <installer>false</installer>
    <default_bypass>false</default_bypass>
    <input_gain>false</input_gain>
    <output_gain>false</output_gain>
  </configuration>
  <implementations>
    <moonbase_licensing>false</moonbase_licensing>
    <melatonin_inspector>false</melatonin_inspector>
    <custom_gui_framework>false</custom_gui_framework>
    <logging_framework>false</logging_framework>
    <clap_builds>false</clap_builds>
    <preset_management>false</preset_management>
    <preset_format></preset_format>
    <ab_comparison>false</ab_comparison>
    <state_management>false</state_management>
    <gpu_audio>false</gpu_audio>
  </implementations>
  <user_experience>
    <wizard>false</wizard>
    <preview>false</preview>
    <preset_management>false</preset_management>
  </user_experience>
  <development_workflow>
    <vcs>false</vcs>
    <testing>false</testing>
    <code_quality>false</code_quality>
    <validation_tools>false</validation_tools>
    <scaffolding>false</scaffolding>
  </development_workflow>
</preset>
"""

# Preset that omits all optional elements inside sections (still valid: all
# section-level elements are marked minOccurs="0" in the XSD).
MINIMAL_SECTION_CONTENT_XML = """\
<?xml version="1.0" encoding="utf-8"?>
<preset name="BareMinimum" schema_version="1.0">
  <project_info/>
  <configuration/>
  <implementations/>
  <user_experience/>
  <development_workflow/>
</preset>
"""

# Preset using aliased boolean values accepted by ConfigManager
BOOLEAN_ALIAS_XML = """\
<?xml version="1.0" encoding="utf-8"?>
<preset name="BoolAlias" schema_version="1.0">
  <project_info/>
  <configuration>
    <standalone>yes</standalone>
    <vst3>on</vst3>
    <au>no</au>
    <auv3>off</auv3>
  </configuration>
  <implementations/>
  <user_experience/>
  <development_workflow/>
</preset>
"""


class TestPresetXSDValidatorClass:
    """Tests for static / class-level attributes of PresetXSDValidator."""

    def test_schema_version_constant(self):
        assert PresetXSDValidator.SCHEMA_VERSION == "1.0"

    def test_xsd_path_exists(self):
        assert PresetXSDValidator.XSD_PATH.exists(), (
            f"XSD file not found at {PresetXSDValidator.XSD_PATH}"
        )

    def test_xsd_path_is_xsd(self):
        assert PresetXSDValidator.XSD_PATH.suffix == ".xsd"


class TestPresetXSDValidatorValidString:
    """Tests for validate_string()."""

    @pytest.fixture
    def validator(self) -> PresetXSDValidator:
        return PresetXSDValidator()

    def test_valid_full_preset(self, validator: PresetXSDValidator):
        ok, errors = validator.validate_string(VALID_PRESET_XML)
        assert ok, f"Expected valid, got errors: {errors}"
        assert errors == []

    def test_valid_minimal_section_content(self, validator: PresetXSDValidator):
        ok, errors = validator.validate_string(MINIMAL_SECTION_CONTENT_XML)
        assert ok, f"Expected valid, got errors: {errors}"

    def test_valid_boolean_aliases(self, validator: PresetXSDValidator):
        """BooleanField union type must accept yes/no/on/off aliases."""
        ok, errors = validator.validate_string(BOOLEAN_ALIAS_XML)
        assert ok, f"Expected valid, got errors: {errors}"

    def test_invalid_xml_syntax(self, validator: PresetXSDValidator):
        ok, errors = validator.validate_string("<preset><unclosed>")
        assert not ok
        assert errors

    def test_missing_required_section_fails(self, validator: PresetXSDValidator):
        """A preset missing one of the five required sections must fail validation."""
        xml = """\
<?xml version="1.0" encoding="utf-8"?>
<preset name="MissingSection" schema_version="1.0">
  <project_info/>
  <configuration/>
  <implementations/>
  <user_experience/>
</preset>
"""
        ok, errors = validator.validate_string(xml)
        assert not ok
        assert errors

    def test_wrong_root_element_fails(self, validator: PresetXSDValidator):
        xml = """\
<?xml version="1.0" encoding="utf-8"?>
<config>
  <project_info/>
  <configuration/>
  <implementations/>
  <user_experience/>
  <development_workflow/>
</config>
"""
        ok, errors = validator.validate_string(xml)
        assert not ok
        assert errors

    def test_invalid_boolean_value_fails(self, validator: PresetXSDValidator):
        """A boolean field containing a non-boolean string must fail."""
        xml = """\
<?xml version="1.0" encoding="utf-8"?>
<preset name="BadBool" schema_version="1.0">
  <project_info/>
  <configuration>
    <vst3>maybe</vst3>
  </configuration>
  <implementations/>
  <user_experience/>
  <development_workflow/>
</preset>
"""
        ok, errors = validator.validate_string(xml)
        assert not ok
        assert errors

    def test_non_positive_integer_gui_width_fails(self, validator: PresetXSDValidator):
        """gui_width must be a positive integer when present."""
        xml = """\
<?xml version="1.0" encoding="utf-8"?>
<preset name="BadWidth" schema_version="1.0">
  <project_info/>
  <configuration>
    <gui_width>-800</gui_width>
  </configuration>
  <implementations/>
  <user_experience/>
  <development_workflow/>
</preset>
"""
        ok, errors = validator.validate_string(xml)
        assert not ok
        assert errors

    def test_zero_gui_height_fails(self, validator: PresetXSDValidator):
        """gui_height=0 is not a positive integer and must fail."""
        xml = """\
<?xml version="1.0" encoding="utf-8"?>
<preset name="ZeroHeight" schema_version="1.0">
  <project_info/>
  <configuration>
    <gui_height>0</gui_height>
  </configuration>
  <implementations/>
  <user_experience/>
  <development_workflow/>
</preset>
"""
        ok, errors = validator.validate_string(xml)
        assert not ok
        assert errors

    def test_unknown_element_in_section_fails(self, validator: PresetXSDValidator):
        """An unrecognised child element inside a section must fail validation."""
        xml = """\
<?xml version="1.0" encoding="utf-8"?>
<preset name="UnknownElem" schema_version="1.0">
  <project_info>
    <nonexistent_field>value</nonexistent_field>
  </project_info>
  <configuration/>
  <implementations/>
  <user_experience/>
  <development_workflow/>
</preset>
"""
        ok, errors = validator.validate_string(xml)
        assert not ok
        assert errors

    def test_preset_without_schema_version_attribute_is_valid(self, validator: PresetXSDValidator):
        """schema_version is optional; omitting it must still pass XSD validation."""
        xml = """\
<?xml version="1.0" encoding="utf-8"?>
<preset name="NoVersion">
  <project_info/>
  <configuration/>
  <implementations/>
  <user_experience/>
  <development_workflow/>
</preset>
"""
        ok, errors = validator.validate_string(xml)
        assert ok, f"Expected valid without schema_version, got errors: {errors}"

    def test_preset_without_name_attribute_is_valid(self, validator: PresetXSDValidator):
        """name is optional; omitting it must still pass XSD validation."""
        xml = """\
<?xml version="1.0" encoding="utf-8"?>
<preset schema_version="1.0">
  <project_info/>
  <configuration/>
  <implementations/>
  <user_experience/>
  <development_workflow/>
</preset>
"""
        ok, errors = validator.validate_string(xml)
        assert ok, f"Expected valid without name, got errors: {errors}"


class TestPresetXSDValidatorValidFile:
    """Tests for validate_file()."""

    @pytest.fixture
    def validator(self) -> PresetXSDValidator:
        return PresetXSDValidator()

    @pytest.fixture
    def valid_preset_file(self, tmp_path: Path) -> Path:
        f = tmp_path / "valid.xml"
        f.write_text(VALID_PRESET_XML, encoding="utf-8")
        return f

    @pytest.fixture
    def invalid_preset_file(self, tmp_path: Path) -> Path:
        f = tmp_path / "invalid.xml"
        f.write_text("<not-a-preset/>", encoding="utf-8")
        return f

    def test_valid_file_passes(self, validator: PresetXSDValidator, valid_preset_file: Path):
        ok, errors = validator.validate_file(valid_preset_file)
        assert ok, errors

    def test_invalid_file_fails(self, validator: PresetXSDValidator, invalid_preset_file: Path):
        ok, errors = validator.validate_file(invalid_preset_file)
        assert not ok
        assert errors

    def test_nonexistent_file_fails(self, validator: PresetXSDValidator, tmp_path: Path):
        ok, errors = validator.validate_file(tmp_path / "ghost.xml")
        assert not ok
        assert errors

    def test_malformed_xml_file_fails(self, validator: PresetXSDValidator, tmp_path: Path):
        bad = tmp_path / "bad.xml"
        bad.write_text("<unclosed>", encoding="utf-8")
        ok, errors = validator.validate_file(bad)
        assert not ok
        assert errors

    def test_bundled_presets_pass_xsd(self, validator: PresetXSDValidator, tmp_path: Path):
        """All shipped preset files must satisfy the XSD schema."""
        mgr = ConfigManager(preset_dir=tmp_path / "presets")
        for preset_stem in ConfigManager.BUNDLED_PRESETS:
            preset_path = mgr.preset_dir / f"{preset_stem}.xml"
            ok, errors = validator.validate_file(preset_path)
            assert ok, f"{preset_stem} failed XSD validation: {errors}"


class TestPresetXSDValidatorSchemaCache:
    """The compiled schema must be cached across instances."""

    def test_schema_is_cached(self):
        v1 = PresetXSDValidator()
        _ = v1.validate_string(VALID_PRESET_XML)
        schema_after_first = PresetXSDValidator._schema

        v2 = PresetXSDValidator()
        _ = v2.validate_string(VALID_PRESET_XML)
        schema_after_second = PresetXSDValidator._schema

        assert schema_after_first is schema_after_second
