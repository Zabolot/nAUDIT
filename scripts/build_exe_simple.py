#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт сборки nAUDIT v3 с полной диагностикой и интерактивными графиками.
Включает все компоненты для работающего анализа и красивого интерфейса с matplotlib.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Установка кодировки вывода
if sys.stdout.encoding != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')


def main():
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    print("=" * 70)
    print("[*] nAUDIT v3 - СБОРКА ФИНАЛЬНОЙ ВЕРСИИ С ДИАГНОСТИКОЙ")
    print("=" * 70)
    
    # Очистка старых сборок
    print("\n[1/3] Очистка старых сборок...")
    for path in ["build", "dist"]:
        if (project_root / path).exists():
            shutil.rmtree(project_root / path)
            print(f"   [+] Удален: {path}/")
    
    for spec_file in project_root.glob("*.spec"):
        spec_file.unlink()
        print(f"   [+] Удален: {spec_file.name}")
    
    # Сборка
    print("\n[2/3] Сборка приложения (3-5 минут)...")
    print("   Используется: PyInstaller с полной коллекцией модулей")
    print("   Параметры:")
    print("     • --onefile (один файл)")
    print("     • --windowed (без консоли)")
    print("     • --collect-all для: n_audit, PyQt6, matplotlib")
    print()
    
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name=nAUDIT_v3",
        "--collect-all=n_audit",
        "--collect-all=PyQt6",
        "--collect-all=matplotlib",
        str(project_root / "n_audit" / "gui" / "main_app.py")
    ]
    
    result = subprocess.run(cmd, cwd=project_root)
    
    if result.returncode != 0:
        print("\n[✗] Сборка не удалась!")
        sys.exit(1)
    
    # Проверка результата
    print("\n[3/3] Проверка результата...")
    exe_file = project_root / "dist" / "nAUDIT_v3.exe"
    
    if exe_file.exists():
        size_mb = exe_file.stat().st_size / (1024 * 1024)
        print(f"   [+] Файл создан: {exe_file}")
        print(f"   [+] Размер: {size_mb:.1f} МБ")
    else:
        print(f"   [-] Файл не найден: {exe_file}")
        sys.exit(1)
    
    # Итоги
    print("\n" + "=" * 70)
    print("[SUCCESS] Сборка v3 завершена успешно!")
    print("=" * 70)
    print(f"\nПриложение: {exe_file}")
    print(f"\nУлучшения v3:")
    print("   [+] Полная диагностика процесса анализа")
    print("   [+] Интерактивные графики matplotlib")
    print("   [+] Реальные метрики вместо фейков")
    print("   [+] Проверка на пустые папки и отсутствие кода")
    print("   [+] История анализов с сохранением")
    print("   [+] Детальные логи и отчёты")
    print(f"\nЗапуск:")
    print(f"   {exe_file}")
    print()


if __name__ == "__main__":
    main()
