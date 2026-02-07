# Getting Started

## What is iPXE Menu Generator?

iPXE Menu Generator creates bootable network menus for iPXE. Point users to operating system installers (Fedora, CentOS, Debian) or tools (netboot.xyz) via PXE network boot.

## How It Works

1. **Configure** - Define OS distributions in `config.yaml`
2. **Generate** - Run `ipxe-menu-gen` to create `menu.ipxe`
3. **Deploy** - Serve `menu.ipxe` from your web server
4. **Boot** - Client machines PXE boot and display your menu

## Quick Example

### 1. Create config.yaml

```yaml
menu:
  title: "Boot Menu"
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
    boot_params: "inst.repo={base_url}/"
```

### 2. Generate menu

```bash
ipxe-menu-gen
```

### 3. Result

You get a `menu.ipxe` file that looks like:

```ipxe
#!ipxe

:start
menu Boot Menu
item fedora_40 Fedora 40 Server
item fedora_39 Fedora 39 Server
choose selected
goto ${selected}

:fedora_40
echo Booting Fedora 40 Server...
initrd http://download.fedoraproject.org/...initrd.img
kernel http://download.fedoraproject.org/...vmlinuz initrd=initrd.img inst.repo=...
boot
```

## Key Concepts

### Static vs Dynamic Distributions

**Static** - You specify versions manually:
```yaml
distributions:
  debian:
    type: "static"
    versions:
      - version: "bookworm"
        label: "Debian 12"
```

**Dynamic** - Versions fetched automatically from metadata:
```yaml
distributions:
  fedora:
    type: "dynamic"
    metadata_provider: "fedora"
    metadata_url: "https://fedoraproject.org/releases.json"
```

### URL Validation

By default, the generator checks that kernel/initrd files exist before adding them to the menu:

- **Fast mode** (`ipxe-menu-gen --skip-validation`): Skip validation (~1 second)
- **Validated mode** (`ipxe-menu-gen`): Check all URLs (~30-45 seconds)

Use fast mode during development, validated mode before deployment.

## Architecture Overview

```
config.yaml → Builder → MenuGenerator → menu.ipxe
                ↓
          [Validator]
                ↓
       [MetadataFetchers]
```

For detailed architecture, see [Architecture Documentation](developer/architecture.md).

## Common Workflows

### Adding a New Distribution

**Option 1: Static** (simple)
```yaml
distributions:
  rocky:
    enabled: true
    type: "static"
    versions:
      - version: "9"
        label: "Rocky Linux 9"
    url_template: "http://mirror.example.com/rocky/{version}/os"
    boot_files:
      kernel: "images/pxeboot/vmlinuz"
      initrd: "images/pxeboot/initrd.img"
```

**Option 2: Dynamic** (advanced)

See [Adding Distributions](developer/adding_distributions.md) for creating metadata fetcher plugins.

### Customizing Boot Parameters

```yaml
boot_params: "console=ttyS0,115200 inst.ks=http://server/kickstart.cfg"
```

### Testing Your Menu

```bash
# Quick test without validation
ipxe-menu-gen --skip-validation

# Check generated menu
cat menu.ipxe

# Validate all URLs work
ipxe-menu-gen
```

## Performance

- **Without validation**: <1 second
- **With validation**: 30-45 seconds (depends on network/mirrors)
- **URL checks**: Parallel HEAD requests with 10s timeout

## Security

- **No code execution** - Config is pure YAML data, no code
- **Safe YAML parsing** - Uses `yaml.safe_load()` only
- **URL validation** - Prevents broken links in menus
- **Timeouts** - All HTTP requests have 10 second timeouts

## Next Steps

- **[Quick Reference](reference.md)** - Commands and configuration reference
- **[Adding Distributions](developer/adding_distributions.md)** - Extend with new OSes
- **[Architecture](developer/architecture.md)** - System design details
- **[Troubleshooting](reference.md#troubleshooting)** - Common issues and solutions

## Need Help?

- Check the [Quick Reference](reference.md) for common commands
- Review [Troubleshooting](reference.md#troubleshooting) for common issues
- See [Contributing](developer/contributing.md) if you want to add features
