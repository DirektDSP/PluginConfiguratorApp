from abc import ABC, abstractmethod
from abc import ABCMeta as ABCTestMeta
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal, QObject, SignalInstance


class TabSignals(QObject):
    """Signals common to all tabs"""

    config_changed = Signal(dict)
    validation_changed = Signal(bool)


class BaseTabMeta(type(QWidget), ABCTestMeta):
    """Metaclass that combines QWidget and ABC metaclasses"""

    pass


class BaseTab(QWidget, ABC, metaclass=BaseTabMeta):
    """Base class for all configuration tabs

    Provides common functionality and structure for all tabs in the application.
    All tabs should inherit from this class and implement the abstract methods.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._signals = TabSignals(self)
        self._is_valid = False
        self._config = {}

    @property
    def config_changed(self):
        """Signal emitted when configuration changes"""
        return self._signals.config_changed

    @property
    def validation_changed(self):
        """Signal emitted when validation state changes"""
        return self._signals.validation_changed

    @property
    def is_valid(self):
        """Current validation state of the tab"""
        return self._is_valid

    @abstractmethod
    def setup_ui(self):
        """Initialize UI components. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def setup_connections(self):
        """Connect signals to slots. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def get_configuration(self):
        """Get current configuration from the tab

        Returns:
            dict: Dictionary containing the current configuration
        """
        pass

    @abstractmethod
    def load_configuration(self, config):
        """Load configuration into the tab

        Args:
            config (dict): Configuration dictionary to load
        """
        pass

    @abstractmethod
    def validate(self):
        """Validate the tab's current state

        Returns:
            bool: True if valid, False otherwise
        """
        pass

    @abstractmethod
    def reset(self):
        """Reset the tab to its default state"""
        pass

    def _emit_validation_changed(self, is_valid):
        """Emit validation changed signal if state changed

        Args:
            is_valid (bool): New validation state
        """
        if is_valid != self._is_valid:
            self._is_valid = is_valid
            self.validation_changed.emit(is_valid)

    def _emit_config_changed(self, config=None):
        """Emit config changed signal

        Args:
            config (dict, optional): Configuration to emit. If None, gets current config.
        """
        if config is None:
            config = self.get_configuration()
        self._config = config
        self.config_changed.emit(config)

    def get_current_config(self):
        """Get the last emitted configuration

        Returns:
            dict: The last configuration that was emitted via config_changed
        """
        return self._config.copy() if self._config else {}
