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
        self.template_library_cb = QCheckBox("Template Library Management")
        self.preset_management_cb = QCheckBox("Preset Configuration Management")
        self.batch_generation_cb = QCheckBox("Batch Project Generation")
        form.addRow(self.wizard_cb)
        form.addRow(self.preview_cb)
        form.addRow(self.template_library_cb)
        form.addRow(self.preset_management_cb)
        form.addRow(self.batch_generation_cb)
        self.group.setLayout(form)
        self.layout.addWidget(self.group)
        self.layout.addStretch()

    def setup_connections(self):
        """Connect signals to slots"""
        checkboxes = [
            self.wizard_cb, self.preview_cb, self.template_library_cb,
            self.preset_management_cb, self.batch_generation_cb,
        ]
        for cb in checkboxes:
            cb.toggled.connect(lambda _: self._emit_config_changed())

    def get_configuration(self):
        return {
            "wizard": self.wizard_cb.isChecked(),
            "preview": self.preview_cb.isChecked(),
            "template_library": self.template_library_cb.isChecked(),
            "preset_management": self.preset_management_cb.isChecked(),
            "batch_generation": self.batch_generation_cb.isChecked(),
        }

    def load_configuration(self, config):
        self.wizard_cb.setChecked(config.get("wizard", False))
        self.preview_cb.setChecked(config.get("preview", False))
        self.template_library_cb.setChecked(config.get("template_library", False))
        self.preset_management_cb.setChecked(config.get("preset_management", False))
        self.batch_generation_cb.setChecked(config.get("batch_generation", False))

    def validate(self):
        # No required fields for now
        return True

    def reset(self):
        self.wizard_cb.setChecked(False)
        self.preview_cb.setChecked(False)
        self.template_library_cb.setChecked(False)
        self.preset_management_cb.setChecked(False)
        self.batch_generation_cb.setChecked(False)
