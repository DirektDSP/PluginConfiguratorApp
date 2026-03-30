import tempfile
import threading
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from core.config_manager import ConfigManager, ConfigurationManager


class TestConfigurationManager:
    """Test suite for ConfigurationManager singleton"""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset the ConfigurationManager singleton state before each test"""
        ConfigurationManager._instance = None
        yield
        ConfigurationManager._instance = None

    def test_singleton_returns_same_instance(self):
        """Two calls to the constructor must return the identical object"""
        mgr1 = ConfigurationManager()
        mgr2 = ConfigurationManager()
        assert mgr1 is mgr2

    def test_initial_full_config_has_quick_start(self):
        """A freshly created manager returns quick_start=False in full config"""
        mgr = ConfigurationManager()
        config = mgr.get_full_config()
        assert "quick_start" in config
        assert config["quick_start"] is False

    def test_update_config_stores_tab_config(self):
        """update_config should persist the tab's settings"""
        mgr = ConfigurationManager()
        mgr.update_config("project_info", {"project_name": "MyPlugin", "vst3": True})
        config = mgr.get_full_config()
        assert config["project_name"] == "MyPlugin"
        assert config["vst3"] is True

    def test_update_config_overwrites_previous(self):
        """Calling update_config twice for the same tab replaces the entry"""
        mgr = ConfigurationManager()
        mgr.update_config("project_info", {"project_name": "First"})
        mgr.update_config("project_info", {"project_name": "Second"})
        config = mgr.get_full_config()
        assert config["project_name"] == "Second"

    def test_get_full_config_merges_multiple_tabs(self):
        """get_full_config should merge settings from all registered tabs"""
        mgr = ConfigurationManager()
        mgr.update_config("tab_a", {"key_a": "value_a"})
        mgr.update_config("tab_b", {"key_b": "value_b"})
        config = mgr.get_full_config()
        assert config["key_a"] == "value_a"
        assert config["key_b"] == "value_b"

    def test_get_full_config_returns_copy(self):
        """Mutating the returned dict must not affect internal state"""
        mgr = ConfigurationManager()
        mgr.update_config("tab_a", {"key": "original"})
        config = mgr.get_full_config()
        config["key"] = "mutated"
        assert mgr.get_full_config()["key"] == "original"

    def test_toggle_quick_start_flips_flag(self):
        """toggle_quick_start should alternate between True and False"""
        mgr = ConfigurationManager()
        assert mgr.toggle_quick_start() is True
        assert mgr.toggle_quick_start() is False
        assert mgr.toggle_quick_start() is True

    def test_toggle_quick_start_reflected_in_full_config(self):
        """quick_start value in get_full_config must track the toggled state"""
        mgr = ConfigurationManager()
        mgr.toggle_quick_start()
        assert mgr.get_full_config()["quick_start"] is True
        mgr.toggle_quick_start()
        assert mgr.get_full_config()["quick_start"] is False

    def test_validate_all_without_tabs_false_when_empty(self):
        """validate_all() with no arguments returns False when no tab has contributed config"""
        mgr = ConfigurationManager()
        assert mgr.validate_all() is False

    def test_validate_all_without_tabs_true_when_populated(self):
        """validate_all() with no arguments returns True after at least one update_config"""
        mgr = ConfigurationManager()
        mgr.update_config("some_tab", {"key": "value"})
        assert mgr.validate_all() is True

    def test_validate_all_with_valid_tabs(self):
        """validate_all(tabs) returns True when all tab.validate() calls return True"""
        mgr = ConfigurationManager()
        tab1 = MagicMock()
        tab1.validate.return_value = True
        tab2 = MagicMock()
        tab2.validate.return_value = True
        assert mgr.validate_all(tabs=[tab1, tab2]) is True

    def test_validate_all_with_invalid_tab(self):
        """validate_all(tabs) returns False when any tab.validate() returns False"""
        mgr = ConfigurationManager()
        tab1 = MagicMock()
        tab1.validate.return_value = True
        tab2 = MagicMock()
        tab2.validate.return_value = False
        assert mgr.validate_all(tabs=[tab1, tab2]) is False

    def test_thread_safe_update_config(self):
        """Concurrent update_config calls must not corrupt internal state"""
        mgr = ConfigurationManager()
        errors: list[Exception] = []

        def writer(tab: str, val: int) -> None:
            try:
                for i in range(50):
                    mgr.update_config(tab, {"counter": i + val})
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=writer, args=(f"tab_{t}", t * 100)) for t in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        # All 5 tabs must still be present.
        config = mgr.get_full_config()
        assert "counter" in config


