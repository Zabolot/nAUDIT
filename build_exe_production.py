#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для построения nAUDIT v2.1.0 .exe

Полностью основан на работающем build_exe_v4.py с поддержкой компонентов v2.1.0:
- graph_visualizer.py
- error_visualization.py
- tree_widget.py (обновленный)

Использует PyInstaller для создания standalone exe.
"""

import sys
import subprocess
from pathlib import Path
import shutil
import time


def verify_components():
    """Проверить наличие всех компонентов v2.1.0"""
    print("[*] Verifying v2.1.0 components...")
    
    project_root = Path.cwd()
    components = [
        "n_audit/gui/main_app.py",
        "n_audit/gui/main_window_v4.py",
        "n_audit/gui/tree_widget.py",
        "n_audit/gui/graph_visualizer.py",
        "n_audit/gui/error_visualization.py",
    ]
    
    all_found = True
    for component in components:
        path = project_root / component
        if path.exists():
            print(f"    [OK] {component}")
        else:
            print(f"    [NO] {component} - NOT FOUND")
            all_found = False
    
    return all_found


def build_exe():
    """Построить .exe на основе v4 архитектуры"""
    print("\n" + "=" * 70)
    print("  nAUDIT v2.1.0 - Production Build (based on v4.0 architecture)")
    print("=" * 70 + "\n")
    
    # Путь к проекту
    project_root = Path.cwd()
    
    # Проверяем компоненты
    if not verify_components():
        print("[!] Warning: Some components not found, continuing anyway...")
    
    # Точка входа
    entry_point = project_root / "run_naudit_gui.py"
    
    if not entry_point.exists():
        print(f"[ERROR] Entry point not found: {entry_point}")
        return False
    
    # Полный путь к n_audit модулю
    n_audit_path = project_root / "n_audit"
    if not n_audit_path.exists():
        print(f"[ERROR] n_audit module not found: {n_audit_path}")
        return False
    
    # Пути для сборки
    build_dir = project_root / 'build'
    dist_dir = project_root / 'dist'
    work_dir = build_dir / 'work'
    
    print(f"[*] Project root: {project_root}")
    print(f"[*] Entry point: {entry_point}")
    print(f"[*] Output: {dist_dir / 'nAUDIT.exe'}")
    print()
    
    # Очищаем старые сборки
    print("[1/7] Cleaning old builds...")
    
    exe_file = dist_dir / 'nAUDIT.exe'
    if exe_file.exists():
        exe_file.unlink()
        print(f"    [OK] Removed old {exe_file.name}")
    
    if work_dir.exists():
        shutil.rmtree(work_dir, ignore_errors=True)
        print(f"    [OK] Cleaned work directory")
    
    # Проверяем PyInstaller
    print("\n[2/7] Verifying PyInstaller...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", "PyInstaller"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    version = line.split(': ')[1]
                    print(f"    [OK] PyInstaller {version} installed")
                    break
        else:
            print("[ERROR] PyInstaller not installed!")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to check PyInstaller: {e}")
        return False
    
    # Подготавливаем скрытые импорты (только необходимые v2.1.0)
    print("\n[3/7] Preparing hidden imports...")
    
    hidden_imports = [
        # PyQt6 core
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtWebEngineCore",
        
        # n_audit modules
        "n_audit.core",
        "n_audit.code_analysis",
        "n_audit.security",
        
        # GUI components (v2.1.0)
        "n_audit.gui.main_app",
        "n_audit.gui.main_window_v4",
        "n_audit.gui.tree_widget",
        "n_audit.gui.graph_visualizer",
        "n_audit.gui.error_visualization",
        
        # Graph visualization (NEW in v2.1.0)
        "networkx",
        "networkx.algorithms",
        "networkx.drawing",
        
        # Interactive visualization (NEW in v2.1.0)
        "pyvis",
        "pyvis.network",
        
        # Graph plotting with Plotly (NEW in v2.1.1)
        "plotly",
        "plotly.graph_objects",
        "plotly.offline",
        "plotly.io",
        
        # Plotting (for error visualization)
        "matplotlib",
        "matplotlib.backends.backend_qt5agg",
        "matplotlib.figure",
        "matplotlib.pyplot",
        "matplotlib.axes",
        
        # Code analysis tools
        "pylint.lint",
        "pylint.reporters",
        "flake8.api.legacy",
        "bandit.main",
    ]
    
    hidden_import_args = []
    for imp in hidden_imports:
        hidden_import_args.extend(['--hidden-import=' + imp])
    
    print(f"    [OK] Prepared {len(hidden_imports)} hidden imports")
    
    # Команда PyInstaller (точно как в v4, но с v2.1.0 компонентами)
    print("\n[4/7] Building PyInstaller command...")
    
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--onefile",                                    # Один файл
        "--windowed",                                   # GUI режим (без консоли)
        "--name=nAUDIT",                               # Имя exe
        f"--distpath={str(dist_dir)}",                 # Путь для exe
        f"--workpath={str(work_dir)}",                 # Рабочая папка
        f"--specpath={str(build_dir)}",
        "--noupx",                                      # Отключить UPX для стабильности
        "-y",                                           # Перезаписать без подтверждения
        f"--add-data={str(n_audit_path)}{';' if sys.platform == 'win32' else ':'}n_audit",
        f"--add-data={str(project_root / 'assets')}{';' if sys.platform == 'win32' else ':'}assets",
    ]
    
    # Добавляем скрытые импорты
    cmd.extend(hidden_import_args)
    
    # Добавляем сбор данных (с явным указанием pyvis и plotly)
    pyvis_path = Path(sys.prefix) / "Lib" / "site-packages" / "pyvis" / "templates"
    cmd.extend([
        "--collect-all=PyQt6",
        "--collect-all=matplotlib",
        "--collect-all=pyvis",
        "--collect-all=plotly",
        "--collect-submodules=pyvis",
        "--collect-submodules=plotly",
    ])
    
    # Убедимся, что шаблоны pyvis включены
    if pyvis_path.exists():
        cmd.append(f"--add-data={str(pyvis_path)}{';' if sys.platform == 'win32' else ':'}pyvis/templates")
    
    cmd.append(str(entry_point))
    
    print(f"    [OK] Command prepared ({len(cmd)} arguments)")
    
    # Запускаем сборку
    print("\n[5/7] Running PyInstaller...")
    print(f"    Output format: nAUDIT.exe (GUI mode, no console)")
    print()
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, cwd=str(project_root), timeout=600)
        elapsed = time.time() - start_time
        
        print()
        print("[6/7] Build process completed")
        print(f"    [OK] Elapsed time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        
    except subprocess.TimeoutExpired:
        print("[ERROR] Build timed out after 600 seconds")
        return False
    except Exception as e:
        print(f"[ERROR] Build failed: {e}")
        return False
    
    # Проверяем результат
    print("\n[7/7] Verifying build...")
    print()
    print("=" * 70)
    
    if result.returncode == 0:
        exe_path = dist_dir / 'nAUDIT.exe'
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"[SUCCESS] Build completed successfully!")
            print(f"[SUCCESS] Executable: {exe_path}")
            print(f"[SUCCESS] Size: {size_mb:.1f} MB")
            print(f"[SUCCESS] Build time: {elapsed/60:.1f} minutes")
            print("=" * 70)
            print("\nYou can now run:")
            print(f"  & \"{exe_path}\"")
            return True
        else:
            print("[ERROR] Build returned 0 but exe not found!")
            print("=" * 70)
            return False
    else:
        print(f"[ERROR] Build failed with return code: {result.returncode}")
        print("=" * 70)
        return False


if __name__ == '__main__':
    try:
        success = build_exe()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        sys.exit(1)
