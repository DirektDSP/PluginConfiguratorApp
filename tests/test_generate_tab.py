"""Tests for the GenerateTab."""

import sys

import pytest
from PySide6.QtWidgets import QApplication, QGroupBox, QScrollArea

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

    def test_metadata_label_shows_project_name(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert "MyPlugin" in generate_tab._metadata_lbl.text()

    def test_metadata_label_shows_company(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert "Acme Corp" in generate_tab._metadata_lbl.text()

    def test_metadata_label_shows_output_directory(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert "/tmp/output" in generate_tab._metadata_lbl.text()

    def test_build_label_shows_vst3(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert "VST3" in generate_tab._build_lbl.text()

    def test_build_label_shows_au(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert "AU" in generate_tab._build_lbl.text()

    def test_build_label_shows_clap(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert "CLAP" in generate_tab._build_lbl.text()

    def test_build_label_does_not_show_standalone_when_disabled(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert "STANDALONE" not in generate_tab._build_lbl.text()

    def test_dsp_label_shows_default_bypass_enabled(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert "Enabled" in generate_tab._dsp_lbl.text()

    def test_ui_label_shows_gui_size(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        assert "800" in generate_tab._ui_lbl.text()
        assert "600" in generate_tab._ui_lbl.text()

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


# ------------------------------------------------------------------ #
# New feature tests                                                    #
# ------------------------------------------------------------------ #

MISSING_METADATA_CONFIG = {
    "project_info": {
        "project_name": "",
        "product_name": "My Plugin",
        "company_name": "",
        "bundle_id": "",
        "manufacturer_code": "Acme",
        "plugin_code": "",
        "version": "1.0.0",
        "output_directory": "",
    },
    "configuration": {
        "vst3": True,
    },
    "implementations": {},
    "user_experience": {},
}

NO_FORMAT_CONFIG = {
    "project_info": SAMPLE_CONFIG["project_info"],
    "configuration": {
        "standalone": False,
        "vst3": False,
        "au": False,
        "auv3": False,
        "clap": False,
    },
    "implementations": {},
    "user_experience": {},
}

TWO_INVALID_SECTIONS_CONFIG = {
    "project_info": {
        "project_name": "",
        "company_name": "",
        "bundle_id": "",
        "manufacturer_code": "",
        "output_directory": "",
    },
    "configuration": {
        "standalone": False,
        "vst3": False,
        "au": False,
        "auv3": False,
        "clap": False,
    },
    "implementations": {},
    "user_experience": {},
}


class TestGenerateTabSectionTooltips:
    """Section-specific error messages in status icon tooltips."""

    def test_valid_metadata_tooltip_says_valid(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        tooltip = generate_tab._status_icons["Metadata"].toolTip()
        assert "Valid" in tooltip

    def test_invalid_metadata_tooltip_mentions_missing_project_name(self, generate_tab):
        cfg = {
            "project_info": {
                "project_name": "",
                "company_name": "Acme",
                "bundle_id": "com.acme.plugin",
                "manufacturer_code": "Acme",
                "output_directory": "/tmp",
            },
            "configuration": {},
        }
        generate_tab.update_full_config(cfg)
        tooltip = generate_tab._status_icons["Metadata"].toolTip()
        assert "Project Name" in tooltip

    def test_invalid_metadata_tooltip_mentions_all_missing_fields(self, generate_tab):
        generate_tab.update_full_config(MISSING_METADATA_CONFIG)
        tooltip = generate_tab._status_icons["Metadata"].toolTip()
        assert "Project Name" in tooltip
        assert "Company Name" in tooltip
        assert "Bundle ID" in tooltip
        assert "Output Directory" in tooltip

    def test_invalid_metadata_tooltip_contains_missing_prefix(self, generate_tab):
        cfg = {
            "project_info": {
                "project_name": "",
                "company_name": "Acme",
                "bundle_id": "com.acme.plugin",
                "manufacturer_code": "Acme",
                "output_directory": "/tmp",
            },
            "configuration": {},
        }
        generate_tab.update_full_config(cfg)
        tooltip = generate_tab._status_icons["Metadata"].toolTip()
        assert "Missing" in tooltip

    def test_invalid_build_tooltip_mentions_no_format(self, generate_tab):
        generate_tab.update_full_config(NO_FORMAT_CONFIG)
        tooltip = generate_tab._status_icons["Build"].toolTip()
        assert "No plugin format selected" in tooltip

    def test_valid_build_tooltip_says_valid(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        tooltip = generate_tab._status_icons["Build"].toolTip()
        assert "Valid" in tooltip

    def test_dsp_tooltip_says_valid(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        tooltip = generate_tab._status_icons["DSP"].toolTip()
        assert "Valid" in tooltip

    def test_ui_tooltip_says_valid(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        tooltip = generate_tab._status_icons["UI"].toolTip()
        assert "Valid" in tooltip

    def test_modules_tooltip_says_valid(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        tooltip = generate_tab._status_icons["Modules"].toolTip()
        assert "Valid" in tooltip


class TestGenerateTabSectionHighlighting:
    """Visual border highlighting of section group boxes."""

    def test_section_groups_dict_has_all_five_sections(self, generate_tab):
        assert set(generate_tab._section_groups.keys()) == {
            "Metadata",
            "Build",
            "DSP",
            "UI",
            "Modules",
        }

    def test_valid_metadata_group_has_green_border(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        style = generate_tab._section_groups["Metadata"].styleSheet()
        assert "#2e7d32" in style

    def test_invalid_metadata_group_has_red_border(self, generate_tab):
        generate_tab.update_full_config(MISSING_METADATA_CONFIG)
        style = generate_tab._section_groups["Metadata"].styleSheet()
        assert "#c62828" in style

    def test_invalid_build_group_has_red_border(self, generate_tab):
        generate_tab.update_full_config(NO_FORMAT_CONFIG)
        style = generate_tab._section_groups["Build"].styleSheet()
        assert "#c62828" in style

    def test_valid_build_group_has_green_border(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        style = generate_tab._section_groups["Build"].styleSheet()
        assert "#2e7d32" in style

    def test_dsp_group_has_green_border_when_config_loaded(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        style = generate_tab._section_groups["DSP"].styleSheet()
        assert "#2e7d32" in style

    def test_ui_group_has_green_border_when_config_loaded(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        style = generate_tab._section_groups["UI"].styleSheet()
        assert "#2e7d32" in style

    def test_modules_group_has_green_border_when_config_loaded(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        style = generate_tab._section_groups["Modules"].styleSheet()
        assert "#2e7d32" in style

    def test_reset_clears_section_group_styles(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        generate_tab.reset()
        for group in generate_tab._section_groups.values():
            assert group.styleSheet() == ""


class TestGenerateTabOverallStatus:
    """Overall status label in the Configuration Status group."""

    def test_overall_status_label_exists(self, generate_tab):
        assert hasattr(generate_tab, "_overall_status_lbl")

    def test_overall_status_empty_initially(self, app):
        new_tab = GenerateTab()
        assert new_tab._overall_status_lbl.text() == ""
        new_tab.deleteLater()

    def test_overall_status_shows_all_valid_when_full_config_valid(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        text = generate_tab._overall_status_lbl.text()
        assert "All sections valid" in text

    def test_overall_status_shows_checkmark_when_all_valid(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        text = generate_tab._overall_status_lbl.text()
        assert "✅" in text

    def test_overall_status_shows_count_when_sections_invalid(self, generate_tab):
        generate_tab.update_full_config(MISSING_METADATA_CONFIG)
        text = generate_tab._overall_status_lbl.text()
        assert "need attention" in text

    def test_overall_status_shows_cross_mark_when_invalid(self, generate_tab):
        generate_tab.update_full_config(MISSING_METADATA_CONFIG)
        text = generate_tab._overall_status_lbl.text()
        assert "❌" in text

    def test_overall_status_counts_one_invalid_section(self, generate_tab):
        generate_tab.update_full_config(MISSING_METADATA_CONFIG)
        text = generate_tab._overall_status_lbl.text()
        assert "1 section" in text

    def test_overall_status_counts_two_invalid_sections(self, generate_tab):
        generate_tab.update_full_config(TWO_INVALID_SECTIONS_CONFIG)
        text = generate_tab._overall_status_lbl.text()
        assert "2 sections" in text

    def test_overall_status_uses_plural_for_multiple_sections(self, generate_tab):
        generate_tab.update_full_config(TWO_INVALID_SECTIONS_CONFIG)
        text = generate_tab._overall_status_lbl.text()
        assert "sections" in text

    def test_reset_clears_overall_status_label(self, generate_tab):
        generate_tab.update_full_config(SAMPLE_CONFIG)
        generate_tab.reset()
        assert generate_tab._overall_status_lbl.text() == ""


class TestGenerateTabScrollReference:
    """Scroll area reference is set and section groups are stored."""

    def test_scroll_area_reference_exists(self, generate_tab):
        assert hasattr(generate_tab, "_scroll")

    def test_scroll_area_is_qscrollarea(self, generate_tab):
        assert isinstance(generate_tab._scroll, QScrollArea)

    def test_section_groups_are_qgroupbox_instances(self, generate_tab):
        for group in generate_tab._section_groups.values():
            assert isinstance(group, QGroupBox)
