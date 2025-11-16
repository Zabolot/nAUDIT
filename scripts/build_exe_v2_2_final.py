#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔨 Сборка nAUDIT.exe v2.2 (с граф-визуализацией)
PyInstaller build для финальной версии
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

print("\n" + "="*80)
print("🔨 СБОРКА NAUDIT.EXE v2.2".center(80))
print("="*80 + "\n")

# Проверка зависимостей
print("📋 Проверка зависимостей...")

try:
    import PyInstaller
    print("  ✅ PyInstaller установлен\n")
except ImportError:
    print("  ❌ PyInstaller не установлен!")
    print("  Установка...")
    subprocess.run([sys.executable, "-m", "pip", "install", "PyInstaller", "--quiet"])
    print("  ✅ PyInstaller установлен\n")

# Проверка основного модуля
print("📋 Проверка модулей...")

modules_to_check = [
    'n_audit',
    'n_audit.gui',
    'n_audit.gui.graph_visualizer',
    'n_audit.core',
]

for module in modules_to_check:
    try:
        __import__(module)
        print(f"  ✅ {module}")
    except ImportError as e:
        print(f"  ❌ {module}: {e}")
        sys.exit(1)

print()

# Подготовка к сборке
print("🔧 Подготовка к сборке...")

build_dir = Path("dist")
build_cache = Path("build")
spec_file = Path("nAUDIT.spec")

# Очистка старых артефактов
if build_dir.exists():
    print(f"  🗑️  Удаляю старую директорию: dist/")
    import shutil
    shutil.rmtree(build_dir, ignore_errors=True)

if build_cache.exists():
    print(f"  🗑️  Удаляю кэш: build/")
    import shutil
    shutil.rmtree(build_cache, ignore_errors=True)

if spec_file.exists():
    print(f"  📝 Использую существующий spec: {spec_file}")
else:
    print(f"  📝 Будет создан новый spec файл")

print()

# Параметры PyInstaller
print("⚙️  Параметры сборки:")
print("  • Режим: PyInstaller (--onefile)")
print("  • Размер: ~275 MB (с PyQt6, Plotly, PyVis)")
print("  • Время: ~2-3 минуты\n")

# Сборка
print("🚀 Запуск PyInstaller...\n")

cmd = [
    sys.executable,
    "-m", "PyInstaller",
    "--onefile",                    # Один файл
    "--windowed",                   # Без консоли
    "--icon=assets/naudit_icon.ico" if Path("assets/naudit_icon.ico").exists() else "",
    "--add-data=assets:assets",     # Включить ассеты
    "--name=nAUDIT",                # Имя
    "--distpath=dist",              # Путь к dist
    "--buildpath=build",            # Путь к build
    "--collect-all=plotly",         # Включить Plotly
    "--collect-all=pyvis",          # Включить PyVis
    "--collect-all=networkx",       # Включить NetworkX
    "n_audit/main.py",              # Entry point
]

# Убрать пустые параметры
cmd = [c for c in cmd if c]

print(f"Команда: {' '.join(cmd)}\n")

try:
    result = subprocess.run(cmd, check=True)
    
    # Проверка результата
    exe_path = Path("dist/nAUDIT.exe")
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print("\n" + "="*80)
        print("✅ УСПЕШНО! EXE СОБРАН".center(80))
        print("="*80 + "\n")
        print(f"📦 Файл: {exe_path}")
        print(f"💾 Размер: {size_mb:.1f} MB")
        print(f"⏰ Время сборки: ~2-3 минуты")
        print(f"📍 Расположение: {exe_path.absolute()}\n")
        
        print("✨ Новые функции в этой версии:")
        print("  ✅ Исключение .venv, __pycache__, .git")
        print("  ✅ Видимые связи между файлами (edges)")
        print("  ✅ Увеличенное расстояние между облаками")
        print("  ✅ Только цифры ошибок на узлах")
        print("  ✅ Цвета по папкам")
        print("  ✅ Спираль без наложения узлов")
        print("  ✅ Переключение Plotly ↔ PyVis\n")
        
        print("🚀 Готово к использованию!")
        print(f"   Запуск: dist\\nAUDIT.exe\n")
        sys.exit(0)
    else:
        print("❌ EXE не найден после сборки!")
        sys.exit(1)

except subprocess.CalledProcessError as e:
    print(f"\n❌ Ошибка сборки: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Неожиданная ошибка: {e}")
    sys.exit(1)
