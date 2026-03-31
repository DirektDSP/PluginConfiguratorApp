"""Tests for ImplementTab (Tab 3: DSP/UI templates and module selection)."""

import sys

import pytest
from PySide6.QtWidgets import QApplication, QComboBox, QCheckBox, QTreeWidget

from ui.tabs.implement_tab import (
    ImplementTab,
    _DEFAULT_GRACE_PERIOD_DAYS,
    _DEFAULT_MOONBASE_LICENSE,
    _DEFAULT_PRESET_FORMAT,
    _DEFAULT_PRESET_STORAGE,
    _DSP_TEMPLATES,
    _MOONBASE_LICENSE_TYPES,
    _MODULES,
    _PRESET_FORMATS,
    _PRESET_STORAGE_LOCATIONS,
    _UI_TEMPLATES,
)


@pytest.fixture(scope="module")
def app():
    """Provide a QApplication for the entire module."""
    instance = QApplication.instance()
    if not instance:
        instance = QApplication(sys.argv)
    yield instance


@pytest.fixture
def tab(app):
    """Return a fresh ImplementTab for each test."""
    t = ImplementTab()
    yield t
    t.deleteLater()


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

class TestInitialization:
    def test_is_implement_tab_instance(self, tab):
        assert isinstance(tab, ImplementTab)

    def test_dsp_combo_exists(self, tab):
        assert hasattr(tab, "dsp_combo")
        assert isinstance(tab.dsp_combo, QComboBox)

    def test_ui_combo_exists(self, tab):
        assert hasattr(tab, "ui_combo")
        assert isinstance(tab.ui_combo, QComboBox)

    def test_file_tree_exists(self, tab):
        assert hasattr(tab, "file_tree")
        assert isinstance(tab.file_tree, QTreeWidget)

    def test_module_checkboxes_exist(self, tab):
        for key in ("Moonbase", "Inspector", "Presets"):
            assert key in tab._module_checkboxes
            assert isinstance(tab._module_checkboxes[key], QCheckBox)
        assert hasattr(tab, "_moonbase_license_type")
        assert hasattr(tab, "_moonbase_grace_period")
        assert hasattr(tab, "_preset_format")
        assert hasattr(tab, "_preset_storage")


# ---------------------------------------------------------------------------
# DSP template dropdown
# ---------------------------------------------------------------------------

class TestDspTemplateDropdown:
    def test_has_all_dsp_options(self, tab):
        items = [tab.dsp_combo.itemText(i) for i in range(tab.dsp_combo.count())]
        assert items == list(_DSP_TEMPLATES.keys())

    def test_default_is_simple(self, tab):
        assert tab.dsp_combo.currentText() == "Simple"

    def test_can_select_each_dsp_template(self, tab):
        for name in _DSP_TEMPLATES:
            tab.dsp_combo.setCurrentText(name)
            assert tab.dsp_combo.currentText() == name

    def test_description_updates_on_dsp_change(self, tab):
        tab.dsp_combo.setCurrentText("EQ")
        assert tab.dsp_description.text() == _DSP_TEMPLATES["EQ"]["description"]

        tab.dsp_combo.setCurrentText("Reverb")
        assert tab.dsp_description.text() == _DSP_TEMPLATES["Reverb"]["description"]


# ---------------------------------------------------------------------------
# UI template dropdown
# ---------------------------------------------------------------------------

class TestUiTemplateDropdown:
    def test_has_all_ui_options(self, tab):
        items = [tab.ui_combo.itemText(i) for i in range(tab.ui_combo.count())]
        assert items == list(_UI_TEMPLATES.keys())

    def test_default_is_minimal(self, tab):
        assert tab.ui_combo.currentText() == "Minimal"

    def test_can_select_each_ui_template(self, tab):
        for name in _UI_TEMPLATES:
            tab.ui_combo.setCurrentText(name)
            assert tab.ui_combo.currentText() == name

    def test_description_updates_on_ui_change(self, tab):
        tab.ui_combo.setCurrentText("Advanced")
        assert tab.ui_description.text() == _UI_TEMPLATES["Advanced"]["description"]


# ---------------------------------------------------------------------------
# Template description panels (features)
# ---------------------------------------------------------------------------


