.DEFAULT_GOAL := help

# Color definitions for help output
_GREEN := $(shell tput setaf 2)
_RESET := $(shell tput sgr0)

help:
	@grep -E '^[a-zA-Z_-]+:.*## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*## "}; {printf "$(_GREEN)make %-20s$(_RESET) %s\n", $$1, $$2}'

all: validate

validate: ## Generate menu with URL validation
	PYTHONPATH=src python3 -m elfshoe

fast: ## Generate menu without validation
	PYTHONPATH=src python3 -m elfshoe --no-validate --quiet

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
	rm -rf htmlcov/ .coverage .pytest_cache site/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

.PHONY: help all validate fast test test-coverage test-quick lint format build publish clean install install-dev docs-lint docs-serve docs-build docs-deploy version-show version-patch version-minor version-major version-tag pre-commit-install pre-commit-run pre-commit-update

lint: ## Check code style
	hatch run lint:check

format: ## Format code
	hatch run lint:format

build: ## Build distribution packages
	hatch build

publish: ## Publish to PyPI
	hatch publish

docs-lint: ## Lint documentation
	hatch run docs:lint

docs-serve: ## Serve documentation locally
	hatch run docs:serve

docs-build: ## Build documentation
	hatch run docs:build

docs-deploy: ## Deploy documentation to GitHub Pages
	mkdocs gh-deploy --force

version-show: ## Show current version
	hatch version

version-patch: ## Bump patch version (0.1.0 -> 0.1.1)
	hatch version patch

version-minor: ## Bump minor version (0.1.0 -> 0.2.0)
	hatch version minor

version-major: ## Bump major version (0.1.0 -> 1.0.0)
	hatch version major

version-tag: ## Create and push git tag for current version
	@VERSION=$$(hatch version) && \
	git tag -a "v$$VERSION" -m "Release v$$VERSION" && \
	echo "Created tag v$$VERSION. Push with: git push origin v$$VERSION"

pre-commit-install: ## Install pre-commit hooks
	pre-commit install
	pre-commit install --hook-type pre-push

pre-commit-run: ## Run pre-commit hooks on all files
	pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks to latest versions
	pre-commit autoupdate
