# Contributing to elfshoe

Thank you for your interest in contributing to elfshoe! This document provides guidelines and instructions for contributing.

## 🎯 How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/timhughes/elfshoe/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Detailed description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Python version, package versions)
   - Relevant logs or error messages

### Suggesting Enhancements

1. Check existing [Issues](https://github.com/timhughes/elfshoe/issues) and [Pull Requests](https://github.com/timhughes/elfshoe/pulls)
2. Create a new issue describing:
   - The enhancement you'd like to see
   - Why it would be useful
   - Possible implementation approaches

### Pull Requests

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/my-new-feature
   ```
4. **Make your changes** following our guidelines below
5. **Test your changes** thoroughly
6. **Commit** with clear, descriptive messages
7. **Push** to your fork
8. **Submit a pull request** to the main repository

## 🛠️ Development Setup

### Prerequisites

- Python 3.7 or higher
- Git
- Make (optional, but recommended)

### Initial Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/elfshoe.git
cd elfshoe

# Install Hatch
pip install hatch

# Create development environment
hatch env create

# Or use editable install
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test file
pytest tests/test_elfshoe.py

# Using hatch
hatch run test
hatch run test-cov
```

### Code Quality

```bash
# Check code style
make lint

# Auto-format code
make format

# Or with hatch
hatch run lint:check
hatch run lint:format
```

## 📝 Code Guidelines

### Style Guide

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use [Black](https://black.readthedocs.io/) for formatting (line length: 88)
- Use [Ruff](https://docs.astral.sh/ruff/) for linting
- Write clear, descriptive variable and function names
- Add docstrings for public functions and classes

### Code Structure

- Keep functions focused and single-purpose
- Use type hints where appropriate
- Avoid deep nesting (max 3-4 levels)
- Extract complex logic into separate functions
- Use dataclasses for data structures

### Testing

- Write tests for all new features
- Maintain or improve test coverage
- Test both success and failure cases
- Use descriptive test names that explain what is being tested
- Group related tests in test classes

### Documentation

- Update relevant documentation for your changes
- Add docstrings for new functions/classes
- Update README.md if adding user-facing features
- Include code examples for new features

## 🔌 Adding New Distributions

See [adding_distributions.md](adding_distributions.md) for detailed instructions on adding support for new operating systems.

### Quick Checklist

1. Create a metadata fetcher class in `src/elfshoe/distributions/`
2. Inherit from `AbstractMetadataFetcher`
3. Implement `fetch_versions()` method
4. Register in `src/elfshoe/distributions/__init__.py`
5. Add tests in `tests/`
6. Update documentation
7. Add example configuration to README

## 🧪 Testing Checklist

Before submitting a pull request, ensure:

- [ ] All tests pass (`make test`)
- [ ] Code is formatted (`make format`)
- [ ] Linting passes (`make lint`)
- [ ] Coverage hasn't decreased (`make test-coverage`)
- [ ] Documentation is updated
- [ ] New features have tests
- [ ] Examples work as documented

## 📋 Commit Messages

Write clear, descriptive commit messages:

```
feat: Add support for Ubuntu metadata fetcher

- Implement UbuntuMetadataFetcher class
- Add tests for Ubuntu version detection
- Update documentation with Ubuntu example
```

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `style`: Code style changes (formatting)
- `chore`: Maintenance tasks

## 🚀 Release Process

Releases are handled by maintainers:

1. Update version in `pyproject.toml`
3. Create and tag release
4. Build and publish to PyPI:
   ```bash
   hatch build
   hatch publish
   ```

## 💡 Need Help?

- Check the [documentation](https://timhughes.github.io/elfshoe/)
- Look at existing code for examples
- Review closed pull requests for similar changes
- Open an issue for questions
- Reach out to maintainers

## 📜 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions
- Help others learn and grow

## 🎉 Recognition

Contributors are recognized in:
- GitHub contributors list
- Project README (for major features)

Thank you for contributing to elfshoe! 🙏
