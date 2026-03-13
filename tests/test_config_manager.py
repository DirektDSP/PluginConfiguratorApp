import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from core.config_manager import ConfigManager


class TestConfigManager:
    """Test suite for ConfigManager class"""

    @pytest.fixture
    def config_manager(self):
        """Create a ConfigManager instance"""
        return ConfigManager()

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
            "project_name": "MyPlugin",
            "product_name": "My Plugin",
            "company_name": "TestCompany",
            "standalone": True,
            "vst3": False,
            "au": True,
        }

    def test_initialization(self, config_manager):
        """Test that ConfigManager initializes correctly"""
        assert config_manager.preset_dir.exists()
        assert config_manager.preset_dir.name == "presets"

    def test_get_default_config(self, config_manager):
        """Test that default config is correctly structured"""
        config = config_manager.get_default_config()

        assert isinstance(config, dict)
        assert "project_name" in config
        assert "product_name" in config
        assert "company_name" in config
        assert "bundle_id" in config
        assert "standalone" in config
        assert "vst3" in config
        assert "au" in config

    def test_save_and_load_config(self, config_manager, temp_file, sample_config):
        """Test saving and loading configuration"""
        config_manager.save_config(sample_config, temp_file)

        assert temp_file.exists()

        loaded_config = config_manager.load_config(temp_file)

        assert loaded_config == sample_config
        assert loaded_config["project_name"] == "MyPlugin"
        assert loaded_config["standalone"] is True
        assert loaded_config["vst3"] is False

    def test_boolean_handling(self, config_manager, temp_file):
        """Test that boolean values are handled correctly"""
        config = {"true_value": True, "false_value": False, "string_value": "test"}

        config_manager.save_config(config, temp_file)
        loaded_config = config_manager.load_config(temp_file)

        assert loaded_config["true_value"] is True
        assert loaded_config["false_value"] is False
        assert loaded_config["string_value"] == "test"

    def test_none_handling(self, config_manager, temp_file):
        """Test that None values are handled correctly"""
        config = {"none_value": None, "normal_value": "test"}

        config_manager.save_config(config, temp_file)
        loaded_config = config_manager.load_config(temp_file)

        assert loaded_config["none_value"] == ""
        assert loaded_config["normal_value"] == "test"

    def test_save_preset(self, config_manager, sample_config):
        """Test saving a preset"""
        preset_name = "test_preset"
        config_manager.save_preset(sample_config, preset_name)

        preset_path = config_manager.preset_dir / f"{preset_name}.xml"
        assert preset_path.exists()

        preset_path.unlink(missing_ok=True)

    def test_load_preset(self, config_manager, sample_config):
        """Test loading a preset"""
        preset_name = "test_preset"
        config_manager.save_preset(sample_config, preset_name)

        loaded_config = config_manager.load_preset(preset_name)

        assert loaded_config == sample_config
        assert loaded_config["project_name"] == "MyPlugin"

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

        assert root.tag == "config"
        assert len(list(root)) == len(sample_config)

        for child in root:
            assert child.tag in sample_config

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
        config = {
            "project_name": "Plugin <test>",
            "description": "Description & more",
            "company": 'My "Company" Ltd.',
        }

        config_manager.save_config(config, temp_file)
        loaded_config = config_manager.load_config(temp_file)

        assert loaded_config == config
        assert loaded_config["project_name"] == "Plugin <test>"
        assert loaded_config["description"] == "Description & more"
