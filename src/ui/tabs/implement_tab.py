from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStyle,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.base_tab import BaseTab

# ---------------------------------------------------------------------------
# Template & module definitions
# ---------------------------------------------------------------------------

_DSP_TEMPLATES: dict[str, dict] = {
    "Simple": {
        "description": "Basic DSP chain with minimal processing",
        "source_files": ["PluginProcessor.cpp", "PluginProcessor.h"],
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
    },
    "Reverb": {
        "description": "Algorithmic reverb with room simulation",
        "source_files": [
            "PluginProcessor.cpp",
            "PluginProcessor.h",
            "ReverbProcessor.cpp",
            "ReverbProcessor.h",
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
    },
    "Scratch": {
        "description": "Empty template - build your DSP from scratch",
        "source_files": ["PluginProcessor.cpp", "PluginProcessor.h"],
    },
}

_UI_TEMPLATES: dict[str, dict] = {
    "Minimal": {
        "description": "Basic editor with minimal controls",
        "editor_files": ["PluginEditor.cpp", "PluginEditor.h"],
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
    },
    "Scratch": {
        "description": "Empty editor - build your UI from scratch",
        "editor_files": ["PluginEditor.cpp", "PluginEditor.h"],
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

        dsp_form.addRow("Template:", self.dsp_combo)
        dsp_form.addRow("", self.dsp_description)
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

        ui_form.addRow("Template:", self.ui_combo)
        ui_form.addRow("", self.ui_description)
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

    def _build_modules_accordion(self) -> QGroupBox:
        """Build the collapsible modules section (accordion disclosure)."""
        group = QGroupBox()

        outer = QVBoxLayout(group)
        outer.setContentsMargins(8, 6, 8, 8)
        outer.setSpacing(4)

        # Toggle button acts as the accordion header
        self._modules_toggle = QPushButton("▶  Modules  (click to expand)")
        self._modules_toggle.setCheckable(True)
        self._modules_toggle.setChecked(False)
        self._modules_toggle.setFlat(True)
        self._modules_toggle.setStyleSheet("text-align: left; font-weight: bold; padding: 4px;")
        self._modules_toggle.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Collapsible body
        self._modules_body = QWidget()
        body_layout = QVBoxLayout(self._modules_body)
        body_layout.setContentsMargins(16, 4, 4, 4)
        body_layout.setSpacing(8)

        self._module_checkboxes: dict[str, QCheckBox] = {}
        for key, info in _MODULES.items():
            cb = QCheckBox(info["label"])
            cb.setToolTip(info["tooltip"])
            body_layout.addWidget(cb)
            self._module_checkboxes[key] = cb

        self._modules_body.setVisible(False)

        outer.addWidget(self._modules_toggle)
        outer.addWidget(self._modules_body)

        return group

    # ------------------------------------------------------------------
    # Signal connections
    # ------------------------------------------------------------------

    def setup_connections(self):
        """Connect signals to slots."""
        self.dsp_combo.currentTextChanged.connect(self._on_dsp_changed)
        self.ui_combo.currentTextChanged.connect(self._on_ui_changed)
        self._modules_toggle.toggled.connect(self._on_modules_toggle)
        for cb in self._module_checkboxes.values():
            cb.toggled.connect(self._on_config_changed)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    @Slot(str)
    def _on_dsp_changed(self, text: str):
        """Update DSP description label and refresh file tree."""
        info = _DSP_TEMPLATES.get(text, {})
        self.dsp_description.setText(info.get("description", ""))
        self._on_config_changed()

    @Slot(str)
    def _on_ui_changed(self, text: str):
        """Update UI description label and refresh file tree."""
        info = _UI_TEMPLATES.get(text, {})
        self.ui_description.setText(info.get("description", ""))
        self._on_config_changed()

    @Slot(bool)
    def _on_modules_toggle(self, checked: bool):
        """Expand or collapse the modules body."""
        self._modules_body.setVisible(checked)
        arrow = "▼" if checked else "▶"
        label = "collapse" if checked else "expand"
        self._modules_toggle.setText(f"{arrow}  Modules  (click to {label})")

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
        return {
            "dsp_template": self.dsp_combo.currentText(),
            "ui_template": self.ui_combo.currentText(),
            "module_moonbase": self._module_checkboxes["Moonbase"].isChecked(),
            "module_inspector": self._module_checkboxes["Inspector"].isChecked(),
            "module_presets": self._module_checkboxes["Presets"].isChecked(),
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

        self._module_checkboxes["Moonbase"].setChecked(config.get("module_moonbase", False))
        self._module_checkboxes["Inspector"].setChecked(config.get("module_inspector", False))
        self._module_checkboxes["Presets"].setChecked(config.get("module_presets", False))

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
        # Collapse the accordion
        self._modules_toggle.setChecked(False)
        self.update_file_tree()
        self._emit_config_changed()
