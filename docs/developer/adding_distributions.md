# Adding New Distribution Support

This guide explains how to add support for new operating systems and distributions.

## Quick Start

To add a new distribution, you have two options:

### Option 1: Static Distribution (Simple)

Use this when you have a fixed list of versions. Just add to `config.yaml`:

```yaml
distributions:
  your_distro:
    enabled: true
    label: "Your Distribution"
    type: "static"
    versions:
      - version: "1.0"
        label: "Your Distro 1.0"
    url_template: "http://mirror.example.com/{version}/os"
    boot_files:
      kernel: "vmlinuz"
      initrd: "initrd.img"
    boot_params: ""
```

No Python code needed!

### Option 2: Dynamic Distribution (Advanced)

Use this when you want to automatically fetch available versions from a metadata source.

**Step 1:** Create `src/elfshoe/distributions/yourdistro.py`:

```python
"""Your Distribution metadata fetcher."""

import json
import sys
import urllib.request
from typing import List

from .base import AbstractMetadataFetcher


class YourDistroMetadataFetcher(AbstractMetadataFetcher):
    """Fetches version information for Your Distribution."""""

    def fetch_versions(self, metadata_url: str, **filters) -> List[str]:
        """Fetch versions from metadata source.

        Args:
            metadata_url: URL to fetch metadata from
            **filters: Custom filters (e.g., variant, arch)

        Returns:
            List of version strings, sorted appropriately
        """
        try:
            with urllib.request.urlopen(metadata_url, timeout=10) as response:
                data = json.loads(response.read().decode())
        except Exception as e:
            print(f"  ✗ Failed to fetch metadata: {e}", file=sys.stderr)
            return []

        # Parse your metadata format
        versions = []
        for release in data:
            # Extract version based on your metadata structure
            versions.append(release['version'])

        # Sort appropriately for your distribution
        return sorted(versions, reverse=True)
```

**Step 2:** Register in `src/elfshoe/distributions/__init__.py`:

```python
from .yourdistro import YourDistroMetadataFetcher

METADATA_PROVIDERS = {
    'fedora': FedoraMetadataFetcher,
    'yourdistro': YourDistroMetadataFetcher,  # Add this line
}
```

**Step 3:** Add to `config.yaml`:

```yaml
distributions:
  your_distro:
    enabled: true
    label: "Your Distribution"
    type: "dynamic"
    metadata_provider: "yourdistro"  # Must match registry key
    metadata_url: "http://example.com/metadata.json"
    metadata_filter:  # Optional, passed to fetch_versions()
      arch: "x86_64"
    url_template: "http://mirror.example.com/{version}/os"
    boot_files:
      kernel: "vmlinuz"
      initrd: "initrd.img"
    boot_params: ""
```

## Real-World Examples

### Windows PE (Static)

```yaml
distributions:
  windows_pe:
    enabled: true
    label: "Windows PE"
    type: "static"
    versions:
      - version: "11"
        label: "Windows 11 PE"
      - version: "10"
        label: "Windows 10 PE"
    url_template: "http://your-server.local/winpe/{version}"
    boot_files:
      kernel: "wimboot"
      initrd: "boot.wim"
    boot_params: ""
```

### FreeBSD (Dynamic)

Create `src/distributions/freebsd.py`:

```python
"""FreeBSD metadata fetcher."""

import re
import sys
import urllib.request
from typing import List

from .base import AbstractMetadataFetcher


class FreeBSDMetadataFetcher(AbstractMetadataFetcher):
    """Fetches FreeBSD release information."""

    def fetch_versions(self, metadata_url: str, **filters) -> List[str]:
        """Fetch FreeBSD versions from FTP directory listing."""
        try:
            with urllib.request.urlopen(metadata_url, timeout=10) as response:
                html = response.read().decode()
        except Exception as e:
            print(f"  ✗ Failed to fetch FreeBSD metadata: {e}", file=sys.stderr)
            return []

        # Parse FTP directory listing for release versions
        versions = []
        for match in re.finditer(r'(\d+\.\d+)-RELEASE', html):
            versions.append(match.group(1))

        # Sort by version number, newest first
        return sorted(set(versions), key=lambda v: tuple(map(int, v.split('.'))),
                     reverse=True)
```

Then configure:

```yaml
distributions:
  freebsd:
    enabled: true
    label: "FreeBSD"
    type: "dynamic"
    metadata_provider: "freebsd"
    metadata_url: "http://ftp.freebsd.org/pub/FreeBSD/releases/amd64/amd64/"
    url_template: "http://ftp.freebsd.org/pub/FreeBSD/releases/amd64/amd64/{version}-RELEASE"
    boot_files:
      kernel: "kernel.txz"
      initrd: "base.txz"
    boot_params: ""
```

## Testing Your Distribution

1. **Test with validation disabled** (fast iteration):

   ```bash
   make fast
   # or
   python3 -m elfshoe --no-validate
   ```

2. **Test with URL validation** (verify files exist):

   ```bash
   make validate
   # or
   python3 -m elfshoe
   ```

3. **Write unit tests** in `tests/test_distributions.py`:

   ```python
   from elfshoe.distributions import YourDistroMetadataFetcher

   def test_fetch_versions():
       fetcher = YourDistroMetadataFetcher()
       versions = fetcher.fetch_versions("http://example.com/metadata.json")
       assert len(versions) > 0
       assert all(isinstance(v, str) for v in versions)
   ```

## Architecture Overview

```
src/
└── elfshoe/            # Main package
    ├── cli.py                # Command-line interface
    ├── builder.py            # DistributionBuilder - orchestration
    ├── core/
    │   ├── models.py         # BootEntry, DistributionMenu
    │   ├── validator.py      # URL validation
    │   └── generator.py      # Jinja2 menu generation
    └── distributions/
        ├── base.py           # AbstractMetadataFetcher (interface)
        ├── __init__.py       # Registry (METADATA_PROVIDERS)
        ├── fedora.py         # Fedora implementation
        └── yourdistro.py     # Your implementation
```

## Best Practices

1. **Error Handling**: Always catch exceptions when fetching metadata
2. **Timeouts**: Use reasonable timeouts (10 seconds) for network requests
3. **Sorting**: Sort versions appropriately (newest first for most distros)
4. **Filtering**: Support optional filters via `**filters` parameter
5. **Testing**: Test with both real and mock metadata sources

## Need Help?

- Look at `src/distributions/fedora.py` for a complete example
- Check existing distribution configs in `config.yaml`
- Run tests: `make test`
- Ask in issues/discussions
