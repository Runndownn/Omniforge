"""Command-line interface for the portable profile toolkit."""

from __future__ import annotations

import shutil
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .applier import ApplyMode, apply_profile
from .exporter import export_windows_terminal_settings
from .github_publisher import publish
from .installer import install_prerequisites
from .sanitizer import sanitize_zshrc
from .validators import resolve_windows_terminal_path, run_diagnostics

app = typer.Typer(add_completion=False)
console = Console()


@dataclass
class MenuItem:
    label: str
    description: str
    action: Callable[[], None]


def _export_settings_action() -> None:
    export_windows_terminal_settings()


def _sanitize_action() -> None:
    sanitize_zshrc()


def _install_action() -> None:
    install_prerequisites()


def _menu_items() -> dict[str, MenuItem]:
    return {
        "1": MenuItem(
            label="Export current Windows Terminal settings",
            description="Reads live settings.json, normalizes them, and refreshes artifacts/settings.json.",
            action=_export_settings_action,
        ),
        "2": MenuItem(
            label="Build sanitized WSL .zshrc",
            description="Applies regex rules to ~/.zshrc and writes artifacts/zshrc.portable",
            action=_sanitize_action,
        ),
        "3": MenuItem(
            label="Install prerequisites",
            description="Installs Windows Terminal, WSL (optional), Oh My Zsh, plugins, and fonts.",
            action=_install_action,
        ),
        "4": MenuItem(
            label="Apply portable profile",
            description="Choose default, copy, or promote mode to apply settings locally.",
            action=_apply_menu,
        ),
        "5": MenuItem(
            label="GitHub release workflow",
            description="Stage, tag, archive, and optionally push release artifacts.",
            action=_release_menu,
        ),
        "6": MenuItem(
            label="Backup & restore",
            description="List backups and restore selected snapshot.",
            action=_restore_menu,
        ),
        "7": MenuItem(
            label="Diagnostics & validation",
            description="Runs environment checks, manifest validation, and git status.",
            action=lambda: run_diagnostics(),
        ),
        "8": MenuItem(
            label="Exit",
            description="Quit the menu",
            action=lambda: None,
        ),
    }


def _apply_menu() -> None:
    table = Table(title="Apply Mode")
    table.add_column("Option")
    table.add_column("Mode")
    table.add_column("Description")
    table.add_row("1", "default", "Backup then overwrite Windows Terminal defaults and ~/.zshrc")
    table.add_row("2", "copy", "Inject portable profile alongside existing defaults")
    table.add_row("3", "promote", "Promote previously copied profile to default")
    console.print(table)

    choice = console.input("Select mode [1-3]: ").strip()
    mapping = {
        "1": ApplyMode.DEFAULT,
        "2": ApplyMode.COPY,
        "3": ApplyMode.PROMOTE,
    }
    mode = mapping.get(choice)
    if not mode:
        console.print("[red]Invalid apply mode[/red]")
        return
    apply_profile(mode=mode, dry_run=False)


def _release_menu() -> None:
    version = console.input("Tag version (e.g., v1.0.0): ").strip()
    if not version:
        console.print("[red]Version is required[/red]")
        return
    push = console.input("Push to remote as well? [y/N]: ").strip().lower().startswith("y")
    publish(version=version, push_changes=push)


def _restore_menu() -> None:
    root = Path.home() / "wt-portable" / "backups"
    if not root.exists():
        console.print("[yellow]No backups recorded yet[/yellow]")
        return
    backups = sorted(root.glob("*"))
    if not backups:
        console.print("[yellow]No backup files available[/yellow]")
        return
    table = Table(title="Available Backups")
    table.add_column("Index")
    table.add_column("File")
    for idx, backup in enumerate(backups, start=1):
        table.add_row(str(idx), backup.name)
    console.print(table)
    choice = console.input("Select backup to restore: ").strip()
    try:
        selected = backups[int(choice) - 1]
    except (ValueError, IndexError):
        console.print("[red]Invalid selection[/red]")
        return
    target = _detect_backup_target(selected.name)
    if not target:
        console.print("[red]Could not infer target location from backup name[/red]")
        return
    console.print(f"[cyan]Restoring {selected} → {target}")
    shutil.copy2(selected, target)


def _detect_backup_target(filename: str) -> Path | None:
    if filename.startswith("settings.json"):
        return resolve_windows_terminal_path()
    if filename.startswith(".zshrc"):
        return Path.home() / ".zshrc"
    return None


@app.command()
def menu() -> None:
    console.print("[bold magenta]Windows Terminal Portable Profile Toolkit[/bold magenta]")
    items = _menu_items()
    while True:
        table = Table(title="Main Menu", show_lines=True)
        table.add_column("Option", style="cyan")
        table.add_column("Action")
        table.add_column("Description")
        for key, menu_item in items.items():
            table.add_row(key, menu_item.label, menu_item.description)
        console.print(table)
        choice = console.input("Select option: ").strip()
        if choice not in items:
            console.print("[red]Invalid selection[/red]")
            continue
        item = items[choice]
        if choice == "8":
            console.print("[green]Goodbye![/green]")
            break
        try:
            item.action()
        except Exception as exc:
            console.print(f"[red]Operation failed:[/red] {exc}")


@app.command()
def export() -> None:
    """Export Windows Terminal settings."""
    export_windows_terminal_settings()


@app.command()
def sanitize() -> None:
    """Sanitize WSL .zshrc and update artifacts."""
    sanitize_zshrc()


@app.command()
def install(
    non_interactive: bool = typer.Option(False, "--non-interactive", help="Suppress prompts"),
    include_wsl: bool = typer.Option(True, "--include-wsl", help="Install WSL if missing"),
) -> None:
    """Install prerequisites such as Windows Terminal, WSL, and required plugins."""
    install_prerequisites(non_interactive=non_interactive, include_wsl=include_wsl)


@app.command()
def apply(
    mode: ApplyMode = typer.Option(ApplyMode.COPY, "--mode", case_sensitive=False),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes"),
) -> None:
    """Apply the portable profile in the selected mode."""
    apply_profile(mode=mode, dry_run=dry_run)


@app.command()
def package(
    version: str = typer.Option("v1.0.0", "--version", help="Release version tag"),
    push_changes: bool = typer.Option(False, "--push", help="Push git changes to remote"),
) -> None:
    """Create release assets and optionally push to GitHub."""
    publish(version=version, push_changes=push_changes)


@app.command()
def diagnostics() -> None:
    """Run diagnostic checks."""
    run_diagnostics()


def main() -> None:
    app()


if __name__ == "__main__":
    main()
