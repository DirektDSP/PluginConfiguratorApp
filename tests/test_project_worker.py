"""Tests for ProjectWorker - project generation logic."""

from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QApplication

from core.project_worker import DEFAULT_TEMPLATE_URL, ProjectWorker


@pytest.fixture(scope="module")
def app():
    instance = QApplication.instance()
    if not instance:
        instance = QApplication(sys.argv)
    yield instance


def _make_params(
    *,
    project_name: str = "TestPlugin",
    product_name: str = "Test Plugin",
    company_name: str = "TestCo",
    bundle_id: str = "com.testco.testplugin",
    manufacturer_code: str = "Ttco",
    plugin_code: str = "TPlg",
    version: str = "2.3.4",
    output_directory: str = "/tmp/test_output",
    fork_url: str = "https://example.com/template.git",
    options: dict | None = None,
) -> dict:
    return {
        "project_name": project_name,
        "product_name": product_name,
        "company_name": company_name,
        "bundle_id": bundle_id,
        "manufacturer_code": manufacturer_code,
        "plugin_code": plugin_code,
        "version": version,
        "output_directory": output_directory,
        "fork_url": fork_url,
        "options": options or {},
    }


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------


class TestProjectWorkerInit:
    def test_params_stored(self, app):
        params = _make_params()
        worker = ProjectWorker(params)
        assert worker.params is params

    def test_options_extracted(self, app):
        params = _make_params(options={"vst3": True, "clap": True})
        worker = ProjectWorker(params)
        assert worker.options == {"vst3": True, "clap": True}

    def test_options_default_to_empty_dict(self, app):
        params = _make_params()
        params.pop("options", None)
        worker = ProjectWorker(params)
        assert worker.options == {}


# ---------------------------------------------------------------------------
# prepare_project_variables - version
# ---------------------------------------------------------------------------


class TestPrepareProjectVariablesVersion:
    def test_uses_version_from_params(self, app, tmp_path):
        params = _make_params(version="3.1.4", output_directory=str(tmp_path))
        worker = ProjectWorker(params)
        variables = worker.prepare_project_variables()
        assert variables["VERSION"] == "3.1.4"

    def test_falls_back_to_version_file_when_params_version_empty(self, app, tmp_path):
        (tmp_path / "VERSION").write_text("1.2.3")
        params = _make_params(version="", output_directory=str(tmp_path))
        worker = ProjectWorker(params)
        variables = worker.prepare_project_variables()
        assert variables["VERSION"] == "1.2.3"

    def test_falls_back_to_default_when_no_params_version_and_no_file(self, app, tmp_path):
        params = _make_params(version="", output_directory=str(tmp_path))
        worker = ProjectWorker(params)
        variables = worker.prepare_project_variables()
        assert variables["VERSION"] == "0.0.1"

    def test_params_version_takes_precedence_over_version_file(self, app, tmp_path):
        (tmp_path / "VERSION").write_text("9.9.9")
        params = _make_params(version="1.0.0", output_directory=str(tmp_path))
        worker = ProjectWorker(params)
        variables = worker.prepare_project_variables()
        assert variables["VERSION"] == "1.0.0"


# ---------------------------------------------------------------------------
# prepare_project_variables - plugin_code
# ---------------------------------------------------------------------------


class TestPrepareProjectVariablesPluginCode:
    def test_uses_plugin_code_from_params(self, app, tmp_path):
        params = _make_params(plugin_code="AbCd", output_directory=str(tmp_path))
        worker = ProjectWorker(params)
        variables = worker.prepare_project_variables()
        assert variables["PLUGIN_CODE"] == "AbCd"

    def test_generates_plugin_code_when_params_code_empty(self, app, tmp_path):
        params = _make_params(plugin_code="", output_directory=str(tmp_path))
        worker = ProjectWorker(params)
        variables = worker.prepare_project_variables()
        code = variables["PLUGIN_CODE"]
        assert len(code) == 4
        assert code[0].isupper()

    def test_generates_plugin_code_when_params_code_whitespace(self, app, tmp_path):
        params = _make_params(plugin_code="   ", output_directory=str(tmp_path))
        worker = ProjectWorker(params)
        variables = worker.prepare_project_variables()
        code = variables["PLUGIN_CODE"]
        assert len(code) == 4


# ---------------------------------------------------------------------------
# prepare_project_variables - formats
# ---------------------------------------------------------------------------


