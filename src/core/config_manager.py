import xml.etree.ElementTree as ET
from pathlib import Path

class ConfigManager:
    """Manages loading and saving of XML configuration files"""
    
    def load_config(self, file_path):
        """Load configuration from an XML file
        
        Args:
            file_path: Path to the XML configuration file
            
        Returns:
            dict: Dictionary containing configuration values
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Create a dictionary from the XML elements
            config = {}
            for child in root:
                # Handle boolean values (stored as text "True"/"False")
                if child.text.lower() in ['true', 'false']:
                    config[child.tag] = child.text.lower() == 'true'
                else:
                    config[child.tag] = child.text
                    
            return config
            
        except Exception as e:
            raise ValueError(f"Failed to load configuration: {str(e)}")
    
    def save_config(self, config, file_path):
        """Save configuration to an XML file
        
        Args:
            config: Dictionary containing configuration values
            file_path: Path where to save the XML file
        """
        try:
            root = ET.Element("config")
            
            # Create XML elements from the dictionary
            for key, value in config.items():
                # Convert value to string
                if isinstance(value, bool):
                    value = str(value)
                elif value is None:
                    value = ""
                
                element = ET.SubElement(root, key)
                element.text = value
            
            # Create a pretty XML file
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ")
            
            tree.write(file_path, encoding="utf-8", xml_declaration=True)
            
        except Exception as e:
            raise ValueError(f"Failed to save configuration: {str(e)}")
    
    def get_default_config(self):
        """Get a dictionary with default configuration values"""
        return {
            "project_name": "",
            "fork_url": "https://github.com/SeamusMullan/PluginTemplate.git",
            "product_name": "",
            "company_name": "DirektDSP",
            "bundle_id": "",
            "manufacturer_code": "Ddsp",
            "output_directory": "",
            "standalone": False,
            "vst3": True,
            "au": True,
            "auv3": False,
            "clap": True,
            "create_git_repo": True,
            "melatonin": True,
            "moonbase": False,
            "clap_export": True,
            "juce_develop": True,
            "xcode_prettify": True,
            "juce_curl": False,
            "juce_web_browser": False,
            "juce_vst2": False
        }
