#!/usr/bin/env python3
"""
Скрипт сборки nAUDIT v2.1.exe с УЛУЧШЕНИЯМИ.
Включает все компоненты для работающего анализа и красивого интерфейса.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def main():
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    print("=" * 70)
    print("[*] nAUDIT v2.1 - СБОРКА УЛУЧШЕННОГО .EXE")
    print("=" * 70)
    
    # Очистка старых сборок
    print("\n[1/3] Очистка старых сборок...")
    for path in ["build", "dist"]:
        if (project_root / path).exists():
            shutil.rmtree(project_root / path)
            print(f"   ✓ Удален: {path}/")
    
    for spec_file in project_root.glob("*.spec"):
        spec_file.unlink()
        print(f"   ✓ Удален: {spec_file.name}")
    
    # Сборка - ВСЕ НЕОБХОДИМЫЕ МОДУЛИ
    print("\n[2/3] Сборка приложения (2-3 минуты)...")
    print("   Используется: PyInstaller с --collect-all")
    print("   Параметры:")
    print("     • --onefile (один файл)")
    print("     • --windowed (без консоли)")
    print("     • --collect-all=n_audit (все модули анализа)")
    print("     • --collect-all=PyQt6 (все компоненты PyQt6)")
    print("     • --collect-all=matplotlib (графики)")
    print()
    
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name=nAUDIT",
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
    exe_file = project_root / "dist" / "nAUDIT.exe"
    
    if exe_file.exists():
        size_mb = exe_file.stat().st_size / (1024 * 1024)
        print(f"   ✓ Файл создан: {exe_file}")
        print(f"   ✓ Размер: {size_mb:.1f} МБ")
    else:
        print(f"   ✗ Файл не найден: {exe_file}")
        sys.exit(1)
    
    # Итоги
    print("\n" + "=" * 70)
    print("[SUCCESS] Сборка v2.1 завершена успешно!")
    print("=" * 70)
    print(f"\nПриложение: {exe_file}")
    print(f"\nУлучшения v2.1:")
    print("   ✓ Реальный анализ кода (не фейковые результаты)")
    print("   ✓ Работающий экспорт (JSON + HTML)")
    print("   ✓ Улучшенный интерфейс с прогрессом")
    print("   ✓ Визуализация результатов")
    print(f"\nЗапуск:")
    print(f"   {exe_file}")
    print()


if __name__ == "__main__":
    main()
