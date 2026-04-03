"""Tests for the GenerateTab."""

import sys

import pytest
from PySide6.QtWidgets import QApplication

from ui.tabs.generate_tab import GenerateTab


@pytest.fixture(scope="module")
def app():
    """Create a single QApplication instance for all tests in this module."""
    instance = QApplication.instance()
    if not instance:
        instance = QApplication(sys.argv)
    yield instance


@pytest.fixture
def generate_tab(app):
    """Create a fresh GenerateTab for each test."""
    tab = GenerateTab()
    yield tab
    tab.deleteLater()


class TestGenerateTabInit:
    def test_tab_is_not_none(self, generate_tab):
        assert generate_tab is not None

    def test_tab_is_instance_of_generate_tab(self, generate_tab):
        assert isinstance(generate_tab, GenerateTab)

    def test_initial_full_config_is_empty(self, generate_tab):
        assert generate_tab._full_config == {}

    def test_had_error_flag_starts_false(self, generate_tab):
        assert generate_tab._had_error is False

    def test_generate_button_is_enabled_initially(self, generate_tab):
        assert generate_tab._generate_button.isEnabled()

    def test_progress_bar_starts_at_zero(self, generate_tab):
        assert generate_tab._progress_bar.value() == 0

    def test_status_label_initial_text(self, generate_tab):
        assert "Ready" in generate_tab._status_label.text()


class TestGenerateTabValidation:
    def test_validate_always_returns_true(self, generate_tab):
        assert generate_tab.validate() is True

    def test_validate_returns_true_even_with_empty_config(self, generate_tab):
        generate_tab._full_config = {}
        assert generate_tab.validate() is True

    def test_get_configuration_returns_dict(self, generate_tab):
        cfg = generate_tab.get_configuration()
        assert isinstance(cfg, dict)

    def test_get_configuration_has_full_config_key(self, generate_tab):
        cfg = generate_tab.get_configuration()
        assert "full_config" in cfg

    def test_get_configuration_has_tab_complete_key(self, generate_tab):
        cfg = generate_tab.get_configuration()
        assert "tab_complete" in cfg

    def test_tab_complete_false_when_empty(self, generate_tab):
        generate_tab._full_config = {}
        cfg = generate_tab.get_configuration()
        assert cfg["tab_complete"] is False

    def test_tab_complete_true_when_config_set(self, generate_tab):
        generate_tab._full_config = {"project_info": {"project_name": "Test"}}
        cfg = generate_tab.get_configuration()
        assert cfg["tab_complete"] is True


SAMPLE_CONFIG = {
    "project_info": {
        "project_name": "MyPlugin",
        "product_name": "My Plugin",
        "company_name": "Acme Corp",
        "bundle_id": "com.acme.myplugin",
        "manufacturer_code": "Acme",
        "plugin_code": "MPlg",
        "version": "1.0.0",
        "output_directory": "/tmp/output",
        "template_url": "https://github.com/example/template.git",
    },
    "configuration": {
        "standalone": False,
        "vst3": True,
        "au": True,
        "auv3": False,
        "clap": True,
        "gui_width": 800,
        "gui_height": 600,
        "resizable": False,
        "code_signing": False,
        "installer": False,
        "default_bypass": True,
        "input_gain": False,
        "output_gain": True,
    },
    "implementations": {
        "moonbase_licensing": True,
        "melatonin_inspector": False,
        "custom_gui_framework": False,
        "logging_framework": False,
        "clap_builds": False,
        "preset_management": True,
        "preset_format": "VST3",
        "ab_comparison": False,
        "state_management": False,
        "gpu_audio": False,
    },
    "user_experience": {
        "wizard": True,
        "preview": False,
        "preset_management": False,
    },
    "development_workflow": {
        "vcs": True,
    },
}


