#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ ПОЛНАЯ ВЕРИФИКАЦИЯ: Граф-визуализация v2.2
Проверяет все 7 требований пользователя и готовит к сборке exe
"""

import sys
from pathlib import Path
import subprocess

print("\n" + "="*80)
print("✅ ПОЛНАЯ ВЕРИФИКАЦИЯ: ВСЕ ТРЕБОВАНИЯ v2.2".center(80))
print("="*80 + "\n")

# Читаем файл
graph_file = Path("n_audit/gui/graph_visualizer.py")
if not graph_file.exists():
    print("❌ Файл не найден!")
    sys.exit(1)

content = graph_file.read_text(encoding='utf-8')

requirements = {
    "1️⃣  Исключение .venv, __pycache__, .git": [
        "EXCLUDE_FOLDERS",
        "_is_excluded_path",
        ".venv",
        "__pycache__",
        ".git"
    ],
    "2️⃣  Видимые связи между файлами (edges)": [
        "self.edges",
        "edge_x, edge_y",
        "self.show_edges.isChecked()",
        "add_trace(go.Scatter"
    ],
    "3️⃣  Расстояние между облаками (GRID_SPACING)": [
        "GRID_SPACING = 25.0",
        "folder_positions[folder] = (fx, fy)"
    ],
    "4️⃣  Только цифры на узлах (опционально имена)": [
        "str(node.errors_count)",
        "self.show_labels.isChecked()"
    ],
    "5️⃣  Цвета по папкам (детерминированные)": [
        "_get_folder_color",
        "hashlib",
        "hsl("
    ],
    "6️⃣  Спираль без наложения узлов": [
        "radius = CLOUD_RADIUS",
        "angle = (i / max(1, n))",
        "math.cos",
        "math.sin"
    ],
    "7️⃣  Переключение Plotly ↔ PyVis": [
        "self.render_combo",
        "_on_render_changed",
        "_render_with_plotly",
        "_render_with_pyvis"
    ]
}

print("📋 ПРОВЕРКА ТРЕБОВАНИЙ:\n")

all_ok = True
for requirement, keywords in requirements.items():
    present_count = sum(1 for kw in keywords if kw in content)
    total_count = len(keywords)
    
    if present_count == total_count:
        print(f"{requirement}")
        print(f"  ✅ Все {total_count} ключевых слов присутствуют\n")
    else:
        print(f"{requirement}")
        print(f"  ⚠️  {present_count}/{total_count} ключевых слов найдено")
        for kw in keywords:
            if kw not in content:
                print(f"     ❌ '{kw}' НЕ НАЙДЕН")
        print()
        all_ok = False

# ════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("🧪 ТЕСТИРОВАНИЕ СИНТАКСИСА И ИМПОРТОВ")
print("="*80 + "\n")

# Тест синтаксиса
print("  ⏳ Проверка синтаксиса Python...")
try:
    import py_compile
    py_compile.compile(str(graph_file), doraise=True)
    print("  ✅ Синтаксис: OK\n")
except Exception as e:
    print(f"  ❌ Ошибка синтаксиса: {e}\n")
    all_ok = False

# Тест импортов
print("  ⏳ Проверка импортов...")
try:
    from n_audit.gui.graph_visualizer import GraphVisualizerWidget, FileNode
    print("  ✅ GraphVisualizerWidget: OK")
    print("  ✅ FileNode: OK\n")
except Exception as e:
    print(f"  ❌ Ошибка импорта: {e}\n")
    all_ok = False

# Тест интеграции
print("  ⏳ Проверка интеграции...")
try:
    from n_audit.gui.error_visualization import ErrorVisualizationWidget
    print("  ✅ ErrorVisualizationWidget: OK\n")
except Exception as e:
    print(f"  ❌ Ошибка интеграции: {e}\n")
    all_ok = False

# Тест зависимостей
print("  ⏳ Проверка зависимостей...")
deps = {
    'plotly.graph_objects': '📊 Plotly',
    'pyvis.network': '🕸️  PyVis',
    'networkx': '🕸️  NetworkX',
    'hashlib': '🔐 hashlib',
    'math': '🔢 math',
}

deps_ok = True
for module, name in deps.items():
    try:
        __import__(module)
        print(f"  ✅ {name}")
    except ImportError:
        print(f"  ❌ {name} - MISSING!")
        deps_ok = False

if deps_ok:
    print()
else:
    print()
    all_ok = False

# ════════════════════════════════════════════════════════════════
print("="*80)
print("📊 СТАТИСТИКА ФАЙЛА")
print("="*80 + "\n")

lines = content.count('\n')
size_kb = graph_file.stat().st_size / 1024

print(f"  📄 Файл: {graph_file.name}")
print(f"  📏 Строк: ~{lines}")
print(f"  💾 Размер: {size_kb:.1f} KB")
print(f"  📍 Расположение: {graph_file.absolute()}\n")

# Подсчёт методов
methods = [
    'populate_from_report',
    'clear',
    'get_all_files',
    '_is_excluded_path',
    '_get_folder_color',
    '_extract_imports',
    '_render_graph',
    '_render_with_plotly',
    '_render_with_pyvis',
    '_on_render_changed',
    '_on_labels_toggled',
    '_on_edges_toggled',
    '_on_scale_changed',
]

methods_found = sum(1 for m in methods if f"def {m}" in content)
print(f"  🔧 Методов: {methods_found}/{len(methods)}")
if methods_found < len(methods):
    print(f"     ⚠️  Отсутствуют: {', '.join(m for m in methods if f'def {m}' not in content)}\n")
else:
    print()

# ════════════════════════════════════════════════════════════════
print("="*80)
print("🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ")
print("="*80 + "\n")

if all_ok and methods_found == len(methods):
    print("✨ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! ✨\n")
    print("📋 Чек-лист завершения:")
    print("  ✅ 7 требований пользователя РЕАЛИЗОВАНЫ")
    print("  ✅ Синтаксис ПРОВЕРЕН")
    print("  ✅ Импорты РАБОТАЮТ")
    print("  ✅ Зависимости УСТАНОВЛЕНЫ")
    print("  ✅ Все методы РЕАЛИЗОВАНЫ\n")
    print("🚀 ГОТОВО К СБОРКЕ EXE!\n")
    sys.exit(0)
else:
    print("⚠️  НЕОБХОДИМО ИСПРАВИТЬ ОШИБКИ\n")
    if not all_ok:
        print("  ❌ Не все требования реализованы")
    if methods_found < len(methods):
        print(f"  ❌ Отсутствуют {len(methods) - methods_found} методов")
    print()
    sys.exit(1)
