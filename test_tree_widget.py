#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест для проверки дерева ошибок
"""

from pathlib import Path
import sys

# Добавляем путь
sys.path.insert(0, str(Path(__file__).parent))

from n_audit.audit_engine import AuditEngine
from n_audit.gui.tree_widget import ErrorTreeWidget
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget


def test_tree_widget():
    """Тестировать дерево ошибок"""
    
    # Запустим аудит на текущей папке
    print("[*] Запускаю аудит на нынешней папке...")
    engine = AuditEngine()
    report = engine.audit(".")
    
    print(f"[*] Отчет получен:")
    print(f"    - Статус пусто: {report.is_empty}")
    print(f"    - Ошибок кода: {len(report.metrics.code_issues)}")
    print(f"    - Проблем безопасности: {len(report.metrics.security_issues)}")
    print(f"    - Общее количество проблем: {len(report.metrics.code_issues) + len(report.metrics.security_issues)}")
    
    if report.is_empty:
        print("[!] ВНИМАНИЕ: Папка пуста!")
    
    # Создаем GUI приложение
    app = QApplication(sys.argv)
    
    # Создаем главное окно
    window = QMainWindow()
    window.setWindowTitle("Test ErrorTreeWidget")
    window.setGeometry(100, 100, 1000, 600)
    
    # Создаем виджет дерева
    tree_widget = ErrorTreeWidget()
    
    # Заполняем дерево
    print("[*] Заполняю дерево ошибок...")
    tree_widget.populate_from_report(report)
    
    print(f"[*] Дерево содержит {tree_widget.tree.topLevelItemCount()} категорий")
    
    # Показываем окно
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    layout.addWidget(tree_widget)
    window.setCentralWidget(central_widget)
    
    window.show()
    
    print("[OK] Дерево должно отображаться в окне")
    print("[*] Закройте окно для завершения теста")
    
    sys.exit(app.exec())


if __name__ == '__main__':
    test_tree_widget()
