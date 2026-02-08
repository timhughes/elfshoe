"""URL validation utilities."""

import sys
import urllib.request


class URLValidator:
    """Validates that URLs are accessible."""

    @staticmethod
    def check_url(url: str, timeout: int = 10, verbose: bool = True) -> bool:
        """Check if a URL is accessible.

        Args:
            url: URL to check
            timeout: Request timeout in seconds
            verbose: Print error messages if True

        Returns:
            True if URL is accessible (200 status), False otherwise
        """
        try:
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=timeout) as response:
                final_url = response.geturl()
                if url.startswith("http://") and final_url.startswith("https://"):
                    if verbose:
                        print(
                            f"  ✗ URL {url} redirects to HTTPS ({final_url}). "
                            "Standard iPXE builds do not support HTTPS!",
                            file=sys.stderr,
                        )
                    return False
                return response.status == 200
        except Exception as e:
            if verbose:
                print(f"  ✗ Failed to access {url}: {e}", file=sys.stderr)
            return False

    @staticmethod
    def verify_boot_files(
        base_url: str, kernel_path: str, initrd_path: str, verbose: bool = True
    ) -> bool:
        """Verify that kernel and initrd files exist.

        Args:
            base_url: Base URL for the distribution
            kernel_path: Relative path to kernel file
            initrd_path: Relative path to initrd file
            verbose: Print status messages if True

        Returns:
            True if both files exist, False otherwise
        """
        kernel_url = f"{base_url}/{kernel_path}"
        initrd_url = f"{base_url}/{initrd_path}"

        kernel_ok = URLValidator.check_url(kernel_url, verbose=verbose)
        initrd_ok = URLValidator.check_url(initrd_url, verbose=verbose)

        return kernel_ok and initrd_ok
