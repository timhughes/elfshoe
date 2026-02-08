"""Tests for FedoraMetadataFetcher (distributions/fedora.py)."""

import json
from unittest.mock import MagicMock, Mock, patch

import pytest

from elfshoe.distributions.fedora import FedoraMetadataFetcher


@pytest.fixture
def sample_fedora_releases():
    """Sample Fedora releases.json data."""
    return [
        {"version": "40", "variant": "Server", "arch": "x86_64", "link": "..."},
        {"version": "40", "variant": "Server", "arch": "aarch64", "link": "..."},
        {"version": "40", "variant": "Server", "arch": "ppc64le", "link": "..."},
        {"version": "40", "variant": "Workstation", "arch": "x86_64", "link": "..."},
        {"version": "39", "variant": "Server", "arch": "x86_64", "link": "..."},
        {"version": "39", "variant": "Server", "arch": "aarch64", "link": "..."},
        {"version": "38", "variant": "Server", "arch": "x86_64", "link": "..."},
        {"version": "38", "variant": "Server", "arch": "aarch64", "link": "..."},
        {"version": "38", "variant": "Server", "arch": "s390x", "link": "..."},
    ]


class TestFedoraMetadataFetcher:
    """Tests for FedoraMetadataFetcher class."""

    def test_init(self):
        """Test FedoraMetadataFetcher initialization."""
        fetcher = FedoraMetadataFetcher()

        assert fetcher._cache is None
        assert fetcher._cache_url is None

    @patch("urllib.request.urlopen")
    def test_fetch_metadata_success(self, mock_urlopen, sample_fedora_releases):
        """Test _fetch_metadata successfully fetches and caches data."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(sample_fedora_releases).encode()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        fetcher = FedoraMetadataFetcher()
        data = fetcher._fetch_metadata("http://example.com/releases.json")

        assert data == sample_fedora_releases
        assert fetcher._cache == sample_fedora_releases
        assert fetcher._cache_url == "http://example.com/releases.json"

    @patch("urllib.request.urlopen")
    def test_fetch_metadata_caches(self, mock_urlopen, sample_fedora_releases):
        """Test _fetch_metadata uses cache for same URL."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(sample_fedora_releases).encode()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        fetcher = FedoraMetadataFetcher()

        # First call should fetch
        data1 = fetcher._fetch_metadata("http://example.com/releases.json")
        assert mock_urlopen.call_count == 1

        # Second call should use cache
        data2 = fetcher._fetch_metadata("http://example.com/releases.json")
        assert mock_urlopen.call_count == 1  # Still only called once
        assert data1 == data2

    @patch("urllib.request.urlopen")
    def test_fetch_metadata_different_url_no_cache(self, mock_urlopen, sample_fedora_releases):
        """Test _fetch_metadata doesn't use cache for different URL."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(sample_fedora_releases).encode()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        fetcher = FedoraMetadataFetcher()

        # First call
        fetcher._fetch_metadata("http://example.com/releases1.json")
        assert mock_urlopen.call_count == 1

        # Different URL should fetch again
        fetcher._fetch_metadata("http://example.com/releases2.json")
        assert mock_urlopen.call_count == 2

    @patch("urllib.request.urlopen")
    def test_fetch_metadata_network_error(self, mock_urlopen):
        """Test _fetch_metadata handles network errors."""
        mock_urlopen.side_effect = Exception("Network error")

        fetcher = FedoraMetadataFetcher()
        data = fetcher._fetch_metadata("http://example.com/releases.json")

        assert data == []
        assert fetcher._cache is None

    @patch("urllib.request.urlopen")
    def test_fetch_metadata_invalid_json(self, mock_urlopen):
        """Test _fetch_metadata handles invalid JSON."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"invalid json {["
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        fetcher = FedoraMetadataFetcher()
        data = fetcher._fetch_metadata("http://example.com/releases.json")

        assert data == []

    @patch.object(FedoraMetadataFetcher, "_fetch_metadata")
    def test_fetch_versions_default_variant(self, mock_fetch, sample_fedora_releases):
        """Test fetch_versions with default Server variant."""
        mock_fetch.return_value = sample_fedora_releases

        fetcher = FedoraMetadataFetcher()
        versions = fetcher.fetch_versions("http://example.com/releases.json")

        # Should return 3 versions (40, 39, 38) in descending order
        assert len(versions) == 3
        assert versions[0]["version"] == "40"
        assert versions[1]["version"] == "39"
        assert versions[2]["version"] == "38"

        # All should be Server variant
        for version in versions:
            assert version["variant"] == "Server"

    @patch.object(FedoraMetadataFetcher, "_fetch_metadata")
    def test_fetch_versions_sorting(self, mock_fetch, sample_fedora_releases):
        """Test fetch_versions sorts versions in descending order."""
        mock_fetch.return_value = sample_fedora_releases

        fetcher = FedoraMetadataFetcher()
        versions = fetcher.fetch_versions("http://example.com/releases.json")

        # Should be sorted newest first
        assert versions[0]["version"] == "40"
        assert versions[1]["version"] == "39"
        assert versions[2]["version"] == "38"

    @patch.object(FedoraMetadataFetcher, "_fetch_metadata")
    def test_fetch_versions_architecture_grouping(self, mock_fetch, sample_fedora_releases):
        """Test fetch_versions groups architectures by version."""
        mock_fetch.return_value = sample_fedora_releases

        fetcher = FedoraMetadataFetcher()
        versions = fetcher.fetch_versions("http://example.com/releases.json")

        # Version 40 should have 3 architectures
        v40 = [v for v in versions if v["version"] == "40"][0]
        assert set(v40["architectures"]) == {"x86_64", "aarch64", "ppc64le"}

        # Version 38 should have 3 architectures
        v38 = [v for v in versions if v["version"] == "38"][0]
        assert set(v38["architectures"]) == {"x86_64", "aarch64", "s390x"}

    @patch.object(FedoraMetadataFetcher, "_fetch_metadata")
    def test_fetch_versions_custom_variant(self, mock_fetch, sample_fedora_releases):
        """Test fetch_versions with custom variant filter."""
        mock_fetch.return_value = sample_fedora_releases

        fetcher = FedoraMetadataFetcher()
        versions = fetcher.fetch_versions("http://example.com/releases.json", variant="Workstation")

        # Should only return Workstation variant
        assert len(versions) == 1
        assert versions[0]["version"] == "40"
        assert versions[0]["variant"] == "Workstation"
        assert versions[0]["architectures"] == ["x86_64"]

    @patch.object(FedoraMetadataFetcher, "_fetch_metadata")
    def test_fetch_versions_architecture_filter_included(self, mock_fetch, sample_fedora_releases):
        """Test fetch_versions with architectures filter (some available)."""
        mock_fetch.return_value = sample_fedora_releases

        fetcher = FedoraMetadataFetcher()
        versions = fetcher.fetch_versions(
            "http://example.com/releases.json", architectures=["x86_64", "aarch64"]
        )

        # Should only include requested architectures
        for version in versions:
            assert set(version["architectures"]).issubset({"x86_64", "aarch64"})

    @patch.object(FedoraMetadataFetcher, "_fetch_metadata")
    def test_fetch_versions_architecture_filter_unavailable(self, mock_fetch):
        """Test fetch_versions filters out versions when arch not available."""
        # Version that only has ppc64le
        data = [
            {"version": "40", "variant": "Server", "arch": "ppc64le", "link": "..."},
        ]
        mock_fetch.return_value = data

        fetcher = FedoraMetadataFetcher()
        versions = fetcher.fetch_versions(
            "http://example.com/releases.json", architectures=["x86_64", "aarch64"]
        )

        # Version 40 should be filtered out since it doesn't have requested archs
        assert len(versions) == 0

    @patch.object(FedoraMetadataFetcher, "_fetch_metadata")
    def test_fetch_versions_architecture_filter_partial_match(self, mock_fetch):
        """Test fetch_versions with partial architecture match."""
        data = [
            {"version": "40", "variant": "Server", "arch": "x86_64", "link": "..."},
            {"version": "40", "variant": "Server", "arch": "ppc64le", "link": "..."},
        ]
        mock_fetch.return_value = data

        fetcher = FedoraMetadataFetcher()
        versions = fetcher.fetch_versions(
            "http://example.com/releases.json", architectures=["x86_64", "aarch64"]
        )

        # Should include version 40 but only with x86_64 (not ppc64le or missing aarch64)
        assert len(versions) == 1
        assert versions[0]["version"] == "40"
        assert versions[0]["architectures"] == ["x86_64"]

    @patch.object(FedoraMetadataFetcher, "_fetch_metadata")
    def test_fetch_versions_architecture_sorting(self, mock_fetch):
        """Test fetch_versions sorts architectures alphabetically."""
        data = [
            {"version": "40", "variant": "Server", "arch": "s390x", "link": "..."},
            {"version": "40", "variant": "Server", "arch": "aarch64", "link": "..."},
            {"version": "40", "variant": "Server", "arch": "x86_64", "link": "..."},
        ]
        mock_fetch.return_value = data

        fetcher = FedoraMetadataFetcher()
        versions = fetcher.fetch_versions("http://example.com/releases.json")

        # Architectures should be sorted
        assert versions[0]["architectures"] == ["aarch64", "s390x", "x86_64"]

    @patch.object(FedoraMetadataFetcher, "_fetch_metadata")
    def test_fetch_versions_empty_data(self, mock_fetch):
        """Test fetch_versions with empty metadata."""
        mock_fetch.return_value = []

        fetcher = FedoraMetadataFetcher()
        versions = fetcher.fetch_versions("http://example.com/releases.json")

        assert versions == []

    @patch.object(FedoraMetadataFetcher, "_fetch_metadata")
    def test_fetch_versions_no_matching_variant(self, mock_fetch, sample_fedora_releases):
        """Test fetch_versions with variant that doesn't exist."""
        mock_fetch.return_value = sample_fedora_releases

        fetcher = FedoraMetadataFetcher()
        versions = fetcher.fetch_versions("http://example.com/releases.json", variant="NonExistent")

        assert versions == []

    @patch.object(FedoraMetadataFetcher, "_fetch_metadata")
    def test_get_version_architectures(self, mock_fetch, sample_fedora_releases):
        """Test get_version_architectures returns version-arch mapping."""
        mock_fetch.return_value = sample_fedora_releases

        fetcher = FedoraMetadataFetcher()
        version_archs = fetcher.get_version_architectures(
            "http://example.com/releases.json", "Server"
        )

        assert "40" in version_archs
        assert set(version_archs["40"]) == {"x86_64", "aarch64", "ppc64le"}

        assert "39" in version_archs
        assert set(version_archs["39"]) == {"x86_64", "aarch64"}

        assert "38" in version_archs
        assert set(version_archs["38"]) == {"x86_64", "aarch64", "s390x"}

    @patch.object(FedoraMetadataFetcher, "_fetch_metadata")
    def test_get_version_architectures_filtering(self, mock_fetch, sample_fedora_releases):
        """Test get_version_architectures filters by variant."""
        mock_fetch.return_value = sample_fedora_releases

        fetcher = FedoraMetadataFetcher()
        version_archs = fetcher.get_version_architectures(
            "http://example.com/releases.json", "Workstation"
        )

        # Should only have Workstation versions
        assert "40" in version_archs
        assert version_archs["40"] == {"x86_64"}
        assert "39" not in version_archs  # No Workstation version 39

    @patch.object(FedoraMetadataFetcher, "_fetch_metadata")
    def test_get_version_architectures_empty(self, mock_fetch):
        """Test get_version_architectures with no matching variant."""
        mock_fetch.return_value = []

        fetcher = FedoraMetadataFetcher()
        version_archs = fetcher.get_version_architectures(
            "http://example.com/releases.json", "Server"
        )

        assert version_archs == {}

    @patch.object(FedoraMetadataFetcher, "_fetch_metadata")
    def test_get_version_architectures_returns_dict(self, mock_fetch, sample_fedora_releases):
        """Test get_version_architectures returns dict not defaultdict."""
        mock_fetch.return_value = sample_fedora_releases

        fetcher = FedoraMetadataFetcher()
        version_archs = fetcher.get_version_architectures(
            "http://example.com/releases.json", "Server"
        )

        # Should be a regular dict, not a defaultdict
        assert isinstance(version_archs, dict)
        assert type(version_archs).__name__ == "dict"
        # Accessing non-existent key should raise KeyError
        with pytest.raises(KeyError):
            _ = version_archs["999"]

    @patch("urllib.request.urlopen")
    def test_fetch_versions_integration(self, mock_urlopen):
        """Integration test for fetch_versions flow."""
        releases = [
            {"version": "40", "variant": "Server", "arch": "x86_64"},
            {"version": "40", "variant": "Server", "arch": "aarch64"},
            {"version": "39", "variant": "Server", "arch": "x86_64"},
        ]
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(releases).encode()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        fetcher = FedoraMetadataFetcher()
        versions = fetcher.fetch_versions("http://example.com/releases.json")

        # Verify complete flow
        assert len(versions) == 2
        assert versions[0]["version"] == "40"
        assert set(versions[0]["architectures"]) == {"x86_64", "aarch64"}
        assert versions[1]["version"] == "39"
        assert versions[1]["architectures"] == ["x86_64"]

    @patch.object(FedoraMetadataFetcher, "_fetch_metadata")
    def test_fetch_versions_preserves_architecture_order_with_filter(self, mock_fetch):
        """Test fetch_versions maintains filter order when architectures specified."""
        data = [
            {"version": "40", "variant": "Server", "arch": "x86_64"},
            {"version": "40", "variant": "Server", "arch": "aarch64"},
            {"version": "40", "variant": "Server", "arch": "ppc64le"},
        ]
        mock_fetch.return_value = data

        fetcher = FedoraMetadataFetcher()
        # Request in specific order
        versions = fetcher.fetch_versions(
            "http://example.com/releases.json", architectures=["ppc64le", "x86_64"]
        )

        # Should preserve the requested order
        assert versions[0]["architectures"] == ["ppc64le", "x86_64"]
