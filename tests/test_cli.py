"""Tests for CLI validation integration."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from elfshoe.cli import main


def create_test_config():
    """Create a minimal test configuration."""
    return {"ipxe": {"boot_url": "http://example.com/boot"}, "distributions": {}}


def test_cli_validates_generated_file(capsys):
    """Test that CLI validates the generated iPXE file."""
    config = create_test_config()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as cfg_file:
        yaml.dump(config, cfg_file)
        cfg_file.flush()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as out_file:
            with patch("sys.argv", ["cli", "-c", cfg_file.name, "-o", out_file.name]):
                main()

            captured = capsys.readouterr()

    Path(cfg_file.name).unlink()
    Path(out_file.name).unlink()

    assert "Validating generated iPXE script" in captured.out
    assert "OK" in captured.out


def test_cli_validation_passes_with_quiet_mode(capsys):
    """Test CLI validation in quiet mode."""
    config = create_test_config()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as cfg_file:
        yaml.dump(config, cfg_file)
        cfg_file.flush()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as out_file:
            with patch("sys.argv", ["cli", "-c", cfg_file.name, "-o", out_file.name, "--quiet"]):
                main()

            captured = capsys.readouterr()

    Path(cfg_file.name).unlink()
    Path(out_file.name).unlink()

    # In quiet mode, output should be minimal (no verbose messages)
    assert "Building distribution menus" not in captured.out


def test_cli_exits_on_validation_failure(capsys):
    """Test that CLI exits with error if validation fails."""
    config = create_test_config()

    # Mock validate_and_report to return False
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as cfg_file:
        yaml.dump(config, cfg_file)
        cfg_file.flush()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as out_file:
            with patch("sys.argv", ["cli", "-c", cfg_file.name, "-o", out_file.name]):
                with patch("elfshoe.cli.validate_and_report", return_value=False):
                    with pytest.raises(SystemExit) as exc_info:
                        main()

            captured = capsys.readouterr()

    Path(cfg_file.name).unlink()
    Path(out_file.name).unlink()

    assert exc_info.value.code == 1
    assert "validation errors" in captured.err.lower()


def test_cli_exits_on_https_redirect(capsys):
    """Test that CLI exits with error on HTTPS redirect detection."""
    config = create_test_config()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as cfg_file:
        yaml.dump(config, cfg_file)
        cfg_file.flush()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".ipxe", delete=False) as out_file:
            with patch("sys.argv", ["cli", "-c", cfg_file.name, "-o", out_file.name]):
                # Mock the URLValidator to simulate HTTPS redirect
                with patch("elfshoe.cli.URLValidator.https_redirect_detected", True):
                    with pytest.raises(SystemExit) as exc_info:
                        main()

            captured = capsys.readouterr()

    Path(cfg_file.name).unlink()
    Path(out_file.name).unlink()

    assert exc_info.value.code == 1
    assert "HTTPS redirect" in captured.err
