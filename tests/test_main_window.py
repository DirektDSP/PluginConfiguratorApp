import sys

import pytest
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


@pytest.fixture
def app():
    """Create QApplication instance for Qt tests."""
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    yield app
    app.processEvents()


@pytest.fixture
def window(app):
    """Create a MainWindow instance."""
    return MainWindow()


def test_main_window_tab_structure(window):
    """MainWindow should load the new 4-tab lifecycle structure."""
    assert window.tab_widget.count() == 4
    titles = [window.tab_widget.tabText(i) for i in range(window.tab_widget.count())]
    assert titles == ["Define", "Configure", "Implement", "Generate"]
    assert window._all_tabs() == [
        window.define_tab,
        window.configure_tab,
        window.implement_tab,
        window.generate_tab,
    ]


def test_config_flow_updates_generate_preview(window):
    """Config updates should flow into ConfigurationManager and Generate tab preview."""
    window.define_tab.load_configuration(
        {"output_directory": "/tmp/plugin-output", "fork_url": "https://example.com/template.git"}
    )

    full_config = window.config_manager.get_full_config()
    assert full_config["output_directory"] == "/tmp/plugin-output"
    assert full_config["fork_url"] == "https://example.com/template.git"
    assert window.generate_tab.full_config["output_directory"] == "/tmp/plugin-output"
    assert window.generate_tab.full_config["fork_url"] == "https://example.com/template.git"
