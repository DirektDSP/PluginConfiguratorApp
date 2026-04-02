"""Tests for the ValidationFooter component."""

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from unittest.mock import Mock

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from ui.components.validation_footer import ValidationFooter


@pytest.fixture(scope="module")
def app():
    if not QApplication.instance():
        _app = QApplication(sys.argv)
    else:
        _app = QApplication.instance()
    yield _app
    _app.quit()


@pytest.fixture
def footer(app):
    return ValidationFooter()


class TestValidationFooterInitialState:
    def test_footer_created_in_ready_state(self, footer):
        assert footer.is_ready is True

    def test_fix_button_hidden_when_ready(self, footer):
        assert footer._fix_button.isHidden() is True

    def test_status_label_shows_ready(self, footer):
        assert footer._status_label.text() == "Ready"

    def test_icon_shows_checkmark(self, footer):
        assert footer._icon_label.text() == ValidationFooter._READY_ICON


class TestValidationFooterSetErrors:
    def test_set_errors_marks_not_ready(self, footer):
        footer.set_errors(3)
        assert footer.is_ready is False

    def test_set_errors_shows_fix_button(self, footer):
        footer.set_errors(1)
        assert footer._fix_button.isHidden() is False

    def test_set_errors_singular_field(self, footer):
        footer.set_errors(1)
        assert "1 required field remaining" in footer._status_label.text()

    def test_set_errors_plural_fields(self, footer):
        footer.set_errors(4)
        assert "4 required fields remaining" in footer._status_label.text()

    def test_set_errors_shows_error_icon(self, footer):
        footer.set_errors(2)
        assert footer._icon_label.text() == ValidationFooter._ERROR_ICON


class TestValidationFooterSetReady:
    def test_set_ready_after_errors_restores_ready_state(self, footer):
        footer.set_errors(2)
        footer.set_ready()
        assert footer.is_ready is True

    def test_set_ready_hides_fix_button(self, footer):
        footer.set_errors(1)
        footer.set_ready()
        assert footer._fix_button.isHidden() is True

    def test_set_ready_shows_ready_text(self, footer):
        footer.set_errors(3)
        footer.set_ready()
        assert footer._status_label.text() == "Ready"

    def test_set_ready_restores_checkmark_icon(self, footer):
        footer.set_errors(2)
        footer.set_ready()
        assert footer._icon_label.text() == ValidationFooter._READY_ICON


class TestValidationFooterSignal:
    def test_fix_requested_emitted_on_button_click(self, footer):
        slot = Mock()
        footer.fix_requested.connect(slot)
        footer.set_errors(2)
        footer._fix_button.click()
        slot.assert_called_once()

    def test_fix_requested_not_emitted_in_ready_state(self, footer, qtbot):
        slot = Mock()
        footer.fix_requested.connect(slot)
        footer.set_ready()
        # Simulate a left-click via mousePressEvent in ready state
        qtbot.mouseClick(footer, Qt.MouseButton.LeftButton)
        slot.assert_not_called()
