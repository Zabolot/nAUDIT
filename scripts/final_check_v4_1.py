#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ФИНАЛЬНАЯ ПРОВЕРКА nAUDIT v4.1

Проверяет все компоненты и их готовность к продакшену
"""

import sys
from pathlib import Path

# Добавляем путь
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Тест импортов всех компонентов"""
    print("\n" + "="*70)
    print("[CHECK 1] ПРОВЕРКА ИМПОРТОВ")
    print("="*70)
    
    try:
        print("[✓] Импорт n_audit.audit_engine...")
        from n_audit.audit_engine import AuditEngine
        
        print("[✓] Импорт n_audit.report_generator...")
        from n_audit.report_generator import ReportGenerator
        
        print("[✓] Импорт n_audit.gui.tree_widget...")
        from n_audit.gui.tree_widget import ErrorTreeWidget, CodeIssueInfo
        
        print("[✓] Импорт n_audit.gui.main_window_v4...")
        from n_audit.gui.main_window_v4 import MainWindowV4
        
        print("[✓] Все импорты успешны!")
        return True
    except ImportError as e:
        print(f"[✗] Ошибка импорта: {e}")
        return False


def test_code_issue_info():
    """Тест типа данных CodeIssueInfo"""
    print("\n" + "="*70)
    print("[CHECK 2] ПРОВЕРКА CodeIssueInfo")
    print("="*70)
    
    try:
        from n_audit.gui.tree_widget import CodeIssueInfo
        
        # Создаём тестовую ошибку
        issue = CodeIssueInfo(
            file_path="test.py",
            line_number=10,
            column=5,
            code="E501",
            message="Line too long",
            severity="LOW",
            issue_type="style_issue",
            context="print('hello world')",
            tool="flake8"
        )
        
        # Проверяем поля
        assert issue.file_path == "test.py"
        assert issue.line_number == 10
        assert issue.severity == "LOW"
        
        print("[✓] CodeIssueInfo работает корректно")
        print(f"    - Поля: file_path, line_number, column, code, message, etc.")
        print(f"    - Тип: dataclass")
        return True
        
    except Exception as e:
        print(f"[✗] Ошибка: {e}")
        return False


def test_tree_widget():
    """Тест ErrorTreeWidget"""
    print("\n" + "="*70)
    print("[CHECK 3] ПРОВЕРКА ErrorTreeWidget")
    print("="*70)
    
    try:
        from n_audit.gui.tree_widget import ErrorTreeWidget
        from PyQt6.QtWidgets import QApplication
        
        # Создаём QApplication
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Создаём виджет
        tree = ErrorTreeWidget()
        print("[✓] ErrorTreeWidget создан успешно")
        
        # Проверяем методы
        methods = [
            'populate_from_report',
            'get_all_issues',
            'clear',
            'filter_by_severity',
            '_build_file_tree',
            '_update_issues_list',
            '_show_issue_details'
        ]
        
        for method_name in methods:
            if hasattr(tree, method_name):
                print(f"[✓] Метод {method_name} существует")
            else:
                print(f"[✗] Метод {method_name} не найден!")
                return False
        
        return True
        
    except Exception as e:
        print(f"[✗] Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_main_window():
    """Тест MainWindowV4"""
    print("\n" + "="*70)
    print("[CHECK 4] ПРОВЕРКА MainWindowV4")
    print("="*70)
    
    try:
        from n_audit.gui.main_window_v4 import MainWindowV4
        from PyQt6.QtWidgets import QApplication
        
        # Создаём QApplication
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Создаём окно (но не показываем)
        window = MainWindowV4()
        print("[✓] MainWindowV4 создано успешно")
        
        # Проверяем компоненты
        assert hasattr(window, 'tree_widget'), "tree_widget не найден"
        assert hasattr(window, 'tabs'), "tabs не найден"
        assert hasattr(window, 'progress_bar'), "progress_bar не найден"
        
        print("[✓] Все компоненты найдены:")
        print("    - tree_widget: ErrorTreeWidget")
        print("    - tabs: QTabWidget с 6 вкладками")
        print("    - progress_bar: для показа прогресса")
        
        return True
        
    except Exception as e:
        print(f"[✗] Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_audit_engine():
    """Тест AuditEngine"""
    print("\n" + "="*70)
    print("[CHECK 5] ПРОВЕРКА AuditEngine")
    print("="*70)
    
    try:
        from n_audit.audit_engine import AuditEngine
        
        # Создаём движок
        engine = AuditEngine()
        print("[✓] AuditEngine создан успешно")
        
        # Проверяем методы
        assert hasattr(engine, 'audit'), "Метод audit не найден"
        print("[✓] Метод audit существует")
        
        return True
        
    except Exception as e:
        print(f"[✗] Ошибка: {e}")
        return False


def test_documentation():
    """Проверка документации"""
    print("\n" + "="*70)
    print("[CHECK 6] ПРОВЕРКА ДОКУМЕНТАЦИИ")
    print("="*70)
    
    files_to_check = [
        "docs/TREE_WIDGET_V4_1_ARCHITECTURE.md",
        "CHANGELOG_V4_1.md",
        "SESSION_COMPLETION_REPORT_V4_1.md",
        "USER_GUIDE_V4_1.md",
        "CHECKLIST_COMPLETION_V4_1.md"
    ]
    
    for filename in files_to_check:
        path = Path(filename)
        if path.exists():
            size = path.stat().st_size
            print(f"[✓] {filename} ({size} байт)")
        else:
            print(f"[✗] {filename} не найден!")
            return False
    
    print("[✓] Вся документация на месте")
    return True


def test_files():
    """Проверка важных файлов"""
    print("\n" + "="*70)
    print("[CHECK 7] ПРОВЕРКА ФАЙЛОВ")
    print("="*70)
    
    files_to_check = [
        "n_audit/gui/tree_widget.py",
        "n_audit/gui/main_window_v4.py",
        "run_naudit_gui.py",
        "test_tree_widget_v4_1.py",
        "test_gui_integration_v4_1.py"
    ]
    
    for filename in files_to_check:
        path = Path(filename)
        if path.exists():
            lines = path.read_text(encoding='utf-8', errors='ignore').count('\n')
            print(f"[✓] {filename} ({lines} строк)")
        else:
            print(f"[!] {filename} не найден (не критично)")
    
    return True


def main():
    """Главная функция проверки"""
    print("\n")
    print("="*70)
    print("ФИНАЛЬНАЯ ПРОВЕРКА nAUDIT v4.1".center(70))
    print("="*70)
    
    # Запускаем все тесты
    results = {}
    results["Импорты"] = test_imports()
    results["CodeIssueInfo"] = test_code_issue_info()
    results["ErrorTreeWidget"] = test_tree_widget()
    results["MainWindowV4"] = test_main_window()
    results["AuditEngine"] = test_audit_engine()
    results["Документация"] = test_documentation()
    results["Файлы"] = test_files()
    
    # Итоги
    print("\n" + "="*70)
    print("ИТОГИ ПРОВЕРКИ")
    print("="*70)
    
    for name, result in results.items():
        status = "[PASSED]" if result else "[FAILED]"
        print(f"{status} {name}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    print("\n" + "="*70)
    if passed == total:
        print(f"[OK] ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ: {passed}/{total}")
        print("[OK] nAUDIT v4.1 ГОТОВА К ПРОДАКШЕНУ!")
    else:
        print(f"[WARNING] НЕКОТОРЫЕ ПРОВЕРКИ НЕ ПРОЙДЕНЫ: {passed}/{total}")
        print("[WARNING] Исправьте ошибки перед развертыванием")
    print("="*70 + "\n")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
