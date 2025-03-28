from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QComboBox, QLabel, QInputDialog, QMessageBox
)
from PySide6.QtCore import Signal

from core.config_manager import ConfigManager

class PresetPanel(QWidget):
    """Panel for managing configuration presets"""
    
    # Signals
    preset_loaded = Signal(dict)  # Emitted when a preset is loaded
    log_message = Signal(str)     # For logging messages
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = ConfigManager()
        self.setup_ui()
        self.setup_connections()
        self.refresh_preset_list()
    
    def setup_ui(self):
        """Initialize UI components"""
        self.layout = QVBoxLayout(self)
        
        # Add label
        self.label = QLabel("Configuration Presets")
        self.layout.addWidget(self.label)
        
        # Add preset selector combo box
        self.preset_selector = QComboBox()
        self.preset_selector.setMinimumWidth(200)
        self.preset_selector.addItem("Select a preset...")
        
        # Add buttons in a horizontal layout
        self.button_layout = QHBoxLayout()
        self.load_button = QPushButton("Load")
        self.save_button = QPushButton("Save As...")
        self.delete_button = QPushButton("Delete")
        
        # Add buttons to layout
        self.button_layout.addWidget(self.preset_selector)
        self.button_layout.addWidget(self.load_button)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.delete_button)
        
        # Add button layout to main layout
        self.layout.addLayout(self.button_layout)
    
    def setup_connections(self):
        """Connect signals to slots"""
        self.load_button.clicked.connect(self.load_selected_preset)
        self.save_button.clicked.connect(self.save_current_as_preset)
        self.delete_button.clicked.connect(self.delete_selected_preset)
    
    def refresh_preset_list(self):
        """Refresh the list of available presets"""
        # Save currently selected item
        current_selection = self.preset_selector.currentText()
        
        # Clear and repopulate
        self.preset_selector.clear()
        self.preset_selector.addItem("Select a preset...")
        
        presets = self.config_manager.get_available_presets()
        for preset in presets:
            self.preset_selector.addItem(preset)
        
        # Restore selection if possible
        index = self.preset_selector.findText(current_selection)
        if index > 0:  # > 0 because index 0 is "Select a preset..."
            self.preset_selector.setCurrentIndex(index)
    
    def load_selected_preset(self):
        """Load the selected preset"""
        current_selection = self.preset_selector.currentText()
        if current_selection == "Select a preset...":
            QMessageBox.warning(self, "Warning", "Please select a preset to load.")
            return
        
        try:
            config = self.config_manager.load_preset(current_selection)
            self.preset_loaded.emit(config)
            self.log_message.emit(f"Preset '{current_selection}' loaded successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load preset: {str(e)}")
    
    def save_current_as_preset(self):
        """Save current configuration as a new preset"""
        # This will be connected to the project panel to get current config
        # For now, we'll just show a dialog to get a name
        preset_name, ok = QInputDialog.getText(
            self, "Save Preset", "Enter a name for the preset:"
        )
        
        if ok and preset_name:
            # We'll emit a signal to request the current config
            # This will be handled by the main window
            self.log_message.emit(f"Saving preset as '{preset_name}'...")
            return preset_name
        
        return None
    
    def delete_selected_preset(self):
        """Delete the selected preset"""
        current_selection = self.preset_selector.currentText()
        if current_selection == "Select a preset...":
            QMessageBox.warning(self, "Warning", "Please select a preset to delete.")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion", 
            f"Are you sure you want to delete the preset '{current_selection}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.config_manager.delete_preset(current_selection):
                self.log_message.emit(f"Preset '{current_selection}' deleted successfully.")
                self.refresh_preset_list()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete preset.")
    
    def save_config_as_preset(self, config):
        """Save the provided config as a preset
        
        Args:
            config: Dictionary containing configuration values
        """
        preset_name = self.save_current_as_preset()
        if preset_name:
            try:
                self.config_manager.save_preset(config, preset_name)
                self.log_message.emit(f"Preset '{preset_name}' saved successfully.")
                self.refresh_preset_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save preset: {str(e)}")
