import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from ui.components import FileTreePreview


@pytest.fixture
def app():
    """Create or reuse QApplication instance for Qt tests"""
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    yield app


@pytest.fixture
def sample_config():
    return {
        "project_info": {
            "project_name": "TestPlugin",
            "template_name": "My Template",
            "template_url": "repo.git",
        },
        "implementations": {"melatonin_inspector": True, "preset_management": True, "preset_format": "JSON"},
        "configuration": {"standalone": True, "vst3": False},
        "user_experience": {"wizard": True},
        "development_workflow": {"vcs": True},
    }


def test_preview_updates_from_configuration(qtbot, app, sample_config):
    preview = FileTreePreview()
    qtbot.addWidget(preview)

    preview.set_configuration(sample_config)
    qtbot.waitUntil(
        lambda: (not preview.is_updating()) and preview._tree.topLevelItemCount() == 1,
        timeout=1000,
    )

    assert preview._tree.topLevelItemCount() == 1
    root = preview._tree.topLevelItem(0)
    assert root.text(0) == "TestPlugin"

    # Enabled feature should appear as enabled
    modules = next(
        root.child(i)
        for i in range(root.childCount())
        if root.child(i).text(0).startswith("Modules")
    )
    enabled_found = any(
        "Melatonin Inspector" in modules.child(i).text(0) and "Enabled" in modules.child(i).text(1)
        for i in range(modules.childCount())
    )
    assert enabled_found

    # Metrics should reflect non-zero files and enabled features
    assert "Files:" in preview._file_count_lbl.text()
    assert "Features:" in preview._feature_lbl.text()


def test_preview_shows_format_details(qtbot, app):
    preview = FileTreePreview()
    qtbot.addWidget(preview)

    config = {
        "project_info": {"project_name": "FormatPlugin"},
        "configuration": {
            "vst3": True,
            "au": True,
            "clap": True,
            "auv3": True,
            "au_component_type": "aufx",
            "au_component_subtype": "synth",
            "au_component_manufacturer": "Acme",
            "au_version": "1.2.3",
            "clap_extensions": "note-ports",
            "clap_features": "instrument",
            "auv3_platform": "macOS",
        },
    }

    preview.set_configuration(config)
    qtbot.waitUntil(
        lambda: (not preview.is_updating()) and preview._tree.topLevelItemCount() == 1,
        timeout=1000,
    )

    root = preview._tree.topLevelItem(0)
    format_details = next(
        (
            root.child(i)
            for i in range(root.childCount())
            if root.child(i).text(0).startswith("Format Details")
        ),
        None,
    )
    assert format_details is not None
    child_names = [format_details.child(i).text(0) for i in range(format_details.childCount())]
    assert any("Audio Unit Resources" in name for name in child_names)
    assert any("CLAP Manifest" in name for name in child_names)
    assert any("AUv3 Platform" in name for name in child_names)
