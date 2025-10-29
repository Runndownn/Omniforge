<#
.SYNOPSIS
    Installs Windows Terminal, WSL, Oh My Zsh, plugins, and Nerd Fonts required by the portable profile.
.DESCRIPTION
    Wraps commands exposed by tool/installer.py so administrators can run prerequisite steps without the Python CLI.
#>
param(
    [switch]$IncludeWSL
)

$ErrorActionPreference = "Stop"

function Install-WindowsTerminal {
    if (Get-Command wt.exe -ErrorAction SilentlyContinue) {
        Write-Host "Windows Terminal already installed." -ForegroundColor Green
        return
    }

    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "Installing Windows Terminal via winget..." -ForegroundColor Cyan
        winget install --id Microsoft.WindowsTerminal -e --source winget --accept-package-agreements --accept-source-agreements
    }
    else {
        Write-Warning "winget not available. Opening Microsoft Store page."
        Start-Process "ms-windows-store://pdp/?productid=9N0DX20HK701"
    }
}

function Install-WSLIfRequested {
    if (-not $IncludeWSL) { return }
    Write-Host "Ensuring WSL is installed..." -ForegroundColor Cyan
    wsl.exe --status *>$null 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing WSL with Ubuntu-22.04..." -ForegroundColor Yellow
        wsl.exe --install -d Ubuntu-22.04
    }
}

function Invoke-PythonInstaller {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        throw "Python 3.10+ is required to run installer routines."
    }

    Write-Host "Invoking tool.installer bootstrap..." -ForegroundColor Cyan
    python -m tool.cli install --non-interactive
}

Install-WindowsTerminal
Install-WSLIfRequested
Invoke-PythonInstaller
