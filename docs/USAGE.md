# Usage Guide

## Prerequisites

- Windows 11 with PowerShell 5.1 or higher. (Windows Terminal export works on Windows 10 19043+ but winget install paths differ.)
- Python 3.10 or later available on both Windows and WSL.
- Git installed and configured with sanitized global identity.
- Optional: Access to Microsoft Store if you prefer GUI installation of Windows Terminal.

## Initial Setup

1. Clone the repository and enter the directory.
2. (Optional) Create a virtual environment by running `make venv`.
3. Launch the interactive menu:

   ```powershell
   python -m tool.cli --menu
   ```

The CLI detects whether it is running under PowerShell or WSL and adjusts defaults accordingly.

## Typical Workflow

1. **Install prerequisites** – Option 3 installs or verifies Windows Terminal, WSL, Oh My Zsh, plugins, and fonts.
2. **Export configuration** – Option 1 reads the live Windows Terminal configuration and copies redistributable assets into `artifacts/`.
3. **Sanitize Zsh profile** – Option 2 captures your current WSL `.zshrc`, applies the rule engine, and writes `artifacts/zshrc.portable`.
4. **Apply on this machine** – Option 4 lets you choose default or copy mode. Default overwrites current settings after creating backups; copy mode keeps your existing defaults and registers a “Portable” profile alongside them.
5. **Publish** – Option 5 walks through staging commits, tagging, and creating a GitHub release bundle with SHA-256 manifest.

At any point you can run **Diagnostics** (Option 7) to confirm environment sanity, file integrity, and detect diffs between current and exported artifacts.

## Backup & Restore

- Every destructive action writes backups to `%USERPROFILE%\wt-portable\backups` (Windows) and `$HOME/wt-portable/backups` (WSL).
- Use menu option 6.2 to restore from a chosen backup. The CLI validates SHA-256 hashes before restoring.

## Applying in Copy Mode Later

If you initially test via Copy Mode, you can later promote the portable profile to default using:

```powershell
python -m tool.cli apply --mode promote
```

This swaps the Windows Terminal default profile GUID with the portable profile's GUID and switches `.zshrc` symlinks.

## Offline Installation

- GitHub Actions produces a release ZIP containing `artifacts/`, `vendor/`, and the CLI.
- Download the ZIP, extract it, and run `python -m tool.cli --menu --offline` to skip network-dependent installations.

## Troubleshooting

| Issue | Resolution |
| ----- | ---------- |
| Windows Terminal path not found | Run Option 3.1 to install via winget; re-run export. |
| WSL distro not detected | Ensure WSL is installed (`wsl.exe --install`) or use Option 3.2. |
| Sanitizer removes desired alias | Add it to `tool/sanitizer.py` `ALLOWLIST_ALIASES` and regenerate. |
| Git push fails | Run Option 5.1 to reinitialize repo or configure Git credentials via PAT. |

## Uninstall / Restore Defaults

1. Launch CLI and choose **Backup & restore** → **Restore**.
2. Select the timestamped backup created prior to applying the portable profile.
3. Confirm re-launch of Windows Terminal to apply changes.

Alternatively, manually copy the backup files from the backup directory to the live locations using PowerShell or File Explorer.
