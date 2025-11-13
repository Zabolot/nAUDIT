#!/usr/bin/env pwsh
# nAUDIT v3 - Launcher script for PowerShell

Write-Host "================================================"
Write-Host " nAUDIT v3 - Code Analysis Audit Tool"
Write-Host "================================================"
Write-Host ""

$exePath = Join-Path $PSScriptRoot "dist" "nAUDIT_v3.exe"

if (Test-Path $exePath) {
    Write-Host "Starting nAUDIT_v3.exe..."
    Write-Host ""
    & $exePath
} else {
    Write-Host "[ERROR] nAUDIT_v3.exe not found!"
    Write-Host "Please run: python build_exe_simple.py"
    Read-Host "Press Enter to exit"
}
