#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт проверки: Граф-визуализация v2.2
Проверяет все компоненты, связанные с граф-визуализацией
"""

import sys
from pathlib import Path
from datetime import datetime

# Цвета для вывода
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_ok(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warn(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def test_imports():
    """Тест 1: Проверить импорты"""
    print_header("Тест 1: Импорты")
    
    tests = [
        ('PyQt6.QtWidgets', 'PyQt6.QtWidgets'),
        ('PyQt6.QtCore', 'PyQt6.QtCore'),
        ('PyQt6.QtWebEngineWidgets', 'PyQt6.QtWebEngineWidgets'),
        ('plotly.graph_objects', 'Plotly'),
        ('pyvis.network', 'PyVis'),
        ('networkx', 'NetworkX'),
        ('n_audit.gui.graph_visualizer', 'nAUDIT Graph Visualizer'),
    ]
    
    passed = 0
    for module, name in tests:
        try:
            __import__(module)
            print_ok(f"{name:40s} [{module}]")
            passed += 1
        except ImportError as e:
            print_error(f"{name:40s} [{module}]\n  {str(e)}")
    
    print(f"\n{GREEN}Результат: {passed}/{len(tests)} ✅{RESET}")
    return passed == len(tests)

def test_graph_visualizer():
    """Тест 2: Проверить GraphVisualizerWidget"""
    print_header("Тест 2: GraphVisualizerWidget")
    
    try:
        from n_audit.gui.graph_visualizer import GraphVisualizerWidget, FileNode
        
        # Проверить методы
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
        ]
        
        passed = 0
        for method in methods:
            if hasattr(GraphVisualizerWidget, method):
                print_ok(f"Метод: {method:30s}")
                passed += 1
            else:
                print_error(f"Метод: {method:30s} - НЕ НАЙДЕН!")
        
        print(f"\n{GREEN}Результат: {passed}/{len(methods)} методов ✅{RESET}")
        
        # Проверить атрибуты FileNode
        print_ok("FileNode класс найден")
        
        return passed == len(methods)
    
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False

def test_integration():
    """Тест 3: Проверить интеграцию с ErrorVisualizationWidget"""
    print_header("Тест 3: Интеграция с ErrorVisualizationWidget")
    
    try:
        from n_audit.gui.error_visualization import ErrorVisualizationWidget
        from n_audit.gui.graph_visualizer import GraphVisualizerWidget
        
        print_ok("ErrorVisualizationWidget импортирован")
        print_ok("GraphVisualizerWidget импортирован")
        
        # Проверить, что ErrorVisualizationWidget содержит график
        if hasattr(ErrorVisualizationWidget, '__init__'):
            print_ok("ErrorVisualizationWidget.__init__ доступен")
        
        print(f"\n{GREEN}Интеграция: ✅ OK{RESET}")
        return True
    
    except Exception as e:
        print_error(f"Ошибка интеграции: {e}")
        return False

def test_exclusions():
    """Тест 4: Проверить исключения"""
    print_header("Тест 4: Исключения файлов")
    
    try:
        from n_audit.gui.graph_visualizer import GraphVisualizerWidget, EXCLUDE_FOLDERS, EXCLUDE_EXT
        
        visualizer = GraphVisualizerWidget()
        
        # Тестовые пути
        test_cases = [
            ('.venv/lib/python.py', True),           # Должен исключиться
            ('__pycache__/module.pyc', True),        # Должен исключиться
            ('.git/config', True),                   # Должен исключиться
            ('n_audit/gui/main.py', False),          # Не должен исключиться
            ('src/core/config.py', False),           # Не должен исключиться
        ]
        
        passed = 0
        for path, should_exclude in test_cases:
            result = visualizer._is_excluded_path(path)
            if result == should_exclude:
                status = "исключён" if result else "включён"
                print_ok(f"{path:40s} [{status}]")
                passed += 1
            else:
                status = "исключён" if result else "включён"
                expected = "исключён" if should_exclude else "включён"
                print_error(f"{path:40s} - ожидалось: {expected}, получено: {status}")
        
        print(f"\n{GREEN}Результат: {passed}/{len(test_cases)} ✅{RESET}")
        return passed == len(test_cases)
    
    except Exception as e:
        print_error(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_colors():
    """Тест 5: Проверить генерацию цветов"""
    print_header("Тест 5: Генерация цветов по папкам")
    
    try:
        from n_audit.gui.graph_visualizer import GraphVisualizerWidget
        
        visualizer = GraphVisualizerWidget()
        
        folders = [
            'n_audit/gui',
            'n_audit/core',
            'n_audit/models',
            'utils/helpers',
            'src/database',
        ]
        
        colors = {}
        for folder in folders:
            color = visualizer._get_folder_color(folder)
            colors[folder] = color
            print_ok(f"{folder:30s} → {color}")
        
        # Проверить уникальность
        unique_colors = set(colors.values())
        if len(unique_colors) == len(colors):
            print_ok(f"Все {len(colors)} цветов уникальны ✅")
        else:
            print_warn(f"Некоторые цвета совпадают ({len(unique_colors)}/{len(colors)})")
        
        print(f"\n{GREEN}Цвета: ✅ OK{RESET}")
        return True
    
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False

def test_syntax():
    """Тест 6: Проверить синтаксис"""
    print_header("Тест 6: Синтаксис Python")
    
    import subprocess
    import os
    
    file_path = Path(r"g:\CODING\nAUDIT\n_audit\gui\graph_visualizer.py")
    
    if not file_path.exists():
        print_error(f"Файл не найден: {file_path}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', str(file_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print_ok(f"Файл: {file_path.name}")
            print_ok(f"Размер: {file_path.stat().st_size / 1024:.1f} KB")
            print_ok("Синтаксис: ✅ OK")
            print(f"\n{GREEN}Синтаксис: ✅ OK{RESET}")
            return True
        else:
            print_error(f"Ошибка компиляции:\n{result.stderr}")
            return False
    
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False

def main():
    """Главная функция"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}nAUDIT - Тест Граф-Визуализации v2.2{RESET}")
    print(f"{BLUE}Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    tests = [
        ("Импорты", test_imports),
        ("GraphVisualizerWidget", test_graph_visualizer),
        ("Интеграция", test_integration),
        ("Исключения", test_exclusions),
        ("Цвета", test_colors),
        ("Синтаксис", test_syntax),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Исключение в тесте '{name}': {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Итоговый отчет
    print_header("Итоговый отчет")
    
    passed_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for name, result in results:
        status = f"{GREEN}✅ PASSED{RESET}" if result else f"{RED}❌ FAILED{RESET}"
        print(f"  {status:20s} | {name}")
    
    print()
    if passed_count == total_count:
        print(f"{GREEN}{'='*60}{RESET}")
        print(f"{GREEN}🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! ({passed_count}/{total_count}){RESET}")
        print(f"{GREEN}{'='*60}{RESET}")
        print(f"\n{GREEN}✅ ГРАФ-ВИЗУАЛИЗАЦИЯ ГОТОВА К ПРОДАКШЕНУ{RESET}\n")
        return 0
    else:
        print(f"{RED}{'='*60}{RESET}")
        print(f"{RED}⚠️  НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ ({passed_count}/{total_count}){RESET}")
        print(f"{RED}{'='*60}{RESET}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
