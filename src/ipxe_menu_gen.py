#!/usr/bin/env python3
"""
iPXE Menu Generator - A configurable iPXE boot menu generator.

This tool generates iPXE menu files from a configuration file and templates.
It supports dynamic version detection, URL validation, and custom boot options.
"""

import argparse
import json
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


@dataclass
class BootEntry:
    """Represents a single boot entry."""
    id: str
    label: str
    kernel_url: str
    initrd_url: str
    boot_params: str


@dataclass
class DistributionMenu:
    """Represents a distribution submenu."""
    id: str
    label: str
    entries: List[BootEntry]


class URLValidator:
    """Validates that URLs are accessible."""
    
    @staticmethod
    def check_url(url: str, timeout: int = 10, verbose: bool = True) -> bool:
        """Check if a URL is accessible."""
        try:
            req = urllib.request.Request(url, method='HEAD')
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.status == 200
        except Exception as e:
            if verbose:
                print(f"  ✗ Failed to access {url}: {e}", file=sys.stderr)
            return False
    
    @staticmethod
    def verify_boot_files(base_url: str, kernel_path: str, initrd_path: str, 
                         verbose: bool = True) -> bool:
        """Verify that kernel and initrd files exist."""
        kernel_url = f"{base_url}/{kernel_path}"
        initrd_url = f"{base_url}/{initrd_path}"
        
        kernel_ok = URLValidator.check_url(kernel_url, verbose=verbose)
        initrd_ok = URLValidator.check_url(initrd_url, verbose=verbose)
        
        return kernel_ok and initrd_ok


class FedoraMetadataFetcher:
    """Fetches Fedora release metadata."""
    
    @staticmethod
    def fetch_versions(metadata_url: str, variant: str, arch: str) -> List[str]:
        """Fetch available Fedora versions from releases.json."""
        try:
            with urllib.request.urlopen(metadata_url, timeout=30) as response:
                data = json.loads(response.read())
            
            versions = set()
            for release in data:
                if (release.get('variant') == variant and 
                    release.get('arch') == arch):
                    versions.add(release['version'])
            
            return sorted(versions, key=int, reverse=True)
        except Exception as e:
            print(f"Error fetching Fedora metadata: {e}", file=sys.stderr)
            return []


