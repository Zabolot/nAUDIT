#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для построения nAUDIT v4.0 .exe

Использует PyInstaller для создания standalone exe.
"""

import sys
import subprocess
from pathlib import Path
import shutil


def build_exe():
    """Построить .exe"""
    print("[*] Building nAUDIT v4.0 executable...")
    
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
    work_dir = build_dir / 'work'
    
    # Очищаем старые сборки
    if (dist_dir / 'nAUDIT_v4.exe').exists():
        print("[*] Removing old build...")
        (dist_dir / 'nAUDIT_v4.exe').unlink()
    
    if work_dir.exists():
        print("[*] Cleaning work directory...")
        shutil.rmtree(work_dir, ignore_errors=True)
    
    # Команда PyInstaller
    cmd = [
        'pyinstaller',
        '--onefile',                              # Один файл
        '--console',                              # Консоль для вывода
        '--name=nAUDIT_v4',                      # Имя exe
        '--distpath=' + str(dist_dir),           # Путь для exe
        '--workpath=' + str(work_dir),           # Рабочая папка
        '--specpath=' + str(build_dir),
        '--add-data=' + str(n_audit_path) + ':n_audit',
        '--add-data=' + str(project_root / 'assets') + ':assets',
        
        # Скрытые импорты
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtGui',
        '--hidden-import=PyQt6.QtWidgets',
        '--hidden-import=matplotlib.backends.backend_qt5agg',
        '--hidden-import=matplotlib.figure',
        '--hidden-import=matplotlib.pyplot',
        '--hidden-import=matplotlib.axes',
        '--hidden-import=pylint.lint',
        '--hidden-import=flake8.api.legacy',
        
        # Сбор необходимых данных
        '--collect-all=PyQt6',
        '--collect-all=matplotlib',
        
        str(entry_point),
    ]
    
    print(f"[*] Entry point: {entry_point}")
    print(f"[*] Output: {dist_dir / 'nAUDIT_v4.exe'}")
    print()
    
    result = subprocess.run(cmd, cwd=str(project_root))
    
    print()
    print("=" * 60)
    
    if result.returncode == 0:
        exe_path = dist_dir / 'nAUDIT_v4.exe'
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print("[OK] Build successful!")
            print(f"[OK] Executable: {exe_path}")
            print(f"[OK] Size: {size_mb:.1f} MB")
            return True
        else:
            print("[NO] Build returned 0 but exe not found!")
            return False
    else:
        print("[NO] Build failed with return code:", result.returncode)
        return False


if __name__ == '__main__':
    success = build_exe()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    success = build_exe()
    sys.exit(0 if success else 1)
