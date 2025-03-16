import glob
import os
import re
import subprocess
import sys

# needs git and only works with tags, not branches

def get_tag_hash(action_name, tag):
    try:
        action_repo_url = f"git@github.com:{action_name}.git"
        hash_cmd = ["git", "ls-remote", action_repo_url, f"refs/tags/{tag}"]
        result = subprocess.run(
            hash_cmd, capture_output=True, text=True, check=True, timeout=5
        )
        if result.stdout:
            return result.stdout.strip().split("\t")[0]
        return None
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def replace_action_versions(workflow_file, repo_path):
    with open(workflow_file, "r") as f:
        lines = f.readlines()

    # I tried to do it without an llm but a wormhole opened and I saw the end of the universe
    pattern = r"(\s*(?:-\s*)?uses:\s*)([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)@([^\s#]+)"
    modified = False
    new_lines = []

    for line in lines:
        match = re.match(pattern, line)
        if match:
            prefix, action, version = match.groups()
            tag_hash = get_tag_hash(action, version)

            if tag_hash:
                new_line = f"{prefix}{action}@{tag_hash} # {version}\n"
                modified = True
            else:
                new_line = line
        else:
            new_line = line

        new_lines.append(new_line)

    if modified:
        with open(workflow_file, "w") as f:
            f.writelines(new_lines)
        rel_path = os.path.relpath(workflow_file, repo_path)
        print(f"-> updated:       {rel_path}")
        return True
    else:
        rel_path = os.path.relpath(workflow_file, repo_path)
        print(f"-> not needed in: {rel_path}")
        return False


def process_files(files=None):
    try:
        current_dir = os.getcwd()
    except FileNotFoundError:
        return 1

    if not os.path.isdir(os.path.join(current_dir, ".git")):
        print("not a git repo")
        return 1

    # pre-commit
    if files:
        updated = False
        for workflow_file in files:
            if os.path.exists(workflow_file) and (
                workflow_file.endswith(".yml") or workflow_file.endswith(".yaml")
            ):
                if replace_action_versions(workflow_file, current_dir):
                    updated = True
        return 1 if updated else 0
    else:
        workflow_dir = os.path.join(current_dir, ".github", "workflows")
        if not os.path.isdir(workflow_dir):
            print("no workflows dir")
            return 0

        workflow_files = glob.glob(os.path.join(workflow_dir, "*.yml")) + glob.glob(
            os.path.join(workflow_dir, "*.yaml")
        )
        if not workflow_files:
            print("no workflow files")
            return 0

        print(f"-> found workflow files: {len(workflow_files)}")
        updated = False
        for workflow_file in workflow_files:
            if replace_action_versions(workflow_file, current_dir):
                updated = True

        print("\n-> done")
        return 0


def main():
    if len(sys.argv) > 1:
        return process_files(sys.argv[1:])
    else:
        return process_files()

if __name__ == "__main__":
    sys.exit(main())
