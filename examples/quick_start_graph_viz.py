#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрый запуск nAUDIT v2.1.0 с граф-визуализацией

Этот скрипт:
1. Проверяет все компоненты
2. Проверяет все зависимости
3. Запускает основное приложение
"""

import sys
import subprocess
from pathlib import Path

print("\n" + "="*70)
print("🚀 nAUDIT v2.1.0 - Быстрый запуск")
print("="*70)

# Шаг 1: Проверка окружения
print("\n[1/3] Проверка окружения...")

try:
    import PyQt6
    print(f"  ✓ PyQt6 {PyQt6.__version__}")
except ImportError as e:
    print(f"  ✗ PyQt6 не установлен: {e}")
    sys.exit(1)

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    print(f"  ✓ PyQt6-WebEngine установлен")
except ImportError as e:
    print(f"  ✗ PyQt6-WebEngine не установлен: {e}")
    print("\nУстановите:")
    print("  pip install PyQt6-WebEngine")
    sys.exit(1)

try:
    import networkx
    print(f"  ✓ networkx {networkx.__version__}")
except ImportError as e:
    print(f"  ✗ networkx не установлен")
    sys.exit(1)

try:
    import pyvis
    print(f"  ✓ pyvis установлен")
except ImportError as e:
    print(f"  ✗ pyvis не установлен")
    sys.exit(1)

# Шаг 2: Проверка компонентов
print("\n[2/3] Проверка компонентов...")

try:
    from n_audit.gui.error_visualization import ErrorVisualizationWidget
    print("  ✓ ErrorVisualizationWidget")
except ImportError as e:
    print(f"  ✗ ErrorVisualizationWidget: {e}")
    sys.exit(1)

try:
    from n_audit.gui.graph_visualizer import GraphVisualizerWidget
    print("  ✓ GraphVisualizerWidget")
except ImportError as e:
    print(f"  ✗ GraphVisualizerWidget: {e}")
    sys.exit(1)

try:
    from n_audit.gui.tree_widget import ErrorTreeWidget
    print("  ✓ ErrorTreeWidget")
except ImportError as e:
    print(f"  ✗ ErrorTreeWidget: {e}")
    sys.exit(1)

# Шаг 3: Запуск приложения
print("\n[3/3] Запуск приложения...")
print("\n" + "="*70)
print("✨ Приложение запущено!")
print("="*70)
print("\nОсновные функции:")
print("  🌳 Вкладка 'Ошибки' - Интерактивное дерево ошибок")
print("  🕸️  Режим 'Граф' - Визуализация всех файлов проекта")
print("  📊 Режим 'Оба' - Дерево и граф одновременно")
print("\nПанель управления графом:")
print("  • Фильтр по серьезности ошибок")
print("  • Масштабирование узлов (50-200%)")
print("  • Переключение метак и связей")
print("  • Кнопка обновления графа")
print("\n" + "="*70 + "\n")

# Запуск приложения
try:
    from n_audit.gui.main_app import main
    main()
except Exception as e:
    print(f"\n✗ Ошибка при запуске: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
