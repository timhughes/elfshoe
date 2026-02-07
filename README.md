# iPXE Network Boot Menu Generator

A flexible, configuration-driven iPXE boot menu generator with automatic version detection, URL validation, and a modular plugin architecture.

[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://timhughes.github.io/ipxe-menu-gen/)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## ✨ Features

- **🔧 Configuration-driven** - Define distributions and boot options in YAML
- **🔄 Dynamic version detection** - Automatically fetch latest versions from metadata
- **✅ URL validation** - Verify boot files exist before adding to menu
- **📝 Custom templates** - Jinja2-based templates, easy to customize
- **🚀 Fast mode** - Skip validation for quick regeneration
- **🎯 Modular architecture** - Plugin system for adding new distributions

## 🚀 Quick Start

```bash
# Generate menu with validation
make validate

# Fast generation (skip validation)
make fast
```

Or directly:

```bash
python3 -m ipxe_menu_gen
```

## 📦 Installation

**Development:**

```bash
pip install hatch
hatch env create
```

**Production:**

```bash
pip install ipxe-menu-generator
ipxe-menu-gen --help
```

## 🎯 Configuration Example

```yaml
menu:
  title: "Network Boot Menu"
  timeout: 30000

distributions:
  fedora:
    enabled: true
    type: "dynamic"
    metadata_provider: "fedora"
    metadata_url: "https://fedoraproject.org/releases.json"
    url_template: "http://download.fedoraproject.org/pub/fedora/linux/releases/{version}/Server/x86_64/os"
    boot_files:
      kernel: "images/pxeboot/vmlinuz"
      initrd: "images/pxeboot/initrd.img"
```

## 📖 Documentation

Full documentation: **https://timhughes.github.io/ipxe-menu-gen/**

- **[Quick Reference](https://timhughes.github.io/ipxe-menu-gen/quickref/)** - Commands and configuration
- **[Getting Started](https://timhughes.github.io/ipxe-menu-gen/overview/)** - Concepts and overview
- **[Adding Distributions](https://timhughes.github.io/ipxe-menu-gen/developer/adding_distributions/)** - Extend with new OSes
- **[Changelog](https://timhughes.github.io/ipxe-menu-gen/changelog/)** - Version history

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

```bash
make test    # Run tests
make lint    # Check code
make format  # Format code
```

## 📝 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Credits

Built with [Python](https://python.org), [Jinja2](https://jinja.palletsprojects.com/), [PyYAML](https://pyyaml.org/), and [Hatch](https://hatch.pypa.io/).
