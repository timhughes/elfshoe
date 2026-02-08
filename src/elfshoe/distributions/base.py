"""Base classes for distribution metadata fetchers."""

from abc import ABC, abstractmethod
from typing import List


class AbstractMetadataFetcher(ABC):
    """Abstract base class for metadata fetchers.

    Each distribution can implement its own metadata fetcher
    by subclassing this and implementing fetch_versions().
    """

    @abstractmethod
    def fetch_versions(self, metadata_url: str, **filters) -> List[dict]:
        """Fetch available versions from metadata source.

        Args:
            metadata_url: URL to fetch metadata from
            **filters: Distribution-specific filters (e.g., variant, architectures)

        Returns:
            List of version objects (dicts with version, variant, name, architectures)
            Example: [
                {"version": "43", "variant": "Server", "architectures": ["x86_64", "aarch64"]},
                {"version": "42", "variant": "Server", "architectures": ["x86_64", "aarch64"]}
            ]
        """
        pass
