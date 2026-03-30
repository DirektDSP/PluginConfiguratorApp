"""Configure tab for project metadata and plugin format options."""
from PySide6.QtCore import QDir, Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.base_tab import BaseTab

# Format-specific notes shown in the disclosure label when a format is selected
_FORMAT_NOTES = {
    "standalone": "Standalone: Runs as an independent application without a DAW.",
    "vst3": "VST3: Widely supported on Windows, macOS and Linux. Recommended for cross-platform distribution.",
    "au": "AU (Audio Unit): macOS/iOS only. Required for Logic Pro and GarageBand compatibility.",
    "auv3": "AUv3: iOS/macOS app-extension format. Requires code signing and an Apple Developer account.",
    "clap": "CLAP: Open, modern plugin standard with advanced features. Growing DAW support.",
}


class ConfigureTab(BaseTab):
    """Tab 2: Configure - Configure plugin metadata and build options.

    This is the second tab in the new 4-lifecycle UI structure.
    Users configure project information, company details, plugin formats,
    build output directory, CI/CD pipelines, and code signing here.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        self._emit_config_changed()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def setup_ui(self):
        """Initialize UI components"""
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # Scrollable content area so the form remains usable on small screens
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)

        # -- Project information ------------------------------------------
        project_group = QGroupBox("Project Information")
        project_layout = QFormLayout()

        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText("MyAwesomePlugin")
        project_layout.addRow("Project Name:", self.project_name)

        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("My Awesome Plugin")
        project_layout.addRow("Product Name:", self.product_name)

        project_group.setLayout(project_layout)

        # -- Company information -----------------------------------------
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

        # -- Plugin formats ----------------------------------------------
        formats_group = QGroupBox("Plugin Formats")
        formats_layout = QVBoxLayout()

        formats_form = QFormLayout()

        self.standalone = QCheckBox("Standalone Application")
        self.standalone.setChecked(False)
        self.standalone.setToolTip(_FORMAT_NOTES["standalone"])
        formats_form.addRow("", self.standalone)

        self.vst3 = QCheckBox("VST3")
        self.vst3.setChecked(True)
        self.vst3.setToolTip(_FORMAT_NOTES["vst3"])
        formats_form.addRow("", self.vst3)

        self.au = QCheckBox("Audio Unit (AU)")
        self.au.setChecked(True)
        self.au.setToolTip(_FORMAT_NOTES["au"])
        formats_form.addRow("", self.au)

        self.auv3 = QCheckBox("AUv3 (iOS)")
        self.auv3.setChecked(False)
        self.auv3.setToolTip(_FORMAT_NOTES["auv3"])
        formats_form.addRow("", self.auv3)

        self.clap = QCheckBox("CLAP")
        self.clap.setChecked(True)
        self.clap.setToolTip(_FORMAT_NOTES["clap"])
        formats_form.addRow("", self.clap)

        formats_layout.addLayout(formats_form)

        # Format-specific disclosure label – updates dynamically
        self.format_disclosure_label = QLabel()
        self.format_disclosure_label.setWordWrap(True)
        self.format_disclosure_label.setStyleSheet("color: #888; font-size: 11px;")
        formats_layout.addWidget(self.format_disclosure_label)

        # Validation hint for "at least one format" rule
        self.format_error_label = QLabel("⚠ At least one plugin format must be selected.")
        self.format_error_label.setStyleSheet("color: #cc3333; font-size: 11px;")
        self.format_error_label.setVisible(False)
        formats_layout.addWidget(self.format_error_label)

        formats_group.setLayout(formats_layout)

        # -- Build options -----------------------------------------------
        build_group = QGroupBox("Build Options")
        build_layout = QFormLayout()

        output_dir_layout = QHBoxLayout()
        self.output_directory = QLineEdit()
        self.output_directory.setPlaceholderText("Select build output directory")
        self.browse_output_button = QPushButton("Browse…")
        self.browse_output_button.setMaximumWidth(80)
        output_dir_layout.addWidget(self.output_directory)
        output_dir_layout.addWidget(self.browse_output_button)
        build_layout.addRow("Output Directory:", output_dir_layout)

        build_group.setLayout(build_layout)

        # -- CI/CD options -----------------------------------------------
        cicd_group = QGroupBox("CI/CD Options")
        cicd_layout = QVBoxLayout()

        self.github_actions = QCheckBox("Generate GitHub Actions workflow")
        self.github_actions.setChecked(False)
        self.github_actions.setToolTip(
            "Creates a .github/workflows/build.yml that builds and tests the plugin on every push."
        )
        cicd_layout.addWidget(self.github_actions)

        # GitHub Actions sub-options (shown when enabled)
        self.cicd_sub_widget = QWidget()
        cicd_sub_layout = QFormLayout(self.cicd_sub_widget)
        cicd_sub_layout.setContentsMargins(20, 0, 0, 0)

        self.cicd_build_matrix = QCheckBox("Build for all platforms (Windows, macOS, Linux)")
        self.cicd_build_matrix.setChecked(True)
        cicd_sub_layout.addRow("", self.cicd_build_matrix)

        self.cicd_run_tests = QCheckBox("Run tests in CI")
        self.cicd_run_tests.setChecked(True)
        cicd_sub_layout.addRow("", self.cicd_run_tests)

        self.cicd_sub_widget.setVisible(False)
        cicd_layout.addWidget(self.cicd_sub_widget)

        cicd_group.setLayout(cicd_layout)

        # -- Code signing options ----------------------------------------
        signing_group = QGroupBox("Code Signing")
        signing_layout = QVBoxLayout()

        self.enable_signing = QCheckBox("Enable code signing")
        self.enable_signing.setChecked(False)
        self.enable_signing.setToolTip(
            "Required for notarised macOS builds and AUv3 distribution."
        )
        signing_layout.addWidget(self.enable_signing)

        # Signing sub-options (shown when enabled)
        self.signing_sub_widget = QWidget()
        signing_sub_layout = QFormLayout(self.signing_sub_widget)
        signing_sub_layout.setContentsMargins(20, 0, 0, 0)

        self.signing_team_id = QLineEdit()
        self.signing_team_id.setPlaceholderText("ABCDE12345")
        self.signing_team_id.setToolTip("Your 10-character Apple Developer Team ID.")
        signing_sub_layout.addRow("Apple Team ID:", self.signing_team_id)

        self.signing_certificate = QLineEdit()
        self.signing_certificate.setPlaceholderText(
            'e.g. "Developer ID Application: Your Name (ABCDE12345)"'
        )
        self.signing_certificate.setToolTip(
            "The exact name of the signing certificate in your Keychain."
        )
        signing_sub_layout.addRow("Certificate Name:", self.signing_certificate)

        self.signing_sub_widget.setVisible(False)
        signing_layout.addWidget(self.signing_sub_widget)

        signing_group.setLayout(signing_layout)

        # -- Progress indicator & navigation -----------------------------
        self.progress_label = QLabel("Step 2 of 4: Configure")
        self.progress_label.setStyleSheet("color: #666; font-style: italic;")

        nav_layout = QHBoxLayout()
        self.back_button = QPushButton("← Back to Define")
        self.continue_button = QPushButton("Continue to Implement →")

        nav_layout.addWidget(self.back_button)
        nav_layout.addStretch()
        nav_layout.addWidget(self.continue_button)

        # -- Assemble main layout ----------------------------------------
        layout.addWidget(project_group)
        layout.addWidget(company_group)
        layout.addWidget(formats_group)
        layout.addWidget(build_group)
        layout.addWidget(cicd_group)
        layout.addWidget(signing_group)
        layout.addWidget(self.progress_label)
        layout.addStretch()
        layout.addLayout(nav_layout)

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

        # Connect format checkboxes
        for checkbox in [self.standalone, self.vst3, self.au, self.auv3, self.clap]:
            checkbox.stateChanged.connect(self._on_format_changed)

    # ------------------------------------------------------------------
    # Signal connections
    # ------------------------------------------------------------------

    def setup_connections(self):
        """Connect signals to slots"""
        self.project_name.textChanged.connect(self._on_project_name_changed)
        self.product_name.textChanged.connect(self._on_config_changed)
        self.company_name.textChanged.connect(self._on_config_changed)
        self.bundle_id.textChanged.connect(self._on_config_changed)
        self.manufacturer_code.textChanged.connect(self._on_config_changed)

        self.browse_output_button.clicked.connect(self._browse_output_dir)
        self.output_directory.textChanged.connect(self._on_config_changed)

        self.github_actions.toggled.connect(self._on_github_actions_toggled)
        self.cicd_build_matrix.stateChanged.connect(self._on_config_changed)
        self.cicd_run_tests.stateChanged.connect(self._on_config_changed)

        self.enable_signing.toggled.connect(self._on_signing_toggled)
        self.signing_team_id.textChanged.connect(self._on_config_changed)
        self.signing_certificate.textChanged.connect(self._on_config_changed)

        self.back_button.clicked.connect(self._go_back_to_define)
        self.continue_button.clicked.connect(self._continue_to_implement)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

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
    def _on_format_changed(self):
        """Handle format checkbox changes and update disclosure label"""
        self._update_format_disclosure()
        self._emit_config_changed()
        self._update_validation_state()

    @Slot(bool)
    def _on_github_actions_toggled(self, checked: bool):
        """Show/hide GitHub Actions sub-options"""
        self.cicd_sub_widget.setVisible(checked)
        self._on_config_changed()

    @Slot(bool)
    def _on_signing_toggled(self, checked: bool):
        """Show/hide code-signing sub-options"""
        self.signing_sub_widget.setVisible(checked)
        self._on_config_changed()

    @Slot()
    def _browse_output_dir(self):
        """Open file dialog to select build output directory"""
        start_dir = self.output_directory.text().strip() or QDir.homePath()
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory", start_dir)
        if directory:
            self.output_directory.setText(directory)

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

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _any_format_selected(self) -> bool:
        """Return True if at least one plugin format checkbox is checked."""
        return any(
            cb.isChecked()
            for cb in [self.standalone, self.vst3, self.au, self.auv3, self.clap]
        )

    def _update_format_disclosure(self):
        """Update the format-specific disclosure label based on selected formats."""
        notes = []
        format_map = {
            "standalone": self.standalone,
            "vst3": self.vst3,
            "au": self.au,
            "auv3": self.auv3,
            "clap": self.clap,
        }
        for key, checkbox in format_map.items():
            if checkbox.isChecked():
                notes.append(_FORMAT_NOTES[key])

        self.format_disclosure_label.setText("\n".join(notes))
        self.format_disclosure_label.setVisible(bool(notes))

        has_formats = bool(notes)
        self.format_error_label.setVisible(not has_formats)

    def _update_validation_state(self):
        """Update validation state based on field values"""
        is_valid = (
            bool(self.project_name.text().strip())
            and bool(self.product_name.text().strip())
            and bool(self.company_name.text().strip())
            and bool(self.bundle_id.text().strip())
            and len(self.manufacturer_code.text().strip()) == 4
            and self._any_format_selected()
        )
        self._emit_validation_changed(is_valid)
        self.continue_button.setEnabled(is_valid)

    # ------------------------------------------------------------------
    # BaseTab interface
    # ------------------------------------------------------------------

    def get_configuration(self):
        """Get current configuration from the tab"""
        return {
            "project_name": self.project_name.text().strip(),
            "product_name": self.product_name.text().strip(),
            "company_name": self.company_name.text().strip(),
            "bundle_id": self.bundle_id.text().strip(),
            "manufacturer_code": self.manufacturer_code.text().strip(),
            # Plugin formats
            "standalone": self.standalone.isChecked(),
            "vst3": self.vst3.isChecked(),
            "au": self.au.isChecked(),
            "auv3": self.auv3.isChecked(),
            "clap": self.clap.isChecked(),
            # Build options
            "output_directory": self.output_directory.text().strip(),
            # CI/CD
            "github_actions": self.github_actions.isChecked(),
            "cicd_build_matrix": self.cicd_build_matrix.isChecked(),
            "cicd_run_tests": self.cicd_run_tests.isChecked(),
            # Code signing
            "enable_signing": self.enable_signing.isChecked(),
            "signing_team_id": self.signing_team_id.text().strip(),
            "signing_certificate": self.signing_certificate.text().strip(),
            "tab_complete": self._is_valid,
        }

    def load_configuration(self, config):
        """Load configuration into the tab"""
        self.project_name.setText(config.get("project_name", ""))
        self.product_name.setText(config.get("product_name", ""))
        self.company_name.setText(config.get("company_name", "DirektDSP"))
        self.bundle_id.setText(config.get("bundle_id", ""))
        self.manufacturer_code.setText(config.get("manufacturer_code", "Ddsp"))
        # Plugin formats
        self.standalone.setChecked(config.get("standalone", False))
        self.vst3.setChecked(config.get("vst3", True))
        self.au.setChecked(config.get("au", True))
        self.auv3.setChecked(config.get("auv3", False))
        self.clap.setChecked(config.get("clap", True))
        # Build options
        self.output_directory.setText(config.get("output_directory", ""))
        # CI/CD
        self.github_actions.setChecked(config.get("github_actions", False))
        self.cicd_build_matrix.setChecked(config.get("cicd_build_matrix", True))
        self.cicd_run_tests.setChecked(config.get("cicd_run_tests", True))
        # Code signing
        self.enable_signing.setChecked(config.get("enable_signing", False))
        self.signing_team_id.setText(config.get("signing_team_id", ""))
        self.signing_certificate.setText(config.get("signing_certificate", ""))

        self._update_format_disclosure()
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

        if not self._any_format_selected():
            errors.append("At least one plugin format must be selected")

        return not errors

    def reset(self):
        """Reset the tab to its default state"""
        self.project_name.clear()
        self.product_name.clear()
        self.company_name.setText("DirektDSP")
        self.bundle_id.clear()
        self.manufacturer_code.setText("Ddsp")
        # Plugin formats
        self.standalone.setChecked(False)
        self.vst3.setChecked(True)
        self.au.setChecked(True)
        self.auv3.setChecked(False)
        self.clap.setChecked(True)
        # Build options
        self.output_directory.clear()
        # CI/CD
        self.github_actions.setChecked(False)
        self.cicd_build_matrix.setChecked(True)
        self.cicd_run_tests.setChecked(True)
        # Code signing
        self.enable_signing.setChecked(False)
        self.signing_team_id.clear()
        self.signing_certificate.clear()

        self._update_format_disclosure()
        self._update_validation_state()
        self._emit_config_changed()
