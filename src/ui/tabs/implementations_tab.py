"""Implementations tab for selecting optional plugin feature sets."""

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.base_tab import BaseTab
from core.gui_components import get_components_grouped


class ImplementationsTab(BaseTab):
    """Tab for configuring plugin implementations and features"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Initialize UI components"""
        # Main layout
        self.main_layout = QVBoxLayout(self)

        # Create a scroll area for implementation options
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)

        # Content widget for the scroll area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(15)

        # Add intro/help text
        self.help_label = QLabel(
            "Select the implementations you want to include in your plugin project. "
            "Each implementation adds specific functionality to your plugin."
        )
        self.help_label.setWordWrap(True)
        self.help_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.content_layout.addWidget(self.help_label)

        # Single group for all implementations
        self.implementations_group = QGroupBox("Plugin Implementation Features")
        implementations_layout = QVBoxLayout()
        implementations_layout.setSpacing(12)  # Increase spacing between elements

        # -- FRAMEWORK & LICENSING SECTION --
        self.add_section_header(implementations_layout, "Framework & Licensing")

        self.moonbase_licensing = QCheckBox("Moonbase_Sh Licensing Client")
        self.moonbase_licensing.setToolTip(
            "Implements Moonbase_Sh license validation for your plugin"
        )
        implementations_layout.addWidget(self.moonbase_licensing)

        self.melatonin_inspector = QCheckBox("Melatonin Inspector")
        self.melatonin_inspector.setToolTip("GUI inspection and debugging tool for JUCE")
        implementations_layout.addWidget(self.melatonin_inspector)

        self.custom_gui = QCheckBox("Custom GUI Framework")
        self.custom_gui.setToolTip("Implements a custom GUI framework with additional components")
        implementations_layout.addWidget(self.custom_gui)

        # DirektDSP_GUI component description panel (shown when Custom GUI is checked)
        self.gui_components_panel = QLabel()
        self.gui_components_panel.setWordWrap(True)
        self.gui_components_panel.setTextFormat(self.gui_components_panel.TextFormat.RichText)
        self.gui_components_panel.setContentsMargins(20, 4, 0, 4)
        self.gui_components_panel.setStyleSheet("color: #999; font-size: 12px;")
        self.gui_components_panel.setText(self._format_gui_components())
        self.gui_components_panel.setVisible(False)
        implementations_layout.addWidget(self.gui_components_panel)

        self.logging_framework = QCheckBox("Logging Framework")
        self.logging_framework.setToolTip(
            "Comprehensive logging system for debugging and analytics"
        )
        implementations_layout.addWidget(self.logging_framework)

        # Add spacing after section
        implementations_layout.addSpacing(10)

        # -- BUILD FEATURES SECTION --
        self.add_section_header(implementations_layout, "Build Features")

        self.clap_builds = QCheckBox("CLAP Plugin Builds")
        self.clap_builds.setToolTip("Add support for building CLAP format plugins")
        implementations_layout.addWidget(self.clap_builds)

        # Add spacing after section
        implementations_layout.addSpacing(10)

        # -- USER FEATURES SECTION --
        self.add_section_header(implementations_layout, "User Experience Features")

        self.preset_management = QCheckBox("Preset Management System")
        self.preset_management.setToolTip("System for saving, loading, and managing user presets")
        implementations_layout.addWidget(self.preset_management)

        # Preset system options
        self.preset_options_layout = QFormLayout()
        self.preset_options_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )
        self.preset_options_layout.setContentsMargins(20, 0, 0, 0)  # Add left indent

        self.preset_format = QComboBox()
        self.preset_format.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.preset_format.addItems(["XML", "JSON", "Binary"])

        self.preset_options_layout.addRow("Preset Format:", self.preset_format)
        implementations_layout.addLayout(self.preset_options_layout)

        self.ab_comparison = QCheckBox("A/B Comparison Feature")
        self.ab_comparison.setToolTip("Allows users to compare settings with A/B switching")
        implementations_layout.addWidget(self.ab_comparison)

        self.state_management = QCheckBox("State Management/Undo History")
        self.state_management.setToolTip("Implements undo/redo functionality for user actions")
        implementations_layout.addWidget(self.state_management)

        # Add spacing after section
        implementations_layout.addSpacing(10)

        # -- PERFORMANCE SECTION --
        self.add_section_header(implementations_layout, "Performance Features")

        self.gpu_audio = QCheckBox("DSP Parallelization on GPU (GPU Audio)")
        self.gpu_audio.setToolTip("Implements GPU-accelerated audio processing")
        implementations_layout.addWidget(self.gpu_audio)

        self.implementations_group.setLayout(implementations_layout)
        self.content_layout.addWidget(self.implementations_group)

        # Add spacer at the bottom
        self.content_layout.addStretch()

        # Set the content widget to the scroll area
        self.scroll_area.setWidget(self.content_widget)
        self.main_layout.addWidget(self.scroll_area)

        # Initialize UI states
        self.update_dependent_widgets()

    def add_section_header(self, layout, text):
        """Add a section header with divider line and bolded text"""
        # Create container for section header
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Add header label
        section_label = QLabel(text)
        section_label.setStyleSheet("font-weight: bold; color: {primary-color};")

        # Add header to layout
        header_layout.addWidget(section_label)
        header_layout.addStretch()

        # Add a divider line
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)

        # Add to parent layout
        layout.addWidget(header_container)
        layout.addWidget(divider)

    def setup_connections(self):
        """Connect signals to slots"""
        # Connect checkboxes to update their dependent widgets
        self.preset_management.toggled.connect(self.update_dependent_widgets)
        self.custom_gui.toggled.connect(self.gui_components_panel.setVisible)

        # Connect all implementation checkboxes to emit signal
        implementations = [
            self.moonbase_licensing,
            self.melatonin_inspector,
            self.custom_gui,
            self.logging_framework,
            self.clap_builds,
            self.preset_management,
            self.ab_comparison,
            self.state_management,
            self.gpu_audio,
        ]

        for checkbox in implementations:
            checkbox.toggled.connect(self.emit_implementations_changed)

    @Slot()
    def update_dependent_widgets(self):
        """Enable/disable dependent widgets based on checkbox states"""
        # GUI components panel
        self.gui_components_panel.setVisible(self.custom_gui.isChecked())

        # Preset options
        for i in range(self.preset_options_layout.rowCount()):
            label_item = self.preset_options_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
            field_item = self.preset_options_layout.itemAt(i, QFormLayout.ItemRole.FieldRole)
            if label_item and field_item:
                label_item.widget().setEnabled(self.preset_management.isChecked())
                field_item.widget().setEnabled(self.preset_management.isChecked())

    @staticmethod
    def _format_gui_components() -> str:
        """Format all DirektDSP_GUI components as HTML grouped by category."""
        grouped = get_components_grouped("Advanced")  # Show full catalogue
        if not grouped:
            return ""
        lines: list[str] = []
        for category, components in grouped.items():
            lines.append(f"<b>{category}/</b>")
            for comp in components:
                lines.append(f"&nbsp;&nbsp;\u2713 {comp.name} \u2014 <i>{comp.description}</i>")
        return "<br>".join(lines)

    @Slot()
    def emit_implementations_changed(self):
        """Emit config changed signal with current implementations configuration"""
        self._emit_config_changed()

    def get_configuration(self):
        """Get current implementation configuration"""
        config = {
            # All implementations
            "moonbase_licensing": self.moonbase_licensing.isChecked(),
            "melatonin_inspector": self.melatonin_inspector.isChecked(),
            "custom_gui_framework": self.custom_gui.isChecked(),
            "logging_framework": self.logging_framework.isChecked(),
            "clap_builds": self.clap_builds.isChecked(),
            "preset_management": self.preset_management.isChecked(),
            "preset_format": (
                self.preset_format.currentText() if self.preset_management.isChecked() else None
            ),
            "ab_comparison": self.ab_comparison.isChecked(),
            "state_management": self.state_management.isChecked(),
            "gpu_audio": self.gpu_audio.isChecked(),
        }
        return config

    def load_configuration(self, config):
        """Load configuration into the UI"""
        # Set checkbox states
        self.moonbase_licensing.setChecked(config.get("moonbase_licensing", False))
        self.melatonin_inspector.setChecked(config.get("melatonin_inspector", False))
        self.custom_gui.setChecked(config.get("custom_gui_framework", False))
        self.logging_framework.setChecked(config.get("logging_framework", False))
        self.clap_builds.setChecked(config.get("clap_builds", False))
        self.preset_management.setChecked(config.get("preset_management", False))
        self.ab_comparison.setChecked(config.get("ab_comparison", False))
        self.state_management.setChecked(config.get("state_management", False))
        self.gpu_audio.setChecked(config.get("gpu_audio", False))

        # Set additional options
        if config.get("preset_format"):
            index = self.preset_format.findText(config.get("preset_format"))
            if index >= 0:
                self.preset_format.setCurrentIndex(index)

        # Update dependent widgets
        self.update_dependent_widgets()

    def validate(self):
        """Validate the selected implementations for compatibility"""
        # This will be expanded later but for now just return True
        return True

    def reset(self):
        """Reset form to default values"""
        # Uncheck all implementations
        self.moonbase_licensing.setChecked(False)
        self.melatonin_inspector.setChecked(False)
        self.custom_gui.setChecked(False)
        self.logging_framework.setChecked(False)
        self.clap_builds.setChecked(False)
        self.preset_management.setChecked(False)
        self.ab_comparison.setChecked(False)
        self.state_management.setChecked(False)
        self.gpu_audio.setChecked(False)

        # Reset dropdown to default
        self.preset_format.setCurrentIndex(0)

        # Update dependent widgets
        self.update_dependent_widgets()
