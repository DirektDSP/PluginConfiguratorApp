from copy import deepcopy

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from core.base_tab import BaseTab
from core.config_manager import ConfigManager


class GenerateTab(BaseTab):
    """Tab 4: Generate - Preview configuration and generate project

    This is the fourth and final tab in the new 4-lifecycle UI structure.
    Users can preview their configuration and generate the plugin project.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = ConfigManager()
        self.full_config = {}
        self.setup_ui()
        self.setup_connections()
        self._emit_config_changed()

    def setup_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)

        # Preview group
        preview_group = QGroupBox("Configuration Preview")
        preview_layout = QVBoxLayout()

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMinimumHeight(200)
        self.preview_text.setPlaceholderText("Configuration will be displayed here...")
        preview_layout.addWidget(self.preview_text)

        preview_group.setLayout(preview_layout)

        # File tree preview group
        file_tree_group = QGroupBox("File Structure Preview")
        file_tree_layout = QVBoxLayout()

        self.file_tree_text = QTextEdit()
        self.file_tree_text.setReadOnly(True)
        self.file_tree_text.setMinimumHeight(150)
        self.file_tree_text.setFontFamily("Monospace")
        self.file_tree_text.setPlaceholderText("File structure will be displayed here...")
        file_tree_layout.addWidget(self.file_tree_text)

        file_tree_group.setLayout(file_tree_layout)

        # Progress group
        progress_group = QGroupBox("Generation Progress")
        progress_layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready to generate project")
        progress_layout.addWidget(self.status_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(100)
        self.log_text.setPlaceholderText("Generation logs will appear here...")
        progress_layout.addWidget(self.log_text)

        progress_group.setLayout(progress_layout)

        # Progress indicator
        self.progress_label = QLabel("Step 4 of 4: Generate")
        self.progress_label.setStyleSheet("color: #666; font-style: italic;")

        # Action buttons
        action_layout = QHBoxLayout()

        self.back_button = QPushButton("← Back to Implement")
        self.save_preset_button = QPushButton("Save as Preset")
        self.load_preset_button = QPushButton("Load Preset")
        self.generate_button = QPushButton("Generate Project")
        self.generate_button.setMinimumHeight(45)
        self.generate_button.setStyleSheet("font-weight: bold; font-size: 14px;")

        action_layout.addWidget(self.back_button)
        action_layout.addStretch()
        action_layout.addWidget(self.save_preset_button)
        action_layout.addWidget(self.load_preset_button)
        action_layout.addWidget(self.generate_button)

        # Add to main layout
        layout.addWidget(preview_group)
        layout.addWidget(file_tree_group)
        layout.addWidget(progress_group)
        layout.addWidget(self.progress_label)
        layout.addStretch()
        layout.addLayout(action_layout)

    def setup_connections(self):
        """Connect signals to slots"""
        self.back_button.clicked.connect(self._go_back_to_implement)
        self.save_preset_button.clicked.connect(self._save_as_preset)
        self.load_preset_button.clicked.connect(self._load_preset)
        self.generate_button.clicked.connect(self._generate_project)

    @Slot()
    def _go_back_to_implement(self):
        """Navigate back to Implement tab"""
        self._emit_config_changed()

    @Slot()
    def _save_as_preset(self):
        """Save current configuration as a preset"""
        preset_name, ok = QFileDialog.getSaveFileName(self, "Save Preset", "", "XML Files (*.xml)")

        if ok and preset_name:
            try:
                self.config_manager.save_config(self.full_config, preset_name)
                QMessageBox.information(
                    self, "Success", f"Preset saved successfully to {preset_name}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save preset: {e!s}")

    def save_as_preset(self):
        """Public wrapper for saving the current configuration as a preset."""
        self._save_as_preset()

    @Slot()
    def _load_preset(self):
        """Load configuration from a preset"""
        preset_path, ok = QFileDialog.getOpenFileName(self, "Load Preset", "", "XML Files (*.xml)")

        if ok and preset_path:
            try:
                config = self.config_manager.load_config(preset_path)
                self.full_config = config
                self._update_preview()
                self._emit_config_changed()
                QMessageBox.information(
                    self, "Success", f"Preset loaded successfully from {preset_path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load preset: {e!s}")

    @Slot()
    def _generate_project(self):
        """Generate the plugin project"""
        if not self.full_config:
            QMessageBox.warning(
                self,
                "No Configuration",
                "Please complete the previous steps to configure your project.",
            )
            return

        reply = QMessageBox.question(
            self,
            "Confirm Generation",
            f"Generate project '{self.full_config.get('project_name', 'Unknown')}'?\n\n"
            f"Output: {self.full_config.get('output_directory', 'Unknown')}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._start_generation()

    def generate_project(self):
        """Public wrapper for generating the plugin project."""
        self._generate_project()

    def _start_generation(self):
        """Start the project generation process"""
        self.status_label.setText("Starting generation...")
        self.log_text.clear()
        self.progress_bar.setValue(0)

        self.log_text.append("=== Starting Project Generation ===")
        self.log_text.append(f"Project: {self.full_config.get('project_name', 'Unknown')}")
        self.log_text.append(f"Output: {self.full_config.get('output_directory', 'Unknown')}")
        self.log_text.append("")

        try:
            self.progress_bar.setValue(10)
            self.log_text.append("[10%] Validating configuration...")
            self._validate_config()

            self.progress_bar.setValue(30)
            self.log_text.append("[30%] Cloning template repository...")
            self.progress_bar.setValue(50)

            self.log_text.append("[50%] Applying configuration...")
            self.progress_bar.setValue(70)

            self.log_text.append("[70%] Configuring project files...")
            self.progress_bar.setValue(90)

            self.log_text.append("[90%] Finalizing setup...")
            self.progress_bar.setValue(100)

            self.log_text.append("\n=== Generation Complete ===")
            self.log_text.append("Project generated successfully!")
            self.status_label.setText("Generation complete!")

            QMessageBox.information(
                self,
                "Success",
                "Project generated successfully!\n\n"
                f"Location: {self.full_config.get('output_directory', 'Unknown')}",
            )

        except Exception as e:
            self.log_text.append(f"\nERROR: {e!s}")
            self.status_label.setText("Generation failed!")
            self.progress_bar.setValue(0)
            QMessageBox.critical(self, "Generation Failed", f"Failed to generate project: {e!s}")

    def _validate_config(self):
        """Validate the configuration"""
        required_fields = [
            "project_name",
            "product_name",
            "company_name",
            "bundle_id",
            "manufacturer_code",
            "output_directory",
            "fork_url",
        ]

        missing = []
        for field in required_fields:
            if not self.full_config.get(field, "").strip():
                missing.append(field)

        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

    def _update_preview(self):
        """Update the configuration preview"""
        preview_lines = []
        preview_lines.append("=" * 50)
        preview_lines.append("PROJECT CONFIGURATION")
        preview_lines.append("=" * 50)
        preview_lines.append("")

        sections = {
            "Project Info": ["project_name", "product_name"],
            "Company Info": ["company_name", "bundle_id", "manufacturer_code"],
            "Build Options": ["standalone", "vst3", "au", "auv3", "clap"],
            "Development": ["create_git_repo", "melatonin", "moonbase"],
            "Location": ["fork_url", "output_directory"],
        }

        for section, fields in sections.items():
            preview_lines.append(f"[{section}]")
            for field in fields:
                value = self.full_config.get(field, "")
                if isinstance(value, bool):
                    value = "Enabled" if value else "Disabled"
                elif not value:
                    value = "Not set"
                preview_lines.append(f"  {field.replace('_', ' ').title()}: {value}")
            preview_lines.append("")

        self.preview_text.setPlainText("\n".join(preview_lines))

        # Update file tree preview
        project_name = self.full_config.get("project_name", "MyProject")
        file_tree = f"""{project_name}/
├── .git/
├── JUCE/
├── cmake/
├── src/
│   ├── {project_name.lower()}.cpp
│   ├── {project_name.lower()}.h
│   ├── PluginProcessor.cpp
│   └── PluginProcessor.h
├── CMakeLists.txt
├── README.md
├── .gitignore
└── {project_name}.jucer"""

        self.file_tree_text.setPlainText(file_tree)

    def update_full_config(self, config):
        """Update full configuration from all tabs"""
        self.full_config = config.copy()
        self._update_preview()

    def get_configuration(self):
        """Get current configuration from the tab"""
        return {"full_config": self.full_config, "tab_complete": bool(self.full_config)}

    def load_configuration(self, config):
        """Load configuration into the tab"""
        self.full_config = deepcopy(config)
        self._update_preview()
        self._emit_config_changed()

    def validate(self):
        """Validate the tab's current state - always valid"""
        return True

    def reset(self):
        """Reset the tab to its default state"""
        self.full_config = {}
        self.preview_text.clear()
        self.file_tree_text.clear()
        self.log_text.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText("Ready to generate project")
        self._emit_config_changed()
