# Changelog

## Version 2.0.0 - Configuration-Driven Rewrite

### Major Changes

- **Complete rewrite** - Moved from shell-out architecture to unified Python program
- **Configuration-driven** - All distributions and options now defined in YAML
- **No more templates** - Menu structure generated programmatically
- **Removed subprocess calls** - Everything in a single process

### Features

- **Flexible configuration** - Users can define custom distributions and boot options
- **Dynamic version detection** - Fedora versions fetched from releases.json
- **URL validation** - Verify boot files exist before including in menu
- **Fast mode** - Skip validation with `--no-validate` flag
- **Better error handling** - Clear messages when URLs fail
- **Makefile** - Convenient shortcuts for common tasks
- **Documentation** - Comprehensive README, quick reference, and examples

### Files

**New:**
- `src/ipxe_menu_gen.py` - Main generator program (16KB, ~500 lines)
- `config.yaml` - Default configuration
- `config.example.yaml` - Example custom configuration
- `Makefile` - Build shortcuts
- `QUICKREF.md` - Quick reference guide
- `CHANGELOG.md` - This file

**Deprecated (kept for reference):**
- `src/generate_fedora_menu.py`
- `src/generate_centos_menu.py`
- `src/generate_debian_menu.py`
- `src/build_menu.py`
- `src/menu.ipxe.template`

### Migration Guide

**Old way:**
```bash
python3 src/build_menu.py
```

**New way:**
```bash
make                                    # or
python3 src/ipxe_menu_gen.py
```

**Adding a distribution (old way):**
- Create new Python generator script
- Update template with placeholder
- Update build_menu.py to call generator

**Adding a distribution (new way):**
- Add entry to config.yaml
- Run `make`

### Breaking Changes

None - `menu.ipxe` output format is compatible with existing iPXE setups.

### Performance

- Validation mode: ~30-45 seconds (with network checks)
- Fast mode: < 1 second (no network checks)

### Requirements

- Python 3.6+
- PyYAML (`pip install pyyaml`)
