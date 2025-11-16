#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование графа-визуализатора v2.6
"""

import sys
from pathlib import Path

# Добавляем проект в path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Проверить все импорты"""
    print("[*] Проверяю импорты...")
    
    try:
        print("  - graph_visualizer_v2_6...", end="")
        from n_audit.gui.graph_visualizer_v2_6 import GraphVisualizerWidget
        print(" ✅")
        
        print("  - graph_visualizer (proxy)...", end="")
        from n_audit.gui.graph_visualizer import GraphVisualizerWidget as GVW
        print(" ✅")
        
        print("  - tree_widget...", end="")
        from n_audit.gui.tree_widget import ErrorTreeWidget
        print(" ✅")
        
        print("  - error_visualization...", end="")
        from n_audit.gui.error_visualization import ErrorVisualizationWidget
        print(" ✅")
        
        print("  - main_window_v4...", end="")
        from n_audit.gui.main_window_v4 import MainWindowV4
        print(" ✅")
        
        print("\n✅ Все импорты успешны!")
        return True
        
    except Exception as e:
        print(f" ❌\n[✗] Ошибка импорта: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_graph_features():
    """Проверить функции графа"""
    print("\n[*] Проверяю функции графа v2.6...")
    
    try:
        from n_audit.gui.graph_visualizer_v2_6 import (
            GraphVisualizerWidget,
            GraphRenderMode,
            EXCLUDE_FOLDERS,
            FileNode
        )
        
        print("  - GraphRenderMode...", end="")
        assert hasattr(GraphRenderMode, 'PLOTLY')
        assert hasattr(GraphRenderMode, 'PYVIS')
        print(" ✅")
        
        print("  - EXCLUDE_FOLDERS...", end="")
        assert '.venv' in EXCLUDE_FOLDERS
        assert '__pycache__' in EXCLUDE_FOLDERS
        assert 'node_modules' in EXCLUDE_FOLDERS
        print(" ✅")
        
        print("  - FileNode...", end="")
        node = FileNode(
            file_path="test.py",
            lines_of_code=100,
            errors_count=5,
            max_severity="HIGH",
            folder="test_folder"
        )
        assert node.get_display_text() == "5"
        print(" ✅")
        
        print("\n✅ Функции графа работают правильно!")
        return True
        
    except Exception as e:
        print(f" ❌\n[✗] Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Главная функция тестирования"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ nAUDIT v2.6 - ГРАФ-ВИЗУАЛИЗАТОР")
    print("=" * 60)
    
    results = []
    
    # Тест 1: Импорты
    results.append(("Импорты", test_imports()))
    
    # Тест 2: Функции
    results.append(("Функции графа", test_graph_features()))
    
    # Итоги
    print("\n" + "=" * 60)
    print("ИТОГИ ТЕСТИРОВАНИЯ:")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_pass = all(r for _, r in results)
    
    print("=" * 60)
    if all_pass:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        return 0
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
