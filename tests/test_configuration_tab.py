"""Tests for ConfigurationTab.get_validation_issues()."""

import sys

import pytest
from PySide6.QtWidgets import QApplication

from ui.tabs.configuration_tab import ConfigurationTab


@pytest.fixture(scope="module")
def app():
    """Create a single QApplication instance for all tests in this module."""
    instance = QApplication.instance()
    if not instance:
        instance = QApplication(sys.argv)
    yield instance


@pytest.fixture
def tab(app):
    """Return a fresh ConfigurationTab for each test."""
    t = ConfigurationTab()
    yield t
    t.deleteLater()


class TestConfigurationTabValidationIssues:
    def test_get_validation_issues_returns_list(self, tab):
        issues = tab.get_validation_issues()
        assert isinstance(issues, list)

    def test_get_validation_issues_empty_when_format_selected(self, tab):
        tab.vst3_cb.setChecked(True)
        assert tab.get_validation_issues() == []

    def test_get_validation_issues_reports_issue_when_no_format_selected(self, tab):
        tab.standalone_cb.setChecked(False)
        tab.vst3_cb.setChecked(False)
        tab.au_cb.setChecked(False)
        tab.auv3_cb.setChecked(False)
        tab.clap_cb.setChecked(False)
        issues = tab.get_validation_issues()
        assert len(issues) == 1
        assert "plugin format" in issues[0].lower()

    def test_get_validation_issues_empty_for_standalone_only(self, tab):
        tab.standalone_cb.setChecked(True)
        tab.vst3_cb.setChecked(False)
        tab.au_cb.setChecked(False)
        tab.auv3_cb.setChecked(False)
        tab.clap_cb.setChecked(False)
        assert tab.get_validation_issues() == []

    def test_get_validation_issues_consistent_with_validate(self, tab):
        """get_validation_issues() must be empty iff validate() returns True."""
        tab.vst3_cb.setChecked(True)
        assert (tab.get_validation_issues() == []) == tab.validate()
        tab.standalone_cb.setChecked(False)
        tab.vst3_cb.setChecked(False)
        tab.au_cb.setChecked(False)
        tab.auv3_cb.setChecked(False)
        tab.clap_cb.setChecked(False)
        assert (tab.get_validation_issues() == []) == tab.validate()
