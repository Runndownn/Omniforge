"""Send Omniforge reports and artifacts to webhook-based messaging services."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from rich.console import Console

console = Console()


DEFAULT_BROADCAST_FILES = [
    Path("README.md"),
    Path("docs/SANITIZATION_REPORT.md"),
    Path("artifacts/manifest.json"),
]

ServiceMode = Literal["generic", "slack", "discord", "teams"]

DEFAULT_MAX_CHARS: dict[ServiceMode, int] = {
    "generic": 3500,
    "slack": 3500,
    "discord": 1900,
    "teams": 3500,
}


@dataclass
class MessagingConfig:
    webhook_url: str
    timeout_seconds: int = 15
    max_chars: int = DEFAULT_MAX_CHARS["generic"]
    service: ServiceMode = "generic"
    dry_run: bool = False


class MessagingError(RuntimeError):
    """Raised when webhook publication fails."""


def resolve_webhook_url(explicit_url: str | None = None) -> str:
    url = explicit_url or os.getenv("OMNIFORGE_WEBHOOK_URL")
    if not url:
        raise MessagingError(
            "Missing webhook URL. Provide --webhook-url or set OMNIFORGE_WEBHOOK_URL."
        )
    return url


def chunk_text(content: str, max_chars: int) -> list[str]:
    if max_chars <= 0:
        raise ValueError("max_chars must be greater than 0")
    if not content:
        return [""]

    chunks: list[str] = []
    cursor = 0
    length = len(content)
    while cursor < length:
        end = min(cursor + max_chars, length)
        chunks.append(content[cursor:end])
        cursor = end
    return chunks


def _post_json(config: MessagingConfig, payload: dict[str, str]) -> None:
    data = json.dumps(payload).encode("utf-8")
    request = Request(
        config.webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=config.timeout_seconds):
            return
    except HTTPError as exc:
        raise MessagingError(f"Webhook rejected request: HTTP {exc.code}") from exc
    except URLError as exc:
        raise MessagingError(f"Could not reach webhook endpoint: {exc.reason}") from exc


def build_payload(service: ServiceMode, text: str) -> dict[str, str]:
    if service == "discord":
        return {"content": text}
    if service == "teams":
        return {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "summary": "Omniforge broadcast",
            "text": text,
        }
    return {"text": text}


def resolve_max_chars(service: ServiceMode, override: int | None) -> int:
    if override is not None:
        return override
    return DEFAULT_MAX_CHARS[service]


def send_text(text: str, config: MessagingConfig) -> int:
    messages = chunk_text(text, config.max_chars)
    sent_count = 0
    for index, message in enumerate(messages, start=1):
        payload = build_payload(config.service, message)
        if config.dry_run:
            console.print(f"[cyan]DRY-RUN[/cyan] message {index}/{len(messages)}")
            console.print(message)
        else:
            _post_json(config, payload)
        sent_count += 1
    return sent_count


def _read_path(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def send_file(path: Path, config: MessagingConfig) -> int:
    if not path.exists() or not path.is_file():
        raise MessagingError(f"File not found: {path}")

    content = _read_path(path)
    parts = chunk_text(content, config.max_chars)
    sent_count = 0
    for part_index, part in enumerate(parts, start=1):
        text = f"[{path}] part {part_index}/{len(parts)}\n\n{part}"
        if config.dry_run:
            console.print(f"[cyan]DRY-RUN[/cyan] {path} part {part_index}/{len(parts)}")
        else:
            _post_json(config, build_payload(config.service, text))
        sent_count += 1
    return sent_count


def broadcast_files(paths: list[Path], config: MessagingConfig) -> int:
    published = 0
    for path in paths:
        published += send_file(path, config)
    return published
