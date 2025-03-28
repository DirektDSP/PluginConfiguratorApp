#!/usr/bin/env python3
"""
Launcher script for Plugin Configurator App
This ensures Python can find all the modules correctly
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Launch the application
from main import main

if __name__ == "__main__":
    main()
