import sys

dark_theme = {
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
}

light_theme = {
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

from pathlib import Path

def findStylesQSS():
    script_dir = Path(__file__).resolve().parent  # Get the directory of the current script
    styles_path = script_dir / "style.qss"

    if styles_path.exists():
        print(f"Found: {styles_path}")
    else:
        print("File not found!")
        
    return styles_path



"""Take an input theme and a QSS file as a string, return the formatted QSS file to be used as a theme.
"""
def create_stylesheet(theme: dict) -> str:

    stylesheet = open(findStylesQSS(), "r").read()
    for key, value in theme.items():
        stylesheet = stylesheet.replace(f"{{{key}}}", value)

    return stylesheet


if __name__ == "__main__":
    x = create_stylesheet(dark_theme)
    print(x)