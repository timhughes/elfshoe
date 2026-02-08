"""Command-line tool for validating iPXE scripts."""

import argparse
import sys
from pathlib import Path

from .validator import validate_multiple_files


def main():
    """Main entry point for ipxelint."""
    parser = argparse.ArgumentParser(
        description="Validate iPXE boot scripts for syntax errors",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s elfshoe.ipxe              # Validate a single file
  %(prog)s *.ipxe                    # Validate multiple files
  %(prog)s --strict elfshoe.ipxe     # Treat warnings as errors
        """,
    )

    parser.add_argument("files", nargs="+", type=Path, help="iPXE script file(s) to validate")
    parser.add_argument(
        "--strict", action="store_true", help="Treat warnings as errors (non-zero exit code)"
    )
    parser.add_argument("--quiet", "-q", action="store_true", help="Only show errors")
    parser.add_argument("--version", action="version", version="%(prog)s 2.0.0")

    args = parser.parse_args()

    all_valid = validate_multiple_files(args.files, strict=args.strict, quiet=args.quiet)

    if not all_valid:
        sys.exit(1)


if __name__ == "__main__":
    main()
