#!/usr/bin/env python3
import sys
import os
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QDir

from ui.main_window import MainWindow
from resources.themes.theme_manager import ThemeManager

def setup_environment():
    """Configure the application environment and paths"""
    # Determine the application's base directory
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        app_dir = Path(sys.executable).parent
    else:
        # Running from source
        app_dir = Path(__file__).parent.parent
    
    # Set up resource paths
    os.environ["APP_DIR"] = str(app_dir)
    os.environ["TEMPLATES_DIR"] = str(app_dir / "templates")
    os.environ["RESOURCES_DIR"] = str(app_dir / "src" / "resources")
    
    # Ensure directories exist
    templates_dir = Path(os.environ["TEMPLATES_DIR"])
    if not templates_dir.exists():
        templates_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created templates directory: {templates_dir}")
    
    # Create preset directory if it doesn't exist
    preset_dir = Path.home() / ".plugin_configurator" / "presets"
    if not preset_dir.exists():
        preset_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created preset directory: {preset_dir}")

def main():
    """Main application entry point"""
    # Set up environment variables and paths
    setup_environment()
    
    # Create the application
    app = QApplication(sys.argv)
    app.setApplicationName("Plugin Configurator")
    app.setOrganizationName("DirektDSP")
    
    # Set up theme and styling
    theme_manager = ThemeManager()
    app.setStyleSheet(theme_manager.get_stylesheet("dark"))
    
    # Create and show the main window
    window = MainWindow(theme_manager)
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
