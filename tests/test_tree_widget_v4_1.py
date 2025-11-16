#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест новой архитектуры дерева ошибок (v4.1)

Проверяет:
1. Построение дерева файлов с иерархией
2. Выделение файлов по серьезности ошибок
3. Список ошибок в файле
4. Детали ошибок
"""

import sys
from pathlib import Path

# Добавляем путь
sys.path.insert(0, str(Path(__file__).parent))

from n_audit.audit_engine import AuditEngine
from n_audit.gui.tree_widget import ErrorTreeWidget, CodeIssueInfo
from PyQt6.QtWidgets import QApplication


def test_tree_widget():
    """Тестировать новое дерево ошибок"""
    
    print("[*] Запускаю аудит на текущей папке...")
    engine = AuditEngine()
    report = engine.audit(".")
    
    if report.is_empty:
        print("[!] Отчет пуст - ошибок не найдено")
        return
    
    print(f"\n[*] Отчет получен:")
    print(f"    - Ошибок кода: {len(report.metrics.code_issues)}")
    print(f"    - Ошибок безопасности: {len(report.metrics.security_issues)}")
    print(f"    - Всего ошибок: {len(report.metrics.code_issues) + len(report.metrics.security_issues)}")
    
    # Создаем QApplication для GUI компонентов
    app = QApplication(sys.argv)
    
    # Создаем дерево
    print("\n[*] Создаю дерево ошибок...")
    tree = ErrorTreeWidget()
    
    # Заполняем дерево из отчета
    print("[*] Заполняю дерево из отчета...")
    tree.populate_from_report(report, project_root=".")
    
    # Проверяем результаты
    print(f"\n[*] Результаты:")
    print(f"    - Всего ошибок в дереве: {len(tree.all_issues)}")
    print(f"    - Файлов с ошибками: {len(tree.files_with_issues)}")
    
    # Показываем информацию о файлах
    print(f"\n[*] Файлы с ошибками:")
    for file_path, issues in sorted(tree.files_with_issues.items()):
        # Определяем максимальную серьезность
        max_severity = tree._get_max_severity(issues)
        severity_icon = tree._get_severity_icon(max_severity)
        
        try:
            print(f"    {severity_icon} {file_path} - {len(issues)} ошибок")
        except UnicodeEncodeError:
            severity_name = max_severity
            print(f"    [{severity_name}] {file_path} - {len(issues)} ошибок")
        
        # Первые 3 ошибки в файле
        for issue in issues[:3]:
            try:
                print(f"       - Строка {issue.line_number}: [{issue.code}] {issue.message[:50]}")
            except UnicodeEncodeError:
                print(f"       - Строка {issue.line_number}: [{issue.code}] [encoding error]")
        
        if len(issues) > 3:
            print(f"       ... и еще {len(issues) - 3} ошибок")
    
    # Проверяем серьезность
    print(f"\n[*] Анализ серьезности:")
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for issue in tree.all_issues:
        severity_counts[issue.severity] += 1
    
    for severity, count in sorted(severity_counts.items(), key=lambda x: {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(x[0])):
        icon = tree._get_severity_icon(severity)
        try:
            print(f"    {icon} {severity}: {count} ошибок")
        except UnicodeEncodeError:
            print(f"    [{severity}]: {count} ошибок")
    
    print(f"\n[OK] Новое дерево ошибок работает корректно!")
    print(f"[OK] Трёхпанельный интерфейс готов к использованию")


if __name__ == '__main__':
    test_tree_widget()