class TestConfigManager:
    """Test suite for ConfigManager class"""

    @pytest.fixture
    def temp_preset_dir(self, tmp_path: Path) -> Path:
        return tmp_path / "presets"

    @pytest.fixture
    def config_manager(self, temp_preset_dir):
        """Create a ConfigManager instance"""
        return ConfigManager(preset_dir=temp_preset_dir)

    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for testing"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            temp_path = Path(f.name)
        yield temp_path
        temp_path.unlink(missing_ok=True)

    @pytest.fixture
    def sample_config(self):
        """Sample configuration dict"""
        return {
            "meta": {"name": "SamplePreset", "description": "Testing preset"},
            "project_info": {
                "template_name": "Audio FX Plugin",
                "template_url": "https://github.com/SeamusMullan/PluginTemplate.git",
                "project_name": "MyPlugin",
                "product_name": "My Plugin",
                "version": "1.0.0",
                "company_name": "TestCompany",
                "bundle_id": "com.test.myplugin",
                "manufacturer_code": "TST1",
                "plugin_code": "TST1",
                "output_directory": "/tmp/output",
            },
            "configuration": {
                "standalone": True,
                "vst3": False,
                "au": True,
                "auv3": False,
                "clap": True,
                "gui_width": 900,
                "gui_height": 600,
                "resizable": True,
                "background_image": "",
                "code_signing": False,
                "installer": False,
                "default_bypass": False,
                "input_gain": False,
                "output_gain": True,
            },
            "implementations": {
                "moonbase_licensing": False,
                "melatonin_inspector": True,
                "custom_gui_framework": False,
                "logging_framework": True,
                "clap_builds": True,
                "preset_management": True,
                "preset_format": "XML",
                "ab_comparison": True,
                "state_management": False,
                "gpu_audio": False,
            },
            "user_experience": {
                "wizard": False,
                "preview": False,
                "preset_management": True,
            },
            "development_workflow": {
                "vcs": True,
                "testing": True,
                "code_quality": True,
                "validation_tools": True,
                "scaffolding": True,
            },
        }

    def test_initialization(self, config_manager):
        """Test that ConfigManager initializes correctly"""
        assert config_manager.preset_dir.exists()
        assert config_manager.preset_dir.name == "presets"
        available = set(config_manager.get_available_presets())
        assert set(ConfigManager.BUNDLED_PRESETS) <= available

    def test_get_default_config(self, config_manager):
        """Test that default config is correctly structured"""
        config = config_manager.get_default_config()

        assert isinstance(config, dict)
        for section in ("project_info", "configuration", "implementations", "user_experience", "development_workflow"):
            assert section in config

    def test_save_and_load_config(self, config_manager, temp_file, sample_config):
        """Test saving and loading configuration"""
        config_manager.save_config(sample_config, temp_file)

        assert temp_file.exists()

        loaded_config = config_manager.load_config(temp_file)

        assert loaded_config == sample_config
        assert loaded_config["project_info"]["project_name"] == "MyPlugin"
        assert loaded_config["configuration"]["standalone"] is True
        assert loaded_config["configuration"]["vst3"] is False

    def test_boolean_handling(self, config_manager, temp_file):
        """Test that boolean values are handled correctly"""
        config = config_manager.get_default_config()
        config["project_info"]["project_name"] = "BoolTest"
        config["project_info"]["product_name"] = "BoolTest"
        config["project_info"]["company_name"] = "TestCompany"
        config["project_info"]["bundle_id"] = "com.test.bool"
        config["project_info"]["manufacturer_code"] = "BOOL"
        config["project_info"]["output_directory"] = "/tmp"
        config["configuration"]["standalone"] = True
        config["configuration"]["vst3"] = False

        config_manager.save_config(config, temp_file)
        loaded_config = config_manager.load_config(temp_file)

        assert loaded_config["configuration"]["standalone"] is True
        assert loaded_config["configuration"]["vst3"] is False

    def test_save_preset(self, config_manager, sample_config):
        """Test saving a preset"""
        preset_name = "test_preset"
        config_manager.save_preset(sample_config, preset_name)

        preset_path = config_manager.preset_dir / f"{preset_name}.xml"
        assert preset_path.exists()
        ok, errors = config_manager.validate_preset_file(preset_path)
        assert ok, errors

        preset_path.unlink(missing_ok=True)

    def test_load_preset(self, config_manager, sample_config):
        """Test loading a preset"""
        preset_name = "test_preset"
        config_manager.save_preset(sample_config, preset_name)

        loaded_config = config_manager.load_preset(preset_name)

        assert loaded_config == sample_config
        assert loaded_config["project_info"]["project_name"] == "MyPlugin"

        preset_path = config_manager.preset_dir / f"{preset_name}.xml"
        preset_path.unlink(missing_ok=True)

    def test_delete_preset(self, config_manager, sample_config):
        """Test deleting a preset"""
        preset_name = "test_preset"
        config_manager.save_preset(sample_config, preset_name)

        preset_path = config_manager.preset_dir / f"{preset_name}.xml"
        assert preset_path.exists()

        result = config_manager.delete_preset(preset_name)

        assert result is True
        assert not preset_path.exists()

    def test_delete_nonexistent_preset(self, config_manager):
        """Test deleting a nonexistent preset"""
        result = config_manager.delete_preset("nonexistent_preset")
        assert result is False

    def test_get_available_presets(self, config_manager, sample_config):
        """Test getting list of available presets"""
        preset_names = ["preset_a", "preset_b", "preset_c"]

        for name in preset_names:
            config_manager.save_preset(sample_config, name)

        presets = config_manager.get_available_presets()

        assert "preset_a" in presets
        assert "preset_b" in presets
        assert "preset_c" in presets
        assert len(presets) >= 3

        for name in preset_names:
            preset_path = config_manager.preset_dir / f"{name}.xml"
            preset_path.unlink(missing_ok=True)

    def test_save_config_creates_valid_xml(self, config_manager, temp_file, sample_config):
        """Test that saved XML is valid and well-formed"""
        config_manager.save_config(sample_config, temp_file)

        tree = ET.parse(temp_file)
        root = tree.getroot()

        assert root.tag == "preset"
        assert {c.tag for c in root} & {"project_info", "configuration", "implementations"}

    def test_load_invalid_file(self, config_manager, temp_file):
        """Test loading an invalid XML file"""
        with open(temp_file, "w") as f:
            f.write("invalid xml content")

        with pytest.raises(ValueError, match="Failed to load configuration"):
            config_manager.load_config(temp_file)

    def test_empty_config(self, config_manager, temp_file):
        """Test saving and loading empty config"""
        config = {}

        config_manager.save_config(config, temp_file)
        loaded_config = config_manager.load_config(temp_file)

        assert loaded_config == {}

    def test_config_with_special_characters(self, config_manager, temp_file):
        """Test config with special characters in values"""
        config = config_manager.get_default_config()
        config["project_info"].update(
            {
                "project_name": "Plugin <test>",
                "product_name": "Product & More",
                "company_name": 'My "Company" Ltd.',
                "bundle_id": "com.example.special",
                "manufacturer_code": "SPCL",
                "output_directory": "/tmp",
            }
        )

        config_manager.save_config(config, temp_file)
        loaded_config = config_manager.load_config(temp_file)

        assert loaded_config["project_info"]["project_name"] == "Plugin <test>"
        assert loaded_config["project_info"]["product_name"] == "Product & More"
        assert loaded_config["project_info"]["company_name"] == 'My "Company" Ltd.'

    def test_bundled_presets_validate(self, config_manager):
        """Bundled presets should pass schema validation"""
        for preset in ConfigManager.BUNDLED_PRESETS:
            ok, errors = config_manager.validate_preset_file(
                config_manager.preset_dir / f"{preset}.xml"
            )
            assert ok, f"{preset} failed validation: {errors}"
