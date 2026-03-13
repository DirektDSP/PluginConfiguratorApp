from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ui.tabs.advanced_tab import AdvancedTab
from ui.tabs.configuration_tab import ConfigurationTab
from ui.tabs.development_workflow_tab import DevelopmentWorkflowTab
from ui.tabs.implementations_tab import ImplementationsTab
from ui.tabs.project_info_tab import ProjectInfoTab
from ui.tabs.user_experience_tab import UserExperienceTab


class MainWindow(QMainWindow):
    """Main application window with tabbed interface"""

    def __init__(self, theme_manager=None, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
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

        # Create tabs with the new structure
        self.project_info_tab = ProjectInfoTab()
        self.implementations_tab = ImplementationsTab()
        self.configuration_tab = ConfigurationTab()
        self.user_experience_tab = UserExperienceTab()
        self.development_workflow_tab = DevelopmentWorkflowTab()
        self.advanced_tab = AdvancedTab()

        # Add tabs to tab widget in the specified order
        self.tab_widget.addTab(self.project_info_tab, "Project Info")
        self.tab_widget.addTab(self.implementations_tab, "Implementations")
        self.tab_widget.addTab(self.configuration_tab, "Configuration")
        self.tab_widget.addTab(self.user_experience_tab, "User Experience")
        self.tab_widget.addTab(self.development_workflow_tab, "Development Workflow")
        self.tab_widget.addTab(self.advanced_tab, "Advanced")

        # Add tab widget to main layout
        self.main_layout.addWidget(self.tab_widget)

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

        save_preset_action = QAction("&Save as Preset", self)
        save_preset_action.setShortcut("Ctrl+S")
        save_preset_action.triggered.connect(self.save_current_as_preset)

        generate_action = QAction("&Generate Project", self)
        generate_action.setShortcut("Ctrl+G")
        generate_action.triggered.connect(self.generate_project)

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        # Add actions to file menu
        file_menu.addAction(new_action)
        file_menu.addAction(save_preset_action)
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
            self.advanced_tab,
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

        # Switch to project info tab
        self.tab_widget.setCurrentIndex(0)

    @Slot()
    def save_current_as_preset(self):
        """Save current configuration as a preset"""
        # Get configuration from all tabs
        config = self.collect_configuration()

        # Pass to advanced tab for saving
        self.advanced_tab.save_config_as_preset(config)
        self.status_bar.showMessage("Preset saved")

    @Slot()
    def generate_project(self):
        """Start the project generation process"""
        # Validate all required information
        # If any tab reports it's not ready, we can't proceed
        if not self.validate_all_tabs():
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please complete all required information before generating the project.",
            )
            return

        # Collect configuration from all tabs
        config = self.collect_configuration()

        # Switch to development workflow tab
        self.tab_widget.setCurrentIndex(4)  # Development workflow tab index

        # Start generation process
        self.development_workflow_tab.start_generation(config)

    def collect_configuration(self):
        """Collect configuration from all tabs using the BaseTab interface"""
        return {
            "project_info": self.project_info_tab.get_configuration(),
            "implementations": self.implementations_tab.get_configuration(),
            "configuration": self.configuration_tab.get_configuration(),
            "user_experience": self.user_experience_tab.get_configuration(),
            "development_workflow": self.development_workflow_tab.get_configuration(),
            "advanced": self.advanced_tab.get_configuration(),
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
        self.advanced_tab.load_configuration(config.get("advanced", {}))

    @Slot(str)
    def update_status(self, message):
        """Update status bar and log message"""
        self.status_bar.showMessage(message)
        # Will be implemented as we add functionality to the tabs

    @Slot(int)
    def handle_tab_changed(self, index):
        """Handle when the user changes tabs"""
        # Will be implemented as we add functionality to the tabs
        pass

    @Slot(dict)
    def _on_tab_config_changed(self, config):
        """Handle configuration change from any tab"""
        self.status_bar.showMessage("Configuration updated")

    @Slot(bool)
    def _on_tab_validation_changed(self, is_valid):
        """Handle validation state change from any tab"""
        pass

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
