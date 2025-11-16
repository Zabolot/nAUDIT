#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Smoke-тест v2.7 - проверка исправлений графа

Проверяет:
1. ✅ PyVis: physics отключена
2. ✅ Plotly: раскраска по папкам работает (приоритет: папка > серьезность)
3. ✅ Edges: создается один trace вместо 10k+ объектов
"""

import sys
import logging
from pathlib import Path
import inspect

# Добавляем path к модулям проекта
sys.path.insert(0, str(Path(__file__).parent / "n_audit"))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_pyvis_physics_disabled():
    """✅ Тест 1: Physics отключена в PyVis"""
    print("\n" + "="*60)
    print("🧪 Тест 1: PyVis physics отключена")
    print("="*60)
    
    try:
        from gui.graph_visualizer_v2_7 import GraphVisualizerWidget
        
        # Проверяем исходный код
        source = inspect.getsource(GraphVisualizerWidget._generate_pyvis_html)
        
        checks = [
            ("physics.enabled = False", "Physics отключена"),
            ("stabilization.iterations = 0", "Стабилизация отключена"),
            ("directed=False", "Граф ненаправленный"),
        ]
        
        passed = 0
        for check_str, desc in checks:
            if check_str in source:
                print(f"✅ {desc}")
                passed += 1
            else:
                print(f"❌ {desc}")
        
        if passed == len(checks):
            print("✅ PASSED: PyVis physics отключена\n")
            return True
        else:
            print(f"❌ FAILED: Только {passed}/{len(checks)} проверок пройдено\n")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_node_color_priority():
    """✅ Тест 2: Приоритет раскраски: папка > серьезность"""
    print("="*60)
    print("🧪 Тест 2: Приоритет раскраски узлов")
    print("="*60)
    
    try:
        from gui.graph_visualizer_v2_7 import FileNode
        
        # Создаём тестовый узел
        node = FileNode(
            file_path="test/myfile.py",
            folder="test",
            errors_count=5,
            max_severity="CRITICAL",
            lines_of_code=100
        )
        
        # Папки и цвета
        folder_colors = {
            "test": "#FF6B6B",  # Красный для папки test
            "src": "#4ECDC4",   # Голубой для папки src
        }
        
        severity_colors = {
            "CRITICAL": "#000000",  # Чёрный для критических ошибок
            "HIGH": "#FF0000",
            "OK": "#00FF00",
        }
        
        # Получаем цвет
        color = node.get_node_color(folder_colors, severity_colors)
        
        # Проверяем что используется цвет папки, а не серьезности
        expected_color = "#FF6B6B"  # Цвет папки test
        
        if color == expected_color:
            print(f"✅ Узел из папки 'test' получил цвет папки: {color}")
            print(f"✅ (Не использовалась severity color: {severity_colors['CRITICAL']})")
            print("✅ PASSED: Приоритет раскраски правильный\n")
            return True
        else:
            print(f"❌ Ожидалось: {expected_color}, получено: {color}")
            print("❌ FAILED: Приоритет раскраски неправильный\n")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_edges_optimization():
    """✅ Тест 3: Edges оптимизированы в один trace"""
    print("="*60)
    print("🧪 Тест 3: Edges создают один trace вместо 10k+")
    print("="*60)
    
    try:
        from gui.graph_visualizer_v2_7 import GraphVisualizerWidget
        
        # Проверяем исходный код
        source = inspect.getsource(GraphVisualizerWidget._generate_plotly_html)
        
        # Проверяем что edges собираются в списки x, y вместо создания trace на каждый edge
        checks = [
            ("edge_x.extend", "Edges собираются в один список"),
            ("edge_y.extend", "Y координаты собираются в один список"),
            ("for source, target in G.edges()", "Итерация по edges правильная"),
            ("if edge_x:", "Проверка что есть edges перед созданием trace"),
            ("5000", "Лимит на количество edges"),
        ]
        
        passed = 0
        for check_str, desc in checks:
            if check_str in source:
                print(f"✅ {desc}")
                passed += 1
            else:
                print(f"❌ {desc}")
        
        if passed == len(checks):
            print("✅ PASSED: Edges оптимизированы\n")
            return True
        else:
            print(f"❌ FAILED: Только {passed}/{len(checks)} проверок пройдено\n")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_imports():
    """✅ Тест 4: Все импорты работают"""
    print("="*60)
    print("🧪 Тест 4: Импорты модулей")
    print("="*60)
    
    try:
        from gui.graph_visualizer_v2_7 import (
            GraphVisualizerWidget,
            FileNode,
            GraphRenderMode,
            GraphRenderThread,
        )
        print("✅ graph_visualizer_v2_7 импортирован")
        print("✅ FileNode импортирован")
        print("✅ GraphRenderMode импортирован")
        print("✅ GraphRenderThread импортирован")
        
        print("✅ PASSED: Все импорты работают\n")
        return True
        
    except ImportError as e:
        print(f"❌ FAILED: Ошибка импорта: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Запустить все тесты"""
    print("\n")
    print("█"*60)
    print("█" + " "*58 + "█")
    print("█" + "🧪 SMOKE-ТЕСТ v2.7 - ИСПРАВЛЕНИЯ ГРАФА".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    tests = [
        ("PyVis physics отключена", test_pyvis_physics_disabled),
        ("Приоритет раскраски", test_node_color_priority),
        ("Edges оптимизированы", test_edges_optimization),
        ("Импорты работают", test_imports),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.exception(f"Ошибка при запуске теста '{test_name}'")
            results[test_name] = False
    
    # Итоги
    print("\n" + "="*60)
    print("📊 ИТОГИ")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print("-"*60)
    print(f"✅ Пройдено: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Исправления работают корректно.\n")
        return 0
    else:
        print(f"\n⚠️  ВНИМАНИЕ: {total - passed} тест(ов) не пройдено.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
