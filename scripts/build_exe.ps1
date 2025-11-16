<#
.SYNOPSIS
    Скрипт для сборки nAUDIT в .exe файл

.DESCRIPTION
    Этот скрипт:
    1. Создаёт виртуальное окружение (если необходимо)
    2. Устанавливает зависимости
    3. Собирает .exe файл с помощью PyInstaller
    4. Проверяет результат

.NOTES
    Требует Python 3.8+
    Для правильной работы установите: Set-ExecutionPolicy Bypass -Scope Process -Force
#>

# Проверка наличия виртуального окружения
if (!(Test-Path -Path "./v.naudit")) {
    Write-Host "Создаём виртуальное окружение..." -ForegroundColor Cyan
    python -m venv v.naudit
    Write-Host "✓ Виртуальное окружение создано" -ForegroundColor Green
}

# Активируем виртуальное окружение
Write-Host "Активируем виртуальное окружение..." -ForegroundColor Cyan
& .\v.naudit\Scripts\Activate.ps1

# Обновляем pip
Write-Host "Обновляем pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Устанавливаем зависимости
Write-Host "Устанавливаем зависимости..." -ForegroundColor Cyan
python -m pip install -r requirements.txt
python -m pip install PyInstaller

# Устанавливаем пакет в режиме разработки
Write-Host "Установка пакета nAUDIT..." -ForegroundColor Cyan
pip install -e .

# Устанавливаем кодировку UTF-8
$env:PYTHONIOENCODING = 'utf-8'
chcp 65001 | Out-Null

# Запуск скрипта сборки
Write-Host "Запускаем сборку .exe файла..." -ForegroundColor Green
python build_exe.py

# Проверка результата
if (Test-Path -Path "./dist/nAUDIT.exe") {
    Write-Host "`n✓ Сборка завершена успешно!" -ForegroundColor Green
    Write-Host "Файл: ./dist/nAUDIT.exe" -ForegroundColor Yellow
    Write-Host "`nВы можете запустить приложение:` ./dist/nAUDIT.exe" -ForegroundColor Cyan
} else {
    Write-Host "`n✗ Ошибка при сборке. Проверьте логи выше." -ForegroundColor Red
    exit 1
}

Write-Host "`nДля деактивации виртуального окружения выполните: deactivate" -ForegroundColor Magenta
