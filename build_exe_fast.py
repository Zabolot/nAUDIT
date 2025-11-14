#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для построения nAUDIT v2.1.0 .exe - Оптимизированная версия

Использует PyInstaller для создания standalone exe.
Оптимизирована для быстрой сборки.
"""

import sys
import subprocess
from pathlib import Path
import shutil
import os


def build_exe():
    """Построить .exe файл nAUDIT v2.1.0 (оптимизированная версия)"""
    
    print("=" * 70)
    print("nAUDIT v2.1.0 - Построение .exe файла (БЫСТРАЯ ВЕРСИЯ)")
    print("=" * 70)
    
    # Путь к проекту
    project_root = Path(__file__).parent
    
    # Точка входа
    entry_point = project_root / "n_audit" / "gui" / "main_app.py"
    
    if not entry_point.exists():
        print(f"\n[!] Точка входа не найдена: {entry_point}")
        return False
    
    # Пути для сборки
    build_dir = project_root / 'build'
    dist_dir = project_root / 'dist'
    work_dir = build_dir / 'work'
    
    # Очищаем старые сборки
    print("\n[1/6] Очистка старых сборок...")
    
    for cleanup_dir in [dist_dir, work_dir]:
        if cleanup_dir.exists():
            print(f"  Удаляется: {cleanup_dir}")
            shutil.rmtree(cleanup_dir, ignore_errors=True)
    
    # Определяем путь к pyinstaller в venv
    print("\n[2/6] Проверка PyInstaller...")
    
    if sys.platform == "win32":
        pyinstaller_path = project_root / "v.naudit" / "Scripts" / "pyinstaller.exe"
    else:
        pyinstaller_path = project_root / "v.naudit" / "bin" / "pyinstaller"
    
    try:
        result = subprocess.run([str(pyinstaller_path), "--version"], 
                              capture_output=True, encoding="utf-8", timeout=5)
        if result.returncode == 0:
            print(f"  [OK] PyInstaller {result.stdout.strip()}")
        else:
            print(f"  [!] PyInstaller ошибка: {result.stderr}")
            return False
    except FileNotFoundError:
        print(f"  [!] PyInstaller не найден в: {pyinstaller_path}")
        return False
    
    # Минимальный набор скрытых импортов (только необходимые для v2.1.0)
    print("\n[3/6] Подготовка параметров сборки...")
    
    hidden_imports = [
        # PyQt6
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtWebEngineCore",
        
        # nAUDIT ядро
        "n_audit.core",
        "n_audit.code_analysis",
        "n_audit.security",
        "n_audit.gui.main_window_v4",
        "n_audit.gui.tree_widget",
        "n_audit.gui.graph_visualizer",
        "n_audit.gui.error_visualization",
        
        # Граф визуализация
        "networkx",
        "pyvis",
        "matplotlib",
    ]
    
    print(f"  Скрытых импортов: {len(hidden_imports)}")
    print(f"  Точка входа: {entry_point}")
    print(f"  Выходной каталог: {dist_dir}")
    
    # Построение команды PyInstaller (минимальная)
    print("\n[4/6] Построение команды сборки...")
    
    cmd = [
        str(pyinstaller_path),
        "--onefile",                           # Один файл
        "--windowed",                          # Без консоли
        "--name=nAUDIT",                       # Имя exe
        f"--distpath={dist_dir}",              # Путь для .exe
        f"--workpath={work_dir}",              # Рабочая папка
        f"--specpath={build_dir}",             # Путь для .spec
        "--noupx",                             # Без UPX сжатия
        "-y",                                  # Перезаписать без вопросов
    ]
    
    # Добавление скрытых импортов
    for hidden_import in hidden_imports:
        cmd.extend(["--hidden-import", hidden_import])
    
    # Точка входа
    cmd.append(str(entry_point))
    
    print(f"  Команда: pyinstaller --onefile --windowed ...")
    print(f"  Всего параметров: {len(cmd)}")
    
    # Запуск PyInstaller
    print("\n[5/6] Запуск PyInstaller...")
    print("-" * 70)
    
    try:
        result = subprocess.run(cmd, cwd=str(project_root), timeout=600)  # 10 минут
        if result.returncode != 0:
            print("-" * 70)
            print(f"\n[!] PyInstaller вернул код ошибки: {result.returncode}")
            return False
    except subprocess.TimeoutExpired:
        print("-" * 70)
        print("\n[!] Сборка превышила время ожидания (10 минут)")
        return False
    except Exception as e:
        print("-" * 70)
        print(f"\n[!] Ошибка при запуске PyInstaller: {e}")
        return False
    
    print("-" * 70)
    
    # Проверка результата
    print("\n[6/6] Проверка результата...")
    
    exe_path = dist_dir / "nAUDIT.exe"
    
    if exe_path.exists():
        file_size = exe_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        
        print(f"  [OK] Файл успешно создан!")
        print(f"  [OK] Путь: {exe_path}")
        print(f"  [OK] Размер: {file_size_mb:.2f} МБ")
        
        print("\n" + "=" * 70)
        print("Сборка завершена успешно!")
        print("=" * 70)
        print(f"\nФайл готов к использованию:")
        print(f"  nAUDIT.exe ({file_size_mb:.0f} МБ)")
        print(f"\nДля запуска приложения:")
        print(f"  - Двойной щелчок по {exe_path.name}")
        print(f"  - Или: & '{exe_path}'")
        
        return True
    else:
        print(f"  [!] Файл не найден: {exe_path}")
        return False


if __name__ == '__main__':
    try:
        success = build_exe()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[!] Сборка отменена пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
