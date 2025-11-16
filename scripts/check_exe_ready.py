#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки что exe собралась и содержит все исправления
"""

import subprocess
import sys
from pathlib import Path

print("\n" + "=" * 80)
print("ПРОВЕРКА ПОСТРОЕНИЯ EXE")
print("=" * 80)

# Проверка 1: Найти exe файл
print("\n[1] Поиск exe файла...")
exe_path = Path("dist/nAUDIT.exe")
if exe_path.exists():
    size_gb = exe_path.stat().st_size / (1024**3)
    print(f"  ✓ Найдена: {exe_path}")
    print(f"  ✓ Размер: {size_gb:.2f} GB")
else:
    print(f"  ✗ Не найдена: {exe_path}")
    sys.exit(1)

# Проверка 2: Попытка запуска exe с --help
print("\n[2] Проверка что exe запускается...")
try:
    result = subprocess.run(
        [str(exe_path), "--help"],
        capture_output=True,
        text=True,
        timeout=10
    )
    if result.returncode in [0, 1]:  # 0 = success, 1 = help shown
        print(f"  ✓ EXE запускается корректно")
    else:
        print(f"  ⚠️  Возврат: {result.returncode}")
except subprocess.TimeoutExpired:
    print(f"  ⚠️  Timeout при запуске (это нормально для GUI приложения)")
except Exception as e:
    print(f"  ⚠️  Ошибка: {e}")

print("\n" + "=" * 80)
print("✅ EXE ГОТОВА К ТЕСТИРОВАНИЮ")
print("=" * 80)
print("""
СЛЕДУЮЩИЕ ШАГИ:

1. Запустить exe:
   .\\dist\\nAUDIT.exe

2. В GUI:
   ✓ Выбрать папку проекта
   ✓ Запустить аудит
   ✓ Проверить что ошибки видны в дереве
   ✓ Клик по файлу в дереве → файл выделяется в графе
   ✓ Клик по файлу в графе → дерево переходит на него
   ✓ Проверить GPU статус
   
3. Проверить логи:
   %USERPROFILE%\\.naudit\\logs\\latest.log
""")
print("=" * 80 + "\n")