class TestTemplateDescriptions:
    def test_dsp_features_label_exists(self, tab):
        assert hasattr(tab, "dsp_features")

    def test_ui_features_label_exists(self, tab):
        assert hasattr(tab, "ui_features")

    def test_dsp_features_updates_on_selection(self, tab):
        for name, info in _DSP_TEMPLATES.items():
            tab.dsp_combo.setCurrentText(name)
            for feature in info.get("features", []):
                assert feature in tab.dsp_features.text()

    def test_ui_features_updates_on_selection(self, tab):
        for name, info in _UI_TEMPLATES.items():
            tab.ui_combo.setCurrentText(name)
            for feature in info.get("features", []):
                assert feature in tab.ui_features.text()

    def test_features_use_checkmark_prefix(self, tab):
        tab.dsp_combo.setCurrentText("EQ")
        assert "\u2713" in tab.dsp_features.text()

    def test_all_templates_have_features(self):
        for name, info in _DSP_TEMPLATES.items():
            assert "features" in info, f"DSP template '{name}' missing features"
            assert len(info["features"]) > 0
        for name, info in _UI_TEMPLATES.items():
            assert "features" in info, f"UI template '{name}' missing features"
            assert len(info["features"]) > 0


# ---------------------------------------------------------------------------
# Module checkboxes
# ---------------------------------------------------------------------------

class TestModuleCheckboxes:
    def test_modules_unchecked_by_default(self, tab):
        for cb in tab._module_checkboxes.values():
            assert not cb.isChecked()

    def test_can_check_moonbase(self, tab):
        tab._module_checkboxes["Moonbase"].setChecked(True)
        assert tab._module_checkboxes["Moonbase"].isChecked()

    def test_can_check_inspector(self, tab):
        tab._module_checkboxes["Inspector"].setChecked(True)
        assert tab._module_checkboxes["Inspector"].isChecked()

    def test_can_check_presets(self, tab):
        tab._module_checkboxes["Presets"].setChecked(True)
        assert tab._module_checkboxes["Presets"].isChecked()


# ---------------------------------------------------------------------------
# Accordion disclosure
# ---------------------------------------------------------------------------

class TestAccordion:
    def test_modules_body_hidden_by_default(self, tab):
        assert tab._modules_expander.is_expanded is False

    def test_toggle_shows_modules_body(self, tab):
        tab._modules_expander.set_expanded(True)
        assert tab._modules_expander.is_expanded is True

    def test_toggle_hides_modules_body_again(self, tab):
        tab._modules_expander.set_expanded(True)
        tab._modules_expander.set_expanded(False)
        assert tab._modules_expander.is_expanded is False

    def test_toggle_text_changes(self, tab):
        tab._modules_expander.set_expanded(True)
        assert "▼" in tab._modules_expander.indicator_text
        tab._modules_expander.set_expanded(False)
        assert "▶" in tab._modules_expander.indicator_text


# ---------------------------------------------------------------------------
# File tree preview
# ---------------------------------------------------------------------------

class TestFileTreePreview:
    def _root_children_names(self, tab) -> list[str]:
        root = tab.file_tree.invisibleRootItem().child(0)
        if root is None:
            return []
        return [root.child(i).text(0) for i in range(root.childCount())]

    def test_tree_populated_on_init(self, tab):
        root = tab.file_tree.invisibleRootItem().child(0)
        assert root is not None
        assert root.childCount() > 0

    def test_source_dir_present(self, tab):
        names = self._root_children_names(tab)
        assert "source" in names

    def test_dsp_change_updates_tree(self, tab):
        tab.dsp_combo.setCurrentText("Full")
        source = self._get_dir_item(tab, "source")
        source_files = [source.child(i).text(0) for i in range(source.childCount())]
        for f in _DSP_TEMPLATES["Full"]["source_files"]:
            assert f in source_files

    def test_ui_change_updates_tree(self, tab):
        tab.ui_combo.setCurrentText("Advanced")
        source = self._get_dir_item(tab, "source")
        source_files = [source.child(i).text(0) for i in range(source.childCount())]
        for f in _UI_TEMPLATES["Advanced"]["editor_files"]:
            assert f in source_files

    def test_module_dir_appears_when_checked(self, tab):
        tab._module_checkboxes["Moonbase"].setChecked(True)
        names = self._root_children_names(tab)
        assert "modules" in names

    def test_module_dir_gone_when_unchecked(self, tab):
        tab._module_checkboxes["Moonbase"].setChecked(True)
        tab._module_checkboxes["Moonbase"].setChecked(False)
        names = self._root_children_names(tab)
        assert "modules" not in names

    def test_presets_module_adds_source_files(self, tab):
        tab._module_checkboxes["Presets"].setChecked(True)
        source = self._get_dir_item(tab, "source")
        source_files = [source.child(i).text(0) for i in range(source.childCount())]
        for f in _MODULES["Presets"]["extra_source"]:
            assert f in source_files

    def _get_dir_item(self, tab, name: str):
        root = tab.file_tree.invisibleRootItem().child(0)
        for i in range(root.childCount()):
            child = root.child(i)
            if child.text(0) == name:
                return child
        return None


