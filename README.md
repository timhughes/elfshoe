# elfshoe

**Automated iPXE boot menu generation - where elves craft your network boot menus.**

[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://timhughes.github.io/elfshoe/)

## Features


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


## Documentation


## Example Configuration

See `docs/examples/config.yaml` for a complete working example with Fedora, CentOS, Debian, and netboot.xyz.

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits


## Development — running tests with Hatch

Install `hatch` and run the test environments locally. The project provides per-interpreter environments:

```bash
python -m pip install --upgrade pip hatch
# Run tests for a single environment (example: py311)
hatch run -e py311 test

# Or run all supported envs in sequence
hatch run -e py311 test && hatch run -e py312 test && hatch run -e py313 test
```

The GitHub Actions CI runs the test matrix in parallel across Python 3.11–3.13.
- Uses [Hatch](https://hatch.pypa.io/) for modern Python packaging
