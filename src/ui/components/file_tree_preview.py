from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QStyle,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


@dataclass(frozen=True)
class TreeEntry:
    """Lightweight description of a tree entry."""

    name: str
    children: List["TreeEntry"]
    enabled: bool = True
    is_file: bool = False
    hint: str | None = None


class FileTreePreview(QWidget):
    """Reusable preview panel that renders a generated file tree with metrics."""

    _DEBOUNCE_MS = 150

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._pending_config: dict = {}
        self._debounce = QTimer(self)
        self._debounce.setInterval(self._DEBOUNCE_MS)
        self._debounce.setSingleShot(True)
        self._debounce.timeout.connect(self._apply_pending_config)

        self._setup_ui()

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #
    def set_configuration(self, config: dict) -> None:
        """Schedule a tree refresh with debouncing for smooth updates."""
        self._pending_config = config or {}
        self._debounce.start()

    # ------------------------------------------------------------------ #
    # UI                                                                 #
    # ------------------------------------------------------------------ #
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(8)

        # Metrics row
        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(12)
        self._file_count_lbl = QLabel("Files: 0")
        self._file_size_lbl = QLabel("Size: 0 KB (est.)")
        self._feature_lbl = QLabel("Features: —")
        for lbl in (self._file_count_lbl, self._file_size_lbl, self._feature_lbl):
            lbl.setStyleSheet("font-weight: bold;")
            metrics_row.addWidget(lbl)
        metrics_row.addStretch()
        layout.addLayout(metrics_row)

        # Tree widget
        tree_group = QGroupBox("Project Structure Preview")
        tree_layout = QVBoxLayout()
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["Item", "Status"])
        self._tree.setAlternatingRowColors(True)
        self._tree.setColumnWidth(0, 220)
        tree_layout.addWidget(self._tree)

        # Legend
        legend = QHBoxLayout()
        legend.setSpacing(12)
        legend.addWidget(self._badge("✅ Enabled"))
        legend.addWidget(self._badge("⚪ Optional"))
        legend.addWidget(self._badge("🚫 Disabled"))
        legend.addStretch()
        tree_layout.addLayout(legend)
        tree_group.setLayout(tree_layout)
        layout.addWidget(tree_group)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(divider)

        # Helper text
        hint = QLabel("Updates in real-time as configuration changes across all tabs.")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(hint)

    def _badge(self, text: str) -> QLabel:
        badge = QLabel(text)
        badge.setStyleSheet(
            "QLabel { border: 1px solid #ccc; border-radius: 4px; padding: 2px 6px; }"
        )
        return badge

    # ------------------------------------------------------------------ #
    # Rendering                                                          #
    # ------------------------------------------------------------------ #
    def _apply_pending_config(self) -> None:
        config = self._pending_config
        project_info = config.get("project_info", {})
        implementations = config.get("implementations", {})
        build = config.get("configuration", {})
        ux = config.get("user_experience", {})
        workflow = config.get("development_workflow", {})

        root_name = project_info.get("project_name", "").strip() or "YourPlugin"
        root = TreeEntry(
            name=root_name,
            children=self._build_structure(project_info, implementations, build, ux, workflow),
            enabled=True,
        )
        self._render_tree(root)

    def _build_structure(
        self,
        project_info: dict,
        implementations: dict,
        build: dict,
        ux: dict,
        workflow: dict,
    ) -> List[TreeEntry]:
        template_name = project_info.get("template_name", "Default Template")

        # Base skeleton
        base_dirs = {
            "source": [
                "PluginProcessor.cpp",
                "PluginProcessor.h",
                "PluginEditor.cpp",
                "PluginEditor.h",
            ],
            "assets": ["logo.png", "background.png"],
            "cmake": ["CPM.cmake", "PamplejuceVersion.cmake", "JUCEDefaults.cmake"],
            "tests": ["PluginBasicTest.cpp"],
            "packaging": ["icon.png", "installer_banner.png"],
        }

        tree: List[TreeEntry] = [
            TreeEntry(
                name=f"Template • {template_name}",
                children=[TreeEntry(name=project_info.get("template_url", ""), children=[], is_file=True)],
                enabled=True,
                hint="Selected template source",
            ),
            TreeEntry(
                name="Project Files",
                children=self._make_dir_entries(base_dirs),
                enabled=True,
                hint="Core project scaffold",
            ),
        ]

        # Build targets / formats
        formats = {
            "Standalone": build.get("standalone", False),
            "VST3": build.get("vst3", True),
            "AU": build.get("au", True),
            "AUv3": build.get("auv3", False),
            "CLAP": build.get("clap", True),
        }
        format_entries = [
            TreeEntry(name=name, children=[], enabled=enabled, is_file=True)
            for name, enabled in formats.items()
        ]
        tree.append(
            TreeEntry(
                name="Build Targets",
                children=format_entries,
                enabled=any(formats.values()),
                hint="Plugin formats to generate",
            )
        )

        # UX features
        ux_entries = [
            TreeEntry(name="Wizard", children=[], enabled=bool(ux.get("wizard")), is_file=True),
            TreeEntry(name="Preview", children=[], enabled=bool(ux.get("preview")), is_file=True),
            TreeEntry(
                name="Preset Management",
                children=[],
                enabled=bool(ux.get("preset_management")),
                is_file=True,
            ),
        ]
        tree.append(
            TreeEntry(
                name="User Experience",
                children=ux_entries,
                enabled=True,
                hint="User experience feature flags",
            )
        )

        # Implementation modules
        module_labels = {
            "moonbase_licensing": "Moonbase Licensing",
            "melatonin_inspector": "Melatonin Inspector",
            "custom_gui_framework": "Custom GUI Framework",
            "logging_framework": "Logging Framework",
            "clap_builds": "CLAP Builds",
            "ab_comparison": "A/B Comparison",
            "state_management": "State Management",
            "gpu_audio": "GPU Audio",
        }
        module_entries = [
            TreeEntry(
                name=label,
                children=[],
                enabled=bool(implementations.get(key)),
                is_file=True,
                hint="Optional module",
            )
            for key, label in module_labels.items()
        ]
        if implementations.get("preset_management"):
            fmt = implementations.get("preset_format") or "XML"
            module_entries.append(
                TreeEntry(
                    name=f"Preset Management ({fmt})",
                    children=[],
                    enabled=True,
                    is_file=True,
                )
            )
        tree.append(
            TreeEntry(
                name="Modules",
                children=module_entries,
                enabled=any(entry.enabled for entry in module_entries),
                hint="Optional integrations and modules",
            )
        )

        # Workflow integrations
        workflow_entries = [
            TreeEntry(name="Version Control", children=[], enabled=bool(workflow.get("vcs")), is_file=True),
            TreeEntry(name="Testing", children=[], enabled=bool(workflow.get("testing")), is_file=True),
            TreeEntry(
                name="Code Quality",
                children=[],
                enabled=bool(workflow.get("code_quality")),
                is_file=True,
            ),
            TreeEntry(
                name="Validation Tools",
                children=[],
                enabled=bool(workflow.get("validation_tools")),
                is_file=True,
            ),
            TreeEntry(
                name="Scaffolding",
                children=[],
                enabled=bool(workflow.get("scaffolding")),
                is_file=True,
            ),
        ]
        tree.append(
            TreeEntry(
                name="Development Workflow",
                children=workflow_entries,
                enabled=any(entry.enabled for entry in workflow_entries),
                hint="Tooling applied during generation",
            )
        )

        return tree

    def _make_dir_entries(self, base_dirs: Dict[str, List[str]]) -> List[TreeEntry]:
        entries: List[TreeEntry] = []
        for dirname, files in base_dirs.items():
            entries.append(
                TreeEntry(
                    name=dirname,
                    children=[TreeEntry(name=f, children=[], enabled=True, is_file=True) for f in files],
                    enabled=True,
                )
            )
        return entries

    def _render_tree(self, root: TreeEntry) -> None:
        self._tree.clear()
        root_item = QTreeWidgetItem(self._tree, [root.name, ""])
        root_item.setExpanded(True)
        self._populate_items(root_item, root.children)
        self._tree.resizeColumnToContents(0)

        file_count, est_size = self._compute_metrics()
        self._file_count_lbl.setText(f"Files: {file_count}")
        self._file_size_lbl.setText(f"Size: {est_size} KB (est.)")
        enabled_features = len([i for i in self._iter_items() if i.data(0, Qt.ItemDataRole.UserRole)])
        self._feature_lbl.setText(f"Features: {enabled_features} enabled")

    def _populate_items(self, parent_item: QTreeWidgetItem, entries: List[TreeEntry]) -> None:
        for entry in entries:
            item = QTreeWidgetItem(parent_item, [entry.name, self._status_text(entry.enabled)])
            item.setData(0, Qt.ItemDataRole.UserRole, entry.enabled)
            if entry.hint:
                item.setToolTip(0, entry.hint)
            item.setIcon(0, self._folder_icon() if entry.children else self._file_icon())
            if not entry.children:
                item.setData(1, Qt.ItemDataRole.DisplayRole, self._status_text(entry.enabled))
            else:
                item.setData(1, Qt.ItemDataRole.DisplayRole, "")
            self._populate_items(item, entry.children)

    # ------------------------------------------------------------------ #
    # Metrics                                                            #
    # ------------------------------------------------------------------ #
    def _iter_items(self) -> List[QTreeWidgetItem]:
        items: List[QTreeWidgetItem] = []
        root = self._tree.invisibleRootItem()
        for i in range(root.childCount()):
            items.extend(self._collect_children(root.child(i)))
        return items

    def _collect_children(self, item: QTreeWidgetItem) -> List[QTreeWidgetItem]:
        items = [item]
        for i in range(item.childCount()):
            items.extend(self._collect_children(item.child(i)))
        return items

    def _compute_metrics(self) -> Tuple[int, int]:
        file_items = [i for i in self._iter_items() if i.childCount() == 0]
        file_count = len(file_items)
        # Rough heuristic: 8 KB per file, +2 KB for enabled feature metadata
        enabled_features = len([i for i in file_items if i.data(0, Qt.ItemDataRole.UserRole)])
        est_size = file_count * 8 + enabled_features * 2
        return file_count, est_size

    # ------------------------------------------------------------------ #
    # Helpers                                                            #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _status_text(enabled: bool) -> str:
        return "✅ Enabled" if enabled else "🚫 Disabled"

    def _folder_icon(self) -> QIcon:
        try:
            return self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        except RuntimeError:
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.GlobalColor.transparent)
            return QIcon(pixmap)

    def _file_icon(self) -> QIcon:
        try:
            return self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        except RuntimeError:
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.GlobalColor.transparent)
            return QIcon(pixmap)
