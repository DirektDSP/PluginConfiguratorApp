from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QCheckBox, 
    QLabel, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Slot

class OptionsPanel(QWidget):
    """Panel for configuring plugin options"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize UI components"""
        self.layout = QVBoxLayout(self)
        
        # Main group box
        self.group_box = QGroupBox("Plugin Options")
        self.group_layout = QVBoxLayout()
        
        # Create a scroll area for options
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create a widget to hold all checkbox groups
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        
        # Add option groups
        self.add_formats_group()
        self.add_separator()
        self.add_features_group()
        self.add_separator()
        self.add_juce_options_group()
        
        # Add spacing at the bottom
        self.scroll_layout.addStretch()
        
        # Set the scroll widget and add to layout
        self.scroll_area.setWidget(self.scroll_widget)
        self.group_layout.addWidget(self.scroll_area)
        self.group_box.setLayout(self.group_layout)
        
        # Add group box to main layout
        self.layout.addWidget(self.group_box)
    
    def add_separator(self):
        """Add a horizontal separator line"""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.scroll_layout.addWidget(separator)
    
    def add_formats_group(self):
        """Add plugin format options"""
        # Container for format options
        formats_container = QGroupBox("Plugin Formats")
        formats_layout = QVBoxLayout()
        
        # Format options
        self.standalone_checkbox = QCheckBox("Standalone Application")
        self.vst3_checkbox = QCheckBox("VST3")
        self.au_checkbox = QCheckBox("Audio Unit (AU)")
        self.auv3_checkbox = QCheckBox("Audio Unit v3 (AUv3)")
        self.clap_checkbox = QCheckBox("CLAP")
        
        # Default selections
        self.vst3_checkbox.setChecked(True)
        self.au_checkbox.setChecked(True)
        self.clap_checkbox.setChecked(True)
        
        # Add checkboxes to layout
        formats_layout.addWidget(self.standalone_checkbox)
        formats_layout.addWidget(self.vst3_checkbox)
        formats_layout.addWidget(self.au_checkbox)
        formats_layout.addWidget(self.auv3_checkbox)
        formats_layout.addWidget(self.clap_checkbox)
        
        # Set layout for container
        formats_container.setLayout(formats_layout)
        self.scroll_layout.addWidget(formats_container)
    
    def add_features_group(self):
        """Add plugin feature options"""
        # Container for feature options
        features_container = QGroupBox("Additional Features")
        features_layout = QVBoxLayout()
        
        # Feature options
        self.create_git_repo_checkbox = QCheckBox("Initialize Git Repository")
        self.melatonin_checkbox = QCheckBox("Include Melatonin Inspector")
        self.moonbase_checkbox = QCheckBox("Moonbase Licensing")
        self.clap_export_checkbox = QCheckBox("CLAP Export Support")
        self.juce_develop_checkbox = QCheckBox("Use JUCE Develop Branch")
        self.xcode_prettify_checkbox = QCheckBox("XCode Prettify")
        
        # Default selections
        self.create_git_repo_checkbox.setChecked(True)
        self.melatonin_checkbox.setChecked(True)
        
        # Add checkboxes to layout
        features_layout.addWidget(self.create_git_repo_checkbox)
        features_layout.addWidget(self.melatonin_checkbox)
        features_layout.addWidget(self.moonbase_checkbox)
        features_layout.addWidget(self.clap_export_checkbox)
        features_layout.addWidget(self.juce_develop_checkbox)
        features_layout.addWidget(self.xcode_prettify_checkbox)
        
        # Set layout for container
        features_container.setLayout(features_layout)
        self.scroll_layout.addWidget(features_container)
    
    def add_juce_options_group(self):
        """Add JUCE-specific options"""
        # Container for JUCE options
        juce_container = QGroupBox("JUCE Options")
        juce_layout = QVBoxLayout()
        
        # JUCE options
        self.juce_curl_checkbox = QCheckBox("Enable JUCE_USE_CURL")
        self.juce_web_browser_checkbox = QCheckBox("Enable JUCE_WEB_BROWSER")
        self.juce_vst2_checkbox = QCheckBox("Enable JUCE_VST3_CAN_REPLACE_VST2")
        
        # Add checkboxes to layout
        juce_layout.addWidget(self.juce_curl_checkbox)
        juce_layout.addWidget(self.juce_web_browser_checkbox)
        juce_layout.addWidget(self.juce_vst2_checkbox)
        
        # Set layout for container
        juce_container.setLayout(juce_layout)
        self.scroll_layout.addWidget(juce_container)
    
    def get_options(self):
        """Collect all option settings"""
        return {
            # Plugin formats
            "standalone": self.standalone_checkbox.isChecked(),
            "vst3": self.vst3_checkbox.isChecked(),
            "au": self.au_checkbox.isChecked(),
            "auv3": self.auv3_checkbox.isChecked(),
            "clap": self.clap_checkbox.isChecked(),
            
            # Features
            "create_git_repo": self.create_git_repo_checkbox.isChecked(),
            "melatonin": self.melatonin_checkbox.isChecked(),
            "moonbase": self.moonbase_checkbox.isChecked(),
            "clap_export": self.clap_export_checkbox.isChecked(),
            "juce_develop": self.juce_develop_checkbox.isChecked(),
            "xcode_prettify": self.xcode_prettify_checkbox.isChecked(),
            
            # JUCE options
            "juce_curl": self.juce_curl_checkbox.isChecked(),
            "juce_web_browser": self.juce_web_browser_checkbox.isChecked(),
            "juce_vst2": self.juce_vst2_checkbox.isChecked()
        }
    
    @Slot(dict)
    def load_preset(self, config):
        """Load preset options into checkboxes
        
        Args:
            config: Dictionary containing configuration values
        """
        # Format options
        if "standalone" in config:
            self.standalone_checkbox.setChecked(config["standalone"])
        if "vst3" in config:
            self.vst3_checkbox.setChecked(config["vst3"])
        if "au" in config:
            self.au_checkbox.setChecked(config["au"])
        if "auv3" in config:
            self.auv3_checkbox.setChecked(config["auv3"])
        if "clap" in config:
            self.clap_checkbox.setChecked(config["clap"])
        
        # Feature options
        if "create_git_repo" in config:
            self.create_git_repo_checkbox.setChecked(config["create_git_repo"])
        if "melatonin" in config:
            self.melatonin_checkbox.setChecked(config["melatonin"])
        if "moonbase" in config:
            self.moonbase_checkbox.setChecked(config["moonbase"])
        if "clap_export" in config:
            self.clap_export_checkbox.setChecked(config["clap_export"])
        if "juce_develop" in config:
            self.juce_develop_checkbox.setChecked(config["juce_develop"])
        if "xcode_prettify" in config:
            self.xcode_prettify_checkbox.setChecked(config["xcode_prettify"])
        
        # JUCE options
        if "juce_curl" in config:
            self.juce_curl_checkbox.setChecked(config["juce_curl"])
        if "juce_web_browser" in config:
            self.juce_web_browser_checkbox.setChecked(config["juce_web_browser"])
        if "juce_vst2" in config:
            self.juce_vst2_checkbox.setChecked(config["juce_vst2"])
