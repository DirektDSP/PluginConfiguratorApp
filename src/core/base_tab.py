"""Abstract base class for all configuration tabs in the Plugin Configurator application."""

from abc import ABC, ABCMeta, abstractmethod

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QLineEdit, QScrollArea, QWidget


class TabSignals(QObject):
    """Signals common to all tabs."""

    config_changed = Signal(dict)
    validation_changed = Signal(bool)


class BaseTabMeta(type(QWidget), ABCMeta):  # type: ignore[misc]
    """Metaclass that combines QWidget and ABC metaclasses."""

    pass


class BaseTab(QWidget, ABC, metaclass=BaseTabMeta):
    """Abstract base class for all configuration tabs.

    Provides common functionality and structure for all tabs in the application.
    All tabs should inherit from this class and implement the abstract methods.

    Signals:
        config_changed: Emitted when the tab's configuration changes.
        validation_changed: Emitted when the tab's validation state changes.
    """

    def __init__(self, parent=None):
        """Initialize the base tab.

        Args:
            parent: Optional parent widget.
        """
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

    def get_required_fields(self) -> list:
        """Return a list of (widget, label) pairs for required fields.

        Subclasses should override this to describe which fields are required.
        The default implementation returns an empty list (no required fields).

        Returns:
            list[tuple[QWidget, str]]: Each tuple contains the widget and its
            human-readable label, e.g. ``(self.project_name, "Project Name")``.
        """
        return []

    def get_invalid_field_count(self) -> int:
        """Return the number of required fields that are currently incomplete.

        The base implementation counts QLineEdit widgets whose text is empty
        after stripping whitespace.  Subclasses may override this for custom
        validation logic (e.g. checkbox groups, spin-box ranges).

        Returns:
            int: Number of unfilled / invalid required fields.
        """
        count = 0
        for widget, _label in self.get_required_fields():
            if isinstance(widget, QLineEdit) and not widget.text().strip():
                count += 1
        return count

    def focus_first_invalid(self):
        """Scroll to and focus the first invalid required field.

        The base implementation iterates ``get_required_fields()`` and focuses
        the first QLineEdit that is empty.  Subclasses may override this to
        handle non-text widgets or custom scroll areas.
        """
        for widget, _label in self.get_required_fields():
            if isinstance(widget, QLineEdit) and not widget.text().strip():
                widget.setFocus()
                widget.ensurePolished()
                # Scroll into view if the field is inside a QScrollArea
                _scroll_into_view(widget)
                return

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


def _scroll_into_view(widget: QWidget) -> None:
    """Walk up the widget tree and scroll ``widget`` into view in any QScrollArea."""
    parent = widget.parent()
    while parent is not None:
        if isinstance(parent, QScrollArea):
            parent.ensureWidgetVisible(widget)
            return
        parent = parent.parent() if hasattr(parent, "parent") else None
