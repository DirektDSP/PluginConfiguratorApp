from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QCheckBox,
    QFileDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QTextEdit, QMessageBox,
    QScrollArea, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, QThread, QObject, pyqtSignal
import sys
import os

import functions as fn


class ProjectWorker(QObject):
    progress = pyqtSignal(str)
    pbar = pyqtSignal(int)
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        import subprocess as sp
        try:
            # --- Clone the repository ---
            fork_url = "https://github.com/DirektDSP/pamplejuce.git"
            self.progress.emit("Cloning pamplejuce repo...")
            sp.run(["git", "clone", fork_url, self.params["output_directory"]], check=True)
            self.progress.emit("Cloned pamplejuce repo successfully.")
            self.pbar.emit(10)
        except Exception as e:
            self.progress.emit("Error during cloning.")
            self.error.emit("An error occurred while cloning the pamplejuce repo. Ensure you have git installed and try again.")
            self.finished.emit()
            return


        try:
            # --- Fetch main submodules ---
            self.progress.emit("Fetching submodules...")
            sp.run(["git", "submodule", "update", "--init", "--recursive"], cwd=self.params["output_directory"], check=True)
            self.progress.emit("Fetched main submodules successfully.")
            self.pbar.emit(20)
        except Exception as e:
            self.progress.emit("Error fetching submodules.")
            self.error.emit("An error occurred while fetching submodules. Ensure you can access all the required submodules with your account.")
            self.finished.emit()
            return

        # --- Optionally fetch the moonbase submodule ---
        if self.params.get("moonbase", False):
            try:
                self.progress.emit("Fetching moonbase submodule...")
                moonbase_url = "https://github.com/Moonbase-sh/moonbase_JUCEClient"
                sp.run(["git", "submodule", "add", "-b", "main", moonbase_url, "modules/moonbase_JUCEClient"],
                       cwd=self.params["output_directory"], check=True)
                
                self.progress.emit("Fetching Moonbase submodules...")
                sp.run(["git", "submodule", "update", "--init", "--recursive"], cwd=self.params["output_directory"], check=True)
                self.progress.emit("Fetched Moonbase submodules successfully.")

                self.progress.emit("Fetched moonbase submodule successfully.")
                self.pbar.emit(60)
            except Exception as e:
                self.progress.emit("Error fetching moonbase submodule.")
                self.error.emit("An error occurred while fetching the moonbase submodule. Ensure you have access to the moonbase repo.")
                self.finished.emit()
                return

        # --- Plugin Info Generation ---
        self.progress.emit("Collecting plugin parameters...")
        PROJECT_NAME = self.params["project_name"]
        PRODUCT_NAME = self.params["product_name"]
        COMPANY_NAME = self.params["company_name"]
        BUNDLE_ID = self.params["bundle_id"]
        PLUGIN_CODE = fn.generate_plugin_id()
        MANUFACTURER_CODE = self.params["manufacturer_code"]

        FORMATS = "FORMATS"
        if self.params["standalone"]:
            FORMATS += " Standalone"
        if self.params["vst3"]:
            FORMATS += " VST3"
        if self.params["au"]:
            FORMATS += " AU AUv3"
        if self.params["clap"]:
            FORMATS += " CLAP"

        # Read version from file; if not found, use a default version
        version_path = os.path.join(self.params["output_directory"], "VERSION")
        if os.path.exists(version_path):
            with open(version_path, "r") as f:
                VERSION = f.read().strip()
        else:
            VERSION = "0.0.0"
        CMAKE_PROJECT_NAME = PROJECT_NAME + " v" + VERSION
        
        JUCE_WEB_BROWSER = 1 if self.params["juce_web_browser"] else 0
        JUCE_USE_CURL = 1 if self.params["juce_curl"] else 0
        JUCE_VST3_CAN_REPLACE_VST2 = 1 if self.params["juce_vst2"] else 0

        CMAKE_FILE_PATH = os.path.join(self.params["output_directory"], "CMakeLists.txt")
        try:
            with open(CMAKE_FILE_PATH, "r") as f:
                CMAKE_FILE = f.read()
        except Exception as e:
            self.progress.emit("Error reading CMakeLists.txt")
            self.error.emit("Failed to read CMakeLists.txt in output directory. Does it exist?")
            self.finished.emit()
            return
        
        # --- Generate the CMake File ---
        self.progress.emit("Generating CMake File...")
        self.pbar.emit(70)

        fn.create_cmake_file(self.params['output_directory'], {
            "PROJECT_NAME": PROJECT_NAME,
            "PRODUCT_NAME": PRODUCT_NAME,
            "COMPANY_NAME": COMPANY_NAME,
            "MANUFACTURER_CODE": MANUFACTURER_CODE,
            "BUNDLE_ID": BUNDLE_ID,
            "PLUGIN_CODE": PLUGIN_CODE,
            "FORMATS": FORMATS,
            "VERSION": VERSION,
            "CMAKE_PROJECT_NAME": CMAKE_PROJECT_NAME,
            "JUCE_WEB_BROWSER": JUCE_WEB_BROWSER,
            "JUCE_USE_CURL": JUCE_USE_CURL,
            "JUCE_VST3_CAN_REPLACE_VST2": JUCE_VST3_CAN_REPLACE_VST2,
            "MOONBASE": self.params.get("moonbase", False)
        })
        self.progress.emit("CMake File Generated.")
        self.pbar.emit(90)

        # --- Optionally make a git repo ---
        if self.params.get("create_git_repo", True):
            try:
                self.progress.emit("Initializing git repository...")
                sp.run(["git", "init"], cwd=self.params["output_directory"], check=True)
                sp.run(["git", "add", "."], cwd=self.params["output_directory"], check=True)
                sp.run(["git", "commit", "-m", "Initial commit by configurator"], cwd=self.params["output_directory"], check=True)
                self.progress.emit("Git repository initialized successfully.")
            except Exception as e:
                self.progress.emit("Error initializing git repository.")
                self.error.emit("An error occurred while initializing the git repository.")
                self.error.emit(e)
                self.finished.emit()
                return

        self.finished.emit()
        self.progress.emit("Project generated successfully.")
        self.pbar.emit(100)


class ProjectGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DirektDSP Project Generator")
        self.setGeometry(100, 100, 920, 640)
        self.setStyleSheet(open("src/style.qss", "r").read())
        self.initUI()

    def initUI(self):
        # Main vertical layout: top area (project info & options) and bottom progress section
        main_layout = QVBoxLayout(self)
        top_layout = QHBoxLayout()

        # === Project Info Section ===
        project_info_box = QGroupBox("Project Info")
        project_layout = QVBoxLayout()

        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText("No spaces, only letters and numbers")
        self.project_name.textChanged.connect(self.update_bundle_id)

        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("Plugin Name")

        self.company_name = QLineEdit()
        self.company_name.setPlaceholderText("DirektDSP")

        self.bundle_id = QLineEdit()
        self.bundle_id.setPlaceholderText("com.direktdsp.pluginname")

        self.manufacturer_code = QLineEdit()
        self.manufacturer_code.setPlaceholderText("Manu")

        project_layout.addWidget(QLabel("Project Name (internal naming w/o spaces)"))
        project_layout.addWidget(self.project_name)

        project_layout.addWidget(QLabel("Product Name (what the DAW shows)"))
        project_layout.addWidget(self.product_name)

        project_layout.addWidget(QLabel("Company Name (DirektDSP)"))
        project_layout.addWidget(self.company_name)

        project_layout.addWidget(QLabel("Bundle ID (com.direktdsp.pluginname)"))
        project_layout.addWidget(self.bundle_id)

        project_layout.addWidget(QLabel("Manufacturer Code (Manu)"))
        project_layout.addWidget(self.manufacturer_code)

        output_layout = QHBoxLayout()
        self.output_directory = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_output)
        output_layout.addWidget(self.output_directory)
        output_layout.addWidget(self.browse_button)

        project_layout.addWidget(QLabel("Output Directory"))
        project_layout.addLayout(output_layout)

        self.generate_button = QPushButton("Generate Project")
        self.generate_button.clicked.connect(self.generate_project)
        project_layout.addWidget(self.generate_button)

        project_info_box.setLayout(project_layout)
        top_layout.addWidget(project_info_box)

        # === Options Section (Scrollable) ===
        options_box = QGroupBox("Options")
        options_layout = QVBoxLayout()

        # Scroll Area Setup
        scroll_area = QScrollArea()
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidgetResizable(True)

        # Scrollable Content Widget & Layout
        scroll_content = QWidget()
        scroll_content_layout = QVBoxLayout(scroll_content)
        options_label_style_override = "font-size: 14px; font-weight: bold;"

        # Helper function for creating separators
        def create_separator():
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
            separator.setStyleSheet("color: #5E81AC;")
            return separator

        # --- Enabled Formats Group ---
        enabled_formats_container = QWidget()
        enabled_formats_container.setStyleSheet(
            "background-color: rgba(94, 129, 172, 0.2); border-radius: 5px; padding: 5px;"
        )
        ef_layout = QVBoxLayout(enabled_formats_container)
        label_enabled_formats = QLabel("Enabled Formats")
        label_enabled_formats.setStyleSheet(options_label_style_override)
        ef_layout.addWidget(label_enabled_formats)
        self.standalone_checkbox = QCheckBox("Standalone")
        self.vst3_checkbox = QCheckBox("VST3")
        self.au_checkbox = QCheckBox("AU + AUv3")
        self.clap_checkbox = QCheckBox("CLAP")
        ef_layout.addWidget(self.standalone_checkbox)
        ef_layout.addWidget(self.vst3_checkbox)
        ef_layout.addWidget(self.au_checkbox)
        ef_layout.addWidget(self.clap_checkbox)
        # Default Values
        self.standalone_checkbox.setChecked(False)
        self.vst3_checkbox.setChecked(True)
        self.au_checkbox.setChecked(True)
        self.clap_checkbox.setChecked(True)
        scroll_content_layout.addWidget(enabled_formats_container)
        scroll_content_layout.addWidget(create_separator())

        # --- Extras Group ---
        extras_container = QWidget()
        extras_container.setStyleSheet(
            "background-color: rgba(94, 129, 172, 0.2); border-radius: 5px; padding: 5px;"
        )
        extras_layout = QVBoxLayout(extras_container)
        extras_label = QLabel("Extras")
        extras_label.setStyleSheet(options_label_style_override)
        extras_layout.addWidget(extras_label)
        self.create_git_repo_checkbox = QCheckBox("Create Git Repository")
        self.melatonin_checkbox = QCheckBox("Melatonin Inspector")
        self.moonbase_checkbox = QCheckBox("Moonbase Licensing")
        self.clap_export_checkbox = QCheckBox("CLAP export support")
        self.juce_develop_checkbox = QCheckBox("Use JUCE Develop branch")
        self.xcode_prettify_checkbox = QCheckBox("XCode Prettify")
        extras_layout.addWidget(self.create_git_repo_checkbox)
        extras_layout.addWidget(self.melatonin_checkbox)
        extras_layout.addWidget(self.moonbase_checkbox)
        extras_layout.addWidget(self.clap_export_checkbox)
        extras_layout.addWidget(self.juce_develop_checkbox)
        extras_layout.addWidget(self.xcode_prettify_checkbox)
        # Default Values
        self.create_git_repo_checkbox.setChecked(True)
        self.melatonin_checkbox.setChecked(True)
        self.moonbase_checkbox.setChecked(False)
        self.clap_export_checkbox.setChecked(True)
        self.juce_develop_checkbox.setChecked(True)
        self.xcode_prettify_checkbox.setChecked(True)
        scroll_content_layout.addWidget(extras_container)
        scroll_content_layout.addWidget(create_separator())

        # --- JUCE CMake Options Group ---
        cmake_container = QWidget()
        cmake_container.setStyleSheet(
            "background-color: rgba(94, 129, 172, 0.2); border-radius: 5px; padding: 5px;"
        )
        cmake_layout = QVBoxLayout(cmake_container)
        cmake_opts_label = QLabel("JUCE CMake Options")
        cmake_opts_label.setStyleSheet(options_label_style_override)
        cmake_layout.addWidget(cmake_opts_label)
        self.juce_curl_checkbox = QCheckBox("Enable JUCE_USE_CURL")
        self.juce_web_browser_checkbox = QCheckBox("Enable JUCE_WEB_BROWSER")
        self.juce_vst2_checkbox = QCheckBox("Enable JUCE_CAN_REPLACE_VST2")
        cmake_layout.addWidget(self.juce_curl_checkbox)
        cmake_layout.addWidget(self.juce_web_browser_checkbox)
        cmake_layout.addWidget(self.juce_vst2_checkbox)
        # Default Values
        self.juce_curl_checkbox.setChecked(False)
        self.juce_web_browser_checkbox.setChecked(False)
        self.juce_vst2_checkbox.setChecked(False)
        scroll_content_layout.addWidget(cmake_container)

        scroll_content_layout.addStretch()  # Push groups to the top
        scroll_content.setLayout(scroll_content_layout)
        scroll_area.setWidget(scroll_content)
        options_layout.addWidget(scroll_area)
        options_box.setLayout(options_layout)
        top_layout.addWidget(options_box)

        # Add top_layout (Project Info & Options) to main layout
        main_layout.addLayout(top_layout)

        # === Progress Section (Full Width at Bottom) ===
        progress_box = QGroupBox("Progress")
        progress_layout = QVBoxLayout()

        # Toggle Progress Log Visibility
        self.toggle_progress_log_checkbox = QCheckBox("Show Progress Log")
        self.toggle_progress_log_checkbox.setChecked(True)
        self.toggle_progress_log_checkbox.toggled.connect(
            lambda checked: self.progress_text.setVisible(checked)
        )
        progress_layout.addWidget(self.toggle_progress_log_checkbox)

        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        self.progress_text.setPlaceholderText("Progress will be shown here")
        self.progress_text.setStyleSheet("font-family: monospace;")
        progress_layout.addWidget(self.progress_text)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        progress_box.setLayout(progress_layout)
        main_layout.addWidget(progress_box)

    def update_bundle_id(self):
        if self.project_name.text():
            self.bundle_id.setText("com.direktdsp." + self.project_name.text())
        else:
            self.bundle_id.setText("")
            self.bundle_id.setPlaceholderText("com.direktdsp.pluginname")

    def activate_generate_button(self):
        # Enable the generate button if project name, product name, and output directory are set
        if self.project_name.text() and self.product_name.text() and self.output_directory.text():
            self.generate_button.setEnabled(True)

    def browse_output(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_directory.setText(directory)

    def show_error_dialog(self, message="An error occurred!"):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Critical)

        ok_button = msg_box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
        cancel_button = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

        msg_box.exec()

        if msg_box.clickedButton() == ok_button:
            print("OK clicked")
        elif msg_box.clickedButton() == cancel_button:
            print("Cancel clicked")

    def append_progress(self, message):
        self.progress_text.append(message)

    def generate_project(self):
        # --- Verify Inputs ---
        try:
            assert self.project_name.text(), "Project Name is required"
            assert self.project_name.text().isalnum(), "Project Name must be alphanumeric"
            assert self.project_name.text().islower(), "Project Name must be lowercase"
            assert self.product_name.text(), "Product Name is required"
            assert self.output_directory.text(), "Output Directory is required"
            assert os.path.exists(self.output_directory.text()), "Output Directory does not exist"
        except AssertionError as e:
            self.show_error_dialog(str(e))
            return

        # --- Gather parameters for the worker ---
        params = {
            "project_name": self.project_name.text().lower(),
            "product_name": self.product_name.text(),
            "company_name": (self.company_name.text() if self.company_name.text() else "DirektDSP"),
            "bundle_id": self.bundle_id.text(),
            "manufacturer_code": (self.manufacturer_code.text() if self.manufacturer_code!="" else "Manu"),
            "output_directory": self.output_directory.text(),
            "standalone": self.standalone_checkbox.isChecked(),
            "vst3": self.vst3_checkbox.isChecked(),
            "au": self.au_checkbox.isChecked(),
            "clap": self.clap_checkbox.isChecked(),
            "moonbase": self.moonbase_checkbox.isChecked(),
            "juce_curl": self.juce_curl_checkbox.isChecked(),
            "juce_web_browser": self.juce_web_browser_checkbox.isChecked(),
            "juce_vst2": self.juce_vst2_checkbox.isChecked(),
            "create_git_repo": self.create_git_repo_checkbox.isChecked()
        }

        # --- Set up the worker and thread ---
        self.thread = QThread()
        self.worker = ProjectWorker(params)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.append_progress)
        self.worker.pbar.connect(self.progress_bar.setValue)
        self.worker.error.connect(self.show_error_dialog)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(open("src/style.qss", "r").read())
    window = ProjectGenerator()
    window.show()
    sys.exit(app.exec())
