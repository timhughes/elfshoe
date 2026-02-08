"""Command-line interface for iPXE Menu Generator."""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

from .builder import DistributionBuilder
from .core import MenuGenerator


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate iPXE boot menus from configuration files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Use default config.yaml
  %(prog)s -c custom.yaml            # Use custom config
  %(prog)s -o custom-menu.ipxe       # Custom output file
  %(prog)s --no-validate             # Skip URL validation (faster)
  %(prog)s --quiet                   # Minimal output
        """,
    )

    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default="config.yaml",
        help="Configuration file (default: config.yaml)",
    )
    parser.add_argument(
        "-o", "--output", type=Path, default="elfshoe.ipxe", help="Output file (default: elfshoe.ipxe)"
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip URL validation (faster but may include broken links)",
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="Minimal output")
    parser.add_argument("--version", action="version", version="%(prog)s 2.0.0")

    args = parser.parse_args()

    # Load configuration
    if not args.config.exists():
        print(f"Error: Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)

    config = load_config(args.config)
    verbose = not args.quiet

    # Build distribution menus
    if verbose:
        print("Building distribution menus...")

    builder = DistributionBuilder(config, validate_urls=not args.no_validate, verbose=verbose)
    menus = []

    for dist_id, dist_config in config.get("distributions", {}).items():
        if verbose:
            print(f"\nProcessing {dist_id}...")

        menu = builder.build_distribution(dist_id, dist_config)
        if menu:
            menus.append(menu)
            if verbose:
                print(f"  ✓ Generated menu with {len(menu.entries)} entries")

    if not menus:
        print("Warning: No distribution menus generated", file=sys.stderr)

    # Generate menu file
    if verbose:
        print("\nGenerating menu file...")

    generator = MenuGenerator(config)
    menu_content = generator.generate(menus)

    # Write output
    try:
        with open(args.output, "w") as f:
            f.write(menu_content)

        if verbose:
            print(f"✓ Menu generated successfully: {args.output}")
            print(f"  Total distributions: {len(menus)}")
            print(f"  Total boot entries: {sum(len(m.entries) for m in menus)}")
    except Exception as e:
        print(f"Error writing output: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
