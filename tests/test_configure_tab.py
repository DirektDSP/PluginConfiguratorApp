"""Tests for ConfigureTab – Tab 2 of the 4-lifecycle UI."""

import sys
from unittest.mock import Mock

import pytest
from PySide6.QtWidgets import QApplication

from ui.tabs.configure_tab import ConfigureTab


@pytest.fixture(scope="module")
def app():
    """Create a QApplication for the entire module."""
    if not QApplication.instance():
        _app = QApplication(sys.argv)
    else:
        _app = QApplication.instance()
    yield _app
    _app.quit()


@pytest.fixture
def tab(app):
    """Return a fresh ConfigureTab for each test."""
    return ConfigureTab()


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------


class TestConfigureTabInit:
    def test_tab_creates_without_error(self, tab):
        assert tab is not None

    def test_tab_is_base_tab_subclass(self, tab):
        from core.base_tab import BaseTab

        assert isinstance(tab, BaseTab)

    def test_default_company_name(self, tab):
        assert tab.company_name.text() == "DirektDSP"

    def test_default_manufacturer_code(self, tab):
        assert tab.manufacturer_code.text() == "Ddsp"

    def test_default_vst3_checked(self, tab):
        assert tab.vst3.isChecked() is True

    def test_default_au_checked(self, tab):
        assert tab.au.isChecked() is True

    def test_default_clap_checked(self, tab):
        assert tab.clap.isChecked() is True

    def test_default_standalone_unchecked(self, tab):
        assert tab.standalone.isChecked() is False

    def test_default_auv3_unchecked(self, tab):
        assert tab.auv3.isChecked() is False

    def test_default_github_actions_unchecked(self, tab):
        assert tab.github_actions.isChecked() is False

    def test_default_enable_signing_unchecked(self, tab):
        assert tab.enable_signing.isChecked() is False

    def test_cicd_sub_widget_hidden_by_default(self, tab):
        assert tab.cicd_sub_widget.isHidden() is True

    def test_signing_sub_widget_hidden_by_default(self, tab):
        assert tab.signing_sub_widget.isHidden() is True


# ---------------------------------------------------------------------------
# Format checkboxes
# ---------------------------------------------------------------------------


class TestFormatCheckboxes:
    def test_all_five_formats_present(self, tab):
        """All five format checkboxes must exist."""
        for name in ("standalone", "vst3", "au", "auv3", "clap"):
            assert hasattr(tab, name), f"Missing format checkbox: {name}"

    def test_format_tooltips_set(self, tab):
        """Each format checkbox should have a non-empty tooltip."""
        for cb in [tab.standalone, tab.vst3, tab.au, tab.auv3, tab.clap]:
            assert cb.toolTip(), f"{cb.text()} checkbox has no tooltip"


# ---------------------------------------------------------------------------
# Output directory
# ---------------------------------------------------------------------------


class TestOutputDirectory:
    def test_output_directory_widget_exists(self, tab):
        assert hasattr(tab, "output_directory")

    def test_browse_output_button_exists(self, tab):
        assert hasattr(tab, "browse_output_button")

    def test_output_directory_in_configuration(self, tab):
        tab.output_directory.setText("/tmp/mybuild")
        config = tab.get_configuration()
        assert config["output_directory"] == "/tmp/mybuild"

    def test_output_directory_round_trip(self, tab):
        tab.load_configuration({"output_directory": "/some/path"})
        assert tab.output_directory.text() == "/some/path"


# ---------------------------------------------------------------------------
# CI/CD options
# ---------------------------------------------------------------------------


