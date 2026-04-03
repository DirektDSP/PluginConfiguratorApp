"""Dialog for selecting and loading a preset configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from core.config_manager import ConfigManager


class PresetLoadDialog(QDialog):
    """Dialog that lists available presets and lets the user select one to load."""

    def __init__(self, config_manager: ConfigManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._config_manager = config_manager
        self._selected_preset_name: str | None = None

        self.setWindowTitle("Load Preset")
        self.setMinimumSize(600, 400)
        self.resize(700, 500)

        self._setup_ui()
        self._refresh_preset_list()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def selected_preset_name(self) -> str | None:
        """Return the name of the preset selected when the dialog was accepted."""
        return self._selected_preset_name

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        """Build the dialog layout."""
        main_layout = QHBoxLayout(self)

        # ── Left panel: preset list ────────────────────────────────────
        left_panel = QVBoxLayout()

        presets_group = QGroupBox("Available Presets")
        presets_group_layout = QVBoxLayout(presets_group)

        self._preset_list = QListWidget()
        self._preset_list.setAlternatingRowColors(True)
        self._preset_list.currentRowChanged.connect(self._on_preset_selected)
        self._preset_list.itemDoubleClicked.connect(self._on_load)
        presets_group_layout.addWidget(self._preset_list)

        left_panel.addWidget(presets_group)

        # ── Right panel: metadata display ──────────────────────────────
        right_panel = QVBoxLayout()

        metadata_group = QGroupBox("Preset Details")
        metadata_layout = QVBoxLayout(metadata_group)

        name_header = QLabel("<b>Name</b>")
        self._name_label = QLabel("—")
        self._name_label.setWordWrap(True)
        self._name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        desc_header = QLabel("<b>Description</b>")
        self._desc_text = QTextEdit()
        self._desc_text.setReadOnly(True)
        self._desc_text.setPlaceholderText("No description available.")
        self._desc_text.setMaximumHeight(120)

        metadata_layout.addWidget(name_header)
        metadata_layout.addWidget(self._name_label)
        metadata_layout.addSpacing(4)
        metadata_layout.addWidget(desc_header)
        metadata_layout.addWidget(self._desc_text)
        metadata_layout.addStretch()

        right_panel.addWidget(metadata_group)

        # ── Dialog buttons (Load / Cancel) ─────────────────────────────
        self._button_box = QDialogButtonBox()
        self._load_btn = self._button_box.addButton(
            "Load", QDialogButtonBox.ButtonRole.AcceptRole
        )
        self._load_btn.setEnabled(False)
        self._load_btn.setToolTip("Select a preset to load")
        self._button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        self._button_box.accepted.connect(self._on_load)
        self._button_box.rejected.connect(self.reject)

        right_panel.addWidget(self._button_box)

        # ── Assemble panels ────────────────────────────────────────────
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setMinimumWidth(260)

        right_widget = QWidget()
        right_widget.setLayout(right_panel)

        main_layout.addWidget(left_widget, 2)
        main_layout.addWidget(right_widget, 3)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _refresh_preset_list(self) -> None:
        """Reload the preset list from disk."""
        self._preset_list.clear()
        for preset_name in self._config_manager.get_available_presets():
            self._preset_list.addItem(QListWidgetItem(preset_name))

        if self._preset_list.count() > 0:
            self._preset_list.setCurrentRow(0)

        self._update_load_button()

    def _update_load_button(self) -> None:
        """Enable the Load button only when a preset is selected."""
        has_selection = self._preset_list.currentItem() is not None
        self._load_btn.setEnabled(has_selection)
        if has_selection:
            self._load_btn.setToolTip("Load the selected preset into the configurator")
        else:
            self._load_btn.setToolTip("Select a preset to load")

    def _current_preset_name(self) -> str | None:
        """Return the currently selected preset name, or ``None``."""
        item = self._preset_list.currentItem()
        return item.text() if item is not None else None

    def _load_metadata(self, preset_name: str) -> dict:
        """Return the ``meta`` section of *preset_name*, or an empty dict on error."""
        try:
            config = self._config_manager.load_preset(preset_name)
            meta: dict = config.get("meta", {})
            return meta
        except Exception:
            return {}

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    @Slot(int)
    def _on_preset_selected(self, row: int) -> None:
        """Update the metadata panel when the user selects a preset."""
        self._update_load_button()

        if row < 0:
            self._name_label.setText("—")
            self._desc_text.setPlainText("")
            return

        preset_name = self._current_preset_name()
        if preset_name is None:
            return

        meta = self._load_metadata(preset_name)
        display_name = meta.get("name") or preset_name
        description = meta.get("description", "")

        self._name_label.setText(display_name)
        self._desc_text.setPlainText(description)

    @Slot()
    def _on_load(self) -> None:
        """Accept the dialog with the currently selected preset."""
        preset_name = self._current_preset_name()
        if preset_name is None:
            return
        self._selected_preset_name = preset_name
        self.accept()
