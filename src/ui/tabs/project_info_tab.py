"""Project info tab with metadata form and live file tree preview."""

from PySide6.QtCore import (
    QByteArray,
    QEasingCurve,
    QParallelAnimationGroup,
    QPropertyAnimation,
    Qt,
    Slot,
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGraphicsOpacityEffect,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QStyle,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.base_tab import BaseTab
from core.config_manager import ConfigurationManager
from core.utils import generate_plugin_id
from core.validators import (
    validate_bundle_id,
    validate_company_name,
    validate_manufacturer_code,
    validate_output_directory,
    validate_plugin_code,
    validate_product_name,
    validate_project_name,
    validate_version,
)
from ui.components.field_validator import FieldValidator, make_error_label
from ui.components.validation_footer import ValidationFooter


def _wrap_with_error(field, error_label):
    """Return a QWidget container holding *field* above *error_label*."""
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(2)
    layout.addWidget(field)
    layout.addWidget(error_label)
    return container


class ProjectInfoTab(BaseTab):
    """Tab for configuring project information and visualizing the project structure"""

    PLUGIN_TYPE_FX = "audio fx"
    PLUGIN_TYPE_INSTRUMENT = "instrument"
    PLUGIN_TYPE_INTERNAL = "internal"
    _ANIMATION_MS = 180

    def __init__(self, parent=None):
        super().__init__(parent)
        self._config_manager = ConfigurationManager()
        self._current_plugin_type = self.PLUGIN_TYPE_INTERNAL
        self._animations: dict[QWidget, QParallelAnimationGroup] = {}
        self._opacity_effects: dict[QWidget, QGraphicsOpacityEffect] = {}
        self.setup_ui()
        self.setup_connections()

        # Default template details
        self.current_template = {
            "name": "Default Template",
            "url": "https://github.com/SeamusMullan/PluginTemplate.git",
            "description": (
                "A basic audio plugin template based on Pamplejuce, with JUCE and CMake setup."
            ),
        }

        # Initial file tree population
        self.populate_default_file_tree()
        self._emit_config_changed()

    def setup_ui(self):
        """Initialize UI components"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to maximize space

        # Create a splitter for the left (form) and right (file tree) sides
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(5)  # Make the splitter handle thinner
        self.splitter.setChildrenCollapsible(False)  # Prevent sections from being collapsed

        # ---- LEFT SIDE - FORM FIELDS ----

        # Create a container widget for the form to add margins
        self.form_container = QWidget()
        self.form_container.setContentsMargins(10, 10, 10, 10)  # Add margins inside the container
        self.form_container.setMinimumWidth(400)  # Set minimum width to prevent over-collapsing
        form_container_layout = QVBoxLayout(self.form_container)
        form_container_layout.setContentsMargins(0, 0, 0, 0)  # No margins for the layout itself

        # Create a scroll area for the form fields
        self.form_scroll = QScrollArea()
        self.form_scroll.setWidgetResizable(True)
        self.form_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
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
        self.template_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.template_combo.addItem("Internal DirektDSP Template")
        self.template_combo.addItem("Audio FX Plugin")
        self.template_combo.addItem("Instrument Plugin")

        self.repo_url = QLineEdit()
        self.repo_url.setPlaceholderText("https://github.com/username/repo.git")
        self.repo_url.setText("https://github.com/SeamusMullan/PluginTemplate.git")

        self.template_layout.addRow("Template:", self.template_combo)
        self.template_layout.addRow("Repository URL:", self.repo_url)

        self.template_group.setLayout(self.template_layout)

        # Plugin type specific options (progressive disclosure)
        self.plugin_type_group = QGroupBox("Plugin Type Options")
        plugin_type_layout = QVBoxLayout()

        # Audio FX options
        self.fx_options_group = QGroupBox("Audio FX")
        fx_layout = QFormLayout()
        self.fx_wet_dry = QSpinBox()
        self.fx_wet_dry.setRange(0, 100)
        self.fx_wet_dry.setValue(50)
        fx_layout.addRow("Wet/Dry Mix (%):", self.fx_wet_dry)

        self.fx_sidechain = QCheckBox("Enable sidechain input")
        fx_layout.addRow("Sidechain:", self.fx_sidechain)

        self.fx_latency = QSpinBox()
        self.fx_latency.setRange(0, 200)
        self.fx_latency.setValue(0)
        fx_layout.addRow("Latency (ms):", self.fx_latency)
        self.fx_options_group.setLayout(fx_layout)

        # Instrument options
        self.instrument_options_group = QGroupBox("Instrument")
        instrument_layout = QFormLayout()
        self.instrument_polyphony = QSpinBox()
        self.instrument_polyphony.setRange(1, 256)
        self.instrument_polyphony.setValue(64)
        instrument_layout.addRow("Polyphony (voices):", self.instrument_polyphony)

        self.instrument_midi_input = QCheckBox("Enable MIDI input")
        self.instrument_midi_input.setChecked(True)
        instrument_layout.addRow("MIDI Input:", self.instrument_midi_input)
        self.instrument_options_group.setLayout(instrument_layout)

        plugin_type_layout.addWidget(self.fx_options_group)
        plugin_type_layout.addWidget(self.instrument_options_group)
        self.plugin_type_group.setLayout(plugin_type_layout)
        self._prepare_disclosure_section(self.fx_options_group)
        self._prepare_disclosure_section(self.instrument_options_group)

        # Project information group
        self.project_group = QGroupBox("Project Information")
        self.project_layout = QFormLayout()
        self.project_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )

        # Project name field
        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText("No spaces, only letters and numbers")
        self._project_name_error = make_error_label()
        self.project_layout.addRow("Project Name:", _wrap_with_error(self.project_name, self._project_name_error))

        # Product name field
        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("Display name in DAWs")
        self._product_name_error = make_error_label()
        self.project_layout.addRow("Product Name:", _wrap_with_error(self.product_name, self._product_name_error))

        # Version field
        self.version = QLineEdit()
        self.version.setPlaceholderText("1.0.0")
        self.version.setText("1.0.0")
        self._version_error = make_error_label()
        self.project_layout.addRow("Version:", _wrap_with_error(self.version, self._version_error))

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
        self._company_name_error = make_error_label()
        self.company_layout.addRow("Company Name:", _wrap_with_error(self.company_name, self._company_name_error))

        # Bundle ID field
        self.bundle_id = QLineEdit()
        self.bundle_id.setPlaceholderText("com.yourcompany.pluginname")
        self._bundle_id_error = make_error_label()
        self.company_layout.addRow("Bundle ID:", _wrap_with_error(self.bundle_id, self._bundle_id_error))

        # Manufacturer code field
        self.manufacturer_code = QLineEdit()
        self.manufacturer_code.setPlaceholderText("Four character code")
        self.manufacturer_code.setText("Ddsp")
        self.manufacturer_code.setMaxLength(4)
        self._manufacturer_code_error = make_error_label()
        self.company_layout.addRow("Manufacturer Code:", _wrap_with_error(self.manufacturer_code, self._manufacturer_code_error))

        # Plugin code field with generate button
        plugin_code_layout = QHBoxLayout()
        self.plugin_code = QLineEdit()
        self.plugin_code.setPlaceholderText("Auto-generated")
        self.plugin_code.setMaxLength(4)
        self.generate_code_button = QPushButton("Generate")
        plugin_code_layout.addWidget(self.plugin_code)
        plugin_code_layout.addWidget(self.generate_code_button)
        self._plugin_code_error = make_error_label()
        plugin_code_container = QWidget()
        plugin_code_container_layout = QVBoxLayout(plugin_code_container)
        plugin_code_container_layout.setContentsMargins(0, 0, 0, 0)
        plugin_code_container_layout.setSpacing(2)
        plugin_code_container_layout.addLayout(plugin_code_layout)
        plugin_code_container_layout.addWidget(self._plugin_code_error)
        self.company_layout.addRow("Plugin Code:", plugin_code_container)

        self.company_group.setLayout(self.company_layout)

        # Output directory group
        self.output_group = QGroupBox("Output Settings")
        self.output_layout = QFormLayout()
        self.output_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        # Output directory selection
        self.output_dir_layout = QHBoxLayout()
        self.output_directory = QLineEdit()
        self.output_directory.setPlaceholderText("Select output directory")
        self.browse_button = QPushButton("Browse...")
        self.output_dir_layout.addWidget(self.output_directory)
        self.output_dir_layout.addWidget(self.browse_button)
        self._output_directory_error = make_error_label()
        output_dir_container = QWidget()
        output_dir_container_layout = QVBoxLayout(output_dir_container)
        output_dir_container_layout.setContentsMargins(0, 0, 0, 0)
        output_dir_container_layout.setSpacing(2)
        output_dir_container_layout.addLayout(self.output_dir_layout)
        output_dir_container_layout.addWidget(self._output_directory_error)
        self.output_layout.addRow("Output Directory:", output_dir_container)

        self.output_group.setLayout(self.output_layout)

        # Quick start group
        self.quick_start_group = QGroupBox("Quick Start")
        quick_start_layout = QVBoxLayout()
        self.quick_start_checkbox = QCheckBox("Enable Quick Start")
        self.quick_start_checkbox.setToolTip(
            "Skip the detailed steps and jump straight to Review & Generate with sensible defaults."
        )
        quick_actions_layout = QHBoxLayout()
        self.review_generate_button = QPushButton("Review & Generate")
        self.review_generate_button.setEnabled(False)
        quick_actions_layout.addWidget(self.review_generate_button)
        quick_actions_layout.addStretch()
        quick_start_layout.addWidget(self.quick_start_checkbox)
        quick_start_layout.addLayout(quick_actions_layout)
        self.quick_start_group.setLayout(quick_start_layout)

        # Add all groups to the form layout
        self.form_layout.addWidget(self.template_group)
        self.form_layout.addWidget(self.plugin_type_group)
        self.form_layout.addWidget(self.project_group)
        self.form_layout.addWidget(self.company_group)
        self.form_layout.addWidget(self.output_group)
        self.form_layout.addWidget(self.quick_start_group)
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
        self.filetree_container.setMinimumWidth(300)  # Set minimum width to prevent over-collapsing
        filetree_container_layout = QVBoxLayout(self.filetree_container)
        filetree_container_layout.setContentsMargins(0, 0, 0, 0)  # No margins for the layout itself

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
        self.file_tree.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

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

        # Validation footer - shows required-field count and allows jump-to-fix
        self.validation_footer = ValidationFooter(self)
        self.main_layout.addWidget(self.validation_footer)

    def setup_connections(self):
        """Connect signals to slots"""
        self.project_name.textChanged.connect(self.update_from_project_name)
        self.browse_button.clicked.connect(self.browse_output_dir)
        self.generate_code_button.clicked.connect(self.generate_plugin_code)
        self.template_combo.currentIndexChanged.connect(self.update_template_selection)
        self.repo_url.textChanged.connect(self.update_repo_url)
        self.project_name.textChanged.connect(self.update_file_tree)
        self.quick_start_checkbox.toggled.connect(self._on_quick_start_toggled)
        self.review_generate_button.clicked.connect(self._on_review_generate_clicked)
        for spin in [self.fx_wet_dry, self.fx_latency, self.instrument_polyphony]:
            spin.valueChanged.connect(self._on_plugin_type_option_changed)
        for checkbox in [self.fx_sidechain, self.instrument_midi_input]:
            checkbox.toggled.connect(self._on_plugin_type_option_changed)
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
            widget.textChanged.connect(self._update_quick_start_button_state)
            widget.textChanged.connect(self._update_validation_footer)
        self._update_quick_start_button_state()
        self._update_plugin_type_sections()
        # Connect footer's fix_requested to focus the first invalid field
        self.validation_footer.fix_requested.connect(self.focus_first_invalid)
        # Set initial footer state
        self._update_validation_footer()
        self._wire_field_validators()

    def _wire_field_validators(self):
        """Attach real-time validators with visual feedback to all form fields."""
        self._field_validators: list[FieldValidator] = [
            FieldValidator(self.project_name, self._project_name_error, validate_project_name),
            FieldValidator(self.product_name, self._product_name_error, validate_product_name),
            FieldValidator(
                self.version, self._version_error, validate_version, validate_on_empty=True
            ),
            FieldValidator(self.company_name, self._company_name_error, validate_company_name),
            FieldValidator(self.bundle_id, self._bundle_id_error, validate_bundle_id),
            FieldValidator(
                self.manufacturer_code,
                self._manufacturer_code_error,
                validate_manufacturer_code,
            ),
            FieldValidator(self.plugin_code, self._plugin_code_error, validate_plugin_code),
            FieldValidator(
                self.output_directory,
                self._output_directory_error,
                validate_output_directory,
            ),
        ]
        # Show initial feedback for fields that already have pre-populated values.
        for fv in self._field_validators:
            fv.trigger_validation()

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

    @Slot(int)
    def update_template_selection(self, index):
        """Update template information based on selection"""
        if index == 0:  # Internal DirektDSP Template
            self.current_template = {
                "name": "Internal DirektDSP Template",
                "url": "https://github.com/SeamusMullan/PluginTemplate.git",
                "description": (
                    "A basic audio plugin template based on Pamplejuce, with JUCE and CMake setup."
                ),
            }
            self._current_plugin_type = self.PLUGIN_TYPE_INTERNAL
        elif index == 1:  # Audio FX Plugin
            self.current_template = {
                "name": "Audio FX Plugin",
                "url": "https://github.com/DirektDSP/FXPluginTemplate.git",
                "description": "A template for creating audio effect plugins with common structures.",
            }
            self._current_plugin_type = self.PLUGIN_TYPE_FX
        elif index == 2:  # Instrument Plugin
            self.current_template = {
                "name": "Instrument Plugin",
                "url": "https://github.com/DirektDSP/InstrumentTemplate.git",
                "description": "A template for creating virtual instrument plugins.",
            }
            self._current_plugin_type = self.PLUGIN_TYPE_INSTRUMENT
        else:
            self._current_plugin_type = self.PLUGIN_TYPE_INTERNAL

        # Update repo URL field
        self.repo_url.setText(self.current_template["url"])

        self._update_plugin_type_sections()
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

    def _add_file_item(self, parent, name, *, disabled=False):
        """Create a file tree item with icon, optionally disabled."""
        item = QTreeWidgetItem(parent, [name])
        icon = self.get_file_icon(name)
        if icon:
            item.setIcon(0, icon)
        item.setDisabled(disabled)
        return item

    def _add_folder_item(self, parent, name):
        """Create a folder tree item with icon."""
        item = QTreeWidgetItem(parent, [name])
        icon = self.get_folder_icon()
        if icon:
            item.setIcon(0, icon)
        return item

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
            dir_item = self._add_folder_item(parent_item, dir_name)
            for file_name in files:
                self._add_file_item(dir_item, file_name)

        # Add top-level files
        top_files = [
            "CMakeLists.txt",
            "README.md",
            f"{project_name}.jucer",
            ".gitignore",
            "LICENSE",
        ]

        for file_name in top_files:
            self._add_file_item(parent_item, file_name)

        plugin_type = self._current_plugin_type
        if plugin_type == self.PLUGIN_TYPE_FX:
            fx_item = self._add_folder_item(parent_item, "fx")
            self._add_file_item(fx_item, f"WetDryMix_{self.fx_wet_dry.value()}pct.cpp")
            self._add_file_item(
                fx_item,
                "SidechainInput.cpp",
                disabled=not self.fx_sidechain.isChecked(),
            )
            self._add_file_item(
                fx_item,
                f"Latency_{self.fx_latency.value()}ms.cpp",
                disabled=self.fx_latency.value() == 0,
            )
        elif plugin_type == self.PLUGIN_TYPE_INSTRUMENT:
            instrument_item = self._add_folder_item(parent_item, "instrument")
            self._add_file_item(
                instrument_item,
                f"VoiceManager_{self.instrument_polyphony.value()}voices.cpp",
            )
            self._add_file_item(
                instrument_item,
                "MidiInput.cpp",
                disabled=not self.instrument_midi_input.isChecked(),
            )

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
            "quick_start": self.quick_start_checkbox.isChecked(),
            "plugin_type": self._current_plugin_type,
            "instrument_polyphony": self.instrument_polyphony.value(),
            "instrument_midi_input": self.instrument_midi_input.isChecked(),
            "fx_wet_dry": self.fx_wet_dry.value(),
            "fx_sidechain": self.fx_sidechain.isChecked(),
            "fx_latency": self.fx_latency.value(),
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

        # Plugin type specific settings
        self._current_plugin_type = self._normalize_plugin_type(
            config.get("plugin_type", self._current_plugin_type)
        )
        self.fx_wet_dry.setValue(config.get("fx_wet_dry", self.fx_wet_dry.value()))
        self.fx_sidechain.setChecked(config.get("fx_sidechain", self.fx_sidechain.isChecked()))
        self.fx_latency.setValue(config.get("fx_latency", self.fx_latency.value()))
        self.instrument_polyphony.setValue(
            config.get("instrument_polyphony", self.instrument_polyphony.value())
        )
        self.instrument_midi_input.setChecked(
            config.get("instrument_midi_input", self.instrument_midi_input.isChecked())
        )
        self._update_plugin_type_sections()

        # Quick start flag (optional)
        quick_start_enabled = config.get("quick_start", False)
        self.quick_start_checkbox.setChecked(bool(quick_start_enabled))
        self._config_manager.set_quick_start(bool(quick_start_enabled))
        self._update_quick_start_button_state()

        # Update file tree based on loaded config
        self.update_file_tree()

    def validate(self):
        """Validate that all required information is provided"""
        if not self._validate_required_fields(show_messages=True):
            return False

        # Generate plugin code if empty
        if not self.plugin_code.text().strip():
            self.generate_plugin_code()

        return True

    def get_required_fields(self) -> list:
        """Return (widget, label) pairs for all required text fields."""
        return [
            (self.project_name, "Project Name"),
            (self.product_name, "Product Name"),
            (self.company_name, "Company Name"),
            (self.bundle_id, "Bundle ID"),
            (self.manufacturer_code, "Manufacturer Code"),
            (self.output_directory, "Output Directory"),
        ]

    def get_invalid_field_count(self) -> int:
        """Count required fields that are empty or otherwise invalid."""
        count = 0
        for widget, _label in self.get_required_fields():
            if not widget.text().strip():
                count += 1
        # Manufacturer code also requires exactly 4 characters
        if not self._is_manufacturer_code_valid():
            count += 1
        return count

    def focus_first_invalid(self):
        """Scroll to and focus the first empty required field."""
        for widget, _label in self.get_required_fields():
            if not widget.text().strip():
                widget.setFocus()
                self.form_scroll.ensureWidgetVisible(widget)
                return
        # If all fields filled but manufacturer code length is wrong, focus it
        if not self._is_manufacturer_code_valid():
            self.manufacturer_code.setFocus()
            self.form_scroll.ensureWidgetVisible(self.manufacturer_code)

    def _is_manufacturer_code_valid(self) -> bool:
        """Return True only if the manufacturer code is exactly 4 non-empty characters."""
        code = self.manufacturer_code.text().strip()
        # An empty code is caught by the required-field check, not here
        return not code or len(code) == 4

    @Slot()
    def _update_validation_footer(self, _text=None):
        """Refresh the validation footer to reflect the current field state."""
        remaining = self.get_invalid_field_count()
        if remaining == 0:
            self.validation_footer.set_ready()
        else:
            self.validation_footer.set_errors(remaining)

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
        self.quick_start_checkbox.setChecked(False)
        self.review_generate_button.setEnabled(False)
        self.fx_wet_dry.setValue(50)
        self.fx_sidechain.setChecked(False)
        self.fx_latency.setValue(0)
        self.instrument_polyphony.setValue(64)
        self.instrument_midi_input.setChecked(True)
        self._current_plugin_type = self.PLUGIN_TYPE_INTERNAL
        self._update_plugin_type_sections()
        self.update_file_tree()

    @Slot()
    def _on_plugin_type_option_changed(self, _value=None):
        """Refresh previews when plugin-type-specific controls change."""
        self.update_file_tree()
        self._emit_config_changed()

    @Slot()
    def _on_form_field_changed(self, _value=None):
        """Emit configuration changes when text fields change (BaseTab helper)."""
        self._emit_config_changed()

    @Slot(bool)
    def _on_quick_start_toggled(self, checked: bool):
        """Update quick start flag in configuration manager and button state."""
        self._config_manager.set_quick_start(checked)
        self._update_quick_start_button_state()
        self._emit_config_changed()

    @Slot()
    def _on_review_generate_clicked(self):
        """Validate and jump to the Review & Generate tab with defaults."""
        if not self.validate():
            self._update_quick_start_button_state()
            return

        main_window = self.window()
        if hasattr(main_window, "quick_start_review_generate"):
            main_window.quick_start_review_generate()
        self._update_quick_start_button_state()

    def _has_required_quick_start_data(self) -> bool:
        """Check required fields without showing dialogs for button state."""
        return self._validate_required_fields(show_messages=False)

    def _update_quick_start_button_state(self, *_args):
        """Provide visual feedback on whether quick start can proceed."""
        ready = self.quick_start_checkbox.isChecked() and self._has_required_quick_start_data()
        self.review_generate_button.setEnabled(ready)
        if ready:
            self.review_generate_button.setToolTip(
                "All required fields look good. Jump to Review & Generate."
            )
        elif not self.quick_start_checkbox.isChecked():
            self.review_generate_button.setToolTip("Enable Quick Start to jump ahead.")
        else:
            self.review_generate_button.setToolTip(
                "Fill all required fields (including a 4-character manufacturer code) to continue."
            )

    def _validate_required_fields(self, show_messages: bool = True) -> bool:
        """Shared validation helper for quick-start readiness and formal validation."""
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
                if show_messages:
                    QMessageBox.warning(self, "Validation Error", f"{name} is required.")
                return False

        if len(self.manufacturer_code.text().strip()) != 4:
            if show_messages:
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    "Manufacturer Code must be exactly 4 characters.",
                )
            return False
        return True

    # ------------------------------------------------------------------ #
    # Progressive disclosure helpers                                     #
    # ------------------------------------------------------------------ #
    def _prepare_disclosure_section(self, widget: QWidget):
        """Initialize collapsible section with hidden state and opacity."""
        effect = QGraphicsOpacityEffect(widget)
        effect.setOpacity(0.0)
        widget.setGraphicsEffect(effect)
        widget.setMaximumHeight(0)
        widget.setVisible(False)
        self._opacity_effects[widget] = effect

    def _normalize_plugin_type(self, value: str) -> str:
        normalized = (value or "").strip().lower()
        if normalized in (self.PLUGIN_TYPE_FX, self.PLUGIN_TYPE_INSTRUMENT):
            return normalized
        return self.PLUGIN_TYPE_INTERNAL

    def _update_plugin_type_sections(self):
        """Show/hide plugin-type-specific groups with animations."""
        show_fx = self._current_plugin_type == self.PLUGIN_TYPE_FX
        show_instrument = self._current_plugin_type == self.PLUGIN_TYPE_INSTRUMENT
        self._animate_section(self.fx_options_group, show_fx)
        self._animate_section(self.instrument_options_group, show_instrument)

    def _animate_section(self, widget: QWidget, should_show: bool):
        """Animate section visibility for smooth disclosure."""
        if widget not in self._opacity_effects:
            return

        effect = self._opacity_effects[widget]
        target_height = widget.sizeHint().height()
        current_height = widget.maximumHeight()

        if should_show and widget.isVisible() and current_height == target_height:
            return
        if not should_show and (not widget.isVisible() or current_height == 0):
            widget.setVisible(False)
            widget.setMaximumHeight(0)
            effect.setOpacity(0.0)
            return

        widget.setVisible(True)
        start_height = current_height if current_height > 0 else 0
        end_height = target_height if should_show else 0

        height_anim = QPropertyAnimation(widget, QByteArray(b"maximumHeight"), self)
        height_anim.setDuration(self._ANIMATION_MS)
        height_anim.setStartValue(start_height)
        height_anim.setEndValue(end_height)
        height_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        opacity_anim = QPropertyAnimation(effect, QByteArray(b"opacity"), self)
        opacity_anim.setDuration(self._ANIMATION_MS)
        opacity_anim.setStartValue(effect.opacity())
        opacity_anim.setEndValue(1.0 if should_show else 0.0)
        opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        group = QParallelAnimationGroup(self)
        group.addAnimation(height_anim)
        group.addAnimation(opacity_anim)

        def finalize():
            widget.setVisible(should_show)
            widget.setMaximumHeight(target_height if should_show else 0)
            effect.setOpacity(1.0 if should_show else 0.0)

        group.finished.connect(finalize)
        self._animations[widget] = group
        group.start()
