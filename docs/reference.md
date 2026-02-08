# elfshoe - Reference

## Command-Line Tools

### elfshoe

The `elfshoe` command generates iPXE boot menu scripts from YAML configuration files.

## Command Line Usage

```bash
# Generate menu with validation (recommended)
elfshoe

# Fast generation (no validation)
elfshoe --skip-validation

# Custom config and output files
elfshoe -c custom-config.yaml -o custom-elfshoe.ipxe

# Quiet mode (no output unless errors)
elfshoe --quiet

# Show help
elfshoe --help
```

### Command Options

- `-c, --config FILE` - Path to config file (default: `config.yaml`)
- `-o, --output FILE` - Output file path (default: `elfshoe.ipxe`)
- `--skip-validation` - Skip URL validation for faster generation
- `--quiet` - Quiet mode, only show errors
- `--help` - Show help message

## Command Line Options

```bash
elfshoe [OPTIONS]

Options:
  -c, --config FILE     Configuration file (default: config.yaml)
  -o, --output FILE     Output file (default: elfshoe.ipxe)
  --no-validate         Skip URL validation (faster)
  --quiet              Minimal output
  --help               Show help message
```

### ipxelint

The `ipxelint` tool validates iPXE scripts for syntax errors and common mistakes.

#### Basic Usage

```bash
# Validate a single file
ipxelint elfshoe.ipxe

# Validate multiple files
ipxelint *.ipxe

# Treat warnings as errors (CI-friendly)
ipxelint --strict elfshoe.ipxe

# Only show errors
ipxelint --quiet elfshoe.ipxe
```

#### What It Checks

- **Shebang**: Ensures script starts with `#!ipxe`
- **Menu balance**: Warns if menu/choose statements are unbalanced
- **Label references**: Detects undefined label references in goto statements
- **Command syntax**: Warns about unknown or potentially misspelled commands

#### Exit Codes

- `0`: All files passed validation
- `1`: At least one file had errors (or warnings with `--strict`)

#### Example Output

```
✓ elfshoe.ipxe: OK

⚠️  custom.ipxe: WARNINGS
  Line 12: Unknown or potentially misspelled command: 'slepe'

❌ broken.ipxe: FAILED
  Line 1: Missing or invalid #!ipxe shebang
  Line 15: Reference to undefined label: 'non_existent'
```

## Command Line Options Full Reference

```bash
-c, --config FILE      # Config file (default: config.yaml)
-o, --output FILE      # Output file (default: elfshoe.ipxe)
--no-validate          # Skip URL validation (faster)
-q, --quiet            # Minimal output
--version              # Show version
  -h, --help             # Show help
```

## Configuration File Structure

```yaml
menu:
  title: "Your Menu Title"
  default_item: "distribution_menu"
  timeout: 30000        # Menu timeout (ms)
  error_timeout: 30000  # Error display timeout (ms)

distributions:
  distro_name:
    enabled: true|false
    label: "Display Label"
    type: "static"|"dynamic"
    
    # For static type:
    versions:
      - version: "X"
        label: "Full Label"
    
    # For dynamic type:
    metadata_provider: "provider_name"  # e.g., "fedora"
    metadata_url: "https://..."
    metadata_filter:
      key: value
    
    # Common fields:
    url_template: "http://example.com/{version}/path"
    boot_files:
      kernel: "path/to/vmlinuz"
      initrd: "path/to/initrd.img"
    boot_params: "kernel_params_here"

additional_items:
  - id: "unique_id"
    label: "Display Label"
    type: "chain"|"shell"|"exit"
    url: "http://..."  # for chain type only
```

## URL Templates

Use `{version}` placeholder in URL templates:

```yaml
# Fedora
url_template: "http://download.fedoraproject.org/pub/fedora/linux/releases/{version}/Server/x86_64/os"

# CentOS Stream
url_template: "http://mirror.stream.centos.org/{version}-stream/BaseOS/x86_64/os"

# Debian
url_template: "http://deb.debian.org/debian/dists/{version}/main/installer-amd64/current/images/netboot/debian-installer/amd64"
```

## Boot Parameters

Use `{base_url}` in boot parameters:

```yaml
# Repository installation
boot_params: "inst.repo={base_url}/"

# Network configuration
boot_params: "ip=dhcp inst.repo={base_url}/"

# Text mode
boot_params: "inst.text inst.repo={base_url}/"
```

## Command-Line Options

```bash
-c, --config FILE      # Config file (default: config.yaml)
-o, --output FILE      # Output file (default: elfshoe.ipxe)
--no-validate          # Skip URL validation (faster)
-q, --quiet            # Minimal output
--version              # Show version
-h, --help             # Show help
```

## File Locations

