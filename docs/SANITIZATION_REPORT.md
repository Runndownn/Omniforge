# SANITIZATION REPORT

**Version**: v1.0.0  
**Date**: 2025-10-29  
**Scope**: artifacts/zshrc.portable; artifacts/settings.json; Windows Terminal fonts/assets manifest

## Rules Applied

- Replace absolute user paths with `$HOME` or `%USERPROFILE%` (regex: `/(home|Users)/[^/]+/` → `$HOME/` and `C:\\Users\\[^\\]+` → `%USERPROFILE%`).
- Strip PAT/secret formats (`AKIA[A-Z0-9]{16}`, `ghp_[A-Za-z0-9]{36}`, `xox[pbar]-`, `Bearer\s+[A-Za-z0-9\-\._~+/]+=*`).
- Remove email addresses (`[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}`) and hostnames/IPs (`\b(?:\d{1,3}\.){3}\d{1,3}\b`).
- Drop aliases referencing destructive or sensitive tooling (`hashcat`, `rustscan`, `sqlmap`, `hydra`, `rm -rf /`).
- Normalize font references to distributable Nerd Fonts and align profile default to sanitized prompt.

## Preserved

- Prompt & color styling, including the two-line glyph-heavy prompt format.
- Safe plugins: `git`, `sudo`, `command-not-found`, `common-aliases`, `zsh-syntax-highlighting`, `zsh-autosuggestions`.
- Practical aliases (`py`, `ll`, `la`, `l`) and portable PATH adjustments.
- Windows Terminal color schemes, acrylic background, and profile commandlines once sanitized.

## Manual Review Flags

- Ensure any newly captured background images are either public-domain or replaced with provided defaults before publishing.
- Validate newly added plugins live under `vendor/plugins/` with compatible licenses.
- If additional aliases are introduced, confirm they do not reference red-flag tooling before exporting.
