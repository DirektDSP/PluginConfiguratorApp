"""Tests for the SuccessDialog."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QApplication

from ui.dialogs.success_dialog import (
    _CELEBRATION_FRAMES,
    SuccessDialog,
    _detect_ides,
    _file_manager_label,
    _open_in_file_manager,
)


@pytest.fixture(scope="module")
def app():
    """Single QApplication for the module."""
    instance = QApplication.instance()
    if not instance:
        instance = QApplication(sys.argv)
    yield instance


@pytest.fixture
def dialog(app):
    """Fresh SuccessDialog for each test."""
    dlg = SuccessDialog("MyPlugin", "/tmp/output")
    dlg._timer.stop()  # don't let the timer fire during tests
    yield dlg
    dlg.deleteLater()


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------


class TestSuccessDialogInit:
    def test_dialog_is_not_none(self, dialog):
        assert dialog is not None

    def test_dialog_is_instance_of_success_dialog(self, dialog):
        assert isinstance(dialog, SuccessDialog)

    def test_window_title(self, dialog):
        assert "Successfully" in dialog.windowTitle()

    def test_project_name_stored(self, dialog):
        assert dialog._project_name == "MyPlugin"

    def test_output_directory_stored(self, dialog):
        assert dialog._output_directory == "/tmp/output"

    def test_animation_index_starts_at_zero(self, dialog):
        assert dialog._animation_index == 0

    def test_animation_label_exists(self, dialog):
        assert dialog._animation_label is not None

    def test_animation_label_initial_frame(self, dialog):
        assert dialog._animation_label.text() == _CELEBRATION_FRAMES[0]

    def test_name_label_shows_project_name(self, dialog):
        assert dialog._name_label.text() == "MyPlugin"

    def test_path_label_shows_output_directory(self, dialog):
        assert dialog._path_label.text() == "/tmp/output"

    def test_minimum_width(self, dialog):
        assert dialog.minimumWidth() >= 480

    def test_minimum_height(self, dialog):
        assert dialog.minimumHeight() >= 280


# ---------------------------------------------------------------------------
# Empty / edge-case inputs
# ---------------------------------------------------------------------------


class TestSuccessDialogEdgeCases:
    def test_empty_project_name_shows_em_dash(self, app):
        dlg = SuccessDialog("", "/tmp/out")
        dlg._timer.stop()
        assert dlg._name_label.text() == "\u2014"
        dlg.deleteLater()

    def test_empty_output_directory_shows_em_dash(self, app):
        dlg = SuccessDialog("MyPlugin", "")
        dlg._timer.stop()
        assert dlg._path_label.text() == "\u2014"
        dlg.deleteLater()

    def test_none_parent_accepted(self, app):
        dlg = SuccessDialog("P", "/p", parent=None)
        dlg._timer.stop()
        assert dlg is not None
        dlg.deleteLater()


# ---------------------------------------------------------------------------
# Animation
# ---------------------------------------------------------------------------


class TestSuccessDialogAnimation:
    def test_advance_frame_cycles(self, dialog):
        dialog._animation_index = 0
        dialog._advance_frame()
        assert dialog._animation_index == 1
        assert dialog._animation_label.text() == _CELEBRATION_FRAMES[1]

    def test_advance_frame_wraps_around(self, dialog):
        dialog._animation_index = len(_CELEBRATION_FRAMES) - 1
        dialog._advance_frame()
        assert dialog._animation_index == 0
        assert dialog._animation_label.text() == _CELEBRATION_FRAMES[0]

    def test_all_frames_are_strings(self):
        for frame in _CELEBRATION_FRAMES:
            assert isinstance(frame, str)
            assert len(frame) > 0

    def test_timer_is_created(self, dialog):
        assert dialog._timer is not None

    def test_timer_interval(self, dialog):
        assert dialog._timer.interval() == 400

    def test_close_event_stops_timer(self, app):
        dlg = SuccessDialog("P", "/p")
        assert dlg._timer.isActive()
        dlg.close()
        assert not dlg._timer.isActive()
        dlg.deleteLater()


# ---------------------------------------------------------------------------
# IDE detection helpers
# ---------------------------------------------------------------------------


class TestDetectIdes:
    def test_returns_list(self):
        result = _detect_ides("/tmp")
        assert isinstance(result, list)

    def test_no_ides_when_none_available(self):
        with patch("shutil.which", return_value=None):
            result = _detect_ides("/tmp")
        assert result == []

    def test_vscode_detected_when_code_on_path(self):
        def fake_which(name):
            return "/usr/bin/code" if name == "code" else None

        with patch("shutil.which", side_effect=fake_which):
            result = _detect_ides("/tmp")

        labels = [label for label, _ in result]
        assert "VSCode" in labels

    def test_clion_detected_when_clion_on_path(self):
        def fake_which(name):
            return "/usr/local/bin/clion" if name == "clion" else None

        with patch("shutil.which", side_effect=fake_which):
            result = _detect_ides("/tmp")

        labels = [label for label, _ in result]
        assert "CLion" in labels

    def test_xcode_detected_only_on_macos(self):
        def fake_which(name):
            return "/usr/bin/xcodebuild" if name == "xcodebuild" else None

        with (
            patch("shutil.which", side_effect=fake_which),
            patch("platform.system", return_value="Darwin"),
        ):
            result = _detect_ides("/tmp")

        labels = [label for label, _ in result]
        assert "Xcode" in labels

    def test_xcode_not_detected_on_linux(self):
        def fake_which(name):
            return "/usr/bin/xcodebuild" if name == "xcodebuild" else None

        with (
            patch("shutil.which", side_effect=fake_which),
            patch("platform.system", return_value="Linux"),
        ):
            result = _detect_ides("/tmp")

        labels = [label for label, _ in result]
        assert "Xcode" not in labels

    def test_ide_entry_is_callable(self):
        def fake_which(name):
            return "/usr/bin/code" if name == "code" else None

        with patch("shutil.which", side_effect=fake_which):
            result = _detect_ides("/tmp")

        for _label, fn in result:
            assert callable(fn)


# ---------------------------------------------------------------------------
# File manager helpers
# ---------------------------------------------------------------------------


class TestFileManagerLabel:
    def test_macos_label(self):
        with patch("platform.system", return_value="Darwin"):
            assert _file_manager_label() == "Open in Finder"

    def test_windows_label(self):
        with patch("platform.system", return_value="Windows"):
            assert _file_manager_label() == "Open in Explorer"

    def test_linux_label(self):
        with patch("platform.system", return_value="Linux"):
            assert _file_manager_label() == "Open in Files"

    def test_unknown_os_label(self):
        with patch("platform.system", return_value="FreeBSD"):
            assert _file_manager_label() == "Open in Files"


class TestOpenInFileManager:
    def test_macos_calls_open(self):
        with (
            patch("platform.system", return_value="Darwin"),
            patch("subprocess.Popen") as mock_popen,
        ):
            _open_in_file_manager("/tmp/project")
            mock_popen.assert_called_once_with(["open", "/tmp/project"])

    def test_windows_calls_explorer(self):
        with (
            patch("platform.system", return_value="Windows"),
            patch("subprocess.Popen") as mock_popen,
        ):
            _open_in_file_manager("/tmp/project")
            mock_popen.assert_called_once_with(["explorer", "/tmp/project"])

    def test_linux_with_xdg_open(self):
        with (
            patch("platform.system", return_value="Linux"),
            patch("shutil.which", return_value="/usr/bin/xdg-open"),
            patch("subprocess.Popen") as mock_popen,
        ):
            _open_in_file_manager("/tmp/project")
            mock_popen.assert_called_once_with(["xdg-open", "/tmp/project"])

    def test_linux_fallback_to_desktop_services(self, app):
        with (
            patch("platform.system", return_value="Linux"),
            patch("shutil.which", return_value=None),
            patch("ui.dialogs.success_dialog.QDesktopServices.openUrl") as mock_open,
        ):
            _open_in_file_manager("/tmp/project")
            assert mock_open.called


# ---------------------------------------------------------------------------
# Dialog action buttons
# ---------------------------------------------------------------------------


class TestSuccessDialogActions:
    def test_open_in_file_manager_slot_calls_helper(self, dialog, monkeypatch):
        called_with = []
        monkeypatch.setattr(
            "ui.dialogs.success_dialog._open_in_file_manager",
            called_with.append,
        )
        dialog._output_directory = "/tmp/output"
        dialog._on_open_in_file_manager()
        assert called_with == ["/tmp/output"]

    def test_open_in_file_manager_noop_when_empty_dir(self, dialog, monkeypatch):
        called = []
        monkeypatch.setattr(
            "ui.dialogs.success_dialog._open_in_file_manager",
            called.append,
        )
        dialog._output_directory = ""
        dialog._on_open_in_file_manager()
        assert called == []

    def test_ide_buttons_created_for_detected_ides(self, app):
        mock_fn = MagicMock()
        with patch(
            "ui.dialogs.success_dialog._detect_ides",
            return_value=[("VSCode", mock_fn)],
        ):
            dlg = SuccessDialog("P", "/p")
            dlg._timer.stop()

        labels = [label for label, _ in dlg._ide_actions]
        assert "VSCode" in labels
        dlg.deleteLater()

    def test_no_ide_buttons_when_none_detected(self, app):
        with patch("ui.dialogs.success_dialog._detect_ides", return_value=[]):
            dlg = SuccessDialog("P", "/p")
            dlg._timer.stop()

        assert dlg._ide_actions == []
        dlg.deleteLater()
