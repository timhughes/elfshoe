"""Tests for URL validation functionality."""

from unittest.mock import MagicMock, Mock, patch

from ipxe_menu_gen.core import URLValidator


class TestURLValidator:
    """Tests for URLValidator class."""

    @patch("urllib.request.urlopen")
    def test_check_url_success(self, mock_urlopen):
        """Test successful URL check."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = URLValidator.check_url("http://example.com/test", verbose=False)
        assert result is True

    @patch("urllib.request.urlopen")
    def test_check_url_failure(self, mock_urlopen):
        """Test failed URL check."""
        mock_urlopen.side_effect = Exception("Connection error")

        result = URLValidator.check_url("http://example.com/test", verbose=False)
        assert result is False

    @patch("urllib.request.urlopen")
    def test_verify_boot_files_success(self, mock_urlopen):
        """Test successful boot files verification."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = URLValidator.verify_boot_files(
            "http://example.com", "vmlinuz", "initrd.img", verbose=False
        )
        assert result is True
        assert mock_urlopen.call_count == 2  # kernel and initrd

    @patch("urllib.request.urlopen")
    def test_verify_boot_files_kernel_missing(self, mock_urlopen):
        """Test boot files verification with missing kernel."""
        # First call (kernel) fails, second call (initrd) succeeds
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)

        mock_urlopen.side_effect = [Exception("Not found"), mock_response]

        result = URLValidator.verify_boot_files(
            "http://example.com", "vmlinuz", "initrd.img", verbose=False
        )
        assert result is False
