#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Полная диагностика компонентов приложения
"""

import sys
from pathlib import Path

# Добавляем путь
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*70)
print("🔍 ДИАГНОСТИКА КОМПОНЕНТОВ nAUDIT v4.0")
print("="*70)

# 1. Проверяем основные модули
print("\n1️⃣  ПРОВЕРКА ИМПОРТОВ:")
print("-"*70)

try:
    from n_audit.audit_engine import AuditEngine
    print("✅ AuditEngine импортирован")
except Exception as e:
    print(f"❌ AuditEngine: {e}")

try:
    from n_audit.report_generator import ReportGenerator
    print("✅ ReportGenerator импортирован")
except Exception as e:
    print(f"❌ ReportGenerator: {e}")

try:
    from n_audit.recommendations_engine import RecommendationsEngine
    print("✅ RecommendationsEngine импортирован")
except Exception as e:
    print(f"❌ RecommendationsEngine: {e}")

# 2. Проверяем PyQt6
print("\n2️⃣  ПРОВЕРКА PyQt6:")
print("-"*70)

try:
    from PyQt6.QtWidgets import QApplication, QMainWindow
    print("✅ PyQt6.QtWidgets импортирован")
except Exception as e:
    print(f"❌ PyQt6.QtWidgets: {e}")

try:
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
    print("✅ PyQt6.QtCore импортирован")
except Exception as e:
    print(f"❌ PyQt6.QtCore: {e}")

try:
    from PyQt6.QtGui import QFont, QIcon
    print("✅ PyQt6.QtGui импортирован")
except Exception as e:
    print(f"❌ PyQt6.QtGui: {e}")

# 3. Проверяем GUI компоненты
print("\n3️⃣  ПРОВЕРКА GUI КОМПОНЕНТОВ:")
print("-"*70)

try:
    from n_audit.gui.main_window_v4 import MainWindowV4
    print("✅ MainWindowV4 импортирован")
except Exception as e:
    print(f"❌ MainWindowV4: {e}")

try:
    from n_audit.gui.error_visualization import ErrorVisualizationWidget
    print("✅ ErrorVisualizationWidget импортирован")
except Exception as e:
    print(f"❌ ErrorVisualizationWidget: {e}")

try:
    from n_audit.gui.tree_widget import ErrorTreeWidget
    print("✅ ErrorTreeWidget импортирован")
except Exception as e:
    print(f"❌ ErrorTreeWidget: {e}")

try:
    from n_audit.gui.metrics_visualizer import MetricsVisualizer
    print("✅ MetricsVisualizer импортирован")
except Exception as e:
    print(f"❌ MetricsVisualizer: {e}")

try:
    from n_audit.gui.graph_visualizer import GraphVisualizerWidget
    print("✅ GraphVisualizerWidget импортирован")
except Exception as e:
    print(f"❌ GraphVisualizerWidget: {e}")

# 4. Проверяем зависимости
print("\n4️⃣  ПРОВЕРКА ЗАВИСИМОСТЕЙ:")
print("-"*70)

deps = [
    'matplotlib',
    'pylint',
    'flake8',
    'mypy',
    'bandit',
    'safety',
    'radon',
    'networkx',
    'pyvis'
]

for dep in deps:
    try:
        __import__(dep)
        print(f"✅ {dep}")
    except ImportError:
        print(f"❌ {dep} - НЕ УСТАНОВЛЕН")

# 5. Проверяем стили
print("\n5️⃣  ПРОВЕРКА СТИЛЕЙ:")
print("-"*70)

try:
    from n_audit.gui.styles import MAIN_STYLESHEET, COLORS
    print("✅ Стили импортированы")
    print(f"   - Цветов: {len(COLORS)}")
    print(f"   - Размер stylesheet: {len(MAIN_STYLESHEET)} символов")
except Exception as e:
    print(f"❌ Стили: {e}")

# 6. Проверяем конфиги
print("\n6️⃣  ПРОВЕРКА КОНФИГУРАЦИИ:")
print("-"*70)

try:
    from n_audit.core import GameConfig
    print("✅ GameConfig импортирован")
except Exception as e:
    # Это может быть другой класс
    try:
        from n_audit.core import Config
        print("✅ Config импортирован")
    except:
        print("⚠️  Конфиг не найден (может быть нормально)")

print("\n" + "="*70)
print("✅ ДИАГНОСТИКА ЗАВЕРШЕНА")
print("="*70 + "\n")
