# Use bash from PATH instead of /bin/sh — uniform behaviour on macOS/Linux/CI.
SHELL := /usr/bin/env bash
# -e fail on first error, -u error on unset vars, -o pipefail propagate pipe failures.
.SHELLFLAGS := -euo pipefail -c
# `make` with no target shows help, not the first recipe.
.DEFAULT_GOAL := help

UV ?= uv
PYTHON_PATHS := scripts/

.PHONY: help uv.init lint type check test

help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make <target>\n\nTargets:\n"} \
	/^[a-zA-Z_.-]+:.*##/ {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

uv.init: ## Install locked Python tooling
	@$(UV) sync --all-groups

lint: ## Check Python formatting, lint, and complexity
	@$(UV) run --group lint ruff format --check $(PYTHON_PATHS)
	@$(UV) run --group lint ruff check $(PYTHON_PATHS)
	@$(UV) run --group lint tooprolix check $(PYTHON_PATHS)

type: ## Check Python types
	@$(UV) run --group type ty check $(PYTHON_PATHS)

check: lint type ## Verify local source integrity (does not run Pine)
	@$(UV) run python3 scripts/check_pe.py check

test: ## Generate the Pine smoke harness (does not run Pine)
	@$(UV) run python3 scripts/check_pe.py generate
