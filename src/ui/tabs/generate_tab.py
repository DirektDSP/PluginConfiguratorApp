"""Generate Tab - summary review and project generation."""

from PySide6.QtCore import Qt, QThread, QUrl, Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.base_tab import BaseTab
from core.project_worker import ProjectWorker


class GenerateTab(BaseTab):
    """Tab: Generate - Summary review and project generation.

    Displays a read-only summary of the entire project configuration grouped
    into Metadata, Build, DSP, UI, and Modules sections, with per-section
    validation status indicators, a prominent Generate button, threaded
    progress tracking, and a post-generation success dialog with actions.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._full_config: dict = {}
        self._worker: ProjectWorker | None = None
        self._thread: QThread | None = None
        self._had_error: bool = False
        self.setup_ui()
        self.setup_connections()
        self._emit_config_changed()

    # ------------------------------------------------------------------ #
    # BaseTab interface                                                     #
    # ------------------------------------------------------------------ #

    def setup_ui(self):
        """Build the tab layout."""
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(10)

        # -- Validation status header --
        status_group = QGroupBox("Configuration Status")
        status_inner = QVBoxLayout()
        status_inner.setSpacing(4)
        self._status_icons: dict[str, QLabel] = {}
        for section in ("Metadata", "Build", "DSP", "UI", "Modules"):
            row = QHBoxLayout()
            icon_lbl = QLabel("⚪")
            icon_lbl.setFixedWidth(22)
            section_lbl = QLabel(section)
            row.addWidget(icon_lbl)
            row.addWidget(section_lbl)
            row.addStretch()
            status_inner.addLayout(row)
            self._status_icons[section] = icon_lbl
        status_group.setLayout(status_inner)
        content_layout.addWidget(status_group)

        # -- Summary sections --
        self._metadata_lbl = self._make_summary_label()
        content_layout.addWidget(self._make_section_group("Metadata", self._metadata_lbl))

        self._build_lbl = self._make_summary_label()
        content_layout.addWidget(self._make_section_group("Build", self._build_lbl))

        self._dsp_lbl = self._make_summary_label()
        content_layout.addWidget(self._make_section_group("DSP", self._dsp_lbl))

        self._ui_lbl = self._make_summary_label()
        content_layout.addWidget(self._make_section_group("UI", self._ui_lbl))

        self._modules_lbl = self._make_summary_label()
        content_layout.addWidget(self._make_section_group("Modules", self._modules_lbl))

        # -- Progress group --
        progress_group = QGroupBox("Generation Progress")
        progress_inner = QVBoxLayout()
        progress_inner.setSpacing(6)

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(True)
        self._progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_inner.addWidget(self._progress_bar)

        self._status_label = QLabel("Ready to generate project")
        progress_inner.addWidget(self._status_label)

        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        self._log_text.setMinimumHeight(120)
        self._log_text.setPlaceholderText("Generation logs will appear here...")
        self._log_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        progress_inner.addWidget(self._log_text)

        progress_group.setLayout(progress_inner)
        content_layout.addWidget(progress_group)
        content_layout.addStretch()

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

        # -- Generate button row (outside scroll so it always stays visible) --
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(12, 6, 12, 12)
        self._generate_button = QPushButton("🚀  Generate Project")
        self._generate_button.setMinimumHeight(48)
        self._generate_button.setToolTip(
            "Generate the plugin project based on the current configuration.\n"
            "Metadata fields and at least one plugin format must be filled in."
        )
        self._generate_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._generate_button.setStyleSheet("QPushButton { font-weight: bold; font-size: 14px; }")
        btn_row.addWidget(self._generate_button)
        outer_layout.addLayout(btn_row)

    def setup_connections(self):
        """Wire up signals."""
        self._generate_button.clicked.connect(self._on_generate_clicked)

    def get_configuration(self) -> dict:
        """Return the tab's stored configuration."""
        return {"full_config": self._full_config, "tab_complete": bool(self._full_config)}

    def load_configuration(self, config: dict) -> None:
        """Load a previously saved configuration into the tab."""
        self._full_config = config.get("full_config", {})
        if self._full_config:
            self._refresh_summary()
        self._emit_config_changed()

    def validate(self) -> bool:
        """The Generate tab itself has no required fields - always reports valid."""
        return True

    def reset(self) -> None:
        """Reset the tab to its initial state."""
        self._full_config = {}
        for lbl in (
            self._metadata_lbl,
            self._build_lbl,
            self._dsp_lbl,
            self._ui_lbl,
            self._modules_lbl,
        ):
            lbl.setText("—")
        for icon in self._status_icons.values():
            icon.setText("⚪")
            icon.setToolTip("")
        self._log_text.clear()
        self._progress_bar.setValue(0)
        self._status_label.setText("Ready to generate project")
        self._generate_button.setEnabled(True)
        self._emit_config_changed()

    # ------------------------------------------------------------------ #
    # Public helpers                                                       #
    # ------------------------------------------------------------------ #

    def update_full_config(self, config: dict) -> None:
        """Refresh the tab with a freshly-collected full configuration dict.

        Called by MainWindow whenever the user switches to this tab, so the
        summary always reflects the latest state of the other tabs.
        """
        self._full_config = config.copy()
        self._refresh_summary()

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _make_summary_label() -> QLabel:
        lbl = QLabel("—")
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        return lbl

    @staticmethod
    def _make_section_group(title: str, label: QLabel) -> QGroupBox:
        group = QGroupBox(title)
        inner = QVBoxLayout()
        inner.addWidget(label)
        group.setLayout(inner)
        return group

    def _refresh_summary(self) -> None:
        """Populate summary labels and update validation indicators."""
        project_info = self._full_config.get("project_info", {})
        config_data = self._full_config.get("configuration", {})
        implementations = self._full_config.get("implementations", {})
        user_exp = self._full_config.get("user_experience", {})

        def _val(v: str) -> str:
            return v if v else "—"

        # ---- Metadata ----
        self._metadata_lbl.setText(
            "\n".join(
                [
                    f"Project Name:      {_val(project_info.get('project_name', ''))}",
                    f"Product Name:      {_val(project_info.get('product_name', ''))}",
                    f"Company:           {_val(project_info.get('company_name', ''))}",
                    f"Bundle ID:         {_val(project_info.get('bundle_id', ''))}",
                    f"Manufacturer Code: {_val(project_info.get('manufacturer_code', ''))}",
                    f"Plugin Code:       {_val(project_info.get('plugin_code', ''))}",
                    f"Version:           {_val(project_info.get('version', ''))}",
                    f"Output Directory:  {_val(project_info.get('output_directory', ''))}",
                ]
            )
        )

        # ---- Build ----
        formats = [
            fmt.upper()
            for fmt in ("standalone", "vst3", "au", "auv3", "clap")
            if config_data.get(fmt, False)
        ]
        self._build_lbl.setText(
            "\n".join(
                [
                    f"Plugin Formats: {', '.join(formats) if formats else 'None selected'}",
                    f"Code Signing:   {'Enabled' if config_data.get('code_signing') else 'Disabled'}",
                    f"Installer:      {'Enabled' if config_data.get('installer') else 'Disabled'}",
                ]
            )
        )

        # ---- DSP ----
        self._dsp_lbl.setText(
            "\n".join(
                [
                    f"Default Bypass: {'Enabled' if config_data.get('default_bypass') else 'Disabled'}",
                    f"Input Gain:     {'Enabled' if config_data.get('input_gain') else 'Disabled'}",
                    f"Output Gain:    {'Enabled' if config_data.get('output_gain') else 'Disabled'}",
                ]
            )
        )

        # ---- UI ----
        self._ui_lbl.setText(
            "\n".join(
                [
                    f"GUI Size:   {config_data.get('gui_width', 800)} x {config_data.get('gui_height', 600)}",
                    f"Resizable:  {'Yes' if config_data.get('resizable') else 'No'}",
                    f"Wizard:     {'Enabled' if user_exp.get('wizard') else 'Disabled'}",
                    f"Preview:    {'Enabled' if user_exp.get('preview') else 'Disabled'}",
                ]
            )
        )

        # ---- Modules ----
        module_map = {
            "moonbase_licensing": "Moonbase Licensing",
            "melatonin_inspector": "Melatonin Inspector",
            "custom_gui_framework": "Custom GUI Framework",
            "logging_framework": "Logging Framework",
            "clap_builds": "CLAP Builds",
            "ab_comparison": "A/B Comparison",
            "state_management": "State Management",
            "gpu_audio": "GPU Audio",
        }
        active_modules = [label for key, label in module_map.items() if implementations.get(key)]
        if implementations.get("preset_management"):
            fmt = implementations.get("preset_format", "")
            active_modules.append(f"Preset Management{' (' + fmt + ')' if fmt else ''}")
        self._modules_lbl.setText(
            "\n".join(active_modules) if active_modules else "No optional modules selected"
        )

        # ---- Validation status indicators ----
        metadata_valid = all(
            project_info.get(f, "").strip()
            for f in (
                "project_name",
                "company_name",
                "bundle_id",
                "manufacturer_code",
                "output_directory",
            )
        )
        build_valid = bool(formats)

        statuses: dict[str, bool] = {
            "Metadata": metadata_valid,
            "Build": build_valid,
            "DSP": True,
            "UI": True,
            "Modules": True,
        }
        for section, ok in statuses.items():
            icon = self._status_icons[section]
            icon.setText("✅" if ok else "❌")
            icon.setToolTip(
                f"{section}: {'Valid' if ok else 'Incomplete — please check this section'}"
            )

    # ------------------------------------------------------------------ #
    # Generation                                                           #
    # ------------------------------------------------------------------ #

    @Slot()
    def _on_generate_clicked(self) -> None:
        if not self._full_config:
            QMessageBox.warning(
                self,
                "No Configuration",
                "Please complete the previous tabs before generating the project.",
            )
            return

        project_info = self._full_config.get("project_info", {})
        project_name = project_info.get("project_name", "Unknown")
        output_dir = project_info.get("output_directory", "Unknown")

        reply = QMessageBox.question(
            self,
            "Confirm Generation",
            f"Generate project '{project_name}'?\n\nOutput: {output_dir}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._start_generation()

    def _start_generation(self) -> None:
        """Kick off the threaded project generation."""
        self._had_error = False
        self._generate_button.setEnabled(False)
        self._progress_bar.setValue(0)
        self._log_text.clear()
        self._status_label.setText("Starting generation...")
        self._log_text.append("=== Starting Project Generation ===")

        project_info = self._full_config.get("project_info", {})
        config_data = self._full_config.get("configuration", {})
        implementations = self._full_config.get("implementations", {})
        dev_workflow = self._full_config.get("development_workflow", {})

        params = {
            "project_name": project_info.get("project_name", ""),
            "product_name": project_info.get("product_name", ""),
            "company_name": project_info.get("company_name", ""),
            "bundle_id": project_info.get("bundle_id", ""),
            "manufacturer_code": project_info.get("manufacturer_code", ""),
            "plugin_code": project_info.get("plugin_code", ""),
            "version": project_info.get("version", "1.0.0"),
            "output_directory": project_info.get("output_directory", ""),
            "fork_url": project_info.get("template_url", ""),
            "options": {
                "standalone": config_data.get("standalone", False),
                "vst3": config_data.get("vst3", True),
                "au": config_data.get("au", True),
                "auv3": config_data.get("auv3", False),
                "clap": config_data.get("clap", True),
                "melatonin": implementations.get("melatonin_inspector", False),
                "moonbase": implementations.get("moonbase_licensing", False),
                "create_git_repo": dev_workflow.get("vcs", True),
            },
        }

        self._thread = QThread(self)
        self._worker = ProjectWorker(params)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress_message)
        self._worker.progress_value.connect(self._progress_bar.setValue)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._on_generation_finished)
        self._worker.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

    @Slot(str)
    def _on_progress_message(self, message: str) -> None:
        self._log_text.append(message)
        self._status_label.setText(message)

    @Slot(str)
    def _on_error(self, error: str) -> None:
        self._had_error = True
        self._log_text.append(f"ERROR: {error}")
        self._status_label.setText("Generation failed!")
        self._generate_button.setEnabled(True)
        QMessageBox.critical(self, "Generation Failed", f"Failed to generate project:\n\n{error}")

    @Slot()
    def _on_generation_finished(self) -> None:
        self._generate_button.setEnabled(True)
        if self._had_error:
            return

        self._status_label.setText("Generation complete!")
        self._log_text.append("\n=== Generation Complete ===")
        self._log_text.append("Project generated successfully!")

        output_dir = self._full_config.get("project_info", {}).get("output_directory", "")

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Project Generated")
        msg_box.setText(f"Project generated successfully!\n\nLocation: {output_dir}")
        msg_box.setIcon(QMessageBox.Icon.Information)
        open_btn = msg_box.addButton("Open Folder", QMessageBox.ButtonRole.ActionRole)
        msg_box.addButton("Close", QMessageBox.ButtonRole.RejectRole)
        msg_box.exec()

        if msg_box.clickedButton() is open_btn and output_dir:
            QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))