```
Project Root/
├── config.yaml              # Main configuration
├── config.example.yaml      # Example config
├── elfshoe.ipxe                # Generated menu (output)
├── src/elfshoe/       # Package source
│   ├── core/                # Core components
│   ├── distributions/       # Distribution plugins
│   └── templates/           # Jinja2 templates
└── tests/                   # Test suite
```

## Adding a Distribution

### Static (Simple)
Add to `config.yaml`:

```yaml
distributions:
  mylinux:
    enabled: true
    type: "static"
    label: "My Linux"
    versions:
      - version: "1.0"
        label: "My Linux 1.0"
    url_template: "http://mirror.example.com/{version}/os"
    boot_files:
      kernel: "vmlinuz"
      initrd: "initrd.img"
    boot_params: ""
```

### Dynamic Distribution (Automatic Version Detection)

For distributions like Fedora that support automatic version detection:

```yaml
distributions:
  fedora:
    enabled: true
    type: "dynamic"
    label: "Boot Fedora"
    metadata_provider: "fedora"
    metadata_url: "https://fedoraproject.org/releases.json"
    metadata_filter:
      variant: "Server"
      arch: "x86_64"
    url_template: "http://download.fedoraproject.org/pub/fedora/linux/releases/{version}/Server/x86_64/os"
    boot_files:
      kernel: "images/pxeboot/vmlinuz"
      initrd: "images/pxeboot/initrd.img"
    boot_params: "inst.repo={base_url}/"
```

**Note:** To add custom metadata providers, see the [Adding Distributions](developer/adding_distributions.md) guide.

## Troubleshooting

### Menu Generation is Slow

```bash
# Skip URL validation for faster generation (development mode)
elfshoe --skip-validation
# or
elfshoe --no-validate
```

**Tip:** Use validation in production to catch broken URLs, but skip it during development/testing.

### Menu Generation Fails

```bash
# Run with validation to see which URLs are failing
elfshoe

# Test specific URL manually
curl -I http://your-mirror-url/vmlinuz
```

### Boot Files Not Found (404 errors)
- Check that the `url_template` is correct for your mirror
- Verify `boot_files` paths match your distribution's file structure
- Test the full URL: `{url_template}/{kernel_path}`
- Try a different mirror if the current one is down

### iPXE Shows "No Such File"
This usually means:
1. The URL in the generated menu is incorrect
2. The web server hosting the files is not accessible from the client
3. The file paths in `boot_files` don't match the actual file locations

**Solutions:**

```bash
# Regenerate menu with validation to check URLs
elfshoe

# Verify your web server can serve the files
curl http://your-server/path/to/vmlinuz

# Check the generated elfshoe.ipxe file for correct URLs
cat elfshoe.ipxe | grep -A5 "boot_fedora"
```

## Performance

- **With validation**: 30-45 seconds (checks all URLs exist)
- **Without validation**: <1 second (generates menu only)
- **Recommendation**: Use validation before deploying to production

## Version Detection

### Fedora (Dynamic)
- Fetches versions from: `https://fedoraproject.org/releases.json`
- Filters by: `variant=Server`, `arch=x86_64`
- Returns: Latest 3-5 supported versions automatically

### Other Distributions
- CentOS, Debian, Rocky: Use static version lists
- Custom distributions: Can add dynamic metadata providers (see contributor docs)

## iPXE Boot Process

### How It Works
1. Client machine boots via PXE
2. DHCP server provides iPXE binary location
3. iPXE loads and fetches `elfshoe.ipxe` from your web server
4. User selects OS from menu
5. iPXE downloads kernel and initrd
6. Boot proceeds with specified parameters

### Generated Menu Structure

```ipxe
#!ipxe

:start
menu Network Boot Menu
item fedora_38 Fedora 38 Server
choose selected
goto ${selected}

:fedora_38
echo Booting Fedora 38 Server...
initrd http://mirror/fedora/38/images/pxeboot/initrd.img || goto error
kernel http://mirror/fedora/38/images/pxeboot/vmlinuz initrd=initrd.img inst.repo=http://mirror/fedora/38/ || goto error
boot

:error
echo Boot failed!
prompt --timeout ${error_timeout}
goto start
```

### Boot Parameters

Common parameters you can add to `boot_params`:
- **Fedora/RHEL**: `inst.repo={base_url}/ inst.ks=http://server/kickstart.cfg`
- **Debian/Ubuntu**: `auto=true url=http://server/preseed.cfg`
- **Generic**: `console=ttyS0,115200` (for serial console)

### Supported File Types
- **Kernel**: `vmlinuz`, `linux`, `bzImage`
- **Initrd**: `initrd.img`, `initrd.gz`, `initramfs`

## Related Documentation

- [Home](index.md) - Full documentation
- [Getting Started](getting-started.md) - Concepts and overview
- [Contributing](developer/contributing.md) - For contributors
