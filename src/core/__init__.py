"""
Core module for the Plugin Configurator application.
Contains business logic and worker classes.
"""

from .base_tab import BaseTab, TabSignals
from .preset_validator import PresetXSDValidator

__all__ = ["BaseTab", "PresetXSDValidator", "TabSignals"]
