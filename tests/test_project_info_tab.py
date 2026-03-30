import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from ui.tabs.project_info_tab import ProjectInfoTab


@pytest.fixture(scope="module")
def app():
    if not QApplication.instance():
        _app = QApplication(sys.argv)
    else:
        _app = QApplication.instance()
    yield _app
    _app.quit()


@pytest.fixture
def tab(app):
    return ProjectInfoTab()


class TestPluginTypeDisclosure:
    def test_fx_options_group_shown_when_fx_plugin_selected(self, tab, qtbot):
        fx_index = tab.template_combo.findText("Audio FX Plugin")
        assert fx_index >= 0
        tab.template_combo.setCurrentIndex(fx_index)
        qtbot.waitUntil(lambda: not tab.fx_options_group.isHidden(), timeout=500)
        assert tab.instrument_options_group.isHidden()

    def test_instrument_options_group_shown_when_instrument_plugin_selected(self, tab, qtbot):
        instrument_index = tab.template_combo.findText("Instrument Plugin")
        assert instrument_index >= 0
        tab.template_combo.setCurrentIndex(instrument_index)
        qtbot.waitUntil(lambda: not tab.instrument_options_group.isHidden(), timeout=500)
        assert tab.fx_options_group.isHidden()


class TestPluginTypeConfiguration:
    def test_configuration_includes_plugin_type_settings(self, tab):
        tab.template_combo.setCurrentIndex(2)
        tab.instrument_polyphony.setValue(32)
        tab.instrument_midi_input.setChecked(True)

        config = tab.get_configuration()
        assert config["plugin_type"] == tab.PLUGIN_TYPE_INSTRUMENT
        assert config["instrument_polyphony"] == 32
        assert config["instrument_midi_input"]

    def test_fx_settings_round_trip(self, tab):
        tab.template_combo.setCurrentIndex(1)
        tab.fx_wet_dry.setValue(70)
        tab.fx_sidechain.setChecked(True)
        tab.fx_latency.setValue(12)

        config = tab.get_configuration()
        new_tab = ProjectInfoTab()
        new_tab.load_configuration(config)

        assert new_tab.fx_wet_dry.value() == 70
        assert new_tab.fx_sidechain.isChecked()
        assert new_tab.fx_latency.value() == 12


class TestFileTreeUpdates:
    def test_file_tree_shows_fx_details(self, tab, qtbot):
        tab.template_combo.setCurrentIndex(1)
        tab.fx_sidechain.setChecked(True)
        tab.fx_latency.setValue(15)
        tab.update_file_tree()

        root = tab.file_tree.topLevelItem(0)
        fx_nodes = []
        for i in range(root.childCount()):
            child = root.child(i)
            if child.text(0) == "fx":
                fx_nodes.append(child)
        assert fx_nodes, "fx folder not present in file tree"
        fx_node = fx_nodes[0]
        child_labels = [fx_node.child(i).text(0) for i in range(fx_node.childCount())]
        assert any("SidechainInput" in name for name in child_labels)
        assert any("Latency_15ms" in name for name in child_labels)
