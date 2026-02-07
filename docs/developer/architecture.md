# Architecture Documentation

## Overview

The iPXE Menu Generator uses a modular, plugin-based architecture that separates concerns and makes it easy to extend with new distributions.

## Directory Structure

```
ipxe/
├── src/
│   └── ipxe_menu_gen/                # Main package
│       ├── __init__.py               # Package exports
│       ├── __main__.py               # Module entry point (python -m)
│       ├── cli.py                    # Command-line interface
│       ├── builder.py                # DistributionBuilder class
│       ├── core/                     # Core functionality
│       │   ├── __init__.py           # Package exports
│       │   ├── models.py             # Data models (BootEntry, DistributionMenu)
│       │   ├── validator.py          # URL validation
│       │   └── generator.py          # Jinja2 menu generation
│       ├── distributions/            # Distribution-specific modules
│       │   ├── __init__.py           # Provider registry
│       │   ├── base.py               # AbstractMetadataFetcher interface
│       │   ├── fedora.py             # Fedora implementation
│       │   └── [future: centos.py, debian.py, windows.py, ...]
│       └── templates/                # Jinja2 templates
│           ├── main_menu.ipxe.j2
│           ├── distribution_submenus.ipxe.j2
│           └── additional_items.ipxe.j2
├── tests/                            # Test suite
│   ├── conftest.py                   # Pytest fixtures
│   ├── test_ipxe_menu_gen.py        # Model tests
│   ├── test_url_validator.py        # Validation tests
│   └── test_menu_generator.py        # Generation tests
├── config.yaml                       # Main configuration
└── menu.ipxe                         # Generated output

```

## Key Components

### 1. Core Package (`src/core/`)

**Purpose**: Provides reusable components independent of specific distributions.

#### `models.py`

- `BootEntry`: Dataclass representing a single boot option
- `DistributionMenu`: Dataclass representing a distribution submenu

#### `validator.py`

- `URLValidator`: Validates that boot files exist before including in menu
- Uses HEAD requests for efficiency
- Optional validation for faster iteration

#### `generator.py`

- `MenuGenerator`: Renders iPXE menus using Jinja2 templates
- Separates presentation logic from business logic
- Template path configurable for customization

### 2. Distributions Package (`src/distributions/`)

**Purpose**: Pluggable system for distribution-specific metadata fetching.

#### `base.py`

- `AbstractMetadataFetcher`: Interface that all fetchers must implement
- Single method: `fetch_versions(metadata_url, **filters) -> List[str]`

#### Provider Implementations

- Each distribution gets its own module (e.g., `fedora.py`)
- Implements metadata fetching logic specific to that distribution
- Returns sorted list of available versions

#### Registry (`distributions/__init__.py`)

```python
METADATA_PROVIDERS = {
    'fedora': FedoraMetadataFetcher,
    # Add more providers here
}
```

### 3. Command-Line Interface (`cli.py`)

**Purpose**: CLI orchestration and argument parsing.

#### `main()` function

- Parses command-line arguments
- Loads configuration from YAML
- Orchestrates builder and generator
- Handles verbose/quiet output

### 4. Distribution Builder (`builder.py`)

**Purpose**: Builds distribution menus from configuration.

#### `DistributionBuilder` class

- Builds distribution menus from configuration
- Supports two types:
  - **Static**: Fixed version list from config
  - **Dynamic**: Fetches versions from metadata provider
- Handles URL validation
- Manages verbose/quiet output

## Data Flow

```
┌─────────────┐
│ config.yaml │
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│ cli.py               │
│  - Loads config      │
│  - Creates Builder   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ DistributionBuilder              │
│  - For each distribution:        │
│    • Static → use config versions│
│    • Dynamic → fetch metadata    │
│  - Validates URLs (optional)     │
│  - Creates BootEntry objects     │
└──────┬───────────────────────────┘
       │
       ├─[dynamic]──┐
       │            ▼
       │    ┌────────────────────────┐
       │    │ MetadataFetcher        │
       │    │  - Fetch from source   │
       │    │  - Parse format        │
       │    │  - Return versions     │
       │    └────────┬───────────────┘
       │             │
       ├─────────────┘
       │
       ▼
┌──────────────────────┐
│ MenuGenerator        │
│  - Renders templates │
│  - Combines sections │
└──────┬───────────────┘
       │
       ▼
┌──────────────┐
│  menu.ipxe   │
└──────────────┘
```

## Plugin System

### How Distribution Plugins Work

1. **Implement the Interface**: Create a class inheriting from `AbstractMetadataFetcher`
2. **Register**: Add to `METADATA_PROVIDERS` dictionary
3. **Configure**: Reference in `config.yaml` with `metadata_provider: "name"`

