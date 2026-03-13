from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QButtonGroup,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)


class TemplateTab(QWidget):
    """Tab for selecting and configuring the project template"""

    # Signals
    template_selected = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()

        # Add some default templates
        self.add_default_templates()

    def setup_ui(self):
        """Initialize UI components"""
        self.layout = QVBoxLayout(self)

        # Template type selection
        self.template_type_group = QGroupBox("Template Source")
        self.template_type_layout = QHBoxLayout()

        # Radio buttons for template source
        self.repository_radio = QRadioButton("Repository")
        self.local_radio = QRadioButton("Local Template")
        self.repository_radio.setChecked(True)

        # Add to button group for mutual exclusivity
        self.source_group = QButtonGroup()
        self.source_group.addButton(self.repository_radio)
        self.source_group.addButton(self.local_radio)

        self.template_type_layout.addWidget(self.repository_radio)
        self.template_type_layout.addWidget(self.local_radio)
        self.template_type_group.setLayout(self.template_type_layout)

        # Repository URL input
        self.repo_group = QGroupBox("Repository Template")
        self.repo_layout = QFormLayout()

        self.repo_url = QLineEdit()
        self.repo_url.setPlaceholderText("https://github.com/username/repo.git")
        self.repo_url.setText("https://github.com/SeamusMullan/PluginTemplate.git")

        self.repo_branch = QLineEdit()
        self.repo_branch.setPlaceholderText("main")
        self.repo_branch.setText("main")

        self.repo_layout.addRow("Repository URL:", self.repo_url)
        self.repo_layout.addRow("Branch:", self.repo_branch)

        # Use predefined template button
        self.predefined_button = QPushButton("Use Predefined Template")
        self.repo_layout.addRow("", self.predefined_button)

        self.repo_group.setLayout(self.repo_layout)

        # Local template selection
        self.local_group = QGroupBox("Local Template")
        self.local_layout = QFormLayout()

        self.local_path = QLineEdit()
        self.local_path.setPlaceholderText("Select local template directory")
        self.browse_button = QPushButton("Browse...")

        self.local_path_layout = QHBoxLayout()
        self.local_path_layout.addWidget(self.local_path)
        self.local_path_layout.addWidget(self.browse_button)

        self.local_layout.addRow("Template Directory:", self.local_path_layout)
        self.local_group.setLayout(self.local_layout)
        self.local_group.setEnabled(False)

        # Predefined templates area
        self.predefined_group = QGroupBox("Predefined Templates")
        self.predefined_layout = QVBoxLayout()

        self.template_list = QListWidget()
        self.template_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

        self.predefined_layout.addWidget(self.template_list)
        self.predefined_group.setLayout(self.predefined_layout)

        # Template description and info
        self.info_group = QGroupBox("Template Information")
        self.info_layout = QVBoxLayout()

        self.template_description = QLabel("Select a template to see its description")
        self.template_description.setWordWrap(True)
        self.template_features = QLabel("")
        self.template_features.setWordWrap(True)

        self.info_layout.addWidget(self.template_description)
        self.info_layout.addWidget(self.template_features)
        self.info_group.setLayout(self.info_layout)

        # Continue button
        self.continue_button = QPushButton("Continue to Project Configuration")
        self.continue_button.setMinimumHeight(40)

        # Add widgets to main layout
        self.layout.addWidget(self.template_type_group)
        self.layout.addWidget(self.repo_group)
        self.layout.addWidget(self.local_group)
        self.layout.addWidget(self.predefined_group)
        self.layout.addWidget(self.info_group)
        self.layout.addWidget(self.continue_button)

    def setup_connections(self):
        """Connect signals to slots"""
        # Radio button connections
        self.repository_radio.toggled.connect(self.toggle_template_source)
        self.local_radio.toggled.connect(self.toggle_template_source)

        # Button connections
        self.browse_button.clicked.connect(self.browse_local_template)
        self.predefined_button.clicked.connect(self.show_predefined_templates)
        self.continue_button.clicked.connect(self.continue_to_project)

        # List selection connection
        self.template_list.itemSelectionChanged.connect(self.update_template_info)

    def add_default_templates(self):
        """Add default templates to the list"""
        # Basic Audio Plugin template
        basic_item = QListWidgetItem("Internal DirektDSP Template")
        basic_item.setData(Qt.ItemDataRole.UserRole, {
            "name": "Internal DirektDSP Template",
            "url": "https://github.com/SeamusMullan/PluginTemplate.git",
            "branch": "main",
            "description": "A basic audio plugin template based on Pamplejuce, with JUCE and CMake setup.",
            "features": "- Modern C++ with CMake\n- JUCE framework\n- Cross-platform\n- CI/CD ready"
        })
        self.template_list.addItem(basic_item)

        # Audio FX Plugin template
        fx_item = QListWidgetItem("Audio FX Plugin")
        fx_item.setData(Qt.ItemDataRole.UserRole, {
            "name": "Audio FX Plugin",
            "url": "https://github.com/DirektDSP/FXPluginTemplate.git",
            "branch": "main",
            "description": "A template for creating audio effect plugins with common structures.",
            "features": "- Effect parameter framework\n- Preset system\n- Modulation routing\n- Visualizers"
        })
        self.template_list.addItem(fx_item)

        # Instrument Plugin template
        instrument_item = QListWidgetItem("Instrument Plugin")
        instrument_item.setData(Qt.ItemDataRole.UserRole, {
            "name": "Instrument Plugin",
            "url": "https://github.com/DirektDSP/InstrumentTemplate.git",
            "branch": "main",
            "description": "A template for creating virtual instrument plugins.",
            "features": "- MIDI processing\n- Voice management\n- Polyphony control\n- Sample playback"
        })
        self.template_list.addItem(instrument_item)

    @Slot(bool)
    def toggle_template_source(self, checked):
        """Toggle between repository and local template sources"""
        if self.repository_radio.isChecked():
            self.repo_group.setEnabled(True)
            self.local_group.setEnabled(False)
        else:
            self.repo_group.setEnabled(False)
            self.local_group.setEnabled(True)

    @Slot()
    def browse_local_template(self):
        """Browse for local template directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Template Directory", ""
        )
        if directory:
            self.local_path.setText(directory)

    @Slot()
    def show_predefined_templates(self):
        """Show the predefined templates section"""
        # Ensure the predefined group is visible
        self.predefined_group.setVisible(True)

    @Slot()
    def update_template_info(self):
        """Update template info when selection changes"""
        selected_items = self.template_list.selectedItems()
        if selected_items:
            template_data = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.template_description.setText(template_data["description"])
            self.template_features.setText(template_data["features"])

            # Update repository fields
            self.repo_url.setText(template_data["url"])
            self.repo_branch.setText(template_data["branch"])

    @Slot()
    def continue_to_project(self):
        """Continue to project configuration tab"""
        # Get template configuration
        config = self.get_configuration()

        # Emit signal for selected template
        self.template_selected.emit(config)

    def get_configuration(self):
        """Get current template configuration"""
        config = {}

        # Repository or local path based on selection
        if self.repository_radio.isChecked():
            config["template_type"] = "repository"
            config["fork_url"] = self.repo_url.text().strip()
            config["branch"] = self.repo_branch.text().strip()
        else:
            config["template_type"] = "local"
            config["template_path"] = self.local_path.text().strip()

        # If a predefined template is selected, include its info
        selected_items = self.template_list.selectedItems()
        if selected_items:
            template_data = selected_items[0].data(Qt.ItemDataRole.UserRole)
            config["template_name"] = template_data["name"]
            config["template_description"] = template_data["description"]

        return config

    def load_configuration(self, config):
        """Load configuration into the UI"""
        # Set template source
        if config.get("template_type") == "local":
            self.local_radio.setChecked(True)
            self.local_path.setText(config.get("template_path", ""))
        else:
            self.repository_radio.setChecked(True)
            self.repo_url.setText(config.get("fork_url", ""))
            self.repo_branch.setText(config.get("branch", "main"))

        # Try to select the predefined template by name if it exists
        if "template_name" in config:
            for i in range(self.template_list.count()):
                item = self.template_list.item(i)
                template_data = item.data(Qt.ItemDataRole.UserRole)
                if template_data["name"] == config["template_name"]:
                    self.template_list.setCurrentItem(item)
                    break

    def validate(self):
        """Validate that all required information is provided"""
        if self.repository_radio.isChecked():
            return bool(self.repo_url.text().strip())
        else:
            return bool(self.local_path.text().strip())

    def reset(self):
        """Reset form to default values"""
        self.repository_radio.setChecked(True)
        self.repo_url.setText("https://github.com/SeamusMullan/PluginTemplate.git")
        self.repo_branch.setText("main")
        self.local_path.clear()
        self.template_list.clearSelection()
        self.template_description.setText("Select a template to see its description")
        self.template_features.setText("")
