"""Distribution metadata fetchers package.

This package contains metadata fetchers for different distributions.
Each distribution can provide its own fetcher by implementing
the AbstractMetadataFetcher interface.
"""

from .base import AbstractMetadataFetcher
from .fedora import FedoraMetadataFetcher

# Registry of available metadata providers
METADATA_PROVIDERS = {
    "fedora": FedoraMetadataFetcher,
    # Add more providers as they're implemented:
    # 'centos': CentOSMetadataFetcher,
    # 'debian': DebianMetadataFetcher,
    # 'windows': WindowsMetadataFetcher,
}


def get_metadata_fetcher(provider_name: str) -> type[AbstractMetadataFetcher] | None:
    """Get a metadata fetcher class by name.

    Args:
        provider_name: Name of the provider (e.g., 'fedora')

    Returns:
        Metadata fetcher class, or None if not found
    """
    return METADATA_PROVIDERS.get(provider_name)


__all__ = [
    "AbstractMetadataFetcher",
    "FedoraMetadataFetcher",
    "METADATA_PROVIDERS",
    "get_metadata_fetcher",
]
