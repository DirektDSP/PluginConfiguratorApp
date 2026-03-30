"""Tests for DefineTab (Tab 1: Define)."""

import sys
from unittest.mock import Mock

import pytest
from PySide6.QtWidgets import QApplication

from core.base_tab import BaseTab
from ui.tabs.define_tab import DefineTab


@pytest.fixture(scope="session")
def app():
    """Create a QApplication for the entire test session."""
    instance = QApplication.instance()
    if instance is None:
        instance = QApplication(sys.argv)
    yield instance


@pytest.fixture
def tab(app):
    """Create a fresh DefineTab for each test."""
    widget = DefineTab()
    yield widget
    widget.deleteLater()


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------


class TestDefineTabInit:
    def test_tab_is_instance_of_base_tab(self, tab):
        assert isinstance(tab, BaseTab)

    def test_plugin_type_default_is_audio_fx(self, tab):
        assert tab.plugin_type.currentText() == "Audio FX"

    def test_plugin_type_has_three_options(self, tab):
        assert tab.plugin_type.count() == 3
        texts = [tab.plugin_type.itemText(i) for i in range(tab.plugin_type.count())]
        assert texts == ["Audio FX", "Instrument", "Utility"]

    def test_company_name_default(self, tab):
        assert tab.company_name.text() == "DirektDSP"

    def test_version_default(self, tab):
        assert tab.version.text() == "1.0.0"

    def test_manufacturer_code_default(self, tab):
        assert tab.manufacturer_code.text() == "Ddsp"

    def test_continue_button_disabled_initially(self, tab):
        """Continue button should be disabled when project_name is empty."""
        tab.project_name.clear()
        assert not tab.continue_button.isEnabled()

    def test_file_tree_shown_on_init(self, tab):
        assert tab.file_tree is not None
        assert tab.file_tree.topLevelItemCount() > 0


# ---------------------------------------------------------------------------
# Auto-population
# ---------------------------------------------------------------------------


class TestDefineTabAutoPopulation:
    def test_product_name_auto_filled_from_project_name(self, tab):
        tab.product_name.clear()
        tab.project_name.setText("MyPlugin")
        assert tab.product_name.text() == "My Plugin"

    def test_product_name_not_overwritten_when_already_filled(self, tab):
        tab.product_name.setText("Custom Name")
        tab.project_name.setText("AnotherPlugin")
        assert tab.product_name.text() == "Custom Name"

    def test_plugin_code_auto_filled_from_project_name(self, tab):
        tab.plugin_code.clear()
        tab.project_name.setText("MyPlugin")
        # First 4 chars, padded with 'x' if shorter
        assert len(tab.plugin_code.text()) == 4
        assert tab.plugin_code.text().startswith("MyPl")

    def test_plugin_code_not_overwritten_when_already_filled(self, tab):
        tab.plugin_code.setText("Abcd")
        tab.project_name.setText("AnotherPlugin")
        assert tab.plugin_code.text() == "Abcd"

    def test_bundle_id_auto_filled(self, tab):
        tab.bundle_id.clear()
        tab.company_name.setText("DirektDSP")
        tab.project_name.setText("MyPlugin")
        assert tab.bundle_id.text() == "com.direktdsp.myplugin"

    def test_bundle_id_updated_when_company_changes(self, tab):
        tab.project_name.setText("TestPlugin")
        tab.company_name.setText("NewCo")
        assert tab.bundle_id.text() == "com.newco.testplugin"

    def test_bundle_id_not_overwritten_when_manually_set(self, tab):
        tab.project_name.setText("TestPlugin")
        tab.company_name.setText("DirektDSP")
        tab.bundle_id.setText("io.custom.bundle")
        # Change project name; bundle_id should not be auto-overwritten
        # because the value no longer starts with "com."
        tab.project_name.setText("AnotherPlugin")
        assert tab.bundle_id.text() == "io.custom.bundle"

    def test_to_display_name_camel_case(self):
        assert DefineTab._to_display_name("MyPlugin") == "My Plugin"

    def test_to_display_name_snake_case(self):
        assert DefineTab._to_display_name("my_plugin") == "My Plugin"

    def test_to_display_name_hyphen(self):
        assert DefineTab._to_display_name("my-plugin") == "My Plugin"

    def test_to_display_name_acronym(self):
        assert DefineTab._to_display_name("HTMLParser") == "Html Parser"

    def test_to_display_name_acronym_mid(self):
        assert DefineTab._to_display_name("MyHTMLPlugin") == "My Html Plugin"


# ---------------------------------------------------------------------------
# File tree preview
# ---------------------------------------------------------------------------


