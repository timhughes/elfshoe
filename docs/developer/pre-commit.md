# Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to ensure code quality and consistency.

## What Gets Checked

### On Every Commit (pre-commit)
- **Trailing whitespace removal**
- **End-of-file fixing** (ensures newline at EOF)
- **YAML validation** (excludes mkdocs.yml)
- **Large file detection**
- **Merge conflict markers**
- **TOML validation**
- **Line ending consistency**
- **Black code formatting** (Python)
- **Ruff linting** (Python)
- **Documentation linting** (when docs/ files change)

### Before Every Push (pre-push)
- **Full test suite** runs all pytest tests
- **Package build** verifies the package builds successfully

## Setup

Install pre-commit hooks:

```bash
make pre-commit-install
```

Or manually:

```bash
pip install pre-commit
pre-commit install
pre-commit install --hook-type pre-push
```

## Usage

### Automatic
Once installed, hooks run automatically:
- On `git commit` - runs formatting and linting
- On `git push` - runs tests and build

### Manual
Run hooks on all files:
```bash
make pre-commit-run
```

Or manually:
```bash
pre-commit run --all-files
```

Run only pre-push hooks:
```bash
pre-commit run --hook-stage pre-push --all-files
```

### Update Hooks
Update to latest hook versions:
```bash
make pre-commit-update
```

## Bypassing Hooks (Not Recommended)

In emergencies only:
```bash
git commit --no-verify
git push --no-verify
```

**Note:** CI will still run all checks, so bypassing locally just delays failure detection.
