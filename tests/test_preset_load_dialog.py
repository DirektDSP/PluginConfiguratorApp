"""Tests for the PresetLoadDialog."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from core.config_manager import ConfigManager
from ui.dialogs.preset_load_dialog import PresetLoadDialog


@pytest.fixture(scope="module")
def app():
    """Create a single QApplication instance for all tests in this module."""
    instance = QApplication.instance()
    if not instance:
        instance = QApplication(sys.argv)
    yield instance


@pytest.fixture
def preset_dir(tmp_path: Path) -> Path:
    return tmp_path / "presets"


@pytest.fixture
def config_manager(preset_dir: Path) -> ConfigManager:
    return ConfigManager(preset_dir=preset_dir)


@pytest.fixture
def sample_config() -> dict:
    return {
        "meta": {"name": "Test Preset", "description": "A test preset description"},
        "project_info": {
            "template_name": "Audio FX Plugin",
            "template_url": "https://github.com/SeamusMullan/PluginTemplate.git",
            "project_name": "TestPlugin",
            "product_name": "Test Plugin",
            "version": "1.0.0",
            "company_name": "TestCo",
            "bundle_id": "com.test.plugin",
            "manufacturer_code": "TST1",
            "plugin_code": "TST1",
            "output_directory": "/tmp/output",
        },
        "configuration": {
            "standalone": False,
            "vst3": True,
            "au": False,
            "auv3": False,
            "clap": False,
            "au_component_type": "aufx",
            "au_component_subtype": "plug",
            "au_component_manufacturer": "Ddsp",
            "au_version": "1.0.0",
            "clap_extensions": "note-ports,state",
            "clap_features": "audio-effect",
            "auv3_platform": "iOS",
            "gui_width": 800,
            "gui_height": 600,
            "resizable": False,
            "background_image": "",
            "code_signing": False,
            "installer": False,
            "default_bypass": False,
            "input_gain": False,
            "output_gain": False,
        },
        "implementations": {
            "moonbase_licensing": False,
            "melatonin_inspector": False,
            "custom_gui_framework": False,
            "logging_framework": False,
            "clap_builds": False,
            "preset_management": False,
            "preset_format": "",
            "ab_comparison": False,
            "state_management": False,
            "gpu_audio": False,
        },
        "user_experience": {
            "wizard": False,
            "preview": False,
            "preset_management": False,
        },
        "development_workflow": {
            "vcs": False,
            "testing": False,
            "code_quality": False,
            "validation_tools": False,
            "scaffolding": False,
        },
    }


@pytest.fixture
def dialog(app, config_manager: ConfigManager) -> PresetLoadDialog:
    dlg = PresetLoadDialog(config_manager)
    yield dlg
    dlg.deleteLater()


# ---------------------------------------------------------------------------
# Initialisation tests
# ---------------------------------------------------------------------------


class TestPresetLoadDialogInit:
    def test_dialog_is_not_none(self, dialog):
        assert dialog is not None

    def test_dialog_window_title(self, dialog):
        assert dialog.windowTitle() == "Load Preset"

    def test_preset_list_is_present(self, dialog):
        assert dialog._preset_list is not None

    def test_load_button_disabled_without_presets(self, app, preset_dir):
        """When there are no presets the Load button must be disabled."""
        empty_dir = preset_dir / "empty"
        empty_dir.mkdir(parents=True, exist_ok=True)
        cfg = ConfigManager.__new__(ConfigManager)
        cfg.preset_dir = empty_dir
        cfg.example_presets_dir = Path("/nonexistent")
        dlg = PresetLoadDialog(cfg)
        assert not dlg._load_btn.isEnabled()
        dlg.deleteLater()

    def test_load_button_enabled_with_preset(self, app, config_manager, sample_config):
        """When at least one preset exists the Load button must be enabled."""
        config_manager.save_preset(sample_config, "init_test_preset")
        dlg = PresetLoadDialog(config_manager)
        # The first preset should be auto-selected so Load is enabled.
        assert dlg._load_btn.isEnabled()
        dlg.deleteLater()

    def test_bundled_presets_appear_in_list(self, dialog):
        """The bundled presets installed by ConfigManager should appear in the list."""
        names = [dialog._preset_list.item(i).text() for i in range(dialog._preset_list.count())]
        for bundled in ConfigManager.BUNDLED_PRESETS:
            assert bundled in names

    def test_selected_preset_name_none_before_accept(self, dialog):
        """selected_preset_name() should return None before the dialog is accepted."""
        assert dialog.selected_preset_name() is None


# ---------------------------------------------------------------------------
# Preset list population
# ---------------------------------------------------------------------------


class TestPresetListPopulation:
    def test_saved_preset_appears_in_list(self, app, config_manager, sample_config):
        config_manager.save_preset(sample_config, "list_test_preset")
        dlg = PresetLoadDialog(config_manager)
        names = [dlg._preset_list.item(i).text() for i in range(dlg._preset_list.count())]
        assert "list_test_preset" in names
        dlg.deleteLater()

    def test_first_preset_auto_selected(self, app, config_manager, sample_config):
        """The first preset in the list should be automatically selected."""
        config_manager.save_preset(sample_config, "auto_select_preset")
        dlg = PresetLoadDialog(config_manager)
        assert dlg._preset_list.currentRow() == 0
        dlg.deleteLater()


# ---------------------------------------------------------------------------
# Metadata display
# ---------------------------------------------------------------------------


class TestMetadataDisplay:
    def test_selecting_preset_shows_name(self, app, config_manager, sample_config):
        config_manager.save_preset(sample_config, "meta_name_preset")
        dlg = PresetLoadDialog(config_manager)

        for i in range(dlg._preset_list.count()):
            if dlg._preset_list.item(i).text() == "meta_name_preset":
                dlg._preset_list.setCurrentRow(i)
                break

        assert dlg._name_label.text() == "Test Preset"
        dlg.deleteLater()

    def test_selecting_preset_shows_description(self, app, config_manager, sample_config):
        config_manager.save_preset(sample_config, "meta_desc_preset")
        dlg = PresetLoadDialog(config_manager)

        for i in range(dlg._preset_list.count()):
            if dlg._preset_list.item(i).text() == "meta_desc_preset":
                dlg._preset_list.setCurrentRow(i)
                break

        assert "A test preset description" in dlg._desc_text.toPlainText()
        dlg.deleteLater()

    def test_no_selection_shows_placeholder(self, app, preset_dir):
        """With no presets and no selection the name label should show a dash."""
        empty_dir = preset_dir / "empty_meta"
        empty_dir.mkdir(parents=True, exist_ok=True)
        cfg = ConfigManager.__new__(ConfigManager)
        cfg.preset_dir = empty_dir
        cfg.example_presets_dir = Path("/nonexistent")
        dlg = PresetLoadDialog(cfg)
        assert dlg._name_label.text() == "—"
        assert dlg._desc_text.toPlainText() == ""
        dlg.deleteLater()


# ---------------------------------------------------------------------------
# Load button behaviour
# ---------------------------------------------------------------------------


class TestLoadButton:
    def test_load_button_enabled_when_preset_selected(self, app, config_manager, sample_config):
        config_manager.save_preset(sample_config, "load_btn_preset")
        dlg = PresetLoadDialog(config_manager)

        for i in range(dlg._preset_list.count()):
            if dlg._preset_list.item(i).text() == "load_btn_preset":
                dlg._preset_list.setCurrentRow(i)
                break

        assert dlg._load_btn.isEnabled()
        dlg.deleteLater()

    def test_on_load_sets_selected_preset_name(self, app, config_manager, sample_config):
        """_on_load() should store the selected preset name."""
        config_manager.save_preset(sample_config, "on_load_preset")
        dlg = PresetLoadDialog(config_manager)

        for i in range(dlg._preset_list.count()):
            if dlg._preset_list.item(i).text() == "on_load_preset":
                dlg._preset_list.setCurrentRow(i)
                break

        # Call _on_load directly to avoid blocking exec()
        dlg._on_load()
        assert dlg.selected_preset_name() == "on_load_preset"
        dlg.deleteLater()

    def test_on_load_with_no_selection_does_nothing(self, app, preset_dir):
        """_on_load() must not crash or change state when nothing is selected."""
        empty_dir = preset_dir / "empty_load"
        empty_dir.mkdir(parents=True, exist_ok=True)
        cfg = ConfigManager.__new__(ConfigManager)
        cfg.preset_dir = empty_dir
        cfg.example_presets_dir = Path("/nonexistent")
        dlg = PresetLoadDialog(cfg)

        # No selection; calling _on_load should be a no-op.
        dlg._on_load()
        assert dlg.selected_preset_name() is None
        dlg.deleteLater()

    def test_double_click_sets_selected_preset_name(self, app, config_manager, sample_config):
        """Double-clicking a preset should select it (same as clicking Load)."""
        config_manager.save_preset(sample_config, "dblclick_preset")
        dlg = PresetLoadDialog(config_manager)

        for i in range(dlg._preset_list.count()):
            item = dlg._preset_list.item(i)
            if item.text() == "dblclick_preset":
                dlg._preset_list.setCurrentRow(i)
                dlg._preset_list.itemDoubleClicked.emit(item)
                break

        assert dlg.selected_preset_name() == "dblclick_preset"
        dlg.deleteLater()
