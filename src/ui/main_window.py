from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QSplitter,
    QMenuBar, QMenu, QMessageBox, QToolBar,
    QStatusBar, QApplication
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QAction

from ui.project_panel import ProjectPanel
from ui.options_panel import OptionsPanel
from ui.progress_panel import ProgressPanel
from ui.preset_panel import PresetPanel

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, theme_manager=None, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.setup_ui()
        self.setup_connections()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        
        # Set window properties
        self.setWindowTitle("Plugin Configurator")
        self.resize(900, 700)
    
    def setup_ui(self):
        """Initialize UI components"""
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create preset panel at the top
        self.preset_panel = PresetPanel()
        self.main_layout.addWidget(self.preset_panel)
        
        # Create horizontal splitter for main content
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: project and options in a vertical splitter
        self.left_splitter = QSplitter(Qt.Orientation.Vertical)
        self.project_panel = ProjectPanel()
        self.options_panel = OptionsPanel()
        self.left_splitter.addWidget(self.project_panel)
        self.left_splitter.addWidget(self.options_panel)
        self.left_splitter.setStretchFactor(0, 1)  # Project panel gets more space
        self.left_splitter.setStretchFactor(1, 2)  # Options panel gets more space
        
        # Right side: progress panel
        self.progress_panel = ProgressPanel()
        
        # Add panels to main splitter
        self.main_splitter.addWidget(self.left_splitter)
        self.main_splitter.addWidget(self.progress_panel)
        self.main_splitter.setStretchFactor(0, 2)  # Left side gets more space
        self.main_splitter.setStretchFactor(1, 1)  # Right side gets less space
        
        # Add main splitter to layout
        self.main_layout.addWidget(self.main_splitter)
        
        # Set central widget
        self.setCentralWidget(self.central_widget)
    
    def setup_connections(self):
        """Connect signals between UI components"""
        # Connect project panel signals to progress panel
        self.project_panel.log_message.connect(self.progress_panel.log_message)
        self.project_panel.update_progress.connect(self.progress_panel.update_progress)
        
        # Connect preset panel signals
        self.preset_panel.log_message.connect(self.progress_panel.log_message)
        self.preset_panel.preset_loaded.connect(self.project_panel.load_preset)
        
        # Connect save preset functionality
        self.preset_panel.save_button.clicked.connect(self.save_current_as_preset)
    
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
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        # Add actions to file menu
        file_menu.addAction(new_action)
        file_menu.addAction(save_preset_action)
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
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        
        # Add actions to help menu
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Set up application toolbar"""
        # Create toolbar
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Toolbar actions
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_project)
        
        save_preset_action = QAction("Save Preset", self)
        save_preset_action.triggered.connect(self.save_current_as_preset)
        
        # Add actions to toolbar
        toolbar.addAction(new_action)
        toolbar.addAction(save_preset_action)
    
    def setup_statusbar(self):
        """Set up status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def new_project(self):
        """Reset form for a new project"""
        # Reset panels
        self.project_panel.fill_form_from_config(self.project_panel.config_manager.get_default_config())
        self.progress_panel.clear_log()
        self.progress_panel.reset_progress()
        self.status_bar.showMessage("New project started")
        self.progress_panel.log_message("Started new project")
    
    def save_current_as_preset(self):
        """Save current configuration as a preset"""
        # Get config from project panel
        project_config = self.project_panel.get_form_config()
        
        # Get options from options panel
        options_config = self.options_panel.get_options()
        
        # Combine configs
        full_config = {**project_config, **options_config}
        
        # Save as preset
        self.preset_panel.save_config_as_preset(full_config)
        self.status_bar.showMessage("Preset saved")
    
    def change_theme(self, theme_name):
        """Change application theme"""
        if self.theme_manager:
            QApplication.instance().setStyleSheet(self.theme_manager.get_stylesheet(theme_name))
            self.status_bar.showMessage(f"Theme changed to {theme_name}")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, 
            "About Plugin Configurator",
            "Plugin Configurator\n\n"
            "A tool for generating audio plugin projects from templates.\n\n"
            "Developed by DirektDSP\n"
            "Version 1.0.0"
        )
