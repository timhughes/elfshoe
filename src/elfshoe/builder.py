"""Distribution menu builder."""

import sys
from typing import Any, Dict, Optional, List

from .core import BootEntry, DistributionMenu, URLValidator, DEFAULT_ARCH_MAPS, ARCH_X86_64
from .distributions import get_metadata_fetcher


class DistributionBuilder:
    """Builds distribution menus from configuration."""

    def __init__(self, config: Dict[str, Any], validate_urls: bool = True, verbose: bool = True):
        """Initialize distribution builder.

        Args:
            config: Configuration dictionary
            validate_urls: Whether to validate URLs before including
            verbose: Print progress messages
        """
        self.config = config
        self.validate_urls = validate_urls
        self.verbose = verbose

    def _get_architectures(self, dist_id: str, dist_config: Dict[str, Any]) -> List[str]:
        """Get list of supported architectures for a distribution.
        
        Args:
            dist_id: Distribution identifier
            dist_config: Distribution configuration
            
        Returns:
            List of architecture strings (e.g., ['x86_64', 'arm64'])
        """
        # Check if architectures are specified
        architectures = dist_config.get("architectures")
        
        if not architectures:
            # Backward compatibility: default to x86_64 only
            return [ARCH_X86_64]
        
        if isinstance(architectures, list):
            # Simple list: ['x86_64', 'aarch64']
            return architectures
        
        if isinstance(architectures, dict):
            # Per-arch config: {x86_64: {...}, aarch64: {...}}
            return list(architectures.keys())
        
        return [ARCH_X86_64]
    
    def _get_arch_map(self, dist_id: str, dist_config: Dict[str, Any]) -> Dict[str, str]:
        """Get architecture name mapping for a distribution.
        
        Args:
            dist_id: Distribution identifier
            dist_config: Distribution configuration
            
        Returns:
            Dict mapping iPXE arch names to distribution arch names
        """
        # Use custom arch_map if provided
        if "arch_map" in dist_config:
            return dist_config["arch_map"]
        
        # Use default mapping for known distributions
        if dist_id in DEFAULT_ARCH_MAPS:
            return DEFAULT_ARCH_MAPS[dist_id]
        
        # Default: identity mapping
        return {ARCH_X86_64: ARCH_X86_64, 'arm64': 'arm64', 'i386': 'i386'}
    
    def _build_entry_for_arch(
        self,
        dist_id: str,
        version: str,
        label: str,
        dist_config: Dict[str, Any],
        ipxe_arch: str,
        arch_map: Dict[str, str]
    ) -> Optional[BootEntry]:
        """Build a boot entry for a specific architecture.
        
        Args:
            dist_id: Distribution identifier
            version: Version string
            label: Display label
            dist_config: Distribution configuration
            ipxe_arch: iPXE architecture name (e.g., 'x86_64', 'arm64')
            arch_map: Architecture name mapping
            
        Returns:
            BootEntry or None if validation fails
        """
        # Map iPXE arch to distribution arch
        dist_arch = arch_map.get(ipxe_arch, ipxe_arch)
        
        # Get configuration for this architecture
        arch_config = dist_config
        architectures = dist_config.get("architectures")
        
        if isinstance(architectures, dict) and ipxe_arch in architectures:
            # Per-arch configuration overrides
            arch_config = {**dist_config, **architectures[ipxe_arch]}
        
        url_template = arch_config["url_template"]
        kernel_path = arch_config["boot_files"]["kernel"]
        initrd_path = arch_config["boot_files"]["initrd"]
        boot_params = arch_config.get("boot_params", "")
        
        # Format URL with version and architecture
        base_url = url_template.format(version=version, arch=dist_arch)
        
        # Validate URLs if requested
        if self.validate_urls:
            if not URLValidator.verify_boot_files(
                base_url, kernel_path, initrd_path, verbose=False
            ):
                if self.verbose:
                    print(f"    ✗ {ipxe_arch}: boot files not found, skipping")
                return None
            if self.verbose:
                print(f"    ✓ {ipxe_arch}: verified")
        
        kernel_url = f"{base_url}/{kernel_path}"
        initrd_url = f"{base_url}/{initrd_path}"
        params = boot_params.format(base_url=base_url) if boot_params else ""
        
        return BootEntry(
            id=f"{dist_id}_{version}_{ipxe_arch}".replace('-', '_').replace('.', '_'),
            label=label,
            kernel_url=kernel_url,
            initrd_url=initrd_url,
            boot_params=params,
            arch=ipxe_arch
        )

    def build_static_distribution(
        self, dist_id: str, dist_config: Dict[str, Any]
    ) -> Optional[DistributionMenu]:
        """Build menu for a distribution with static version list.

        Args:
            dist_id: Distribution identifier (e.g., 'centos')
            dist_config: Distribution configuration from config file

        Returns:
            DistributionMenu object, or None if no valid entries
        """
        entries = []
        
        # Get supported architectures
        ipxe_architectures = self._get_architectures(dist_id, dist_config)
        arch_map = self._get_arch_map(dist_id, dist_config)

        for version_info in dist_config["versions"]:
            version = version_info["version"]
            label = version_info.get("label", f"{dist_id.title()} {version}")

            if self.verbose:
                print(f"  Checking {label}...")

            # Build entries for each architecture
            arch_entries = {}
            for ipxe_arch in ipxe_architectures:
                entry = self._build_entry_for_arch(
                    dist_id, version, label, dist_config, ipxe_arch, arch_map
                )
                if entry:
                    arch_entries[ipxe_arch] = entry

            if not arch_entries:
                if self.verbose:
                    print(f"  ✗ {label} - no valid architectures found, skipping")
                continue

            # Create multi-arch boot entry
            # Use first arch as primary for backward compatibility
            primary_arch = ipxe_architectures[0]
            primary_entry = arch_entries.get(primary_arch) or list(arch_entries.values())[0]
            
            # Build arch_urls mapping for template
            arch_urls = {}
            for ipxe_arch, entry in arch_entries.items():
                arch_urls[ipxe_arch] = {
                    'kernel': entry.kernel_url,
                    'initrd': entry.initrd_url,
                    'boot_params': entry.boot_params
                }
            
            # Create entry with multi-arch support
            entry = BootEntry(
                id=f"{dist_id}_{version.replace('-', '_').replace('.', '_')}",
                label=label,
                kernel_url=primary_entry.kernel_url,  # Fallback for single-arch
                initrd_url=primary_entry.initrd_url,
                boot_params=primary_entry.boot_params,
                arch_urls=arch_urls if len(arch_urls) > 1 else None
            )
            entries.append(entry)
            
            if self.verbose:
                archs_str = ", ".join(arch_entries.keys())
                print(f"  ✓ {label} ({archs_str})")

        if not entries:
            return None

        return DistributionMenu(
            id=f"{dist_id}_menu",
            label=dist_config["label"],
            entries=entries,
            architectures=ipxe_architectures
        )

    def build_dynamic_distribution(
        self, dist_id: str, dist_config: Dict[str, Any]
    ) -> Optional[DistributionMenu]:
        """Build menu for a distribution with dynamic version detection.

        Args:
            dist_id: Distribution identifier (e.g., 'fedora')
            dist_config: Distribution configuration from config file

        Returns:
            DistributionMenu object, or None if no valid entries
        """
        entries = []

        # Get metadata provider
        metadata_provider = dist_config.get("metadata_provider")
        if not metadata_provider:
            print(f"  ✗ No metadata_provider specified for {dist_id}", file=sys.stderr)
            return None

        fetcher_class = get_metadata_fetcher(metadata_provider)
        if not fetcher_class:
            print(f"  ✗ Unknown metadata provider: {metadata_provider}", file=sys.stderr)
            from .distributions import METADATA_PROVIDERS

            providers = ", ".join(METADATA_PROVIDERS.keys())
            print(f"     Available providers: {providers}", file=sys.stderr)
            return None

        # Fetch versions from metadata
        metadata_url = dist_config["metadata_url"]
        metadata_filter = dist_config.get("metadata_filter", {})

        if self.verbose:
            print(f"  Fetching metadata from {metadata_url}...")

        fetcher = fetcher_class()
        versions = fetcher.fetch_versions(metadata_url, **metadata_filter)

        if not versions:
            print(f"  ✗ No versions found for {dist_id}", file=sys.stderr)
            return None

        if self.verbose:
            print(f"  Found {len(versions)} versions: {', '.join(map(str, versions))}")

        # Get supported architectures from config
        ipxe_architectures = self._get_architectures(dist_id, dist_config)
        arch_map = self._get_arch_map(dist_id, dist_config)
        
        # For Fedora, check which architectures are actually available in metadata
        version_architectures = {}
        if metadata_provider == "fedora" and hasattr(fetcher, 'get_version_architectures'):
            variant = metadata_filter.get("variant", "Server")
            version_architectures = fetcher.get_version_architectures(metadata_url, variant)
            if self.verbose and version_architectures:
                print(f"  Metadata indicates available architectures per version")

        # Build entries for each version
        for version in versions:
            label = f"{dist_config['label']} {version}"

            if self.verbose:
                print(f"  Checking {label}...")
            
            # Filter architectures: only check those available in metadata (if known)
            architectures_to_check = ipxe_architectures
            if str(version) in version_architectures:
                available_in_metadata = version_architectures[str(version)]
                # Map iPXE arch names to distro arch names and check
                architectures_to_check = [
                    ipxe_arch for ipxe_arch in ipxe_architectures
                    if arch_map.get(ipxe_arch, ipxe_arch) in available_in_metadata
                ]
                
                if self.verbose and len(architectures_to_check) < len(ipxe_architectures):
                    skipped = set(ipxe_architectures) - set(architectures_to_check)
                    print(f"    ℹ Skipping {', '.join(skipped)} (not in metadata)")

            # Build entries for each architecture
            arch_entries = {}
            for ipxe_arch in architectures_to_check:
                entry = self._build_entry_for_arch(
                    dist_id, str(version), label, dist_config, ipxe_arch, arch_map
                )
                if entry:
                    arch_entries[ipxe_arch] = entry

            if not arch_entries:
                if self.verbose:
                    print(f"  ✗ {label} - no valid architectures found, skipping")
                continue

            # Create multi-arch boot entry
            primary_arch = ipxe_architectures[0]
            primary_entry = arch_entries.get(primary_arch) or list(arch_entries.values())[0]
            
            # Build arch_urls mapping
            arch_urls = {}
            for ipxe_arch, entry in arch_entries.items():
                arch_urls[ipxe_arch] = {
                    'kernel': entry.kernel_url,
                    'initrd': entry.initrd_url,
                    'boot_params': entry.boot_params
                }
            
            entry = BootEntry(
                id=f"{dist_id}_{version}".replace('-', '_').replace('.', '_'),
                label=label,
                kernel_url=primary_entry.kernel_url,
                initrd_url=primary_entry.initrd_url,
                boot_params=primary_entry.boot_params,
                arch_urls=arch_urls if len(arch_urls) > 1 else None
            )
            entries.append(entry)
            
            if self.verbose:
                archs_str = ", ".join(arch_entries.keys())
                print(f"  ✓ {label} ({archs_str})")

        if not entries:
            return None

        return DistributionMenu(
            id=f"{dist_id}_menu",
            label=dist_config["label"],
            entries=entries,
            architectures=ipxe_architectures
        )

    def build_distribution(
        self, dist_id: str, dist_config: Dict[str, Any]
    ) -> Optional[DistributionMenu]:
        """Build a distribution menu based on its type.

        Args:
            dist_id: Distribution identifier
            dist_config: Distribution configuration from config file

        Returns:
            DistributionMenu object, or None if disabled or invalid
        """
        if not dist_config.get("enabled", True):
            if self.verbose:
                print("  ⊘ Skipped (disabled)")
            return None

        dist_type = dist_config.get("type", "static")

        if dist_type == "static":
            return self.build_static_distribution(dist_id, dist_config)
        elif dist_type == "dynamic":
            return self.build_dynamic_distribution(dist_id, dist_config)
        else:
            print(f"  ✗ Unknown distribution type: {dist_type}", file=sys.stderr)
            return None
