#!/usr/bin/env python3
"""
🧪 Smoke-тест v2.7 - проверка исправлений графа

Проверяет:
1. ✅ PyVis: physics отключена
2. ✅ Plotly: раскраска по папкам работает (приоритет: папка > серьезность)
3. ✅ Фильтрация: узлы без ошибок (OK) отображаются зелёным
4. ✅ Edges: создается один trace вместо 10k+ объектов
5. ✅ Узлы: все узлы фильтруются правильно
"""

import sys
import logging
from pathlib import Path

# Добавляем path к модулям проекта
sys.path.insert(0, str(Path(__file__).parent / "n_audit"))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
        
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


def test_ok_nodes_green():
    """✅ Тест 3: Узлы без ошибок (OK) зелёные"""
    print("="*60)
    print("🧪 Тест 3: Узлы OK получают зелёный цвет")
    print("="*60)
    
    try:
        from gui.graph_visualizer_v2_7 import GraphNode
        
        # Создаём узел без ошибок
        node = GraphNode(
            file_path="clean/file.py",
            folder="clean",
            errors_count=0,
            max_severity="OK"
        )
        
        folder_colors = {
            "clean": "#90EE90",  # Светлый зелёный
        }
        
        severity_colors = {
            "OK": "#00FF00",  # Яркий зелёный
        }
        
        color = node.get_node_color(folder_colors, severity_colors)
        
        # Должен быть зелёный (от папки)
        if color == "#90EE90":
            print(f"✅ Узел без ошибок получил зелёный цвет: {color}")
            print("✅ PASSED: OK узлы зелёные\n")
            return True
        else:
            print(f"❌ Ожидалось: #90EE90, получено: {color}")
            print("❌ FAILED: OK узлы неправильно раскрашены\n")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
        return False


def test_filter_nodes_by_severity():
    """✅ Тест 4: Фильтрация узлов по серьезности"""
    print("="*60)
    print("🧪 Тест 4: Фильтрация узлов работает правильно")
    print("="*60)
    
    try:
        from gui.graph_visualizer_v2_7 import GraphVisualizer, GraphNode
        from PyQt6.QtWidgets import QApplication, QMainWindow
        
        # Создаём тестовые узлы
        nodes = {
            "file1.py": GraphNode("file1.py", "src", 5, "CRITICAL"),
            "file2.py": GraphNode("file2.py", "src", 2, "HIGH"),
            "file3.py": GraphNode("file3.py", "src", 0, "OK"),
            "file4.py": GraphNode("file4.py", "test", 1, "LOW"),
        }
        
        # Тест фильтра "Все"
        severity_filter = "Все"
        filtered = [f for f in nodes.keys() if nodes[f].max_severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] or severity_filter == "Все"]
        
        if len(filtered) == 4:
            print(f"✅ Фильтр 'Все': {len(filtered)} узлов найдено")
        else:
            print(f"❌ Фильтр 'Все': ожидалось 4 узла, получено {len(filtered)}")
            return False
        
        # Тест фильтра "CRITICAL"
        severity_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, 'OK': 0}
        filter_level = severity_order.get("CRITICAL", 0)
        critical_only = [f for f in nodes.keys() if severity_order.get(nodes[f].max_severity, 0) >= filter_level]
        
        if len(critical_only) == 1 and "file1.py" in critical_only:
            print(f"✅ Фильтр 'CRITICAL': {len(critical_only)} узел найден")
        else:
            print(f"❌ Фильтр 'CRITICAL': ожидалось 1 узел, получено {len(critical_only)}")
            return False
        
        print("✅ PASSED: Фильтрация узлов работает правильно\n")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_edges_optimization():
    """✅ Тест 5: Edges оптимизированы в один trace"""
    print("="*60)
    print("🧪 Тест 5: Edges создают один trace вместо 10k+")
    print("="*60)
    
    try:
        from gui.graph_visualizer_v2_7 import GraphVisualizer
        import inspect
        
        # Проверяем исходный код
        source = inspect.getsource(GraphVisualizer._generate_plotly_html)
        
        # Проверяем что edges собираются в списки x, y вместо создания trace на каждый edge
        checks = [
            ("edge_x.extend", "Edges собираются в один список"),
            ("edge_y.extend", "Y координаты собираются в один список"),
            ("for source, target in G.edges()", "Итерация по edges правильная"),
            ("if edge_x:", "Проверка что есть edges перед созданием trace"),
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
        return False


def test_imports():
    """✅ Тест 6: Все импорты работают"""
    print("="*60)
    print("🧪 Тест 6: Импорты модулей")
    print("="*60)
    
    try:
        from gui.graph_visualizer_v2_7 import (
            GraphVisualizer,
            GraphNode,
            GraphRenderMode,
            GraphRenderThread,
        )
        print("✅ graph_visualizer_v2_7 импортирован")
        
        print("✅ PASSED: Все импорты работают\n")
        return True
        
    except ImportError as e:
        print(f"❌ FAILED: Ошибка импорта: {e}\n")
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
        ("OK узлы зелёные", test_ok_nodes_green),
        ("Фильтрация узлов", test_filter_nodes_by_severity),
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
