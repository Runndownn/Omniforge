from pathlib import Path

from tool.messaging import MessagingConfig, broadcast_files, build_payload, chunk_text, resolve_max_chars


def test_chunk_text_splits_by_max_chars() -> None:
    chunks = chunk_text("abcdef", 2)
    assert chunks == ["ab", "cd", "ef"]


def test_broadcast_files_dry_run_counts_chunks(tmp_path: Path) -> None:
    target = tmp_path / "report.txt"
    target.write_text("abcdefghij", encoding="utf-8")

    config = MessagingConfig(
        webhook_url="https://example.invalid/webhook",
        max_chars=4,
        dry_run=True,
    )

    sent = broadcast_files([target], config)
    assert sent == 3


def test_build_payload_by_service_mode() -> None:
    assert build_payload("generic", "hello") == {"text": "hello"}
    assert build_payload("slack", "hello") == {"text": "hello"}
    assert build_payload("discord", "hello") == {"content": "hello"}
    assert build_payload("teams", "hello")["@type"] == "MessageCard"


def test_resolve_max_chars_uses_service_default_when_unset() -> None:
    assert resolve_max_chars("discord", None) == 1900
    assert resolve_max_chars("slack", None) == 3500
    assert resolve_max_chars("teams", 1200) == 1200