class TestDefineTabFileTree:
    def test_root_node_uses_project_name(self, tab):
        tab.project_name.setText("CoolPlugin")
        root = tab.file_tree.topLevelItem(0)
        assert root is not None
        assert "CoolPlugin" in root.text(0)

    def test_editor_files_absent_for_utility_type(self, tab):
        tab.project_name.setText("MyUtil")
        idx = tab.plugin_type.findText("Utility")
        tab.plugin_type.setCurrentIndex(idx)

        root = tab.file_tree.topLevelItem(0)
        # Find the Source/ child
        source_item = None
        for i in range(root.childCount()):
            if root.child(i).text(0).startswith("Source"):
                source_item = root.child(i)
                break

        assert source_item is not None
        child_texts = [source_item.child(j).text(0) for j in range(source_item.childCount())]
        assert "PluginEditor.cpp" not in child_texts
        assert "PluginEditor.h" not in child_texts

    def test_editor_files_present_for_audio_fx(self, tab):
        tab.project_name.setText("MyFX")
        idx = tab.plugin_type.findText("Audio FX")
        tab.plugin_type.setCurrentIndex(idx)

        root = tab.file_tree.topLevelItem(0)
        source_item = None
        for i in range(root.childCount()):
            if root.child(i).text(0).startswith("Source"):
                source_item = root.child(i)
                break

        assert source_item is not None
        child_texts = [source_item.child(j).text(0) for j in range(source_item.childCount())]
        assert "PluginEditor.cpp" in child_texts
        assert "PluginEditor.h" in child_texts

    def test_file_tree_updates_on_type_change(self, tab):
        tab.project_name.setText("SynthPlug")
        tab.plugin_type.setCurrentIndex(tab.plugin_type.findText("Instrument"))
        root1_text = tab.file_tree.topLevelItem(0).text(0)
        tab.plugin_type.setCurrentIndex(tab.plugin_type.findText("Utility"))
        root2_text = tab.file_tree.topLevelItem(0).text(0)
        # Root label should remain consistent; just verifying tree rebuilds
        assert "SynthPlug" in root1_text
        assert "SynthPlug" in root2_text


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


class TestDefineTabValidation:
    def test_validation_fails_when_project_name_empty(self, tab):
        tab.project_name.clear()
        tab.company_name.setText("DirektDSP")
        assert not tab.validate()

    def test_validation_fails_when_company_empty(self, tab):
        tab.project_name.setText("MyPlugin")
        tab.company_name.clear()
        assert not tab.validate()

    def test_validation_passes_when_required_fields_filled(self, tab):
        tab.project_name.setText("MyPlugin")
        tab.company_name.setText("DirektDSP")
        assert tab.validate()

    def test_continue_button_enabled_when_valid(self, tab):
        tab.project_name.setText("MyPlugin")
        tab.company_name.setText("DirektDSP")
        assert tab.continue_button.isEnabled()

    def test_continue_button_disabled_when_invalid(self, tab):
        tab.project_name.clear()
        tab.company_name.setText("DirektDSP")
        assert not tab.continue_button.isEnabled()


# ---------------------------------------------------------------------------
# get_configuration / load_configuration / reset
# ---------------------------------------------------------------------------


class TestDefineTabConfiguration:
    def test_get_configuration_returns_dict(self, tab):
        config = tab.get_configuration()
        assert isinstance(config, dict)

    def test_get_configuration_keys(self, tab):
        config = tab.get_configuration()
        expected_keys = {
            "plugin_type",
            "project_name",
            "product_name",
            "company_name",
            "version",
            "manufacturer_code",
            "plugin_code",
            "bundle_id",
            "tab_complete",
        }
        assert expected_keys.issubset(config.keys())

    def test_get_configuration_values(self, tab):
        tab.project_name.setText("MyPlugin")
        tab.company_name.setText("DirektDSP")
        tab.version.setText("2.0.0")
        tab.plugin_type.setCurrentIndex(tab.plugin_type.findText("Instrument"))

        config = tab.get_configuration()
        assert config["project_name"] == "MyPlugin"
        assert config["company_name"] == "DirektDSP"
        assert config["version"] == "2.0.0"
        assert config["plugin_type"] == "Instrument"

    def test_load_configuration_restores_state(self, tab):
        original_config = {
            "plugin_type": "Utility",
            "project_name": "SavedPlugin",
            "product_name": "Saved Plugin",
            "company_name": "TestCo",
            "version": "3.1.0",
            "manufacturer_code": "Test",
            "plugin_code": "TSPl",
            "bundle_id": "com.testco.savedplugin",
        }
        tab.load_configuration(original_config)

        assert tab.plugin_type.currentText() == "Utility"
        assert tab.project_name.text() == "SavedPlugin"
        assert tab.product_name.text() == "Saved Plugin"
        assert tab.company_name.text() == "TestCo"
        assert tab.version.text() == "3.1.0"
        assert tab.manufacturer_code.text() == "Test"
        assert tab.plugin_code.text() == "TSPl"
        assert tab.bundle_id.text() == "com.testco.savedplugin"

    def test_reset_restores_defaults(self, tab):
        tab.project_name.setText("SomePlugin")
        tab.company_name.setText("SomeCo")
        tab.version.setText("9.9.9")
        tab.reset()

        assert tab.project_name.text() == ""
        assert tab.company_name.text() == "DirektDSP"
        assert tab.version.text() == "1.0.0"
        assert tab.manufacturer_code.text() == "Ddsp"

    def test_config_changed_signal_emitted(self, tab):
        mock_slot = Mock()
        tab.config_changed.connect(mock_slot)
        tab.project_name.setText("SignalTest")
        assert mock_slot.called

    def test_validation_changed_signal_emitted(self, tab):
        mock_slot = Mock()
        tab.validation_changed.connect(mock_slot)
        tab.project_name.setText("SignalTestPlugin")
        assert mock_slot.called
