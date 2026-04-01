from functools import partial
from typing import Any

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QStyle,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.base_tab import BaseTab
from core.gui_components import get_components_grouped
from ui.components import SUBTEXT_COLOR, AccordionExpander

# ---------------------------------------------------------------------------
# Template & module definitions
# ---------------------------------------------------------------------------

_DSP_TEMPLATES: dict[str, dict] = {
    "Simple": {
        "description": "Basic DSP chain with minimal processing",
        "source_files": ["PluginProcessor.cpp", "PluginProcessor.h"],
        "features": ["Basic processor scaffold"],
    },
    "EQ": {
        "description": "Parametric EQ with multiple bands",
        "source_files": [
            "PluginProcessor.cpp",
            "PluginProcessor.h",
            "EqProcessor.cpp",
            "EqProcessor.h",
            "BandConfig.h",
        ],
        "features": [
            "Multi-band EQ processor",
            "Per-band configuration",
            "Basic processor scaffold",
        ],
    },
    "Reverb": {
        "description": "Algorithmic reverb with room simulation",
        "source_files": [
            "PluginProcessor.cpp",
            "PluginProcessor.h",
            "ReverbProcessor.cpp",
            "ReverbProcessor.h",
        ],
        "features": [
            "Algorithmic reverb engine",
            "Room simulation parameters",
            "Basic processor scaffold",
        ],
    },
    "Full": {
        "description": "Complete DSP chain with all common components",
        "source_files": [
            "PluginProcessor.cpp",
            "PluginProcessor.h",
            "EqProcessor.cpp",
            "EqProcessor.h",
            "ReverbProcessor.cpp",
            "ReverbProcessor.h",
            "CompressorProcessor.cpp",
            "CompressorProcessor.h",
        ],
        "features": [
            "Multi-band EQ processor",
            "Algorithmic reverb engine",
            "Dynamics compressor",
            "Basic processor scaffold",
        ],
    },
    "Scratch": {
        "description": "Empty template - build your DSP from scratch",
        "source_files": ["PluginProcessor.cpp", "PluginProcessor.h"],
        "features": ["Bare processor stub"],
    },
}

_UI_TEMPLATES: dict[str, dict] = {
    "Minimal": {
        "description": "Basic editor with minimal controls",
        "editor_files": ["PluginEditor.cpp", "PluginEditor.h"],
        "features": ["Basic editor scaffold"],
    },
    "Standard": {
        "description": "Standard editor with common UI components",
        "editor_files": [
            "PluginEditor.cpp",
            "PluginEditor.h",
            "MainComponent.cpp",
            "MainComponent.h",
            "LookAndFeel.h",
        ],
        "features": ["Main component layout", "Custom look-and-feel", "Basic editor scaffold"],
    },
    "Advanced": {
        "description": "Advanced editor with custom controls and animations",
        "editor_files": [
            "PluginEditor.cpp",
            "PluginEditor.h",
            "MainComponent.cpp",
            "MainComponent.h",
            "CustomControls.cpp",
            "CustomControls.h",
            "LookAndFeel.cpp",
            "LookAndFeel.h",
            "Animations.h",
        ],
        "features": [
            "Main component layout",
            "Custom control widgets",
            "Custom look-and-feel",
            "Animation system",
            "Basic editor scaffold",
        ],
    },
    "Scratch": {
        "description": "Empty editor - build your UI from scratch",
        "editor_files": ["PluginEditor.cpp", "PluginEditor.h"],
        "features": ["Bare editor stub"],
    },
}

_MODULES: dict[str, dict] = {
    "Moonbase": {
        "label": "Moonbase Licensing",
        "tooltip": "Include the Moonbase_Sh licensing client for copy protection",
        "module_dir": "moonbase",
    },
    "Inspector": {
        "label": "Melatonin Inspector",
        "tooltip": "GUI inspection and live-debugging tool for JUCE",
        "module_dir": "melatonin_inspector",
    },
    "Presets": {
        "label": "Preset Manager",
        "tooltip": "Full preset save/load/factory system",
        "module_dir": "preset_manager",
        "extra_source": ["PresetManager.cpp", "PresetManager.h"],
    },
}

