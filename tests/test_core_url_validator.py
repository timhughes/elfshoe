"""Tests for URLValidator class (core/validator.py)."""

from unittest.mock import MagicMock, Mock, patch

from elfshoe.core import URLValidator


class TestURLValidator:
    """Tests for URLValidator class."""

    @patch("urllib.request.urlopen")
    def test_check_url_success(self, mock_urlopen):
        """Test successful URL check."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.geturl.return_value = "http://example.com/test"
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
    def test_check_url_https_redirect(self, mock_urlopen):
        """Test URL check detects HTTP to HTTPS redirect."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.geturl.return_value = "https://example.com/test"
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = URLValidator.check_url("http://example.com/test", verbose=False)
        assert result is False

    @patch("urllib.request.urlopen")
    def test_verify_boot_files_success(self, mock_urlopen):
        """Test successful boot files verification."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.geturl.side_effect = [
            "http://example.com/vmlinuz",
            "http://example.com/initrd.img",
        ]
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
