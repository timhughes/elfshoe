.PHONY: all clean validate fast help

# Default target
all: validate

# Generate menu with full validation
validate:
	@echo "Generating iPXE menu with URL validation..."
	python3 src/ipxe_menu_gen.py

# Generate menu without validation (fast)
fast:
	@echo "Generating iPXE menu (fast mode, no validation)..."
	python3 src/ipxe_menu_gen.py --no-validate --quiet

# Generate with custom config
custom:
	@echo "Generating iPXE menu from custom config..."
	python3 src/ipxe_menu_gen.py -c config.example.yaml -o menu-custom.ipxe

# Clean generated files
clean:
	@echo "Removing generated files..."
	rm -f menu.ipxe menu-custom.ipxe

# Show help
help:
	@echo "iPXE Menu Generator - Makefile targets:"
	@echo ""
	@echo "  make            - Generate menu with validation (default)"
	@echo "  make validate   - Generate menu with URL validation"
	@echo "  make fast       - Generate menu without validation (faster)"
	@echo "  make custom     - Generate menu from example config"
	@echo "  make clean      - Remove generated menu files"
	@echo "  make help       - Show this help message"
	@echo ""
	@echo "Advanced usage:"
	@echo "  python3 src/ipxe_menu_gen.py --help"
