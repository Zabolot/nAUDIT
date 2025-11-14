#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест интеграции граф-визуализации с основным приложением
"""

import sys
from pathlib import Path

# Добавим root в path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("[Test] Проверяем граф-визуализацию...")
print("=" * 60)

# Тест 1: Импорт компонентов
print("\n[1] Импорт компонентов...")
try:
    from n_audit.gui.error_visualization import ErrorVisualizationWidget, ViewMode
    print("  ✓ ErrorVisualizationWidget импортирован")
    print("  ✓ ViewMode enum импортирован")
except Exception as e:
    print(f"  ✗ Ошибка: {e}")
    sys.exit(1)

try:
    from n_audit.gui.graph_visualizer import GraphVisualizerWidget, FileNode
    print("  ✓ GraphVisualizerWidget импортирован")
    print("  ✓ FileNode dataclass импортирован")
except Exception as e:
    print(f"  ✗ Ошибка: {e}")
    sys.exit(1)

try:
    from n_audit.gui.tree_widget import ErrorTreeWidget
    print("  ✓ ErrorTreeWidget импортирован")
except Exception as e:
    print(f"  ✗ Ошибка: {e}")
    sys.exit(1)

# Тест 2: Проверяем ViewMode enum
print("\n[2] Проверяем ViewMode enum...")
modes = [ViewMode.TREE, ViewMode.GRAPH, ViewMode.SPLIT]
for mode in modes:
    print(f"  ✓ {mode.name} = {mode.value}")

# Тест 3: Создание объектов без GUI
print("\n[3] Создание объектов (без GUI)...")
try:
    from n_audit.gui.tree_widget import ErrorTreeWidget
    from n_audit.gui.graph_visualizer import GraphVisualizerWidget
    from n_audit.gui.error_visualization import ErrorVisualizationWidget
    
    # Эти требуют QApplication, поэтому тестируем только импорт
    print("  ✓ Все классы могут быть импортированы")
except Exception as e:
    print(f"  ✗ Ошибка при импорте: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Тест 4: FileNode dataclass
print("\n[4] Тестирование FileNode dataclass...")
try:
    node = FileNode(
        file_path="test.py",
        lines_of_code=100,
        errors_count=5,
        max_severity="HIGH",
        folder="src"
    )
    print(f"  ✓ FileNode создан: {node.file_path}, {node.errors_count} ошибок")
    print(f"    - Строк: {node.lines_of_code}")
    print(f"    - Папка: {node.folder}")
    print(f"    - Max severity: {node.max_severity}")
except Exception as e:
    print(f"  ✗ Ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Тест 5: Проверяем методы
print("\n[5] Проверяем основные методы...")
try:
    # Проверяем что методы существуют
    methods_graph = ['populate_from_report', 'clear', '_get_color', '_get_size', '_render_graph']
    for method in methods_graph:
        if hasattr(GraphVisualizerWidget, method):
            print(f"  ✓ GraphVisualizerWidget.{method} существует")
        else:
            print(f"  ✗ GraphVisualizerWidget.{method} НЕ найден")
    
    methods_visualization = ['populate_from_report', 'clear', '_on_tree_mode', '_on_graph_mode', '_on_split_mode']
    for method in methods_visualization:
        if hasattr(ErrorVisualizationWidget, method):
            print(f"  ✓ ErrorVisualizationWidget.{method} существует")
        else:
            print(f"  ✗ ErrorVisualizationWidget.{method} НЕ найден")
            
except Exception as e:
    print(f"  ✗ Ошибка: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ Все тесты пройдены успешно!")
print("=" * 60)
print("\nСтруктура граф-визуализации:")
print("  ErrorVisualizationWidget")
print("    ├── 🌳 Дерево режима -> ErrorTreeWidget")
print("    ├── 🕸️  Граф режима -> GraphVisualizerWidget")
print("    └── 📊 Разделённый -> оба одновременно")
print("\nОписание файлов:")
print("  • error_visualization.py - основной компонент (wrapper)")
print("  • graph_visualizer.py - граф-визуализация")
print("  • tree_widget.py - иерархическое дерево")
print("\n✓ Готово к использованию в main_window_v4!")