class TestPrepareProjectVariablesFormats:
    def _get_formats(self, options: dict, tmp_path) -> str:
        params = _make_params(options=options, output_directory=str(tmp_path))
        worker = ProjectWorker(params)
        return worker.prepare_project_variables()["FORMATS"]

    def test_vst3_included_by_default(self, app, tmp_path):
        fmt = self._get_formats({"vst3": True}, tmp_path)
        assert "VST3" in fmt

    def test_au_included_by_default(self, app, tmp_path):
        fmt = self._get_formats({"au": True}, tmp_path)
        assert "AU" in fmt

    def test_standalone_included_when_enabled(self, app, tmp_path):
        fmt = self._get_formats({"standalone": True}, tmp_path)
        assert "Standalone" in fmt

    def test_standalone_excluded_when_disabled(self, app, tmp_path):
        fmt = self._get_formats({"standalone": False}, tmp_path)
        assert "Standalone" not in fmt

    def test_clap_included_when_enabled(self, app, tmp_path):
        fmt = self._get_formats({"clap": True}, tmp_path)
        assert "CLAP" in fmt

    def test_clap_excluded_when_disabled(self, app, tmp_path):
        fmt = self._get_formats({"clap": False}, tmp_path)
        assert "CLAP" not in fmt

    def test_auv3_included_when_enabled(self, app, tmp_path):
        fmt = self._get_formats({"auv3": True}, tmp_path)
        assert "AUv3" in fmt

    def test_formats_string_starts_with_formats_keyword(self, app, tmp_path):
        fmt = self._get_formats({"vst3": True}, tmp_path)
        assert fmt.startswith("FORMATS")

    def test_multiple_formats_combined(self, app, tmp_path):
        fmt = self._get_formats({"standalone": True, "vst3": True, "clap": True}, tmp_path)
        assert "Standalone" in fmt
        assert "VST3" in fmt
        assert "CLAP" in fmt


# ---------------------------------------------------------------------------
# prepare_project_variables - other fields
# ---------------------------------------------------------------------------


class TestPrepareProjectVariablesFields:
    def test_project_name_in_variables(self, app, tmp_path):
        params = _make_params(project_name="MyPlugin", output_directory=str(tmp_path))
        variables = ProjectWorker(params).prepare_project_variables()
        assert variables["PROJECT_NAME"] == "MyPlugin"

    def test_product_name_in_variables(self, app, tmp_path):
        params = _make_params(product_name="My Plugin", output_directory=str(tmp_path))
        variables = ProjectWorker(params).prepare_project_variables()
        assert variables["PRODUCT_NAME"] == "My Plugin"

    def test_company_name_in_variables(self, app, tmp_path):
        params = _make_params(company_name="TestCorp", output_directory=str(tmp_path))
        variables = ProjectWorker(params).prepare_project_variables()
        assert variables["COMPANY_NAME"] == "TestCorp"

    def test_bundle_id_in_variables(self, app, tmp_path):
        params = _make_params(bundle_id="com.tc.plug", output_directory=str(tmp_path))
        variables = ProjectWorker(params).prepare_project_variables()
        assert variables["BUNDLE_ID"] == "com.tc.plug"

    def test_manufacturer_code_in_variables(self, app, tmp_path):
        params = _make_params(manufacturer_code="TcCo", output_directory=str(tmp_path))
        variables = ProjectWorker(params).prepare_project_variables()
        assert variables["MANUFACTURER_CODE"] == "TcCo"

    def test_readme_plugin_name_matches_product_name(self, app, tmp_path):
        params = _make_params(product_name="Awesome FX", output_directory=str(tmp_path))
        variables = ProjectWorker(params).prepare_project_variables()
        assert variables["plugin_name"] == "Awesome FX"


# ---------------------------------------------------------------------------
# clone_template_repo - validation
# ---------------------------------------------------------------------------


class TestCloneTemplateRepoValidation:
    def test_raises_when_output_directory_empty(self, app):
        params = _make_params(output_directory="")
        worker = ProjectWorker(params)
        with pytest.raises(RuntimeError, match="Output directory is not specified"):
            worker.clone_template_repo()

    def test_raises_when_output_directory_already_exists(self, app, tmp_path):
        existing = tmp_path / "already_exists"
        existing.mkdir()
        params = _make_params(output_directory=str(existing))
        worker = ProjectWorker(params)
        with pytest.raises(RuntimeError, match="already exists"):
            worker.clone_template_repo()

    def test_uses_default_url_when_fork_url_empty(self, app, tmp_path):
        target = str(tmp_path / "new_project")
        params = _make_params(fork_url="", output_directory=target)
        worker = ProjectWorker(params)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            worker.clone_template_repo()

        clone_call = mock_run.call_args_list[0]
        cmd = clone_call[0][0]
        assert DEFAULT_TEMPLATE_URL in cmd

    def test_uses_provided_url_when_set(self, app, tmp_path):
        target = str(tmp_path / "new_project")
        custom_url = "https://custom.example.com/template.git"
        params = _make_params(fork_url=custom_url, output_directory=target)
        worker = ProjectWorker(params)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            worker.clone_template_repo()

        clone_call = mock_run.call_args_list[0]
        cmd = clone_call[0][0]
        assert custom_url in cmd


