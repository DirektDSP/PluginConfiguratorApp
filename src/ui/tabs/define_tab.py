"""Define tab for plugin type, metadata, and file tree preview."""

import re
from typing import ClassVar

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.base_tab import BaseTab

# Padding used when auto-generating a 4-character plugin code from a project
# name that has fewer than 4 characters.
_PLUGIN_CODE_PADDING = "xxxx"


class DefineTab(BaseTab):
    """Tab 1: Define - Plugin type selection and metadata

    This is the first tab in the 4-lifecycle UI structure.
    Users select the plugin type and fill in project metadata here.
    Derived fields are auto-populated and a live file tree preview
    reflects the expected project structure.
    """

    PLUGIN_TYPES: ClassVar[list[str]] = ["Audio FX", "Instrument", "Utility"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        self._update_file_tree()
        self._emit_config_changed()

    # ------------------------------------------------------------------
    # BaseTab interface
    # ------------------------------------------------------------------

    def setup_ui(self):
        """Initialize UI components"""
        outer_layout = QHBoxLayout(self)

        # ---- Left panel: form inputs --------------------------------
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Plugin type group
        type_group = QGroupBox("Plugin Type")
        type_layout = QFormLayout()

        self.plugin_type = QComboBox()
        self.plugin_type.addItems(self.PLUGIN_TYPES)
        self.plugin_type.setToolTip("Select the type of audio plugin to create")
        type_layout.addRow("Type:", self.plugin_type)

        type_group.setLayout(type_layout)

        # Metadata group
        metadata_group = QGroupBox("Project Metadata")
        metadata_layout = QFormLayout()

        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText("MyPlugin")
        metadata_layout.addRow("Project Name *:", self.project_name)

        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("My Plugin (auto-filled)")
        metadata_layout.addRow("Product Name:", self.product_name)

        self.company_name = QLineEdit()
        self.company_name.setPlaceholderText("Your Company")
        self.company_name.setText("DirektDSP")
        metadata_layout.addRow("Company Name *:", self.company_name)

        self.version = QLineEdit()
        self.version.setPlaceholderText("1.0.0")
        self.version.setText("1.0.0")
        metadata_layout.addRow("Version:", self.version)

        metadata_group.setLayout(metadata_layout)

        # Advanced group
        advanced_group = QGroupBox("Advanced (Optional)")
        advanced_layout = QFormLayout()

        self.manufacturer_code = QLineEdit()
        self.manufacturer_code.setPlaceholderText("Mfct")
        self.manufacturer_code.setText("Ddsp")
        self.manufacturer_code.setMaxLength(4)
        self.manufacturer_code.setToolTip("Four-character manufacturer identifier")
        advanced_layout.addRow("Manufacturer Code:", self.manufacturer_code)

        self.plugin_code = QLineEdit()
        self.plugin_code.setPlaceholderText("Plug (auto-filled)")
        self.plugin_code.setMaxLength(4)
        self.plugin_code.setToolTip("Four-character plugin identifier")
        advanced_layout.addRow("Plugin Code:", self.plugin_code)

        self.bundle_id = QLineEdit()
        self.bundle_id.setPlaceholderText("com.company.plugin (auto-filled)")
        self.bundle_id.setToolTip("Reverse-DNS bundle identifier")
        advanced_layout.addRow("Bundle ID:", self.bundle_id)

        advanced_group.setLayout(advanced_layout)

        # Progress indicator
        self.progress_label = QLabel("Step 1 of 4: Define")
        self.progress_label.setStyleSheet("color: #666; font-style: italic;")

        # Continue button
        self.continue_button = QPushButton("Continue to Configure →")
        self.continue_button.setMinimumHeight(40)
        self.continue_button.setEnabled(False)

        left_layout.addWidget(type_group)
        left_layout.addWidget(metadata_group)
        left_layout.addWidget(advanced_group)
        left_layout.addWidget(self.progress_label)
        left_layout.addStretch()
        left_layout.addWidget(self.continue_button)

        # ---- Right panel: file tree preview -------------------------
        right_group = QGroupBox("File Tree Preview")
        right_layout = QVBoxLayout()

        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabel("Project Structure")
        self.file_tree.setAnimated(True)
        right_layout.addWidget(self.file_tree)

        right_group.setLayout(right_layout)

        # ---- Splitter -----------------------------------------------
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_group)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        outer_layout.addWidget(splitter)

    def setup_connections(self):
        """Connect signals to slots"""
        self.plugin_type.currentIndexChanged.connect(self._on_config_changed)
        self.project_name.textChanged.connect(self._on_project_name_changed)
        self.product_name.textChanged.connect(self._on_config_changed)
        self.company_name.textChanged.connect(self._on_company_changed)
        self.version.textChanged.connect(self._on_config_changed)
        self.manufacturer_code.textChanged.connect(self._on_config_changed)
        self.plugin_code.textChanged.connect(self._on_config_changed)
        self.bundle_id.textChanged.connect(self._on_config_changed)
        self.continue_button.clicked.connect(self._continue_to_configure)

    def get_configuration(self):
        """Get current configuration from the tab"""
        return {
            "plugin_type": self.plugin_type.currentText(),
            "project_name": self.project_name.text().strip(),
            "product_name": self.product_name.text().strip(),
            "company_name": self.company_name.text().strip(),
            "version": self.version.text().strip(),
            "manufacturer_code": self.manufacturer_code.text().strip(),
            "plugin_code": self.plugin_code.text().strip(),
            "bundle_id": self.bundle_id.text().strip(),
            "tab_complete": self._is_valid,
        }

    def load_configuration(self, config):
        """Load configuration into the tab"""
        plugin_type = config.get("plugin_type", self.PLUGIN_TYPES[0])
        idx = self.plugin_type.findText(plugin_type)
        if idx >= 0:
            self.plugin_type.setCurrentIndex(idx)

        self.project_name.setText(config.get("project_name", ""))
        self.product_name.setText(config.get("product_name", ""))
        self.company_name.setText(config.get("company_name", "DirektDSP"))
        self.version.setText(config.get("version", "1.0.0"))
        self.manufacturer_code.setText(config.get("manufacturer_code", "Ddsp"))
        self.plugin_code.setText(config.get("plugin_code", ""))
        self.bundle_id.setText(config.get("bundle_id", ""))

        self._update_validation_state()
        self._update_file_tree()
        self._emit_config_changed()

    def validate(self):
        """Validate the tab's current state"""
        errors = []
        if not self.project_name.text().strip():
            errors.append("Project Name is required")
        if not self.company_name.text().strip():
            errors.append("Company Name is required")
        return not errors

    def reset(self):
        """Reset the tab to its default state"""
        self.plugin_type.setCurrentIndex(0)
        self.project_name.clear()
        self.product_name.clear()
        self.company_name.setText("DirektDSP")
        self.version.setText("1.0.0")
        self.manufacturer_code.setText("Ddsp")
        self.plugin_code.clear()
        self.bundle_id.clear()
        self._update_validation_state()
        self._update_file_tree()
        self._emit_config_changed()

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    @Slot()
    def _on_project_name_changed(self):
        """Auto-populate derived fields when the project name changes."""
        project = self.project_name.text().strip()

        # Auto-fill product name only if the user has not entered one yet
        if project and not self.product_name.text().strip():
            self.product_name.blockSignals(True)
            self.product_name.setText(self._to_display_name(project))
            self.product_name.blockSignals(False)

        # Auto-fill plugin code only if the user has not entered one yet
        if project and not self.plugin_code.text().strip():
            code = (project + _PLUGIN_CODE_PADDING)[:4]
            self.plugin_code.blockSignals(True)
            self.plugin_code.setText(code)
            self.plugin_code.blockSignals(False)

        self._auto_fill_bundle_id()
        self._update_file_tree()
        self._emit_config_changed()
        self._update_validation_state()

    @Slot()
    def _on_company_changed(self):
        """Re-derive the bundle ID when the company name changes."""
        self._auto_fill_bundle_id()
        self._on_config_changed()

    @Slot()
    def _on_config_changed(self):
        """Handle generic configuration changes."""
        self._update_file_tree()
        self._emit_config_changed()
        self._update_validation_state()

    @Slot()
    def _continue_to_configure(self):
        """Validate before continuing to the Configure tab."""
        if self.validate():
            self._emit_config_changed()
        else:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please complete all required fields before continuing.",
            )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _auto_fill_bundle_id(self):
        """Set bundle ID from company + project name when the field is empty
        or still contains a previously auto-generated value."""
        current = self.bundle_id.text().strip()
        company = self.company_name.text().strip().lower().replace(" ", "")
        project = (
            self.project_name.text().strip().lower().replace(" ", "").replace("_", "")
        )

        if not company or not project:
            return

        new_bundle = f"com.{company}.{project}"

        # Only overwrite if the field is empty or looks auto-generated
        if (not current or current.startswith("com.")) and current != new_bundle:
            self.bundle_id.blockSignals(True)
            self.bundle_id.setText(new_bundle)
            self.bundle_id.blockSignals(False)

    @staticmethod
    def _to_display_name(name: str) -> str:
        """Convert CamelCase or snake_case identifier to a human-readable name.

        Examples::

            "MyPlugin"     → "My Plugin"
            "my_plugin"    → "My Plugin"
            "HTMLParser"   → "Html Parser"
            "MyHTMLPlugin" → "My Html Plugin"
        """
        # Insert a space between a lowercase letter and the following uppercase letter
        name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
        # Insert a space between a run of uppercase letters and the next uppercase+lowercase pair
        # (handles acronyms like "HTML" in "HTMLParser" → "HTML Parser")
        name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", name)
        # Replace underscores/hyphens with spaces
        name = name.replace("_", " ").replace("-", " ")
        return name.strip().title()

    def _update_validation_state(self):
        """Enable the continue button only when all required fields are filled."""
        is_valid = bool(self.project_name.text().strip()) and bool(
            self.company_name.text().strip()
        )
        self._emit_validation_changed(is_valid)
        self.continue_button.setEnabled(is_valid)

    def _update_file_tree(self):
        """Rebuild the file tree preview to reflect the current configuration."""
        self.file_tree.clear()

        project_name = self.project_name.text().strip() or "MyPlugin"
        plugin_type = self.plugin_type.currentText()

        # Root node
        root = QTreeWidgetItem(self.file_tree, [f"{project_name}/"])
        root.setExpanded(True)

        # Top-level files
        QTreeWidgetItem(root, ["CMakeLists.txt"])
        QTreeWidgetItem(root, ["README.md"])
        QTreeWidgetItem(root, [".gitignore"])

        # Source folder
        source = QTreeWidgetItem(root, ["Source/"])
        source.setExpanded(True)
        QTreeWidgetItem(source, ["PluginProcessor.cpp"])
        QTreeWidgetItem(source, ["PluginProcessor.h"])

        # Editor files are not typically generated for Utility plugins
        if plugin_type != "Utility":
            QTreeWidgetItem(source, ["PluginEditor.cpp"])
            QTreeWidgetItem(source, ["PluginEditor.h"])

        # Resources folder (always present)
        QTreeWidgetItem(root, ["Resources/"])
