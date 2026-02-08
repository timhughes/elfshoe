"""iPXE script validator.

Validates generated iPXE scripts for common syntax errors.
"""

from pathlib import Path
from typing import List, Tuple


class ValidationError:
    """Represents a validation error in an iPXE script."""

    def __init__(self, line_num: int, message: str):
        self.line_num = line_num
        self.message = message

    def __str__(self):
        return f"Line {self.line_num}: {self.message}"


class IPXEValidator:
    """Validates iPXE script syntax."""

    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []

    def validate_file(
        self, script_path: Path
    ) -> Tuple[bool, List[ValidationError], List[ValidationError]]:
        """Validate an iPXE script file.

        Args:
            script_path: Path to iPXE script file

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []

        with open(script_path) as f:
            lines = f.readlines()

        self._check_shebang(lines)
        self._check_menu_balance(lines)
        self._check_labels(lines)
        self._check_commands(lines)

        return len(self.errors) == 0, self.errors, self.warnings

    def _check_shebang(self, lines: List[str]):
        """Check for valid iPXE shebang."""
        if not lines:
            self.errors.append(ValidationError(0, "Empty file"))
            return

        if not lines[0].strip().startswith("#!ipxe"):
            self.errors.append(ValidationError(1, "Missing or invalid #!ipxe shebang"))

    def _check_menu_balance(self, lines: List[str]):
        """Check that all menus have corresponding choose statements."""
        menu_count = sum(1 for line in lines if line.strip().startswith("menu "))
        choose_count = sum(1 for line in lines if line.strip().startswith("choose "))

        if menu_count != choose_count:
            self.warnings.append(
                ValidationError(
                    0,
                    f"Unbalanced menus: {menu_count} menu statements, "
                    f"{choose_count} choose statements",
                )
            )

    def _check_labels(self, lines: List[str]):
        """Check for undefined label references."""
        # Collect all defined labels
        labels = set()
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith(":") and not stripped.startswith("::"):
                # Extract label name (everything after :)
                label = stripped[1:].split()[0] if stripped[1:].split() else ""
                if label:
                    labels.add(label)

        # Check goto targets
        for i, line in enumerate(lines, 1):
            if " goto " in line or line.strip().startswith("goto "):
                # Extract everything after 'goto '
                goto_pos = line.find("goto ")
                if goto_pos == -1:
                    continue

                after_goto = line[goto_pos + 5 :].strip()
                if not after_goto:
                    continue

                # Get first token (the target)
                target = after_goto.split()[0] if after_goto.split() else ""

                # Skip variable references: ${var}, $var, or any string containing $
                if "$" in target or "{" in target:
                    continue

                # Check if label exists
                if target and target not in labels:
                    self.errors.append(
                        ValidationError(i, f"Reference to undefined label: '{target}'")
                    )

    def _check_commands(self, lines: List[str]):
        """Check for common command syntax errors."""
        known_commands = {
            "menu",
            "item",
            "choose",
            "goto",
            "chain",
            "kernel",
            "initrd",
            "boot",
            "set",
            "echo",
            "dhcp",
            "shell",
            "exit",
            "sleep",
            "sanboot",
            "imgfree",
            "imgload",
            "prompt",
            "read",
            "isset",
            "iseq",  # Compare strings/variables
            "inc",
            "dec",
        }

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Skip comments and labels
            if stripped.startswith("#") or stripped.startswith(":"):
                continue

            # Skip empty lines
            if not stripped:
                continue

            # Check if line starts with known command
            first_word = stripped.split()[0] if stripped.split() else ""
            if first_word and first_word not in known_commands:
                # Could be a typo or unknown command
                self.warnings.append(
                    ValidationError(i, f"Unknown or potentially misspelled command: '{first_word}'")
                )
