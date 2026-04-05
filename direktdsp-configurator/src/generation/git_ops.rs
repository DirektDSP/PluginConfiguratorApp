use std::path::Path;
use std::process::{Command, Stdio};

use color_eyre::{Result, eyre::eyre};

/// Run a git command with stdout/stderr suppressed (piped to null)
/// so it doesn't corrupt the TUI.
fn git_command() -> Command {
    let mut cmd = Command::new("git");
    cmd.stdout(Stdio::null()).stderr(Stdio::null());
    cmd
}

/// Clone a git repository with depth 1.
pub fn clone_template(url: &str, branch: &str, output_dir: &Path) -> Result<()> {
    let status = git_command()
        .args([
            "clone",
            "--depth",
            "1",
            "--branch",
            branch,
            url,
            &output_dir.to_string_lossy(),
        ])
        .status()
        .map_err(|e| eyre!("Failed to run git clone: {e}"))?;

    if !status.success() {
        return Err(eyre!(
            "git clone failed with exit code {}",
            status.code().unwrap_or(-1)
        ));
    }
    Ok(())
}

/// Selectively initialize submodules for the given paths.
/// `submodule_paths` should be relative to the repo root (e.g. "JUCE", "modules/clap-juce-extensions").
pub fn init_submodules(repo_dir: &Path, submodule_paths: &[&str]) -> Result<()> {
    if submodule_paths.is_empty() {
        return Ok(());
    }

    let mut args = vec!["submodule", "update", "--init", "--recursive", "--depth", "1", "--"];
    args.extend(submodule_paths);

    let status = git_command()
        .current_dir(repo_dir)
        .args(&args)
        .status()
        .map_err(|e| eyre!("Failed to run git submodule update: {e}"))?;

    if !status.success() {
        return Err(eyre!(
            "git submodule update failed with exit code {}",
            status.code().unwrap_or(-1)
        ));
    }
    Ok(())
}

/// Remove the template's .git directory and initialize a fresh repository.
pub fn reinit_git(repo_dir: &Path) -> Result<()> {
    let git_dir = repo_dir.join(".git");
    if git_dir.exists() {
        std::fs::remove_dir_all(&git_dir)
            .map_err(|e| eyre!("Failed to remove .git directory: {e}"))?;
    }

    let status = git_command()
        .current_dir(repo_dir)
        .args(["init"])
        .status()
        .map_err(|e| eyre!("Failed to run git init: {e}"))?;

    if !status.success() {
        return Err(eyre!("git init failed"));
    }

    let status = git_command()
        .current_dir(repo_dir)
        .args(["add", "-A"])
        .status()
        .map_err(|e| eyre!("Failed to run git add: {e}"))?;

    if !status.success() {
        return Err(eyre!("git add failed"));
    }

    let status = git_command()
        .current_dir(repo_dir)
        .args(["commit", "-m", "Initial commit from DirektDSP Configurator"])
        .status()
        .map_err(|e| eyre!("Failed to run git commit: {e}"))?;

    if !status.success() {
        return Err(eyre!("git commit failed"));
    }

    Ok(())
}
