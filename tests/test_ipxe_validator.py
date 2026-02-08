"""Tests for IPXEValidator class and validation helpers (validator.py)."""

import tempfile
from pathlib import Path

from elfshoe.validator import IPXEValidator, validate_and_report, validate_multiple_files


def test_valid_script():
    """Test validation of a minimal valid script."""
    validator = IPXEValidator()
    script = """#!ipxe
echo Hello World
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
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
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
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
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
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
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
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
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
        f.write(script)
        f.flush()
        is_valid, errors, warnings = validator.validate_file(f.name)
    Path(f.name).unlink()
    assert is_valid  # Still valid, just a warning
    assert len(warnings) > 0
    assert any("unbalanced" in str(w).lower() for w in warnings)


def test_validate_and_report_success(capsys):
    """Test validate_and_report with a valid script."""
    script = """#!ipxe
echo Hello World
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
        f.write(script)
        f.flush()
        result = validate_and_report(Path(f.name))
        captured = capsys.readouterr()
    Path(f.name).unlink()

    assert result is True
    assert "OK" in captured.out


def test_validate_and_report_with_errors(capsys):
    """Test validate_and_report with an invalid script."""
    script = """#!ipxe
goto nonexistent_label
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
        f.write(script)
        f.flush()
        result = validate_and_report(Path(f.name))
        captured = capsys.readouterr()
    Path(f.name).unlink()

    assert result is False
    assert "FAILED" in captured.out
    assert "undefined" in captured.out.lower()


def test_validate_and_report_with_warnings_quiet(capsys):
    """Test validate_and_report with warnings in quiet mode."""
    script = """#!ipxe
menu My Menu
item option1 Option 1
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
        f.write(script)
        f.flush()
        result = validate_and_report(Path(f.name), quiet=True)
        captured = capsys.readouterr()
    Path(f.name).unlink()

    assert result is True
    assert captured.out == ""  # No output in quiet mode


def test_validate_and_report_with_warnings_strict(capsys):
    """Test validate_and_report with warnings in strict mode."""
    script = """#!ipxe
menu My Menu
item option1 Option 1
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
        f.write(script)
        f.flush()
        result = validate_and_report(Path(f.name), strict=True)
        captured = capsys.readouterr()
    Path(f.name).unlink()

    assert result is False  # Strict mode treats warnings as failures
    assert "WARNINGS" in captured.out


def test_validate_and_report_file_not_found(capsys):
    """Test validate_and_report with non-existent file."""
    result = validate_and_report(Path("/nonexistent/file.ipxe"))
    captured = capsys.readouterr()

    assert result is False
    assert "not found" in captured.err.lower()


def test_validate_multiple_files_all_valid(capsys):
    """Test validate_multiple_files with all valid scripts."""
    scripts = [
        """#!ipxe
echo Script 1
""",
        """#!ipxe
echo Script 2
""",
    ]

    files = []
    for i, script in enumerate(scripts):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
            f.write(script)
            f.flush()
            files.append(Path(f.name))

    result = validate_multiple_files(files)
    captured = capsys.readouterr()

    for f in files:
        f.unlink()

    assert result is True
    assert "OK" in captured.out
    assert "Validated 2 file(s)" in captured.out


def test_validate_multiple_files_with_errors(capsys):
    """Test validate_multiple_files with some invalid scripts."""
    scripts = [
        """#!ipxe
echo Valid script
""",
        """#!ipxe
goto undefined_label
""",
    ]

    files = []
    for i, script in enumerate(scripts):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
            f.write(script)
            f.flush()
            files.append(Path(f.name))

    result = validate_multiple_files(files)
    captured = capsys.readouterr()

    for f in files:
        f.unlink()

    assert result is False
    assert "FAILED" in captured.out
    assert "Errors: 1" in captured.out


def test_validate_multiple_files_quiet(capsys):
    """Test validate_multiple_files in quiet mode."""
    script = """#!ipxe
