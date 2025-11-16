<#
.SYNOPSIS
    Быстрый запуск nAUDIT GUI приложения
.DESCRIPTION
    Этот скрипт подготавливает окружение и запускает nAUDIT
#>

param(
    [switch]$BuildExe = $false,
    [switch]$Help = $false
)

# Установка кодировки UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = 'utf-8'

if ($Help) {
    Write-Host "Использование: .\run_naudit.ps1 [параметры]"
    Write-Host ""
    Write-Host "Параметры:"
    Write-Host "  -BuildExe    Собрать .exe файл после запуска"
    Write-Host "  -Help        Показать эту справку"
    exit 0
}

$ProjectRoot = $PSScriptRoot
$VenvPath = Join-Path $ProjectRoot "v.naudit"

Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🚀 nAUDIT 2.0 — Быстрый запуск" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

# Проверка наличия виртуального окружения
Write-Host ""
Write-Host "[1/3] Подготовка окружения..." -ForegroundColor Yellow

if (!(Test-Path -Path $VenvPath)) {
    Write-Host "  Создание виртуального окружения..."
    python -m venv $VenvPath
    Write-Host "  ✓ Виртуальное окружение создано" -ForegroundColor Green
} else {
    Write-Host "  ✓ Виртуальное окружение существует" -ForegroundColor Green
}

# Активация виртуального окружения
& "$VenvPath\Scripts\Activate.ps1"

# Установка зависимостей
Write-Host ""
Write-Host "[2/3] Установка зависимостей..." -ForegroundColor Yellow

python -m pip install --upgrade pip 2>&1 | Out-Null
if (Test-Path -Path "$ProjectRoot\requirements.txt") {
    pip install -q -r "$ProjectRoot\requirements.txt"
    Write-Host "  ✓ Зависимости установлены" -ForegroundColor Green
}

# Установка пакета
pip install -q -e "$ProjectRoot"
Write-Host "  ✓ Пакет установлен" -ForegroundColor Green

# Запуск приложения
Write-Host ""
Write-Host "[3/3] Запуск nAUDIT GUI..." -ForegroundColor Yellow
Write-Host ""

python -m n_audit.gui.main_app

# Опция сборки .exe
if ($BuildExe) {
    Write-Host ""
    Write-Host "🔨 Сборка .exe файла..." -ForegroundColor Cyan
    & "$ProjectRoot\build_exe.ps1"
}

Write-Host ""
Write-Host "До встречи! 👋" -ForegroundColor Green
