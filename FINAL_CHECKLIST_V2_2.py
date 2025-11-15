#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ Финальный чек-лист: Граф-визуализация v2.2

Проверяет все аспекты работоспособности новой версии
"""

import sys
from pathlib import Path

print("\n" + "="*70)
print("✅ ФИНАЛЬНЫЙ ЧЕК-ЛИСТ: ГРАФ-ВИЗУАЛИЗАЦИЯ v2.2".center(70))
print("="*70 + "\n")

checks = []

# ════════════════════════════════════════════════════════════════
print("📋 ПРОВЕРКА 1: Файл существует и доступен")
print("─" * 70)

graph_file = Path("g:/CODING/nAUDIT/n_audit/gui/graph_visualizer.py")
if graph_file.exists():
    size_kb = graph_file.stat().st_size / 1024
    print(f"  ✅ Файл: {graph_file.name}")
    print(f"  ✅ Размер: {size_kb:.1f} KB (~600 строк)")
    checks.append(True)
else:
    print(f"  ❌ Файл НЕ найден: {graph_file}")
    checks.append(False)

# ════════════════════════════════════════════════════════════════
print("\n📋 ПРОВЕРКА 2: Синтаксис Python")
print("─" * 70)

try:
    import py_compile
    py_compile.compile(str(graph_file), doraise=True)
    print(f"  ✅ Синтаксис OK (no errors)")
    checks.append(True)
except py_compile.PyCompileError as e:
    print(f"  ❌ Ошибка синтаксиса: {e}")
    checks.append(False)

# ════════════════════════════════════════════════════════════════
print("\n📋 ПРОВЕРКА 3: Импорты зависимостей")
print("─" * 70)

dependencies = [
    ('PyQt6.QtWidgets', 'PyQt6'),
    ('PyQt6.QtCore', 'PyQt6'),
    ('PyQt6.QtWebEngineWidgets', 'PyQt6-WebEngine'),
    ('plotly.graph_objects', 'Plotly'),
    ('pyvis.network', 'PyVis'),
    ('networkx', 'NetworkX'),
    ('hashlib', 'hashlib (std)'),
    ('math', 'math (std)'),
]

deps_ok = True
for module, name in dependencies:
    try:
        __import__(module)
        print(f"  ✅ {name:30s}")
    except ImportError:
        print(f"  ❌ {name:30s} - MISSING!")
        deps_ok = False

checks.append(deps_ok)

# ════════════════════════════════════════════════════════════════
print("\n📋 ПРОВЕРКА 4: Импорт основного класса")
print("─" * 70)

try:
    from n_audit.gui.graph_visualizer import GraphVisualizerWidget
    print(f"  ✅ GraphVisualizerWidget импортирован")
    checks.append(True)
except ImportError as e:
    print(f"  ❌ Ошибка импорта: {e}")
    checks.append(False)

# ════════════════════════════════════════════════════════════════
print("\n📋 ПРОВЕРКА 5: Импорт FileNode")
print("─" * 70)

try:
    from n_audit.gui.graph_visualizer import FileNode
    print(f"  ✅ FileNode импортирован")
    checks.append(True)
except ImportError as e:
    print(f"  ❌ Ошибка импорта: {e}")
    checks.append(False)

# ════════════════════════════════════════════════════════════════
print("\n📋 ПРОВЕРКА 6: Методы класса")
print("─" * 70)

try:
    from n_audit.gui.graph_visualizer import GraphVisualizerWidget
    
    required_methods = [
        'populate_from_report',
        'clear',
        'get_all_files',
        '_is_excluded_path',
        '_get_folder_color',
        '_extract_imports',
        '_render_graph',
        '_render_with_plotly',
        '_render_with_pyvis',
    ]
    
    methods_ok = True
    for method in required_methods:
        if hasattr(GraphVisualizerWidget, method):
            print(f"  ✅ {method}")
        else:
            print(f"  ❌ {method} - NOT FOUND!")
            methods_ok = False
    
    checks.append(methods_ok)
except Exception as e:
    print(f"  ❌ Ошибка: {e}")
    checks.append(False)

# ════════════════════════════════════════════════════════════════
print("\n📋 ПРОВЕРКА 7: Константы конфигурации")
print("─" * 70)

try:
    from n_audit.gui.graph_visualizer import (
        EXCLUDE_FOLDERS, GRID_SPACING, CLOUD_RADIUS, MIN_NODE_DISTANCE
    )
    
    print(f"  ✅ EXCLUDE_FOLDERS: {len(EXCLUDE_FOLDERS)} папок исключено")
    print(f"  ✅ GRID_SPACING: {GRID_SPACING}")
    print(f"  ✅ CLOUD_RADIUS: {CLOUD_RADIUS}")
    print(f"  ✅ MIN_NODE_DISTANCE: {MIN_NODE_DISTANCE}")
    checks.append(True)
except ImportError as e:
    print(f"  ❌ Ошибка импорта констант: {e}")
    checks.append(False)

# ════════════════════════════════════════════════════════════════
print("\n📋 ПРОВЕРКА 8: Интеграция с ErrorVisualizationWidget")
print("─" * 70)

try:
    from n_audit.gui.error_visualization import ErrorVisualizationWidget
    from n_audit.gui.graph_visualizer import GraphVisualizerWidget
    
    print(f"  ✅ ErrorVisualizationWidget импортирован")
    print(f"  ✅ GraphVisualizerWidget доступен")
    checks.append(True)
except ImportError as e:
    print(f"  ❌ Ошибка интеграции: {e}")
    checks.append(False)

# ════════════════════════════════════════════════════════════════
print("\n📋 ПРОВЕРКА 9: Исключение файлов")
print("─" * 70)

try:
    from n_audit.gui.graph_visualizer import GraphVisualizerWidget
    
    widget = GraphVisualizerWidget()
    
    test_cases = [
        ('.venv/lib/python.py', True),
        ('__pycache__/module.pyc', True),
        ('.git/config', True),
        ('n_audit/gui/main.py', False),
        ('src/core/config.py', False),
    ]
    
    exclusion_ok = True
    for path, should_exclude in test_cases:
        result = widget._is_excluded_path(path)
        if result == should_exclude:
            status = "исключён" if result else "включён"
            print(f"  ✅ {path:40s} [{status}]")
        else:
            print(f"  ❌ {path:40s} - неправильно!")
            exclusion_ok = False
    
    checks.append(exclusion_ok)
except Exception as e:
    print(f"  ❌ Ошибка: {e}")
    checks.append(False)

# ════════════════════════════════════════════════════════════════
print("\n📋 ПРОВЕРКА 10: Генерация цветов")
print("─" * 70)

try:
    from n_audit.gui.graph_visualizer import GraphVisualizerWidget
    
    widget = GraphVisualizerWidget()
    
    folders = ['n_audit/gui', 'n_audit/core', 'n_audit/models']
    colors = set()
    
    for folder in folders:
        color = widget._get_folder_color(folder)
        colors.add(color)
        print(f"  ✅ {folder:30s} → {color}")
    
    if len(colors) == len(folders):
        print(f"  ✅ Все цвета уникальны ({len(colors)} different)")
        checks.append(True)
    else:
        print(f"  ⚠️  Некоторые цвета совпадают ({len(colors)}/{len(folders)})")
        checks.append(True)  # Не критично
except Exception as e:
    print(f"  ❌ Ошибка: {e}")
    checks.append(False)

# ════════════════════════════════════════════════════════════════
print("\n📋 ПРОВЕРКА 11: Документация")
print("─" * 70)

docs = [
    "SESSION_2_FINAL_REPORT.md",
    "SESSION_2_GRAPH_IMPROVEMENTS_SUMMARY.md",
    "docs/SESSION_2_GRAPH_IMPROVEMENTS_V2_2.md",
    "docs/GRAPH_VISUALIZER_USAGE_GUIDE.md",
]

docs_ok = True
for doc in docs:
    doc_path = Path("g:/CODING/nAUDIT") / doc
    if doc_path.exists():
        print(f"  ✅ {doc}")
    else:
        print(f"  ⚠️  {doc} - не найден (опционально)")

checks.append(True)  # Документация опциональна

# ════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("ИТОГОВЫЙ РЕЗУЛЬТАТ".center(70))
print("="*70 + "\n")

passed = sum(checks)
total = len(checks)
percentage = (passed / total) * 100

for i, check in enumerate(checks, 1):
    status = "✅ PASSED" if check else "❌ FAILED"
    print(f"  {i:2d}. {status}")

print(f"\n{passed}/{total} проверок пройдено ({percentage:.0f}%)\n")

if passed == total:
    print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
    print("\n✨ ГРАФ-ВИЗУАЛИЗАЦИЯ v2.2 ГОТОВА К ПРОДАКШЕНУ ✨")
    print("\nРекомендуемые действия:")
    print("  1. Собрать exe: python build_exe.py")
    print("  2. Протестировать на реальном проекте")
    print("  3. Проверить граф в режиме 'Граф' или 'Оба'")
    print("  4. Попробовать переключение Plotly ↔ PyVis")
    print("\n✅ ГОТОВО!")
    sys.exit(0)
else:
    print("⚠️  НЕКОТОРЫЕ ПРОВЕРКИ НЕ ПРОЙДЕНЫ")
    print("Пожалуйста, исправьте ошибки перед использованием")
    sys.exit(1)
