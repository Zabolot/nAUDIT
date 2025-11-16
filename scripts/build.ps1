#!/usr/bin/env pwsh
# Скрипт для быстрой сборки nAUDIT v2.1.0 .exe файла
# Использование: .\build.ps1

Set-Location $PSScriptRoot

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "nAUDIT v2.1.0 - Быстрая сборка .exe файла" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Активируем venv
Write-Host "[*] Активация виртуального окружения..." -ForegroundColor Yellow
. .\v.naudit\Scripts\Activate.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Ошибка: виртуальное окружение не активировано" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host "[OK] Виртуальное окружение активировано" -ForegroundColor Green
Write-Host ""

# Проверяем PyInstaller
Write-Host "[*] Проверка PyInstaller..." -ForegroundColor Yellow
python -c "import PyInstaller" 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] PyInstaller не установлен" -ForegroundColor Red
    Write-Host "[*] Установка PyInstaller..." -ForegroundColor Yellow
    pip install PyInstaller --quiet
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[!] Ошибка при установке PyInstaller" -ForegroundColor Red
        Read-Host "Нажмите Enter для выхода"
        exit 1
    }
}

Write-Host "[OK] PyInstaller готов" -ForegroundColor Green
Write-Host ""

# Запускаем сборку
Write-Host "[*] Запускаем сборку..." -ForegroundColor Yellow
Write-Host "[*] Время сборки: ~2-3 минуты" -ForegroundColor Cyan
Write-Host ""

python build_exe_v2_1.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[!] Ошибка при сборке" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "Сборка завершена успешно!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
Write-Host ""

$exePath = Join-Path $PSScriptRoot "dist\nAUDIT.exe"
if (Test-Path $exePath) {
    $size = (Get-Item $exePath).Length / 1MB
    Write-Host "[OK] Файл создан: $exePath" -ForegroundColor Green
    Write-Host "[OK] Размер: $([Math]::Round($size, 2)) МБ" -ForegroundColor Green
} else {
    Write-Host "[!] Файл не найден: $exePath" -ForegroundColor Red
}

Write-Host ""
Write-Host "Для запуска: & `"$exePath`"" -ForegroundColor Cyan
Write-Host ""

Read-Host "Нажмите Enter для выхода"
