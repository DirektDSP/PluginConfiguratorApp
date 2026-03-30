from __future__ import annotations

import threading
import xml.etree.ElementTree as ET
from copy import deepcopy
from pathlib import Path
from typing import Any, ClassVar, Mapping


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

    # Stored with file stems to mirror the shipped preset filenames.
    BUNDLED_PRESETS: ClassVar[tuple[str, ...]] = (
        "StandardAudioFX_Preset",
        "Instrument_Preset",
        "MinimalPlugin_Preset",
    )
    PRESET_SCHEMA: ClassVar[dict[str, dict[str, dict[str, Any]]]] = {
        "project_info": {
            "template_name": {"type": str, "default": "Internal DirektDSP Template"},
            "template_url": {
                "type": str,
                "default": "https://github.com/SeamusMullan/PluginTemplate.git",
            },
            "project_name": {"type": str, "default": "", "required": True},
            "product_name": {"type": str, "default": "", "required": True},
            "version": {"type": str, "default": "1.0.0"},
            "company_name": {"type": str, "default": "DirektDSP", "required": True},
            "bundle_id": {"type": str, "default": "", "required": True},
            "manufacturer_code": {"type": str, "default": "Ddsp", "required": True},
            "plugin_code": {"type": str, "default": ""},
            "output_directory": {"type": str, "default": "", "required": True},
        },
        "configuration": {
            "standalone": {"type": bool, "default": False},
            "vst3": {"type": bool, "default": True},
            "au": {"type": bool, "default": True},
            "auv3": {"type": bool, "default": False},
            "clap": {"type": bool, "default": True},
            "gui_width": {"type": int, "default": 800},
            "gui_height": {"type": int, "default": 600},
            "resizable": {"type": bool, "default": False},
            "background_image": {"type": str, "default": ""},
            "code_signing": {"type": bool, "default": False},
            "installer": {"type": bool, "default": False},
            "default_bypass": {"type": bool, "default": False},
            "input_gain": {"type": bool, "default": False},
            "output_gain": {"type": bool, "default": False},
        },
        "implementations": {
            "moonbase_licensing": {"type": bool, "default": False},
            "melatonin_inspector": {"type": bool, "default": False},
            "custom_gui_framework": {"type": bool, "default": False},
            "logging_framework": {"type": bool, "default": False},
            "clap_builds": {"type": bool, "default": False},
            "preset_management": {"type": bool, "default": False},
            "preset_format": {"type": str, "default": ""},
            "ab_comparison": {"type": bool, "default": False},
            "state_management": {"type": bool, "default": False},
            "gpu_audio": {"type": bool, "default": False},
        },
        "user_experience": {
            "wizard": {"type": bool, "default": False},
            "preview": {"type": bool, "default": False},
            "preset_management": {"type": bool, "default": False},
        },
        "development_workflow": {
            "vcs": {"type": bool, "default": False},
            "testing": {"type": bool, "default": False},
            "code_quality": {"type": bool, "default": False},
            "validation_tools": {"type": bool, "default": False},
            "scaffolding": {"type": bool, "default": False},
        },
    }

    META_FIELDS: ClassVar[dict[str, dict[str, Any]]] = {
        "name": {"type": str, "default": ""},
        "description": {"type": str, "default": ""},
    }

    def __init__(self, preset_dir: Path | None = None):
        """Initialize the ConfigManager with preset directory"""
        self.preset_dir = preset_dir or Path.home() / ".plugin_configurator" / "presets"
        self.example_presets_dir = Path(__file__).resolve().parents[1] / "resources" / "presets"
        self.preset_dir.mkdir(parents=True, exist_ok=True)
        self._install_bundled_presets()

    def load_config(self, file_path: Path | str) -> dict:
        """Load configuration from an XML file

        Args:
            file_path: Path to the XML configuration file

        Returns:
            dict: Dictionary containing configuration values
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            if root.tag == "preset":
                return self._load_structured_preset(root, Path(file_path))
            return self._load_flat_config(root)
        except Exception as e:
            raise ValueError(f"Failed to load configuration: {e!s}")

    def save_config(self, config: Mapping[str, Any], file_path: Path | str) -> None:
        """Save configuration to an XML file

        Args:
            config: Dictionary containing configuration values
            file_path: Path where to save the XML file
        """
        try:
            file_path = Path(file_path)
            if self._looks_structured(config):
                self._save_structured_config(config, file_path)
            else:
                self._save_flat_config(config, file_path)
        except Exception as e:
            raise ValueError(f"Failed to save configuration: {e!s}")

    def get_default_config(self) -> dict:
        """Get a dictionary with default configuration values"""
        return self._apply_defaults({})

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
        config_with_defaults = self._apply_defaults(config)
        errors = self.validate_config(config_with_defaults)
        if errors:
            raise ValueError(f"Preset validation failed: {', '.join(errors)}")
        self.save_config(config_with_defaults, preset_path)

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

    def validate_preset_file(self, file_path: Path | str) -> tuple[bool, list[str]]:
        """Validate a preset file against the schema."""
        try:
            config = self.load_config(file_path)
        except ValueError as exc:
            return False, [str(exc)]
        errors = self.validate_config(config)
        return (not errors, errors)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _install_bundled_presets(self) -> None:
        """Copy shipped presets into the user preset directory if they are missing."""
        if not self.example_presets_dir.exists():
            return
        for preset_name in self.BUNDLED_PRESETS:
            preset_file = self.example_presets_dir / f"{preset_name}.xml"
            if not preset_file.exists():
                continue
            target = self.preset_dir / preset_file.name
            if not target.exists():
                target.write_text(preset_file.read_text(encoding="utf-8"), encoding="utf-8")

    def _apply_defaults(self, config: Mapping[str, Any]) -> dict:
        meta_source = config.get("meta", {})
        meta: dict[str, Any] = {}
        for key, meta_def in self.META_FIELDS.items():
            meta[key] = meta_source.get(key, meta_def["default"])

        result: dict[str, Any] = {"meta": meta}
        for section, fields in self.PRESET_SCHEMA.items():
            section_data = config.get(section, {})
            result[section] = {}
            for field, meta_info in fields.items():
                result[section][field] = section_data.get(field, meta_info["default"])
        return result

    def validate_config(self, config: Mapping[str, Any]) -> list[str]:
        errors: list[str] = []
        for section, fields in self.PRESET_SCHEMA.items():
            if section not in config:
                errors.append(f"Missing section '{section}'")
                continue
            section_data = config[section]
            if not isinstance(section_data, Mapping):
                errors.append(f"Section '{section}' must be a mapping")
                continue
            for field, meta_info in fields.items():
                if field not in section_data:
                    errors.append(f"Missing field '{section}.{field}'")
                    continue
                value = section_data[field]
                if value is None:
                    if meta_info.get("required"):
                        errors.append(f"Field '{section}.{field}' is required")
                    continue
                expected_type = meta_info["type"]
                if not self._matches_type(value, expected_type):
                    errors.append(
                        f"Field '{section}.{field}' must be a {expected_type.__name__}"
                    )
                if meta_info.get("required") and isinstance(value, str) and not value.strip():
                    errors.append(f"Field '{section}.{field}' cannot be empty")
        return errors

    def _coerce_value(self, value: str | None, expected_type: type, default: Any) -> Any:
        """Convert a string value from XML into the expected Python type."""
        if value is None:
            return default
        value = value.strip()
        if expected_type is bool:
            # Accept common truthy tokens to stay resilient to hand-edited presets; save operations emit
            # canonical "true"/"false".
            return value.lower() in {"true", "1", "yes", "on"}
        if expected_type is int:
            try:
                return int(value)
            except ValueError:
                return default
        return value

    def _load_structured_preset(self, root: ET.Element, file_path: Path) -> dict:
        config: dict[str, Any] = {"meta": {"name": root.attrib.get("name", file_path.stem)}}

        meta_element = root.find("meta")
        if meta_element is not None:
            for key, meta_def in self.META_FIELDS.items():
                elem = meta_element.find(key)
                if elem is not None and elem.text is not None:
                    config["meta"][key] = elem.text
                elif key not in config["meta"]:
                    config["meta"][key] = meta_def["default"]

        for section, fields in self.PRESET_SCHEMA.items():
            section_elem = root.find(section)
            section_data: dict[str, Any] = {}
            for field, meta_info in fields.items():
                value_elem = section_elem.find(field) if section_elem is not None else None
                section_data[field] = self._coerce_value(
                    value_elem.text if value_elem is not None else None,
                    meta_info["type"],
                    meta_info["default"],
                )
            config[section] = section_data

        config = self._apply_defaults(config)
        errors = self.validate_config(config)
        if errors:
            raise ValueError(f"Invalid preset: {', '.join(errors)}")
        return config

    def _load_flat_config(self, root: ET.Element) -> dict:
        config: dict[str, Any] = {}
        for child in root:
            text_value = child.text if child.text is not None else ""
            if text_value.lower() in ["true", "false"]:
                config[child.tag] = text_value.lower() == "true"
            else:
                config[child.tag] = text_value
        return config

    def _matches_type(self, value: Any, expected_type: type) -> bool:
        if expected_type is bool:
            return isinstance(value, bool)
        if expected_type is int:
            # bool is a subclass of int in Python, so explicitly exclude booleans.
            return isinstance(value, int) and not isinstance(value, bool)
        if expected_type is str:
            return isinstance(value, str)
        # Future-proofing for potential new field types.
        return isinstance(value, expected_type)

    def _save_structured_config(self, config: Mapping[str, Any], file_path: Path) -> None:
        config_with_defaults = self._apply_defaults(config)
        errors = self.validate_config(config_with_defaults)
        if errors:
            raise ValueError(f"Preset validation failed: {', '.join(errors)}")

        root = ET.Element("preset")
        meta = config_with_defaults.get("meta", {})
        if meta.get("name"):
            root.set("name", str(meta.get("name")))
        if meta.get("description"):
            meta_elem = ET.SubElement(root, "meta")
            desc_elem = ET.SubElement(meta_elem, "description")
            desc_elem.text = str(meta.get("description", ""))

        for section, fields in self.PRESET_SCHEMA.items():
            section_elem = ET.SubElement(root, section)
            section_data = config_with_defaults.get(section, {})
            for field, meta_info in fields.items():
                element = ET.SubElement(section_elem, field)
                value = section_data.get(field, meta_info["default"])
                if isinstance(value, bool):
                    element.text = "true" if value else "false"
                elif value is None:
                    element.text = ""
                else:
                    element.text = str(value)

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        tree.write(file_path, encoding="utf-8", xml_declaration=True)

    def _save_flat_config(self, config: Mapping[str, Any], file_path: Path) -> None:
        root = ET.Element("config")
        for key, value in config.items():
            if isinstance(value, bool):
                value = str(value)
            elif value is None:
                value = ""
            element = ET.SubElement(root, key)
            element.text = value

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        tree.write(file_path, encoding="utf-8", xml_declaration=True)

    def _looks_structured(self, config: Mapping[str, Any]) -> bool:
        return isinstance(config, Mapping) and all(
            section in config for section in self.PRESET_SCHEMA
        )
