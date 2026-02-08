# Testing Guide

## Quick Start

Run tests using hatch (recommended):

```bash
# Run all tests
hatch run test

# Run with coverage report
hatch run test-cov
```

Or using pytest directly:

```bash
# Install in development mode first
pip install -e ".[dev]"

# Run tests
pytest
pytest -v                              # Verbose output
pytest -k test_validator               # Run specific tests
pytest tests/test_ipxe_validator.py    # Run specific file
```

## Test Structure

```
tests/
├── conftest.py                  # Shared fixtures and configuration
├── test_models.py               # Core data models (BootEntry, DistributionMenu)
├── test_generator.py            # Menu generator
├── test_core_url_validator.py   # URL validator
├── test_ipxe_validator.py       # iPXE script validator
├── test_cli.py                  # Main CLI tool
└── test_ipxelint.py             # iPXE linting CLI tool
```

## Running Tests

### Recommended: Using Hatch

```bash
hatch run test              # All tests, minimal output
hatch run test -v           # Verbose output
hatch run test-cov          # With coverage report
```

### Alternative: Direct pytest

```bash
pytest                                          # All tests
pytest -v                                       # Verbose
pytest --cov=src --cov-report=html              # Coverage report
pytest tests/test_ipxe_validator.py             # Specific file
pytest -k "validator and not url"               # Filter by name
```

### Using Make

```bash
make test              # Run all tests
make test-coverage     # With coverage
```

## Viewing Coverage

Generate and view test coverage reports:

```bash
# Generate coverage report
hatch run test-cov              # Terminal + HTML report

# View HTML report
open htmlcov/index.html         # macOS
xdg-open htmlcov/index.html     # Linux

# Terminal-only report with missing lines
pytest --cov=src --cov-report=term-missing
```

## Code Quality

### Linting and Formatting

```bash
# Check code quality (linting + formatting)
hatch run lint:check

# Auto-fix issues
hatch run lint:format

# Individual tools
ruff check src tests                # Linting
ruff format --check src tests       # Format check
```

### Pre-commit Hooks

Install and run pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## Writing Tests

### Basic Test Example

```python
import pytest
from elfshoe.core import BootEntry

def test_boot_entry_creation():
    """Test creating a boot entry."""
    entry = BootEntry(
        id='test',
        label='Test Entry',
        kernel_url='http://example.com/vmlinuz',
        initrd_url='http://example.com/initrd.img',
        boot_params='console=tty0'
    )
    assert entry.id == 'test'
    assert entry.label == 'Test Entry'
```

### Using Fixtures

Fixtures are defined in `tests/conftest.py`:

```python
def test_with_config(sample_config):
    """Test uses sample_config fixture from conftest.py."""
    assert 'menu' in sample_config
    assert sample_config['menu']['title'] == 'Test Menu'
```

### Mocking External Calls

Always mock HTTP requests and file I/O:

```python
from unittest.mock import patch, MagicMock

@patch('urllib.request.urlopen')
def test_url_validation(mock_urlopen):
    """Test URL checking with mocked requests."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.geturl.return_value = "http://example.com"
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=False)
    mock_urlopen.return_value = mock_response

    result = URLValidator.check_url('http://example.com', verbose=False)
    assert result is True
```

### Testing CLI Tools

```python
from unittest.mock import patch
import pytest

def test_cli_with_args(capsys):
    """Test CLI with command line arguments."""
    with patch('sys.argv', ['cli', '--help']):
        with pytest.raises(SystemExit) as exc_info:
            main()

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert 'usage:' in captured.out
```

## Best Practices

1. **Use descriptive test names** - `test_url_validation_fails_on_404` not `test_url1`
2. **One concept per test** - Keep tests focused on a single behavior
3. **Use fixtures** - Share setup code via `conftest.py`
4. **Mock external dependencies** - No real network calls or file system changes
5. **Test edge cases** - Empty inputs, invalid data, boundary conditions
6. **Keep tests fast** - Use mocking to avoid slow operations
7. **Clean up resources** - Use `tempfile` or fixtures for file operations

## Pytest Configuration

Configuration in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]
pythonpath = ["src"]
```

The `pythonpath = ["src"]` setting means pytest can import the package without installation.

## CI/CD Integration

Tests run automatically in GitHub Actions:

```yaml
- name: Run tests
  run: hatch run test

- name: Run linting
  run: hatch run lint:check
```

View the full CI configuration in `.github/workflows/ci.yml`.

## Troubleshooting

### Import Errors

If you get import errors when running pytest:

```bash
# Option 1: Use hatch (isolated environment)
hatch run test

# Option 2: Install in editable mode
pip install -e .

# Option 3: Check pythonpath in pyproject.toml
grep pythonpath pyproject.toml
```

### Mock Not Working

Ensure you patch where the function is used, not where it's defined:

```python
# ✓ Correct - patch where it's imported
@patch('elfshoe.core.validator.urlopen')

# ✗ Wrong - may not work
@patch('urllib.request.urlopen')
```

### Hatch Environment Issues

Reset the hatch environment:

```bash
hatch env remove default
hatch env create
hatch run test
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Hatch Documentation](https://hatch.pypa.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
