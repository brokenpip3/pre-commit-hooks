# My pre-commit hooks

This repository contains my pre-commit hooks, feel free to contribute.

## Hooks

### `github-actions-hash`

This simple hook will automatically replace each github action dependency with the hash of the specific tag and a human readable tag that dependabot will keep/update in the future.

```diff
       - name: Create Pull Request
-        uses: peter-evans/create-pull-request@v7
+        uses: peter-evans/create-pull-request@271a8d0340265f705b14b6d32b9829c1cb33d45e # v7
```

This will prevent the action from changing and breaking your workflow, or even worse, introduce a security vulnerability/malicious code by repushing a tag.
It's just a quick solution that will leverage `ls-remote` git functionality and only support tags, not branches.

I wrote it after the `tj-actions` [incident](https://www.stepsecurity.io/blog/harden-runner-detection-tj-actions-changed-files-action-is-compromised) to
quickly fix all my workflows in all my repositories and can be used both as [standalone](./hooks/github_actions_hash.py) (to quickly fix all the workflow in a repo) or as a pre-commit hook (to be sure that all the new workflows will be fixed).

#### Usage

```yaml
- repo: https://github.com/brokenpip3/pre-commit-hooks
  rev: dd7b3821637ba3c3a8628ad487fd84edec8006f2  # frozen: 0.0.1
  hooks:
    - id: github-actions-hash
      files: ^.github/workflows/.*\.(yml|yaml)$ # limit only to github workflows
```

#### Example output

```bash
github action hash replacer..............................................Failed
- hook id: github-actions-hash
- duration: 24.66s
- exit code: 1
- files were modified by this hook

-> updated:       .github/workflows/pr.yaml
-> not needed in: .github/workflows/auto-check-updates.yaml
-> updated:       .github/workflows/build-image.yaml
-> updated:       .github/workflows/auto-push-updates.yaml
-> updated:       .github/workflows/update-pre-commit-hooks.yaml
```
