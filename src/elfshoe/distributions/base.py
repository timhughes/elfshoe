"""Base classes for distribution metadata fetchers."""

from abc import ABC, abstractmethod
from typing import List


class AbstractMetadataFetcher(ABC):
    """Abstract base class for metadata fetchers.

    Each distribution can implement its own metadata fetcher
    by subclassing this and implementing fetch_versions().
    """

    @abstractmethod
    def fetch_versions(self, metadata_url: str, **filters) -> List[str]:
        """Fetch available versions from metadata source.

        Args:
            metadata_url: URL to fetch metadata from
            **filters: Distribution-specific filters (e.g., variant, arch)

        Returns:
            List of version strings, sorted appropriately for the distribution
        """
        pass
