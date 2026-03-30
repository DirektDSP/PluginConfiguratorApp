import threading
import xml.etree.ElementTree as ET
from copy import deepcopy
from pathlib import Path


class ConfigurationManager:
    """Singleton for centralized, thread-safe configuration management across all tabs.

    Stores configuration contributed by each tab, exposes the merged full config,
    and provides helpers for quick-start toggling and full validation.
    """

    _instance: "ConfigurationManager | None" = None
    _instance_lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "ConfigurationManager":
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._initialized = False
                    cls._instance = instance
        return cls._instance

    def __init__(self) -> None:
        # Guard against re-initialisation when the singleton already exists.
        if self._initialized:
            return
        with self._instance_lock:
            if self._initialized:
                return
            self._config: dict[str, dict] = {}
            self._quick_start: bool = False
            self._data_lock: threading.Lock = threading.Lock()
            self._initialized: bool = True

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update_config(self, tab_name: str, config: dict) -> None:
        """Store (or replace) configuration contributed by *tab_name*.

        Args:
            tab_name: Unique identifier for the tab (e.g. ``"project_info"``).
            config: Configuration dictionary emitted by the tab.
        """
        with self._data_lock:
            self._config[tab_name] = deepcopy(config)

    def get_full_config(self) -> dict:
        """Return the merged configuration from all registered tabs.

        Tab configs are merged in insertion order; later tabs override earlier
        ones for duplicate keys.  The ``quick_start`` flag is always included.

        Returns:
            dict: Merged configuration plus the ``quick_start`` flag.
        """
        with self._data_lock:
            full_config: dict = {}
            for tab_config in self._config.values():
                full_config.update(tab_config)
            full_config["quick_start"] = self._quick_start
            return full_config

    def toggle_quick_start(self) -> bool:
        """Toggle the quick-start mode flag.

        Returns:
            bool: The new value of the ``quick_start`` flag.
        """
        with self._data_lock:
            self._quick_start = not self._quick_start
            return self._quick_start

    def set_quick_start(self, enabled: bool) -> bool:
        """Explicitly set the quick-start flag.

        Args:
            enabled: Desired quick-start state.

        Returns:
            bool: The value that was set.
        """
        with self._data_lock:
            self._quick_start = bool(enabled)
            return self._quick_start

    def validate_all(self, tabs: list | None = None) -> bool:
        """Validate configuration across all tabs.

        When *tabs* is provided each element must expose a ``validate()``
        method (i.e. be a :class:`~core.base_tab.BaseTab` instance).  All tabs
        must pass validation for this method to return ``True``.

        When *tabs* is ``None`` the method returns ``True`` only if at least
        one tab has already contributed configuration via
        :meth:`update_config`.

        Args:
            tabs: Optional sequence of :class:`~core.base_tab.BaseTab`
                instances to validate.

        Returns:
            bool: ``True`` if all validations pass, ``False`` otherwise.
        """
        if tabs is not None:
            return all(tab.validate() for tab in tabs)
        with self._data_lock:
            return bool(self._config)


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
