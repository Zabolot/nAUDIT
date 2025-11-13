#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Оптимизированный скрипт для построения nAUDIT v4.0 .exe

Минимизирует размер за счет исключения ненужных модулей и баз данных.
"""

import sys
import subprocess
from pathlib import Path
import shutil


def build_exe():
    """Построить оптимизированный .exe"""
    print("[*] Building nAUDIT v4.0 executable (OPTIMIZED)...")
    
    # Путь к проекту
    project_root = Path(__file__).parent
    
    # Точка входа
    entry_point = project_root / "run_naudit_gui.py"
    
    if not entry_point.exists():
        print(f"[✗] Entry point not found: {entry_point}")
        return False
    
    # Полный путь к n_audit модулю
    n_audit_path = project_root / "n_audit"
    if not n_audit_path.exists():
        print(f"[✗] n_audit module not found: {n_audit_path}")
        return False
    
    # Пути для сборки
    build_dir = project_root / 'build'
    dist_dir = project_root / 'dist'
    work_dir = build_dir / 'work_optimized'
    
    # Очищаем старые сборки
    if (dist_dir / 'nAUDIT_v4.exe').exists():
        print("[*] Removing old build...")
        (dist_dir / 'nAUDIT_v4.exe').unlink()
    
    if work_dir.exists():
        print("[*] Cleaning work directory...")
        shutil.rmtree(work_dir, ignore_errors=True)
    
    # Команда PyInstaller с оптимизацией
    cmd = [
        'pyinstaller',
        '--onefile',                                    # Один файл
        '--console',                                    # Консоль для вывода
        '--name=nAUDIT_v4',                            # Имя exe
        '--distpath=' + str(dist_dir),                 # Путь для exe
        '--workpath=' + str(work_dir),                 # Рабочая папка
        '--specpath=' + str(build_dir),                # Spec файлы
        '--add-data=' + str(n_audit_path) + ':n_audit',
        '--add-data=' + str(project_root / 'assets') + ':assets',
        
        # Скрытые импорты только нужные
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtGui',
        '--hidden-import=PyQt6.QtWidgets',
        '--hidden-import=matplotlib.backends.backend_qt5agg',
        '--hidden-import=matplotlib.figure',
        '--hidden-import=matplotlib.pyplot',
        '--hidden-import=pylint.lint',
        '--hidden-import=flake8.api.legacy',
        
        # Исключаем ненужные модули для уменьшения размера
        '--exclude-module=matplotlib.tests',
        '--exclude-module=matplotlib.sphinxext',
        '--exclude-module=matplotlib.mpl-data',
        '--exclude-module=tkinter',
        '--exclude-module=tcl',
        '--exclude-module=tk',
        '--exclude-module=PIL',
        '--exclude-module=numpy.tests',
        '--exclude-module=scipy',
        '--exclude-module=pandas',
        '--exclude-module=jupyter',
        '--exclude-module=jedi',
        '--exclude-module=sphinx',
        '--exclude-module=pytest',
        
        # Только критические данные
        '--collect-all=PyQt6',
        
        # Не собираем тестовые данные matplotlib
        '--copy-metadata=matplotlib',
        
        # Оптимизация размера
        '--optimize=2',
        '--noupx',
        
        str(entry_point),
    ]
    
    print(f"[*] Command: pyinstaller [оптимизированные параметры]")
    print(f"[*] Entry point: {entry_point}")
    print(f"[*] Output: {dist_dir / 'nAUDIT_v4.exe'}")
    print(f"[*] Working directory: {work_dir}")
    print()
    
    result = subprocess.run(cmd, cwd=str(project_root))
    
    print()
    print("=" * 70)
    
    if result.returncode == 0:
        exe_path = dist_dir / 'nAUDIT_v4.exe'
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"[✓] Build successful!")
            print(f"[✓] Executable: {exe_path}")
            print(f"[✓] Size: {size_mb:.1f} MB")
            print(f"[*] To run: {exe_path}")
            
            # Статистика
            print()
            print("[*] Build Statistics:")
            print(f"    - Executable size: {size_mb:.1f} MB ({exe_path.stat().st_size:,} bytes)")
            print(f"    - Optimizations applied: matplotlib test data excluded, unused modules excluded")
            print(f"    - Optimization level: 2")
            
            return True
        else:
            print("[✗] Build returned 0 but exe not found!")
            return False
    else:
        print("[✗] Build failed!")
        return False


if __name__ == '__main__':
    success = build_exe()
    sys.exit(0 if success else 1)
