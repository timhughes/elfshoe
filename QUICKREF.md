# iPXE Menu Generator - Quick Reference

## Common Commands

```bash
# Generate menu (recommended)
make

# Fast generation (no validation)
make fast

# Show available commands
make help

# Direct invocation
python3 src/ipxe_menu_gen.py
python3 src/ipxe_menu_gen.py --help
```

## Configuration File Structure

```yaml
menu:
  title: "Your Menu Title"
  default_item: "distribution_menu"
  timeout: 30000

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
    metadata_url: "https://..."
    metadata_filter:
      variant: "Server"
      arch: "x86_64"
    
    # Common fields:
    url_template: "http://.../{version}/..."
    boot_files:
      kernel: "path/to/vmlinuz"
      initrd: "path/to/initrd"
    boot_params: "extra boot params"
    menu_label: "Label {version}"

additional_items:
  - id: "item_id"
    label: "Display Label"
    type: "chain"|"shell"|"exit"
    url: "http://..."  # for chain type
```

## Common URL Templates

### Fedora
```
http://download.fedoraproject.org/pub/fedora/linux/releases/{version}/Server/x86_64/os
```

### CentOS Stream
```
http://mirror.stream.centos.org/{version}-stream/BaseOS/x86_64/os
```

### Debian
```
http://deb.debian.org/debian/dists/{version}/main/installer-amd64/current/images/netboot/debian-installer/amd64
```

### Ubuntu
```
http://archive.ubuntu.com/ubuntu/dists/{version}/main/installer-amd64/current/legacy-images/netboot/ubuntu-installer/amd64
```

### Rocky Linux
```
http://download.rockylinux.org/pub/rocky/{version}/BaseOS/x86_64/os
```

### AlmaLinux
```
http://repo.almalinux.org/almalinux/{version}/BaseOS/x86_64/os
```

## Boot File Paths

### RHEL-based (Fedora, CentOS, Rocky, Alma)
```yaml
boot_files:
  kernel: "images/pxeboot/vmlinuz"
  initrd: "images/pxeboot/initrd.img"
boot_params: "inst.repo={base_url}/"
```

### Debian-based (Debian, Ubuntu)
```yaml
boot_files:
  kernel: "linux"
  initrd: "initrd.gz"
boot_params: ""
```

## Tips

1. **Test without validation first** - Use `--no-validate` to quickly test config syntax
2. **Use verbose mode** - Default mode shows which URLs are being checked
3. **Start with examples** - Copy `config.example.yaml` and modify
4. **Check one distro at a time** - Set `enabled: false` for others while testing
5. **Use internal mirrors** - Replace official URLs with your mirror for faster local boots

## Workflow

1. Edit `config.yaml`
2. Run `make fast` to test syntax
3. Run `make` to validate URLs
4. Deploy `menu.ipxe` to your TFTP/HTTP server
5. Test boot

## Troubleshooting

**URLs timing out?**
- Use `--no-validate` flag
- Check your internet connection
- Use closer mirrors

**Distribution not appearing?**
- Check if `enabled: true`
- Verify URL template is correct
- Run with validation to see errors

**Wrong boot files?**
- Check architecture (x86_64 vs aarch64)
- Verify paths on the mirror website
- Some distros use different paths for different releases
