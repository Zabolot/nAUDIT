#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка nAUDIT.exe v2.3 с АКТИВИРОВАННЫМ виртуальным окружением
PyInstaller build для финальной версии
"""

import sys
import subprocess
import os
from pathlib import Path
from datetime import datetime

# Определить пути
PROJECT_ROOT = Path(__file__).parent
VENV_ACTIVATE = PROJECT_ROOT / "v.naudit" / "Scripts" / "Activate.ps1"
VENV_PYTHON = PROJECT_ROOT / "v.naudit" / "Scripts" / "python.exe"

print("\n" + "="*80)
print("СБОРКА NAUDIT.EXE v2.3")
print("="*80 + "\n")

# Проверяем, что используется Python из виртуального окружения
print(f"[INFO] Текущий Python: {sys.executable}")
print(f"[INFO] Версия Python: {sys.version}")
print(f"[INFO] Виртуальное окружение: {PROJECT_ROOT / 'v.naudit'}")
print()

# Проверка основного модуля
print("Проверка модулей...")
print("-" * 80)

modules_to_check = [
    'n_audit',
    'n_audit.gui',
    'n_audit.gui.graph_visualizer',
]

all_ok = True
for module in modules_to_check:
    try:
        __import__(module)
        print(f"  [OK] {module}")
    except ImportError as e:
        print(f"  [ERROR] {module}: {e}")
        all_ok = False

if not all_ok:
    print("\n[ERROR] Некоторые модули не найдены!")
    sys.exit(1)

print()

# Проверка зависимостей
print("Проверка зависимостей...")
print("-" * 80)

dependencies = [
    ('PyQt6', 'PyQt6'),
    ('PyInstaller', 'PyInstaller'),
    ('plotly', 'plotly'),
    ('pyvis', 'pyvis'),
    ('networkx', 'networkx'),
    ('requests', 'requests'),
    ('pydantic', 'pydantic'),
]

for dep_name, import_name in dependencies:
    try:
        __import__(import_name)
        print(f"  [OK] {dep_name}")
    except ImportError:
        print(f"  [ERROR] {dep_name} - установка...")
        subprocess.run([sys.executable, "-m", "pip", "install", dep_name, "--quiet"], check=False)

print()

# Подготовка к сборке
print("Подготовка к сборке...")
print("-" * 80)

# Поиск main.py в правильном месте
main_file = PROJECT_ROOT / "n_audit" / "main.py"

if not main_file.exists():
    print(f"[INFO] Основной файл не найден по пути: n_audit/main.py")
    print(f"[INFO] Поиск в других местах...")
    
    # Попытаться найти main.py в других местах
    possible_mains = []
    for m in PROJECT_ROOT.rglob("main.py"):
        # Исключить файлы из виртуального окружения и третьих библиотек
        if 'v.naudit' not in str(m) and 'site-packages' not in str(m):
            possible_mains.append(m)
    
    if possible_mains:
        print(f"[INFO] Найдено {len(possible_mains)} файлов main.py:")
        for m in possible_mains[:3]:
            print(f"       - {m.relative_to(PROJECT_ROOT)}")
        main_file = possible_mains[0]
        print(f"[INFO] Используем: {main_file.relative_to(PROJECT_ROOT)}")
    else:
        print("[ERROR] main.py не найден!")
        sys.exit(1)

print(f"[OK] Основной файл: {main_file.relative_to(PROJECT_ROOT)}")

# Проверить иконку
icon_path = PROJECT_ROOT / "assets" / "icon.ico"
icon_args = []
if icon_path.exists():
    icon_args = [f"--icon={icon_path}"]
    print(f"[OK] Иконка найдена")
else:
    print(f"[INFO] Иконка не найдена (будет использована по умолчанию)")

print()

# Параметры сборки
print("Параметры сборки:")
print("-" * 80)

distpath = PROJECT_ROOT / "dist"
buildpath = PROJECT_ROOT / "build_v2_3"

print(f"  [*] Выходной файл: {distpath / 'nAUDIT.exe'}")
print(f"  [*] Сборка в: {buildpath}")
print(f"  [*] Режим: --onefile --windowed")
print()

# Команда PyInstaller
print("Запуск PyInstaller...")
print("-" * 80)

cmd = [
    sys.executable,
    "-m", "PyInstaller",
    str(main_file),
    "--onefile",
    "--windowed",
    "--name=nAUDIT",
    f"--distpath={distpath}",
    "--specpath=.",
    "--noupx",
    "--log-level=INFO",
    *icon_args,
    # Исключить ненужное
    "--exclude-module=PyInstaller",
    "--exclude-module=pip",
    "--exclude-module=setuptools",
    # Включить скрытые импорты
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

print(f"Команда: {' '.join(cmd[:5])} ...\n")

# Выполнить сборку
start_time = datetime.now()
result = subprocess.run(cmd, cwd=PROJECT_ROOT)
end_time = datetime.now()
build_time = (end_time - start_time).total_seconds()

print()
print("-" * 80)

if result.returncode == 0:
    print()
    print("СБОРКА УСПЕШНА!")
    print()
    
    exe_path = distpath / "nAUDIT.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"Файл: {exe_path.name}")
        print(f"Размер: {size_mb:.1f} MB")
        print(f"Время сборки: {build_time:.1f} сек ({build_time/60:.1f} мин)")
        print()
        print("✓ Готово к использованию!")
        print()
        print(f"Расположение: {exe_path}")
    else:
        print(f"[WARNING] Файл {exe_path} не найден")
else:
    print()
    print("ОШИБКА СБОРКИ!")
    print(f"Код ошибки: {result.returncode}")
    print(f"Время попытки: {build_time:.1f} сек")
    sys.exit(result.returncode)

print("="*80 + "\n")
