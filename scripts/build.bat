@echo off
REM Скрипт для быстрой сборки nAUDIT v2.1.0 .exe файла
REM Используйте: запустите этот файл двойным щелчком или из cmd

cd /d %~dp0

echo.
echo ======================================================================
echo nAUDIT v2.1.0 - Сборка .exe файла
echo ======================================================================
echo.

REM Активируем venv
call v.naudit\Scripts\activate.bat

if errorlevel 1 (
    echo [!] Ошибка: виртуальное окружение не активировано
    pause
    exit /b 1
)

REM Проверяем наличие PyInstaller
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [!] PyInstaller не установлен
    echo [*] Установка PyInstaller...
    pip install PyInstaller --quiet
    if errorlevel 1 (
        echo [!] Ошибка при установке PyInstaller
        pause
        exit /b 1
    )
)

REM Запускаем сборку
echo [*] Запускаем сборку (это займет 2-3 минуты)...
echo.
python build_exe_v2_1.py

if errorlevel 1 (
    echo.
    echo [!] Ошибка при сборке
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo Сборка завершена успешно!
echo ======================================================================
echo.
echo Файл находится в: %cd%\dist\nAUDIT.exe
echo.
pause
