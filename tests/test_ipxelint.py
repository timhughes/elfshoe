"""Tests for ipxelint CLI."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from elfshoe.ipxelint import main


def test_ipxelint_valid_file(capsys):
    """Test ipxelint with a valid script."""
    script = """#!ipxe
echo Hello World
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
        f.write(script)
        f.flush()

        with patch("sys.argv", ["ipxelint", str(f.name)]):
            main()

        captured = capsys.readouterr()
    Path(f.name).unlink()

    assert "OK" in captured.out


def test_ipxelint_invalid_file(capsys):
    """Test ipxelint with an invalid script."""
    script = """#!ipxe
goto undefined_label
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
        f.write(script)
        f.flush()

        with patch("sys.argv", ["ipxelint", str(f.name)]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        captured = capsys.readouterr()
    Path(f.name).unlink()

    assert exc_info.value.code == 1
    assert "FAILED" in captured.out


def test_ipxelint_multiple_files(capsys):
    """Test ipxelint with multiple files."""
    scripts = [
        """#!ipxe
echo Script 1
""",
        """#!ipxe
echo Script 2
""",
    ]

    files = []
    for script in scripts:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
            f.write(script)
            f.flush()
            files.append(str(f.name))

    with patch("sys.argv", ["ipxelint"] + files):
        main()

    captured = capsys.readouterr()

    for f in files:
        Path(f).unlink()

    assert "Validated 2 file(s)" in captured.out


def test_ipxelint_quiet_mode(capsys):
    """Test ipxelint in quiet mode."""
    script = """#!ipxe
echo Hello World
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
        f.write(script)
        f.flush()

        with patch("sys.argv", ["ipxelint", "--quiet", str(f.name)]):
            main()

        captured = capsys.readouterr()
    Path(f.name).unlink()

    assert captured.out == ""  # No output in quiet mode


def test_ipxelint_strict_mode_with_warnings(capsys):
    """Test ipxelint in strict mode with warnings."""
    script = """#!ipxe
menu My Menu
item option1 Option 1
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as f:
        f.write(script)
        f.flush()

        with patch("sys.argv", ["ipxelint", "--strict", str(f.name)]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        captured = capsys.readouterr()
    Path(f.name).unlink()

    assert exc_info.value.code == 1
    assert "WARNINGS" in captured.out


def test_ipxelint_file_not_found(capsys):
    """Test ipxelint with non-existent file."""
    with patch("sys.argv", ["ipxelint", "/nonexistent/file.ipxe"]):
        with pytest.raises(SystemExit) as exc_info:
            main()

    captured = capsys.readouterr()
    assert exc_info.value.code == 1
    assert "not found" in captured.err.lower()