### Example: Adding Windows Support

**Step 1**: Create `src/distributions/windows.py`

```python
from .base import AbstractMetadataFetcher

class WindowsMetadataFetcher(AbstractMetadataFetcher):
    def fetch_versions(self, metadata_url, **filters):
        # Implement Windows-specific logic
        return ['11', '10', '7']
```

**Step 2**: Register in `src/distributions/__init__.py`

```python
from .windows import WindowsMetadataFetcher

METADATA_PROVIDERS = {
    'fedora': FedoraMetadataFetcher,
    'windows': WindowsMetadataFetcher,  # Add this
}
```

**Step 3**: Use in `config.yaml`

```yaml
distributions:
  windows:
    type: "dynamic"
    metadata_provider: "windows"
    metadata_url: "http://your-server/windows-versions.json"
    # ... rest of config
```

## Design Principles

### Separation of Concerns

- **Core**: Reusable, distribution-agnostic
- **Distributions**: Specific to each OS/distro
- **Templates**: Presentation logic only
- **Main**: Orchestration and CLI

### Open/Closed Principle

- **Open for extension**: Add new distributions without modifying existing code
- **Closed for modification**: Core components rarely change

### Dependency Inversion

- Core depends on abstractions (`AbstractMetadataFetcher`)
- Specific implementations depend on same abstractions
- No dependency on concrete implementations

### Configuration Over Code

- Everything configurable via YAML
- No Python changes needed for new static distributions
- Templates customizable without code changes

## Testing Strategy

### Unit Tests

- `test_ipxe_menu_gen.py`: Test data models
- `test_url_validator.py`: Test URL validation (mocked)
- `test_menu_generator.py`: Test menu generation

### Integration Tests

- Run with `--no-validate` for fast testing
- Run with validation for complete testing
- Mock HTTP requests to avoid network dependencies

### Manual Testing

```bash
# Fast iteration (no network calls)
make fast

# Full validation
make validate

# Custom config
python3 -m ipxe_menu_gen -c custom.yaml
```

## Extension Points

### Add New Distribution

See `ADDING_DISTRIBUTIONS.md` for detailed guide.

### Custom Templates

1. Copy `src/templates/` to custom location
2. Modify templates as needed
3. Use with `MenuGenerator(config, template_dir=custom_path)`

### Custom Validation

Extend `URLValidator` class or implement custom validator.

### Additional Boot Types

Modify templates to add new boot types beyond chain/shell/exit.

## Performance Considerations

### URL Validation

- Most expensive operation (network I/O)
- Use `--no-validate` during development
- Validation runs in serial (could be parallelized in future)

### Metadata Fetching

- Cached by default (reuse connection)
- Timeout: 10 seconds
- Could add persistent caching in future

### Template Rendering

- Negligible overhead
- Pre-compiled by Jinja2
- Happens once per invocation

## Future Enhancements

### Potential Improvements

1. **Parallel URL Validation**: Use asyncio or threading for faster validation
2. **Metadata Caching**: Cache API responses locally to reduce network calls
3. **Auto-Discovery**: Automatically scan `distributions/` directory for plugins instead of manual registry (currently requires manual registration in `__init__.py`)
4. **Configuration Validation**: Use JSON Schema to validate config.yaml structure
5. **More Providers**: CentOS, Debian, Ubuntu, Windows, BSD metadata fetchers
6. **Multi-Architecture**: ARM, aarch64 support in addition to x86_64
7. **CI/CD Integration**: GitHub Actions workflow examples
8. **Web UI**: Optional web interface for configuration management

### Backward Compatibility

- Configuration format is stable
- Core API unlikely to change
- New providers don't affect existing ones

## Migration Notes

### From Old Architecture

The refactoring (February 2026) moved from a monolithic design to modular:

**Before** (monolithic file):

- All code in single `ipxe_menu_gen.py` file (401 lines)
- `FedoraMetadataFetcher` hardcoded
- String check for 'fedoraproject.org'

**After** (modular):

- Core: Data models, validation, generation
- Distributions: Plugin system for metadata fetching
- CLI: User interface and orchestration
- Easier to test, extend, and maintain

### Breaking Changes

- Import paths changed:
  - `from ipxe_menu_gen import BootEntry` → `from core import BootEntry`
  - `from ipxe_menu_gen import URLValidator` → `from core import URLValidator`
- Config requires `metadata_provider` field for dynamic distributions
- Tests updated to use new imports

### Non-Breaking Changes

- CLI interface unchanged
- Configuration format mostly unchanged (only `metadata_provider` added)
- Template format unchanged
- Generated menu.ipxe format unchanged
