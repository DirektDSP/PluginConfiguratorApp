"""Success dialog shown after a project is generated successfully."""

from __future__ import annotations

import platform
import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

from PySide6.QtCore import Qt, QTimer, QUrl, Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# Emoji frames for the celebration animation
_CELEBRATION_FRAMES = ["🎉", "🎊", "✨", "🌟", "⭐", "✨", "🎊", "🎉"]

# IDE definitions: (display_name, executable, args_before_path)
_IDE_DEFINITIONS: list[tuple[str, str, list[str]]] = [
    ("VSCode", "code", ["."]),
    ("CLion", "clion", ["."]),
    ("Xcode", "xcode-select", []),  # macOS only - we handle separately
]


def _detect_ides(project_path: str) -> list[tuple[str, Callable[..., None]]]:
    """Return a list of (label, open_callable) for IDEs available on this machine.

    Args:
        project_path: Absolute path to the generated project directory.

    Returns:
        List of (display_label, callable) tuples where calling the callable
        opens the project in the corresponding IDE.
    """
    available: list[tuple[str, Callable[..., None]]] = []
    current_os = platform.system()

    # VSCode
    if shutil.which("code"):
        def _open_vscode(path: str = project_path) -> None:
            subprocess.Popen(["code", path])

        available.append(("VSCode", _open_vscode))

    # CLion
    if shutil.which("clion"):
        def _open_clion(path: str = project_path) -> None:
            subprocess.Popen(["clion", path])

        available.append(("CLion", _open_clion))

    # Xcode (macOS only)
    if current_os == "Darwin" and shutil.which("xcodebuild"):
        def _open_xcode(path: str = project_path) -> None:
            # Look for an .xcodeproj or .xcworkspace in the project directory
            p = Path(path)
            for pattern in ("*.xcworkspace", "*.xcodeproj"):
                matches = list(p.glob(pattern))
                if matches:
                    subprocess.Popen(["open", str(matches[0])])
                    return
            # Fall back to opening the folder
            subprocess.Popen(["open", path])

        available.append(("Xcode", _open_xcode))

    return available


def _open_in_file_manager(path: str) -> None:
    """Open *path* in the native file manager, cross-platform."""
    current_os = platform.system()
    if current_os == "Darwin":
        subprocess.Popen(["open", path])
    elif current_os == "Windows":
        subprocess.Popen(["explorer", path])
    elif shutil.which("xdg-open"):
        # Linux / other POSIX - try xdg-open, fall back to QDesktopServices
        subprocess.Popen(["xdg-open", path])
    else:
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))


def _file_manager_label() -> str:
    """Return the platform-appropriate label for the file manager action."""
    current_os = platform.system()
    if current_os == "Darwin":
        return "Open in Finder"
    if current_os == "Windows":
        return "Open in Explorer"
    return "Open in Files"


class SuccessDialog(QDialog):
    """Dialog displayed after a project is generated successfully.

    Features:
    - Animated celebration header
    - Project name and output location display
    - "Open in IDE" buttons for each detected IDE (VSCode, Xcode, CLion)
    - Platform-aware "Open in Finder/Explorer/Files" button
    - "Close" button
    - Green-accented styling for the success state
    """

    def __init__(
        self,
        project_name: str,
        output_directory: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._project_name = project_name
        self._output_directory = output_directory
        self._animation_index = 0

        self.setWindowTitle("Project Generated Successfully")
        self.setMinimumWidth(480)
        self.setMinimumHeight(280)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self._setup_ui()
        self._start_animation()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        """Build the dialog layout."""
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 20)
        root.setSpacing(16)

        # Celebration header
        header_frame = QFrame()
        header_frame.setObjectName("successHeader")
        header_frame.setStyleSheet(
            "#successHeader {"
            "  background-color: #1e7e34;"
            "  border-radius: 8px;"
            "}"
        )
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(16, 12, 16, 12)
        header_layout.setSpacing(4)

        self._animation_label = QLabel("🎉")
        self._animation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._animation_label.setStyleSheet("font-size: 32px;")
        header_layout.addWidget(self._animation_label)

        success_text = QLabel("Project Generated Successfully!")
        success_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        success_text.setStyleSheet(
            "color: #ffffff; font-size: 16px; font-weight: bold;"
        )
        header_layout.addWidget(success_text)

        root.addWidget(header_frame)

        # Project info panel
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.StyledPanel)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(12, 10, 12, 10)
        info_layout.setSpacing(6)

        name_row = QHBoxLayout()
        name_title = QLabel("<b>Project:</b>")
        name_title.setFixedWidth(80)
        self._name_label = QLabel(self._project_name or "\u2014")
        self._name_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        name_row.addWidget(name_title)
        name_row.addWidget(self._name_label, stretch=1)
        info_layout.addLayout(name_row)

        path_row = QHBoxLayout()
        path_title = QLabel("<b>Location:</b>")
        path_title.setFixedWidth(80)
        self._path_label = QLabel(self._output_directory or "\u2014")
        self._path_label.setWordWrap(True)
        self._path_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        path_row.addWidget(path_title)
        path_row.addWidget(self._path_label, stretch=1)
        info_layout.addLayout(path_row)

        root.addWidget(info_frame)

        # Action buttons
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(8)

        # File-manager button (always shown)
        fm_btn = QPushButton(f"\U0001f4c1  {_file_manager_label()}")
        fm_btn.setMinimumHeight(36)
        fm_btn.setToolTip(f"Open the project folder:\n{self._output_directory}")
        fm_btn.clicked.connect(self._on_open_in_file_manager)
        actions_layout.addWidget(fm_btn)

        # IDE buttons (only for detected IDEs)
        self._ide_actions = _detect_ides(self._output_directory)
        if self._ide_actions:
            ide_row = QHBoxLayout()
            ide_row.setSpacing(8)
            for ide_label, ide_fn in self._ide_actions:
                btn = self._make_ide_button(ide_label, ide_fn)
                ide_row.addWidget(btn)
            actions_layout.addLayout(ide_row)

        root.addLayout(actions_layout)

        # Dialog close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.accept)
        root.addWidget(button_box)

    @staticmethod
    def _make_ide_button(label: str, callback: Callable[..., None]) -> QPushButton:
        """Return a styled IDE button that calls *callback* when clicked."""
        icon_map = {"VSCode": "\U0001f4bb", "Xcode": "\U0001f528", "CLion": "\U0001f6e0"}
        icon = icon_map.get(label, "\U0001f5a5")
        btn = QPushButton(f"{icon}  Open in {label}")
        btn.setMinimumHeight(36)
        btn.setToolTip(f"Open the project in {label}")
        btn.clicked.connect(callback)
        return btn

    # ------------------------------------------------------------------
    # Animation
    # ------------------------------------------------------------------

    def _start_animation(self) -> None:
        """Start the celebration emoji cycling animation."""
        self._timer = QTimer(self)
        self._timer.setInterval(400)
        self._timer.timeout.connect(self._advance_frame)
        self._timer.start()

    @Slot()
    def _advance_frame(self) -> None:
        """Advance to the next animation frame."""
        self._animation_index = (self._animation_index + 1) % len(_CELEBRATION_FRAMES)
        self._animation_label.setText(_CELEBRATION_FRAMES[self._animation_index])

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    @Slot()
    def _on_open_in_file_manager(self) -> None:
        """Open the project directory in the native file manager."""
        if self._output_directory:
            _open_in_file_manager(self._output_directory)

    def closeEvent(self, event) -> None:
        """Stop the animation timer before closing."""
        self._timer.stop()
        super().closeEvent(event)

