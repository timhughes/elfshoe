"""Command-line tool for validating iPXE scripts."""

import argparse
import sys
from pathlib import Path

from .validator import IPXEValidator


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

    validator = IPXEValidator()
    all_valid = True
    total_errors = 0
    total_warnings = 0

    for script_path in args.files:
        if not script_path.exists():
            print(f"Error: File not found: {script_path}", file=sys.stderr)
            all_valid = False
            continue

        is_valid, errors, warnings = validator.validate_file(script_path)

        # Print results
        if errors:
            print(f"\n❌ {script_path}: FAILED")
            for error in errors:
                print(f"  {error}")
            total_errors += len(errors)
            all_valid = False
        elif warnings:
            if not args.quiet:
                print(f"\n⚠️  {script_path}: WARNINGS")
                for warning in warnings:
                    print(f"  {warning}")
            total_warnings += len(warnings)
            if args.strict:
                all_valid = False
        else:
            if not args.quiet:
                print(f"✓ {script_path}: OK")

    # Summary
    if len(args.files) > 1 and not args.quiet:
        print("\n" + "=" * 60)
        print(f"Validated {len(args.files)} file(s)")
        if total_errors:
            print(f"  Errors: {total_errors}")
        if total_warnings:
            print(f"  Warnings: {total_warnings}")

    if not all_valid:
        sys.exit(1)


if __name__ == "__main__":
    main()
