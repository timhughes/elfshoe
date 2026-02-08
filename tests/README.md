# Test Organization

All test files follow pytest naming conventions and clearly map to their source modules.

## Test Files

| Test File | Tests Module | Description |
|-----------|--------------|-------------|
| `test_cli.py` | `cli.py` | Main CLI with validation integration |
| `test_ipxelint.py` | `ipxelint.py` | iPXE script linting CLI tool |
| `test_ipxe_validator.py` | `validator.py` | iPXE script validator (IPXEValidator class and helpers) |
| `test_core_url_validator.py` | `core/validator.py` | URL validator (URLValidator class) |
| `test_generator.py` | `core/generator.py` | Menu generator (MenuGenerator class) |
| `test_models.py` | `core/models.py` | Data models (BootEntry, DistributionMenu) |

## Coverage Summary

| Module | Coverage | Test Count |
|--------|----------|------------|
| `validator.py` | 98% | 22 tests |
| `ipxelint.py` | 100% | 6 tests |
| `cli.py` | 75% | 4 tests |
| `core/validator.py` | 93% | 5 tests |
| `core/generator.py` | 100% | 5 tests |
| `core/models.py` | 100% | 2 tests |

**Total: 44 tests, all passing ✅**

## Running Tests

Use hatch to run tests in the proper environment:

```bash
# Run all tests
hatch run test

# Run all tests with verbose output
hatch run test -v

# Run specific test file
hatch run test tests/test_ipxe_validator.py

# Run with coverage report
hatch run test-cov

# Run tests matching a pattern
hatch run test -k "validator"
```

## Test Organization Philosophy

- **One test file per source module** - Easy to find tests for any module
- **Clear naming** - Test file names match the module they test
- **Comprehensive coverage** - Critical paths and edge cases covered
- **Fast execution** - All tests run in < 1 second
