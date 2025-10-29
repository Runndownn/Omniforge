"""Utilities to publish artifacts to GitHub."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console

console = Console()


@dataclass
class GitConfig:
    remote: str = "origin"
    branch: str = "main"


class GitError(RuntimeError):
    """Raised when Git interaction fails."""


def _run_git(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    console.print(f"[cyan]$ git {' '.join(args)}")
    return subprocess.run(["git", *args], check=check, text=True)


def initialize_repository(config: GitConfig = GitConfig()) -> None:
    if Path(".git").exists():
        console.print("[green]Git repository already initialized[/green]")
    else:
        _run_git(["init", "-b", config.branch])
    _run_git(["remote", "show", config.remote], check=False)


def stage_and_commit(message: str = "chore: update portable profile") -> None:
    _run_git(["add", "."])
    status = subprocess.run(["git", "status", "--short"], check=False, capture_output=True, text=True)
    if not status.stdout.strip():
        console.print("[yellow]Nothing to commit[/yellow]")
        return
    _run_git(["commit", "-m", message])


def tag_release(version: str) -> None:
    _run_git(["tag", "-f", version])


def push(config: GitConfig = GitConfig(), tags: bool = True) -> None:
    args = ["push", config.remote, config.branch]
    _run_git(args)
    if tags:
        _run_git(["push", config.remote, "--tags"])


def build_release_manifest(output: Path = Path("release")) -> Path:
    output.mkdir(parents=True, exist_ok=True)
    archive = output / "portable-profile.zip"
    console.print(f"[cyan]Creating release archive at[/cyan] {archive}")
    subprocess.run(
        [
            "powershell",
            "-Command",
            (
                "Compress-Archive -Path artifacts,docs,tool,scripts,pyproject.toml,requirements.txt,"
                "README.md,LICENSE -DestinationPath release/portable-profile.zip -Force"
            ),
        ],
        check=True,
        text=True,
    )
    return archive


def create_release_json(version: str, archive: Path) -> Path:
    payload = {
        "tag_name": version,
        "name": f"Portable Profile {version}",
        "body": "Automated release containing sanitized Windows Terminal profile and dependencies.",
    }
    json_path = archive.with_suffix(".json")
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    console.print(f"[green]Release descriptor written[/green] → {json_path}")
    return json_path


def publish(version: str, push_changes: bool = False) -> None:
    initialize_repository()
    stage_and_commit(f"chore: release {version}")
    tag_release(version)
    archive = build_release_manifest()
    create_release_json(version, archive)
    if push_changes:
        push()
        console.print("[green]Changes pushed to remote. Create GitHub release manually or via workflow.[/green]")
    else:
        console.print("[yellow]Push disabled. Upload archive and JSON manually or via workflow.[/yellow]")
