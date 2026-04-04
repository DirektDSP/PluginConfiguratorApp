"""Dialog for capturing a preset name and optional description before saving."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class SavePresetDialog(QDialog):
    """Prompt the user for a preset name (required) and optional description."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Save as Preset")
        self.setMinimumWidth(380)
        self._setup_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        """Build the dialog layout."""
        outer = QVBoxLayout(self)

        form = QFormLayout()
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("e.g. My Audio FX Preset")
        self._name_edit.setMaxLength(128)
        form.addRow("Preset Name *", self._name_edit)

        self._desc_edit = QTextEdit()
        self._desc_edit.setPlaceholderText("Optional description…")
        self._desc_edit.setFixedHeight(80)
        form.addRow("Description", self._desc_edit)

        self._error_label = QLabel()
        self._error_label.setStyleSheet("color: red;")
        self._error_label.setVisible(False)

        outer.addLayout(form)
        outer.addWidget(self._error_label)

        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._button_box.accepted.connect(self._on_accept)
        self._button_box.rejected.connect(self.reject)
        outer.addWidget(self._button_box)

        # Keep OK enabled; validate on accept instead of live to keep it simple.
        self._name_edit.textChanged.connect(self._clear_error)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def preset_name(self) -> str:
        """Return the trimmed preset name entered by the user."""
        return self._name_edit.text().strip()

    def description(self) -> str:
        """Return the trimmed description entered by the user."""
        return self._desc_edit.toPlainText().strip()

    # ------------------------------------------------------------------
    # Private slots
    # ------------------------------------------------------------------

    def _on_accept(self) -> None:
        """Validate the name field before accepting the dialog."""
        if not self._name_edit.text().strip():
            self._error_label.setText("Preset name cannot be empty.")
            self._error_label.setVisible(True)
            self._name_edit.setFocus()
            return
        self.accept()

    def _clear_error(self) -> None:
        self._error_label.setVisible(False)
