# elfshoe

**Automated iPXE boot menu generation - where elves craft your network boot menus.**

[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://timhughes.github.io/elfshoe/)
[![PyPI version](https://img.shields.io/pypi/v/elfshoe)](https://pypi.org/p/elfshoe)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/elfshoe)](https://pypi.org/p/elfshoe)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/elfshoe)](https://pypi.org/p/elfshoe)

## Features

- **🔧 Configuration-driven** - Define distributions and boot options in YAML
- **🏗️ Multi-architecture support** - Automatic x86_64, ARM64, i386, ARM filtering per client
- **🔄 Dynamic version detection** - Automatically fetch latest versions from metadata
- **✅ URL validation** - Verify boot files exist before adding to menu
- **📝 Custom templates** - Jinja2-based templates, easy to customize
- **🚀 Fast mode** - Skip validation for quick regeneration
- **🎯 Modular architecture** - Plugin system for adding new distributions
- **🏗️ Modern build system** - Uses Hatch for packaging and environments

## Quick Start

```bash
# 1. Copy example configuration
cp docs/examples/config.yaml config.yaml

# 2. Generate menu
elfshoe

# 3. Deploy to your HTTP server
sudo cp elfshoe.ipxe /var/www/pxe/
```

## Installation

### From PyPI

```bash
pip install elfshoe
```

### From Source

```bash
# Clone repository
git clone https://github.com/timhughes/elfshoe.git
cd elfshoe

# Install with pip
pip install -e .

# Or use hatch
hatch shell
```

### Requirements

- Python >= 3.7
- PyYAML >= 6.0
- Jinja2 >= 3.0

## Documentation

- **[Getting Started](https://timhughes.github.io/elfshoe/getting-started/)** - Create your first boot menu
- **[Server Setup](https://timhughes.github.io/elfshoe/server-setup/)** - Configure DHCP, TFTP, and HTTP infrastructure
- **[Reference](https://timhughes.github.io/elfshoe/reference/)** - Commands and configuration
- **[Architecture](https://timhughes.github.io/elfshoe/developer/architecture/)** - Technical design

## Example Configuration

See `docs/examples/config.yaml` for a complete working example with Fedora, CentOS, Debian, and netboot.xyz.

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

- Built with [iPXE](https://ipxe.org/) - open source network boot firmware
- Uses [Hatch](https://hatch.pypa.io/) for modern Python packaging
