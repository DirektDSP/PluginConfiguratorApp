"""Field validation utilities for the PluginConfiguratorApp.

Each validator returns a ``(is_valid: bool, error_message: str)`` tuple.
``error_message`` is an empty string when ``is_valid`` is ``True``.
"""

from __future__ import annotations

import re


def validate_project_name(name: str) -> tuple[bool, str]:
    """Validate a project name.

    Rules:
    - Must not be empty.
    - Must not contain whitespace.
    - May only contain letters, digits, hyphens, and underscores.
    """
    stripped = name.strip()
    if not stripped:
        return False, "Project name is required."
    if re.search(r"\s", stripped):
        return False, "Project name must not contain spaces."
    if not re.match(r"^[A-Za-z0-9_-]+$", stripped):
        return False, "Only letters, digits, hyphens, and underscores are allowed."
    return True, ""


def validate_product_name(name: str) -> tuple[bool, str]:
    """Validate a product / display name.

    Rules:
    - Must not be empty.
    """
    if not name.strip():
        return False, "Product name is required."
    return True, ""


def validate_company_name(name: str) -> tuple[bool, str]:
    """Validate a company name.

    Rules:
    - Must not be empty.
    """
    if not name.strip():
        return False, "Company name is required."
    return True, ""


def validate_bundle_id(bundle_id: str) -> tuple[bool, str]:
    """Validate a bundle ID.

    Rules:
    - Must not be empty.
    - Must follow reverse-domain notation: at least three dot-separated
      segments, each starting with a letter and containing only
      alphanumeric characters, hyphens, or underscores.

    Examples of valid IDs: ``com.company.plugin``, ``com.my-company.MyPlugin``
    """
    stripped = bundle_id.strip()
    if not stripped:
        return False, "Bundle ID is required."
    pattern = r"^[A-Za-z][A-Za-z0-9_-]*(\.[A-Za-z][A-Za-z0-9_-]*){2,}$"
    if not re.match(pattern, stripped):
        return False, "Use reverse-domain notation, e.g. com.company.plugin."
    return True, ""


def validate_manufacturer_code(code: str) -> tuple[bool, str]:
    """Validate a JUCE manufacturer code.

    Rules:
    - Must not be empty.
    - Must be exactly 4 characters long.
    """
    stripped = code.strip()
    if not stripped:
        return False, "Manufacturer code is required."
    if len(stripped) != 4:
        return False, f"Must be exactly 4 characters (currently {len(stripped)})."
    return True, ""


def validate_plugin_code(code: str) -> tuple[bool, str]:
    """Validate an optional JUCE plugin code.

    Rules:
    - May be empty (will be auto-generated on export).
    - If provided, must be at most 4 characters.
    - If provided, first character must be an uppercase letter.
    """
    stripped = code.strip()
    if not stripped:
        return True, ""  # Auto-generation is acceptable
    if len(stripped) > 4:
        return False, "Plugin code must be at most 4 characters."
    if not stripped[0].isupper():
        return False, "Plugin code must start with a capital letter."
    return True, ""


def validate_version(version: str) -> tuple[bool, str]:
    """Validate a semantic version string.

    Rules:
    - Must not be empty.
    - Must match ``MAJOR.MINOR.PATCH`` format (all numeric).
    """
    stripped = version.strip()
    if not stripped:
        return False, "Version is required."
    if not re.match(r"^\d+\.\d+\.\d+$", stripped):
        return False, "Use semantic versioning, e.g. 1.0.0."
    return True, ""


def validate_output_directory(path: str) -> tuple[bool, str]:
    """Validate an output directory path.

    Rules:
    - Must not be empty.
    """
    if not path.strip():
        return False, "Output directory is required."
    return True, ""
