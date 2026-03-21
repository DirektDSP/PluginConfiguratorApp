from functools import partial

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

from core.config_manager import ConfigurationManager
from ui.tabs.configure_tab import ConfigureTab
from ui.tabs.define_tab import DefineTab
from ui.tabs.generate_tab import GenerateTab
from ui.tabs.implement_tab import ImplementTab


class MainWindow(QMainWindow):
    """Main application window with tabbed interface"""

    def __init__(self, theme_manager=None, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.config_manager = ConfigurationManager()
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
        self.define_tab = DefineTab()
        self.configure_tab = ConfigureTab()
        self.implement_tab = ImplementTab()
        self.generate_tab = GenerateTab()
        self._tab_registry = {
            self.define_tab: "define",
            self.configure_tab: "configure",
            self.implement_tab: "implement",
            self.generate_tab: "generate",
        }
        self._tab_order = [
            self.define_tab,
            self.configure_tab,
            self.implement_tab,
            self.generate_tab,
        ]

        # Add tabs to tab widget in the specified order
        self.tab_widget.addTab(self.define_tab, "Define")
        self.tab_widget.addTab(self.configure_tab, "Configure")
        self.tab_widget.addTab(self.implement_tab, "Implement")
        self.tab_widget.addTab(self.generate_tab, "Generate")

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
            # Bind tab instance so handlers know which tab emitted the signal.
            tab.config_changed.connect(partial(self._on_tab_config_changed, tab))
            tab.validation_changed.connect(partial(self._on_tab_validation_changed, tab))
        self._sync_configuration_from_tabs()

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
        return self._tab_order

    def _sync_configuration_from_tabs(self):
        """Initialize configuration manager from current tab states."""
        for tab in self._all_tabs():
            config = tab.get_configuration()
            tab_name = self._tab_registry.get(tab)
            if tab_name:
                self.config_manager.update_config(tab_name, config)
            self._update_quick_start_from_config(tab, config)
        self._update_generate_preview()

    def _update_quick_start_from_config(self, tab, config):
        """Sync quick-start state when the define tab emits updates."""
        if tab is self.define_tab and "quick_start_mode" in config:
            self._sync_quick_start(config["quick_start_mode"])

    def _sync_quick_start(self, desired_state):
        """Ensure quick-start flag matches the requested state.

        Args:
            desired_state: Desired value of the quick-start mode flag.
        """
        self.config_manager.set_quick_start(desired_state)

    def _update_generate_preview(self):
        """Update the Generate tab with the latest full configuration."""
        self.generate_tab.update_full_config(self.config_manager.get_full_config())

    @Slot()
    def new_project(self):
        """Reset form for a new project"""
        # Reset all tabs using the BaseTab interface
        for tab in self._all_tabs():
            tab.reset()
        self._sync_configuration_from_tabs()

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
        self._update_generate_preview()
        self.generate_tab.save_as_preset()
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

        # Update configuration and switch to generate tab
        self._update_generate_preview()
        self.tab_widget.setCurrentWidget(self.generate_tab)

        # Start generation process
        self.generate_tab.generate_project()

    def validate_all_tabs(self):
        """Validate all tabs using the ConfigurationManager"""
        return self.config_manager.validate_all(self._all_tabs())

    @Slot(dict)
    def load_preset_to_all_tabs(self, config):
        """Load preset configuration to all tabs using the BaseTab interface"""
        # Tabs accept the full config dict and extract relevant keys internally.
        for tab in self._all_tabs():
            tab.load_configuration(config)
        self._sync_configuration_from_tabs()

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

    @Slot(object, dict)
    def _on_tab_config_changed(self, tab, config):
        """Handle configuration change from any tab.

        Args:
            tab: Tab instance that emitted the signal.
            config: Configuration payload from the emitting tab.
        """
        tab_name = self._tab_registry.get(tab)
        if tab_name:
            self.config_manager.update_config(tab_name, config)
        self._update_quick_start_from_config(tab, config)
        self._update_generate_preview()
        self.status_bar.showMessage("Configuration updated")

    @Slot(object, bool)
    def _on_tab_validation_changed(self, tab, is_valid):
        """Handle validation state change from any tab.

        Args:
            tab: Tab instance that emitted the signal.
            is_valid: Whether the emitting tab is currently valid.
        """
        # Will be implemented as validation UI indicators are added.
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
