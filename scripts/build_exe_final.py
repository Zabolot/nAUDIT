#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка nAUDIT.exe v2.2 (с граф-визуализацией)
PyInstaller build для финальной версии
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
import os

# Отключаем эмодзи - используем текст
print("\n" + "="*80)
print("СБОРКА NAUDIT.EXE v2.2".center(80))
print("="*80 + "\n")

# Проверка зависимостей
print("Проверка зависимостей...")

try:
    import PyInstaller
    print("  [OK] PyInstaller установлен\n")
except ImportError:
    print("  [ERROR] PyInstaller не установлен!")
    print("  Установка...")
    subprocess.run([sys.executable, "-m", "pip", "install", "PyInstaller", "--quiet"])
    print("  [OK] PyInstaller установлен\n")

# Проверка основного модуля
print("Проверка модулей...")

modules_to_check = [
    'n_audit',
    'n_audit.gui',
    'n_audit.gui.graph_visualizer',
    'n_audit.core',
]

for module in modules_to_check:
    try:
        __import__(module)
        print(f"  [OK] {module}")
    except ImportError as e:
        print(f"  [ERROR] {module}: {e}")
        sys.exit(1)

print()

# Подготовка к сборке
print("Подготовка к сборке...")

project_root = Path(__file__).parent
main_file = project_root / "src" / "main.py"

if not main_file.exists():
    print(f"  [ERROR] Файл {main_file} не найден!")
    sys.exit(1)

print(f"  [OK] Основной файл: {main_file}")

# Путь к иконке (если существует)
icon_path = project_root / "assets" / "icon.ico"
icon_args = []
if icon_path.exists():
    icon_args = [f"--icon={icon_path}"]
    print(f"  [OK] Иконка найдена: {icon_path}")

# Исключить ненужные файлы
excludes = [
    '--exclude-module=PyInstaller',
    '--exclude-module=pip',
    '--exclude-module=setuptools',
    '--exclude-module=tests',
]

print()
print("Запуск PyInstaller...")
print("-" * 80)

# Команда PyInstaller
cmd = [
    sys.executable,
    "-m", "PyInstaller",
    str(main_file),
    "--onefile",
    "--windowed",
    "--name=nAUDIT",
    "--distpath=dist",
    "--buildpath=build",
    "--specpath=.",
    "--noupx",
    "--log-level=INFO",
    *icon_args,
    *excludes,
]

# Добавить хиденную импорты для PyQt и других модулей
hidden_imports = [
    "--hidden-import=PyQt6",
    "--hidden-import=PyQt6.QtCore",
    "--hidden-import=PyQt6.QtGui",
    "--hidden-import=PyQt6.QtWidgets",
    "--hidden-import=PyQt6.QtWebEngineWidgets",
    "--hidden-import=plotly",
    "--hidden-import=plotly.graph_objects",
    "--hidden-import=pyvis",
    "--hidden-import=pyvis.network",
    "--hidden-import=networkx",
]

cmd.extend(hidden_imports)

# Выполнить сборку
result = subprocess.run(cmd)

if result.returncode == 0:
    print("-" * 80)
    print()
    print("СБОРКА УСПЕШНА!")
    print()
    
    exe_path = project_root / "dist" / "nAUDIT.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"Файл: {exe_path}")
        print(f"Размер: {size_mb:.1f} MB")
        print()
        print("Готово к использованию!")
    else:
        print(f"[WARNING] Файл {exe_path} не найден")
else:
    print("-" * 80)
    print()
    print("ОШИБКА СБОРКИ!")
    print(f"Код ошибки: {result.returncode}")
    sys.exit(result.returncode)