# ---------------------------------------------------------------------------
# Module option panels
# ---------------------------------------------------------------------------


class TestModuleOptions:
    def test_module_options_disabled_until_enabled(self, tab):
        assert not tab._moonbase_license_type.isEnabled()
        assert not tab._moonbase_grace_period.isEnabled()
        assert not tab._preset_format.isEnabled()
        assert not tab._preset_storage.isEnabled()

    def test_enabling_module_reveals_options(self, tab):
        tab._module_checkboxes["Moonbase"].setChecked(True)
        assert tab._moonbase_license_type.isEnabled()
        assert tab._moonbase_grace_period.isEnabled()
        assert tab._module_expanders["Moonbase"].is_expanded

    def test_preset_storage_nested_accordion(self, tab):
        tab._module_checkboxes["Presets"].setChecked(True)
        tab._preset_storage_expander.set_expanded(True)
        assert tab._preset_storage_expander.is_expanded is True

    def test_enabling_presets_enables_controls(self, tab):
        tab._module_checkboxes["Presets"].setChecked(True)
        assert tab._preset_format.isEnabled()
        assert tab._preset_storage.isEnabled()

    def test_disabling_module_collapses_expander(self, tab):
        tab._module_checkboxes["Moonbase"].setChecked(True)
        tab._module_checkboxes["Moonbase"].setChecked(False)
        assert tab._module_expanders["Moonbase"].is_expanded is False


# ---------------------------------------------------------------------------
# get_configuration / load_configuration
# ---------------------------------------------------------------------------

class TestConfiguration:
    def test_get_configuration_returns_dict(self, tab):
        config = tab.get_configuration()
        assert isinstance(config, dict)

    def test_get_configuration_keys(self, tab):
        config = tab.get_configuration()
        assert "dsp_template" in config
        assert "ui_template" in config
        assert "module_moonbase" in config
        assert "module_moonbase_license_type" in config
        assert "module_moonbase_grace_period" in config
        assert "module_inspector" in config
        assert "module_presets" in config
        assert "module_presets_format" in config
        assert "module_presets_storage" in config
        assert "modules_expanded" in config

    def test_get_configuration_defaults(self, tab):
        config = tab.get_configuration()
        assert config["dsp_template"] == "Simple"
        assert config["ui_template"] == "Minimal"
        assert config["module_moonbase"] is False
        assert config["module_inspector"] is False
        assert config["module_presets"] is False
        assert config["module_moonbase_license_type"] is None
        assert config["module_moonbase_grace_period"] is None
        assert config["module_presets_format"] is None
        assert config["module_presets_storage"] is None

    def test_load_configuration_restores_state(self, tab):
        saved = {
            "dsp_template": "EQ",
            "ui_template": "Advanced",
            "module_moonbase": True,
            "module_moonbase_license_type": "Perpetual",
            "module_moonbase_grace_period": 30,
            "module_inspector": False,
            "module_presets": True,
            "module_presets_format": "JSON",
            "module_presets_storage": "Cloud/Sync",
            "module_moonbase_expanded": True,
            "module_inspector_expanded": False,
            "module_presets_expanded": True,
            "module_presets_storage_expanded": True,
            "modules_expanded": True,
        }
        tab.load_configuration(saved)
        assert tab.dsp_combo.currentText() == "EQ"
        assert tab.ui_combo.currentText() == "Advanced"
        assert tab._module_checkboxes["Moonbase"].isChecked() is True
        assert tab._module_checkboxes["Inspector"].isChecked() is False
        assert tab._module_checkboxes["Presets"].isChecked() is True
        assert tab._moonbase_license_type.currentText() == "Perpetual"
        assert tab._moonbase_grace_period.value() == 30
        assert tab._preset_format.currentText() == "JSON"
        assert tab._preset_storage.currentText() == "Cloud/Sync"
        assert tab._module_expanders["Moonbase"].is_expanded is True
        assert tab._module_expanders["Inspector"].is_expanded is False
        assert tab._module_expanders["Presets"].is_expanded is True
        assert tab._preset_storage_expander.is_expanded is True
        assert tab._modules_expander.is_expanded is True

    def test_load_configuration_unknown_template_ignored(self, tab):
        tab.load_configuration({"dsp_template": "NonExistent"})
        # Should stay on whatever was already selected; not crash
        assert tab.dsp_combo.currentText() in list(_DSP_TEMPLATES.keys())

    def test_round_trip(self, tab):
        tab.dsp_combo.setCurrentText("Reverb")
        tab.ui_combo.setCurrentText("Standard")
        tab._module_checkboxes["Inspector"].setChecked(True)
        tab._module_checkboxes["Moonbase"].setChecked(True)
        tab._moonbase_license_type.setCurrentText("Subscription")
        tab._moonbase_grace_period.setValue(21)

        config = tab.get_configuration()

        fresh = ImplementTab()
        fresh.load_configuration(config)
        assert fresh.get_configuration() == config
        fresh.deleteLater()


