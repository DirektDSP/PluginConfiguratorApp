"""Configure tab for project metadata and plugin format options."""

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from core.base_tab import BaseTab


class ConfigureTab(BaseTab):
    """Tab 2: Configure - Configure plugin metadata and build options

    This is the second tab in the new 4-lifecycle UI structure.
    Users configure project information, company details, and build options here.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        self._emit_config_changed()

    def setup_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)

        # Project information group
        project_group = QGroupBox("Project Information")
        project_layout = QFormLayout()

        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText("MyAwesomePlugin")
        project_layout.addRow("Project Name:", self.project_name)

        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("My Awesome Plugin")
        project_layout.addRow("Product Name:", self.product_name)

        project_group.setLayout(project_layout)

        # Company information group
        company_group = QGroupBox("Company Information")
        company_layout = QFormLayout()

        self.company_name = QLineEdit()
        self.company_name.setPlaceholderText("Your Company Name")
        self.company_name.setText("DirektDSP")
        company_layout.addRow("Company Name:", self.company_name)

        self.bundle_id = QLineEdit()
        self.bundle_id.setPlaceholderText("com.yourcompany.pluginname")
        company_layout.addRow("Bundle ID:", self.bundle_id)

        self.manufacturer_code = QLineEdit()
        self.manufacturer_code.setPlaceholderText("Four character code")
        self.manufacturer_code.setText("Ddsp")
        self.manufacturer_code.setMaxLength(4)
        company_layout.addRow("Manufacturer Code:", self.manufacturer_code)

        company_group.setLayout(company_layout)

        # Plugin formats group
        formats_group = QGroupBox("Plugin Formats")
        formats_layout = QVBoxLayout()

        plugin_formats_form = QFormLayout()

        self.standalone = QCheckBox("Standalone Application")
        self.standalone.setChecked(False)
        plugin_formats_form.addRow("", self.standalone)

        self.vst3 = QCheckBox("VST3")
        self.vst3.setChecked(True)
        plugin_formats_form.addRow("", self.vst3)

        self.au = QCheckBox("Audio Unit (AU)")
        self.au.setChecked(True)
        plugin_formats_form.addRow("", self.au)

        self.auv3 = QCheckBox("AUv3 (iOS)")
        self.auv3.setChecked(False)
        plugin_formats_form.addRow("", self.auv3)

        self.clap = QCheckBox("CLAP")
        self.clap.setChecked(True)
        plugin_formats_form.addRow("", self.clap)

        formats_layout.addLayout(plugin_formats_form)
        formats_group.setLayout(formats_layout)

        # Progress indicator
        self.progress_label = QLabel("Step 2 of 4: Configure")
        self.progress_label.setStyleSheet("color: #666; font-style: italic;")

        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.back_button = QPushButton("← Back to Define")
        self.continue_button = QPushButton("Continue to Implement →")

        nav_layout.addWidget(self.back_button)
        nav_layout.addStretch()
        nav_layout.addWidget(self.continue_button)

        # Add to main layout
        layout.addWidget(project_group)
        layout.addWidget(company_group)
        layout.addWidget(formats_group)
        layout.addWidget(self.progress_label)
        layout.addStretch()
        layout.addLayout(nav_layout)

        # Connect state changes
        for checkbox in [self.standalone, self.vst3, self.au, self.auv3, self.clap]:
            checkbox.stateChanged.connect(self._on_config_changed)

    def setup_connections(self):
        """Connect signals to slots"""
        self.project_name.textChanged.connect(self._on_project_name_changed)
        self.product_name.textChanged.connect(self._on_config_changed)
        self.company_name.textChanged.connect(self._on_config_changed)
        self.bundle_id.textChanged.connect(self._on_config_changed)
        self.manufacturer_code.textChanged.connect(self._on_config_changed)

        self.back_button.clicked.connect(self._go_back_to_define)
        self.continue_button.clicked.connect(self._continue_to_implement)

    @Slot()
    def _on_project_name_changed(self):
        """Auto-generate bundle ID from project name"""
        project_name = self.project_name.text().strip()
        company = self.company_name.text().strip().lower().replace(" ", "")

        if project_name and company:
            plugin = project_name.lower().replace(" ", "").replace("_", "")
            if not self.bundle_id.text().strip():
                self.bundle_id.setText(f"com.{company}.{plugin}")

        self._emit_config_changed()
        self._update_validation_state()

    @Slot()
    def _on_config_changed(self):
        """Handle configuration changes"""
        self._emit_config_changed()
        self._update_validation_state()

    @Slot()
    def _go_back_to_define(self):
        """Navigate back to Define tab"""
        self._emit_config_changed()

    @Slot()
    def _continue_to_implement(self):
        """Continue to implement tab"""
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
        is_valid = (
            bool(self.project_name.text().strip())
            and bool(self.product_name.text().strip())
            and bool(self.company_name.text().strip())
            and bool(self.bundle_id.text().strip())
            and len(self.manufacturer_code.text().strip()) == 4
        )
        self._emit_validation_changed(is_valid)
        self.continue_button.setEnabled(is_valid)

    def get_configuration(self):
        """Get current configuration from the tab"""
        return {
            "project_name": self.project_name.text().strip(),
            "product_name": self.product_name.text().strip(),
            "company_name": self.company_name.text().strip(),
            "bundle_id": self.bundle_id.text().strip(),
            "manufacturer_code": self.manufacturer_code.text().strip(),
            "standalone": self.standalone.isChecked(),
            "vst3": self.vst3.isChecked(),
            "au": self.au.isChecked(),
            "auv3": self.auv3.isChecked(),
            "clap": self.clap.isChecked(),
            "tab_complete": self._is_valid,
        }

    def load_configuration(self, config):
        """Load configuration into the tab"""
        self.project_name.setText(config.get("project_name", ""))
        self.product_name.setText(config.get("product_name", ""))
        self.company_name.setText(config.get("company_name", "DirektDSP"))
        self.bundle_id.setText(config.get("bundle_id", ""))
        self.manufacturer_code.setText(config.get("manufacturer_code", "Ddsp"))
        self.standalone.setChecked(config.get("standalone", False))
        self.vst3.setChecked(config.get("vst3", True))
        self.au.setChecked(config.get("au", True))
        self.auv3.setChecked(config.get("auv3", False))
        self.clap.setChecked(config.get("clap", True))
        self._update_validation_state()
        self._emit_config_changed()

    def validate(self):
        """Validate the tab's current state"""
        errors = []

        if not self.project_name.text().strip():
            errors.append("Project Name is required")

        if not self.product_name.text().strip():
            errors.append("Product Name is required")

        if not self.company_name.text().strip():
            errors.append("Company Name is required")

        if not self.bundle_id.text().strip():
            errors.append("Bundle ID is required")

        if len(self.manufacturer_code.text().strip()) != 4:
            errors.append("Manufacturer Code must be exactly 4 characters")

        return not errors

    def reset(self):
        """Reset the tab to its default state"""
        self.project_name.clear()
        self.product_name.clear()
        self.company_name.setText("DirektDSP")
        self.bundle_id.clear()
        self.manufacturer_code.setText("Ddsp")
        self.standalone.setChecked(False)
        self.vst3.setChecked(True)
        self.au.setChecked(True)
        self.auv3.setChecked(False)
        self.clap.setChecked(True)
        self._update_validation_state()
        self._emit_config_changed()