class TestCICDOptions:
    def test_github_actions_checkbox_exists(self, tab):
        assert hasattr(tab, "github_actions")

    def test_cicd_sub_options_exist(self, tab):
        assert hasattr(tab, "cicd_build_matrix")
        assert hasattr(tab, "cicd_run_tests")

    def test_enabling_github_actions_shows_sub_options(self, tab):
        tab.github_actions.setChecked(True)
        # isHidden() checks the widget's own visibility flag regardless of whether
        # the parent window has been shown (which it hasn't in headless tests).
        assert tab.cicd_sub_widget.isHidden() is False

    def test_disabling_github_actions_hides_sub_options(self, tab):
        tab.github_actions.setChecked(True)
        tab.github_actions.setChecked(False)
        assert tab.cicd_sub_widget.isHidden() is True

    def test_cicd_settings_in_configuration(self, tab):
        tab.github_actions.setChecked(True)
        tab.cicd_build_matrix.setChecked(False)
        tab.cicd_run_tests.setChecked(True)
        config = tab.get_configuration()
        assert config["github_actions"] is True
        assert config["cicd_build_matrix"] is False
        assert config["cicd_run_tests"] is True

    def test_cicd_round_trip(self, tab):
        tab.load_configuration(
            {
                "github_actions": True,
                "cicd_build_matrix": False,
                "cicd_run_tests": False,
            }
        )
        assert tab.github_actions.isChecked() is True
        assert tab.cicd_build_matrix.isChecked() is False
        assert tab.cicd_run_tests.isChecked() is False


# ---------------------------------------------------------------------------
# Code signing options
# ---------------------------------------------------------------------------


class TestCodeSigningOptions:
    def test_enable_signing_checkbox_exists(self, tab):
        assert hasattr(tab, "enable_signing")

    def test_signing_sub_fields_exist(self, tab):
        assert hasattr(tab, "signing_team_id")
        assert hasattr(tab, "signing_certificate")

    def test_enabling_signing_shows_sub_options(self, tab):
        tab.enable_signing.setChecked(True)
        # isHidden() checks the widget's own flag regardless of parent show state.
        assert tab.signing_sub_widget.isHidden() is False

    def test_disabling_signing_hides_sub_options(self, tab):
        tab.enable_signing.setChecked(True)
        tab.enable_signing.setChecked(False)
        assert tab.signing_sub_widget.isHidden() is True

    def test_signing_settings_in_configuration(self, tab):
        tab.enable_signing.setChecked(True)
        tab.signing_team_id.setText("ABCDE12345")
        tab.signing_certificate.setText("Developer ID Application: Test")
        config = tab.get_configuration()
        assert config["enable_signing"] is True
        assert config["signing_team_id"] == "ABCDE12345"
        assert config["signing_certificate"] == "Developer ID Application: Test"

    def test_signing_round_trip(self, tab):
        tab.load_configuration(
            {
                "enable_signing": True,
                "signing_team_id": "XYZ999",
                "signing_certificate": "My Cert",
            }
        )
        assert tab.enable_signing.isChecked() is True
        assert tab.signing_team_id.text() == "XYZ999"
        assert tab.signing_certificate.text() == "My Cert"


# ---------------------------------------------------------------------------
# Format-specific option disclosure
# ---------------------------------------------------------------------------


class TestFormatSpecificOptions:
    def test_format_option_groups_match_defaults(self, tab):
        # AU and CLAP are checked by default, AUv3 is not.
        assert tab.au_options_group.isHidden() is False
        assert tab.clap_options_group.isHidden() is False
        assert tab.auv3_options_group.isHidden() is True

    def test_enabling_format_reveals_option_group(self, tab):
        tab.au.setChecked(True)
        tab.clap.setChecked(True)
        tab.auv3.setChecked(True)
        assert tab.au_options_group.isHidden() is False
        assert tab.clap_options_group.isHidden() is False
        assert tab.auv3_options_group.isHidden() is False

    def test_format_specific_fields_in_configuration(self, tab):
        tab.au.setChecked(True)
        tab.clap.setChecked(True)
        tab.auv3.setChecked(True)
        tab.au_component_type.setText("aufx")
        tab.au_component_subtype.setText("abcd")
        tab.au_component_manufacturer.setText("Ddsp")
        tab.au_version.setText("1.2.3")
        tab.clap_extensions.setText("note-ports")
        tab.clap_features.setText("instrument,audio-effect")
        tab.auv3_platform.setCurrentText("Universal (iOS + macOS)")
        cfg = tab.get_configuration()
        assert cfg["au_component_type"] == "aufx"
        assert cfg["au_component_subtype"] == "abcd"
        assert cfg["au_component_manufacturer"] == "Ddsp"
        assert cfg["au_version"] == "1.2.3"
        assert cfg["clap_extensions"] == "note-ports"
        assert cfg["clap_features"] == "instrument,audio-effect"
        assert cfg["auv3_platform"] == "Universal (iOS + macOS)"

    def test_format_specific_settings_round_trip(self, tab):
        config = {
            "au_component_type": "aumi",
            "au_component_subtype": "syn1",
            "au_component_manufacturer": "Acme",
            "au_version": "2.0.0",
            "clap_extensions": "state",
            "clap_features": "instrument",
            "auv3_platform": "macOS",
            "au": True,
            "clap": True,
            "auv3": True,
        }
        tab.load_configuration(config)
        assert tab.au_component_type.text() == "aumi"
        assert tab.au_component_subtype.text() == "syn1"
        assert tab.au_component_manufacturer.text() == "Acme"
        assert tab.au_version.text() == "2.0.0"
        assert tab.clap_extensions.text() == "state"
        assert tab.clap_features.text() == "instrument"
        assert tab.auv3_platform.currentText() == "macOS"


