"""XSD-based validation utilities for preset XML files.

This module provides :class:`PresetXSDValidator`, which validates preset XML
files and strings against the formal ``preset_schema.xsd`` W3C schema bundled
with the application.  It requires the ``lxml`` library.

Typical usage::

    from core.preset_validator import PresetXSDValidator

    validator = PresetXSDValidator()

    ok, errors = validator.validate_file("path/to/preset.xml")
    if not ok:
        print("\\n".join(errors))

    ok, errors = validator.validate_string(xml_content)
"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from lxml import etree


class PresetXSDValidator:
    """Validates preset XML files against the bundled XSD schema.

    The compiled :class:`lxml.etree.XMLSchema` object is cached on the class so
    that the schema file is parsed only once per interpreter session.

    Attributes:
        SCHEMA_VERSION: The preset schema version this validator understands.
        XSD_PATH: Absolute path to the bundled ``preset_schema.xsd`` file.
    """

    SCHEMA_VERSION: ClassVar[str] = "1.0"
    XSD_PATH: ClassVar[Path] = (
        Path(__file__).resolve().parents[1] / "resources" / "presets" / "preset_schema.xsd"
    )

    _schema: ClassVar[etree.XMLSchema | None] = None

    # ------------------------------------------------------------------
    # Construction / schema loading
    # ------------------------------------------------------------------

    @classmethod
    def _get_schema(cls) -> etree.XMLSchema:
        """Return the compiled XMLSchema, loading it on first access."""
        if cls._schema is None:
            schema_doc = etree.parse(str(cls.XSD_PATH))
            cls._schema = etree.XMLSchema(schema_doc)
        return cls._schema

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate_file(self, file_path: Path | str) -> tuple[bool, list[str]]:
        """Validate a preset XML file against the XSD schema.

        Args:
            file_path: Path to the XML preset file to validate.

        Returns:
            A ``(is_valid, errors)`` tuple.  *errors* is an empty list when
            *is_valid* is ``True``.
        """
        try:
            doc = etree.parse(str(file_path))
        except etree.XMLSyntaxError as exc:
            return False, [f"XML syntax error: {exc}"]
        except OSError as exc:
            return False, [f"Cannot read file: {exc}"]
        return self._validate_doc(doc)

    def validate_string(self, xml_content: str) -> tuple[bool, list[str]]:
        """Validate an XML string against the XSD schema.

        Args:
            xml_content: XML text to validate.

        Returns:
            A ``(is_valid, errors)`` tuple.  *errors* is an empty list when
            *is_valid* is ``True``.
        """
        try:
            doc = etree.fromstring(xml_content.encode())
        except etree.XMLSyntaxError as exc:
            return False, [f"XML syntax error: {exc}"]
        return self._validate_doc(etree.ElementTree(doc))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_doc(self, doc: etree._ElementTree) -> tuple[bool, list[str]]:  # type: ignore[name-defined]
        """Run the schema against a parsed lxml document tree."""
        schema = self._get_schema()
        is_valid = schema.validate(doc)
        errors = [str(err) for err in schema.error_log]
        return is_valid, errors