class DistributionBuilder:
    """Builds distribution menu entries from configuration."""
    
    def __init__(self, config: Dict[str, Any], validate_urls: bool = True, 
                 verbose: bool = True):
        self.config = config
        self.validate_urls = validate_urls
        self.verbose = verbose
    
    def build_static_distribution(self, dist_id: str, dist_config: Dict[str, Any]) -> Optional[DistributionMenu]:
        """Build menu for a distribution with static version list."""
        entries = []
        
        url_template = dist_config['url_template']
        kernel_path = dist_config['boot_files']['kernel']
        initrd_path = dist_config['boot_files']['initrd']
        boot_params = dist_config.get('boot_params', '')
        
        for version_info in dist_config['versions']:
            version = version_info['version']
            label = version_info.get('label', f"{dist_id.title()} {version}")
            
            base_url = url_template.format(version=version)
            
            if self.verbose:
                print(f"  Checking {label}...")
            
            # Validate URLs if requested
            if self.validate_urls:
                if not URLValidator.verify_boot_files(base_url, kernel_path, initrd_path, 
                                                      verbose=self.verbose):
                    if self.verbose:
                        print(f"  ✗ {label} - boot files not found, skipping")
                    continue
                if self.verbose:
                    print(f"  ✓ {label} verified")
            
            entry_id = f"{dist_id}_{version.replace('-', '_')}"
            kernel_url = f"{base_url}/{kernel_path}"
            initrd_url = f"{base_url}/{initrd_path}"
            
            params = boot_params.format(base_url=base_url) if boot_params else ""
            
            entry = BootEntry(
                id=entry_id,
                label=label,
                kernel_url=kernel_url,
                initrd_url=initrd_url,
                boot_params=params
            )
            entries.append(entry)
        
        if not entries:
            return None
        
        return DistributionMenu(
            id=f"{dist_id}_menu",
            label=dist_config['label'],
            entries=entries
        )
    
    def build_dynamic_distribution(self, dist_id: str, dist_config: Dict[str, Any]) -> Optional[DistributionMenu]:
        """Build menu for a distribution with dynamic version detection."""
        entries = []
        
        # Fetch versions from metadata
        metadata_url = dist_config['metadata_url']
        metadata_filter = dist_config.get('metadata_filter', {})
        
        if self.verbose:
            print(f"  Fetching metadata from {metadata_url}...")
        
        if 'fedoraproject.org' in metadata_url:
            versions = FedoraMetadataFetcher.fetch_versions(
                metadata_url,
                metadata_filter.get('variant', 'Server'),
                metadata_filter.get('arch', 'x86_64')
            )
        else:
            print(f"  ✗ Unknown metadata source for {dist_id}", file=sys.stderr)
            return None
        
        if not versions:
            print(f"  ✗ No versions found for {dist_id}", file=sys.stderr)
            return None
        
        if self.verbose:
            print(f"  Found versions: {', '.join(versions)}")
        
        # Build entries
        url_template = dist_config['url_template']
        kernel_path = dist_config['boot_files']['kernel']
        initrd_path = dist_config['boot_files']['initrd']
        boot_params = dist_config.get('boot_params', '')
        menu_label = dist_config.get('menu_label', f"{dist_id.title()} {{version}}")
        
        for version in versions:
            label = menu_label.format(version=version)
            base_url = url_template.format(version=version)
            
            if self.verbose:
                print(f"  Checking {label}...")
            
            # Validate URLs if requested
            if self.validate_urls:
                if not URLValidator.verify_boot_files(base_url, kernel_path, initrd_path,
                                                      verbose=self.verbose):
                    if self.verbose:
                        print(f"  ✗ {label} - boot files not found, skipping")
                    continue
                if self.verbose:
                    print(f"  ✓ {label} verified")
            
            entry_id = f"{dist_id}_{version}"
            kernel_url = f"{base_url}/{kernel_path}"
            initrd_url = f"{base_url}/{initrd_path}"
            
            params = boot_params.format(base_url=base_url) if boot_params else ""
            
            entry = BootEntry(
                id=entry_id,
                label=label,
                kernel_url=kernel_url,
                initrd_url=initrd_url,
                boot_params=params
            )
            entries.append(entry)
        
        if not entries:
            return None
        
        return DistributionMenu(
            id=f"{dist_id}_menu",
            label=dist_config['label'],
            entries=entries
        )
    
    def build_distribution(self, dist_id: str, dist_config: Dict[str, Any]) -> Optional[DistributionMenu]:
        """Build a distribution menu."""
        if not dist_config.get('enabled', True):
            if self.verbose:
                print(f"  Skipping {dist_id} (disabled)")
            return None
        
        dist_type = dist_config.get('type', 'static')
        
        if dist_type == 'static':
            return self.build_static_distribution(dist_id, dist_config)
        elif dist_type == 'dynamic':
            return self.build_dynamic_distribution(dist_id, dist_config)
        else:
            print(f"  ✗ Unknown distribution type: {dist_type}", file=sys.stderr)
            return None


