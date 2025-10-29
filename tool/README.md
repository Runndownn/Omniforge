# Tool Package

The `tool` package holds the production code paths that power the portable profile workflow. Each module isolates one responsibility so the CLI can orchestrate complex tasks while remaining easy to audit and test.

## Module Inventory

- `cli.py` builds the Typer entrypoint and interactive menu.
- `exporter.py` lifts Windows Terminal settings and copies any referenced assets.
- `sanitizer.py` normalizes `.zshrc`, removes sensitive material, and maintains the manifest.
- `applier.py` writes sanitized profiles back to disk with safe backups.
- `installer.py` installs optional prerequisites such as WSL and Oh My Zsh.
- `github_publisher.py` prepares Git release artifacts, tags, and pushes.
- `validators.py` provides shared environment and manifest checks.

```mermaid
classDiagram
    direction LR
    class CLI {
        +menu()
        +export()
        +sanitize()
        +install()
        +apply(mode, dry_run)
        +package(version, push_changes)
        +diagnostics()
    }
    class Exporter {
        +export_windows_terminal_settings()
        +sanitize_settings()
        +copy_assets()
        +update_manifest()
    }
    class Sanitizer {
        +sanitize_zshrc()
        +apply_rules(content)
        +strip_denylisted_aliases(content)
    }
    class Applier {
        +apply_profile(mode, dry_run)
        +_apply_settings(mode, dry_run)
        +_apply_zsh(mode, dry_run)
    }
    class Installer {
        +install_prerequisites(non_interactive, include_wsl)
        +install_windows_terminal()
        +install_wsl(distro)
        +install_font()
    }
    class Publisher {
        +publish(version, push_changes)
        +stage_and_commit(message)
        +tag_release(version)
        +build_release_manifest()
    }
    class Validators {
        +run_diagnostics()
        +validate_manifest(entries)
        +resolve_windows_terminal_path()
    }
    CLI --> Exporter : delegates export
    CLI --> Sanitizer : delegates scrub
    CLI --> Applier : applies profiles
    CLI --> Installer : installs deps
    CLI --> Publisher : releases
    CLI --> Validators : diagnostics
    Exporter --> Validators : ensure manifest
    Sanitizer --> Validators : ensure directories
    Applier --> Validators : ensure directories
```

## Runtime Flow

```mermaid
flowchart TD
    Menu["User picks action\nvia tool.cli.menu"] --> Decision{Selected command}
    Decision -->|Export| ExportPath["export_windows_terminal_settings\ncreates artifacts/settings.json"]
    Decision -->|Sanitize| SanitizePath["sanitize_zshrc\nproduces artifacts/zshrc.portable"]
    Decision -->|Install| InstallPath["install_prerequisites\nvendors dependencies"]
    Decision -->|Apply| ApplyPath["apply_profile\nupdates local WT + .zshrc"]
    Decision -->|Package| PackagePath["publish\nbuilds release archive"]
    ExportPath --> Manifest["manifest.json updated\nwith signed checksum"]
    SanitizePath --> Manifest
    ApplyPath --> Backup["Timestamped backups\nwt-portable/backups"]
    PackagePath --> Release["release/portable-profile.zip"]
```

## Testing Notes

- Functions are designed to be called directly from tests (see `tests/test_sanitizer.py`).
- Pure helpers accept simple inputs (e.g., raw strings or `Path` objects) so they can be fuzzed without disk access.
- Safety checks guard destructive operations with explicit backups and dry-run modes.

## Configuration Touchpoints

- Global settings live in `pyproject.toml` and `Makefile`; both map directly to Typer commands exposed in `cli.py`.
- Environment detection and safeguards are handled in `validators.py` so other modules remain unaware of platform-specific quirks.
- Feature flags or future toggles should be centralized in `validators` or dedicated config modules to keep the CLI thin.
