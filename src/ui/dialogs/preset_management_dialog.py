"""Preset management dialog for the Plugin Configurator application."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from core.config_manager import ConfigManager


class PresetManagementDialog(QDialog):
    """Dialog for managing presets: view metadata, delete, export, and import."""

    #: Emitted after any change that modifies the set of available presets.
    presets_changed = Signal()

    def __init__(self, config_manager: ConfigManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._config_manager = config_manager

        self.setWindowTitle("Manage Presets")
        self.setMinimumSize(600, 400)
        self.resize(700, 500)

        self._setup_ui()
        self._refresh_preset_list()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        """Build the dialog layout."""
        main_layout = QHBoxLayout(self)

        # ── Left panel: preset list + action buttons ──────────────────
        left_panel = QVBoxLayout()

        presets_group = QGroupBox("Available Presets")
        presets_group_layout = QVBoxLayout(presets_group)

        self._preset_list = QListWidget()
        self._preset_list.setAlternatingRowColors(True)
        self._preset_list.currentRowChanged.connect(self._on_preset_selected)
        presets_group_layout.addWidget(self._preset_list)

        left_panel.addWidget(presets_group)

        # Action buttons below the list
        btn_layout = QHBoxLayout()

        self._delete_btn = QPushButton("Delete")
        self._delete_btn.setEnabled(False)
        self._delete_btn.setToolTip("Delete the selected preset")
        self._delete_btn.clicked.connect(self._on_delete)

        self._export_btn = QPushButton("Export…")
        self._export_btn.setEnabled(False)
        self._export_btn.setToolTip("Export the selected preset to a file")
        self._export_btn.clicked.connect(self._on_export)

        self._import_btn = QPushButton("Import…")
        self._import_btn.setToolTip("Import a preset from a file")
        self._import_btn.clicked.connect(self._on_import)

        btn_layout.addWidget(self._delete_btn)
        btn_layout.addWidget(self._export_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self._import_btn)

        left_panel.addLayout(btn_layout)

        # ── Right panel: metadata display ─────────────────────────────
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

        file_header = QLabel("<b>File</b>")
        self._file_label = QLabel("—")
        self._file_label.setWordWrap(True)
        self._file_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        metadata_layout.addWidget(name_header)
        metadata_layout.addWidget(self._name_label)
        metadata_layout.addSpacing(4)
        metadata_layout.addWidget(desc_header)
        metadata_layout.addWidget(self._desc_text)
        metadata_layout.addSpacing(4)
        metadata_layout.addWidget(file_header)
        metadata_layout.addWidget(self._file_label)
        metadata_layout.addStretch()

        right_panel.addWidget(metadata_group)

        # ── Dialog close button ───────────────────────────────────────
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        right_panel.addWidget(button_box)

        # ── Assemble panels ───────────────────────────────────────────
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
        current_text = ""
        current_item = self._preset_list.currentItem()
        if current_item is not None:
            current_text = current_item.text()

        self._preset_list.clear()
        for preset_name in self._config_manager.get_available_presets():
            item = QListWidgetItem(preset_name)
            self._preset_list.addItem(item)
            if preset_name == current_text:
                self._preset_list.setCurrentItem(item)

        if self._preset_list.currentItem() is None and self._preset_list.count() > 0:
            self._preset_list.setCurrentRow(0)

        self._update_action_buttons()

    def _update_action_buttons(self) -> None:
        """Enable or disable action buttons based on selection state."""
        has_selection = self._preset_list.currentItem() is not None
        self._delete_btn.setEnabled(has_selection)
        self._export_btn.setEnabled(has_selection)

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
        self._update_action_buttons()

        if row < 0:
            self._name_label.setText("—")
            self._desc_text.setPlainText("")
            self._file_label.setText("—")
            return

        preset_name = self._current_preset_name()
        if preset_name is None:
            return

        meta = self._load_metadata(preset_name)
        display_name = meta.get("name") or preset_name
        description = meta.get("description", "")

        self._name_label.setText(display_name)
        self._desc_text.setPlainText(description)

        preset_file = self._config_manager.preset_dir / f"{preset_name}.xml"
        self._file_label.setText(str(preset_file))

    @Slot()
    def _on_delete(self) -> None:
        """Ask for confirmation then delete the selected preset."""
        preset_name = self._current_preset_name()
        if preset_name is None:
            return

        reply = QMessageBox.question(
            self,
            "Delete Preset",
            f'Are you sure you want to delete the preset "{preset_name}"?\n'
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        success = self._config_manager.delete_preset(preset_name)
        if success:
            self._refresh_preset_list()
            self._on_preset_selected(self._preset_list.currentRow())
            self.presets_changed.emit()
        else:
            QMessageBox.warning(
                self,
                "Delete Failed",
                f'Could not delete preset "{preset_name}".\n'
                "The file may already have been removed.",
            )

    @Slot()
    def _on_export(self) -> None:
        """Export the selected preset to a user-chosen file."""
        preset_name = self._current_preset_name()
        if preset_name is None:
            return

        source_path = self._config_manager.preset_dir / f"{preset_name}.xml"
        if not source_path.exists():
            QMessageBox.warning(
                self,
                "Export Failed",
                f"Preset file not found:\n{source_path}",
            )
            return

        dest_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Preset",
            str(Path.home() / f"{preset_name}.xml"),
            "XML Preset Files (*.xml);;All Files (*)",
        )
        if not dest_path:
            return

        try:
            shutil.copy2(source_path, dest_path)
            QMessageBox.information(
                self,
                "Export Successful",
                f"Preset exported to:\n{dest_path}",
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Could not export preset:\n{exc}",
            )

    @Slot()
    def _on_import(self) -> None:
        """Import a preset from a file chosen by the user."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Preset",
            str(Path.home()),
            "XML Preset Files (*.xml);;All Files (*)",
        )
        if not file_path:
            return

        source = Path(file_path)

        # Validate before importing
        is_valid, errors = self._config_manager.validate_preset_file(source)
        if not is_valid:
            QMessageBox.warning(
                self,
                "Invalid Preset",
                "The selected file is not a valid preset:\n\n" + "\n".join(errors),
            )
            return

        dest_path = self._config_manager.preset_dir / source.name
        if dest_path.exists():
            reply = QMessageBox.question(
                self,
                "Overwrite Preset",
                f'A preset named "{source.stem}" already exists.\n'
                "Do you want to overwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        try:
            shutil.copy2(source, dest_path)
            self._refresh_preset_list()
            # Select the newly imported preset
            for i in range(self._preset_list.count()):
                if self._preset_list.item(i).text() == source.stem:
                    self._preset_list.setCurrentRow(i)
                    break
            self.presets_changed.emit()
            QMessageBox.information(
                self,
                "Import Successful",
                f'Preset "{source.stem}" imported successfully.',
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Import Failed",
                f"Could not import preset:\n{exc}",
            )
