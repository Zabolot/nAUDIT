#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug скрипт для проверки дерева ошибок
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from n_audit.audit_engine import AuditEngine

def test_report():
    """Протестировать отчет"""
    
    print("[*] Запускаю аудит на текущей папке...")
    engine = AuditEngine()
    report = engine.audit(".")
    
    print(f"\n[REPORT]")
    print(f"  is_empty: {report.is_empty}")
    print(f"  rating: {report.rating}")
    print(f"\n[METRICS]")
    print(f"  total_files: {report.metrics.total_files}")
    print(f"  total_lines: {report.metrics.total_lines}")
    print(f"  code_issues: {len(report.metrics.code_issues)}")
    print(f"  security_issues: {len(report.metrics.security_issues)}")
    
    print(f"\n[FIRST 5 CODE ISSUES]")
    for i, issue in enumerate(report.metrics.code_issues[:5]):
        print(f"  {i+1}. {issue.code} - {issue.message}")
        print(f"     File: {issue.file_path}:{issue.line_number}")
        print(f"     Type: {issue.issue_type}, Severity: {issue.severity}")
        print()
    
    print(f"\n[FIRST 5 SECURITY ISSUES]")
    for i, issue in enumerate(report.metrics.security_issues[:5]):
        print(f"  {i+1}. {issue.code} - {issue.message}")
        print(f"     File: {issue.file_path}:{issue.line_number}")
        print(f"     Type: {issue.issue_type}, Severity: {issue.severity}")
        print()
    
    # Теперь тестируем дерево
    print(f"\n[TREE WIDGET TEST]")
    from n_audit.gui.tree_widget import ErrorTreeWidget
    from PyQt6.QtWidgets import QApplication
    import sys
    
    # Создаем QApplication для QtGui компонентов
    if not QApplication.instance():
        app = QApplication(sys.argv)
    
    tree = ErrorTreeWidget()
    print(f"  Tree created")
    print(f"  Tree items before populate: {tree.tree.topLevelItemCount()}")
    
    tree.populate_from_report(report)
    print(f"  Tree items after populate (categories): {tree.tree.topLevelItemCount()}")
    
    # Показываем все категории и их элементы
    for i in range(tree.tree.topLevelItemCount()):
        category_item = tree.tree.topLevelItem(i)
        print(f"    Category {i}: {category_item.text(0)} - children: {category_item.childCount()}")
        # Показываем первые 3 файла в каждой категории
        for j in range(min(3, category_item.childCount())):
            file_item = category_item.child(j)
            print(f"      File {j}: {file_item.text(0)} - children: {file_item.childCount()}")
    print(f"  Tree total issues: {len(tree.issues)}")
    
    for category, issues in tree.issues.items():
        print(f"  Category {category}: {len(issues)} issues")


if __name__ == '__main__':
    test_report()
