"""Distribution menu builder."""

import sys
from typing import Any, Dict, List, Optional

from .core import ARCH_X86_64, DEFAULT_ARCH_MAPS, BootEntry, DistributionMenu, URLValidator
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
        return {ARCH_X86_64: ARCH_X86_64, "arm64": "arm64", "i386": "i386"}

    def _build_entry_for_arch(
        self,
        dist_id: str,
        version: str,
        label: str,
        dist_config: Dict[str, Any],
        ipxe_arch: str,
        arch_map: Dict[str, str],
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
            id=f"{dist_id}_{version}_{ipxe_arch}".replace("-", "_").replace(".", "_"),
            label=label,
            kernel_url=kernel_url,
            initrd_url=initrd_url,
            boot_params=params,
            architecture=ipxe_arch,
            version=version,
        )

    def _format_label(
        self,
        dist_label: str,
        version: str,
        ipxe_arch: str,
        arch_map: Dict[str, str],
        variant: Optional[str] = None,
        name: Optional[str] = None,
    ) -> str:
        """Format a human-friendly label for a boot entry.

        Args:
            dist_label: Distribution label (e.g., "Fedora")
            version: Version string (e.g., "43")
            ipxe_arch: iPXE architecture name (e.g., "x86_64", "arm64")
            arch_map: Architecture name mapping
            variant: Optional variant name (e.g., "Server")
            name: Optional release name (e.g., "Bookworm")

        Returns:
            Formatted label (e.g., "Fedora 43 Server (x86_64)")
        """
        # Get the architecture name to display (use distribution name if mapped)
        display_arch = arch_map.get(ipxe_arch, ipxe_arch)

        parts = [dist_label, version]

        if name:
            parts.append(name)
        elif variant:
            parts.append(variant)

        parts.append(f"({display_arch})")

        return " ".join(parts)

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

        # Get architecture mapping
        arch_map = self._get_arch_map(dist_id, dist_config)

        for version_info in dist_config["versions"]:
            version = version_info["version"]
            base_label = version_info.get("label", f"{dist_id.title()} {version}")
            name = version_info.get("name")  # e.g., "Bookworm" for Debian

            # Get architectures for this version
            version_architectures = version_info.get("architectures")
            if not version_architectures:
                # Backward compatibility: use top-level architectures or default to x86_64
                version_architectures = self._get_architectures(dist_id, dist_config)

            if self.verbose:
                print(f"  Checking {base_label}...")

            # Build entry for each architecture
            for ipxe_arch in version_architectures:

                # Generate human-friendly label
                label = self._format_label(
                    dist_config["label"].replace("Boot ", "").replace(" (multiple versions)", ""),
                    version,
                    ipxe_arch,
                    arch_map,
                    name=name,
                )

                # Build boot entry
                entry = self._build_entry_for_arch(
                    dist_id, version, label, dist_config, ipxe_arch, arch_map
                )

                if entry:
                    entries.append(entry)
                    if self.verbose:
                        print(f"    ✓ {label}")
                else:
                    if self.verbose:
                        print(f"    ✗ {label} - boot files not found, skipping")

        if not entries:
            return None

        # Collect all architectures used
        all_architectures = list(set(entry.architecture for entry in entries))

        return DistributionMenu(
            id=f"{dist_id}_menu",
            label=dist_config["label"],
            entries=entries,
            architectures=all_architectures,
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

        # Fetch version objects from metadata
        metadata_url = dist_config["metadata_url"]
        metadata_filter = dist_config.get("metadata_filter", {})

        if self.verbose:
            print(f"  Fetching metadata from {metadata_url}...")

        fetcher = fetcher_class()
        version_objects = fetcher.fetch_versions(metadata_url, **metadata_filter)

        if not version_objects:
            print(f"  ✗ No versions found for {dist_id}", file=sys.stderr)
            return None

        if self.verbose:
            version_list = [vo["version"] for vo in version_objects]
            print(f"  Found {len(version_objects)} versions: {', '.join(version_list)}")

        # Get architecture mapping
        arch_map = self._get_arch_map(dist_id, dist_config)

        # Build entries for each version × architecture combination
        for version_obj in version_objects:
            version = version_obj["version"]
            variant = version_obj.get("variant")
            name = version_obj.get("name")
            architectures = version_obj["architectures"]

            if self.verbose:
                archs_str = ", ".join(architectures)
                print(f"  Checking {dist_config['label']} {version} ({archs_str})...")

            # Build entry for each architecture
            for dist_arch in architectures:
                # Map distribution arch to iPXE arch (reverse mapping)
                ipxe_arch = None
                for ipxe, dist in arch_map.items():
                    if dist == dist_arch:
                        ipxe_arch = ipxe
                        break
                if not ipxe_arch:
                    ipxe_arch = dist_arch  # Use as-is if no mapping

                # Generate human-friendly label
                label = self._format_label(
                    dist_config["label"], version, ipxe_arch, arch_map, variant=variant, name=name
                )

                # Build boot entry
                entry = self._build_entry_for_arch(
                    dist_id, version, label, dist_config, ipxe_arch, arch_map
                )

                if entry:
                    entries.append(entry)
                    if self.verbose:
                        print(f"    ✓ {label}")
                else:
                    if self.verbose:
                        print(f"    ✗ {label} - boot files not found, skipping")

        if not entries:
            return None

        # Collect all architectures used
        all_architectures = list(set(entry.architecture for entry in entries))

        return DistributionMenu(
            id=f"{dist_id}_menu",
            label=dist_config["label"],
            entries=entries,
            architectures=all_architectures,
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
