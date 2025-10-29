SHELL := powershell.exe
.SHELLFLAGS := -NoLogo -NoProfile -Command
PYTHON := python
PYTHON3 := python3
VENV := .venv
REQUIREMENTS := requirements.txt

.PHONY: help venv lint test typecheck format export sanitize apply release clean

help:
	Write-Output "Targets:"; \
	Write-Output "  make venv       # create local venv"; \
	Write-Output "  make lint       # run ruff"; \
	Write-Output "  make test       # run pytest"; \
	Write-Output "  make typecheck  # run mypy"; \
	Write-Output "  make export     # export WT settings"; \
	Write-Output "  make sanitize   # sanitize zshrc"; \
	Write-Output "  make apply      # apply defaults (dry-run)"; \
	Write-Output "  make release    # build offline ZIP";

venv:
	if (!(Test-Path $(VENV))) { $(PYTHON) -m venv $(VENV) }
	$(VENV)\Scripts\pip.exe install --upgrade pip
	$(VENV)\Scripts\pip.exe install -r $(REQUIREMENTS) -e .[dev]

lint:
	$(VENV)\Scripts\ruff.exe check tool

format:
	$(VENV)\Scripts\ruff.exe format tool

test:
	$(VENV)\Scripts\pytest.exe

typecheck:
	$(VENV)\Scripts\mypy.exe tool

export:
	$(PYTHON) -m tool.cli export

sanitize:
	$(PYTHON) -m tool.cli sanitize

apply:
	$(PYTHON) -m tool.cli apply --mode copy --dry-run

release:
	$(PYTHON) -m tool.cli package --offline

clean:
	Remove-Item -Recurse -Force $(VENV) -ErrorAction SilentlyContinue
	Remove-Item -Recurse -Force .pytest_cache -ErrorAction SilentlyContinue
	Remove-Item -Recurse -Force .mypy_cache -ErrorAction SilentlyContinue
