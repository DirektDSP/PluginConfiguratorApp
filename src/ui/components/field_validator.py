"""Visual field-validation helper for PySide6 form fields.

Usage
-----
Attach a :class:`FieldValidator` to any ``QLineEdit`` together with a
``QLabel`` that lives below the field in the same layout.  The helper
connects to the field's ``textChanged`` signal, runs the supplied
validation function, and updates both the label and the field's border
color in real time.

Example::

    self.project_name = QLineEdit()
    self._project_name_error = _make_error_label()

    FieldValidator(
        field=self.project_name,
        error_label=self._project_name_error,
        validate_fn=validate_project_name,
    )
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QLabel, QLineEdit

if TYPE_CHECKING:
    from collections.abc import Callable

# Stylesheet templates applied to the QLineEdit
_STYLE_VALID = "QLineEdit { border: 1.5px solid #4CAF50; border-radius: 4px; padding-right: 24px; }"
_STYLE_INVALID = (
    "QLineEdit { border: 1.5px solid #F44336; border-radius: 4px; padding-right: 24px; }"
)
_STYLE_NEUTRAL = ""

# Unicode indicators placed at the end of the placeholder text aren't
# visible enough; instead we show them inside the error label.
_INDICATOR_VALID = "\u2713"
_INDICATOR_INVALID = "\u2717"

# Error-label stylesheet
_ERROR_LABEL_STYLE = "color: #F44336; font-size: 11px;"
_OK_LABEL_STYLE = "color: #4CAF50; font-size: 11px;"


def make_error_label() -> QLabel:
    """Create a pre-styled error/status label suitable for inline display."""
    label = QLabel()
    label.setStyleSheet(_ERROR_LABEL_STYLE)
    label.setVisible(False)
    label.setWordWrap(True)
    return label


class FieldValidator:
    """Attach real-time validation and visual feedback to a ``QLineEdit``.

    Parameters
    ----------
    field:
        The ``QLineEdit`` to validate.
    error_label:
        A ``QLabel`` positioned below *field* in the same layout.  It is
        shown/hidden automatically.
    validate_fn:
        A callable that accepts the field text (``str``) and returns a
        ``tuple[bool, str]`` where the bool indicates validity and the
        string is the error message (empty when valid).
    validate_on_empty:
        When ``False`` (default) the validator treats an untouched empty
        field as *neutral* - no red border, no error label - until the
        user has typed at least one character and then cleared the field.
        Set to ``True`` to validate immediately even when empty.
    """

    def __init__(
        self,
        field: QLineEdit,
        error_label: QLabel,
        validate_fn: Callable[[str], tuple[bool, str]],
        *,
        validate_on_empty: bool = False,
    ) -> None:
        self._field = field
        self._error_label = error_label
        self._validate_fn = validate_fn
        self._validate_on_empty = validate_on_empty
        self._touched = False  # becomes True after the user first types

        field.textChanged.connect(self._on_text_changed)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def trigger_validation(self) -> bool:
        """Run validation using the current field text and show feedback.

        Unlike :meth:`revalidate`, this respects the *neutral* state: an
        untouched empty field is left without feedback unless
        ``validate_on_empty`` was set to ``True``.
        """
        self._on_text_changed(self._field.text())
        return self.is_valid

    def revalidate(self) -> bool:
        """Force a validation run and return whether the field is valid.

        Calling this treats the field as *touched* so red feedback is
        shown even when empty.
        """
        self._touched = True
        return self._run(self._field.text())

    @property
    def is_valid(self) -> bool:
        """Return whether the current field value passes validation."""
        valid, _ = self._validate_fn(self._field.text())
        return valid

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _on_text_changed(self, text: str) -> None:
        if text:
            self._touched = True
        if not self._touched and not self._validate_on_empty:
            # Neutral state - don't show any feedback yet
            self._field.setStyleSheet(_STYLE_NEUTRAL)
            self._error_label.setVisible(False)
            return
        self._run(text)

    def _run(self, text: str) -> bool:
        valid, message = self._validate_fn(text)
        if valid:
            self._field.setStyleSheet(_STYLE_VALID)
            self._error_label.setStyleSheet(_OK_LABEL_STYLE)
            self._error_label.setText(_INDICATOR_VALID)
            self._error_label.setVisible(True)
        else:
            self._field.setStyleSheet(_STYLE_INVALID)
            self._error_label.setStyleSheet(_ERROR_LABEL_STYLE)
            self._error_label.setText(f"{_INDICATOR_INVALID} {message}")
            self._error_label.setVisible(True)
        return valid