_MOONBASE_LICENSE_TYPES = ["Trial", "Perpetual", "Subscription"]
_DEFAULT_MOONBASE_LICENSE = "Trial"
_DEFAULT_GRACE_PERIOD_DAYS = 14
_PRESET_FORMATS = ["XML", "JSON", "Binary"]
_DEFAULT_PRESET_FORMAT = "XML"
_PRESET_STORAGE_LOCATIONS = ["Project-relative", "User AppData", "Cloud/Sync"]
_DEFAULT_PRESET_STORAGE = "Project-relative"


class ImplementTab(BaseTab):
    """Tab 3: Implement - DSP/UI templates and module selection.

    This is the third tab in the 4-lifecycle UI structure.  Users choose
    DSP and UI starter templates and opt-in to optional modules such as
    Moonbase licensing, the Melatonin inspector, and preset management.
    A file-tree preview on the right reflects all selections live.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        self.update_file_tree()
        self._emit_config_changed()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def setup_ui(self):
        """Initialize UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Horizontal splitter: form (left) | file tree (right)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(5)
        self.splitter.setChildrenCollapsible(False)

        # ---- LEFT: scrollable form ----
        self._form_container = QWidget()
        self._form_container.setMinimumWidth(380)
        form_outer = QVBoxLayout(self._form_container)
        form_outer.setContentsMargins(10, 10, 10, 10)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        self._form_widget = QWidget()
        form_layout = QVBoxLayout(self._form_widget)
        form_layout.setSpacing(14)

        # -- DSP template --
        dsp_group = QGroupBox("DSP Template")
        dsp_form = QFormLayout()
        dsp_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        self.dsp_combo = QComboBox()
        self.dsp_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.dsp_combo.addItems(list(_DSP_TEMPLATES.keys()))
        self.dsp_combo.setToolTip("Choose the DSP processing template to scaffold")

        self.dsp_description = QLabel(_DSP_TEMPLATES["Simple"]["description"])
        self.dsp_description.setWordWrap(True)
        self.dsp_description.setStyleSheet("color: grey; font-style: italic;")

        self.dsp_features = QLabel(self._format_features(_DSP_TEMPLATES["Simple"]))
        self.dsp_features.setWordWrap(True)
        self.dsp_features.setStyleSheet(f"color: {SUBTEXT_COLOR}; font-size: 11px;")

        dsp_form.addRow("Template:", self.dsp_combo)
        dsp_form.addRow("", self.dsp_description)
        dsp_form.addRow("", self.dsp_features)
        dsp_group.setLayout(dsp_form)

        # -- UI template --
        ui_group = QGroupBox("UI Template")
        ui_form = QFormLayout()
        ui_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        self.ui_combo = QComboBox()
        self.ui_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.ui_combo.addItems(list(_UI_TEMPLATES.keys()))
        self.ui_combo.setToolTip("Choose the editor/UI template to scaffold")

        self.ui_description = QLabel(_UI_TEMPLATES["Minimal"]["description"])
        self.ui_description.setWordWrap(True)
        self.ui_description.setStyleSheet("color: grey; font-style: italic;")

        self.ui_features = QLabel(self._format_features(_UI_TEMPLATES["Minimal"]))
        self.ui_features.setWordWrap(True)
        self.ui_features.setStyleSheet(f"color: {SUBTEXT_COLOR}; font-size: 11px;")

        self.ui_components_label = QLabel("DirektDSP_GUI Components:")
        self.ui_components_label.setStyleSheet("font-weight: bold; margin-top: 6px;")

        self.ui_components_list = QLabel(self._format_components("Minimal"))
        self.ui_components_list.setWordWrap(True)
        self.ui_components_list.setStyleSheet(f"color: {SUBTEXT_COLOR}; font-size: 11px;")
        self.ui_components_list.setTextFormat(Qt.TextFormat.RichText)

        ui_form.addRow("Template:", self.ui_combo)
        ui_form.addRow("", self.ui_description)
        ui_form.addRow("", self.ui_features)
        ui_form.addRow("", self.ui_components_label)
        ui_form.addRow("", self.ui_components_list)
        ui_group.setLayout(ui_form)

        # -- Modules accordion --
        self._modules_group = self._build_modules_accordion()

        form_layout.addWidget(dsp_group)
        form_layout.addWidget(ui_group)
        form_layout.addWidget(self._modules_group)
        form_layout.addStretch()

        self._scroll.setWidget(self._form_widget)
        form_outer.addWidget(self._scroll)

        # ---- RIGHT: file tree preview ----
        self._tree_container = QWidget()
        self._tree_container.setMinimumWidth(280)
        tree_outer = QVBoxLayout(self._tree_container)
        tree_outer.setContentsMargins(10, 10, 10, 10)

        tree_group = QGroupBox("Project Structure Preview")
        tree_inner = QVBoxLayout()

        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabel("Project Files")
        self.file_tree.setAlternatingRowColors(True)
        self.file_tree.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        tree_inner.addWidget(self.file_tree)
        tree_group.setLayout(tree_inner)
        tree_outer.addWidget(tree_group)

        # Assemble splitter
        self.splitter.addWidget(self._form_container)
        self.splitter.addWidget(self._tree_container)
        self.splitter.setSizes([int(self.width() * 0.55), int(self.width() * 0.45)])

        main_layout.addWidget(self.splitter)

    def _build_modules_accordion(self) -> AccordionExpander:
        """Build the collapsible modules section (accordion disclosure)."""
        self._module_checkboxes: dict[str, QCheckBox] = {}
        self._module_expanders: dict[str, AccordionExpander] = {}

        self._modules_expander = AccordionExpander(
            "Modules",
            "Enable optional modules and configure their options",
            start_expanded=False,
        )

        body_layout = self._modules_expander.body_layout

        for key, info in _MODULES.items():
            toggle = QCheckBox("Enable")
            toggle.setToolTip(info["tooltip"])
            self._module_checkboxes[key] = toggle

            module_expander = AccordionExpander(
                info["label"],
                subtitle=info.get("tooltip"),
                control_widget=toggle,
                start_expanded=False,
            )
            self._module_expanders[key] = module_expander

            module_body = module_expander.body_layout
            module_body.addWidget(self._hint_label(info.get("tooltip", "")))

            if key == "Moonbase":
                module_body.addLayout(self._build_moonbase_options())
            elif key == "Presets":
                module_body.addLayout(self._build_presets_options())
            else:
                module_body.addWidget(self._hint_label("No additional options for this module."))

            body_layout.addWidget(module_expander)

        body_layout.addStretch()
        return self._modules_expander

    def _build_moonbase_options(self) -> QFormLayout:
        layout = QFormLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        self._moonbase_license_type = QComboBox()
        self._moonbase_license_type.addItems(_MOONBASE_LICENSE_TYPES)
        default_license_idx = self._moonbase_license_type.findText(_DEFAULT_MOONBASE_LICENSE)
        if default_license_idx >= 0:
            self._moonbase_license_type.setCurrentIndex(default_license_idx)

        self._moonbase_grace_period = QSpinBox()
        self._moonbase_grace_period.setRange(0, 60)
        self._moonbase_grace_period.setSuffix(" days")
        self._moonbase_grace_period.setValue(_DEFAULT_GRACE_PERIOD_DAYS)

        layout.addRow("License type:", self._moonbase_license_type)
        layout.addRow("Grace period:", self._moonbase_grace_period)
        return layout

    def _build_presets_options(self) -> QFormLayout:
        layout = QFormLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        self._preset_format = QComboBox()
        self._preset_format.addItems(_PRESET_FORMATS)
        default_format_idx = self._preset_format.findText(_DEFAULT_PRESET_FORMAT)
        if default_format_idx >= 0:
            self._preset_format.setCurrentIndex(default_format_idx)

        self._preset_storage = QComboBox()
        self._preset_storage.addItems(_PRESET_STORAGE_LOCATIONS)
        default_storage_idx = self._preset_storage.findText(_DEFAULT_PRESET_STORAGE)
        if default_storage_idx >= 0:
            self._preset_storage.setCurrentIndex(default_storage_idx)

        self._preset_storage_expander = AccordionExpander(
            "Storage options", "Choose where presets are stored", start_expanded=False
        )
        self._preset_storage_expander.body_layout.addWidget(self._preset_storage)

        layout.addRow("Format:", self._preset_format)
        layout.addRow("Storage:", self._preset_storage_expander)
        return layout

    def _hint_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet(f"color: {SUBTEXT_COLOR};")
        return label

    def _value_if_enabled(self, enabled: bool, value: Any) -> Any | None:
        """Return *value* when the module is enabled, otherwise ``None``."""
        return value if enabled else None

    # ------------------------------------------------------------------
    # Signal connections
    # ------------------------------------------------------------------

    def setup_connections(self):
        """Connect signals to slots."""
        self.dsp_combo.currentTextChanged.connect(self._on_dsp_changed)
        self.ui_combo.currentTextChanged.connect(self._on_ui_changed)
        self._modules_expander.toggled.connect(self._on_modules_toggle)
        for key, cb in self._module_checkboxes.items():
            cb.toggled.connect(partial(self._on_module_toggled, key))

        self._moonbase_license_type.currentTextChanged.connect(self._on_config_changed)
        self._moonbase_grace_period.valueChanged.connect(self._on_config_changed)
        self._preset_format.currentTextChanged.connect(self._on_config_changed)
        self._preset_storage.currentTextChanged.connect(self._on_config_changed)
        self._preset_storage_expander.toggled.connect(self._on_config_changed)
        for module_expander in self._module_expanders.values():
            module_expander.toggled.connect(self._on_config_changed)

        # Ensure option controls reflect initial checkbox states
        for key, cb in self._module_checkboxes.items():
            self._update_module_enabled_state(key, cb.isChecked(), emit=False)

    def _on_module_toggled(self, key: str, checked: bool):
        """Handle module enablement toggles and reveal nested options."""
        if checked:
            self._modules_expander.set_expanded(True)
        self._update_module_enabled_state(key, checked)

    def _update_module_enabled_state(self, key: str, enabled: bool, *, emit: bool = True):
        expander = self._module_expanders.get(key)
        if expander:
            # Expand when enabled to reveal options; collapse when disabled
            expander.set_expanded(enabled)

        if key == "Moonbase":
            self._moonbase_license_type.setEnabled(enabled)
            self._moonbase_grace_period.setEnabled(enabled)
        elif key == "Presets":
            self._preset_format.setEnabled(enabled)
            self._preset_storage.setEnabled(enabled)
            self._preset_storage_expander.setEnabled(enabled)

        if emit:
            self._on_config_changed()

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    @staticmethod
    def _format_features(info: dict) -> str:
        """Format a template's feature list as checkmark-prefixed lines."""
        features = info.get("features", [])
        if not features:
            return ""
        return "\n".join(f"\u2713  {f}" for f in features)

    @staticmethod
    def _format_components(template_name: str) -> str:
        """Format DirektDSP_GUI components as an HTML list grouped by category."""
        grouped = get_components_grouped(template_name)
        if not grouped:
            return ""
        lines: list[str] = []
        for category, components in grouped.items():
            lines.append(f"<b>{category}/</b>")
            for comp in components:
                lines.append(f"&nbsp;&nbsp;\u2713 {comp.name} — <i>{comp.description}</i>")
        return "<br>".join(lines)

    @Slot(str)
    def _on_dsp_changed(self, text: str):
        """Update DSP description label and refresh file tree."""
        info = _DSP_TEMPLATES.get(text, {})
        self.dsp_description.setText(info.get("description", ""))
        self.dsp_features.setText(self._format_features(info))
        self._on_config_changed()

    @Slot(str)
    def _on_ui_changed(self, text: str):
        """Update UI description label and refresh file tree."""
        info = _UI_TEMPLATES.get(text, {})
        self.ui_description.setText(info.get("description", ""))
        self.ui_features.setText(self._format_features(info))
        self.ui_components_list.setText(self._format_components(text))
        self._on_config_changed()

    @Slot(bool)
    def _on_modules_toggle(self, checked: bool):
        """Emit config when the modules accordion state changes for persistence."""
        self._emit_config_changed()

    @Slot()
    def _on_config_changed(self):
        """Propagate any change to the file tree and config signal."""
        self.update_file_tree()
        self._emit_config_changed()

    # ------------------------------------------------------------------
    # File tree
    # ------------------------------------------------------------------

    def update_file_tree(self):
        """Rebuild the file tree preview from current selections."""
        self.file_tree.clear()

        root = QTreeWidgetItem(self.file_tree, ["YourPlugin"])
        root.setExpanded(True)

        dsp_key = self.dsp_combo.currentText()
        ui_key = self.ui_combo.currentText()

        dsp_info = _DSP_TEMPLATES.get(dsp_key, _DSP_TEMPLATES["Simple"])
        ui_info = _UI_TEMPLATES.get(ui_key, _UI_TEMPLATES["Minimal"])

        # source/ directory
        source_files = list(dsp_info["source_files"]) + list(ui_info["editor_files"])

        # Extra source files from enabled modules
        module_extra: list[str] = []
        module_dirs: list[str] = []
        for key, cb in self._module_checkboxes.items():
            if cb.isChecked():
                info = _MODULES[key]
                module_dirs.append(info["module_dir"])
                module_extra.extend(info.get("extra_source", []))

        source_files.extend(module_extra)

        self._add_tree_dir(root, "source", source_files)
        self._add_tree_dir(root, "assets", ["logo.png", "background.png"])
        self._add_tree_dir(root, "cmake", ["CPM.cmake", "PamplejuceVersion.cmake"])
        self._add_tree_dir(root, "JUCE", ["[JUCE framework]"])
        self._add_tree_dir(root, "tests", ["PluginBasicTest.cpp"])
        self._add_tree_dir(root, "packaging", ["icon.png", "installer_banner.png"])

        if module_dirs:
            self._add_tree_dir(root, "modules", module_dirs)

        # Top-level files
        for name in ["CMakeLists.txt", "README.md", "YourPlugin.jucer", ".gitignore", "LICENSE"]:
            item = QTreeWidgetItem(root, [name])
            icon = self._file_icon(name)
            if icon:
                item.setIcon(0, icon)

    def _add_tree_dir(self, parent: QTreeWidgetItem, name: str, children: list[str]):
        """Add a directory node with child file nodes."""
        dir_item = QTreeWidgetItem(parent, [name])
        folder = self._folder_icon()
        if folder:
            dir_item.setIcon(0, folder)
        for child in children:
            child_item = QTreeWidgetItem(dir_item, [child])
            icon = self._file_icon(child)
            if icon:
                child_item.setIcon(0, icon)

    def _folder_icon(self) -> QIcon | None:
        try:
            return self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        except RuntimeError:
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.GlobalColor.transparent)
            return QIcon(pixmap)

    def _file_icon(self, filename: str) -> QIcon | None:
        try:
            return self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        except RuntimeError:
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.GlobalColor.transparent)
            return QIcon(pixmap)

    # ------------------------------------------------------------------
    # BaseTab interface
    # ------------------------------------------------------------------

    def get_configuration(self) -> dict:
        """Return the current tab configuration."""
        moonbase_enabled = self._module_checkboxes["Moonbase"].isChecked()
        presets_enabled = self._module_checkboxes["Presets"].isChecked()
        return {
            "dsp_template": self.dsp_combo.currentText(),
            "ui_template": self.ui_combo.currentText(),
            "module_moonbase": moonbase_enabled,
            "module_moonbase_license_type": self._value_if_enabled(
                moonbase_enabled, self._moonbase_license_type.currentText()
            ),
            "module_moonbase_grace_period": self._value_if_enabled(
                moonbase_enabled, self._moonbase_grace_period.value()
            ),
            "module_inspector": self._module_checkboxes["Inspector"].isChecked(),
            "module_presets": presets_enabled,
            "module_presets_format": self._value_if_enabled(
                presets_enabled, self._preset_format.currentText()
            ),
            "module_presets_storage": self._value_if_enabled(
                presets_enabled, self._preset_storage.currentText()
            ),
            "modules_expanded": self._modules_expander.is_expanded,
            "module_moonbase_expanded": self._module_expanders["Moonbase"].is_expanded,
            "module_inspector_expanded": self._module_expanders["Inspector"].is_expanded,
            "module_presets_expanded": self._module_expanders["Presets"].is_expanded,
            "module_presets_storage_expanded": self._preset_storage_expander.is_expanded,
        }

    def load_configuration(self, config: dict):
        """Populate the tab from a saved configuration."""
        dsp = config.get("dsp_template", "Simple")
        idx = self.dsp_combo.findText(dsp)
        if idx >= 0:
            self.dsp_combo.setCurrentIndex(idx)

        ui = config.get("ui_template", "Minimal")
        idx = self.ui_combo.findText(ui)
        if idx >= 0:
            self.ui_combo.setCurrentIndex(idx)

        self._modules_expander.set_expanded(config.get("modules_expanded", False))

        self._module_checkboxes["Moonbase"].setChecked(config.get("module_moonbase", False))
        moonbase_license = config.get("module_moonbase_license_type")
        if moonbase_license in _MOONBASE_LICENSE_TYPES:
            self._moonbase_license_type.setCurrentText(moonbase_license)
        else:
            self._moonbase_license_type.setCurrentText(_DEFAULT_MOONBASE_LICENSE)

        grace_period = config.get("module_moonbase_grace_period")
        self._moonbase_grace_period.setValue(
            grace_period if grace_period is not None else _DEFAULT_GRACE_PERIOD_DAYS
        )

        self._module_checkboxes["Inspector"].setChecked(config.get("module_inspector", False))

        self._module_checkboxes["Presets"].setChecked(config.get("module_presets", False))
        preset_format = config.get("module_presets_format")
        if preset_format in _PRESET_FORMATS:
            self._preset_format.setCurrentText(preset_format)
        else:
            self._preset_format.setCurrentText(_DEFAULT_PRESET_FORMAT)

        preset_storage = config.get("module_presets_storage")
        if preset_storage in _PRESET_STORAGE_LOCATIONS:
            self._preset_storage.setCurrentText(preset_storage)
        else:
            self._preset_storage.setCurrentText(_DEFAULT_PRESET_STORAGE)

        self._module_expanders["Moonbase"].set_expanded(
            config.get("module_moonbase_expanded", False)
        )
        self._module_expanders["Inspector"].set_expanded(
            config.get("module_inspector_expanded", False)
        )
        self._module_expanders["Presets"].set_expanded(config.get("module_presets_expanded", False))
        self._preset_storage_expander.set_expanded(
            config.get("module_presets_storage_expanded", False)
        )

        self.update_file_tree()
        self._emit_config_changed()

    def validate(self) -> bool:
        """This tab is always valid - all selections are optional."""
        return True

    def reset(self):
        """Reset all controls to their defaults."""
        self.dsp_combo.setCurrentIndex(0)
        self.ui_combo.setCurrentIndex(0)
        for cb in self._module_checkboxes.values():
            cb.setChecked(False)
        self._moonbase_license_type.setCurrentIndex(0)
        self._moonbase_grace_period.setValue(_DEFAULT_GRACE_PERIOD_DAYS)
        self._preset_format.setCurrentIndex(0)
        self._preset_storage.setCurrentIndex(0)

        self._modules_expander.set_expanded(False)
        for module_expander in self._module_expanders.values():
            module_expander.set_expanded(False)
        self._preset_storage_expander.set_expanded(False)
        self.update_file_tree()
        self._emit_config_changed()
