import os
import subprocess
import sys
import tempfile
from unittest.mock import patch

import pytest

from hooks.github_actions_hash import get_tag_hash
from hooks.github_actions_hash import main
from hooks.github_actions_hash import process_files
from hooks.github_actions_hash import replace_action_versions


@pytest.fixture
def real_repo():
    with tempfile.TemporaryDirectory() as repo:
        os.makedirs(os.path.join(repo, ".git"))
        os.makedirs(os.path.join(repo, ".github", "workflows"))
        yield repo


@pytest.fixture
def real_workflow(real_repo):
    workflow_file = os.path.join(real_repo, ".github", "workflows", "ci.yml")
    with open(workflow_file, "w") as f:
        f.write("""
        name: CI
        on: [push, pull_request]
        jobs:
          build:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v4
              - uses: actions/setup-python@v4
              - uses: docker/build-push-action@v3
        """)
    return workflow_file


@patch("subprocess.run")
def test_get_tag_hash(mock_run):
    mock_run.return_value.stdout = "abcd5678\ttags/v4\n"
    tag_hash = get_tag_hash("actions/setup-python", "v4")
    assert tag_hash == "abcd5678"


@patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "git"))
def test_get_tag_hash_fail(mock_run):
    assert get_tag_hash("docker/build-push-action", "v3") is None


@patch("hooks.github_actions_hash.get_tag_hash", return_value="abcd5678")
def test_replace_action_versions(mock_get_hash, real_workflow, real_repo):
    assert replace_action_versions(real_workflow, real_repo) is True
    with open(real_workflow) as f:
        content = f.read()
    assert "actions/setup-python@abcd5678 # v4" in content


@patch("hooks.github_actions_hash.get_tag_hash", return_value=None)
def test_replace_action_versions_no_update(mock_get_hash, real_workflow, real_repo):
    assert replace_action_versions(real_workflow, real_repo) is False
    with open(real_workflow) as f:
        content = f.read()
    assert "docker/build-push-action@v3" in content


@patch("glob.glob", return_value=[])
def test_process_files_no_workflows(mock_glob):
    assert process_files() == 0


@patch("glob.glob", return_value=[".github/workflows/ci.yml"])
@patch("hooks.github_actions_hash.replace_action_versions", return_value=True)
def test_process_files_with_updates(mock_replace, mock_glob):
    assert process_files() == 0


@patch("hooks.github_actions_hash.replace_action_versions", return_value=False)
def test_process_files_no_updates(mock_glob, real_repo):
    os.chdir(real_repo)
    assert process_files() == 0


@patch("hooks.github_actions_hash.process_files")
def test_pre_commit_run(mock_process):
    mock_process.return_value = 1
    sys.argv = ["hooks.github_actions_hash.py", "./.github/workflows/ci.yml"]
    assert main() == 1
