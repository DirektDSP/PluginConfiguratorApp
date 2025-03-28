from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QFormLayout, 
    QLineEdit, QPushButton, QLabel, QHBoxLayout,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Signal, QObject, QThread, Slot
from PySide6.QtGui import QIcon

from core.config_manager import ConfigManager
from core.project_worker import ProjectWorker

class ProjectPanel(QWidget):
    """Panel for project information input"""
    
    # Signals
    log_message = Signal(str)
    update_progress = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = ConfigManager()
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Initialize UI components"""
        self.layout = QVBoxLayout(self)
        
        # Group box for project info
        self.group_box = QGroupBox("Project Information")
        self.form_layout = QFormLayout()
        
        # Project name field
        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText("No spaces, only letters and numbers")
        self.form_layout.addRow("Project Name:", self.project_name)
        
        # Fork URL field
        self.fork_url = QLineEdit()
        self.fork_url.setPlaceholderText("https://github.com/user/repo.git")
        self.fork_url.setText("https://github.com/SeamusMullan/PluginTemplate.git")
        self.form_layout.addRow("Template Repository:", self.fork_url)
        
        # Product name field
        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("Display name in DAWs")
        self.form_layout.addRow("Product Name:", self.product_name)
        
        # Company name field
        self.company_name = QLineEdit()
        self.company_name.setPlaceholderText("DirektDSP")
        self.company_name.setText("DirektDSP")
        self.form_layout.addRow("Company Name:", self.company_name)
        
        # Bundle ID field
        self.bundle_id = QLineEdit()
        self.bundle_id.setPlaceholderText("com.direktdsp.pluginname")
        self.form_layout.addRow("Bundle ID:", self.bundle_id)
        
        # Manufacturer code field
        self.manufacturer_code = QLineEdit()
        self.manufacturer_code.setPlaceholderText("Manu")
        self.manufacturer_code.setText("Ddsp")
        self.form_layout.addRow("Manufacturer Code:", self.manufacturer_code)
        
        # Output directory selection
        self.output_dir_layout = QHBoxLayout()
        self.output_directory = QLineEdit()
        self.output_directory.setPlaceholderText("Select output directory")
        self.browse_button = QPushButton("Browse...")
        self.output_dir_layout.addWidget(self.output_directory)
        self.output_dir_layout.addWidget(self.browse_button)
        self.form_layout.addRow("Output Directory:", self.output_dir_layout)
        
        # Add form layout to group box
        self.group_box.setLayout(self.form_layout)
        
        # Generate button
        self.generate_button = QPushButton("Generate Project")
        self.generate_button.setMinimumHeight(40)
        
        # Add widgets to main layout
        self.layout.addWidget(self.group_box)
        self.layout.addWidget(self.generate_button)
        self.layout.addStretch()
    
    def setup_connections(self):
        """Connect signals to slots"""
        self.project_name.textChanged.connect(self.update_bundle_id)
        self.browse_button.clicked.connect(self.browse_output_dir)
        self.generate_button.clicked.connect(self.generate_project)
    
    @Slot(str)
    def update_bundle_id(self, text):
        """Automatically update bundle ID based on project name"""
        if text:
            self.bundle_id.setText(f"com.direktdsp.{text.lower()}")
    
    @Slot()
    def browse_output_dir(self):
        """Open file dialog to select output directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", ""
        )
        if directory:
            self.output_directory.setText(directory)
    
    def get_project_parameters(self):
        """Collect and validate project parameters"""
        params = {
            "project_name": self.project_name.text().strip(),
            "fork_url": self.fork_url.text().strip(),
            "product_name": self.product_name.text().strip(),
            "company_name": self.company_name.text().strip() or "DirektDSP",
            "bundle_id": self.bundle_id.text().strip(),
            "manufacturer_code": self.manufacturer_code.text().strip() or "Ddsp",
            "output_directory": self.output_directory.text().strip()
        }
        
        # Validate required fields
        if not params["project_name"]:
            raise ValueError("Project name is required")
        if not params["product_name"]:
            raise ValueError("Product name is required")
        if not params["fork_url"]:
            raise ValueError("Template repository URL is required")
        if not params["output_directory"]:
            raise ValueError("Output directory is required")
            
        return params
    
    @Slot()
    def generate_project(self):
        """Start the project generation process"""
        try:
            params = self.get_project_parameters()
            
            # Create worker and thread
            self.worker_thread = QThread()
            self.worker = ProjectWorker(params)
            self.worker.moveToThread(self.worker_thread)
            
            # Connect signals
            self.worker_thread.started.connect(self.worker.run)
            self.worker.progress.connect(self.log_message)
            self.worker.progress_value.connect(self.update_progress)
            self.worker.finished.connect(self.worker_thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker_thread.finished.connect(self.worker_thread.deleteLater)
            self.worker.error.connect(self.show_error)
            
            # Disable inputs during processing
            self.generate_button.setEnabled(False)
            self.log_message.emit("Starting project generation...")
            self.update_progress.emit(0)
            
            # Start the thread
            self.worker_thread.start()
            
            # Re-enable the button when done
            self.worker_thread.finished.connect(
                lambda: self.generate_button.setEnabled(True)
            )
            
        except ValueError as e:
            self.show_error(str(e))
    
    @Slot(str)
    def show_error(self, message):
        """Display error message"""
        QMessageBox.critical(self, "Error", message)
    
    def open_config(self):
        """Open and load configuration from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Configuration", "", "XML Files (*.xml)"
        )
        if file_path:
            try:
                config = self.config_manager.load_config(file_path)
                self.fill_form_from_config(config)
                self.log_message.emit(f"Configuration loaded from {file_path}")
            except Exception as e:
                self.show_error(f"Failed to load configuration: {str(e)}")
    
    def save_config(self):
        """Save current configuration to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Configuration", "", "XML Files (*.xml)"
        )
        if file_path:
            try:
                config = self.get_form_config()
                self.config_manager.save_config(config, file_path)
                self.log_message.emit(f"Configuration saved to {file_path}")
            except Exception as e:
                self.show_error(f"Failed to save configuration: {str(e)}")
    
    def get_form_config(self):
        """Collect form data for saving configuration"""
        config = {
            "project_name": self.project_name.text(),
            "fork_url": self.fork_url.text(),
            "product_name": self.product_name.text(),
            "company_name": self.company_name.text(),
            "bundle_id": self.bundle_id.text(),
            "manufacturer_code": self.manufacturer_code.text(),
            "output_directory": self.output_directory.text()
        }
        return config
    
    def fill_form_from_config(self, config):
        """Populate form fields from loaded configuration"""
        self.project_name.setText(config.get("project_name", ""))
        self.fork_url.setText(config.get("fork_url", ""))
        self.product_name.setText(config.get("product_name", ""))
        self.company_name.setText(config.get("company_name", ""))
        self.bundle_id.setText(config.get("bundle_id", ""))
        self.manufacturer_code.setText(config.get("manufacturer_code", ""))
        self.output_directory.setText(config.get("output_directory", ""))
