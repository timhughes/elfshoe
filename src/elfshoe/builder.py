"""Distribution menu builder."""

import sys
from typing import Any, Dict, Optional

from .core import BootEntry, DistributionMenu, URLValidator
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

        url_template = dist_config["url_template"]
        kernel_path = dist_config["boot_files"]["kernel"]
        initrd_path = dist_config["boot_files"]["initrd"]
        boot_params = dist_config.get("boot_params", "")

        for version_info in dist_config["versions"]:
            version = version_info["version"]
            label = version_info.get("label", f"{dist_id.title()} {version}")

            base_url = url_template.format(version=version)

            if self.verbose:
                print(f"  Checking {label}...")

            # Validate URLs if requested
            if self.validate_urls:
                if not URLValidator.verify_boot_files(
                    base_url, kernel_path, initrd_path, verbose=self.verbose
                ):
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
                boot_params=params,
            )
            entries.append(entry)

        if not entries:
            return None

        return DistributionMenu(id=f"{dist_id}_menu", label=dist_config["label"], entries=entries)

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

        # Build entries for each version
        url_template = dist_config["url_template"]
        kernel_path = dist_config["boot_files"]["kernel"]
        initrd_path = dist_config["boot_files"]["initrd"]
        boot_params = dist_config.get("boot_params", "")

        for version in versions:
            base_url = url_template.format(version=version)
            label = f"{dist_config['label']} {version}"

            if self.verbose:
                print(f"  Checking {label}...")

            # Validate URLs if requested
            if self.validate_urls:
                if not URLValidator.verify_boot_files(
                    base_url, kernel_path, initrd_path, verbose=self.verbose
                ):
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
                boot_params=params,
            )
            entries.append(entry)

        if not entries:
            return None

        return DistributionMenu(id=f"{dist_id}_menu", label=dist_config["label"], entries=entries)

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
