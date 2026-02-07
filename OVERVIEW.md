# iPXE Menu Generator - System Overview

## What This Does

Generates iPXE boot menu files from YAML configuration files, with automatic version detection and URL validation for multiple Linux distributions.

## Architecture

```
┌─────────────────┐
│   config.yaml   │  User configuration
└────────┬────────┘
         │
         v
┌─────────────────────────────────────┐
│   ipxe_menu_gen.py (main program)   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  Configuration Loader       │   │
│  │  (YAML parser)              │   │
│  └──────────┬──────────────────┘   │
│             │                       │
│             v                       │
│  ┌─────────────────────────────┐   │
│  │  Distribution Builder       │   │
│  │  • Static versions          │   │
│  │  • Dynamic version fetch    │   │
│  │  • URL validation           │   │
│  └──────────┬──────────────────┘   │
│             │                       │
│             v                       │
│  ┌─────────────────────────────┐   │
│  │  Menu Generator             │   │
│  │  • Main menu                │   │
│  │  • Submenus                 │   │
│  │  • Boot entries             │   │
│  └──────────┬──────────────────┘   │
└─────────────┼───────────────────────┘
              │
              v
      ┌───────────────┐
      │  menu.ipxe    │  Generated output
      └───────────────┘
```

## Key Components

### 1. Configuration System (`config.yaml`)
- Declarative YAML format
- Supports static and dynamic distribution types
- Customizable boot parameters
- Additional menu items (netboot.xyz, shell, etc.)

### 2. Distribution Builder
- **Static Type**: Manually defined versions
- **Dynamic Type**: Fetches versions from metadata (Fedora releases.json)
- URL validation to verify boot files exist
- Flexible URL templating

### 3. Menu Generator
- Generates main menu with distribution list
- Creates submenus for each distribution
- Handles boot entries with proper initrd detection
- Supports custom additional items

## Data Flow

1. **Load Config** → Parse `config.yaml`
2. **For Each Distribution**:
   - Fetch versions (static list or dynamic query)
   - Build URL for each version
   - Validate boot files exist (optional)
   - Create boot entry objects
3. **Generate iPXE Code**:
   - Main menu
   - Distribution submenus
   - Boot entry labels
   - Additional items
4. **Write Output** → `menu.ipxe`

## Extension Points

### Adding a New Distribution

1. Add to `config.yaml`:
```yaml
distributions:
  your_distro:
    enabled: true
    type: "static"
    versions: [...]
    url_template: "..."
    boot_files: {...}
```

2. Run generator:
```bash
make
```

### Adding a New Metadata Source

1. Create fetcher class in `ipxe_menu_gen.py`:
```python
class YourDistroMetadataFetcher:
    @staticmethod
    def fetch_versions(url):
        # Implementation
        return versions
```

2. Add to `build_dynamic_distribution`:
```python
if 'yourdistro.org' in metadata_url:
    versions = YourDistroMetadataFetcher.fetch_versions(...)
```

### Custom Boot Parameters

Add to distribution config:
```yaml
boot_params: "custom=param other={base_url}/path"
```

Variables available:
- `{base_url}` - The base URL for the version
- `{version}` - The version number

## Performance Characteristics

| Mode | Time | Network Requests | Use Case |
|------|------|-----------------|----------|
| Full validation | 30-45s | ~20-30 | Production deployment |
| No validation | <1s | 1 (metadata only) | Development/testing |

## Security Considerations

- **URL validation** prevents broken boot entries
- **No code execution** from config (pure data)
- **YAML safe_load** prevents arbitrary code execution
- All HTTP requests have timeouts

## Future Enhancements

Potential improvements:
- [ ] Support for ARM architectures
- [ ] Caching of metadata queries
- [ ] Custom templates support
- [ ] More metadata sources (Ubuntu, Arch)
- [ ] Automated testing suite
- [ ] CI/CD integration examples

## Dependencies

- Python 3.6+
- PyYAML library
- urllib (standard library)

## File Size

- Generator: ~16KB (~500 lines)
- Config: ~2KB
- Output: ~3-5KB (varies by distributions)

## Comparison with Previous Version

| Aspect | V1 (Template) | V2 (Config) |
|--------|---------------|-------------|
| Architecture | Multiple scripts + template | Single program |
| Configuration | Code changes needed | YAML file |
| Extension | Write Python | Edit YAML |
| Subprocess calls | Yes (3) | No |
| Performance | ~1s (fast only) | <1s (fast), ~30s (validated) |
| Lines of code | ~250 (3 scripts + template) | ~500 (1 program) |
| User complexity | High | Low |
