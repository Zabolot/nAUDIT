#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отладка .exe файла с логами
Запускает .exe в подпроцессе и собирает все ошибки
"""

import subprocess
import sys
import time
import os
from pathlib import Path
from datetime import datetime

print("\n" + "="*70)
print("🔍 ОТЛАДКА .exe ФАЙЛА nAUDIT")
print("="*70)

exe_path = Path("G:\\CODING\\nAUDIT\\dist\\nAUDIT.exe")
log_file = Path("exe_debug_log.txt")

if not exe_path.exists():
    print(f"❌ ОШИБКА: Файл не найден: {exe_path}")
    sys.exit(1)

print(f"\n📁 Путь: {exe_path}")
print(f"📏 Размер: {exe_path.stat().st_size / 1024 / 1024:.1f} МБ")
print(f"⏰ Создан: {datetime.fromtimestamp(exe_path.stat().st_mtime)}")

print("\n" + "="*70)
print("🚀 Запуск .exe с логами (30 секунд)...")
print("="*70)

try:
    # Запускаем .exe и перенаправляем вывод
    process = subprocess.Popen(
        [str(exe_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    
    # Даем приложению 30 секунд на запуск
    try:
        stdout, stderr = process.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        print("⏱️  Timeout: приложение запустилось, но не завершилось за 30 сек")
        print("   (это может быть нормально для GUI приложения)")
        process.kill()
        stdout, stderr = process.communicate()
    
    # Пишем логи в файл
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("ВЫВОД STDOUT:\n")
        f.write("="*70 + "\n")
        f.write(stdout or "(пусто)\n")
        f.write("\n" + "="*70 + "\n")
        f.write("ВЫВОД STDERR:\n")
        f.write("="*70 + "\n")
        f.write(stderr or "(пусто)\n")
    
    # Выводим результаты
    print("\n📋 STDOUT:")
    print("-"*70)
    if stdout:
        print(stdout[:1000])
        if len(stdout) > 1000:
            print(f"... (остаток {len(stdout) - 1000} символов)")
    else:
        print("(пусто)")
    
    print("\n⚠️  STDERR:")
    print("-"*70)
    if stderr:
        print(stderr[:1000])
        if len(stderr) > 1000:
            print(f"... (остаток {len(stderr) - 1000} символов)")
    else:
        print("(пусто)")
    
    print(f"\n✅ Логи сохранены в {log_file}")
    
    # Проверяем на типичные ошибки
    print("\n" + "="*70)
    print("🔍 АНАЛИЗ ОШИБОК:")
    print("="*70)
    
    has_errors = False
    
    if "ModuleNotFoundError" in stderr or "ModuleNotFoundError" in stdout:
        print("❌ Обнаружена ошибка: ModuleNotFoundError")
        has_errors = True
    
    if "AttributeError" in stderr or "AttributeError" in stdout:
        print("❌ Обнаружена ошибка: AttributeError")
        has_errors = True
    
    if "ImportError" in stderr or "ImportError" in stdout:
        print("❌ Обнаружена ошибка: ImportError")
        has_errors = True
    
    if "Traceback" in stderr or "Traceback" in stdout:
        print("❌ Обнаружена ошибка: Exception/Traceback")
        has_errors = True
    
    if not has_errors:
        print("✅ Критических ошибок не обнаружено")
        print("ℹ️  Возможно, приложение запустилось нормально (GUI приложение)")
    
    print(f"\n📊 Код выхода: {process.returncode}")
    if process.returncode == 0:
        print("✅ Приложение завершилось с кодом 0 (успех)")
    elif process.returncode is None:
        print("⏱️  Приложение все еще работает")
    else:
        print(f"❌ Приложение завершилось с кодом ошибки: {process.returncode}")

except Exception as e:
    print(f"❌ ОШИБКА при запуске: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
print("🎯 ОТЛАДКА ЗАВЕРШЕНА")
print("="*70)
