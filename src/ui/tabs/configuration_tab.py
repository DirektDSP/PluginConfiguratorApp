"""Configuration tab for build, GUI, and DSP options."""

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
)

from core.base_tab import BaseTab
from ui.components.validation_footer import ValidationFooter


class ConfigurationTab(BaseTab):
    """Tab for general plugin configuration (build, GUI, DSP, etc.)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)

        # --- Build Settings ---
        self.build_group = QGroupBox("Build Settings / Plugin Formats")
        build_layout = QFormLayout()
        self.standalone_cb = QCheckBox("Standalone")
        self.vst3_cb = QCheckBox("VST3")
        self.vst3_cb.setChecked(True)
        self.au_cb = QCheckBox("AU")
        self.au_cb.setChecked(True)
        self.auv3_cb = QCheckBox("AUv3")
        self.clap_cb = QCheckBox("CLAP")
        self.clap_cb.setChecked(True)
        build_layout.addRow(self.standalone_cb)
        build_layout.addRow(self.vst3_cb)
        build_layout.addRow(self.au_cb)
        build_layout.addRow(self.auv3_cb)
        build_layout.addRow(self.clap_cb)
        self.build_group.setLayout(build_layout)

        # --- GUI Settings ---
        self.gui_group = QGroupBox("GUI Settings")
        gui_layout = QFormLayout()
        self.gui_width = QSpinBox()
        self.gui_width.setRange(200, 4000)
        self.gui_width.setValue(800)
        self.gui_height = QSpinBox()
        self.gui_height.setRange(200, 4000)
        self.gui_height.setValue(600)
        self.resizable_cb = QCheckBox("Resizable Window")
        self.bg_image = QLineEdit()
        self.bg_image.setPlaceholderText("Background image path (optional)")
        gui_layout.addRow("Width:", self.gui_width)
        gui_layout.addRow("Height:", self.gui_height)
        gui_layout.addRow(self.resizable_cb)
        gui_layout.addRow("Background Image:", self.bg_image)
        self.gui_group.setLayout(gui_layout)

        # --- Code Signing & Installer ---
        self.code_group = QGroupBox("Code Signing & Installer")
        code_layout = QFormLayout()
        self.code_signing_cb = QCheckBox("Enable Code Signing")
        self.installer_cb = QCheckBox("Generate Installer")
        code_layout.addRow(self.code_signing_cb)
        code_layout.addRow(self.installer_cb)
        self.code_group.setLayout(code_layout)

        # --- DSP Feature Toggles ---
        self.dsp_group = QGroupBox("DSP Feature Toggles")
        dsp_layout = QFormLayout()
        self.default_bypass_cb = QCheckBox("Default Bypass")
        self.in_gain_cb = QCheckBox("Input Gain")
        self.out_gain_cb = QCheckBox("Output Gain")
        dsp_layout.addRow(self.default_bypass_cb)
        dsp_layout.addRow(self.in_gain_cb)
        dsp_layout.addRow(self.out_gain_cb)
        self.dsp_group.setLayout(dsp_layout)

        # --- Add all groups to main layout ---
        self.main_layout.addWidget(self.build_group)
        self.main_layout.addWidget(self.gui_group)
        self.main_layout.addWidget(self.code_group)
        self.main_layout.addWidget(self.dsp_group)
        self.main_layout.addStretch()

        # Validation footer
        self.validation_footer = ValidationFooter(self)
        self.main_layout.addWidget(self.validation_footer)

    def setup_connections(self):
        """Connect signals to slots"""
        format_checkboxes = [
            self.standalone_cb,
            self.vst3_cb,
            self.au_cb,
            self.auv3_cb,
            self.clap_cb,
        ]
        other_checkboxes = [
            self.resizable_cb,
            self.code_signing_cb,
            self.installer_cb,
            self.default_bypass_cb,
            self.in_gain_cb,
            self.out_gain_cb,
        ]
        for cb in format_checkboxes:
            cb.toggled.connect(lambda checked: self._emit_config_changed())
            cb.toggled.connect(self._update_validation_footer)
        for cb in other_checkboxes:
            cb.toggled.connect(lambda checked: self._emit_config_changed())
        self.gui_width.valueChanged.connect(lambda value: self._emit_config_changed())
        self.gui_height.valueChanged.connect(lambda value: self._emit_config_changed())
        self.bg_image.textChanged.connect(lambda text: self._emit_config_changed())
        self.validation_footer.fix_requested.connect(self._focus_first_invalid_format)
        self._update_validation_footer()

    def get_configuration(self):
        return {
            # Build settings
            "standalone": self.standalone_cb.isChecked(),
            "vst3": self.vst3_cb.isChecked(),
            "au": self.au_cb.isChecked(),
            "auv3": self.auv3_cb.isChecked(),
            "clap": self.clap_cb.isChecked(),
            # GUI settings
            "gui_width": self.gui_width.value(),
            "gui_height": self.gui_height.value(),
            "resizable": self.resizable_cb.isChecked(),
            "background_image": self.bg_image.text().strip(),
            # Code signing & installer
            "code_signing": self.code_signing_cb.isChecked(),
            "installer": self.installer_cb.isChecked(),
            # DSP toggles
            "default_bypass": self.default_bypass_cb.isChecked(),
            "input_gain": self.in_gain_cb.isChecked(),
            "output_gain": self.out_gain_cb.isChecked(),
        }

    def load_configuration(self, config):
        self.standalone_cb.setChecked(config.get("standalone", False))
        self.vst3_cb.setChecked(config.get("vst3", True))
        self.au_cb.setChecked(config.get("au", True))
        self.auv3_cb.setChecked(config.get("auv3", False))
        self.clap_cb.setChecked(config.get("clap", True))
        self.gui_width.setValue(config.get("gui_width", 800))
        self.gui_height.setValue(config.get("gui_height", 600))
        self.resizable_cb.setChecked(config.get("resizable", False))
        self.bg_image.setText(config.get("background_image", ""))
        self.code_signing_cb.setChecked(config.get("code_signing", False))
        self.installer_cb.setChecked(config.get("installer", False))
        self.default_bypass_cb.setChecked(config.get("default_bypass", False))
        self.in_gain_cb.setChecked(config.get("input_gain", False))
        self.out_gain_cb.setChecked(config.get("output_gain", False))

    def validate(self):
        # At least one plugin format must be selected
        return (
            self.standalone_cb.isChecked()
            or self.vst3_cb.isChecked()
            or self.au_cb.isChecked()
            or self.auv3_cb.isChecked()
            or self.clap_cb.isChecked()
        )

    def get_invalid_field_count(self) -> int:
        """Return 1 if no plugin format is selected, 0 otherwise."""
        return 0 if self.validate() else 1

    @Slot()
    def _update_validation_footer(self, _checked=None):
        """Refresh the footer to reflect whether a plugin format is selected."""
        if self.validate():
            self.validation_footer.set_ready()
        else:
            self.validation_footer.set_errors(1)

    @Slot()
    def _focus_first_invalid_format(self):
        """Focus the VST3 checkbox as the canonical 'fix' target."""
        self.vst3_cb.setFocus()

    def reset(self):
        self.standalone_cb.setChecked(False)
        self.vst3_cb.setChecked(True)
        self.au_cb.setChecked(True)
        self.auv3_cb.setChecked(False)
        self.clap_cb.setChecked(True)
        self.gui_width.setValue(800)
        self.gui_height.setValue(600)
        self.resizable_cb.setChecked(False)
        self.bg_image.setText("")
        self.code_signing_cb.setChecked(False)
        self.installer_cb.setChecked(False)
        self.default_bypass_cb.setChecked(False)
        self.in_gain_cb.setChecked(False)
        self.out_gain_cb.setChecked(False)
