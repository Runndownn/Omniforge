"""Windows Terminal exporter."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

from rich.console import Console

from .validators import ensure_directory, resolve_windows_terminal_path

console = Console()


@dataclass
class ExportResult:
    source: Path
    destination: Path
    checksum: str


ASSETS_DIR = Path("artifacts/assets")
ARTIFACTS_DIR = Path("artifacts")
MANIFEST_PATH = ARTIFACTS_DIR / "manifest.json"


def _load_settings(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)
    if not isinstance(data, dict):
        raise ValueError(f"Expected dict at {path}, received {type(data).__name__}")
    return data


def _write_settings(data: dict[str, Any], destination: Path) -> None:
    with destination.open("w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2)
        fp.write("\n")


def _hash_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sanitize_settings(data: dict[str, Any]) -> dict[str, Any]:
    profile_list = data.get("profiles", {}).get("list", [])
    if not isinstance(profile_list, list):
        return data
    for profile in profile_list:
        if not isinstance(profile, dict):
            console.print("[yellow]Skipping non-dict profile entry[/yellow]")
            continue
        if "startingDirectory" in profile:
            profile["startingDirectory"] = profile["startingDirectory"].replace(
                str(Path.home()), "$HOME"
            )
        if "commandline" in profile and ".exe" not in profile["commandline"].lower():
            # Ensure we invoke zsh through WSL exec for portability.
            profile["commandline"] = "wsl.exe -d Ubuntu-22.04 --exec /bin/zsh"
        profile.setdefault("hidden", False)
    return data


def copy_assets(settings: dict[str, Any]) -> list[Path]:
    ensure_directory(ASSETS_DIR)
    copied: list[Path] = []
    profile_list = settings.get("profiles", {}).get("list", [])
    if not isinstance(profile_list, list):
        return copied
    for profile in profile_list:
        if not isinstance(profile, dict):
            continue
        icon = profile.get("icon")
        if icon and icon.startswith("C:"):
            icon_path = Path(icon)
            if icon_path.exists():
                destination = ASSETS_DIR / icon_path.name
                shutil.copy2(icon_path, destination)
                profile["icon"] = f"artifacts/assets/{icon_path.name}"
                copied.append(destination)
    return copied


def update_manifest(entry: ExportResult) -> None:
    ensure_directory(ARTIFACTS_DIR)
    manifest_data: dict[str, Any] = {
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_machine": "sanitized",
        "artifacts": [],
    }
    if MANIFEST_PATH.exists():
        with MANIFEST_PATH.open("r", encoding="utf-8") as fp:
            loaded = json.load(fp)
        if isinstance(loaded, dict):
            manifest_data.update(loaded)

    artifacts = [
        item
        for item in manifest_data.get("artifacts", [])
        if isinstance(item, dict) and item.get("path") != entry.destination.as_posix()
    ]
    artifacts.append(
        {
            "name": "Windows Terminal settings",
            "path": entry.destination.as_posix(),
            "sha256": entry.checksum,
        }
    )
    manifest_data["artifacts"] = artifacts

    with MANIFEST_PATH.open("w", encoding="utf-8") as fp:
        json.dump(manifest_data, fp, indent=2)
        fp.write("\n")


def export_windows_terminal_settings(destination: Path | None = None) -> ExportResult:
    destination = destination or ARTIFACTS_DIR / "settings.json"
    ensure_directory(destination.parent)

    source = resolve_windows_terminal_path()
    console.print(f"[cyan]Reading Windows Terminal settings from[/cyan] {source}")
    data = sanitize_settings(_load_settings(source))
    assets = copy_assets(data)
    if assets:
        console.print(f"[cyan]Copied assets:[/cyan] {[asset.name for asset in assets]}")
    _write_settings(data, destination)

    checksum = _hash_file(destination)
    update_manifest(ExportResult(source=source, destination=destination, checksum=checksum))
    console.print(f"[green]Exported settings[/green] → {destination} (sha256={checksum})")
    return ExportResult(source=source, destination=destination, checksum=checksum)
