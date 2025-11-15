#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nAUDIT v2.7.1 - Ultimate Builder with All Fixes

Основан на build_exe_ultimate.py и build_v2_7_final.py

Сборка финального exe включающего все 3 исправления:
✅ GPU Detection улучшена (с логированием и fallback через nvidia-smi)
✅ Tree Widget Error Display исправлена (гарантированный вывод, auto-expand)
✅ Tree-Graph Synchronization реализована (двусторонняя синхронизация)

Использует виртуальное окружение v.naudit где установлены все зависимости
"""

import sys
import subprocess
import shutil
import time
from pathlib import Path
from datetime import datetime

# ════════════════════════════════════════════════════════════════
# CONFIGURATION
# ════════════════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).parent
VENV_PYTHON = PROJECT_ROOT / "v.naudit" / "Scripts" / "python.exe"
ENTRY_POINT = PROJECT_ROOT / "run_naudit_gui.py"
OUTPUT_EXE = PROJECT_ROOT / "dist" / "nAUDIT.exe"

# ════════════════════════════════════════════════════════════════
# OUTPUT UTILITIES
# ════════════════════════════════════════════════════════════════

def print_header(text):
    print(f"\n{'='*75}")
    print(f"  {text}")
    print(f"{'='*75}\n")

def print_step(step_num, total, text):
    print(f"\n[{step_num}/{total}] {text}")
    print("-" * 75)

def print_ok(text):
    print(f"  ✅ {text}")

def print_error(text):
    print(f"  ❌ {text}")

def print_warn(text):
    print(f"  ⚠️  {text}")

def print_info(text):
    print(f"  ℹ️  {text}")

def print_success(text):
    print(f"\n  ✨ {text}")

# ════════════════════════════════════════════════════════════════
# VERIFICATION
# ════════════════════════════════════════════════════════════════

def verify_venv():
    """Verify virtual environment exists and has dependencies"""
    print_info("Проверка виртуального окружения...")
    
    if not VENV_PYTHON.exists():
        print_error(f"Виртуальное окружение не найдено: {VENV_PYTHON}")
        return False
    print_ok("Виртуальное окружение найдено")
    
    # Check if dependencies are installed
    check_cmd = f'"{VENV_PYTHON}" -c "import PyQt6; import torch; import networkx; import pyvis; import plotly; import psutil"'
    
    try:
        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print_ok("Все зависимости установлены в виртуальном окружении")
            return True
        else:
            print_error(f"Отсутствуют зависимости: {result.stderr}")
            return False
    except Exception as e:
        print_error(f"Ошибка проверки: {e}")
        return False

def verify_entry_point():
    """Verify entry point exists"""
    if not ENTRY_POINT.exists():
        print_error(f"Entry point не найден: {ENTRY_POINT}")
        return False
    print_ok(f"Entry point найден: {ENTRY_POINT.name}")
    return True

def verify_n_audit_module():
    """Verify n_audit module structure"""
    print_info("Проверка модуля n_audit...")
    
    n_audit_path = PROJECT_ROOT / "n_audit"
    if not n_audit_path.exists():
        print_error(f"Модуль n_audit не найден: {n_audit_path}")
        return False
    
    # Проверка ключевых файлов с исправлениями
    critical_files = [
        ("gui/main_window_v4.py", "Главное окно"),
        ("gui/tree_widget.py", "Tree Widget (исправления)"),
        ("gui/graph_visualizer_v2_6.py", "Graph Visualizer (синхронизация)"),
        ("gui/error_visualization.py", "Error Visualization (синхронизация)"),
        ("gui/gpu_detector.py", "GPU Detector (улучшения)"),
    ]
    
    all_found = True
    for file_path, description in critical_files:
        full_path = n_audit_path / file_path
        if full_path.exists():
            print_ok(f"{description}: {file_path}")
        else:
            print_error(f"{description} не найден: {file_path}")
            all_found = False
    
    return all_found

def verify_pyinstaller():
    """Verify PyInstaller is working"""
    print_info("Проверка PyInstaller...")
    
    try:
        cmd = f'"{VENV_PYTHON}" -m PyInstaller --version'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            version = result.stdout.strip()
            print_ok(f"PyInstaller {version}")
            return True
        else:
            print_error("PyInstaller не работает")
            return False
    except Exception as e:
        print_error(f"Ошибка проверки PyInstaller: {e}")
        return False

# ════════════════════════════════════════════════════════════════
# BUILD SYSTEM
# ════════════════════════════════════════════════════════════════

def clean_old_builds():
    """Clean old build artifacts"""
    print_info("Очистка старых артефактов...")
    
    # Remove old exe
    if OUTPUT_EXE.exists():
        OUTPUT_EXE.unlink()
        print_ok(f"Удалён старый exe: {OUTPUT_EXE.name}")
    
    # Clean build directory
    build_dir = PROJECT_ROOT / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir, ignore_errors=True)
        print_ok("Очищена папка build/")

def build_pyinstaller_command():
    """Build PyInstaller command"""
    print_info("Построение команды PyInstaller...")
    
    n_audit_path = PROJECT_ROOT / "n_audit"
    dist_dir = PROJECT_ROOT / "dist"
    build_dir = PROJECT_ROOT / "build"
    
    separator = ";" if sys.platform == "win32" else ":"
    
    # Base command using venv python
    cmd = (
        f'"{VENV_PYTHON}" -m PyInstaller '
        '--onefile '
        '--windowed '
        '--name=nAUDIT '
        f'--distpath="{dist_dir}" '
        f'--workpath="{build_dir}/work" '
        f'--specpath="{build_dir}" '
        '--noupx '
        '-y '
    )
    
    # Add data files
    cmd += f'--add-data="{n_audit_path}{separator}n_audit" '
    assets_dir = PROJECT_ROOT / "assets"
    if assets_dir.exists():
        cmd += f'--add-data="{assets_dir}{separator}assets" '
    
    # Critical hidden imports
    critical_imports = [
        "PyQt6.QtCore", "PyQt6.QtGui", "PyQt6.QtWidgets",
        "PyQt6.QtWebEngineWidgets", "PyQt6.QtWebEngineCore", "PyQt6.QtWebChannel",
        "networkx", "networkx.algorithms",
        "pyvis", "pyvis.network",
        "plotly", "plotly.graph_objects", "plotly.offline", "plotly.io",
    ]
    
    for imp in critical_imports:
        cmd += f'--hidden-import={imp} '
    
    # Collect all data
    cmd += (
        '--collect-all=PyQt6 '
        '--collect-all=plotly '
        '--collect-all=pyvis '
        '--collect-submodules=pyvis '
        '--collect-submodules=plotly '
    )
    
    # PyVis templates
    try:
        import pyvis
        pyvis_path = Path(pyvis.__file__).parent
        templates_path = pyvis_path / "templates"
        if templates_path.exists():
            cmd += f'--add-data="{templates_path}{separator}pyvis/templates" '
            print_ok("Добавлены PyVis templates")
    except:
        print_warn("PyVis templates не найдены")
    
    # Entry point
    cmd += f'"{ENTRY_POINT}"'
    
    return cmd

def run_pyinstaller(cmd):
    """Run PyInstaller build"""
    print_info("Запуск сборки PyInstaller...")
    print()
    
    start_time = time.time()
    
    try:
        # Run in shell to handle the long command
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=str(PROJECT_ROOT),
            timeout=900  # 15 minutes
        )
        
        elapsed = time.time() - start_time
        return result.returncode, elapsed
        
    except subprocess.TimeoutExpired:
        print_error("Сборка истекла (15 минут)")
        return 1, 900
    except Exception as e:
        print_error(f"Ошибка сборки: {e}")
        return 1, 0

def verify_build_output():
    """Verify build was successful"""
    if not OUTPUT_EXE.exists():
        print_error(f"EXE не найден: {OUTPUT_EXE}")
        return False
    
    size_gb = OUTPUT_EXE.stat().st_size / (1024**3)
    size_mb = OUTPUT_EXE.stat().st_size / (1024**2)
    mtime = OUTPUT_EXE.stat().st_mtime
    mod_time = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
    
    print_ok(f"EXE создан: {OUTPUT_EXE.name}")
    print_ok(f"Размер: {size_gb:.2f} GB ({size_mb:.0f} MB)")
    print_ok(f"Время: {mod_time}")
    
    return True

# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════

def main():
    print_header("🚀 nAUDIT v2.7.1 - СБОРКА С ИСПРАВЛЕНИЯМИ")
    
    print("""
