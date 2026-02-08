# elfshoe - Getting Started

This guide walks you through creating your first iPXE boot menu with elfshoe.

## Prerequisites

Before using elfshoe, you need:

1. **Server infrastructure** - DHCP, TFTP, and HTTP servers configured for network booting
   - See the [Server Setup Guide](server-setup.md) for complete instructions
   - Includes getting iPXE boot files, configuring DHCP/TFTP, and setting up HTTP delivery

2. **Python 3.7 or higher** - For running elfshoe
3. **Network boot enabled** - On client machines (BIOS/UEFI settings)

**New to network booting?** Start with the [Server Setup Guide](server-setup.md) to get your infrastructure ready.

## How It Works

1. **Configure** - Define OS distributions in `config.yaml`
2. **Generate** - Run `elfshoe` to create `elfshoe.ipxe`
3. **Deploy** - Serve `elfshoe.ipxe` from your web server
4. **Boot** - Client machines PXE boot and display your menu

## Quick Example

### 1. Create config.yaml

Start with the example configuration:

```bash
# Copy the example config
cp docs/examples/config.yaml config.yaml

# Or view it at: docs/examples/config.yaml
```

**Example configuration:**

```yaml
--8<-- "docs/examples/config.yaml"
```

### 2. Generate menu

```bash
elfshoe
```

### 3. Result

You get a `elfshoe.ipxe` file (91 lines) that looks like:

```ipxe
#!ipxe
dhcp

:start
menu Network Boot Menu
item --gap -- Operating Systems:
item fedora_menu Boot Fedora (multiple versions)
item centos_menu Boot CentOS Stream (multiple versions)
item debian_menu Boot Debian (multiple versions)
item --gap -- Other Options:
item netboot netboot.xyz
item --gap -- Advanced:
item shell iPXE Shell
item exit Exit to BIOS
choose --default fedora_menu --timeout 30000 target && goto ${target}

:fedora_menu
menu Boot Fedora - Select Version
item fedora_43 Boot Fedora (multiple versions) 43
item fedora_42 Boot Fedora (multiple versions) 42
item fedora_41 Boot Fedora (multiple versions) 41
item --gap --
item back_fedora_menu Back to main menu
choose --default fedora_43 target && goto ${target}

:fedora_43
initrd http://download.fedoraproject.org/.../43/.../initrd.img
chain http://download.fedoraproject.org/.../43/.../vmlinuz \
  initrd=initrd.img inst.repo=http://... || goto fedora_menu_error

:fedora_menu_error
echo
echo Boot failed! Press any key to return to menu...
prompt --timeout 30000
goto fedora_menu

# ... similar sections for CentOS and Debian ...

:netboot
chain --autofree http://boot.netboot.xyz || goto start

:shell
shell

:exit
exit
```

The generator creates a hierarchical menu structure with sub-menus for each distribution, error handling, and navigation.

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

- **Fast mode** (`elfshoe --skip-validation`): Skip validation (~1 second)
- **Validated mode** (`elfshoe`): Check all URLs (~30-45 seconds)

Use fast mode during development, validated mode before deployment.

## Architecture Overview

```
config.yaml → Builder → MenuGenerator → elfshoe.ipxe
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
elfshoe --skip-validation

# Check generated menu
cat elfshoe.ipxe

# Validate all URLs work
elfshoe
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

### Deploy Your Menu

Copy the generated `elfshoe.ipxe` to your HTTP server:

```bash
# Example: Copy to nginx web root
sudo cp elfshoe.ipxe /var/www/pxe/

# Or to Apache
sudo cp elfshoe.ipxe /var/www/html/pxe/
```

**Don't have a server set up yet?** See the [Server Setup Guide](server-setup.md) for:
- Installing and configuring DHCP/TFTP servers (dnsmasq, ISC DHCP, Windows)
- Setting up HTTP servers (nginx, Apache)
- Getting iPXE boot files
- Complete deployment instructions

### Test Network Booting

1. **Enable network boot** in your client's BIOS/UEFI settings
2. **Boot the client** - it should:
   - Get an IP from DHCP
   - Download iPXE bootloader via TFTP
   - Load your elfshoe menu via HTTP
   - Display your boot options

### Troubleshooting

**Menu doesn't appear:**
- Verify HTTP server is accessible: `curl http://your-server/elfshoe.ipxe`
- Check client can reach server (ping, firewall rules)
- Review DHCP/TFTP logs

**URLs fail validation:**
- Check mirror URLs are accessible
- Try a different mirror
- Use `--skip-validation` for testing (not recommended for production)

For infrastructure issues, see the [Server Setup Guide - Troubleshooting](server-setup.md#troubleshooting).

### Learn More

- **[Reference](reference.md)** - Complete command and configuration reference
- **[Server Setup](server-setup.md)** - DHCP, TFTP, HTTP configuration details
- **[Adding Distributions](developer/adding_distributions.md)** - Extend with new OSes
- **[Contributing](developer/contributing.md)** - Add features or fix bugs
