"""Tests for MenuGenerator class (core/generator.py)."""

from elfshoe.core import BootEntry, DistributionMenu, MenuGenerator


class TestMenuGenerator:
    """Tests for MenuGenerator class."""

    def test_generate_with_single_distribution(self, sample_config):
        """Test generating menu with one distribution."""
        entry = BootEntry(
            id="test_1",
            label="Test 1",
            kernel_url="http://example.com/vmlinuz1",
            initrd_url="http://example.com/initrd1.img",
            boot_params="param1",
        )
        menu = DistributionMenu(id="test_menu", label="Test Distribution", entries=[entry])

        generator = MenuGenerator(sample_config)
        output = generator.generate([menu])

        assert "#!ipxe" in output
        assert "dhcp" in output
        assert ":start" in output
        assert "Test Menu" in output
        assert "test_menu" in output
        assert ":test_1" in output
        assert "initrd http://example.com/initrd1.img" in output
        assert "chain http://example.com/vmlinuz1" in output

    def test_generate_minimal_menu(self, minimal_config):
        """Test generating a minimal menu."""
        generator = MenuGenerator(minimal_config)
        output = generator.generate([])

        assert "#!ipxe" in output
        assert "Minimal Menu" in output
        assert "shell" in output

    def test_initrd_img_vs_gz(self, sample_config):
        """Test correct initrd naming for .img vs .gz files."""
        entry_img = BootEntry(
            id="test_img",
            label="Test IMG",
            kernel_url="http://example.com/vmlinuz",
            initrd_url="http://example.com/initrd.img",
            boot_params="",
        )
        entry_gz = BootEntry(
            id="test_gz",
            label="Test GZ",
            kernel_url="http://example.com/vmlinuz",
            initrd_url="http://example.com/initrd.gz",
            boot_params="",
        )
        menu = DistributionMenu(id="test_menu", label="Test", entries=[entry_img, entry_gz])

        generator = MenuGenerator(sample_config)
        output = generator.generate([menu])

        # Check .img uses initrd.img
        assert "chain http://example.com/vmlinuz initrd=initrd.img" in output
        # Check .gz uses initrd.gz
        assert "chain http://example.com/vmlinuz initrd=initrd.gz" in output

    def test_error_handlers_included(self, sample_config):
        """Test that error handlers are included."""
        entry = BootEntry(
            id="test_1",
            label="Test 1",
            kernel_url="http://example.com/vmlinuz",
            initrd_url="http://example.com/initrd.img",
            boot_params="",
        )
        menu = DistributionMenu(id="test_menu", label="Test", entries=[entry])

        generator = MenuGenerator(sample_config)
        output = generator.generate([menu])

        # Check distribution error handler
        assert ":test_menu_error" in output
        assert "echo Boot failed!" in output
        # Timeout should match config (10000 from sample_config)
        assert "prompt --timeout 10000" in output
        assert "goto test_menu" in output

    def test_chain_error_handler(self):
        """Test chain error handler for additional items."""
        config = {
            "menu": {"title": "Test", "default_item": "shell", "timeout": 5000},
            "distributions": {},
            "additional_items": [
                {
                    "id": "netboot",
                    "label": "Netboot",
                    "type": "chain",
                    "url": "http://boot.netboot.xyz",
                },
                {"id": "shell", "label": "Shell", "type": "shell"},
            ],
        }

        generator = MenuGenerator(config)
        output = generator.generate([])

        assert ":netboot" in output
        assert "chain --autofree http://boot.netboot.xyz || goto chain_error" in output
        assert ":chain_error" in output
        assert "echo Chain load failed!" in output