class MenuGenerator:
    """Generates iPXE menu files."""
    
    def __init__(self, config: Dict[str, Any], template_path: Optional[Path] = None):
        self.config = config
        self.template_path = template_path
    
    def generate_submenu(self, menu: DistributionMenu) -> str:
        """Generate iPXE code for a distribution submenu."""
        lines = [f":{menu.id}"]
        lines.append(f"menu {menu.label.split('(')[0].strip()} - Select Version")
        
        # Add menu items
        for entry in menu.entries:
            lines.append(f"item {entry.id} {entry.label}")
        
        lines.append("item --gap --")
        lines.append(f"item back_{menu.id} Back to main menu")
        lines.append(f"choose --default {menu.entries[0].id} target && goto ${{target}}")
        lines.append("")
        
        # Add boot entries
        for entry in menu.entries:
            lines.append(f":{entry.id}")
            
            # Determine initrd parameter name based on file extension
            initrd_name = "initrd.img" if entry.initrd_url.endswith('.img') else "initrd.gz"
            
            # Load initrd first, then chain to kernel
            lines.append(f"initrd {entry.initrd_url}")
            boot_line = f"chain {entry.kernel_url} initrd={initrd_name}"
            if entry.boot_params:
                boot_line += f" {entry.boot_params}"
            boot_line += f" || goto {menu.id}_error"
            
            lines.append(boot_line)
            lines.append("")
        
        # Add error handler with pause
        lines.append(f":{menu.id}_error")
        lines.append("echo")
        lines.append("echo Boot failed! Press any key to return to menu...")
        lines.append("prompt --timeout 30000")
        lines.append(f"goto {menu.id}")
        lines.append("")
        
        # Add back option
        lines.append(f":back_{menu.id}")
        lines.append("goto start")
        lines.append("")
        
        return "\n".join(lines)
    
    def generate_additional_items(self) -> str:
        """Generate iPXE code for additional menu items."""
        lines = []
        
        for item in self.config.get('additional_items', []):
            item_id = item['id']
            item_type = item['type']
            
            lines.append(f":{item_id}")
            
            if item_type == 'chain':
                lines.append(f"chain --autofree {item['url']} || goto chain_error")
            elif item_type == 'shell':
                lines.append("shell")
            elif item_type == 'exit':
                lines.append("exit")
            
            lines.append("")
        
        # Add error handler for chain failures
        if any(item['type'] == 'chain' for item in self.config.get('additional_items', [])):
            lines.append(":chain_error")
            lines.append("echo")
            lines.append("echo Chain load failed! Press any key to return to menu...")
            lines.append("prompt --timeout 30000")
            lines.append("goto start")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_main_menu(self, menus: List[DistributionMenu]) -> str:
        """Generate the main menu."""
        menu_config = self.config.get('menu', {})
        title = menu_config.get('title', 'Network Boot Menu')
        default = menu_config.get('default_item', 'shell')
        timeout = menu_config.get('timeout', 30000)
        
        lines = ["#!ipxe", "dhcp", "", ":start"]
        lines.append(f"menu {title}")
        
        # Distribution section
        if menus:
            lines.append("item --gap -- Operating Systems:")
            for menu in menus:
                lines.append(f"item {menu.id} {menu.label}")
        
        # Additional items section
        additional_items = self.config.get('additional_items', [])
        if additional_items:
            lines.append("item --gap -- Other Options:")
            for item in additional_items:
                if item['type'] not in ['shell', 'exit']:
                    lines.append(f"item {item['id']} {item['label']}")
        
        # Advanced section
        advanced_items = [item for item in additional_items if item['type'] in ['shell', 'exit']]
        if advanced_items:
            lines.append("item --gap -- Advanced:")
            for item in advanced_items:
                lines.append(f"item {item['id']} {item['label']}")
        
        lines.append(f"choose --default {default} --timeout {timeout} target && goto ${{target}}")
        lines.append("")
        
        return "\n".join(lines)
    
    def generate(self, menus: List[DistributionMenu]) -> str:
        """Generate complete iPXE menu."""
        parts = []
        
        # Main menu
        parts.append(self.generate_main_menu(menus))
        
        # Distribution submenus
        for menu in menus:
            parts.append(self.generate_submenu(menu))
        
        # Additional items
        parts.append(self.generate_additional_items())
        
        return "\n".join(parts)


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate iPXE boot menus from configuration files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Use default config.yaml
  %(prog)s -c custom.yaml            # Use custom config
  %(prog)s -o custom-menu.ipxe       # Custom output file
  %(prog)s --no-validate             # Skip URL validation (faster)
  %(prog)s --quiet                   # Minimal output
        """
    )
    
    parser.add_argument('-c', '--config', type=Path, default='config.yaml',
                       help='Configuration file (default: config.yaml)')
    parser.add_argument('-o', '--output', type=Path, default='menu.ipxe',
                       help='Output file (default: menu.ipxe)')
    parser.add_argument('--no-validate', action='store_true',
                       help='Skip URL validation (faster but may include broken links)')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Minimal output')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    
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
    
    builder = DistributionBuilder(config, validate_urls=not args.no_validate, 
                                  verbose=verbose)
    menus = []
    
    for dist_id, dist_config in config.get('distributions', {}).items():
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
        print(f"\nGenerating menu file...")
    
    generator = MenuGenerator(config)
    menu_content = generator.generate(menus)
    
    # Write output
    try:
        with open(args.output, 'w') as f:
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