ВКЛЮЧЁННЫЕ ИСПРАВЛЕНИЯ:
✅ GPU Detection - улучшена логика обнаружения (PyTorch + nvidia-smi fallback)
✅ Tree Widget - ошибки гарантированно отображаются (auto-expand папки)
✅ Synchronization - двусторонняя синхронизация дерева ↔ графа
    """)
    
    start_time = time.time()
    
    # Step 1: Verification
    print_step(1, 5, "Проверка предварительных условий")
    
    if not verify_venv():
        print_error("Виртуальное окружение не готово")
        return 1
    
    if not verify_entry_point():
        print_error("Entry point не найден")
        return 1
    
    if not verify_n_audit_module():
        print_error("Модуль n_audit не найден")
        return 1
    
    if not verify_pyinstaller():
        print_error("PyInstaller не работает")
        return 1
    
    print_success("Все предварительные проверки пройдены")
    
    # Step 2: Clean
    print_step(2, 5, "Очистка старых артефактов")
    clean_old_builds()
    print_success("Очистка завершена")
    
    # Step 3: Build command
    print_step(3, 5, "Подготовка команды сборки")
    cmd = build_pyinstaller_command()
    print_ok(f"Команда готова ({len(cmd)} символов)")
    
    # Step 4: Build
    print_step(4, 5, "Сборка EXE с PyInstaller")
    returncode, elapsed = run_pyinstaller(cmd)
    
    if returncode != 0:
        print_error("Сборка провалилась")
        return 1
    
    print_ok(f"Сборка завершена за {elapsed:.1f} сек")
    
    # Step 5: Verify
    print_step(5, 5, "Проверка результата сборки")
    if not verify_build_output():
        print_error("Проверка результата провалилась")
        return 1
    
    # Final report
    total_time = time.time() - start_time
    print_header("✨ СБОРКА УСПЕШНА - nAUDIT v2.7.1")
    
    print(f"""
📁 Расположение:  {OUTPUT_EXE}

🔧 ВКЛЮЧЁННЫЕ ИСПРАВЛЕНИЯ:
   ✅ GPU Detection (с fallback через nvidia-smi)
   ✅ Tree Widget Error Display (гарантированный вывод)
   ✅ Tree-Graph Synchronization (двусторонняя работа)

📝 СЛЕДУЮЩИЕ ШАГИ:
   1. Запустить:    .\\dist\\nAUDIT.exe
   2. Выбрать папку проекта с ошибками
   3. Запустить аудит
   4. Проверить что ошибки видны в дереве
   5. Проверить синхронизацию: клик в дереве → выделение в графе

📚 ДОКУМЕНТАЦИЯ:
   - SUMMARY_v2_7_1_FINAL.md - итоговый отчет
   - TESTING_GUIDE_v2_7_1.md - руководство тестирования
   - FIXES_REPORT_v2_7_1.md - детальное описание

⏱️  Время сборки: {total_time:.1f} сек
    """)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
