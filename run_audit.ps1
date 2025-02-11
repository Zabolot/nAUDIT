# Запускается в PowerShell
# Если виртуальное окружение (venv) ещё не создано, создаём его
if (!(Test-Path -Path "./v.naudit")) {
    Write-Host "Виртуальное окружение не найдено. Создаём..."
    python -m venv v.naudit
}

# Активировать виртуальное окружение
Write-Host "Активируем виртуальное окружение..."
& .\v.naudit\Scripts\Activate.ps1

# Обновляем pip и устанавливаем зависимости проекта (на примере nAUDIT)
Write-Host "Обновляем pip и устанавливаем зависимости..."
python -m pip install --upgrade pip
# Если нужно установить пакет nAUDIT из исходников (убедитесь, что вы находитесь в каталоге nAUDIT)
Push-Location .\nAUDIT
python -m pip install -e .
Pop-Location

# Запускаем аудит проекта.
# В данном примере указываем модуль для аудита и исключаем тесты.
Write-Host "Запускаем аудит..."
python -m n_audit.main --module ..\crypto_trading_bot --report-level full --export-format html --verbose

# После завершения работы автоматически деактивируем виртуальное окружение
Write-Host "Аудит завершён. Деактивируем виртуальное окружение..."
deactivate

Write-Host "Готово. Отчёт и результаты аудита находятся в папке audit_results"