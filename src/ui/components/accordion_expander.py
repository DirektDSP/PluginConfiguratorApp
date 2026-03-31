from __future__ import annotations

from PySide6.QtCore import QByteArray, QEasingCurve, QPropertyAnimation, Qt, Signal, Slot
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

SUBTEXT_COLOR = "#666"
_MAXIMUM_HEIGHT_PROPERTY = QByteArray(b"maximumHeight")


class AccordionExpander(QWidget):
    """Reusable animated accordion-style expander with optional header control.

    The expander provides a clickable header with a chevron, animated
    expand/collapse of its body, and an optional trailing control widget
    (e.g. checkbox, switch) for module enablement.  Nested accordions are
    supported by simply adding another :class:`AccordionExpander` to the
    body layout.
    """

    toggled = Signal(bool)

    def __init__(
        self,
        title: str,
        subtitle: str | None = None,
        *,
        control_widget: QWidget | None = None,
        start_expanded: bool = False,
        animation_duration_ms: int = 150,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._animation_duration = animation_duration_ms

        self._toggle = QPushButton(self)
        self._toggle.setCheckable(True)
        self._toggle.setChecked(start_expanded)
        self._toggle.setFlat(True)
        self._toggle.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._toggle.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._toggle.clicked.connect(self._on_toggle_clicked)

        self._title_label = QLabel(title)
        self._title_label.setStyleSheet("font-weight: bold;")

        self._subtitle_label = QLabel(subtitle or "")
        self._subtitle_label.setStyleSheet(f"color: {SUBTEXT_COLOR};")
        self._subtitle_label.setVisible(bool(subtitle))

        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addWidget(self._title_label)
        header_layout.addWidget(self._subtitle_label)

        header = QHBoxLayout()
        header.setContentsMargins(8, 6, 8, 6)
        header.setSpacing(8)
        header.addWidget(self._toggle)
        header.addLayout(header_layout)
        header.addStretch()
        if control_widget is not None:
            control_widget.setParent(self)
            header.addWidget(control_widget)

        header_frame = QFrame()
        header_frame.setLayout(header)
        header_frame.setStyleSheet(
            "QFrame { border: 1px solid #d5d5d5; border-radius: 6px; background: #f9f9f9; }"
        )

        self._content = QWidget()
        self._content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._content.setVisible(start_expanded)

        self.body_layout = QVBoxLayout(self._content)
        self.body_layout.setContentsMargins(12, 8, 12, 8)
        self.body_layout.setSpacing(8)

        # Qt's property animation API expects property names as bytes literals.
        self._animation = QPropertyAnimation(self._content, _MAXIMUM_HEIGHT_PROPERTY, self._content)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._animation.setDuration(self._animation_duration)
        self._animation.finished.connect(self._on_animation_finished)

        self._update_toggle_label(start_expanded)
        self._content.setMaximumHeight(self._content.sizeHint().height() if start_expanded else 0)

        wrapper = QVBoxLayout(self)
        wrapper.setContentsMargins(0, 0, 0, 0)
        wrapper.addWidget(header_frame)
        wrapper.addWidget(self._content)

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #
    def set_expanded(self, expanded: bool) -> None:
        """Programmatically expand or collapse the body with animation."""
        if expanded == self.is_expanded:
            return
        self._toggle.setChecked(expanded)
        self._animate_body(expanded)

    @property
    def is_expanded(self) -> bool:
        """Return current expanded state."""
        return self._toggle.isChecked()

    @property
    def indicator_text(self) -> str:
        """Return the current chevron text."""
        return self._toggle.text()

    # ------------------------------------------------------------------ #
    # Slots                                                              #
    # ------------------------------------------------------------------ #
    @Slot(bool)
    def _on_toggle_clicked(self, checked: bool) -> None:
        self._animate_body(checked)
        self.toggled.emit(checked)

    def _animate_body(self, expand: bool) -> None:
        self._content.setVisible(True)
        start_value = self._content.maximumHeight()
        target = self._content.sizeHint().height() if expand else 0

        self._animation.stop()
        self._animation.setStartValue(start_value)
        self._animation.setEndValue(target)
        self._animation.start()

        self._update_toggle_label(expand)

    def _update_toggle_label(self, expanded: bool) -> None:
        arrow = "▼" if expanded else "▶"
        self._toggle.setText(arrow)

    def _on_animation_finished(self) -> None:
        if not self.is_expanded:
            self._content.setVisible(False)
            self._content.setMaximumHeight(0)
        else:
            # Keep the body height in sync with its contents after expand.
            self._content.setMaximumHeight(self._content.sizeHint().height())
