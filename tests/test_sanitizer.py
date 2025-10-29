from pathlib import Path

from tool import sanitizer


def test_strip_denylisted_aliases(tmp_path: Path) -> None:
    source = tmp_path / ".zshrc"
    source.write_text("alias hashcat='hashcat --hz'\nalias py='python3'\n", encoding="utf-8")

    destination = sanitizer.sanitize_zshrc(
        source=source,
        destination=tmp_path / "portable",
        manifest_path=tmp_path / "manifest.json",
        log_path=tmp_path / "report.md",
    )

    content = destination.read_text(encoding="utf-8")
    assert "hashcat" not in content
    assert "alias py='python3'" in content
