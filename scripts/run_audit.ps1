//// filepath: /f:/CryptoPenXL/CryptoPenetratorXL_Bot/nAUDIT/run_audit.ps1
<#
.SYNOPSIS
    Полный аудит и анализ Python-проекта с подробным логированием.

.DESCRIPTION
    Скрипт проверяет наличие и при необходимости создаёт виртуальное окружение, активирует его,
    обновляет pip, устанавливает зависимости и последовательно запускает:
      - основной аудит (статический анализ, генерация отчётов)
      - анализ покрытия тестов
      - проверку безопасности
      - генерацию визуализаций
      - запуск дополнительных плагинов
    После завершения выводит сводку и длительность аудита.

.NOTES
    Для деактивации виртуального окружения завершите сессию PowerShell или выполните 'exit'.
#>

# Проверка наличия виртуального окружения, создание при отсутствии
if (!(Test-Path -Path "./v.naudit")) {
    Write-Host "Создаём виртуальное окружение..." -ForegroundColor Cyan
    python -m venv v.naudit
}

# Активируем виртуальное окружение
Write-Host "Активируем виртуальное окружение..." -ForegroundColor Cyan
& .\v.naudit\Scripts\Activate.ps1

# Обновляем pip и устанавливаем зависимости
Write-Host "Обновляем pip и устанавливаем зависимости..." -ForegroundColor Cyan
python -m pip install --upgrade pip
Push-Location .\n_audit
python -m pip install -e .
Pop-Location

# Устанавливаем кодировку UTF-8 для консоли
$env:PYTHONIOENCODING = 'utf-8'
chcp 65001 | Out-Null

# Фиксируем время начала аудита
$startTime = Get-Date

Write-Host "Запускаем аудит..." -ForegroundColor Green
try {
    Write-Host "[*] Выполнение основного аудита..." -ForegroundColor Cyan
    python -m n_audit.main --module ..\crypto_trading_bot --report-level full --export-format html --verbose

    Write-Host "[*] Запуск анализа тестового покрытия..." -ForegroundColor Cyan
    python -m n_audit.tests_analysis --module ..\crypto_trading_bot

    Write-Host "[*] Запуск проверки безопасности..." -ForegroundColor Cyan
    python -m n_audit.security --module ..\crypto_trading_bot

    Write-Host "[*] Генерация визуализаций..." -ForegroundColor Cyan
    python -m n_audit.visualizations --reports-dir "audit_results\reports"

    Write-Host "[*] Запуск дополнительных плагинов..." -ForegroundColor Cyan
    python -m n_audit.core --run-plugins
} catch {
    Write-Error "Ошибка при выполнении аудита: $_"
    exit 1
}

# Фиксируем время завершения аудита и вычисляем продолжительность
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host "Аудит завершён успешно." -ForegroundColor Green
Write-Host ("Общая длительность аудита: {0:hh\:mm\:ss}" -f $duration) -ForegroundColor Yellow
Write-Host "Полные отчёты доступны в папке audit_results."
Write-Host "Для деактивации виртуального окружения завершите сессию PowerShell или выполните 'exit'." -ForegroundColor Magenta

# При необходимости автоматического завершения (раскомментируйте следующую строку):
# exit