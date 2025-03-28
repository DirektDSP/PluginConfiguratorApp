import os
from pathlib import Path

class ThemeManager:
    """Manages application themes and stylesheets"""
    
    def __init__(self):
        self.themes = {
            "dark": {
                "background-color": "#2E3440",
                "foreground-color": "#FFFFFF",
                "primary-color": "#5E81AC",
                "secondary-color": "#3B4252",
                "highlight-color": "#81A1C1",
                "input-background-color": "#434C5E",
                "input-placeholder-color": "rgba(94, 129, 172, 0.5)",
                "border-color": "#5E81AC",
                "scrollbar-background-color": "#3B4252",
                "scrollbar-handle-color": "#5E81AC",
                "scrollbar-handle-hover-color": "#81A1C1",
                "textedit-background-color": "#434C5E",
                "progressbar-background-color": "#434C5E",
                "progressbar-chunk-color": "#5E81AC",
            },
            "light": {
                "background-color": "#ECEFF4",
                "foreground-color": "#2E3440",
                "primary-color": "#5E81AC",
                "secondary-color": "#D8DEE9",
                "highlight-color": "#81A1C1",
                "input-background-color": "#E5E9F0",
                "input-placeholder-color": "rgba(94, 129, 172, 0.5)",
                "border-color": "#5E81AC",
                "scrollbar-background-color": "#D8DEE9",
                "scrollbar-handle-color": "#5E81AC",
                "scrollbar-handle-hover-color": "#81A1C1",
                "textedit-background-color": "#E5E9F0",
                "progressbar-background-color": "#E5E9F0",
                "progressbar-chunk-color": "#5E81AC",
            }
        }
    
    def get_stylesheet(self, theme_name="dark"):
        """Get the stylesheet for the specified theme"""
        # Ensure the theme exists, default to dark if not
        if theme_name not in self.themes:
            theme_name = "dark"
            
        # Get the theme variables
        theme_vars = self.themes[theme_name]
        
        # Find the stylesheet file
        stylesheet_path = self._find_stylesheet_path()
        
        # Read the stylesheet template
        with open(stylesheet_path, 'r') as file:
            stylesheet = file.read()
            
        # Replace variables with theme values
        for key, value in theme_vars.items():
            stylesheet = stylesheet.replace(f"{{{key}}}", value)
            
        return stylesheet
    
    def _find_stylesheet_path(self):
        """Find the path to the stylesheet file"""
        # Try to use the environment variable first
        if "RESOURCES_DIR" in os.environ:
            path = Path(os.environ["RESOURCES_DIR"]) / "style.qss"
            if path.exists():
                return path
        
        # Fall back to relative path from this file
        current_dir = Path(__file__).parent.parent
        path = current_dir / "style.qss"
        
        if not path.exists():
            raise FileNotFoundError(f"Could not find stylesheet file at {path}")
            
        return path
