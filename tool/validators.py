"""Environment validation helpers."""

from __future__ import annotations

import json
import os
import platform
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
except ImportError as exc:  # pragma: no cover - dependency guard
    raise RuntimeError(
        "The 'rich' package is required. Install dependencies with `pip install -r requirements.txt`."
    ) from exc

console = Console()


@dataclass
class DiagnosticResult:
    name: str
    status: str
    details: str


def detect_environment() -> str:
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    if "microsoft" in platform.release().lower():
        return "wsl"
    return system


def ensure_python_version(min_major: int = 3, min_minor: int = 10) -> None:
    major, minor, _ = platform.python_version_tuple()
    if int(major) < min_major or (int(major) == min_major and int(minor) < min_minor):
        raise RuntimeError(
            f"Python {min_major}.{min_minor}+ is required, found {platform.python_version()}"
        )


def validate_json(path: Path) -> None:
    try:
        with path.open("r", encoding="utf-8") as fp:
            json.load(fp)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc


def validate_manifest(entries: Iterable[Path]) -> list[DiagnosticResult]:
    diagnostics: list[DiagnosticResult] = []
    manifest = Path("artifacts/manifest.json")
    if not manifest.exists():
        diagnostics.append(
            DiagnosticResult(
                name="Manifest",
                status="error",
                details="artifacts/manifest.json missing",
            )
        )
        return diagnostics

    with manifest.open("r", encoding="utf-8") as fp:
        data = json.load(fp)

    paths = {Path(item["path"]) for item in data.get("artifacts", [])}
    for entry in entries:
        status = "ok" if entry in paths else "missing"
        diagnostics.append(
            DiagnosticResult(
                name=entry.as_posix(),
                status=status,
                details="Present in manifest" if status == "ok" else "Not tracked in manifest",
            )
        )
    return diagnostics


def run_diagnostics() -> None:
    ensure_python_version()
    environment = detect_environment()

    results: list[DiagnosticResult] = [
        DiagnosticResult("Environment", "ok", environment),
    ]

    wt_settings = Path("artifacts/settings.json")
    zsh_portable = Path("artifacts/zshrc.portable")

    for path in (wt_settings, zsh_portable):
        if path.exists():
            try:
                if path.suffix == ".json":
                    validate_json(path)
                results.append(DiagnosticResult(path.name, "ok", "Readable"))
            except ValueError as exc:
                results.append(DiagnosticResult(path.name, "error", str(exc)))
        else:
            results.append(DiagnosticResult(path.name, "missing", "File not found"))

    results.extend(validate_manifest([wt_settings, zsh_portable]))

    git_status = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True,
        text=True,
        check=False,
    )
    clean = not git_status.stdout.strip()
    results.append(
        DiagnosticResult(
            "Git status",
            "ok" if clean else "dirty",
            "Working tree clean" if clean else git_status.stdout.strip(),
        )
    )

    table = Table(title="Diagnostics")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Details")
    for result in results:
        table.add_row(result.name, result.status, result.details)
    console.print(table)


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def resolve_windows_terminal_path() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        raise FileNotFoundError("LOCALAPPDATA environment variable is not set")

    candidates = [
        Path(local_app_data)
        / "Packages"
        / "Microsoft.WindowsTerminal_8wekyb3d8bbwe"
        / "LocalState"
        / "settings.json",
        Path(local_app_data)
        / "Packages"
        / "Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe"
        / "LocalState"
        / "settings.json",
        Path(local_app_data)
        / "Microsoft"
        / "Windows Terminal"
        / "settings.json",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError("Windows Terminal settings.json not found in known locations")