# ---------------------------------------------------------------------------
# At least one format required validation
# ---------------------------------------------------------------------------


class TestAtLeastOneFormatValidation:
    def _fill_required_fields(self, tab):
        """Fill all required text fields so only format selection matters."""
        tab.project_name.setText("TestPlugin")
        tab.product_name.setText("Test Plugin")
        tab.company_name.setText("TestCo")
        tab.bundle_id.setText("com.testco.testplugin")
        tab.manufacturer_code.setText("Test")

    def test_valid_when_at_least_one_format_selected(self, tab):
        self._fill_required_fields(tab)
        # Only VST3 selected
        tab.standalone.setChecked(False)
        tab.vst3.setChecked(True)
        tab.au.setChecked(False)
        tab.auv3.setChecked(False)
        tab.clap.setChecked(False)
        assert tab.validate() is True

    def test_invalid_when_no_format_selected(self, tab):
        self._fill_required_fields(tab)
        tab.standalone.setChecked(False)
        tab.vst3.setChecked(False)
        tab.au.setChecked(False)
        tab.auv3.setChecked(False)
        tab.clap.setChecked(False)
        assert tab.validate() is False

    def test_format_error_label_visible_when_no_format(self, tab):
        tab.standalone.setChecked(False)
        tab.vst3.setChecked(False)
        tab.au.setChecked(False)
        tab.auv3.setChecked(False)
        tab.clap.setChecked(False)
        # Trigger the slot manually
        tab._on_format_changed()
        assert tab.format_error_label.isHidden() is False

    def test_format_error_label_hidden_when_format_selected(self, tab):
        tab.vst3.setChecked(True)
        tab._on_format_changed()
        assert tab.format_error_label.isHidden() is True

    def test_continue_button_disabled_when_no_format(self, tab):
        self._fill_required_fields(tab)
        tab.standalone.setChecked(False)
        tab.vst3.setChecked(False)
        tab.au.setChecked(False)
        tab.auv3.setChecked(False)
        tab.clap.setChecked(False)
        tab._update_validation_state()
        assert tab.continue_button.isEnabled() is False


# ---------------------------------------------------------------------------
# Format-specific disclosure
# ---------------------------------------------------------------------------


class TestFormatDisclosure:
    def test_disclosure_label_exists(self, tab):
        assert hasattr(tab, "format_disclosure_label")

    def test_disclosure_label_shows_note_for_selected_format(self, tab):
        tab.vst3.setChecked(True)
        tab.standalone.setChecked(False)
        tab.au.setChecked(False)
        tab.auv3.setChecked(False)
        tab.clap.setChecked(False)
        tab._update_format_disclosure()
        assert "VST3" in tab.format_disclosure_label.text()

    def test_disclosure_label_shows_notes_for_multiple_formats(self, tab):
        tab.vst3.setChecked(True)
        tab.clap.setChecked(True)
        tab.standalone.setChecked(False)
        tab.au.setChecked(False)
        tab.auv3.setChecked(False)
        tab._update_format_disclosure()
        text = tab.format_disclosure_label.text()
        assert "VST3" in text
        assert "CLAP" in text

    def test_disclosure_label_hidden_when_no_format_selected(self, tab):
        tab.standalone.setChecked(False)
        tab.vst3.setChecked(False)
        tab.au.setChecked(False)
        tab.auv3.setChecked(False)
        tab.clap.setChecked(False)
        tab._update_format_disclosure()
        assert tab.format_disclosure_label.isHidden() is True


