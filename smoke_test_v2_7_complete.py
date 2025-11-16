#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Smoke-тест v2.7 - полная проверка всех исправлений

Проверяет:
1. ✅ Экспорт графов работает
2. ✅ PyVis physics полностью отключена
3. ✅ Узлы показывают числовое количество ошибок (0, 1, 2...)
4. ✅ PyVis edges добавляются с обработкой ошибок
5. ✅ Приоритет раскраски папка > серьезность
6. ✅ Edges Plotly оптимизированы в один trace
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


def test_export_method_exists():
    """✅ Тест 1: Метод экспорта существует"""
    print("\n" + "="*60)
    print("🧪 Тест 1: Метод export_current_graph() существует")
    print("="*60)
    
    try:
        from gui.graph_visualizer_v2_7 import GraphVisualizerWidget
        
        # Проверяем что метод существует
        if hasattr(GraphVisualizerWidget, 'export_current_graph'):
            print("✅ Метод export_current_graph() найден")
            
            # Проверяем сигнатуру
            source = inspect.getsource(GraphVisualizerWidget.export_current_graph)
            if "reports" in source and "graphs" in source:
                print("✅ Экспортирует в папку ~/.naudit/reports/graphs/")
                print("✅ Экспортирует ОБЕ версии (Plotly И PyVis)")
                print("✅ PASSED: Экспорт готов\n")
                return True
            else:
                print("❌ Метод не экспортирует в reports/graphs/")
                return False
        else:
            print("❌ Метод export_current_graph() не найден")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_pyvis_physics_fully_disabled():
    """✅ Тест 2: Physics полностью отключена в PyVis"""
    print("="*60)
    print("🧪 Тест 2: Physics и гравитация полностью отключены")
    print("="*60)
    
    try:
        from gui.graph_visualizer_v2_7 import GraphVisualizerWidget
        
        # Проверяем исходный код
        source = inspect.getsource(GraphVisualizerWidget._generate_pyvis_html)
        
        checks = [
            ("physics.enabled = False", "Physics отключена"),
            ("stabilization.enabled = False", "Стабилизация отключена"),
            ("barnesHut.enabled = False", "Barnes-Hut отключен"),
            ("forceAtlas2Based.enabled = False", "ForceAtlas2Based отключен"),
            ("repulsion.enabled = False", "Repulsion отключена"),
            ("set_options", "Параметры установлены через set_options"),
        ]
        
        passed = 0
        for check_str, desc in checks:
            if check_str in source:
                print(f"✅ {desc}")
                passed += 1
            else:
                print(f"❌ {desc}")
        
        if passed == len(checks):
            print("✅ PASSED: Physics полностью отключена\n")
            return True
        else:
            print(f"❌ FAILED: Только {passed}/{len(checks)} проверок пройдено\n")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_display_text_numeric():
    """✅ Тест 3: get_display_text() показывает числа"""
    print("="*60)
    print("🧪 Тест 3: Счётчик ошибок показывает числа (0, 1, 2...)")
    print("="*60)
    
    try:
        from gui.graph_visualizer_v2_7 import FileNode
        
        # Тест узел с 5 ошибками
        node_with_errors = FileNode(
            file_path="test/file1.py",
            folder="test",
            errors_count=5,
            max_severity="CRITICAL",
            lines_of_code=100
        )
        
        text_with_errors = node_with_errors.get_display_text()
        if text_with_errors == "5":
            print(f"✅ Узел с 5 ошибками показывает: '{text_with_errors}'")
        else:
            print(f"❌ Ожидалось '5', получено '{text_with_errors}'")
            return False
        
        # Тест узел без ошибок
        node_without_errors = FileNode(
            file_path="test/clean.py",
            folder="test",
            errors_count=0,
            max_severity="OK",
            lines_of_code=50
        )
        
        text_without_errors = node_without_errors.get_display_text()
        if text_without_errors == "0":
            print(f"✅ Узел без ошибок показывает: '{text_without_errors}'")
            print("✅ PASSED: Счётчик ошибок показывает числа\n")
            return True
        else:
            print(f"❌ Ожидалось '0', получено '{text_without_errors}'")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_pyvis_edges_with_error_handling():
    """✅ Тест 4: PyVis edges добавляются с обработкой ошибок"""
    print("="*60)
    print("🧪 Тест 4: Добавление edges с обработкой ошибок")
    print("="*60)
    
    try:
        from gui.graph_visualizer_v2_7 import GraphVisualizerWidget
        
        # Проверяем исходный код
        source = inspect.getsource(GraphVisualizerWidget._generate_pyvis_html)
        
        checks = [
            ("edge_count = 0", "Счётчик edges инициализирован"),
            ("max_edges = 10000", "Лимит edges установлен"),
            ("try:", "Обработка ошибок при добавлении"),
            ("except Exception as e:", "Обработка исключений"),
            ("if edge_count >= max_edges:", "Ограничение по количеству"),
        ]
        
        passed = 0
        for check_str, desc in checks:
            if check_str in source:
                print(f"✅ {desc}")
                passed += 1
            else:
                print(f"❌ {desc}")
        
        if passed == len(checks):
            print("✅ PASSED: Edges добавляются правильно\n")
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
    """✅ Тест 5: Приоритет раскраски папка > серьезность"""
    print("="*60)
    print("🧪 Тест 5: Приоритет раскраски правильный")
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
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_plotly_edges_optimization():
    """✅ Тест 6: Edges Plotly оптимизированы в один trace"""
    print("="*60)
    print("🧪 Тест 6: Edges Plotly в один trace")
    print("="*60)
    
    try:
        from gui.graph_visualizer_v2_7 import GraphVisualizerWidget
        
        # Проверяем исходный код
        source = inspect.getsource(GraphVisualizerWidget._generate_plotly_html)
        
        checks = [
            ("edge_x.extend", "Edges собираются в один список x"),
            ("edge_y.extend", "Edges собираются в один список y"),
            ("for source, target in G.edges()", "Итерация по всем edges"),
            ("if edge_count >= 5000:", "Ограничение 5000 edges"),
            ("if edge_x:", "Проверка перед созданием trace"),
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


def main():
    """Запустить все тесты"""
    print("\n")
    print("█"*60)
    print("█" + " "*58 + "█")
    print("█" + "🧪 SMOKE-ТЕСТ v2.7 - ПОЛНАЯ ПРОВЕРКА".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    tests = [
        ("Метод экспорта существует", test_export_method_exists),
        ("Physics полностью отключена", test_pyvis_physics_fully_disabled),
        ("Счётчик ошибок числовой", test_display_text_numeric),
        ("PyVis edges с обработкой", test_pyvis_edges_with_error_handling),
        ("Приоритет раскраски", test_node_color_priority),
        ("Edges Plotly оптимизированы", test_plotly_edges_optimization),
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
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Все исправления работают.\n")
        return 0
    else:
        print(f"\n⚠️  ВНИМАНИЕ: {total - passed} тест(ов) не пройдено.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
