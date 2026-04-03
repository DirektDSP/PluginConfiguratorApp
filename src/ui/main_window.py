from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.config_manager import ConfigManager
from ui.components import FileTreePreview
from ui.dialogs import PresetLoadDialog, PresetManagementDialog
from ui.tabs.configuration_tab import ConfigurationTab
from ui.tabs.development_workflow_tab import DevelopmentWorkflowTab
from ui.tabs.generate_tab import GenerateTab
from ui.tabs.implementations_tab import ImplementationsTab
from ui.tabs.project_info_tab import ProjectInfoTab
from ui.tabs.user_experience_tab import UserExperienceTab

PREVIEW_MIN_WIDTH = 340
GENERATE_TAB_INDEX = 5


class MainWindow(QMainWindow):
    """Main application window with tabbed interface"""

    def __init__(self, theme_manager=None, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self._config_manager = ConfigManager()
        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
        self.setup_connections()

        # Set window properties
        self.setWindowTitle("Plugin Configurator")
        self.resize(900, 700)

    def setup_ui(self):
        """Initialize UI components with tabs"""
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)

        # Create tab widget
        self.tab_widget = QTabWidget()

        # File tree preview (persistent across tabs)
        self.file_tree_preview = FileTreePreview()
        self.file_tree_preview.setMinimumWidth(PREVIEW_MIN_WIDTH)

        # Create tabs with the new structure
        self.project_info_tab = ProjectInfoTab()
        self.implementations_tab = ImplementationsTab()
        self.configuration_tab = ConfigurationTab()
        self.user_experience_tab = UserExperienceTab()
        self.development_workflow_tab = DevelopmentWorkflowTab()
        self.generate_tab = GenerateTab()

        # Add tabs to tab widget in the specified order
        self.tab_widget.addTab(self.project_info_tab, "Project Info")
        self.tab_widget.addTab(self.implementations_tab, "Implementations")
        self.tab_widget.addTab(self.configuration_tab, "Configuration")
        self.tab_widget.addTab(self.user_experience_tab, "User Experience")
        self.tab_widget.addTab(self.development_workflow_tab, "Development Workflow")
        self.tab_widget.addTab(self.generate_tab, "Generate")

        # Splitter keeps preview visible alongside tabs
        self.content_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.content_splitter.setChildrenCollapsible(False)
        self.content_splitter.addWidget(self.tab_widget)
        self.content_splitter.addWidget(self.file_tree_preview)
        self.content_splitter.setStretchFactor(0, 3)
        self.content_splitter.setStretchFactor(1, 2)

        # Add splitter to main layout
        self.main_layout.addWidget(self.content_splitter)

        # Progress bar at the bottom of main window
        self.global_progress_bar = QProgressBar()
        self.global_progress_bar.setRange(0, 100)
        self.global_progress_bar.setValue(0)
        self.global_progress_bar.setTextVisible(True)
        self.global_progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.global_progress_bar)

        # Set central widget
        self.setCentralWidget(self.central_widget)

    def setup_connections(self):
        """Connect signals between UI components"""
        # Connect tab change signals
        self.tab_widget.currentChanged.connect(self.handle_tab_changed)

        # Connect config_changed signals from all tabs to update status
        for tab in self._all_tabs():
            tab.config_changed.connect(self._on_tab_config_changed)
            tab.validation_changed.connect(self._on_tab_validation_changed)

        # Initialize persistent preview with defaults
        self._update_file_tree_preview()

        # Initialize the generate-button state from the start
        self._update_global_validation_status()

    def setup_menu(self):
        """Set up application menu"""
        # Create menu bar
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&File")

        # File menu actions
        new_action = QAction("&New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)

        load_preset_action = QAction("&Load Preset…", self)
        load_preset_action.setShortcut("Ctrl+L")
        load_preset_action.triggered.connect(self.show_load_preset_dialog)

        save_preset_action = QAction("&Save as Preset", self)
        save_preset_action.setShortcut("Ctrl+S")
        save_preset_action.triggered.connect(self.save_current_as_preset)

        manage_presets_action = QAction("&Manage Presets…", self)
        manage_presets_action.setShortcut("Ctrl+M")
        manage_presets_action.triggered.connect(self.show_preset_management)

        generate_action = QAction("&Generate Project", self)
        generate_action.setShortcut("Ctrl+G")
        generate_action.triggered.connect(self.generate_project)

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        # Add actions to file menu
        file_menu.addAction(new_action)
        file_menu.addAction(load_preset_action)
        file_menu.addAction(save_preset_action)
        file_menu.addAction(manage_presets_action)
        file_menu.addAction(generate_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # Theme menu
        if self.theme_manager:
            theme_menu = menu_bar.addMenu("&Theme")

            # Theme menu actions
            light_theme_action = QAction("&Light", self)
            light_theme_action.triggered.connect(lambda: self.change_theme("light"))

            dark_theme_action = QAction("&Dark", self)
            dark_theme_action.triggered.connect(lambda: self.change_theme("dark"))

            # Add actions to theme menu
            theme_menu.addAction(light_theme_action)
            theme_menu.addAction(dark_theme_action)

        # Help menu
        help_menu = menu_bar.addMenu("&Help")

        # Help menu actions
        doc_action = QAction("&Documentation", self)
        doc_action.triggered.connect(self.show_documentation)

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)

        # Add actions to help menu
        help_menu.addAction(doc_action)
        help_menu.addAction(about_action)

    def setup_statusbar(self):
        """Set up status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _all_tabs(self):
        """Return all configuration tabs as a list"""
        return [
            self.project_info_tab,
            self.implementations_tab,
            self.configuration_tab,
            self.user_experience_tab,
            self.development_workflow_tab,
            self.generate_tab,
        ]

    def _config_tabs(self):
        """Return the configuration tabs (all tabs except the Generate summary tab)."""
        return [
            self.project_info_tab,
            self.implementations_tab,
            self.configuration_tab,
            self.user_experience_tab,
            self.development_workflow_tab,
        ]

    @Slot()
    def new_project(self):
        """Reset form for a new project"""
        # Reset all tabs using the BaseTab interface
        for tab in self._all_tabs():
            tab.reset()

        # Reset progress
        self.global_progress_bar.setValue(0)

        # Update status
        self.status_bar.showMessage("New project started")
        self.update_status("Started new project")
        self._update_file_tree_preview()

        # Switch to project info tab
        self.tab_widget.setCurrentIndex(0)

    @Slot()
    def save_current_as_preset(self):
        """Save current configuration as a preset"""
        self.collect_configuration()
        self.status_bar.showMessage("Preset saved")

    @Slot()
    def show_preset_management(self):
        """Open the preset management dialog."""
        dialog = PresetManagementDialog(self._config_manager, parent=self)
        dialog.exec()

    @Slot()
    def show_load_preset_dialog(self):
        """Open the preset load dialog and apply the chosen preset to all tabs."""
        dialog = PresetLoadDialog(self._config_manager, parent=self)
        if not dialog.exec():
            return

        preset_name = dialog.selected_preset_name()
        if preset_name is None:
            return

        try:
            config = self._config_manager.load_preset(preset_name)
        except ValueError as exc:
            QMessageBox.warning(
                self,
                "Load Preset Failed",
                f'Could not load preset "{preset_name}":\n{exc}',
            )
            return

        self.load_preset_to_all_tabs(config)
        self.status_bar.showMessage(f'Preset "{preset_name}" loaded')

    @Slot()
    def generate_project(self):
        """Start the project generation process"""
        # Switch to the Generate tab so the user can review and trigger generation
        self.tab_widget.setCurrentIndex(GENERATE_TAB_INDEX)  # Generate tab index

        # Refresh the generate tab's summary with the latest configuration
        config = self.collect_configuration()
        self.generate_tab.update_full_config(config)
        self._update_file_tree_preview(config)

    def quick_start_review_generate(self):
        """Apply quick-start defaults and navigate to the Generate tab."""
        self._apply_quick_start_defaults()
        config = self.collect_configuration()
        self.generate_tab.update_full_config(config)
        self._update_file_tree_preview(config)
        self.tab_widget.setCurrentIndex(GENERATE_TAB_INDEX)
        self.status_bar.showMessage("Quick Start: Review & Generate")

    def collect_configuration(self):
        """Collect configuration from all tabs using the BaseTab interface"""
        return {
            "project_info": self.project_info_tab.get_configuration(),
            "implementations": self.implementations_tab.get_configuration(),
            "configuration": self.configuration_tab.get_configuration(),
            "user_experience": self.user_experience_tab.get_configuration(),
            "development_workflow": self.development_workflow_tab.get_configuration(),
        }

    def validate_all_tabs(self):
        """Validate all tabs using the BaseTab interface"""
        return all(tab.validate() for tab in self._all_tabs())

    @Slot(dict)
    def load_preset_to_all_tabs(self, config):
        """Load preset configuration to all tabs using the BaseTab interface"""
        self.project_info_tab.load_configuration(config.get("project_info", {}))
        self.implementations_tab.load_configuration(config.get("implementations", {}))
        self.configuration_tab.load_configuration(config.get("configuration", {}))
        self.user_experience_tab.load_configuration(config.get("user_experience", {}))
        self.development_workflow_tab.load_configuration(config.get("development_workflow", {}))
        self.generate_tab.load_configuration(config.get("generate", {}))
        self._update_file_tree_preview(config)

    @Slot(str)
    def update_status(self, message):
        """Update status bar and log message"""
        self.status_bar.showMessage(message)
        # Will be implemented as we add functionality to the tabs

    @Slot(int)
    def handle_tab_changed(self, index):
        """Handle when the user changes tabs"""
        # Refresh the Generate tab summary whenever it becomes active
        if index == GENERATE_TAB_INDEX:  # Generate tab
            config = self.collect_configuration()
            self.generate_tab.update_full_config(config)
            self._update_file_tree_preview(config)

    @Slot(dict)
    def _on_tab_config_changed(self, config):
        """Handle configuration change from any tab"""
        self._update_file_tree_preview()
        self._update_global_validation_status()

    @Slot(bool)
    def _on_tab_validation_changed(self, is_valid):
        """Handle validation state change from any tab"""
        self._update_global_validation_status()

    def _update_global_validation_status(self) -> None:
        """Aggregate validation issues from all config tabs and update the UI.

        Collects human-readable issues from every configuration tab, updates
        the status bar with a concise overall status, and forwards the result
        to the Generate tab so the Generate button can be enabled or disabled
        with an informative tooltip listing all outstanding issues.
        """
        all_issues: list[str] = []
        for tab in self._config_tabs():
            all_issues.extend(tab.get_validation_issues())

        is_valid = not all_issues
        if is_valid:
            self.status_bar.showMessage("✅ All configuration valid — ready to generate")
        else:
            count = len(all_issues)
            self.status_bar.showMessage(
                f"❌ {count} issue{'s' if count != 1 else ''} found — fix before generating"
            )

        self.generate_tab.set_global_validation(is_valid, all_issues)

    def change_theme(self, theme_name):
        """Change application theme"""
        if self.theme_manager:
            QApplication.instance().setStyleSheet(self.theme_manager.get_stylesheet(theme_name))
            self.status_bar.showMessage(f"Theme changed to {theme_name}")

    def show_documentation(self):
        """Show documentation"""
        QMessageBox.information(
            self,
            "Documentation",
            "Please visit our online documentation at:\n"
            "https://github.com/SeamusMullan/PluginConfiguratorApp/docs",
        )

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Plugin Configurator",
            "Plugin Configurator\n\n"
            "A tool for generating audio plugin projects from templates.\n\n"
            "Developed by DirektDSP\n"
            "Version 1.0.0",
        )

    def _update_file_tree_preview(self, config=None):
        """Refresh the persistent file tree preview with current configuration."""
        if config is None:
            config = self.collect_configuration()
        self.file_tree_preview.set_configuration(config)

    def _apply_quick_start_defaults(self):
        """Auto-populate downstream tabs with intelligent defaults for quick start."""
        configuration_defaults = {
            "standalone": False,
            "vst3": True,
            "au": True,
            "auv3": False,
            "clap": True,
            "gui_width": 800,
            "gui_height": 600,
            "resizable": False,
            "background_image": "",
            "code_signing": False,
            "installer": False,
            "default_bypass": True,
            "input_gain": True,
            "output_gain": True,
        }
        implementations_defaults = {
            "moonbase_licensing": False,
            "melatonin_inspector": True,
            "custom_gui_framework": True,
            "logging_framework": True,
            "clap_builds": True,
            "preset_management": True,
            "preset_format": "XML",
            "ab_comparison": True,
            "state_management": True,
            "gpu_audio": False,
        }
        user_experience_defaults = {
            "wizard": True,
            "preview": True,
            "preset_management": True,
        }
        development_workflow_defaults = {
            "vcs": True,
            "testing": False,
            "code_quality": True,
            "validation_tools": True,
            "scaffolding": True,
        }

        self.configuration_tab.load_configuration(configuration_defaults)
        self.implementations_tab.load_configuration(implementations_defaults)
        self.user_experience_tab.load_configuration(user_experience_defaults)
        self.development_workflow_tab.load_configuration(development_workflow_defaults)
