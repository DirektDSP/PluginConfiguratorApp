"""Tests for the PresetLoadDialog."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

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
        "meta": {"name": "My Test Preset", "description": "A preset for testing"},
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


# ---------------------------------------------------------------------------
# Initialisation tests
# ---------------------------------------------------------------------------


class TestPresetLoadDialogInit:
    def test_dialog_is_not_none(self, app, config_manager):
        dlg = PresetLoadDialog(config_manager)
        assert dlg is not None
        dlg.deleteLater()

    def test_dialog_window_title(self, app, config_manager):
        dlg = PresetLoadDialog(config_manager)
        assert dlg.windowTitle() == "Load Preset"
        dlg.deleteLater()

    def test_preset_list_is_present(self, app, config_manager):
        dlg = PresetLoadDialog(config_manager)
        assert dlg._preset_list is not None
        dlg.deleteLater()

    def test_load_button_disabled_without_presets(self, app, preset_dir, monkeypatch):
        """When there are no presets the Load button must be disabled."""
        empty_dir = preset_dir / "empty_load"
        empty_dir.mkdir(parents=True, exist_ok=True)
        cfg = ConfigManager.__new__(ConfigManager)
        cfg.preset_dir = empty_dir
        cfg.example_presets_dir = Path("/nonexistent")
        monkeypatch.setattr(cfg, "_install_bundled_presets", lambda: None)
        dlg = PresetLoadDialog(cfg)
        assert not dlg._load_btn.isEnabled()
        dlg.deleteLater()

    def test_load_button_enabled_when_presets_available(self, app, config_manager, sample_config):
        """The Load button must be enabled when at least one preset is available and auto-selected."""
        config_manager.save_preset(sample_config, "btn_enable_preset")
        dlg = PresetLoadDialog(config_manager)
        # The list should be populated and the first row auto-selected
        assert dlg._preset_list.count() > 0
        assert dlg._preset_list.currentItem() is not None, "First preset should be auto-selected"
        assert dlg._load_btn.isEnabled()
        dlg.deleteLater()

    def test_load_button_disabled_when_selection_cleared(self, app, config_manager):
        """Deselecting all presets must disable the Load button."""
        dlg = PresetLoadDialog(config_manager)
        # Bundled presets ensure the list is non-empty
        assert dlg._preset_list.count() > 0
        dlg._preset_list.setCurrentRow(-1)
        assert not dlg._load_btn.isEnabled()
        dlg.deleteLater()

    def test_bundled_presets_appear_in_list(self, app, config_manager):
        """Bundled presets installed by ConfigManager must appear in the list."""
        dlg = PresetLoadDialog(config_manager)
        names = [dlg._preset_list.item(i).text() for i in range(dlg._preset_list.count())]
        for bundled in ConfigManager.BUNDLED_PRESETS:
            assert bundled in names
        dlg.deleteLater()


# ---------------------------------------------------------------------------
# Preset list population
# ---------------------------------------------------------------------------


class TestPresetLoadDialogListPopulation:
    def test_saved_preset_appears_in_list(self, app, config_manager, sample_config):
        config_manager.save_preset(sample_config, "load_list_test")
        dlg = PresetLoadDialog(config_manager)
        names = [dlg._preset_list.item(i).text() for i in range(dlg._preset_list.count())]
        assert "load_list_test" in names
        dlg.deleteLater()

    def test_list_is_sorted(self, app, config_manager, sample_config):
        config_manager.save_preset(sample_config, "zzz_last")
        config_manager.save_preset(sample_config, "aaa_first")
        dlg = PresetLoadDialog(config_manager)
        names = [dlg._preset_list.item(i).text() for i in range(dlg._preset_list.count())]
        assert names == sorted(names)
        dlg.deleteLater()


# ---------------------------------------------------------------------------
# Metadata display
# ---------------------------------------------------------------------------


class TestPresetLoadDialogMetadata:
    def test_selecting_preset_shows_display_name(self, app, config_manager, sample_config):
        config_manager.save_preset(sample_config, "meta_load_test")
        dlg = PresetLoadDialog(config_manager)

        for i in range(dlg._preset_list.count()):
            if dlg._preset_list.item(i).text() == "meta_load_test":
                dlg._preset_list.setCurrentRow(i)
                break

        assert dlg._name_label.text() == "My Test Preset"
        dlg.deleteLater()

    def test_selecting_preset_shows_description(self, app, config_manager, sample_config):
        config_manager.save_preset(sample_config, "desc_load_test")
        dlg = PresetLoadDialog(config_manager)

        for i in range(dlg._preset_list.count()):
            if dlg._preset_list.item(i).text() == "desc_load_test":
                dlg._preset_list.setCurrentRow(i)
                break

        assert "A preset for testing" in dlg._desc_text.toPlainText()
        dlg.deleteLater()

    def test_no_selection_shows_dash(self, app, preset_dir, monkeypatch):
        """When no preset is selected the name label should show a dash."""
        empty_dir = preset_dir / "empty_meta"
        empty_dir.mkdir(parents=True, exist_ok=True)
        cfg = ConfigManager.__new__(ConfigManager)
        cfg.preset_dir = empty_dir
        cfg.example_presets_dir = Path("/nonexistent")
        monkeypatch.setattr(cfg, "_install_bundled_presets", lambda: None)
        dlg = PresetLoadDialog(cfg)
        assert dlg._name_label.text() == "—"
        dlg.deleteLater()


# ---------------------------------------------------------------------------
# Load / accept behaviour
# ---------------------------------------------------------------------------


class TestPresetLoadDialogAccept:
    def test_selected_preset_name_is_none_before_accept(self, app, config_manager):
        dlg = PresetLoadDialog(config_manager)
        assert dlg.selected_preset_name() is None
        dlg.deleteLater()

    def test_on_load_stores_preset_name_and_accepts(self, app, config_manager, sample_config):
        config_manager.save_preset(sample_config, "accept_test_preset")
        dlg = PresetLoadDialog(config_manager)

        for i in range(dlg._preset_list.count()):
            if dlg._preset_list.item(i).text() == "accept_test_preset":
                dlg._preset_list.setCurrentRow(i)
                break

        # Simulate pressing Load without actually opening the dialog event loop
        dlg._on_load()

        assert dlg.selected_preset_name() == "accept_test_preset"
        dlg.deleteLater()

    def test_on_load_does_nothing_without_selection(self, app, preset_dir, monkeypatch):
        """Calling _on_load with no preset selected must not crash."""
        empty_dir = preset_dir / "empty_load2"
        empty_dir.mkdir(parents=True, exist_ok=True)
        cfg = ConfigManager.__new__(ConfigManager)
        cfg.preset_dir = empty_dir
        cfg.example_presets_dir = Path("/nonexistent")
        monkeypatch.setattr(cfg, "_install_bundled_presets", lambda: None)
        dlg = PresetLoadDialog(cfg)
        dlg._on_load()  # Should not raise
        assert dlg.selected_preset_name() is None
        dlg.deleteLater()

    def test_invalid_preset_shows_warning(self, app, config_manager, tmp_path, monkeypatch):
        """Loading a corrupt preset file must display a warning."""
        # Write a bad XML file directly to preset_dir
        bad_file = config_manager.preset_dir / "corrupt_preset.xml"
        bad_file.write_text("<not_a_preset/>", encoding="utf-8")

        dlg = PresetLoadDialog(config_manager)

        for i in range(dlg._preset_list.count()):
            if dlg._preset_list.item(i).text() == "corrupt_preset":
                dlg._preset_list.setCurrentRow(i)
                break

        warnings = []
        monkeypatch.setattr(
            QMessageBox,
            "warning",
            staticmethod(lambda *a, **kw: warnings.append(True)),
        )

        dlg._on_load()
        assert warnings, "Expected a warning dialog for invalid preset"
        assert dlg.selected_preset_name() is None
        dlg.deleteLater()


# ---------------------------------------------------------------------------
# MainWindow integration
# ---------------------------------------------------------------------------


class TestMainWindowLoadPreset:
    """Verify that MainWindow.show_load_preset_dialog applies config to all tabs."""

    def test_show_load_preset_dialog_applies_config(
        self, app, config_manager, sample_config, monkeypatch
    ):
        from ui.main_window import MainWindow

        window = MainWindow()

        # Save a preset and monkey-patch the dialog to auto-accept it
        config_manager.save_preset(sample_config, "integration_preset")

        # Provide a config manager that has the preset
        window._config_manager = config_manager

        loaded_configs = []

        original_load = window.load_preset_to_all_tabs

        def capture_load(config):
            loaded_configs.append(config)
            original_load(config)

        monkeypatch.setattr(window, "load_preset_to_all_tabs", capture_load)

        # Simulate the dialog returning "accepted" with a preset selected
        class _FakeDialog:
            def __init__(self, *a, **kw):
                pass

            def exec(self):
                return 1  # QDialog.DialogCode.Accepted

            def selected_preset_name(self):
                return "integration_preset"

        monkeypatch.setattr(
            "ui.main_window.PresetLoadDialog",
            _FakeDialog,
        )

        window.show_load_preset_dialog()

        assert loaded_configs, "load_preset_to_all_tabs was not called"
        config = loaded_configs[0]
        assert config["project_info"]["project_name"] == "TestPlugin"
        window.close()

    def test_show_load_preset_dialog_cancelled_does_nothing(
        self, app, config_manager, monkeypatch
    ):
        from ui.main_window import MainWindow

        window = MainWindow()

        loaded = []

        def capture_load(config):
            loaded.append(config)

        monkeypatch.setattr(window, "load_preset_to_all_tabs", capture_load)

        class _CancelledDialog:
            def __init__(self, *a, **kw):
                pass

            def exec(self):
                return 0  # QDialog.DialogCode.Rejected

            def selected_preset_name(self):
                return None

        monkeypatch.setattr("ui.main_window.PresetLoadDialog", _CancelledDialog)

        window.show_load_preset_dialog()

        assert not loaded, "load_preset_to_all_tabs should not be called on cancel"
        window.close()
