"""Development workflow tab for optional tooling integrations."""

from PySide6.QtWidgets import QCheckBox, QFormLayout, QGroupBox, QVBoxLayout

from core.base_tab import BaseTab


class DevelopmentWorkflowTab(BaseTab):
    """Tab for configuring development workflow options"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)

        self.group = QGroupBox("Development Workflow Features")
        form = QFormLayout()
        self.vcs_cb = QCheckBox("Version Control Integration")
        self.testing_cb = QCheckBox("Automated Testing of Generated Projects")
        self.code_quality_cb = QCheckBox("Post-Generation Code Quality Checks")
        self.validation_tools_cb = QCheckBox("Plugin Validation Tools Integration")
        self.scaffolding_cb = QCheckBox("Project Scaffolding (README, License, etc.)")
        form.addRow(self.vcs_cb)
        form.addRow(self.testing_cb)
        form.addRow(self.code_quality_cb)
        form.addRow(self.validation_tools_cb)
        form.addRow(self.scaffolding_cb)
        self.group.setLayout(form)
        self.main_layout.addWidget(self.group)
        self.main_layout.addStretch()

    def setup_connections(self):
        """Connect signals to slots"""
        checkboxes = [
            self.vcs_cb,
            self.testing_cb,
            self.code_quality_cb,
            self.validation_tools_cb,
            self.scaffolding_cb,
        ]
        for cb in checkboxes:
            cb.toggled.connect(lambda _: self._emit_config_changed())

    def get_configuration(self):
        return {
            "vcs": self.vcs_cb.isChecked(),
            "testing": self.testing_cb.isChecked(),
            "code_quality": self.code_quality_cb.isChecked(),
            "validation_tools": self.validation_tools_cb.isChecked(),
            "scaffolding": self.scaffolding_cb.isChecked(),
        }

    def load_configuration(self, config):
        self.vcs_cb.setChecked(config.get("vcs", False))
        self.testing_cb.setChecked(config.get("testing", False))
        self.code_quality_cb.setChecked(config.get("code_quality", False))
        self.validation_tools_cb.setChecked(config.get("validation_tools", False))
        self.scaffolding_cb.setChecked(config.get("scaffolding", False))

    def validate(self):
        # No required fields for now
        return True

    def reset(self):
        self.vcs_cb.setChecked(False)
        self.testing_cb.setChecked(False)
        self.code_quality_cb.setChecked(False)
        self.validation_tools_cb.setChecked(False)
        self.scaffolding_cb.setChecked(False)

    def start_generation(self, config):
        """Start the project generation process (stub for now)"""
        # Placeholder until workflow execution is implemented.
        if config:
            self._emit_config_changed()
