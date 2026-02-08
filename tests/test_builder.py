"""Tests for DistributionBuilder class (builder.py)."""

from unittest.mock import MagicMock, patch

import pytest

from elfshoe.builder import DistributionBuilder
from elfshoe.core import ARCH_ARM64, ARCH_X86_64, BootEntry, DistributionMenu


@pytest.fixture
def basic_static_config():
    """Basic static distribution configuration."""
    return {
        "type": "static",
        "label": "Test Distribution",
        "enabled": True,
        "url_template": "http://example.com/{version}/{arch}",
        "boot_files": {"kernel": "vmlinuz", "initrd": "initrd.img"},
        "boot_params": "console=tty0",
        "versions": [{"version": "1.0", "label": "Test 1.0"}],
    }


@pytest.fixture
def multi_arch_config():
    """Multi-architecture configuration."""
    return {
        "type": "static",
        "label": "Multi-Arch Distribution",
        "enabled": True,
        "architectures": [ARCH_X86_64, ARCH_ARM64],
        "url_template": "http://example.com/{version}/{arch}",
        "boot_files": {"kernel": "vmlinuz", "initrd": "initrd.img"},
        "versions": [{"version": "2.0"}],
    }


@pytest.fixture
def dynamic_config():
    """Dynamic distribution configuration."""
    return {
        "type": "dynamic",
        "label": "Dynamic Distribution",
        "enabled": True,
        "metadata_provider": "fedora",
        "metadata_url": "http://example.com/metadata.json",
        "url_template": "http://example.com/{version}/{arch}",
        "boot_files": {"kernel": "vmlinuz", "initrd": "initrd.img"},
    }


