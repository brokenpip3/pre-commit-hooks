# My pre-commit hooks

This repository contains my pre-commit hooks, feel free to contribute.

## Hooks

### `github-actions-hash`

This hook will automatically replace each github action dependency with the hash of the specific tag.

This will prevent the action from changing and breaking your workflow, or even worse, introduce a security vulnerability/malicious code.

I wrote it after the `tj-actions` [incident](https://www.stepsecurity.io/blog/harden-runner-detection-tj-actions-changed-files-action-is-compromised) to
quickly fix all my workflows in all my repositories and can be used both as standalone or as a pre-commit hook.

#### Usage

```yaml
- repo: https://github.com/brokenpip3/pre-commit-hooks
  rev: v0.1.0
  hooks:
    - id: github-actions-hash
      files: ^github/workflows/.*\.(yml|yaml)$
```
