from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from core.base_tab import BaseTab


class ImplementTab(BaseTab):
    """Tab 3: Implement - Configure development extras and dependencies

    This is the third tab in the new 4-lifecycle UI structure.
    Users configure optional development tools and libraries here.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        self._emit_config_changed()

    def setup_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)

        # Optional dependencies group
        optional_group = QGroupBox("Optional Dependencies")
        optional_layout = QVBoxLayout()

        self.create_git_repo = QCheckBox("Create Git Repository")
        self.create_git_repo.setChecked(True)
        self.create_git_repo.setToolTip("Initialize a Git repository in your project")
        optional_layout.addWidget(self.create_git_repo)

        self.melatonin = QCheckBox("Melatonin Inspector")
        self.melatonin.setChecked(True)
        self.melatonin.setToolTip("Add Melatonin JUCE inspector for debugging")
        optional_layout.addWidget(self.melatonin)

        self.moonbase = QCheckBox("Moonbase Audio Plugin Host")
        self.moonbase.setChecked(False)
        self.moonbase.setToolTip("Include Moonbase plugin testing host")
        optional_layout.addWidget(self.moonbase)

        optional_group.setLayout(optional_layout)

        # JUCE extras group
        juce_group = QGroupBox("JUCE Extras")
        juce_layout = QVBoxLayout()

        self.juce_develop = QCheckBox("JUCE Develop Mode")
        self.juce_develop.setChecked(True)
        self.juce_develop.setToolTip("Enable JUCE development mode features")
        juce_layout.addWidget(self.juce_develop)

        self.xcode_prettify = QCheckBox("Xcode Prettifier")
        self.xcode_prettify.setChecked(True)
        self.xcode_prettify.setToolTip("Enable code formatting for Xcode projects")
        juce_layout.addWidget(self.xcode_prettify)

        self.juce_curl = QCheckBox("JUCE cURL Support")
        self.juce_curl.setChecked(False)
        self.juce_curl.setToolTip("Enable cURL support for networking")
        juce_layout.addWidget(self.juce_curl)

        self.juce_web_browser = QCheckBox("JUCE Web Browser")
        self.juce_web_browser.setChecked(False)
        self.juce_web_browser.setToolTip("Enable embedded web browser component")
        juce_layout.addWidget(self.juce_web_browser)

        self.juce_vst2 = QCheckBox("JUCE VST2 Support (Legacy)")
        self.juce_vst2.setChecked(False)
        self.juce_vst2.setToolTip("Enable VST2 support (requires license)")
        juce_layout.addWidget(self.juce_vst2)

        juce_group.setLayout(juce_layout)

        # Progress indicator
        self.progress_label = QLabel("Step 3 of 4: Implement")
        self.progress_label.setStyleSheet("color: #666; font-style: italic;")

        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.back_button = QPushButton("← Back to Configure")
        self.continue_button = QPushButton("Continue to Generate →")

        nav_layout.addWidget(self.back_button)
        nav_layout.addStretch()
        nav_layout.addWidget(self.continue_button)

        # Add to main layout
        layout.addWidget(optional_group)
        layout.addWidget(juce_group)
        layout.addWidget(self.progress_label)
        layout.addStretch()
        layout.addLayout(nav_layout)

        # Connect state changes
        for checkbox in [
            self.create_git_repo,
            self.melatonin,
            self.moonbase,
            self.juce_develop,
            self.xcode_prettify,
            self.juce_curl,
            self.juce_web_browser,
            self.juce_vst2,
        ]:
            checkbox.stateChanged.connect(self._on_config_changed)

    def setup_connections(self):
        """Connect signals to slots"""
        self.back_button.clicked.connect(self._go_back_to_configure)
        self.continue_button.clicked.connect(self._continue_to_generate)

    @Slot()
    def _on_config_changed(self):
        """Handle configuration changes"""
        self._emit_config_changed()
        self._update_validation_state()

    @Slot()
    def _go_back_to_configure(self):
        """Navigate back to Configure tab"""
        self._emit_config_changed()

    @Slot()
    def _continue_to_generate(self):
        """Continue to generate tab"""
        if self.validate():
            self._emit_config_changed()
        else:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please fix validation issues before continuing.",
            )

    def _update_validation_state(self):
        """Update validation state - this tab is always valid (all optional)"""
        self._emit_validation_changed(True)

    def get_configuration(self):
        """Get current configuration from the tab"""
        return {
            "create_git_repo": self.create_git_repo.isChecked(),
            "melatonin": self.melatonin.isChecked(),
            "moonbase": self.moonbase.isChecked(),
            "juce_develop": self.juce_develop.isChecked(),
            "xcode_prettify": self.xcode_prettify.isChecked(),
            "juce_curl": self.juce_curl.isChecked(),
            "juce_web_browser": self.juce_web_browser.isChecked(),
            "juce_vst2": self.juce_vst2.isChecked(),
            "tab_complete": True,
        }

    def load_configuration(self, config):
        """Load configuration into the tab"""
        self.create_git_repo.setChecked(config.get("create_git_repo", True))
        self.melatonin.setChecked(config.get("melatonin", True))
        self.moonbase.setChecked(config.get("moonbase", False))
        self.juce_develop.setChecked(config.get("juce_develop", True))
        self.xcode_prettify.setChecked(config.get("xcode_prettify", True))
        self.juce_curl.setChecked(config.get("juce_curl", False))
        self.juce_web_browser.setChecked(config.get("juce_web_browser", False))
        self.juce_vst2.setChecked(config.get("juce_vst2", False))
        self._emit_config_changed()

    def validate(self):
        """Validate the tab's current state - always valid (all optional)"""
        return True

    def reset(self):
        """Reset the tab to its default state"""
        self.create_git_repo.setChecked(True)
        self.melatonin.setChecked(True)
        self.moonbase.setChecked(False)
        self.juce_develop.setChecked(True)
        self.xcode_prettify.setChecked(True)
        self.juce_curl.setChecked(False)
        self.juce_web_browser.setChecked(False)
        self.juce_vst2.setChecked(False)
        self._emit_config_changed()
