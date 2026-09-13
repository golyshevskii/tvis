# Use bash from PATH instead of /bin/sh — uniform behaviour on macOS/Linux/CI.
SHELL := /usr/bin/env bash
# -e fail on first error, -u error on unset vars, -o pipefail propagate pipe failures.
.SHELLFLAGS := -euo pipefail -c
# `make` with no target shows help, not the first recipe.
.DEFAULT_GOAL := help

.PHONY: help lint type test check

help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make <target>\n\nTargets:\n"} \
	/^[a-zA-Z_.-]+:.*##/ {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

lint: ## Lint the code
	@# TODO: Implement linting

type: ## Check the types
	@# TODO: Implement type checking

test: ## Run the tests
	@# TODO: Implement tests

check: lint type test ## Run the checks (lint, type, test)
