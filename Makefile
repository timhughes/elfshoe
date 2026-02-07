.DEFAULT_GOAL := help

# Color definitions for help output
_GREEN := $(shell tput setaf 2)
_RESET := $(shell tput sgr0)

help:
	@grep -E '^[a-zA-Z_-]+:.*## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*## "}; {printf "$(_GREEN)make %-20s$(_RESET) %s\n", $$1, $$2}'

all: validate

validate: ## Generate menu with URL validation
	python3 src/ipxe_menu_gen.py

fast: ## Generate menu without validation
	python3 src/ipxe_menu_gen.py --no-validate --quiet

test: ## Run all tests
	python3 -m pytest tests/ -v

test-coverage: ## Run tests with coverage
	python3 -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

test-quick: ## Run tests (minimal output)
	python3 -m pytest tests/ -q

install: ## Install in development mode
	pip install -e .

install-dev: ## Install with dev dependencies
	pip install -e ".[dev]"

clean: ## Remove generated files
	rm -f menu.ipxe menu-custom.ipxe
	rm -rf htmlcov/ .coverage .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

.PHONY: help all validate fast test test-coverage test-quick clean install install-dev
