from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.utils import generate_plugin_id


class ProjectTab(QWidget):
    """Tab for configuring project information"""

    # Signals
    project_configured = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Initialize UI components"""
        self.layout = QVBoxLayout(self)

        # Project information group
        self.project_group = QGroupBox("Project Information")
        self.project_layout = QFormLayout()

        # Project name field
        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText("No spaces, only letters and numbers")
        self.project_layout.addRow("Project Name:", self.project_name)

        # Product name field
        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("Display name in DAWs")
        self.project_layout.addRow("Product Name:", self.product_name)

        self.project_group.setLayout(self.project_layout)

        # Company information group
        self.company_group = QGroupBox("Company Information")
        self.company_layout = QFormLayout()

        # Company name field
        self.company_name = QLineEdit()
        self.company_name.setPlaceholderText("Your Company Name")
        self.company_name.setText("DirektDSP")
        self.company_layout.addRow("Company Name:", self.company_name)

        # Bundle ID field
        self.bundle_id = QLineEdit()
        self.bundle_id.setPlaceholderText("com.yourcompany.pluginname")
        self.company_layout.addRow("Bundle ID:", self.bundle_id)

        # Manufacturer code field
        self.manufacturer_code = QLineEdit()
        self.manufacturer_code.setPlaceholderText("Four character code")
        self.manufacturer_code.setText("Ddsp")
        self.manufacturer_code.setMaxLength(4)
        self.company_layout.addRow("Manufacturer Code:", self.manufacturer_code)

        # Plugin code field with generate button
        plugin_code_layout = QHBoxLayout()
        self.plugin_code = QLineEdit()
        self.plugin_code.setPlaceholderText("Auto-generated")
        self.plugin_code.setMaxLength(4)
        self.generate_code_button = QPushButton("Generate")
        plugin_code_layout.addWidget(self.plugin_code)
        plugin_code_layout.addWidget(self.generate_code_button)
        self.company_layout.addRow("Plugin Code:", plugin_code_layout)

        self.company_group.setLayout(self.company_layout)

        # Output directory group
        self.output_group = QGroupBox("Output Settings")
        self.output_layout = QFormLayout()

        # Output directory selection
        self.output_dir_layout = QHBoxLayout()
        self.output_directory = QLineEdit()
        self.output_directory.setPlaceholderText("Select output directory")
        self.browse_button = QPushButton("Browse...")
        self.output_dir_layout.addWidget(self.output_directory)
        self.output_dir_layout.addWidget(self.browse_button)
        self.output_layout.addRow("Output Directory:", self.output_dir_layout)

        self.output_group.setLayout(self.output_layout)

        # Continue button
        self.continue_button = QPushButton("Continue to Options")
        self.continue_button.setMinimumHeight(40)

        # Add groups to main layout
        self.layout.addWidget(self.project_group)
        self.layout.addWidget(self.company_group)
        self.layout.addWidget(self.output_group)
        self.layout.addWidget(self.continue_button)
        self.layout.addStretch()

    def setup_connections(self):
        """Connect signals to slots"""
        self.project_name.textChanged.connect(self.update_from_project_name)
        self.browse_button.clicked.connect(self.browse_output_dir)
        self.generate_code_button.clicked.connect(self.generate_plugin_code)
        self.continue_button.clicked.connect(self.continue_to_options)

    @Slot(str)
    def update_from_project_name(self, text):
        """Update other fields based on project name"""
        # Update product name if empty
        if not self.product_name.text():
            # Replace underscores with spaces and capitalize words
            product_name = text.replace("_", " ").title()
            self.product_name.setText(product_name)

        # Update bundle ID
        company = self.company_name.text().lower().replace(" ", "")
        plugin = text.lower().replace(" ", "")
        if company and plugin:
            self.bundle_id.setText(f"com.{company}.{plugin}")

    @Slot()
    def browse_output_dir(self):
        """Open file dialog to select output directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory", "")
        if directory:
            self.output_directory.setText(directory)

    @Slot()
    def generate_plugin_code(self):
        """Generate and set a random plugin code"""
        code = generate_plugin_id()
        self.plugin_code.setText(code)

    @Slot()
    def continue_to_options(self):
        """Continue to options tab after validating project info"""
        if self.validate():
            config = self.get_configuration()
            self.project_configured.emit(config)
        else:
            QMessageBox.warning(
                self, "Validation Error", "Please complete all required fields before continuing."
            )

    def get_configuration(self):
        """Get current project configuration"""
        return {
            "project_name": self.project_name.text().strip(),
            "product_name": self.product_name.text().strip(),
            "company_name": self.company_name.text().strip(),
            "bundle_id": self.bundle_id.text().strip(),
            "manufacturer_code": self.manufacturer_code.text().strip(),
            "plugin_code": self.plugin_code.text().strip() or generate_plugin_id(),
            "output_directory": self.output_directory.text().strip(),
        }

    def load_configuration(self, config):
        """Load configuration into the UI"""
        self.project_name.setText(config.get("project_name", ""))
        self.product_name.setText(config.get("product_name", ""))
        self.company_name.setText(config.get("company_name", "DirektDSP"))
        self.bundle_id.setText(config.get("bundle_id", ""))
        self.manufacturer_code.setText(config.get("manufacturer_code", "Ddsp"))
        self.plugin_code.setText(config.get("plugin_code", ""))
        self.output_directory.setText(config.get("output_directory", ""))

    def update_from_template(self, template_config):
        """Update relevant fields based on selected template"""
        # If this template suggests a default project name pattern, apply it
        if "template_name" in template_config and not self.project_name.text():
            # Create a default project name from template name
            template_name = template_config["template_name"]
            suggested_name = template_name.replace(" ", "")
            self.project_name.setText(suggested_name)

    def validate(self):
        """Validate that all required information is provided"""
        required_fields = [
            (self.project_name, "Project Name"),
            (self.product_name, "Product Name"),
            (self.company_name, "Company Name"),
            (self.bundle_id, "Bundle ID"),
            (self.manufacturer_code, "Manufacturer Code"),
            (self.output_directory, "Output Directory"),
        ]

        for field, _name in required_fields:
            if not field.text().strip():
                return False

        # Validate manufacturer code is exactly 4 characters
        if len(self.manufacturer_code.text().strip()) != 4:
            QMessageBox.warning(
                self, "Validation Error", "Manufacturer Code must be exactly 4 characters."
            )
            return False

        # Generate plugin code if empty
        if not self.plugin_code.text().strip():
            self.generate_plugin_code()

        return True

    def reset(self):
        """Reset form to default values"""
        self.project_name.clear()
        self.product_name.clear()
        self.company_name.setText("DirektDSP")
        self.bundle_id.clear()
        self.manufacturer_code.setText("Ddsp")
        self.plugin_code.clear()
        self.output_directory.clear()
