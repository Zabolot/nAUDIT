#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная проверка перед сборкой - Проверяет все критические компоненты
"""

import sys
from pathlib import Path

def check_imports():
    """Проверяет все критические импорты"""
    print("🔍 Проверка импортов...")
    
    checks = [
        ("PyQt6", "PyQt6.QtWidgets"),
        ("PyVis", "pyvis.network"),
        ("NetworkX", "networkx"),
        ("Plotly", "plotly.graph_objects"),
        ("Pillow", "PIL"),
    ]
    
    failed = []
    for name, module in checks:
        try:
            __import__(module)
            print(f"  ✅ {name:15} - OK")
        except ImportError as e:
            print(f"  ❌ {name:15} - FAILED: {e}")
            failed.append(name)
    
    return len(failed) == 0


def check_file_exists():
    """Проверяет существование критических файлов"""
    print("\n📁 Проверка файлов...")
    
    files_to_check = [
        "n_audit/gui/graph_visualizer_v2_6.py",
        "n_audit/gui/tree_widget.py",
        "n_audit/gui/graph_visualizer.py",
        ".gitignore",
    ]
    
    failed = []
    for file_path in files_to_check:
        full_path = Path(file_path)
        if full_path.exists():
            print(f"  ✅ {file_path:40} - OK ({full_path.stat().st_size} bytes)")
        else:
            print(f"  ❌ {file_path:40} - NOT FOUND")
            failed.append(file_path)
    
    return len(failed) == 0


def check_syntax():
    """Проверяет синтаксис критических файлов"""
    print("\n🐍 Проверка синтаксиса Python...")
    
    import py_compile
    
    files_to_check = [
        "n_audit/gui/graph_visualizer_v2_6.py",
        "n_audit/gui/tree_widget.py",
        "n_audit/gui/graph_visualizer.py",
    ]
    
    failed = []
    for file_path in files_to_check:
        full_path = Path(file_path)
        if not full_path.exists():
            continue
            
        try:
            py_compile.compile(str(full_path), doraise=True)
            print(f"  ✅ {file_path:40} - Syntax OK")
        except py_compile.PyCompileError as e:
            print(f"  ❌ {file_path:40} - ERROR:\n     {e}")
            failed.append(file_path)
    
    return len(failed) == 0


def check_critical_code():
    """Проверяет наличие критических исправлений в коде"""
    print("\n🔧 Проверка критических исправлений...")
    
    checks = [
        (
            "n_audit/gui/graph_visualizer_v2_6.py",
            "net.get_html()",
            "PyVis HTML extraction fix"
        ),
        (
            "n_audit/gui/graph_visualizer_v2_6.py",
            "write_html",
            "PyVis fallback write_html"
        ),
        (
            "n_audit/gui/graph_visualizer_v2_6.py",
            "folder_centers",
            "Plotly folder clustering"
        ),
        (
            ".gitignore",
            "v.naudit/",
            "Git .gitignore fix"
        ),
    ]
    
    failed = []
    for file_path, pattern, description in checks:
        full_path = Path(file_path)
        if not full_path.exists():
            print(f"  ❌ {description:40} - File not found: {file_path}")
            failed.append(description)
            continue
        
        content = full_path.read_text(encoding='utf-8')
        if pattern in content:
            print(f"  ✅ {description:40} - Found")
        else:
            print(f"  ❌ {description:40} - NOT found")
            failed.append(description)
    
    return len(failed) == 0


def check_folder_structure():
    """Проверяет структуру папок проекта"""
    print("\n📂 Проверка структуры папок...")
    
    required_dirs = [
        "n_audit",
        "n_audit/gui",
        "n_audit/plugins",
    ]
    
    failed = []
    for dir_path in required_dirs:
        full_path = Path(dir_path)
        if full_path.is_dir():
            print(f"  ✅ {dir_path:40} - OK")
        else:
            print(f"  ❌ {dir_path:40} - NOT FOUND")
            failed.append(dir_path)
    
    return len(failed) == 0


def main():
    """Запускает все проверки"""
    print("=" * 70)
    print("🎯 ФИНАЛЬНАЯ ПРОВЕРКА ПЕРЕД СБОРКОЙ EXE")
    print("=" * 70)
    
    results = []
    
    results.append(("Импорты", check_imports()))
    results.append(("Файлы", check_file_exists()))
    results.append(("Синтаксис", check_syntax()))
    results.append(("Критические исправления", check_critical_code()))
    results.append(("Структура папок", check_folder_structure()))
    
    print("\n" + "=" * 70)
    print("📊 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print("=" * 70)
    
    all_ok = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name:30} {status}")
        if not result:
            all_ok = False
    
    print("=" * 70)
    
    if all_ok:
        print("\n🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! Готово к сборке EXE\n")
        return 0
    else:
        print("\n⚠️  ОБНАРУЖЕНЫ ПРОБЛЕМЫ! Требуется исправление перед сборкой\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
