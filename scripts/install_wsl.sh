#!/usr/bin/env bash
set -euo pipefail

if ! command -v wsl.exe >/dev/null 2>&1; then
  echo "wsl.exe not available. Run from Windows PowerShell instead." >&2
  exit 1
fi

echo "Ensuring WSL is installed..."
wsl.exe --status >/dev/null 2>&1 || wsl.exe --install -d Ubuntu-22.04

echo "Bootstraping prerequisites through Python CLI..."
python3 -m tool.cli install --non-interactive
