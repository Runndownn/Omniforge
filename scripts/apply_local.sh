#!/usr/bin/env bash
set -euo pipefail

MODE="copy"
DRY_RUN=""

usage() {
  cat <<'EOF'
Usage: apply_local.sh [--mode default|copy|promote] [--dry-run]

  --mode      default  Replace the existing default profile and ~/.zshrc
              copy      Add a parallel profile without overwriting defaults (default)
              promote   Promote the portable profile to be default
  --dry-run   Print what would happen without modifying files
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN="--dry-run"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

python3 -m tool.cli apply --mode "$MODE" $DRY_RUN