echo Valid script
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
        f.write(script)
        f.flush()
        result = validate_multiple_files([Path(f.name)], quiet=True)
        captured = capsys.readouterr()
    Path(f.name).unlink()

    assert result is True
    assert captured.out == ""  # No output in quiet mode


def test_validate_multiple_files_strict_with_warnings(capsys):
    """Test validate_multiple_files with warnings in strict mode."""
    scripts = [
        """#!ipxe
menu My Menu
item option1 Option 1
""",
        """#!ipxe
echo Valid script
""",
    ]

    files = []
    for i, script in enumerate(scripts):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
            f.write(script)
            f.flush()
            files.append(Path(f.name))

    result = validate_multiple_files(files, strict=True)
    captured = capsys.readouterr()

    for f in files:
        f.unlink()

    assert result is False
    assert "Warnings: 1" in captured.out


def test_validate_multiple_files_nonexistent(capsys):
    """Test validate_multiple_files with non-existent file."""
    result = validate_multiple_files([Path("/nonexistent/file.ipxe")])
    captured = capsys.readouterr()

    assert result is False
    assert "not found" in captured.err.lower()


def test_empty_file():
    """Test validation of empty file."""
    validator = IPXEValidator()
    script = ""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
        f.write(script)
        f.flush()
        is_valid, errors, warnings = validator.validate_file(f.name)
    Path(f.name).unlink()
    assert not is_valid
    assert any("empty" in str(e).lower() for e in errors)


def test_unknown_command_warning():
    """Test warning for unknown commands."""
    validator = IPXEValidator()
    script = """#!ipxe
unknowncommand arg1 arg2
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
        f.write(script)
        f.flush()
        is_valid, errors, warnings = validator.validate_file(f.name)
    Path(f.name).unlink()
    assert is_valid  # Unknown command is a warning, not error
    assert len(warnings) > 0
    assert any("unknown" in str(w).lower() for w in warnings)


def test_known_commands_no_warning():
    """Test that known commands don't trigger warnings."""
    validator = IPXEValidator()
    script = """#!ipxe
set var value
echo ${var}
dhcp
chain http://example.com/kernel
boot
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
        f.write(script)
        f.flush()
        is_valid, errors, warnings = validator.validate_file(f.name)
    Path(f.name).unlink()
    assert is_valid
    assert len(errors) == 0
    assert len(warnings) == 0


def test_labels_with_goto():
    """Test that defined labels don't trigger errors."""
    validator = IPXEValidator()
    script = """#!ipxe
:start
echo Starting
goto end
:end
echo Done
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
        f.write(script)
        f.flush()
        is_valid, errors, warnings = validator.validate_file(f.name)
    Path(f.name).unlink()
    assert is_valid
    assert len(errors) == 0


def test_comments_and_blank_lines():
    """Test that comments and blank lines are ignored."""
    validator = IPXEValidator()
    script = """#!ipxe
# This is a comment
echo Hello

# Another comment
echo World
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
        f.write(script)
        f.flush()
        is_valid, errors, warnings = validator.validate_file(f.name)
    Path(f.name).unlink()
    assert is_valid
    assert len(errors) == 0


def test_conditional_goto_with_variable():
    """Test conditional goto with variable doesn't cause false positive."""
    validator = IPXEValidator()
    script = """#!ipxe
isset menu && goto ${menu}
:default
echo Default
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
        f.write(script)
        f.flush()
        is_valid, errors, warnings = validator.validate_file(f.name)
    Path(f.name).unlink()
    assert is_valid
    assert len(errors) == 0


def test_goto_without_target():
    """Test goto without a target (edge case)."""
    validator = IPXEValidator()
    script = """#!ipxe
echo test
goto
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
        f.write(script)
        f.flush()
        is_valid, errors, warnings = validator.validate_file(f.name)
    Path(f.name).unlink()
    # Should be valid since we skip empty goto targets
    assert is_valid
