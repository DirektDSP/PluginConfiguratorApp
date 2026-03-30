"""Project info tab with metadata form and live file tree preview."""

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStyle,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.base_tab import BaseTab
from core.utils import generate_plugin_id


class ProjectInfoTab(BaseTab):
    """Tab for configuring project information and visualizing the project structure"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()

        # Default template details
        self.current_template = {
            "name": "Default Template",
            "url": "https://github.com/SeamusMullan/PluginTemplate.git",
            "description": (
                "A basic audio plugin template based on Pamplejuce, "
                "with JUCE and CMake setup."
            ),
        }

        # Initial file tree population
        self.populate_default_file_tree()
        self._emit_config_changed()

    def setup_ui(self):
        """Initialize UI components"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(
            0, 0, 0, 0
        )  # Remove margins to maximize space

        # Create a splitter for the left (form) and right (file tree) sides
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(5)  # Make the splitter handle thinner
        self.splitter.setChildrenCollapsible(
            False
        )  # Prevent sections from being collapsed

        # ---- LEFT SIDE - FORM FIELDS ----

        # Create a container widget for the form to add margins
        self.form_container = QWidget()
        self.form_container.setContentsMargins(
            10, 10, 10, 10
        )  # Add margins inside the container
        self.form_container.setMinimumWidth(
            400
        )  # Set minimum width to prevent over-collapsing
        form_container_layout = QVBoxLayout(self.form_container)
        form_container_layout.setContentsMargins(
            0, 0, 0, 0
        )  # No margins for the layout itself

        # Create a scroll area for the form fields
        self.form_scroll = QScrollArea()
        self.form_scroll.setWidgetResizable(True)
        self.form_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.form_scroll.setFrameShape(
            QScrollArea.Shape.NoFrame
        )  # Remove border around scroll area

        # Create the form widget that will be inside the scroll area
        self.form_widget = QWidget()
        self.form_layout = QVBoxLayout(self.form_widget)
        self.form_layout.setSpacing(12)  # Add more spacing between groups

        # Template selection section
        self.template_group = QGroupBox("Template Selection")
        self.template_layout = QFormLayout()
        self.template_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )

        self.template_combo = QComboBox()
        self.template_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        self.template_combo.addItem("Internal DirektDSP Template")
        self.template_combo.addItem("Audio FX Plugin")
        self.template_combo.addItem("Instrument Plugin")

        self.repo_url = QLineEdit()
        self.repo_url.setPlaceholderText("https://github.com/username/repo.git")
        self.repo_url.setText("https://github.com/SeamusMullan/PluginTemplate.git")

        self.template_layout.addRow("Template:", self.template_combo)
        self.template_layout.addRow("Repository URL:", self.repo_url)

        self.template_group.setLayout(self.template_layout)

        # Project information group
        self.project_group = QGroupBox("Project Information")
        self.project_layout = QFormLayout()
        self.project_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )

        # Project name field
        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText("No spaces, only letters and numbers")
        self.project_layout.addRow("Project Name:", self.project_name)

        # Product name field
        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("Display name in DAWs")
        self.project_layout.addRow("Product Name:", self.product_name)

        # Version field
        self.version = QLineEdit()
        self.version.setPlaceholderText("1.0.0")
        self.version.setText("1.0.0")
        self.project_layout.addRow("Version:", self.version)

        self.project_group.setLayout(self.project_layout)

        # Company information group
        self.company_group = QGroupBox("Company Information")
        self.company_layout = QFormLayout()
        self.company_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )

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
        self.manufacturer_code.setText("NewCode")
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
        self.output_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )

        # Output directory selection
        self.output_dir_layout = QHBoxLayout()
        self.output_directory = QLineEdit()
        self.output_directory.setPlaceholderText("Select output directory")
        self.browse_button = QPushButton("Browse...")
        self.output_dir_layout.addWidget(self.output_directory)
        self.output_dir_layout.addWidget(self.browse_button)
        self.output_layout.addRow("Output Directory:", self.output_dir_layout)

        self.output_group.setLayout(self.output_layout)

        # Add all groups to the form layout
        self.form_layout.addWidget(self.template_group)
        self.form_layout.addWidget(self.project_group)
        self.form_layout.addWidget(self.company_group)
        self.form_layout.addWidget(self.output_group)
        self.form_layout.addStretch()  # Add stretch to push all groups to the top

        # Set the form widget as the widget for the scroll area
        self.form_scroll.setWidget(self.form_widget)
        form_container_layout.addWidget(self.form_scroll)

        # ---- RIGHT SIDE - FILE TREE VISUALIZATION ----

        # Create a container widget for the file tree to add margins
        self.filetree_container = QWidget()
        self.filetree_container.setContentsMargins(
            10, 10, 10, 10
        )  # Add margins inside the container
        self.filetree_container.setMinimumWidth(
            300
        )  # Set minimum width to prevent over-collapsing
        filetree_container_layout = QVBoxLayout(self.filetree_container)
        filetree_container_layout.setContentsMargins(
            0, 0, 0, 0
        )  # No margins for the layout itself

        self.filetree_widget = QWidget()
        self.filetree_layout = QVBoxLayout(self.filetree_widget)
        self.filetree_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

        # Project structure visualization
        self.structure_group = QGroupBox("Project Structure Preview")
        self.structure_layout = QVBoxLayout()

        # File tree widget
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabel("Project Files")
        self.file_tree.setMinimumWidth(250)  # Ensure a minimum width
        self.file_tree.setAlternatingRowColors(True)
        self.file_tree.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # Add tree to layout
        self.structure_layout.addWidget(self.file_tree)
        self.structure_group.setLayout(self.structure_layout)

        self.filetree_layout.addWidget(self.structure_group)
        filetree_container_layout.addWidget(self.filetree_widget)

        # Add container widgets to splitter
        self.splitter.addWidget(self.form_container)
        self.splitter.addWidget(self.filetree_container)

        # Set initial sizes for the splitter
        self.splitter.setSizes([int(self.width() * 0.6), int(self.width() * 0.4)])

        # Add splitter to main layout
        self.main_layout.addWidget(self.splitter)

    def setup_connections(self):
        """Connect signals to slots"""
        self.project_name.textChanged.connect(self.update_from_project_name)
        self.browse_button.clicked.connect(self.browse_output_dir)
        self.generate_code_button.clicked.connect(self.generate_plugin_code)
        self.template_combo.currentIndexChanged.connect(self.update_template_selection)
        self.repo_url.textChanged.connect(self.update_repo_url)
        self.project_name.textChanged.connect(self.update_file_tree)
        # Emit configuration changes for live preview updates
        text_widgets = [
            self.project_name,
            self.product_name,
            self.version,
            self.company_name,
            self.bundle_id,
            self.manufacturer_code,
            self.plugin_code,
            self.output_directory,
        ]
        for widget in text_widgets:
            widget.textChanged.connect(self._on_form_field_changed)

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
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", ""
        )
        if directory:
            self.output_directory.setText(directory)

    @Slot()
    def generate_plugin_code(self):
        """Generate and set a random plugin code"""
        code = generate_plugin_id()
        self.plugin_code.setText(code)

    @Slot(int)
    def update_template_selection(self, index):
        """Update template information based on selection"""
        if index == 0:  # Internal DirektDSP Template
            self.current_template = {
                "name": "Internal DirektDSP Template",
                "url": "https://github.com/SeamusMullan/PluginTemplate.git",
                "description": (
                    "A basic audio plugin template based on Pamplejuce, "
                    "with JUCE and CMake setup."
                ),
            }
        elif index == 1:  # Audio FX Plugin
            self.current_template = {
                "name": "Audio FX Plugin",
                "url": "https://github.com/DirektDSP/FXPluginTemplate.git",
                "description": "A template for creating audio effect plugins with common structures.",
            }
        elif index == 2:  # Instrument Plugin
            self.current_template = {
                "name": "Instrument Plugin",
                "url": "https://github.com/DirektDSP/InstrumentTemplate.git",
                "description": "A template for creating virtual instrument plugins.",
            }

        # Update repo URL field
        self.repo_url.setText(self.current_template["url"])

        # Update file tree visualization
        self.update_file_tree()
        self._emit_config_changed()

    @Slot(str)
    def update_repo_url(self, url):
        """Update current template when repo URL is changed manually"""
        if url != self.current_template["url"]:
            self.current_template = {
                "name": "Custom Template",
                "url": url,
                "description": "Custom repository URL provided by user.",
            }
        self._emit_config_changed()

    @Slot(str)
    def update_file_tree(self, _text=None):
        """Update the file tree visualization based on current settings"""
        # Clear existing tree
        self.file_tree.clear()

        # Create root item with project name or placeholder
        project_name = self.project_name.text().strip() or "YourPlugin"
        root_item = QTreeWidgetItem(self.file_tree, [project_name])
        root_item.setExpanded(True)

        # Populate based on selected template
        self.populate_file_tree(root_item, project_name)

    def populate_default_file_tree(self):
        """Populate the file tree with default structure"""
        # Clear existing tree
        self.file_tree.clear()

        # Create root item with placeholder
        root_item = QTreeWidgetItem(self.file_tree, ["YourPlugin"])
        root_item.setExpanded(True)

        # Populate with default structure
        self.populate_file_tree(root_item, "YourPlugin")

    def populate_file_tree(self, parent_item, project_name):
        """Populate the file tree with common JUCE plugin structure

        This uses a standard structure based on the Pamplejuce template
        """
        # Common directories for all templates
        common_dirs = {
            "source": [
                "PluginProcessor.cpp",
                "PluginProcessor.h",
                "PluginEditor.cpp",
                "PluginEditor.h",
            ],
            "assets": ["logo.png", "background.png"],
            "cmake": ["CPM.cmake", "PamplejuceVersion.cmake", "JUCEDefaults.cmake"],
            "JUCE": ["[JUCE framework]"],
            "tests": ["PluginBasicTest.cpp"],
            "packaging": ["icon.png", "installer_banner.png"],
            "modules": ["clap-juce-extensions", "melatonin_inspector"],
        }

        # Create directory items
        for dir_name, files in common_dirs.items():
            dir_item = QTreeWidgetItem(parent_item, [dir_name])
            folder_icon = self.get_folder_icon()
            if folder_icon:  # Only set icon if we have one
                dir_item.setIcon(0, folder_icon)

            # Add files to directory
            for file_name in files:
                file_item = QTreeWidgetItem(dir_item, [file_name])
                file_icon = self.get_file_icon(file_name)
                if file_icon:  # Only set icon if we have one
                    file_item.setIcon(0, file_icon)

        # Add top-level files
        top_files = [
            "CMakeLists.txt",
            "README.md",
            f"{project_name}.jucer",
            ".gitignore",
            "LICENSE",
        ]

        for file_name in top_files:
            file_item = QTreeWidgetItem(parent_item, [file_name])
            file_icon = self.get_file_icon(file_name)
            if file_icon:  # Only set icon if we have one
                file_item.setIcon(0, file_icon)

    def get_folder_icon(self):
        """Return a folder icon from the system"""
        try:
            # Try to get standard folder icon from the style
            return self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        except RuntimeError as e:
            print(f"Error occurred while fetching folder icon: {e}")
            # Create a simple folder icon as fallback
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.GlobalColor.transparent)
            return QIcon(pixmap)

    def get_file_icon(self, filename):
        """Return an appropriate file icon based on extension"""
        try:
            # Get icon based on file extension
            if (
                filename.endswith(".cpp")
                or filename.endswith(".h")
                or filename.endswith(".txt")
                or filename.endswith(".md")
                or filename.endswith(".png")
                or filename.endswith(".jpg")
                or filename.endswith(".jucer")
            ):
                return self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
            else:
                return self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        except RuntimeError as e:
            print(f"Error occurred while fetching file icon: {e}")
            # Create a simple file icon as fallback
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.GlobalColor.transparent)
            return QIcon(pixmap)

    def get_configuration(self):
        """Get current project configuration"""
        return {
            "template_name": self.current_template["name"],
            "template_url": self.current_template["url"],
            "project_name": self.project_name.text().strip(),
            "product_name": self.product_name.text().strip(),
            "version": self.version.text().strip() or "1.0.0",
            "company_name": self.company_name.text().strip(),
            "bundle_id": self.bundle_id.text().strip(),
            "manufacturer_code": self.manufacturer_code.text().strip(),
            "plugin_code": self.plugin_code.text().strip() or generate_plugin_id(),
            "output_directory": self.output_directory.text().strip(),
        }

    def load_configuration(self, config):
        """Load configuration into the UI"""
        # Select template if it matches a known one
        template_name = config.get("template_name", "")
        for i in range(self.template_combo.count()):
            if self.template_combo.itemText(i) == template_name:
                self.template_combo.setCurrentIndex(i)
                break

        # Set repository URL
        self.repo_url.setText(config.get("template_url", ""))

        # Set project fields
        self.project_name.setText(config.get("project_name", ""))
        self.product_name.setText(config.get("product_name", ""))
        self.version.setText(config.get("version", "1.0.0"))

        # Set company fields
        self.company_name.setText(config.get("company_name", "DirektDSP"))
        self.bundle_id.setText(config.get("bundle_id", ""))
        self.manufacturer_code.setText(config.get("manufacturer_code", "Ddsp"))
        self.plugin_code.setText(config.get("plugin_code", ""))

        # Set output directory
        self.output_directory.setText(config.get("output_directory", ""))

        # Update file tree based on loaded config
        self.update_file_tree()

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

        for field, name in required_fields:
            if not field.text().strip():
                QMessageBox.warning(self, "Validation Error", f"{name} is required.")
                return False

        # Validate manufacturer code is exactly 4 characters
        if len(self.manufacturer_code.text().strip()) != 4:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Manufacturer Code must be exactly 4 characters.",
            )
            return False

        # Generate plugin code if empty
        if not self.plugin_code.text().strip():
            self.generate_plugin_code()

        return True

    def reset(self):
        """Reset form to default values"""
        self.template_combo.setCurrentIndex(0)
        self.repo_url.setText("https://github.com/SeamusMullan/PluginTemplate.git")
        self.project_name.clear()
        self.product_name.clear()
        self.version.setText("1.0.0")
        self.company_name.setText("DirektDSP")
        self.bundle_id.clear()
        self.manufacturer_code.setText("Ddsp")
        self.plugin_code.clear()
        self.output_directory.clear()
        self.update_file_tree()

    @Slot()
    def _on_form_field_changed(self, _value=None):
        """Emit configuration changes when text fields change."""
        self._emit_config_changed()
