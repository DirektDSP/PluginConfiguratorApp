from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QMenu, QMenuBar, QStatusBar, QSplitter, QMessageBox
)
from PySide6.QtCore import Qt, Slot, QThread
from PySide6.QtGui import QAction, QIcon

from ui.project_panel import ProjectPanel
from ui.options_panel import OptionsPanel
from ui.progress_panel import ProgressPanel
from core.project_worker import ProjectWorker  # Changed from workers.project_worker to core.project_worker

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, theme_manager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.setup_ui()
        self.setup_actions()
        self.setup_menus()
        self.setup_connections()
        self.setWindowTitle("Plugin Configurator")
        self.resize(1000, 700)
    
    def setup_ui(self):
        """Initialize UI components"""
        # Central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Horizontal layout for panels
        self.panel_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create panels
        self.project_panel = ProjectPanel()
        self.options_panel = OptionsPanel()
        
        # Add panels to splitter
        self.panel_splitter.addWidget(self.project_panel)
        self.panel_splitter.addWidget(self.options_panel)
        self.panel_splitter.setSizes([400, 600])
        
        # Progress panel at the bottom
        self.progress_panel = ProgressPanel()
        
        # Add widgets to main layout
        self.main_layout.addWidget(self.panel_splitter, 3)
        self.main_layout.addWidget(self.progress_panel, 1)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
    
    def setup_actions(self):
        """Create actions for menus and toolbars"""
        # File actions
        self.action_new = QAction("New Configuration", self)
        self.action_open = QAction("Open Configuration...", self)
        self.action_save = QAction("Save Configuration...", self)
        self.action_exit = QAction("Exit", self)
        
        # Theme actions
        self.action_theme_light = QAction("Light Theme", self)
        self.action_theme_dark = QAction("Dark Theme", self)
        
        # Help actions
        self.action_about = QAction("About", self)
        self.action_docs = QAction("Documentation", self)
    
    def setup_menus(self):
        """Create application menus"""
        self.menu_bar = QMenuBar()
        self.setMenuBar(self.menu_bar)
        
        # File menu
        self.file_menu = QMenu("&File", self)
        self.file_menu.addAction(self.action_new)
        self.file_menu.addAction(self.action_open)
        self.file_menu.addAction(self.action_save)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.action_exit)
        
        # View menu
        self.view_menu = QMenu("&View", self)
        self.themes_menu = QMenu("Themes", self)
        self.themes_menu.addAction(self.action_theme_light)
        self.themes_menu.addAction(self.action_theme_dark)
        self.view_menu.addMenu(self.themes_menu)
        
        # Help menu
        self.help_menu = QMenu("&Help", self)
        self.help_menu.addAction(self.action_docs)
        self.help_menu.addAction(self.action_about)
        
        # Add menus to menu bar
        self.menu_bar.addMenu(self.file_menu)
        self.menu_bar.addMenu(self.view_menu)
        self.menu_bar.addMenu(self.help_menu)
    
    def setup_connections(self):
        """Connect signals to slots"""
        # File actions
        self.action_open.triggered.connect(self.open_config)
        self.action_save.triggered.connect(self.save_config)
        self.action_exit.triggered.connect(self.close)
        
        # Theme actions
        self.action_theme_light.triggered.connect(lambda: self.change_theme("light"))
        self.action_theme_dark.triggered.connect(lambda: self.change_theme("dark"))
        
        # Connect project panel to progress panel
        self.project_panel.log_message.connect(self.progress_panel.log_message)
        self.project_panel.update_progress.connect(self.progress_panel.update_progress)
        
        # Connect project generation button directly (alternative to parent traversal)
        self.project_panel.generate_button.clicked.connect(self.generate_project)

    @Slot()
    def open_config(self):
        """Open and load a configuration file"""
        self.project_panel.open_config()
    
    @Slot()
    def save_config(self):
        """Save the current configuration to a file"""
        self.project_panel.save_config()
    
    @Slot(str)
    def change_theme(self, theme_name):
        """Change the application theme"""
        stylesheet = self.theme_manager.get_stylesheet(theme_name)
        self.setStyleSheet(stylesheet)
    
    @Slot()
    def generate_project(self):
        """Generate project with options from options panel"""
        try:
            # Get project parameters
            params = self.project_panel.get_project_parameters()
            
            # Add options from the options panel
            params['options'] = self.options_panel.get_options()
            
            # Create and run worker
            self.worker_thread = QThread()
            self.worker = ProjectWorker(params)
            self.worker.moveToThread(self.worker_thread)
            
            # Connect signals
            self.worker_thread.started.connect(self.worker.run)
            self.worker.progress.connect(self.progress_panel.log_message)
            self.worker.progress_value.connect(self.progress_panel.update_progress)
            self.worker.finished.connect(self.worker_thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker_thread.finished.connect(self.worker_thread.deleteLater)
            self.worker.error.connect(self.show_error)
            
            # Disable generate button during processing
            self.project_panel.generate_button.setEnabled(False)
            self.progress_panel.log_message("Starting project generation...")
            self.progress_panel.update_progress(0)
            
            # Start the thread
            self.worker_thread.start()
            
            # Re-enable button when done
            self.worker_thread.finished.connect(
                lambda: self.project_panel.generate_button.setEnabled(True)
            )
            
        except ValueError as e:
            self.show_error(str(e))

    @Slot(str)
    def show_error(self, message):
        """Display error message"""
        QMessageBox.critical(self, "Error", message)
