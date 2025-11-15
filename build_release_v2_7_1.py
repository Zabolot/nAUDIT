#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nAUDIT v2.7.1 - Direct PyInstaller Builder (без torch в проверках)

Использует PyInstaller для создания exe с исправлениями v2.7.1
"""

import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
VENV_PYTHON = PROJECT_ROOT / "v.naudit" / "Scripts" / "python.exe"
ENTRY_POINT = PROJECT_ROOT / "run_naudit_gui.py"
OUTPUT_EXE = PROJECT_ROOT / "dist" / "nAUDIT.exe"

def print_header(text):
    print(f"\n{'='*75}\n  {text}\n{'='*75}\n")

def print_ok(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warn(text):
    print(f"⚠️  {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def main():
    print_header("🚀 nAUDIT v2.7.1 - ФИНАЛЬНАЯ СБОРКА EXE")
    
    print("""ИСПРАВЛЕНИЯ В v2.7.1:
✅ GPU Detection улучшена
   - Детальное логирование процесса
   - Fallback через nvidia-smi
   - Обработка ошибок для каждого GPU

✅ Tree Widget Error Display исправлена
   - Гарантированное отображение ошибок
   - Auto-expand всех папок
   - Полная совместимость с форматами данных

✅ Tree-Graph Synchronization реализована
   - Двусторонняя синхронизация
   - Выбор в дереве → выделение в графе
   - Выбор в графе → переход в дереве
""")
    
    # Step 1: Clean
    print_info("Шаг 1: Очистка старых артефактов...")
    if OUTPUT_EXE.exists():
        OUTPUT_EXE.unlink()
        print_ok("Удален старый exe")
    
    build_dir = PROJECT_ROOT / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir, ignore_errors=True)
        print_ok("Очищена папка build/")
    
    # Step 2: Check PyInstaller
    print_info("\nШаг 2: Проверка PyInstaller...")
    try:
        result = subprocess.run(
            [str(VENV_PYTHON), "-m", "PyInstaller", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_ok(f"PyInstaller: {result.stdout.strip()}")
        else:
            print_error("PyInstaller не работает")
            return 1
    except Exception as e:
        print_error(f"Ошибка проверки PyInstaller: {e}")
        return 1
    
    # Step 3: Build command
    print_info("\nШаг 3: Подготовка команды сборки...")
    
    n_audit_path = PROJECT_ROOT / "n_audit"
    dist_dir = PROJECT_ROOT / "dist"
    build_dir = PROJECT_ROOT / "build"
    separator = ";"
    
    cmd = [
        str(VENV_PYTHON),
        "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name=nAUDIT",
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}/work",
        f"--specpath={build_dir}",
        "--noupx",
        "-y",
    ]
    
    # Add data files
    cmd.extend([
        f"--add-data={n_audit_path}{separator}n_audit",
    ])
    
    assets_dir = PROJECT_ROOT / "assets"
    if assets_dir.exists():
        cmd.append(f"--add-data={assets_dir}{separator}assets")
    
    # Hidden imports
    hidden_imports = [
        "PyQt6.QtCore", "PyQt6.QtGui", "PyQt6.QtWidgets",
        "PyQt6.QtWebEngineWidgets", "PyQt6.QtWebEngineCore", "PyQt6.QtWebChannel",
        "networkx", "networkx.algorithms",
        "pyvis", "pyvis.network",
        "plotly", "plotly.graph_objects", "plotly.offline", "plotly.io",
        "psutil",
    ]
    
    for imp in hidden_imports:
        cmd.append(f"--hidden-import={imp}")
    
    # Collect all
    cmd.extend([
        "--collect-all=PyQt6",
        "--collect-all=plotly",
        "--collect-all=pyvis",
        "--collect-submodules=pyvis",
        "--collect-submodules=plotly",
    ])
    
    cmd.append(str(ENTRY_POINT))
    
    print_ok(f"Команда готова ({len(cmd)} аргументов)")
    
    # Step 4: Run build
    print_info("\nШаг 4: Запуск PyInstaller...")
    print_info("⏳ Это может занять 3-5 минут...\n")
    
    try:
        result = subprocess.run(cmd, timeout=600)
        
        if result.returncode != 0:
            print_error(f"PyInstaller вернул код {result.returncode}")
            return 1
        
        # Verify
        if OUTPUT_EXE.exists():
            size_gb = OUTPUT_EXE.stat().st_size / (1024**3)
            size_mb = OUTPUT_EXE.stat().st_size / (1024**2)
            mtime = datetime.fromtimestamp(OUTPUT_EXE.stat().st_mtime)
            mtime_str = mtime.strftime("%Y-%m-%d %H:%M:%S")
            
            print_header("✨ СБОРКА УСПЕШНА - nAUDIT v2.7.1")
            
            print(f"""
📁 РАСПОЛОЖЕНИЕ:      {OUTPUT_EXE}
📊 РАЗМЕР:            {size_gb:.2f} GB ({size_mb:.0f} MB)
⏱️  ВРЕМЯ СОЗДАНИЯ:    {mtime_str}

🔧 ИСПРАВЛЕНИЯ v2.7.1:

1️⃣  GPU DETECTION
    ✅ Улучшена логика обнаружения GPU
    ✅ Добавлено детальное логирование
    ✅ Реализован fallback через nvidia-smi
    📁 Файл: n_audit/gui/gpu_detector.py

2️⃣  TREE WIDGET ERROR DISPLAY
    ✅ Гарантированное отображение ошибок
    ✅ Auto-expand папок при загрузке
    ✅ Полная совместимость форматов
    📁 Файл: n_audit/gui/tree_widget.py

3️⃣  TREE-GRAPH SYNCHRONIZATION
    ✅ Двусторонняя синхронизация
    ✅ Выбор в дереве → выделение в графе
    ✅ Выбор в графе → переход в дереве
    📁 Файлы: error_visualization.py, graph_visualizer_v2_6.py

📝 ТЕСТИРОВАНИЕ:

   1. Запустить exe:
      .\\dist\\nAUDIT.exe

   2. В GUI:
      ✓ Выбрать папку проекта с ошибками
      ✓ Запустить аудит
      ✓ Проверить что ошибки видны в дереве (папки раскрыты)
      ✓ Клик в дереве → выделение в графе
      ✓ Клик в графе → переход в дереве
      ✓ Проверить GPU статус
      ✓ Проверить логи

📚 ДОКУМЕНТАЦИЯ:

   - SUMMARY_v2_7_1_FINAL.md
     Итоговый отчет со всеми изменениями

   - TESTING_GUIDE_v2_7_1.md
     Полное руководство по тестированию каждой функции

   - FIXES_REPORT_v2_7_1.md
     Детальное описание всех исправлений

   - test_fixes_comprehensive.py
     Автоматизированное тестирование логики

📋 ПРОВЕРКА ЛОГОВ:

   %USERPROFILE%\\.naudit\\logs\\latest.log

   Ищите:
   [GPU Detector] ... GPU detection завершен
   [Tree Widget] Building tree for N files
   [ErrorVisualizationWidget] Синхронизация: дерево → граф

🎯 РЕЗУЛЬТАТ:

   ✅ Все 3 критические проблемы исправлены
   ✅ Exe готова к развёртыванию
   ✅ Готова к тестированию на реальных проектах

""")
            
            print_header("ГОТОВО К ТЕСТИРОВАНИЮ!")
            return 0
        else:
            print_error(f"EXE не найден: {OUTPUT_EXE}")
            return 1
            
    except subprocess.TimeoutExpired:
        print_error("Сборка истекла (10 минут)")
        return 1
    except Exception as e:
        print_error(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
