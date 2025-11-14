#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Отладочный скрипт для проверки графа"""

import sys
from pathlib import Path
import tempfile

# Нужна QApplication для работы с Qt
from PyQt6.QtWidgets import QApplication
app = QApplication(sys.argv)

# Добавляем проект в path
sys.path.insert(0, str(Path(__file__).parent))

# Простые структуры данных вместо импорта из несуществующих модулей
from dataclasses import dataclass, field

@dataclass
class Issue:
    """Базовый класс проблемы"""
    file_path: str
    severity: str
    message: str

@dataclass
class CodeIssue(Issue):
    """Ошибка в коде"""
    line: int = 0
    column: int = 1
    rule: str = ""

@dataclass
class SecurityIssue(Issue):
    """Проблема безопасности"""
    vulnerability_type: str = ""
    cve: str = ""
    cvss_score: float = 0.0

@dataclass
class Metrics:
    """Метрики аудита"""
    code_issues: list = field(default_factory=list)
    security_issues: list = field(default_factory=list)

@dataclass
class AuditReport:
    """Отчёт аудита"""
    project_name: str = ""
    project_root: str = ""
    audit_timestamp: str = ""
    metrics: Metrics = field(default_factory=Metrics)

from n_audit.gui.graph_visualizer import GraphVisualizerWidget

# Создаём тестовый отчёт с данными
report = AuditReport(
    project_name="nAUDIT",
    project_root=str(Path(__file__).parent),
    audit_timestamp="2025-11-14"
)

# Добавляем тестовые ошибки (код с ошибками)
report.metrics.code_issues = [
    CodeIssue(
        file_path="n_audit/gui/tree_widget.py",
        line=10,
        column=1,
        severity="HIGH",
        rule="undefined-variable",
        message="Undefined variable 'x'"
    ),
    CodeIssue(
        file_path="n_audit/gui/graph_visualizer.py",
        line=20,
        column=5,
        severity="MEDIUM",
        rule="unused-import",
        message="Unused import 'sys'"
    ),
    CodeIssue(
        file_path="n_audit/core/game_config.py",
        line=5,
        column=1,
        severity="LOW",
        rule="line-too-long",
        message="Line too long (120 > 100)"
    ),
    CodeIssue(
        file_path="n_audit/audit_engine.py",
        line=50,
        column=10,
        severity="CRITICAL",
        rule="sql-injection",
        message="Potential SQL injection"
    ),
]

# Добавляем безопасность ошибки
report.metrics.security_issues = [
    SecurityIssue(
        file_path="n_audit/gui/tree_widget.py",
        severity="CRITICAL",
        vulnerability_type="hardcoded-secret",
        message="Hardcoded API key found",
        cve="",
        cvss_score=9.8
    ),
    SecurityIssue(
        file_path="n_audit/main.py",
        severity="HIGH",
        vulnerability_type="insecure-pickle",
        message="Insecure pickle usage",
        cve="",
        cvss_score=7.5
    ),
]

print("[DEBUG] Создаю GraphVisualizerWidget...")
graph_widget = GraphVisualizerWidget()

print("[DEBUG] Заполняю граф из отчёта...")
graph_widget.populate_from_report(report, str(Path(__file__).parent))

print("[DEBUG] Проверяю данные...")
print(f"  - Количество узлов: {len(graph_widget.nodes)}")
for file_path, node in graph_widget.nodes.items():
    print(f"    * {file_path}: {node.errors_count} ошибок, max_severity={node.max_severity}")

print("[DEBUG] Проверяю HTML файл...")
html_file = Path(tempfile.gettempdir()) / "naudit_graph_temp.html"
if html_file.exists():
    print(f"  ✓ HTML файл создан: {html_file}")
    
    # Проверяем содержимое HTML
    html_content = html_file.read_text(encoding='utf-8')
    
    # Ищем узлы в JavaScript коде
    if "nodes = new vis.DataSet(" in html_content:
        # Получаем данные узлов
        start = html_content.find("nodes = new vis.DataSet([") + len("nodes = new vis.DataSet(")
        end = html_content.find("]", start) + 1
        nodes_json = html_content[start:end]
        
        # Подсчитываем узлы (грубо)
        node_count = nodes_json.count('"id":')
        print(f"  - Узлов в HTML: {node_count}")
        
        # Ищем информацию о цветах
        if "#ff4444" in html_content:
            print(f"  - Красные узлы (CRITICAL): найдены")
        if "#ff9900" in html_content:
            print(f"  - Оранжевые узлы (HIGH): найдены")
        if "#ffcc00" in html_content:
            print(f"  - Жёлтые узлы (MEDIUM): найдены")
        if "#44dd44" in html_content:
            print(f"  - Зелёные узлы (LOW): найдены")
            
        # Проверяем стиль фона
        if "background-color: #ffffff" in html_content or "background: #ffffff" in html_content:
            print(f"  - Фон белый (#ffffff)")
        else:
            print(f"  - Фон НЕ белый, проверяем...")
            if "background-color:" in html_content:
                import re
                bg_matches = re.findall(r'background-color:\s*([#\w]+)', html_content)
                print(f"    Найденные цвета фона: {set(bg_matches)}")
    else:
        print("  ! Узлы не найдены в HTML файле")
        # Выводим часть HTML для отладки
        print("\n=== ЧАСТЬ HTML (первые 2000 символов) ===")
        print(html_content[:2000])
        print("=== КОНЕЦ ===\n")
else:
    print(f"  ✗ HTML файл не найден: {html_file}")

print("\n[DEBUG] Проверка завершена!")