# ---------------------------------------------------------------------------
# validate / reset
# ---------------------------------------------------------------------------

class TestValidateAndReset:
    def test_validate_always_true(self, tab):
        assert tab.validate() is True

    def test_reset_returns_to_defaults(self, tab):
        tab.dsp_combo.setCurrentText("Full")
        tab.ui_combo.setCurrentText("Advanced")
        tab._module_checkboxes["Moonbase"].setChecked(True)
        tab._modules_expander.set_expanded(True)
        tab._moonbase_license_type.setCurrentText("Subscription")
        tab._moonbase_grace_period.setValue(25)
        tab._preset_storage_expander.set_expanded(True)

        tab.reset()

        assert tab.dsp_combo.currentText() == "Simple"
        assert tab.ui_combo.currentText() == "Minimal"
        for cb in tab._module_checkboxes.values():
            assert not cb.isChecked()
        assert tab._moonbase_license_type.currentText() == _DEFAULT_MOONBASE_LICENSE
        assert tab._moonbase_grace_period.value() == _DEFAULT_GRACE_PERIOD_DAYS
        assert tab._preset_format.currentText() == _DEFAULT_PRESET_FORMAT
        assert tab._preset_storage.currentText() == _DEFAULT_PRESET_STORAGE
        assert not tab._modules_expander.is_expanded
        assert all(not expander.is_expanded for expander in tab._module_expanders.values())

    def test_reset_repopulates_file_tree(self, tab):
        tab.dsp_combo.setCurrentText("Full")
        tab.reset()
        root = tab.file_tree.invisibleRootItem().child(0)
        assert root is not None
        assert root.childCount() > 0


# ---------------------------------------------------------------------------
# Signals
# ---------------------------------------------------------------------------

class TestSignals:
    def test_config_changed_emitted_on_dsp_change(self, tab):
        received = []
        tab.config_changed.connect(lambda c: received.append(c))
        tab.dsp_combo.setCurrentText("EQ")
        assert len(received) > 0
        assert received[-1]["dsp_template"] == "EQ"

    def test_config_changed_emitted_on_ui_change(self, tab):
        received = []
        tab.config_changed.connect(lambda c: received.append(c))
        tab.ui_combo.setCurrentText("Standard")
        assert len(received) > 0
        assert received[-1]["ui_template"] == "Standard"

    def test_config_changed_emitted_on_module_toggle(self, tab):
        received = []
        tab.config_changed.connect(lambda c: received.append(c))
        tab._module_checkboxes["Presets"].setChecked(True)
        assert len(received) > 0
        assert received[-1]["module_presets"] is True
