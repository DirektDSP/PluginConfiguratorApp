from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QFileDialog,
    QMessageBox,
    QCheckBox,
)
from PySide6.QtCore import Signal, Slot

from core.base_tab import BaseTab
from core.utils import generate_plugin_id


class DefineTab(BaseTab):
    """Tab 1: Define - Select template and output directory

    This is the first tab in the new 4-lifecycle UI structure.
    Users select a template fork and output directory here.
    """

    PROJECT_TEMPLATE_URL = "https://github.com/SeamusMullan/PluginTemplate.git"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        self._emit_config_changed()

    def setup_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)

        # Template selection group
        template_group = QGroupBox("Template Selection")
        template_layout = QFormLayout()

        # Fork URL field
        fork_url_layout = QHBoxLayout()
        self.fork_url = QLineEdit()
        self.fork_url.setPlaceholderText("Enter Git repository URL")
        self.fork_url.setText(self.PROJECT_TEMPLATE_URL)
        self.fork_url.setMinimumWidth(400)

        self.fork_url_button = QPushButton("Clone")
        self.fork_url_button.setMaximumWidth(80)
        fork_url_layout.addWidget(self.fork_url)
        fork_url_layout.addWidget(self.fork_url_button)
        template_layout.addRow("Template Fork URL:", fork_url_layout)

        # Quick select presets dropdown
        preset_layout = QHBoxLayout()
        self.preset_dropdown = QLineEdit()
        self.preset_dropdown.setPlaceholderText(
            "Select a preset or leave empty for custom"
        )
        self.preset_dropdown.setReadOnly(True)

        self.browse_preset_button = QPushButton("Browse Presets...")
        preset_layout.addWidget(self.preset_dropdown)
        preset_layout.addWidget(self.browse_preset_button)
        template_layout.addRow("Preset:", preset_layout)

        template_group.setLayout(template_layout)

        # Output directory group
        output_group = QGroupBox("Output Directory")
        output_layout = QFormLayout()

        # Output directory selection
        output_dir_layout = QHBoxLayout()
        self.output_directory = QLineEdit()
        self.output_directory.setPlaceholderText(
            "Select output directory for your plugin project"
        )
        self.browse_button = QPushButton("Browse...")
        self.browse_button.setMaximumWidth(80)
        output_dir_layout.addWidget(self.output_directory)
        output_dir_layout.addWidget(self.browse_button)
        output_layout.addRow("Project Output:", output_dir_layout)

        # Quick start mode checkbox
        self.quick_start_mode = QCheckBox("Quick Start Mode")
        self.quick_start_mode.setChecked(True)
        self.quick_start_mode.setToolTip(
            "Enable Quick Start mode with simplified interface"
        )
        output_layout.addRow(self.quick_start_mode)

        output_group.setLayout(output_layout)

        # Progress indicator
        self.progress_label = QLabel("Step 1 of 4: Define")
        self.progress_label.setStyleSheet("color: #666; font-style: italic;")

        # Continue button
        self.continue_button = QPushButton("Continue to Configure →")
        self.continue_button.setMinimumHeight(40)
        self.continue_button.setEnabled(False)

        # Add to main layout
        layout.addWidget(template_group)
        layout.addWidget(output_group)
        layout.addWidget(self.progress_label)
        layout.addStretch()
        layout.addWidget(self.continue_button)

    def setup_connections(self):
        """Connect signals to slots"""
        self.fork_url.textChanged.connect(self._on_config_changed)
        self.output_directory.textChanged.connect(self._on_config_changed)
        self.browse_button.clicked.connect(self._browse_output_dir)
        self.browse_preset_button.clicked.connect(self._browse_presets)
        self.continue_button.clicked.connect(self._continue_to_configure)
        self.quick_start_mode.toggled.connect(self._on_quick_start_toggled)

    @Slot()
    def _on_config_changed(self):
        """Handle configuration changes"""
        self._emit_config_changed()
        self._update_validation_state()

    @Slot(bool)
    def _on_quick_start_toggled(self, checked):
        """Handle Quick Start mode toggle"""
        self._emit_config_changed()

    @Slot()
    def _browse_output_dir(self):
        """Open file dialog to select output directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", ""
        )
        if directory:
            self.output_directory.setText(directory)

    @Slot()
    def _browse_presets(self):
        """Open preset browser dialog"""
        QMessageBox.information(
            self,
            "Preset Browser",
            "Preset browser will be implemented in Phase 2.\n"
            "For now, you can manually load presets from the Advanced tab.",
        )

    @Slot()
    def _continue_to_configure(self):
        """Continue to configure tab"""
        if self.validate():
            self._emit_config_changed()
        else:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please complete all required fields before continuing.",
            )

    def _update_validation_state(self):
        """Update validation state based on field values"""
        is_valid = bool(self.fork_url.text().strip()) and bool(
            self.output_directory.text().strip()
        )
        self._emit_validation_changed(is_valid)
        self.continue_button.setEnabled(is_valid)

    def get_configuration(self):
        """Get current configuration from the tab"""
        return {
            "fork_url": self.fork_url.text().strip(),
            "preset": self.preset_dropdown.text().strip(),
            "output_directory": self.output_directory.text().strip(),
            "quick_start_mode": self.quick_start_mode.isChecked(),
            "tab_complete": self._is_valid,
        }

    def load_configuration(self, config):
        """Load configuration into the tab"""
        self.fork_url.setText(config.get("fork_url", self.PROJECT_TEMPLATE_URL))
        self.preset_dropdown.setText(config.get("preset", ""))
        self.output_directory.setText(config.get("output_directory", ""))
        self.quick_start_mode.setChecked(config.get("quick_start_mode", True))
        self._update_validation_state()
        self._emit_config_changed()

    def validate(self):
        """Validate the tab's current state"""
        errors = []

        if not self.fork_url.text().strip():
            errors.append("Template Fork URL is required")

        if not self.output_directory.text().strip():
            errors.append("Output Directory is required")

        if errors:
            return False

        return True

    def reset(self):
        """Reset the tab to its default state"""
        self.fork_url.setText(self.PROJECT_TEMPLATE_URL)
        self.preset_dropdown.clear()
        self.output_directory.clear()
        self.quick_start_mode.setChecked(True)
        self._update_validation_state()
        self._emit_config_changed()