# ---------------------------------------------------------------------------
# _cleanup_on_failure
# ---------------------------------------------------------------------------


class TestCleanupOnFailure:
    def test_removes_existing_output_directory(self, app, tmp_path):
        output = tmp_path / "partial_project"
        output.mkdir()
        (output / "some_file.txt").write_text("data")

        params = _make_params(output_directory=str(output))
        worker = ProjectWorker(params)
        worker._cleanup_on_failure()

        assert not output.exists()

    def test_does_nothing_when_output_directory_absent(self, app, tmp_path):
        non_existent = str(tmp_path / "does_not_exist")
        params = _make_params(output_directory=non_existent)
        worker = ProjectWorker(params)
        # Should not raise
        worker._cleanup_on_failure()

    def test_does_nothing_when_output_directory_is_empty_string(self, app):
        params = _make_params(output_directory="")
        worker = ProjectWorker(params)
        # Should not raise
        worker._cleanup_on_failure()


# ---------------------------------------------------------------------------
# run() - cleanup on failure
# ---------------------------------------------------------------------------


class TestRunCleansUpOnFailure:
    def test_cleanup_called_on_exception(self, app, tmp_path):
        output = str(tmp_path / "project")
        params = _make_params(output_directory=output)
        worker = ProjectWorker(params)

        with patch.object(
            worker, "clone_template_repo", side_effect=RuntimeError("boom")
        ), patch.object(worker, "_cleanup_on_failure") as mock_cleanup:
            worker.run()
            mock_cleanup.assert_called_once()

    def test_error_signal_emitted_on_exception(self, app, tmp_path):
        output = str(tmp_path / "project")
        params = _make_params(output_directory=output)
        worker = ProjectWorker(params)

        errors: list[str] = []
        worker.error.connect(errors.append)

        with patch.object(
            worker, "clone_template_repo", side_effect=RuntimeError("kaboom")
        ), patch.object(worker, "_cleanup_on_failure"):
            worker.run()

        assert len(errors) == 1
        assert "kaboom" in errors[0]

    def test_finished_signal_emitted_even_on_exception(self, app, tmp_path):
        output = str(tmp_path / "project")
        params = _make_params(output_directory=output)
        worker = ProjectWorker(params)

        finished: list[bool] = []
        worker.finished.connect(lambda: finished.append(True))

        with patch.object(
            worker, "clone_template_repo", side_effect=RuntimeError("fail")
        ), patch.object(worker, "_cleanup_on_failure"):
            worker.run()

        assert finished


# ---------------------------------------------------------------------------
# init_git_repo - author env vars
# ---------------------------------------------------------------------------


class TestInitGitRepoEnv:
    def test_git_commit_uses_env_with_author_info(self, app, tmp_path):
        output = str(tmp_path / "project")
        os.makedirs(output)
        params = _make_params(output_directory=output, options={"create_git_repo": True})
        worker = ProjectWorker(params)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            worker.init_git_repo()

        # The commit call is the third subprocess.run call (init, add, commit)
        commit_call = mock_run.call_args_list[2]
        env_arg = commit_call[1].get("env") or commit_call.kwargs.get("env")
        assert env_arg is not None
        assert "GIT_AUTHOR_NAME" in env_arg
        assert "GIT_COMMITTER_NAME" in env_arg

    def test_init_git_repo_skipped_when_option_false(self, app, tmp_path):
        output = str(tmp_path / "project")
        os.makedirs(output)
        params = _make_params(output_directory=output, options={"create_git_repo": False})
        worker = ProjectWorker(params)

        with patch("subprocess.run") as mock_run:
            worker.init_git_repo()
            mock_run.assert_not_called()


# ---------------------------------------------------------------------------
# DEFAULT_TEMPLATE_URL constant
# ---------------------------------------------------------------------------


class TestDefaultTemplateUrl:
    def test_constant_is_a_valid_url(self):
        assert DEFAULT_TEMPLATE_URL.startswith("https://")

    def test_constant_ends_with_git(self):
        assert DEFAULT_TEMPLATE_URL.endswith(".git")
