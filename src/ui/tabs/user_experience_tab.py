from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QCheckBox, QFormLayout, QLabel
)
from PySide6.QtCore import Signal

class UserExperienceTab(QWidget):
    """Tab for configuring user experience options"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
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
