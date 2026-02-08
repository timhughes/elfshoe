"""Fedora metadata fetcher."""

import json
import sys
import urllib.request
from typing import List, Dict, Set, Tuple
from collections import defaultdict

from .base import AbstractMetadataFetcher


class FedoraMetadataFetcher(AbstractMetadataFetcher):
    """Fetches Fedora release metadata from releases.json."""
    
    def __init__(self):
        """Initialize fetcher with cache."""
        self._cache = None  # Cache the metadata to avoid multiple fetches
        self._cache_url = None

    def _fetch_metadata(self, metadata_url: str) -> List[Dict]:
        """Fetch and cache metadata.
        
        Args:
            metadata_url: URL to Fedora releases.json
            
        Returns:
            List of release entries
        """
        # Return cached data if same URL
        if self._cache is not None and self._cache_url == metadata_url:
            return self._cache
            
        try:
            with urllib.request.urlopen(metadata_url, timeout=10) as response:
                self._cache = json.loads(response.read().decode())
                self._cache_url = metadata_url
                return self._cache
        except Exception as e:
            print(f"  ✗ Failed to fetch Fedora metadata: {e}", file=sys.stderr)
            return []

    def fetch_versions(self, metadata_url: str, **filters) -> List[str]:
        """Fetch Fedora versions from releases.json.

        Args:
            metadata_url: URL to Fedora releases.json
            **filters: Can include 'variant' filter (arch is ignored for multi-arch support)

        Returns:
            List of version strings, sorted descending (newest first)
        """
        variant = filters.get("variant", "Server")
        data = self._fetch_metadata(metadata_url)

        versions = set()
        for release in data:
            # Only filter by variant, collect all versions regardless of arch
            if release.get("variant") == variant:
                versions.add(release["version"])

        # Sort numerically, newest first
        return sorted(versions, key=int, reverse=True)
    
    def get_version_architectures(self, metadata_url: str, variant: str) -> Dict[str, Set[str]]:
        """Get available architectures for each version of a variant.
        
        Args:
            metadata_url: URL to Fedora releases.json
            variant: Variant name (e.g., "Server")
            
        Returns:
            Dict mapping version -> set of available architectures
            Example: {'43': {'x86_64', 'aarch64', 'ppc64le', 's390x'}}
        """
        data = self._fetch_metadata(metadata_url)
        
        # Group architectures by version
        version_archs = defaultdict(set)
        for release in data:
            if release.get("variant") == variant:
                version = release["version"]
                arch = release["arch"]
                version_archs[version].add(arch)
        
        return dict(version_archs)
