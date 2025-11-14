#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная проверка v2.1.0 - Граф-визуализация
"""

import sys
from pathlib import Path
from datetime import datetime

print("\n" + "=" * 70)
print("🎉 ФИНАЛЬНАЯ ПРОВЕРКА nAUDIT v2.1.0 - ГРАФ-ВИЗУАЛИЗАЦИЯ")
print("=" * 70)
print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

# Логирование результатов
results = []

def check(name, condition, details=""):
    """Проверить условие и логировать результат"""
    status = "✅" if condition else "❌"
    results.append((name, condition))
    print(f"\n{status} {name}")
    if details:
        print(f"   {details}")
    return condition

print("\n📋 ПРОВЕРКА КОМПОНЕНТОВ\n" + "-" * 70)

# Проверка 1: Файлы существуют
print("\n[1] Проверка файлов...")
files_exist = {
    'error_visualization.py': 'n_audit/gui/error_visualization.py',
    'graph_visualizer.py': 'n_audit/gui/graph_visualizer.py',
    'tree_widget.py': 'n_audit/gui/tree_widget.py',
    'main_window_v4.py': 'n_audit/gui/main_window_v4.py',
}

for name, path in files_exist.items():
    full_path = Path(path)
    exists = full_path.exists()
    check(f"Файл: {name}", exists, f"Путь: {full_path}")

# Проверка 2: Импорты
print("\n[2] Проверка импортов...")
try:
    from n_audit.gui.error_visualization import ErrorVisualizationWidget, ViewMode
    check("ErrorVisualizationWidget", True)
    check("ViewMode enum", True)
except Exception as e:
    check("ErrorVisualizationWidget", False, str(e))

try:
    from n_audit.gui.graph_visualizer import GraphVisualizerWidget, FileNode
    check("GraphVisualizerWidget", True)
    check("FileNode dataclass", True)
except Exception as e:
    check("GraphVisualizerWidget", False, str(e))

try:
    from n_audit.gui.tree_widget import ErrorTreeWidget
    check("ErrorTreeWidget", True)
except Exception as e:
    check("ErrorTreeWidget", False, str(e))

# Проверка 3: ViewMode
print("\n[3] Проверка ViewMode enum...")
try:
    from n_audit.gui.error_visualization import ViewMode
    
    modes = [
        (ViewMode.TREE, "tree"),
        (ViewMode.GRAPH, "graph"),
        (ViewMode.SPLIT, "split")
    ]
    
    for mode, expected_value in modes:
        check(f"ViewMode.{mode.name}", mode.value == expected_value)
except Exception as e:
    check("ViewMode", False, str(e))

# Проверка 4: FileNode
print("\n[4] Проверка FileNode dataclass...")
try:
    from n_audit.gui.graph_visualizer import FileNode
    
    node = FileNode(
        file_path="test.py",
        lines_of_code=100,
        errors_count=5,
        max_severity="HIGH",
        folder="src"
    )
    
    check("FileNode создание", True, f"{node.file_path}: {node.errors_count} ошибок")
    check("FileNode.file_path", node.file_path == "test.py")
    check("FileNode.errors_count", node.errors_count == 5)
    check("FileNode.max_severity", node.max_severity == "HIGH")
    check("FileNode.imports (set)", isinstance(node.imports, set))
except Exception as e:
    check("FileNode", False, str(e))

# Проверка 5: Методы класса
print("\n[5] Проверка методов...")
try:
    from n_audit.gui.error_visualization import ErrorVisualizationWidget
    from n_audit.gui.graph_visualizer import GraphVisualizerWidget
    
    # Проверка методов ErrorVisualizationWidget
    required_methods_viz = [
        'populate_from_report',
        'clear',
        'filter_by_severity',
        'get_current_mode',
        '_on_tree_mode',
        '_on_graph_mode',
        '_on_split_mode'
    ]
    
    for method in required_methods_viz:
        has_method = hasattr(ErrorVisualizationWidget, method)
        check(f"ErrorVisualizationWidget.{method}", has_method)
    
    # Проверка методов GraphVisualizerWidget
    required_methods_graph = [
        'populate_from_report',
        'clear',
        'get_all_files',
        'filter_by_severity',
        '_get_color',
        '_get_size',
        '_render_graph'
    ]
    
    for method in required_methods_graph:
        has_method = hasattr(GraphVisualizerWidget, method)
        check(f"GraphVisualizerWidget.{method}", has_method)
        
except Exception as e:
    check("Методы", False, str(e))

# Проверка 6: Интеграция с main_window
print("\n[6] Проверка интеграции с main_window_v4...")
try:
    with open('n_audit/gui/main_window_v4.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    check("Import ErrorVisualizationWidget", 'ErrorVisualizationWidget' in content)
    check("Использование ErrorVisualizationWidget", 
          'self.tree_widget = ErrorVisualizationWidget()' in content)
    check("populate_from_report", 'populate_from_report' in content)
except Exception as e:
    check("Интеграция main_window", False, str(e))

# Проверка 7: Документация
print("\n[7] Проверка документации...")
docs_files = [
    ('GRAPH_VISUALIZATION_GUIDE.md', 'docs/GRAPH_VISUALIZATION_GUIDE.md'),
    ('CHANGELOG.md', 'CHANGELOG.md')
]

for name, path in docs_files:
    full_path = Path(path)
    exists = full_path.exists() and full_path.stat().st_size > 0
    check(f"Документация: {name}", exists)

# Проверка 8: Зависимости
print("\n[8] Проверка зависимостей...")
try:
    import networkx
    check("networkx", True, f"v{networkx.__version__}")
except:
    check("networkx", False)

try:
    import pyvis
    check("pyvis", True, f"v{pyvis.__version__}")
except:
    check("pyvis", False)

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    check("PyQt6.QtWebEngineWidgets", True)
except:
    check("PyQt6.QtWebEngineWidgets", False)

# Финальный итог
print("\n" + "=" * 70)
passed = sum(1 for _, condition in results if condition)
total = len(results)

print(f"\n📊 РЕЗУЛЬТАТЫ: {passed}/{total} проверок пройдено")
print("=" * 70)

if passed == total:
    print("\n✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
    print("\n🎯 Статус версии v2.1.0:")
    print("   • ✅ ErrorTreeWidget (3-панельное дерево)")
    print("   • ✅ GraphVisualizerWidget (граф-визуализация)")
    print("   • ✅ ErrorVisualizationWidget (комбинированный компонент)")
    print("   • ✅ Три режима просмотра (Дерево, Граф, Разделённый)")
    print("   • ✅ Интегрирован в main_window_v4")
    print("   • ✅ Полная документация")
    print("   • ✅ Все зависимости установлены")
    print("\n🚀 Приложение готово к использованию!")
    print("\n📝 Чтобы запустить приложение:")
    print("   python -m n_audit.gui.main_app")
else:
    print(f"\n⚠️ ВНИМАНИЕ: {total - passed} проверок не пройдено!")
    print("\nНе пройденные проверки:")
    for name, condition in results:
        if not condition:
            print(f"   ❌ {name}")

print("\n" + "=" * 70)
print("📚 Документация:")
print("   • docs/GRAPH_VISUALIZATION_GUIDE.md - Полное руководство")
print("   • docs/USER_GUIDE_V4_1.md - Руководство пользователя")
print("   • CHANGELOG.md - История изменений")
print("=" * 70 + "\n")

sys.exit(0 if passed == total else 1)
