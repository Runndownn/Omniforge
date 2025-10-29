"""Sanitize WSL Zsh profile for public redistribution."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from re import Pattern

from rich.console import Console

from .validators import ensure_directory

console = Console()


@dataclass
class SanitizationRule:
    description: str
    pattern: Pattern[str]
    replacement: str


RULES = [
    SanitizationRule(
        "Normalize UNIX absolute paths",
        re.compile(r"/home/[^/]+/"),
        "$HOME/",
    ),
    SanitizationRule(
        "Normalize Windows user paths",
        re.compile(r"C:\\Users\\[^\\]+"),
        "%USERPROFILE%",
    ),
    SanitizationRule(
        "Drop tokens",
        re.compile(r"(AKIA[A-Z0-9]{16}|ghp_[A-Za-z0-9]{36}|xox[pbar]-[A-Za-z0-9-]+)"),
        "<redacted>",
    ),
    SanitizationRule(
        "Remove bearer tokens",
        re.compile(r"Bearer\s+[A-Za-z0-9\-\._~+/]+=*"),
        "Bearer <redacted>",
    ),
    SanitizationRule(
        "Scrub email addresses",
        re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
        "user@example.com",
    ),
]

DENYLIST_ALIASES = {
    "hashcat",
    "sqlmap",
    "hydra",
    "john",
    "rustscan",
}

PORTABLE_OUTPUT = Path("artifacts/zshrc.portable")
SANITIZATION_LOG = Path("docs/SANITIZATION_REPORT.md")


def apply_rules(content: str) -> str:
    scrubbed = content
    for rule in RULES:
        scrubbed, count = re.subn(rule.pattern, rule.replacement, scrubbed)
        if count:
            console.print(f"[yellow]Applied rule[/yellow] {rule.description}: {count} substitutions")
    return scrubbed


def strip_denylisted_aliases(content: str) -> str:
    lines = []
    for line in content.splitlines():
        if line.startswith("alias "):
            alias_name = line.split("=", maxsplit=1)[0].replace("alias", "").strip()
            if alias_name in DENYLIST_ALIASES:
                console.print(f"[red]Removed sensitive alias[/red]: {alias_name}")
                continue
        lines.append(line)
    return "\n".join(lines) + "\n"


def sanitize_zshrc(
    source: Path | None = None,
    destination: Path | None = None,
    manifest_path: Path | None = None,
    log_path: Path | None = None,
) -> Path:
    source = source or Path.home() / ".zshrc"
    destination = destination or PORTABLE_OUTPUT
    manifest_path = manifest_path or Path("artifacts/manifest.json")
    log_path = log_path or SANITIZATION_LOG
    ensure_directory(destination.parent)

    if not source.exists():
        raise FileNotFoundError(f"No .zshrc found at {source}")

    content = source.read_text(encoding="utf-8")
    content = apply_rules(content)
    content = strip_denylisted_aliases(content)

    destination.write_text(content, encoding="utf-8")
    checksum = sha256(destination.read_bytes()).hexdigest()
    console.print(f"[green]Wrote sanitized profile[/green] → {destination} (sha256={checksum})")

    _update_manifest(checksum, manifest_path)
    _append_log_entry(source, log_path)
    return destination


def _update_manifest(checksum: str, manifest: Path) -> None:
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest_data = {
        "name": "Portable Zsh profile",
        "path": "artifacts/zshrc.portable",
        "sha256": checksum,
    }
    if manifest.exists():
        with manifest.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
        artifacts = [
            item for item in data.get("artifacts", []) if item.get("path") != "artifacts/zshrc.portable"
        ]
        artifacts.append(manifest_data)
        data["artifacts"] = artifacts
    else:
        data = {
            "version": "1.0.0",
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source_machine": "sanitized",
            "artifacts": [manifest_data],
        }

    with manifest.open("w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2)
        fp.write("\n")


def _append_log_entry(source: Path, log_path: Path) -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    entry = f"- {timestamp}: Sanitized profile from {source} to artifacts/zshrc.portable\n"

    content = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    if entry.strip() in content:
        return

    with log_path.open("a", encoding="utf-8") as fp:
        if content and not content.endswith("\n\n"):
            fp.write("\n")
        fp.write(entry)
