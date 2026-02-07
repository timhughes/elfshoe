"""Unit tests for iPXE menu generator core functionality."""

from ipxe_menu_gen.core import BootEntry, DistributionMenu


class TestBootEntry:
    """Tests for BootEntry dataclass."""

    def test_boot_entry_creation(self, boot_entry_data):
        """Test creating a boot entry."""
        entry = BootEntry(**boot_entry_data)
        assert entry.id == "test_entry"
        assert entry.label == "Test Entry"
        assert entry.kernel_url == "http://example.com/vmlinuz"
        assert entry.initrd_url == "http://example.com/initrd.img"
        assert entry.boot_params == "test=param"


class TestDistributionMenu:
    """Tests for DistributionMenu dataclass."""

    def test_distribution_menu_creation(self):
        """Test creating a distribution menu."""
        entry = BootEntry(
            id="test",
            label="Test",
            kernel_url="http://example.com/vmlinuz",
            initrd_url="http://example.com/initrd.img",
            boot_params="",
        )
        menu = DistributionMenu(id="test_menu", label="Test Menu", entries=[entry])
        assert menu.id == "test_menu"
        assert menu.label == "Test Menu"
        assert len(menu.entries) == 1
        assert menu.entries[0].id == "test"
