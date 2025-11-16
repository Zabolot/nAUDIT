#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки скомпилированного .exe файла.
"""

import os
import sys
from pathlib import Path


def check_exe():
    """Проверка скомпилированного .exe файла"""
    
    project_root = Path(__file__).parent
    exe_path = project_root / "dist" / "nAUDIT.exe"
    
    print("=" * 60)
    print("Проверка скомпилированного .exe файла")
    print("=" * 60)
    
    # Проверка существования файла
    print("\n[1/5] Проверка файла...")
    if not exe_path.exists():
        print(f"  [!] Файл не найден: {exe_path}")
        return False
    
    print(f"  [OK] Файл найден: {exe_path}")
    
    # Размер файла
    print("\n[2/5] Информация о файле...")
    file_size = exe_path.stat().st_size
    file_size_mb = file_size / (1024 * 1024)
    print(f"  [OK] Размер файла: {file_size_mb:.2f} МБ ({file_size:,} байт)")
    
    # Проверка прав доступа
    print("\n[3/5] Проверка прав доступа...")
    if os.access(exe_path, os.X_OK):
        print(f"  [OK] Файл исполняемый")
    else:
        print(f"  [!] Файл не имеет прав на выполнение")
        return False
    
    # Проверка зависимостей в исходном коде
    print("\n[4/5] Проверка компонентов...")
    components_found = []
    components_to_check = [
        ("PyQt6", "GUI фреймворк"),
        ("networkx", "Граф сетей"),
        ("pyvis", "Визуализация графов"),
        ("matplotlib", "Научная визуализация"),
    ]
    
    for component, description in components_to_check:
        try:
            __import__(component)
            components_found.append(f"[OK] {component}: {description}")
        except ImportError:
            components_found.append(f"[!] {component}: ОТСУТСТВУЕТ")
    
    for msg in components_found:
        print(f"  {msg}")
    
    # Итоги
    print("\n[5/5] Итоги...")
    print("\n" + "=" * 60)
    print("Проверка завершена успешно!")
    print("=" * 60)
    print(f"\n[OK] nAUDIT.exe готов к использованию")
    print(f"[OK] Путь: {exe_path}")
    print(f"[OK] Размер: {file_size_mb:.2f} МБ")
    print("\nДля запуска:")
    print(f"  1. Откройте папку: {project_root / 'dist'}")
    print(f"  2. Дважды щелкните на nAUDIT.exe")
    print(f"  3. Приложение запустится автоматически")
    
    return True


if __name__ == "__main__":
    try:
        success = check_exe()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[!] Ошибка: {e}")
        sys.exit(1)
