"""Validation status footer component for configuration tabs."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy


class ValidationFooter(QFrame):
    """A compact footer widget that shows a tab's validation status.

    Displays whether the tab is ready (all required fields filled) or has
    errors (required fields remaining).  When errors are present the label
    is clickable and emits ``fix_requested`` so the tab can scroll to the
    first invalid field.

    Signals:
        fix_requested: Emitted when the user clicks the footer in error state.
    """

    fix_requested = Signal()

    # Stylesheet tokens - kept as class constants so they are easy to theme.
    _READY_STYLE = (
        "background-color: #1e4620;"
        "border: 1px solid #2e7d32;"
        "border-radius: 4px;"
        "padding: 4px 8px;"
    )
    _ERROR_STYLE = (
        "background-color: #4a1942;"
        "border: 1px solid #7b1fa2;"
        "border-radius: 4px;"
        "padding: 4px 8px;"
    )
    _READY_ICON = "✓"
    _ERROR_ICON = "✗"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_ready: bool = False
        self._setup_ui()
        self.set_ready()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_ready(self):
        """Switch the footer to the 'Ready' (valid) state."""
        self._is_ready = True
        self.setStyleSheet(self._READY_STYLE)
        self._icon_label.setText(self._READY_ICON)
        self._icon_label.setStyleSheet("color: #66bb6a; font-weight: bold;")
        self._status_label.setText("Ready")
        self._status_label.setStyleSheet("color: #66bb6a;")
        self._fix_button.setVisible(False)
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def set_errors(self, remaining: int):
        """Switch the footer to the 'Errors' state.

        Args:
            remaining: Number of required fields that are still incomplete.
        """
        self._is_ready = False
        self.setStyleSheet(self._ERROR_STYLE)
        self._icon_label.setText(self._ERROR_ICON)
        self._icon_label.setStyleSheet("color: #ce93d8; font-weight: bold;")
        noun = "field" if remaining == 1 else "fields"
        self._status_label.setText(f"{remaining} required {noun} remaining")
        self._status_label.setStyleSheet("color: #ce93d8;")
        self._fix_button.setVisible(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    @property
    def is_ready(self) -> bool:
        """True when the footer is in the 'Ready' state."""
        return self._is_ready

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        self._icon_label = QLabel()
        self._icon_label.setFixedWidth(16)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._status_label = QLabel()
        self._status_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self._fix_button = QPushButton("Click to fix issues")
        self._fix_button.setFlat(True)
        self._fix_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._fix_button.setStyleSheet(
            "color: #ce93d8; text-decoration: underline; border: none; background: transparent;"
        )
        self._fix_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._fix_button.clicked.connect(self.fix_requested)
        self._fix_button.setVisible(False)

        layout.addWidget(self._icon_label)
        layout.addWidget(self._status_label)
        layout.addWidget(self._fix_button)

    def mousePressEvent(self, event):
        """Emit fix_requested when the footer is clicked in error state."""
        if not self._is_ready and event.button() == Qt.MouseButton.LeftButton:
            self.fix_requested.emit()
        super().mousePressEvent(event)
