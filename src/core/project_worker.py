import os
import shutil
import stat
import subprocess

from PySide6.QtCore import QObject, Signal

from core.utils import (
    create_cmake_file,
    create_gitignore_file,
    create_readme_from_variables,
    generate_plugin_id,
    update_workflow_files,
)


class ProjectWorker(QObject):
    """Worker class that handles project generation in a separate thread"""

    # Signals
    progress = Signal(str)  # For log messages
    progress_value = Signal(int)  # For progress bar updates
    error = Signal(str)  # For error messages
    finished = Signal()  # When work is complete

    def __init__(self, params):
        super().__init__()
        self.params = params
        # Get plugin formats and options from options panel if provided
        self.options = params.get('options', {})

    def remove_readonly(self, func, path, excinfo):
        """Error handler for shutil.rmtree to handle read-only files"""
        os.chmod(path, stat.S_IWRITE)
        func(path)

    def run(self):
        """Main worker method that runs in the thread"""
        try:
            # Clone the template repository
            self.clone_template_repo()

            # Fetch main submodules
            self.fetch_submodules()

            # Fetch optional submodules
            self.fetch_optional_submodules()

            # Generate project files
            self.generate_project_files()

            # Clean up git history
            self.cleanup_git_history()

            # Initialize new git repository if requested
            self.init_git_repo()

            # We're done!
            self.progress.emit("Project generation completed successfully!")
            self.progress_value.emit(100)
            self.finished.emit()

        except Exception as e:
            self.error.emit(f"Project generation failed: {e!s}")
            self.finished.emit()

    def clone_template_repo(self):
        """Clone the template repository"""
        try:
            self.progress.emit(f"Cloning template repository: {self.params['fork_url']}")
            self.progress_value.emit(5)

            subprocess.run(
                ["git", "clone", self.params["fork_url"], self.params["output_directory"]],
                check=True,
                capture_output=True,
                text=True
            )

            self.progress.emit("Template repository cloned successfully")
            self.progress_value.emit(15)

        except subprocess.CalledProcessError as e:
            self.progress.emit(f"Error during cloning: {e.stderr}")
            raise RuntimeError(f"Failed to clone template repository: {e.stderr}")

    def fetch_submodules(self):
        """Fetch and initialize submodules"""
        try:
            self.progress.emit("Fetching submodules...")
            self.progress_value.emit(20)

            subprocess.run(
                ["git", "submodule", "update", "--init", "--recursive"],
                cwd=self.params["output_directory"],
                check=True,
                capture_output=True,
                text=True
            )

            self.progress.emit("Submodules fetched successfully")
            self.progress_value.emit(30)

        except subprocess.CalledProcessError as e:
            self.progress.emit(f"Error fetching submodules: {e.stderr}")
            raise RuntimeError(f"Failed to fetch submodules: {e.stderr}")

    def fetch_optional_submodules(self):
        """Fetch optional submodules based on configuration"""
        # Fetch Moonbase if selected
        if self.options.get("moonbase", False):
            try:
                self.progress.emit("Fetching Moonbase submodule...")
                self.progress_value.emit(40)

                moonbase_url = "https://github.com/Moonbase-sh/moonbase_JUCEClient"
                subprocess.run(
                    ["git", "submodule", "add", "-b", "main", moonbase_url, "modules/moonbase_JUCEClient"],
                    cwd=self.params["output_directory"],
                    check=True,
                    capture_output=True,
                    text=True
                )

                self.progress.emit("Fetching Moonbase submodules...")
                subprocess.run(
                    ["git", "submodule", "update", "--init", "--recursive"],
                    cwd=self.params["output_directory"],
                    check=True,
                    capture_output=True,
                    text=True
                )

                self.progress.emit("Moonbase submodule fetched successfully")
                self.progress_value.emit(50)

            except subprocess.CalledProcessError as e:
                # Check if it's already added
                if "already exists" in e.stderr:
                    self.progress.emit("Moonbase submodule already exists")
                    self.progress_value.emit(50)
                else:
                    self.progress.emit(f"Error fetching Moonbase submodule: {e.stderr}")
                    raise RuntimeError(f"Failed to fetch Moonbase submodule: {e.stderr}")

    def prepare_project_variables(self):
        """Prepare variables for template substitution"""
        # Read version from file if it exists
        version_path = os.path.join(self.params["output_directory"], "VERSION")
        if os.path.exists(version_path):
            with open(version_path) as f:
                version = f.read().strip()
        else:
            version = "0.0.1"

        # Generate unique plugin code
        plugin_code = generate_plugin_id()

        # Format selection
        formats = []
        if self.options.get("standalone", False):
            formats.append("Standalone")
        if self.options.get("vst3", True): # Default to true
            formats.append("VST3")
        if self.options.get("au", True): # Default to true
            formats.append("AU")
        if self.options.get("auv3", False):
            formats.append("AUv3")

        # Format string for CMake
        formats_string = f"FORMATS {' '.join(formats)}"

        # JUCE options
        juce_web_browser = "1" if self.options.get("juce_web_browser", False) else "0"
        juce_use_curl = "1" if self.options.get("juce_curl", False) else "0"
        juce_vst3_can_replace_vst2 = "1" if self.options.get("juce_vst2", False) else "0"

        # Moonbase options
        moonbase = self.options.get("moonbase", False)
        moonbase_include = 'add_subdirectory(modules/moonbase_JUCEClient)' if moonbase else ''
        moonbase_licensing = f'MOONBASE_DECLARE_LICENSING ("{self.params["company_name"]}", "{self.params["project_name"]}", VERSION)' if moonbase else ''
        moonbase_linking = f'target_link_libraries("{self.params["project_name"]}" PRIVATE moonbase_JUCEClient)' if moonbase else ''

        # Final variables dictionary
        return {
            "PROJECT_NAME": self.params["project_name"],
            "PRODUCT_NAME": self.params["product_name"],
            "COMPANY_NAME": self.params["company_name"],
            "BUNDLE_ID": self.params["bundle_id"],
            "MANUFACTURER_CODE": self.params["manufacturer_code"],
            "PLUGIN_CODE": plugin_code,
            "FORMATS": formats_string,
            "VERSION": version,
            "JUCE_WEB_BROWSER": juce_web_browser,
            "JUCE_USE_CURL": juce_use_curl,
            "JUCE_VST3_CAN_REPLACE_VST2": juce_vst3_can_replace_vst2,
            "MOONBASE_INCLUDE": moonbase_include,
            "MOONBASE_LICENSING": moonbase_licensing,
            "MOONBASE_LINKING": moonbase_linking,

            # Variables for README.md
            "plugin_name": self.params["product_name"],
            "plugin_description": "an audio plugin created with DirektDSP Plugin Configurator",
            "plugin_overview": "It provides a foundation for building professional audio plugins with JUCE.",
            "plugin_features": "- Modern C++ codebase\n- CMake build system\n- Cross-platform support",
            "installation_instructions": "1. Copy the plugin files to your system's plugin directories\n2. Restart your DAW\n3. Scan for new plugins",
            "usage_instructions": "1. Add the plugin to an audio track\n2. Adjust parameters as needed",
            "additional_info": f"Created with DirektDSP Plugin Configurator. Version: {version}",
            "roadmap": "- Add more features\n- Expand platform support",
            "feedback_instructions": "Please report any issues or feature requests to the project repository."
        }

    def generate_project_files(self):
        """Generate project files from templates with proper variable substitution"""
        self.progress.emit("Generating project files...")
        self.progress_value.emit(60)

        # Prepare variables for template substitution
        project_variables = self.prepare_project_variables()

        # Generate CMakeLists.txt
        self.progress.emit("Generating CMakeLists.txt...")
        create_cmake_file(self.params['output_directory'], project_variables)
        self.progress.emit("CMakeLists.txt generated successfully")

        # Generate .gitignore
        self.progress.emit("Generating .gitignore...")
        create_gitignore_file(self.params['output_directory'])
        self.progress.emit(".gitignore generated successfully")

        # Generate README.md
        self.progress.emit("Generating README.md...")
        create_readme_from_variables(self.params['output_directory'], project_variables)
        self.progress.emit("README.md generated successfully")

        # Update workflow files
        self.progress.emit("Updating GitHub workflow files...")
        update_workflow_files(self.params['output_directory'], project_variables)
        self.progress.emit("GitHub workflow files updated successfully")

        self.progress_value.emit(80)

    def cleanup_git_history(self):
        """Remove Git history from the template to start fresh"""
        self.progress.emit("Cleaning up Git history...")
        git_dir = os.path.join(self.params["output_directory"], ".git")

        if os.path.exists(git_dir):
            try:
                shutil.rmtree(git_dir, onerror=self.remove_readonly)
                self.progress.emit("Git history removed successfully")
            except Exception as e:
                self.progress.emit(f"Error removing Git directory: {e!s}")
                raise RuntimeError(f"Failed to remove Git directory: {e!s}")

    def init_git_repo(self):
        """Initialize a new Git repository if requested"""
        if self.options.get("create_git_repo", True):
            self.progress.emit("Initializing new Git repository...")

            try:
                # Initialize repository
                subprocess.run(
                    ["git", "init"],
                    cwd=self.params["output_directory"],
                    check=True,
                    capture_output=True,
                    text=True
                )

                # Add all files
                subprocess.run(
                    ["git", "add", "."],
                    cwd=self.params["output_directory"],
                    check=True,
                    capture_output=True,
                    text=True
                )

                # Commit
                subprocess.run(
                    ["git", "commit", "-m", "Initial commit (generated by Plugin Configurator)"],
                    cwd=self.params["output_directory"],
                    check=True,
                    capture_output=True,
                    text=True
                )

                self.progress.emit("Git repository initialized successfully")
                self.progress_value.emit(90)

            except subprocess.CalledProcessError as e:
                self.progress.emit(f"Error initializing Git repository: {e.stderr}")
                raise RuntimeError(f"Failed to initialize Git repository: {e.stderr}")