class TestGenerateTabSummary:
    def test_update_full_config_stores_config(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert generate_tab._full_config == SAMPLE_CONFIG

    def test_metadata_field_shows_project_name(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert generate_tab._meta_fields["project_name"].text() == "MyPlugin"

    def test_metadata_field_shows_company(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert generate_tab._meta_fields["company_name"].text() == "Acme Corp"

    def test_metadata_field_shows_output_directory(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert generate_tab._meta_fields["output_directory"].text() == "/tmp/output"

    def test_metadata_field_shows_product_name(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert generate_tab._meta_fields["product_name"].text() == "My Plugin"

    def test_metadata_field_shows_bundle_id(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert generate_tab._meta_fields["bundle_id"].text() == "com.acme.myplugin"

    def test_metadata_field_shows_version(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert generate_tab._meta_fields["version"].text() == "1.0.0"

    def test_build_field_shows_vst3(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert "VST3" in generate_tab._build_fields["formats"].text()

    def test_build_field_shows_au(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert "AU" in generate_tab._build_fields["formats"].text()

    def test_build_field_shows_clap(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert "CLAP" in generate_tab._build_fields["formats"].text()

    def test_build_field_does_not_show_standalone_when_disabled(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert "STANDALONE" not in generate_tab._build_fields["formats"].text()

    def test_build_field_code_signing_disabled(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert generate_tab._build_fields["code_signing"].text() == "Disabled"

    def test_dsp_field_shows_default_bypass_enabled(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert generate_tab._dsp_fields["default_bypass"].text() == "Enabled"

    def test_dsp_field_shows_input_gain_disabled(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert generate_tab._dsp_fields["input_gain"].text() == "Disabled"

    def test_ui_field_shows_gui_size(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert "800" in generate_tab._ui_fields["gui_size"].text()
        assert "600" in generate_tab._ui_fields["gui_size"].text()

    def test_ui_field_shows_resizable_no(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert generate_tab._ui_fields["resizable"].text() == "No"

    def test_ui_field_shows_wizard_enabled(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert generate_tab._ui_fields["wizard"].text() == "Enabled"

    def test_modules_label_shows_moonbase(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert "Moonbase" in generate_tab._modules_lbl.text()

    def test_modules_label_shows_preset_management_with_format(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert "Preset Management" in generate_tab._modules_lbl.text()
        assert "VST3" in generate_tab._modules_lbl.text()

    def test_modules_label_no_modules_when_all_disabled(self, generate_tab):
        cfg = dict(SAMPLE_CONFIG)
        cfg["implementations"] = {}
        generate_tab.update_full_config(cfg)
        assert "No optional modules selected" in generate_tab._modules_lbl.text()

    def test_metadata_field_shows_dash_for_empty_value(self, generate_tab):
        generate_tab.update_full_config({"project_info": {"project_name": ""}})
        assert generate_tab._meta_fields["project_name"].text() == "—"

    def test_build_field_shows_none_selected_when_no_formats(self, generate_tab):
        generate_tab.update_full_config({"configuration": {}})
        assert generate_tab._build_fields["formats"].text() == "None selected"


class TestGenerateTabStatusIcons:
    def test_metadata_icon_valid_when_all_required_fields_filled(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert generate_tab._status_icons["Metadata"].text() == "\u2705"

    def test_metadata_icon_invalid_when_project_name_missing(self, generate_tab):
        cfg = {
            "project_info": {
                "project_name": "",
                "company_name": "Acme",
                "bundle_id": "com.acme",
                "manufacturer_code": "Acme",
                "output_directory": "/tmp",
            },
            "configuration": {},
        }
        generate_tab.update_full_config(cfg)
        assert generate_tab._status_icons["Metadata"].text() == "\u274c"

    def test_build_icon_valid_when_at_least_one_format_selected(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert generate_tab._status_icons["Build"].text() == "\u2705"

    def test_build_icon_invalid_when_no_format_selected(self, generate_tab):
        cfg = {
            "project_info": SAMPLE_CONFIG["project_info"],
            "configuration": {
                "standalone": False,
                "vst3": False,
                "au": False,
                "auv3": False,
                "clap": False,
            },
        }
        generate_tab.update_full_config(cfg)
        assert generate_tab._status_icons["Build"].text() == "\u274c"

    def test_dsp_icon_always_valid(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert generate_tab._status_icons["DSP"].text() == "\u2705"

    def test_ui_icon_always_valid(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert generate_tab._status_icons["UI"].text() == "\u2705"

    def test_modules_icon_always_valid(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert generate_tab._status_icons["Modules"].text() == "\u2705"

    def test_initial_icons_are_neutral(self, app):
        new_tab = GenerateTab()
        for icon in new_tab._status_icons.values():
            assert icon.text() == "\u26aa"
        new_tab.deleteLater()


class TestGenerateTabLoadAndReset:
    def test_load_configuration_restores_full_config(self, generate_tab):
        saved = generate_tab.get_configuration()
        saved["full_config"] = SAMPLE_CONFIG
        generate_tab.load_configuration(saved)
        assert generate_tab._full_config == SAMPLE_CONFIG

    def test_load_configuration_empty_dict_clears_full_config(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        generate_tab.load_configuration({})
        assert generate_tab._full_config == {}

    def test_reset_clears_full_config(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        generate_tab.reset()
        assert generate_tab._full_config == {}

    def test_reset_clears_progress_bar(self, generate_tab):
        generate_tab._progress_bar.setValue(75)
        generate_tab.reset()
        assert generate_tab._progress_bar.value() == 0

    def test_reset_re_enables_generate_button(self, generate_tab):
        generate_tab._generate_button.setEnabled(False)
        generate_tab.reset()
        assert generate_tab._generate_button.isEnabled()

    def test_reset_returns_neutral_icons(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        generate_tab.reset()
        for icon in generate_tab._status_icons.values():
            assert icon.text() == "\u26aa"

    def test_reset_clears_log_text(self, generate_tab):
        generate_tab._log_text.append("some log entry")
        generate_tab.reset()
        assert generate_tab._log_text.toPlainText() == ""

    def test_reset_clears_meta_fields_to_dash(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        generate_tab.reset()
        for lbl in generate_tab._meta_fields.values():
            assert lbl.text() == "—"

    def test_reset_clears_build_fields_to_dash(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        generate_tab.reset()
        for lbl in generate_tab._build_fields.values():
            assert lbl.text() == "—"

    def test_reset_clears_dsp_fields_to_dash(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        generate_tab.reset()
        for lbl in generate_tab._dsp_fields.values():
            assert lbl.text() == "—"

    def test_reset_clears_ui_fields_to_dash(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        generate_tab.reset()
        for lbl in generate_tab._ui_fields.values():
            assert lbl.text() == "—"

    def test_reset_resets_modules_label(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        generate_tab.reset()
        assert generate_tab._modules_lbl.text() == "No optional modules selected"


class TestGenerateTabModulesAccordion:
    def test_modules_accordion_exists(self, generate_tab):
        assert generate_tab._modules_accordion is not None

    def test_modules_accordion_starts_expanded(self, generate_tab):
        assert generate_tab._modules_accordion.is_expanded is True

    def test_modules_accordion_can_be_collapsed(self, generate_tab):
        generate_tab._modules_accordion.set_expanded(False)
        assert generate_tab._modules_accordion.is_expanded is False

    def test_modules_accordion_can_be_re_expanded(self, generate_tab):
        generate_tab._modules_accordion.set_expanded(False)
        generate_tab._modules_accordion.set_expanded(True)
        assert generate_tab._modules_accordion.is_expanded is True

    def test_modules_lbl_is_inside_accordion(self, generate_tab):
        # The modules label should be a child of the accordion's content widget
        assert generate_tab._modules_lbl.parent() is not None

class TestGenerateTabButton:
    def test_generate_button_has_tooltip(self, generate_tab):
        tooltip = generate_tab._generate_button.toolTip()
        assert len(tooltip) > 0

    def test_generate_button_tooltip_mentions_configuration(self, generate_tab):
        tooltip = generate_tab._generate_button.toolTip()
        assert "configuration" in tooltip.lower() or "generate" in tooltip.lower()


class TestGenerateTabGlobalValidation:
    def test_set_global_validation_disables_button_when_invalid(self, generate_tab):
        generate_tab.set_global_validation(False, ["Project Info: Project Name is required"])
        assert not generate_tab._generate_button.isEnabled()

    def test_set_global_validation_enables_button_when_valid(self, generate_tab):
        generate_tab.set_global_validation(False, ["some issue"])
        generate_tab.set_global_validation(True, [])
        assert generate_tab._generate_button.isEnabled()

    def test_set_global_validation_tooltip_lists_issues_when_invalid(self, generate_tab):
        issues = ["Project Info: Project Name is required", "Configuration: Select a format"]
        generate_tab.set_global_validation(False, issues)
        tooltip = generate_tab._generate_button.toolTip()
        assert "Project Name" in tooltip
        assert "Select a format" in tooltip

    def test_set_global_validation_tooltip_contains_bullet_points(self, generate_tab):
        generate_tab.set_global_validation(False, ["Issue one", "Issue two"])
        tooltip = generate_tab._generate_button.toolTip()
        assert "•" in tooltip

    def test_set_global_validation_tooltip_restored_when_valid(self, generate_tab):
        generate_tab.set_global_validation(False, ["some issue"])
        generate_tab.set_global_validation(True, [])
        tooltip = generate_tab._generate_button.toolTip()
        assert "Generate" in tooltip or "generate" in tooltip.lower()

    def test_set_global_validation_empty_issues_enables_button(self, generate_tab):
        generate_tab.set_global_validation(True, [])
        assert generate_tab._generate_button.isEnabled()
