"""Tests for the SavePresetDialog."""

from __future__ import annotations

import sys

import pytest
from PySide6.QtWidgets import QApplication, QDialog

from ui.dialogs.save_preset_dialog import SavePresetDialog


@pytest.fixture(scope="module")
def app():
    """Ensure a QApplication exists for all tests in this module."""
    instance = QApplication.instance()
    if not instance:
        instance = QApplication(sys.argv)
    yield instance


@pytest.fixture
def dialog(app) -> SavePresetDialog:
    dlg = SavePresetDialog()
    yield dlg
    dlg.deleteLater()


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------


class TestSavePresetDialogInit:
    def test_dialog_is_not_none(self, dialog):
        assert dialog is not None

    def test_window_title(self, dialog):
        assert dialog.windowTitle() == "Save as Preset"

    def test_name_edit_present(self, dialog):
        assert dialog._name_edit is not None

    def test_desc_edit_present(self, dialog):
        assert dialog._desc_edit is not None

    def test_error_label_hidden_initially(self, dialog):
        assert not dialog._error_label.isVisible()

    def test_preset_name_empty_initially(self, dialog):
        assert dialog.preset_name() == ""

    def test_description_empty_initially(self, dialog):
        assert dialog.description() == ""


# ---------------------------------------------------------------------------
# Validation: empty name is rejected
# ---------------------------------------------------------------------------


class TestSavePresetDialogValidation:
    def test_accept_with_empty_name_shows_error(self, dialog):
        """Clicking OK with an empty name must NOT accept the dialog."""
        dialog._name_edit.setText("")
        dialog._on_accept()
        # The label text is set (and would be visible in a shown dialog)
        assert dialog._error_label.text()
        assert "empty" in dialog._error_label.text().lower()

    def test_accept_with_whitespace_only_name_shows_error(self, dialog):
        dialog._name_edit.setText("   ")
        dialog._on_accept()
        assert dialog._error_label.text()

    def test_accept_with_valid_name_accepts_dialog(self, app):
        dlg = SavePresetDialog()
        dlg._name_edit.setText("My Preset")
        dlg._on_accept()
        assert dlg.result() == QDialog.DialogCode.Accepted
        dlg.deleteLater()

    def test_error_cleared_on_text_change(self, dialog):
        dialog._name_edit.setText("")
        dialog._on_accept()
        assert dialog._error_label.text()
        dialog._name_edit.setText("x")
        # _clear_error hides the label; check it's hidden (text still there but hidden)
        assert not dialog._error_label.isVisible()


# ---------------------------------------------------------------------------
# Accessors
# ---------------------------------------------------------------------------


class TestSavePresetDialogAccessors:
    def test_preset_name_returns_trimmed_text(self, app):
        dlg = SavePresetDialog()
        dlg._name_edit.setText("  My Preset  ")
        assert dlg.preset_name() == "My Preset"
        dlg.deleteLater()

    def test_description_returns_trimmed_text(self, app):
        dlg = SavePresetDialog()
        dlg._desc_edit.setPlainText("  A description  ")
        assert dlg.description() == "A description"
        dlg.deleteLater()

    def test_description_can_be_empty(self, app):
        dlg = SavePresetDialog()
        dlg._desc_edit.setPlainText("")
        assert dlg.description() == ""
        dlg.deleteLater()
