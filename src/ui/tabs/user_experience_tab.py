from PySide6.QtWidgets import QCheckBox, QFormLayout, QGroupBox, QVBoxLayout

from core.base_tab import BaseTab


class UserExperienceTab(BaseTab):
    """Tab for configuring user experience options"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        self.group = QGroupBox("User Experience Features")
        form = QFormLayout()
        self.wizard_cb = QCheckBox("Project Creation Wizard UI")
        self.preview_cb = QCheckBox("Real-time Preview of Configuration Choices")
        self.preset_management_cb = QCheckBox("Preset Configuration Management")
        form.addRow(self.wizard_cb)
        form.addRow(self.preview_cb)
        form.addRow(self.preset_management_cb)
        self.group.setLayout(form)
        self.layout.addWidget(self.group)
        self.layout.addStretch()

    def setup_connections(self):
        """Connect signals to slots"""
        checkboxes = [
            self.wizard_cb, self.preview_cb,
            self.preset_management_cb,
        ]
        for cb in checkboxes:
            cb.toggled.connect(lambda _: self._emit_config_changed())

    def get_configuration(self):
        return {
            "wizard": self.wizard_cb.isChecked(),
            "preview": self.preview_cb.isChecked(),
            "preset_management": self.preset_management_cb.isChecked(),
        }

    def load_configuration(self, config):
        self.wizard_cb.setChecked(config.get("wizard", False))
        self.preview_cb.setChecked(config.get("preview", False))
        self.preset_management_cb.setChecked(config.get("preset_management", False))

    def validate(self):
        # No required fields for now
        return True

    def reset(self):
        self.wizard_cb.setChecked(False)
        self.preview_cb.setChecked(False)
        self.preset_management_cb.setChecked(False)
