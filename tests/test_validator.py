"""Tests for iPXE script validator."""

import tempfile
from pathlib import Path

from elfshoe.validator import IPXEValidator


def test_valid_script():
    """Test validation of a minimal valid script."""
    validator = IPXEValidator()
    script = """#!ipxe
echo Hello World
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ipxe', delete=False) as f:
        f.write(script)
        f.flush()
        is_valid, errors, warnings = validator.validate_file(f.name)
    Path(f.name).unlink()
    assert is_valid
    assert len(errors) == 0


def test_missing_shebang():
    """Test validation fails without shebang."""
    validator = IPXEValidator()
    script = "echo Hello World"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ipxe', delete=False) as f:
        f.write(script)
        f.flush()
        is_valid, errors, warnings = validator.validate_file(f.name)
    Path(f.name).unlink()
    assert not is_valid
    assert any("shebang" in str(e).lower() for e in errors)


def test_undefined_label():
    """Test detection of undefined label references."""
    validator = IPXEValidator()
    script = """#!ipxe
goto undefined_label
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ipxe', delete=False) as f:
        f.write(script)
        f.flush()
        is_valid, errors, warnings = validator.validate_file(f.name)
    Path(f.name).unlink()
    assert not is_valid
    assert any("undefined" in str(e).lower() for e in errors)


def test_variable_goto_allowed():
    """Test that goto with variables doesn't trigger false positives."""
    validator = IPXEValidator()
    script = """#!ipxe
choose target && goto ${target}
:option1
echo Option 1
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ipxe', delete=False) as f:
        f.write(script)
        f.flush()
        is_valid, errors, warnings = validator.validate_file(f.name)
    Path(f.name).unlink()
    assert is_valid
    assert len(errors) == 0


def test_menu_imbalance_warning():
    """Test warning for unbalanced menu/choose statements."""
    validator = IPXEValidator()
    script = """#!ipxe
menu My Menu
item option1 Option 1
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ipxe', delete=False) as f:
        f.write(script)
        f.flush()
        is_valid, errors, warnings = validator.validate_file(f.name)
    Path(f.name).unlink()
    assert is_valid  # Still valid, just a warning
    assert len(warnings) > 0
    assert any("unbalanced" in str(w).lower() for w in warnings)
