"""Install prerequisites for the portable profile."""

from __future__ import annotations

import platform
import shutil
import subprocess
from collections.abc import Sequence
from pathlib import Path

from rich.console import Console

console = Console()

NERD_FONT_URL = "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.1.1/CascadiaCode.zip"
FONT_NAME = "Cascadia Code"  # sanitized base font


def _run(command: Sequence[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    console.print(f"[cyan]$ {' '.join(command)}")
    return subprocess.run(command, check=check, text=True)


def install_windows_terminal() -> None:
    if shutil.which("wt.exe"):
        console.print("[green]Windows Terminal already installed[/green]")
        return
    if shutil.which("winget"):
        _run(
            [
                "winget",
                "install",
                "--id",
                "Microsoft.WindowsTerminal",
                "-e",
                "--source",
                "winget",
                "--accept-package-agreements",
                "--accept-source-agreements",
            ]
        )
    else:
        console.print(
            "[red]winget not available[/red]. Please install Windows Terminal from the Microsoft Store.",
        )


def install_wsl(distro: str = "Ubuntu-22.04") -> None:
    if platform.system().lower() != "windows":
        console.print("[yellow]Skipping WSL install on non-Windows host[/yellow]")
        return
    status = subprocess.run(["wsl.exe", "--status"], check=False, capture_output=True, text=True)
    if status.returncode == 0:
        console.print("[green]WSL already installed[/green]")
        return
    _run(["wsl.exe", "--install", "-d", distro])


def install_oh_my_zsh(target_dir: Path) -> None:
    if target_dir.exists():
        console.print("[green]Oh My Zsh already vendored[/green]")
        return
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    _run(
        [
            "git",
            "clone",
            "https://github.com/ohmyzsh/ohmyzsh",
            str(target_dir),
            "--depth",
            "1",
        ]
    )


def install_plugin(name: str, repo: str, destination: Path) -> None:
    if (destination / name).exists():
        console.print(f"[green]{name} already present[/green]")
        return
    destination.mkdir(parents=True, exist_ok=True)
    _run(["git", "clone", repo, str(destination / name), "--depth", "1"])


def install_font() -> None:
    if platform.system().lower() != "windows":
        console.print("[yellow]Skipping font install on non-Windows host[/yellow]")
        return
    fonts_dir = Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    tmp_zip = Path("./fonts.zip")
    _run(["powershell", "-Command", f"Invoke-WebRequest -Uri {NERD_FONT_URL} -OutFile {tmp_zip}"])
    _run(["powershell", "-Command", f"Expand-Archive -LiteralPath {tmp_zip} -DestinationPath {fonts_dir}"], check=False)
    tmp_zip.unlink(missing_ok=True)
    console.print(f"[green]Installed {FONT_NAME} Nerd Font[/green]")


def install_prerequisites(non_interactive: bool = False, include_wsl: bool = True) -> None:
    install_windows_terminal()
    if include_wsl:
        install_wsl()
    vendor_dir = Path("vendor")
    install_oh_my_zsh(vendor_dir / "oh-my-zsh")
    install_plugin("zsh-syntax-highlighting", "https://github.com/zsh-users/zsh-syntax-highlighting", vendor_dir / "plugins")
    install_plugin("zsh-autosuggestions", "https://github.com/zsh-users/zsh-autosuggestions", vendor_dir / "plugins")
    install_font()
    if not non_interactive:
        console.print("[green]Prerequisites installed. You can now run export and sanitize steps.[/green]")