# ---------------------------------------------------------------------------
# get_configuration / load_configuration round-trip
# ---------------------------------------------------------------------------


class TestConfigurationRoundTrip:
    def test_full_round_trip(self, tab):
        full_config = {
            "project_name": "RoundTrip",
            "product_name": "Round Trip Plugin",
            "company_name": "AcmeCo",
            "bundle_id": "com.acme.roundtrip",
            "manufacturer_code": "Acme",
            "standalone": True,
            "vst3": False,
            "au": False,
            "auv3": True,
            "clap": False,
            "output_directory": "/tmp/output",
            "github_actions": True,
            "cicd_build_matrix": False,
            "cicd_run_tests": True,
            "enable_signing": True,
            "signing_team_id": "ABC123",
            "signing_certificate": "Dev Cert",
        }
        tab.load_configuration(full_config)
        result = tab.get_configuration()

        for key in full_config:
            assert result[key] == full_config[key], f"Mismatch for key: {key}"

    def test_configuration_contains_tab_complete_key(self, tab):
        config = tab.get_configuration()
        assert "tab_complete" in config


# ---------------------------------------------------------------------------
# reset()
# ---------------------------------------------------------------------------


class TestReset:
    def test_reset_clears_project_name(self, tab):
        tab.project_name.setText("SomePlugin")
        tab.reset()
        assert tab.project_name.text() == ""

    def test_reset_restores_company_defaults(self, tab):
        tab.company_name.setText("SomeCo")
        tab.manufacturer_code.setText("Some")
        tab.reset()
        assert tab.company_name.text() == "DirektDSP"
        assert tab.manufacturer_code.text() == "Ddsp"

    def test_reset_restores_format_defaults(self, tab):
        tab.standalone.setChecked(True)
        tab.vst3.setChecked(False)
        tab.clap.setChecked(False)
        tab.reset()
        assert tab.standalone.isChecked() is False
        assert tab.vst3.isChecked() is True
        assert tab.clap.isChecked() is True

    def test_reset_clears_output_directory(self, tab):
        tab.output_directory.setText("/some/dir")
        tab.reset()
        assert tab.output_directory.text() == ""

    def test_reset_clears_github_actions(self, tab):
        tab.github_actions.setChecked(True)
        tab.reset()
        assert tab.github_actions.isChecked() is False

    def test_reset_clears_signing(self, tab):
        tab.enable_signing.setChecked(True)
        tab.signing_team_id.setText("ABC123")
        tab.reset()
        assert tab.enable_signing.isChecked() is False
        assert tab.signing_team_id.text() == ""


# ---------------------------------------------------------------------------
# Signal emission
# ---------------------------------------------------------------------------


class TestSignals:
    def test_config_changed_emitted_on_project_name_change(self, tab):
        received = []
        tab.config_changed.connect(received.append)
        tab.project_name.setText("NewPlugin")
        assert len(received) > 0

    def test_config_changed_emitted_on_format_change(self, tab):
        received = []
        tab.config_changed.connect(received.append)
        tab.vst3.setChecked(not tab.vst3.isChecked())
        assert len(received) > 0

    def test_config_changed_emitted_on_github_actions_toggle(self, tab):
        received = []
        tab.config_changed.connect(received.append)
        tab.github_actions.setChecked(not tab.github_actions.isChecked())
        assert len(received) > 0

    def test_config_changed_emitted_on_signing_toggle(self, tab):
        received = []
        tab.config_changed.connect(received.append)
        tab.enable_signing.setChecked(not tab.enable_signing.isChecked())
        assert len(received) > 0
