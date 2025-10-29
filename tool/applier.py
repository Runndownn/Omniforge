"""Apply portable profile in different modes."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from rich.console import Console

from .validators import ensure_directory, resolve_windows_terminal_path

console = Console()


class ApplyMode(str, Enum):
    DEFAULT = "default"
    COPY = "copy"
    PROMOTE = "promote"


@dataclass
class ApplyResult:
    settings_path: Path
    zsh_path: Path
    backups: list[Path]


BACKUP_ROOT_WINDOWS = Path.home() / "wt-portable" / "backups"
BACKUP_ROOT_WSL = Path("~/wt-portable/backups").expanduser()
PORTABLE_SETTINGS = Path("artifacts/settings.json")
PORTABLE_ZSH = Path("artifacts/zshrc.portable")


class ApplyError(RuntimeError):
    """Raised when application fails."""


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def _backup_file(source: Path, root: Path) -> Path:
    ensure_directory(root)
    destination = root / f"{source.name}.{_timestamp()}"
    shutil.copy2(source, destination)
    console.print(f"[yellow]Backup[/yellow] {source} → {destination}")
    return destination


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)
    if not isinstance(data, dict):
        raise ValueError(f"Expected dict in {path}, got {type(data).__name__}")
    return data


def _write_json(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2)
        fp.write("\n")


def _ensure_portable_profile(settings: dict[str, Any], set_default: bool) -> dict[str, Any]:
    profiles_section = settings.setdefault("profiles", {})
    if not isinstance(profiles_section, dict):
        raise ValueError("profiles section must be a mapping")
    profile_list = profiles_section.setdefault("list", [])
    if not isinstance(profile_list, list):
        raise ValueError("profiles.list must be a list")
    portable_guid = "{6fd0b4a5-95a6-46ed-9ad4-71fb4c6d9d25}"

    existing = next((p for p in profile_list if isinstance(p, dict) and p.get("guid") == portable_guid), None)
    if existing:
        existing.update(
            {
                "name": "Runndownn Portable",
                "commandline": "wsl.exe -d Ubuntu-22.04 --exec /bin/zsh",
                "startingDirectory": "\\\\wsl$\\Ubuntu-22.04\\home\\$USER",
                "hidden": False,
            }
        )
    else:
        profile_list.append(
            {
                "name": "Runndownn Portable",
                "guid": portable_guid,
                "commandline": "wsl.exe -d Ubuntu-22.04 --exec /bin/zsh",
                "startingDirectory": "\\\\wsl$\\Ubuntu-22.04\\home\\$USER",
                "icon": "ms-appdata:///roaming/runndownn-portable.png",
                "hidden": False,
            }
        )

    if set_default:
        settings["defaultProfile"] = portable_guid
    return settings


def _apply_settings(mode: ApplyMode, dry_run: bool) -> tuple[Path, list[Path]]:
    if not PORTABLE_SETTINGS.exists():
        raise ApplyError("artifacts/settings.json not found; run export first")

    target = resolve_windows_terminal_path()
    backups: list[Path] = []
    if target.exists() and not dry_run:
        backups.append(_backup_file(target, BACKUP_ROOT_WINDOWS))

    if mode == ApplyMode.DEFAULT:
        if dry_run:
            console.print(f"[cyan]Would overwrite[/cyan] {target} with portable settings")
        else:
            shutil.copy2(PORTABLE_SETTINGS, target)
    else:
        base_path = PORTABLE_SETTINGS if mode != ApplyMode.COPY or not target.exists() else target
        settings = _load_json(base_path)
        portable = _load_json(PORTABLE_SETTINGS)
        if mode == ApplyMode.COPY:
            updated = _ensure_portable_profile(settings, set_default=False)
        else:  # PROMOTE uses portable template and becomes default
            updated = _ensure_portable_profile(portable, set_default=True)
        if dry_run:
            console.print(f"[cyan]Would update profiles list[/cyan] in {target}")
        else:
            _write_json(target, updated)
    return target, backups


def _apply_zsh_default(target: Path, dry_run: bool, backups: list[Path]) -> None:
    if target.exists() and not dry_run:
        backups.append(_backup_file(target, BACKUP_ROOT_WSL))
    if dry_run:
        console.print(f"[cyan]Would overwrite[/cyan] {target} with portable profile")
    else:
        shutil.copy2(PORTABLE_ZSH, target)


def _apply_zsh_copy(target: Path, dry_run: bool) -> None:
    portable_copy = target.with_name(".zshrc-runndownn-portable")
    if dry_run:
        console.print(f"[cyan]Would create copy[/cyan] at {portable_copy}")
        return
    shutil.copy2(PORTABLE_ZSH, portable_copy)
    loader_line = "[[ -f ~/.zshrc-runndownn-portable ]] && source ~/.zshrc-runndownn-portable\n"
    if target.exists():
        current = target.read_text(encoding="utf-8")
        if loader_line not in current:
            target.write_text(current + "\n" + loader_line, encoding="utf-8")
    else:
        target.write_text(loader_line, encoding="utf-8")


def _apply_zsh_promote(target: Path, dry_run: bool, backups: list[Path]) -> None:
    if target.exists() and not dry_run:
        backups.append(_backup_file(target, BACKUP_ROOT_WSL))
    if dry_run:
        console.print(f"[cyan]Would promote portable profile to default[/cyan] at {target}")
    else:
        shutil.copy2(PORTABLE_ZSH, target)


def _apply_zsh(mode: ApplyMode, dry_run: bool) -> tuple[Path, list[Path]]:
    if not PORTABLE_ZSH.exists():
        raise ApplyError("artifacts/zshrc.portable missing; run sanitize first")

    target = Path.home() / ".zshrc"
    backups: list[Path] = []

    if mode == ApplyMode.DEFAULT:
        _apply_zsh_default(target, dry_run, backups)
    elif mode == ApplyMode.COPY:
        _apply_zsh_copy(target, dry_run)
    elif mode == ApplyMode.PROMOTE:
        _apply_zsh_promote(target, dry_run, backups)
    else:
        raise ApplyError(f"Unknown apply mode {mode}")

    for backup in backups:
        console.print(f"[green]Backup created at[/green] {backup}")
    return target, backups


def apply_profile(mode: ApplyMode = ApplyMode.COPY, dry_run: bool = False) -> ApplyResult:
    console.print(f"[magenta]Applying portable profile[/magenta] (mode={mode}, dry_run={dry_run})")
    settings_path, settings_backups = _apply_settings(mode, dry_run)
    zsh_path, zsh_backups = _apply_zsh(mode, dry_run)
    return ApplyResult(
        settings_path=settings_path,
        zsh_path=zsh_path,
        backups=settings_backups + zsh_backups,
    )