class TestDistributionBuilder:
    """Tests for DistributionBuilder class."""

    def test_init(self):
        """Test DistributionBuilder initialization."""
        config = {"test": "config"}
        builder = DistributionBuilder(config, validate_urls=False, verbose=False)

        assert builder.config == config
        assert builder.validate_urls is False
        assert builder.verbose is False
        assert builder.validation_errors == []

    def test_init_defaults(self):
        """Test DistributionBuilder with default parameters."""
        config = {"test": "config"}
        builder = DistributionBuilder(config)

        assert builder.validate_urls is True
        assert builder.verbose is True

    def test_get_architectures_default(self, basic_static_config):
        """Test _get_architectures returns x86_64 by default."""
        builder = DistributionBuilder({}, validate_urls=False, verbose=False)
        archs = builder._get_architectures("test", basic_static_config)

        assert archs == [ARCH_X86_64]

    def test_get_architectures_list(self, multi_arch_config):
        """Test _get_architectures with list of architectures."""
        builder = DistributionBuilder({}, validate_urls=False, verbose=False)
        archs = builder._get_architectures("test", multi_arch_config)

        assert archs == [ARCH_X86_64, ARCH_ARM64]

    def test_get_architectures_dict(self):
        """Test _get_architectures with dict of architectures."""
        config = {
            "architectures": {
                ARCH_X86_64: {"url_template": "http://example.com/x86"},
                ARCH_ARM64: {"url_template": "http://example.com/arm"},
            }
        }
        builder = DistributionBuilder({}, validate_urls=False, verbose=False)
        archs = builder._get_architectures("test", config)

        assert set(archs) == {ARCH_X86_64, ARCH_ARM64}

    def test_get_arch_map_default(self, basic_static_config):
        """Test _get_arch_map returns default mapping."""
        builder = DistributionBuilder({}, validate_urls=False, verbose=False)
        arch_map = builder._get_arch_map("test", basic_static_config)

        assert ARCH_X86_64 in arch_map
        assert "arm64" in arch_map

    def test_get_arch_map_custom(self):
        """Test _get_arch_map with custom mapping."""
        config = {"arch_map": {ARCH_X86_64: "amd64", ARCH_ARM64: "aarch64"}}
        builder = DistributionBuilder({}, validate_urls=False, verbose=False)
        arch_map = builder._get_arch_map("test", config)

        assert arch_map == {ARCH_X86_64: "amd64", ARCH_ARM64: "aarch64"}

    def test_get_arch_map_from_defaults(self):
        """Test _get_arch_map uses DEFAULT_ARCH_MAPS for known distributions."""
        builder = DistributionBuilder({}, validate_urls=False, verbose=False)
        arch_map = builder._get_arch_map("debian", {})

        # Debian should have a default mapping
        assert arch_map is not None
        assert isinstance(arch_map, dict)

    def test_format_label_basic(self):
        """Test _format_label with basic inputs."""
        builder = DistributionBuilder({}, validate_urls=False, verbose=False)
        label = builder._format_label("Fedora", "39", ARCH_X86_64, {ARCH_X86_64: ARCH_X86_64})

        assert label == "Fedora 39 (x86_64)"

    def test_format_label_with_variant(self):
        """Test _format_label with variant."""
        builder = DistributionBuilder({}, validate_urls=False, verbose=False)
        label = builder._format_label(
            "Fedora", "39", ARCH_X86_64, {ARCH_X86_64: ARCH_X86_64}, variant="Server"
        )

        assert label == "Fedora 39 Server (x86_64)"

    def test_format_label_with_name(self):
        """Test _format_label with name (takes precedence over variant)."""
        builder = DistributionBuilder({}, validate_urls=False, verbose=False)
        label = builder._format_label(
            "Debian",
            "12",
            ARCH_X86_64,
            {ARCH_X86_64: "amd64"},
            variant="Server",
            name="Bookworm",
        )

        assert label == "Debian 12 Bookworm (amd64)"
        assert "Server" not in label

    def test_format_label_with_arch_map(self):
        """Test _format_label uses architecture mapping."""
        builder = DistributionBuilder({}, validate_urls=False, verbose=False)
        label = builder._format_label("Debian", "12", ARCH_X86_64, {ARCH_X86_64: "amd64"})

        assert label == "Debian 12 (amd64)"

    @patch("elfshoe.builder.URLValidator.verify_boot_files")
    def test_build_entry_for_arch_success(self, mock_verify, basic_static_config):
        """Test _build_entry_for_arch builds valid entry."""
        mock_verify.return_value = True
        builder = DistributionBuilder({}, validate_urls=True, verbose=False)

        entry = builder._build_entry_for_arch(
            "test",
            "1.0",
            "Test 1.0 (x86_64)",
            basic_static_config,
            ARCH_X86_64,
            {ARCH_X86_64: ARCH_X86_64},
        )

        assert entry is not None
        assert isinstance(entry, BootEntry)
        assert entry.label == "Test 1.0 (x86_64)"
        assert entry.version == "1.0"
        assert entry.architecture == ARCH_X86_64
        assert "http://example.com/1.0/x86_64/vmlinuz" in entry.kernel_url
        assert "http://example.com/1.0/x86_64/initrd.img" in entry.initrd_url

    @patch("elfshoe.builder.URLValidator.verify_boot_files")
    def test_build_entry_for_arch_validation_failure(self, mock_verify, basic_static_config):
        """Test _build_entry_for_arch returns None when validation fails."""
        mock_verify.return_value = False
        builder = DistributionBuilder({}, validate_urls=True, verbose=False)

        entry = builder._build_entry_for_arch(
            "test",
            "1.0",
            "Test 1.0 (x86_64)",
            basic_static_config,
            ARCH_X86_64,
            {ARCH_X86_64: ARCH_X86_64},
        )

        assert entry is None

    def test_build_entry_for_arch_no_validation(self, basic_static_config):
        """Test _build_entry_for_arch without URL validation."""
        builder = DistributionBuilder({}, validate_urls=False, verbose=False)

        entry = builder._build_entry_for_arch(
            "test",
            "1.0",
            "Test 1.0 (x86_64)",
            basic_static_config,
            ARCH_X86_64,
            {ARCH_X86_64: ARCH_X86_64},
        )

        assert entry is not None
        assert entry.kernel_url == "http://example.com/1.0/x86_64/vmlinuz"
        assert entry.boot_params == "console=tty0"

    def test_build_entry_for_arch_with_boot_params_formatting(self):
        """Test _build_entry_for_arch formats boot_params with base_url."""
        config = {
            "url_template": "http://example.com/{version}",
            "boot_files": {"kernel": "vmlinuz", "initrd": "initrd.img"},
            "boot_params": "inst.repo={base_url}",
        }
        builder = DistributionBuilder({}, validate_urls=False, verbose=False)

        entry = builder._build_entry_for_arch(
            "test", "1.0", "Test", config, ARCH_X86_64, {ARCH_X86_64: ARCH_X86_64}
        )

        assert entry.boot_params == "inst.repo=http://example.com/1.0"

    def test_build_entry_for_arch_per_arch_config(self):
        """Test _build_entry_for_arch with per-architecture config overrides."""
        config = {
            "url_template": "http://example.com/{version}/{arch}",
            "boot_files": {"kernel": "vmlinuz", "initrd": "initrd.img"},
            "architectures": {
                ARCH_X86_64: {"boot_params": "x86_param=1"},
                ARCH_ARM64: {"boot_params": "arm_param=1"},
            },
        }
        builder = DistributionBuilder({}, validate_urls=False, verbose=False)

        entry_x86 = builder._build_entry_for_arch(
            "test", "1.0", "Test", config, ARCH_X86_64, {ARCH_X86_64: ARCH_X86_64}
        )
        entry_arm = builder._build_entry_for_arch(
            "test", "1.0", "Test", config, ARCH_ARM64, {ARCH_ARM64: ARCH_ARM64}
        )

        assert entry_x86.boot_params == "x86_param=1"
        assert entry_arm.boot_params == "arm_param=1"

    @patch("elfshoe.builder.URLValidator.verify_boot_files")
    def test_build_static_distribution_success(self, mock_verify, basic_static_config):
        """Test build_static_distribution builds menu successfully."""
        mock_verify.return_value = True
        builder = DistributionBuilder({}, validate_urls=True, verbose=False)

        menu = builder.build_static_distribution("test", basic_static_config)

        assert menu is not None
        assert isinstance(menu, DistributionMenu)
        assert menu.id == "test_menu"
        assert menu.label == "Test Distribution"
        assert len(menu.entries) == 1
        assert menu.architectures == [ARCH_X86_64]

    @patch("elfshoe.builder.URLValidator.verify_boot_files")
    def test_build_static_distribution_multiple_versions(self, mock_verify):
        """Test build_static_distribution with multiple versions."""
        mock_verify.return_value = True
        config = {
            "label": "Test",
            "url_template": "http://example.com/{version}",
            "boot_files": {"kernel": "vmlinuz", "initrd": "initrd.img"},
            "versions": [{"version": "1.0"}, {"version": "2.0"}, {"version": "3.0"}],
        }
        builder = DistributionBuilder({}, validate_urls=True, verbose=False)

        menu = builder.build_static_distribution("test", config)

        assert menu is not None
        assert len(menu.entries) == 3

    @patch("elfshoe.builder.URLValidator.verify_boot_files")
    def test_build_static_distribution_multiple_architectures(self, mock_verify, multi_arch_config):
        """Test build_static_distribution with multiple architectures."""
        mock_verify.return_value = True
        builder = DistributionBuilder({}, validate_urls=True, verbose=False)

        menu = builder.build_static_distribution("test", multi_arch_config)

        assert menu is not None
        assert len(menu.entries) == 2  # 1 version × 2 archs
        assert set(menu.architectures) == {ARCH_X86_64, ARCH_ARM64}

    @patch("elfshoe.builder.URLValidator.verify_boot_files")
    def test_build_static_distribution_no_valid_entries(self, mock_verify, basic_static_config):
        """Test build_static_distribution returns None when all entries fail validation."""
        mock_verify.return_value = False
        builder = DistributionBuilder({}, validate_urls=True, verbose=False)

        menu = builder.build_static_distribution("test", basic_static_config)

        assert menu is None

    @patch("elfshoe.builder.URLValidator.verify_boot_files")
    def test_build_static_distribution_per_version_architectures(self, mock_verify):
        """Test build_static_distribution with per-version architecture lists."""
        mock_verify.return_value = True
        config = {
            "label": "Test",
            "url_template": "http://example.com/{version}/{arch}",
            "boot_files": {"kernel": "vmlinuz", "initrd": "initrd.img"},
            "versions": [
                {"version": "1.0", "architectures": [ARCH_X86_64]},
                {"version": "2.0", "architectures": [ARCH_X86_64, ARCH_ARM64]},
            ],
        }
        builder = DistributionBuilder({}, validate_urls=True, verbose=False)

        menu = builder.build_static_distribution("test", config)

        assert menu is not None
        assert len(menu.entries) == 3  # 1 + 2 architectures

    @patch("elfshoe.builder.get_metadata_fetcher")
    @patch("elfshoe.builder.URLValidator.verify_boot_files")
    def test_build_dynamic_distribution_success(
        self, mock_verify, mock_get_fetcher, dynamic_config
    ):
        """Test build_dynamic_distribution with successful metadata fetch."""
        mock_verify.return_value = True

        # Mock metadata fetcher
        mock_fetcher_instance = MagicMock()
        mock_fetcher_instance.fetch_versions.return_value = [
            {"version": "39", "variant": "Server", "architectures": [ARCH_X86_64]}
        ]
        mock_fetcher_class = MagicMock(return_value=mock_fetcher_instance)
        mock_get_fetcher.return_value = mock_fetcher_class

        builder = DistributionBuilder({}, validate_urls=True, verbose=False)
        menu = builder.build_dynamic_distribution("fedora", dynamic_config)

        assert menu is not None
        assert len(menu.entries) == 1
        mock_fetcher_instance.fetch_versions.assert_called_once()

    @patch("elfshoe.builder.get_metadata_fetcher")
    def test_build_dynamic_distribution_no_provider(self, mock_get_fetcher):
        """Test build_dynamic_distribution without metadata_provider."""
        config = {"label": "Test"}  # Missing metadata_provider
        builder = DistributionBuilder({}, validate_urls=False, verbose=False)

        menu = builder.build_dynamic_distribution("test", config)

        assert menu is None

    @patch("elfshoe.builder.get_metadata_fetcher")
    def test_build_dynamic_distribution_unknown_provider(self, mock_get_fetcher):
        """Test build_dynamic_distribution with unknown metadata provider."""
        mock_get_fetcher.return_value = None

        config = {"metadata_provider": "unknown", "metadata_url": "http://example.com"}
        builder = DistributionBuilder({}, validate_urls=False, verbose=False)

        menu = builder.build_dynamic_distribution("test", config)

        assert menu is None

    @patch("elfshoe.builder.get_metadata_fetcher")
    def test_build_dynamic_distribution_no_versions(self, mock_get_fetcher, dynamic_config):
        """Test build_dynamic_distribution when no versions are found."""
        mock_fetcher_instance = MagicMock()
        mock_fetcher_instance.fetch_versions.return_value = []
        mock_fetcher_class = MagicMock(return_value=mock_fetcher_instance)
        mock_get_fetcher.return_value = mock_fetcher_class

        builder = DistributionBuilder({}, validate_urls=False, verbose=False)
        menu = builder.build_dynamic_distribution("fedora", dynamic_config)

        assert menu is None

    @patch("elfshoe.builder.URLValidator.verify_boot_files")
    def test_build_distribution_static(self, mock_verify, basic_static_config):
        """Test build_distribution routes to build_static_distribution."""
        mock_verify.return_value = True
        builder = DistributionBuilder({}, validate_urls=True, verbose=False)

        menu = builder.build_distribution("test", basic_static_config)

        assert menu is not None
        assert menu.id == "test_menu"

    @patch("elfshoe.builder.get_metadata_fetcher")
    @patch("elfshoe.builder.URLValidator.verify_boot_files")
    def test_build_distribution_dynamic(self, mock_verify, mock_get_fetcher, dynamic_config):
        """Test build_distribution routes to build_dynamic_distribution."""
        mock_verify.return_value = True
        mock_fetcher_instance = MagicMock()
        mock_fetcher_instance.fetch_versions.return_value = [
            {"version": "39", "architectures": [ARCH_X86_64]}
        ]
        mock_get_fetcher.return_value = MagicMock(return_value=mock_fetcher_instance)

        builder = DistributionBuilder({}, validate_urls=True, verbose=False)
        menu = builder.build_distribution("fedora", dynamic_config)

        assert menu is not None

    def test_build_distribution_disabled(self, basic_static_config):
        """Test build_distribution returns None when distribution is disabled."""
        basic_static_config["enabled"] = False
        builder = DistributionBuilder({}, validate_urls=False, verbose=False)

        menu = builder.build_distribution("test", basic_static_config)

        assert menu is None

    def test_build_distribution_unknown_type(self):
        """Test build_distribution with unknown distribution type."""
        config = {"type": "unknown", "enabled": True}
        builder = DistributionBuilder({}, validate_urls=False, verbose=False)

        menu = builder.build_distribution("test", config)

        assert menu is None

    def test_build_distribution_default_type(self, basic_static_config):
        """Test build_distribution defaults to static type."""
        del basic_static_config["type"]
        builder = DistributionBuilder({}, validate_urls=False, verbose=False)

        with patch.object(builder, "build_static_distribution") as mock_build:
            mock_build.return_value = MagicMock()
            builder.build_distribution("test", basic_static_config)
            mock_build.assert_called_once()
