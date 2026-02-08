# elfshoe - Getting Started

This guide walks you through creating your first iPXE boot menu with elfshoe.

## Prerequisites

Before using elfshoe, you need:

1. **Server infrastructure** - DHCP, TFTP, and HTTP servers configured for network booting
   - See the [Server Setup Guide](server-setup.md) for complete instructions
   - Includes getting iPXE boot files, configuring DHCP/TFTP, and setting up HTTP delivery

2. **Python 3.10 or higher** - For running elfshoe (it probably works on earlier but is untested)
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

You get a `elfshoe.ipxe` file that looks like:

```ipxe
#!ipxe
dhcp

:start
menu Network Boot Menu
item --gap -- Operating Systems:
item fedora_menu Fedora
item centos_menu CentOS Stream
item debian_menu Debian
item --gap -- Other Options:
item netboot netboot.xyz
item --gap -- Advanced:
item shell iPXE Shell
item exit Exit to BIOS
choose --default fedora_menu --timeout 30000 target && goto ${target}

:fedora_menu
# Architecture-aware menu - shows only matching client architecture
menu Fedora - Select Version
iseq ${buildarch} x86_64 && item fedora_43_x86_64 Fedora 43 Server (x86_64) ||
iseq ${buildarch} arm64 && item fedora_43_arm64 Fedora 43 Server (aarch64) ||
iseq ${buildarch} x86_64 && item fedora_42_x86_64 Fedora 42 Server (x86_64) ||
iseq ${buildarch} arm64 && item fedora_42_arm64 Fedora 42 Server (aarch64) ||
item --gap --
item back_fedora_menu Back to main menu
choose --default fedora_43_x86_64 target && goto ${target}

:fedora_43_x86_64
initrd http://download.fedoraproject.org/pub/fedora/linux/releases/43/Server/x86_64/os/images/pxeboot/initrd.img
chain http://download.fedoraproject.org/pub/fedora/linux/releases/43/Server/x86_64/os/images/pxeboot/vmlinuz initrd=initrd.img inst.repo=http://download.fedoraproject.org/pub/fedora/linux/releases/43/Server/x86_64/os/ || goto fedora_menu_error

:fedora_43_arm64
initrd http://download.fedoraproject.org/pub/fedora/linux/releases/43/Server/aarch64/os/images/pxeboot/initrd.img
chain http://download.fedoraproject.org/pub/fedora/linux/releases/43/Server/aarch64/os/images/pxeboot/vmlinuz initrd=initrd.img inst.repo=http://download.fedoraproject.org/pub/fedora/linux/releases/43/Server/aarch64/os/ || goto fedora_menu_error

# ... similar sections for other versions ...
```

**Key features:**
- **Architecture-aware menus** - x86_64 clients only see x86_64 options, ARM64 clients only see ARM64 options
- **Automatic filtering** - Uses iPXE's `iseq ${buildarch}` to show only compatible entries
- **Human-friendly labels** - "Fedora 43 Server (x86_64)" clearly shows what you're booting
- **Error handling** - Built-in navigation and error recovery

## Key Concepts

### Architecture Support

elfshoe automatically handles multiple CPU architectures (x86_64, ARM64, etc.) with smart client filtering:

**What you configure:**
```yaml
distributions:
  fedora:
    type: dynamic
    metadata_filter:
      variant: Server
      architectures: [x86_64, aarch64]  # Fetch both architectures
    arch_map:
      arm64: aarch64  # Map iPXE's arm64 to Fedora's aarch64
```

**What clients see:**

*x86_64 client menu:*
```
Fedora - Select Version
  • Fedora 43 Server (x86_64)
  • Fedora 42 Server (x86_64)
  • Fedora 41 Server (x86_64)
```

*ARM64 client menu:*
```
Fedora - Select Version
  • Fedora 43 Server (aarch64)
  • Fedora 42 Server (aarch64)
  • Fedora 41 Server (aarch64)
```

**How it works:**
- Uses iPXE's `${buildarch}` variable to detect client architecture
- `iseq ${buildarch} x86_64 && item ...` shows items only to matching clients
- No wrong architecture served - clients only see what works for them

**Supported architectures:**
- `x86_64` - 64-bit x86 (most common)
- `arm64` - 64-bit ARM (Raspberry Pi 4, Apple Silicon, etc.)
- `i386` - 32-bit x86 (legacy)
- `arm` - 32-bit ARM (older devices)

### Static vs Dynamic Distributions

**Static** - You specify versions and architectures manually:
```yaml
distributions:
  debian:
    type: "static"
    arch_map:
      x86_64: amd64  # Map iPXE names to Debian names
    versions:
      - version: "bookworm"
        name: "12 Bookworm"
        architectures: [x86_64, arm64]
```

**Dynamic** - Versions and architectures fetched automatically from metadata:
```yaml
distributions:
  fedora:
    type: "dynamic"
    metadata_provider: "fedora"
    metadata_url: "https://fedoraproject.org/releases.json"
    metadata_filter:
      variant: Server
      architectures: [x86_64, aarch64]
```

### URL Validation

By default, the generator checks that kernel/initrd files exist before adding them to the menu:

- **Fast mode** (`elfshoe --no-validate`): Skip validation (~1 second)
- **Validated mode** (`elfshoe`): Check all URLs (~30-45 seconds)

Use fast mode during development, validated mode before deployment.

**Note:** With multi-architecture support, each architecture is validated separately, so validation may take longer for distributions with multiple architectures.

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
    label: "Rocky Linux"
    arch_map:
      arm64: aarch64  # Map architecture names if needed
    versions:
      - version: "9"
        label: "Rocky Linux 9"
        architectures: [x86_64, arm64]  # Optional: specify per version
    url_template: "http://mirror.example.com/rocky/{version}/BaseOS/{arch}/os"
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
