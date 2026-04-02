"""Tests for the PresetManagementDialog."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

from core.config_manager import ConfigManager
from ui.dialogs.preset_management_dialog import PresetManagementDialog


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
def sample_config(config_manager: ConfigManager) -> dict:
    return {
        "meta": {"name": "TestPreset", "description": "A test preset"},
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
def dialog(app, config_manager: ConfigManager) -> PresetManagementDialog:
    dlg = PresetManagementDialog(config_manager)
    yield dlg
    dlg.deleteLater()


# ---------------------------------------------------------------------------
# Initialisation tests
# ---------------------------------------------------------------------------


class TestPresetManagementDialogInit:
    def test_dialog_is_not_none(self, dialog):
        assert dialog is not None

    def test_dialog_window_title(self, dialog):
        assert dialog.windowTitle() == "Manage Presets"

    def test_preset_list_is_present(self, dialog):
        assert dialog._preset_list is not None

    def test_delete_button_disabled_initially_without_presets(self, app, preset_dir):
        """When there are no presets the delete button must be disabled."""
        # Use an empty preset_dir (no bundled presets to avoid pre-population)
        empty_dir = preset_dir / "empty"
        empty_dir.mkdir(parents=True, exist_ok=True)
        cfg = ConfigManager.__new__(ConfigManager)
        cfg.preset_dir = empty_dir
        cfg.example_presets_dir = Path("/nonexistent")
        cfg.preset_dir.mkdir(parents=True, exist_ok=True)
        cfg._install_bundled_presets = lambda: None  # type: ignore[method-assign]
        dlg = PresetManagementDialog(cfg)
        assert not dlg._delete_btn.isEnabled()
        dlg.deleteLater()

    def test_export_button_disabled_initially_without_presets(self, app, preset_dir):
        """When there are no presets the export button must be disabled."""
        empty_dir = preset_dir / "empty2"
        empty_dir.mkdir(parents=True, exist_ok=True)
        cfg = ConfigManager.__new__(ConfigManager)
        cfg.preset_dir = empty_dir
        cfg.example_presets_dir = Path("/nonexistent")
        cfg._install_bundled_presets = lambda: None  # type: ignore[method-assign]
        dlg = PresetManagementDialog(cfg)
        assert not dlg._export_btn.isEnabled()
        dlg.deleteLater()

    def test_import_button_always_enabled(self, dialog):
        assert dialog._import_btn.isEnabled()

    def test_bundled_presets_appear_in_list(self, dialog):
        """The list should contain the bundled presets that were installed."""
        names = [dialog._preset_list.item(i).text() for i in range(dialog._preset_list.count())]
        for bundled in ConfigManager.BUNDLED_PRESETS:
            assert bundled in names


# ---------------------------------------------------------------------------
# Preset list population
# ---------------------------------------------------------------------------


class TestPresetListPopulation:
    def test_saved_preset_appears_in_list(self, app, config_manager, sample_config):
        config_manager.save_preset(sample_config, "my_test_preset")
        dlg = PresetManagementDialog(config_manager)
        names = [dlg._preset_list.item(i).text() for i in range(dlg._preset_list.count())]
        assert "my_test_preset" in names
        dlg.deleteLater()

    def test_deleted_preset_disappears_from_list(self, app, config_manager, sample_config):
        config_manager.save_preset(sample_config, "to_delete_preset")
        config_manager.delete_preset("to_delete_preset")
        dlg = PresetManagementDialog(config_manager)
        names = [dlg._preset_list.item(i).text() for i in range(dlg._preset_list.count())]
        assert "to_delete_preset" not in names
        dlg.deleteLater()


# ---------------------------------------------------------------------------
# Metadata display
# ---------------------------------------------------------------------------


class TestMetadataDisplay:
    def test_selecting_preset_shows_name(self, app, config_manager, sample_config):
        config_manager.save_preset(sample_config, "meta_test_preset")
        dlg = PresetManagementDialog(config_manager)

        # Find and select the preset
        for i in range(dlg._preset_list.count()):
            if dlg._preset_list.item(i).text() == "meta_test_preset":
                dlg._preset_list.setCurrentRow(i)
                break

        assert dlg._name_label.text() == "TestPreset"
        dlg.deleteLater()

    def test_selecting_preset_shows_description(self, app, config_manager, sample_config):
        config_manager.save_preset(sample_config, "desc_test_preset")
        dlg = PresetManagementDialog(config_manager)

        for i in range(dlg._preset_list.count()):
            if dlg._preset_list.item(i).text() == "desc_test_preset":
                dlg._preset_list.setCurrentRow(i)
                break

        assert "A test preset" in dlg._desc_text.toPlainText()
        dlg.deleteLater()

    def test_selecting_preset_shows_file_path(self, app, config_manager, sample_config):
        config_manager.save_preset(sample_config, "path_test_preset")
        dlg = PresetManagementDialog(config_manager)

        for i in range(dlg._preset_list.count()):
            if dlg._preset_list.item(i).text() == "path_test_preset":
                dlg._preset_list.setCurrentRow(i)
                break

        assert "path_test_preset.xml" in dlg._file_label.text()
        dlg.deleteLater()


# ---------------------------------------------------------------------------
# Delete functionality
# ---------------------------------------------------------------------------


class TestDeletePreset:
    def test_delete_removes_file(self, app, config_manager, sample_config, monkeypatch):
        config_manager.save_preset(sample_config, "deleteme_preset")
        dlg = PresetManagementDialog(config_manager)

        for i in range(dlg._preset_list.count()):
            if dlg._preset_list.item(i).text() == "deleteme_preset":
                dlg._preset_list.setCurrentRow(i)
                break

        # Bypass the confirmation dialog
        monkeypatch.setattr(
            QMessageBox,
            "question",
            staticmethod(lambda *a, **kw: QMessageBox.StandardButton.Yes),
        )

        emitted = []
        dlg.presets_changed.connect(lambda: emitted.append(True))
        dlg._on_delete()

        preset_path = config_manager.preset_dir / "deleteme_preset.xml"
        assert not preset_path.exists()
        assert emitted, "presets_changed signal was not emitted"
        dlg.deleteLater()

    def test_delete_updates_list(self, app, config_manager, sample_config, monkeypatch):
        config_manager.save_preset(sample_config, "listupdate_preset")
        dlg = PresetManagementDialog(config_manager)

        for i in range(dlg._preset_list.count()):
            if dlg._preset_list.item(i).text() == "listupdate_preset":
                dlg._preset_list.setCurrentRow(i)
                break

        monkeypatch.setattr(
            QMessageBox,
            "question",
            staticmethod(lambda *a, **kw: QMessageBox.StandardButton.Yes),
        )

        dlg._on_delete()

        names = [dlg._preset_list.item(i).text() for i in range(dlg._preset_list.count())]
        assert "listupdate_preset" not in names
        dlg.deleteLater()

    def test_delete_cancelled_keeps_preset(self, app, config_manager, sample_config, monkeypatch):
        config_manager.save_preset(sample_config, "keepme_preset")
        dlg = PresetManagementDialog(config_manager)

        for i in range(dlg._preset_list.count()):
            if dlg._preset_list.item(i).text() == "keepme_preset":
                dlg._preset_list.setCurrentRow(i)
                break

        monkeypatch.setattr(
            QMessageBox,
            "question",
            staticmethod(lambda *a, **kw: QMessageBox.StandardButton.No),
        )

        dlg._on_delete()

        preset_path = config_manager.preset_dir / "keepme_preset.xml"
        assert preset_path.exists()
        dlg.deleteLater()


# ---------------------------------------------------------------------------
# Export functionality
# ---------------------------------------------------------------------------


class TestExportPreset:
    def test_export_creates_file(self, app, config_manager, sample_config, tmp_path, monkeypatch):
        config_manager.save_preset(sample_config, "export_test_preset")
        dlg = PresetManagementDialog(config_manager)

        for i in range(dlg._preset_list.count()):
            if dlg._preset_list.item(i).text() == "export_test_preset":
                dlg._preset_list.setCurrentRow(i)
                break

        dest = tmp_path / "exported_preset.xml"

        monkeypatch.setattr(
            "ui.dialogs.preset_management_dialog.QFileDialog.getSaveFileName",
            lambda *a, **kw: (str(dest), "XML Preset Files (*.xml)"),
        )
        monkeypatch.setattr(
            QMessageBox,
            "information",
            staticmethod(lambda *a, **kw: None),
        )

        dlg._on_export()
        assert dest.exists()
        dlg.deleteLater()

    def test_export_cancelled_no_file(self, app, config_manager, sample_config, monkeypatch):
        config_manager.save_preset(sample_config, "export_cancel_preset")
        dlg = PresetManagementDialog(config_manager)

        for i in range(dlg._preset_list.count()):
            if dlg._preset_list.item(i).text() == "export_cancel_preset":
                dlg._preset_list.setCurrentRow(i)
                break

        monkeypatch.setattr(
            "ui.dialogs.preset_management_dialog.QFileDialog.getSaveFileName",
            lambda *a, **kw: ("", ""),
        )

        # Should return without errors
        dlg._on_export()
        dlg.deleteLater()


# ---------------------------------------------------------------------------
# Import functionality
# ---------------------------------------------------------------------------


class TestImportPreset:
    def test_import_valid_preset(self, app, config_manager, sample_config, tmp_path, monkeypatch):
        # Save a preset to a temp file to use as import source
        source_cfg = ConfigManager(preset_dir=tmp_path / "source_presets")
        source_cfg.save_preset(sample_config, "import_source")
        source_file = source_cfg.preset_dir / "import_source.xml"

        dlg = PresetManagementDialog(config_manager)

        monkeypatch.setattr(
            "ui.dialogs.preset_management_dialog.QFileDialog.getOpenFileName",
            lambda *a, **kw: (str(source_file), "XML Preset Files (*.xml)"),
        )
        monkeypatch.setattr(
            QMessageBox,
            "information",
            staticmethod(lambda *a, **kw: None),
        )

        emitted = []
        dlg.presets_changed.connect(lambda: emitted.append(True))
        dlg._on_import()

        dest = config_manager.preset_dir / "import_source.xml"
        assert dest.exists()
        assert emitted, "presets_changed signal was not emitted"
        dlg.deleteLater()

    def test_import_invalid_file_shows_warning(
        self, app, config_manager, tmp_path, monkeypatch
    ):
        bad_file = tmp_path / "bad_preset.xml"
        bad_file.write_text("<not_a_preset/>", encoding="utf-8")

        dlg = PresetManagementDialog(config_manager)

        monkeypatch.setattr(
            "ui.dialogs.preset_management_dialog.QFileDialog.getOpenFileName",
            lambda *a, **kw: (str(bad_file), "XML Preset Files (*.xml)"),
        )

        warnings = []
        monkeypatch.setattr(
            QMessageBox,
            "warning",
            staticmethod(lambda *a, **kw: warnings.append(True)),
        )

        dlg._on_import()
        assert warnings, "Expected a warning dialog for invalid preset"
        dlg.deleteLater()

    def test_import_cancelled_no_change(self, app, config_manager, monkeypatch):
        dlg = PresetManagementDialog(config_manager)
        initial_count = dlg._preset_list.count()

        monkeypatch.setattr(
            "ui.dialogs.preset_management_dialog.QFileDialog.getOpenFileName",
            lambda *a, **kw: ("", ""),
        )

        dlg._on_import()
        assert dlg._preset_list.count() == initial_count
        dlg.deleteLater()

    def test_import_updates_list(self, app, config_manager, sample_config, tmp_path, monkeypatch):
        source_cfg = ConfigManager(preset_dir=tmp_path / "list_update_source")
        source_cfg.save_preset(sample_config, "new_imported_preset")
        source_file = source_cfg.preset_dir / "new_imported_preset.xml"

        dlg = PresetManagementDialog(config_manager)

        monkeypatch.setattr(
            "ui.dialogs.preset_management_dialog.QFileDialog.getOpenFileName",
            lambda *a, **kw: (str(source_file), "XML Preset Files (*.xml)"),
        )
        monkeypatch.setattr(
            QMessageBox,
            "information",
            staticmethod(lambda *a, **kw: None),
        )

        dlg._on_import()

        names = [dlg._preset_list.item(i).text() for i in range(dlg._preset_list.count())]
        assert "new_imported_preset" in names
        dlg.deleteLater()
