import pytest
from unittest.mock import Mock, MagicMock
from PySide6.QtWidgets import QApplication, QWidget
import sys

from core.base_tab import BaseTab, TabSignals


class MockTab(BaseTab):
    """Mock implementation of BaseTab for testing"""

    def setup_ui(self):
        self.layout = Mock()

    def setup_connections(self):
        self._connected = True

    def get_configuration(self):
        return {"test": "value"}

    def load_configuration(self, config):
        self._loaded_config = config

    def validate(self):
        return True

    def reset(self):
        self._reset_called = True


class TestBaseTab:
    """Test suite for BaseTab abstract class"""

    @pytest.fixture
    def app(self):
        """Create QApplication instance for Qt tests"""
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        yield app
        app.quit()

    @pytest.fixture
    def mock_tab(self, app):
        """Create a MockTab instance"""
        return MockTab()

    def test_tab_initialization(self, mock_tab):
        """Test that tab initializes correctly"""
        assert mock_tab is not None
        assert isinstance(mock_tab, BaseTab)
        assert isinstance(mock_tab, QWidget)
        assert hasattr(mock_tab, "_signals")
        assert isinstance(mock_tab._signals, TabSignals)

    def test_signals_exist(self, mock_tab):
        """Test that signals are properly exposed"""
        assert hasattr(mock_tab, "config_changed")
        assert hasattr(mock_tab, "validation_changed")
        assert callable(mock_tab.config_changed.connect)
        assert callable(mock_tab.validation_changed.connect)

    def test_is_valid_property(self, mock_tab):
        """Test that is_valid property works"""
        assert hasattr(mock_tab, "is_valid")
        assert hasattr(mock_tab, "_is_valid")
        assert isinstance(mock_tab.is_valid, bool)

    def test_emit_validation_changed(self, mock_tab):
        """Test that validation changed signal emits correctly"""
        mock_slot = Mock()
        mock_tab.validation_changed.connect(mock_slot)

        mock_tab._emit_validation_changed(True)
        assert mock_tab._is_valid is True
        mock_slot.assert_called_once_with(True)

        mock_tab._emit_validation_changed(False)
        assert mock_tab._is_valid is False
        assert mock_slot.call_count == 2
        mock_slot.assert_called_with(False)

    def test_emit_validation_changed_no_duplicate(self, mock_tab):
        """Test that validation changed signal doesn't emit for same state"""
        mock_slot = Mock()
        mock_tab.validation_changed.connect(mock_slot)

        mock_tab._emit_validation_changed(True)
        mock_tab._emit_validation_changed(True)  # Same state, no emit

        mock_slot.assert_called_once_with(True)

    def test_emit_config_changed(self, mock_tab):
        """Test that config changed signal emits correctly"""
        mock_slot = Mock()
        mock_tab.config_changed.connect(mock_slot)

        mock_tab._emit_config_changed({"test": "value"})

        assert mock_tab._config == {"test": "value"}
        mock_slot.assert_called_once_with({"test": "value"})

    def test_emit_config_changed_gets_current(self, mock_tab):
        """Test that config changed signal gets current config if not provided"""
        mock_slot = Mock()
        mock_tab.config_changed.connect(mock_slot)

        mock_tab._emit_config_changed()

        assert mock_tab._config == {"test": "value"}
        mock_slot.assert_called_once_with({"test": "value"})

    def test_get_current_config(self, mock_tab):
        """Test that get_current_config returns a copy of config"""
        mock_tab._emit_config_changed({"test": "value", "other": "data"})

        config1 = mock_tab.get_current_config()
        config2 = mock_tab.get_current_config()

        assert config1 == {"test": "value", "other": "data"}
        assert config1 is not config2
        config1["test"] = "modified"
        assert config2["test"] == "value"

    def test_get_current_config_empty(self, mock_tab):
        """Test that get_current_config returns empty dict if no config"""
        assert mock_tab.get_current_config() == {}


class TestTabSignals:
    """Test suite for TabSignals class"""

    @pytest.fixture
    def app(self):
        """Create QApplication instance for Qt tests"""
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        yield app
        app.quit()

    @pytest.fixture
    def signals(self, app):
        """Create TabSignals instance"""
        return TabSignals()

    def test_signals_initialization(self, signals):
        """Test that signals initialize correctly"""
        assert hasattr(signals, "config_changed")
        assert hasattr(signals, "validation_changed")

    def test_config_changed_signal(self, signals):
        """Test that config_changed signal works"""
        mock_slot = Mock()
        signals.config_changed.connect(mock_slot)

        signals.config_changed.emit({"test": "value"})
        mock_slot.assert_called_once_with({"test": "value"})

    def test_validation_changed_signal(self, signals):
        """Test that validation_changed signal works"""
        mock_slot = Mock()
        signals.validation_changed.connect(mock_slot)

        signals.validation_changed.emit(True)
        mock_slot.assert_called_once_with(True)
