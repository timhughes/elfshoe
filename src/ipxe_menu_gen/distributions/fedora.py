"""Fedora metadata fetcher."""

import json
import sys
import urllib.request
from typing import List

from .base import AbstractMetadataFetcher


class FedoraMetadataFetcher(AbstractMetadataFetcher):
    """Fetches Fedora release metadata from releases.json."""

    def fetch_versions(self, metadata_url: str, **filters) -> List[str]:
        """Fetch Fedora versions from releases.json.

        Args:
            metadata_url: URL to Fedora releases.json
            **filters: Can include 'variant' and 'arch' filters

        Returns:
            List of version strings, sorted descending (newest first)
        """
        variant = filters.get("variant", "Server")
        arch = filters.get("arch", "x86_64")

        try:
            with urllib.request.urlopen(metadata_url, timeout=10) as response:
                data = json.loads(response.read().decode())
        except Exception as e:
            print(f"  ✗ Failed to fetch Fedora metadata: {e}", file=sys.stderr)
            return []

        versions = set()
        for release in data:
            if release.get("variant") == variant and release.get("arch") == arch:
                versions.add(release["version"])

        # Sort numerically, newest first
        return sorted(versions, key=int, reverse=True)
