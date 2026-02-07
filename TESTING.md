# Testing Guide

## Running Tests

### Install Test Dependencies

```bash
pip install -e ".[dev]"
```

Or manually:
```bash
pip install pytest pytest-cov pytest-mock
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_ipxe_menu_gen.py -v

# Run specific test class
pytest tests/test_menu_generator.py::TestMenuGenerator -v

# Run specific test function
pytest tests/test_menu_generator.py::TestMenuGenerator::test_generate_minimal_menu -v
```

### Using Make

```bash
# Run tests
make test

# Run tests with coverage
make test-coverage

# Run linting
make lint
```

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── test_ipxe_menu_gen.py      # Core dataclass tests
├── test_url_validator.py      # URL validation tests
└── test_menu_generator.py     # Menu generation tests
```

## Writing Tests

### Example Test

```python
import pytest
from ipxe_menu_gen import BootEntry

def test_boot_entry_creation():
    """Test creating a boot entry."""
    entry = BootEntry(
        id='test',
        label='Test',
        kernel_url='http://example.com/vmlinuz',
        initrd_url='http://example.com/initrd.img',
        boot_params='param=value'
    )
    assert entry.id == 'test'
    assert entry.label == 'Test'
```

### Using Fixtures

```python
def test_with_config(sample_config):
    """Test uses sample_config fixture from conftest.py."""
    assert 'menu' in sample_config
    assert sample_config['menu']['title'] == 'Test Menu'
```

### Mocking URL Requests

```python
from unittest.mock import patch, MagicMock

@patch('urllib.request.urlopen')
def test_url_check(mock_urlopen):
    """Test URL checking with mocked requests."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_urlopen.return_value = mock_response
    
    # Your test code here
```

## Test Coverage

Current test coverage:
- BootEntry: 100%
- DistributionMenu: 100%
- URLValidator: 100%
- MenuGenerator: 80%
- Overall: ~25% (initial implementation)

Target coverage: 80%+

## Continuous Integration

Tests can be run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pip install -e ".[dev]"
    pytest --cov=src --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Test Categories

### Unit Tests
- Test individual functions and classes
- Mock external dependencies
- Fast execution (< 1 second per test)

### Integration Tests
- Test complete workflows
- May involve file I/O
- Medium execution time (< 5 seconds per test)

### Functional Tests
- End-to-end scenarios
- Test CLI interface
- Slower execution (< 10 seconds per test)

## Common Test Patterns

### Testing Configuration Loading

```python
def test_load_config(temp_dir, sample_config):
    import yaml
    
    config_file = temp_dir / 'config.yaml'
    with open(config_file, 'w') as f:
        yaml.dump(sample_config, f)
    
    loaded = load_config(config_file)
    assert loaded == sample_config
```

### Testing Menu Generation

```python
def test_menu_output(sample_config):
    generator = MenuGenerator(sample_config)
    output = generator.generate([])
    
    assert '#!ipxe' in output
    assert 'dhcp' in output
```

### Testing URL Validation

```python
@patch('urllib.request.urlopen')
def test_url_validation(mock_urlopen):
    mock_response = MagicMock()
    mock_response.status = 200
    mock_urlopen.return_value = mock_response
    
    result = URLValidator.check_url('http://example.com')
    assert result is True
```

## Troubleshooting

### Import Errors

If you get import errors:
```bash
# Make sure src is in Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
```

### Fixture Not Found

Check that `conftest.py` is in the tests directory and contains the fixture.

### Mock Not Working

Ensure you're patching the correct import path:
```python
# Patch where it's used, not where it's defined
@patch('ipxe_menu_gen.urllib.request.urlopen')  # ✓ Correct
@patch('urllib.request.urlopen')                # ✗ May not work
```

## Best Practices

1. **One assertion concept per test** - Keep tests focused
2. **Use descriptive names** - `test_url_validation_fails_on_404` not `test_url1`
3. **Use fixtures** - Share setup code via conftest.py
4. **Mock external calls** - Don't make real network requests
5. **Test edge cases** - Empty inputs, invalid data, etc.
6. **Keep tests fast** - Use mocking to avoid slow operations
7. **Clean up** - Use temp_dir fixture for file operations
