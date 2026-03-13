import xml.etree.ElementTree as ET
from pathlib import Path


class ConfigManager:
    """Manages loading and saving of XML configuration files and presets"""

    def __init__(self):
        """Initialize the ConfigManager with preset directory"""
        # Define preset directory in user's home folder
        self.preset_dir = Path.home() / ".plugin_configurator" / "presets"
        # Ensure preset directory exists
        self.preset_dir.mkdir(parents=True, exist_ok=True)

    def load_config(self, file_path):
        """Load configuration from an XML file

        Args:
            file_path: Path to the XML configuration file

        Returns:
            dict: Dictionary containing configuration values
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Create a dictionary from the XML elements
            config = {}
            for child in root:
                # Handle None values (empty elements)
                text_value = child.text if child.text is not None else ""

                # Handle boolean values (stored as text "True"/"False")
                if text_value.lower() in ["true", "false"]:
                    config[child.tag] = text_value.lower() == "true"
                else:
                    config[child.tag] = text_value

            return config

        except Exception as e:
            raise ValueError(f"Failed to load configuration: {e!s}")

    def save_config(self, config, file_path):
        """Save configuration to an XML file

        Args:
            config: Dictionary containing configuration values
            file_path: Path where to save the XML file
        """
        try:
            root = ET.Element("config")

            # Create XML elements from the dictionary
            for key, value in config.items():
                # Convert value to string
                if isinstance(value, bool):
                    value = str(value)
                elif value is None:
                    value = ""

                element = ET.SubElement(root, key)
                element.text = value

            # Create a pretty XML file
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ")

            tree.write(file_path, encoding="utf-8", xml_declaration=True)

        except Exception as e:
            raise ValueError(f"Failed to save configuration: {e!s}")

    def get_default_config(self):
        """Get a dictionary with default configuration values"""
        return {
            "project_name": "",
            "fork_url": "https://github.com/SeamusMullan/PluginTemplate.git",
            "product_name": "",
            "company_name": "DirektDSP",
            "bundle_id": "",
            "manufacturer_code": "Ddsp",
            "output_directory": "",
            "standalone": False,
            "vst3": True,
            "au": True,
            "auv3": False,
            "clap": True,
            "create_git_repo": True,
            "melatonin": True,
            "moonbase": False,
            "clap_export": True,
            "juce_develop": True,
            "xcode_prettify": True,
            "juce_curl": False,
            "juce_web_browser": False,
            "juce_vst2": False,
        }

    def get_available_presets(self):
        """Get a list of available preset names"""
        presets = []
        for file in self.preset_dir.glob("*.xml"):
            presets.append(file.stem)
        return sorted(presets)

    def save_preset(self, config, preset_name):
        """Save configuration as a preset

        Args:
            config: Dictionary containing configuration values
            preset_name: Name of the preset (without extension)
        """
        preset_path = self.preset_dir / f"{preset_name}.xml"
        self.save_config(config, preset_path)

    def load_preset(self, preset_name):
        """Load configuration from a preset

        Args:
            preset_name: Name of the preset (without extension)

        Returns:
            dict: Dictionary containing configuration values
        """
        preset_path = self.preset_dir / f"{preset_name}.xml"
        return self.load_config(preset_path)

    def delete_preset(self, preset_name):
        """Delete a preset

        Args:
            preset_name: Name of the preset (without extension)

        Returns:
            bool: True if preset was deleted, False otherwise
        """
        preset_path = self.preset_dir / f"{preset_name}.xml"
        try:
            preset_path.unlink()
            return True
        except Exception:
            return False
