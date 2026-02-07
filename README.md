# iPXE Network Boot Menu Generator

A flexible, configuration-driven iPXE boot menu generator with automatic version detection and URL validation.

## Features

- **🔧 Configuration-driven** - Define distributions and boot options in YAML
- **🔄 Dynamic version detection** - Automatically fetch latest Fedora versions from metadata
- **✅ URL validation** - Verify boot files exist before adding to menu
- **📝 Custom templates** - Easy to customize for your needs
- **🚀 Fast mode** - Skip validation for quick regeneration
- **🎯 Modular design** - Add/remove distributions easily

## Quick Start

Generate a menu using the default configuration:

```bash
python3 src/ipxe_menu_gen.py
```

This will create `menu.ipxe` with Fedora, CentOS Stream, and Debian options.

## Installation

Required dependencies:
```bash
pip install pyyaml
```

## Usage

```bash
# Basic usage with default config
python3 src/ipxe_menu_gen.py

# Use custom config file
python3 src/ipxe_menu_gen.py -c my-config.yaml

# Custom output file
python3 src/ipxe_menu_gen.py -o custom-menu.ipxe

# Skip URL validation (faster)
python3 src/ipxe_menu_gen.py --no-validate

# Quiet mode
python3 src/ipxe_menu_gen.py --quiet
```

## Configuration

The configuration file (`config.yaml`) defines:

### Menu Settings

```yaml
menu:
  title: "Network Boot Menu"
  default_item: "fedora_menu"
  timeout: 30000  # milliseconds
```

### Distribution Types

#### Static Distributions
For distributions with manually specified versions:

```yaml
distributions:
  debian:
    enabled: true
    label: "Boot Debian (multiple versions)"
    type: "static"
    versions:
      - version: "bookworm"
        label: "Debian 12 Bookworm (Stable)"
      - version: "trixie"
        label: "Debian 13 Trixie (Testing)"
    url_template: "http://deb.debian.org/debian/dists/{version}/main/installer-amd64/current/images/netboot/debian-installer/amd64"
    boot_files:
      kernel: "linux"
      initrd: "initrd.gz"
    boot_params: ""
```

#### Dynamic Distributions
For distributions that fetch versions from metadata:

```yaml
distributions:
  fedora:
    enabled: true
    label: "Boot Fedora (multiple versions)"
    type: "dynamic"
    metadata_url: "https://fedoraproject.org/releases.json"
    metadata_filter:
      variant: "Server"
      arch: "x86_64"
    url_template: "http://download.fedoraproject.org/pub/fedora/linux/releases/{version}/Server/x86_64/os"
    boot_files:
      kernel: "images/pxeboot/vmlinuz"
      initrd: "images/pxeboot/initrd.img"
    boot_params: "inst.repo={base_url}/"
    menu_label: "Fedora {version} Server"
```

### Additional Menu Items

```yaml
additional_items:
  - id: "netboot"
    label: "netboot.xyz"
    type: "chain"
    url: "http://boot.netboot.xyz"
    
  - id: "shell"
    label: "iPXE Shell"
    type: "shell"
    
  - id: "exit"
    label: "Exit to BIOS"
    type: "exit"
```

## Directory Structure

```
├── config.yaml                     # Main configuration
├── config.example.yaml             # Example custom configuration
├── menu.ipxe                       # Generated menu (output)
├── src/
│   ├── ipxe_menu_gen.py           # Main generator program
│   └── [old scripts - deprecated]
└── README.md
```

## Examples

### Example 1: Corporate Internal Network

```yaml
menu:
  title: "Corporate Boot Menu"
  default_item: "ubuntu_menu"
  timeout: 10000

distributions:
  ubuntu:
    enabled: true
    label: "Ubuntu LTS"
    type: "static"
    versions:
      - version: "24.04"
        label: "Ubuntu 24.04 LTS"
    url_template: "http://mirror.internal/ubuntu/{version}/netboot"
    boot_files:
      kernel: "linux"
      initrd: "initrd.gz"
    boot_params: "url=http://preseed.internal/ubuntu.cfg"
```

### Example 2: Multi-Architecture Support

You can create separate configs for different architectures:

```bash
# Generate x86_64 menu
python3 src/ipxe_menu_gen.py -c config-x86_64.yaml -o menu-x86_64.ipxe

# Generate ARM64 menu
python3 src/ipxe_menu_gen.py -c config-arm64.yaml -o menu-arm64.ipxe
```

### Example 3: Fast Development Cycle

When testing configurations, skip validation for speed:

```bash
# Edit config
vim config.yaml

# Quick regeneration (< 1 second)
python3 src/ipxe_menu_gen.py --no-validate --quiet

# Test with iPXE
```

## Adding Custom Distributions

To add a new distribution:

1. Add entry to `config.yaml`:

```yaml
distributions:
  alma:
    enabled: true
    label: "Boot AlmaLinux"
    type: "static"
    versions:
      - version: "9"
        label: "AlmaLinux 9"
    url_template: "http://repo.almalinux.org/almalinux/{version}/BaseOS/x86_64/os"
    boot_files:
      kernel: "images/pxeboot/vmlinuz"
      initrd: "images/pxeboot/initrd.img"
    boot_params: "inst.repo={base_url}/"
```

2. Regenerate menu:

```bash
python3 src/ipxe_menu_gen.py
```

## Troubleshooting

### URLs not validating?

Run with verbose output to see which URLs are failing:

```bash
python3 src/ipxe_menu_gen.py
```

### Want to skip broken URLs?

The generator automatically skips distributions where boot files don't exist. Check the output for "✗" marks.

### Need to use a mirror?

Update the `url_template` in your config to point to your preferred mirror.

## Contributing

See `config.example.yaml` for more configuration examples.

## Legacy Files

The following files in `src/` are deprecated and kept for reference:
- `generate_fedora_menu.py`
- `generate_centos_menu.py`
- `generate_debian_menu.py`
- `build_menu.py`
- `menu.ipxe.template`

Use `ipxe_menu_gen.py` instead.

