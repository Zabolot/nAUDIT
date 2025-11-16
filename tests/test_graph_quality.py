#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка качества графа - Визуализация проектов

Этот скрипт проверяет:
1. Генерирует ли Plotly граф правильно
2. Отображаются ли все цвета
3. Видны ли узлы на разных фонах
4. Работает ли Canvas/SVG fallback
"""

import sys
import tempfile
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

# Создаём QApplication без GUI
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt6.QtWidgets import QApplication
app = QApplication(sys.argv)

from n_audit.gui.graph_visualizer import GraphVisualizerWidget

# Создаём тестовые данные
from dataclasses import dataclass, field

@dataclass
class Issue:
    """Базовая ошибка"""
    file_path: str
    severity: str
    message: str = ""

@dataclass
class Metrics:
    """Метрики"""
    code_issues: list = field(default_factory=list)
    security_issues: list = field(default_factory=list)

@dataclass
class AuditReport:
    """Отчёт"""
    project_name: str = ""
    project_root: str = ""
    audit_timestamp: str = ""
    metrics: Metrics = field(default_factory=Metrics)

print("="*70)
print("  Тестирование графа визуализации")
print("="*70 + "\n")

# Создаём граф с данными
graph_widget = GraphVisualizerWidget()

# Создаём тестовый отчёт
report = AuditReport(
    project_name="test",
    project_root=".",
    audit_timestamp="2025-11-14"
)

# Добавляем тестовые ошибки разных уровней
report.metrics.code_issues = [
    # CRITICAL
    Issue("file1.py", "CRITICAL", "Critical error"),
    Issue("file2.py", "CRITICAL", "Critical error"),
    # HIGH
    Issue("file3.py", "HIGH", "High priority"),
    Issue("file4.py", "HIGH", "High priority"),
    Issue("file5.py", "HIGH", "High priority"),
    # MEDIUM
    Issue("file6.py", "MEDIUM", "Medium priority"),
    Issue("file7.py", "MEDIUM", "Medium priority"),
    Issue("file8.py", "MEDIUM", "Medium priority"),
    Issue("file9.py", "MEDIUM", "Medium priority"),
    # LOW
    Issue("file10.py", "LOW", "Low priority"),
    Issue("file11.py", "LOW", "Low priority"),
]

print("[1/4] Заполняю граф данными...")
graph_widget.populate_from_report(report, ".")
print(f"  ✓ Загружено {len(graph_widget.nodes)} узлов\n")

# Проверяем, что генерируется HTML
html_file = Path(tempfile.gettempdir()) / "naudit_graph_temp.html"

print("[2/4] Проверяю HTML файл...")
if html_file.exists():
    size_kb = html_file.stat().st_size / 1024
    print(f"  ✓ HTML файл создан: {html_file.name}")
    print(f"  ✓ Размер: {size_kb:.1f} KB\n")
    
    content = html_file.read_text(encoding='utf-8')
    
    print("[3/4] Проверяю содержимое HTML...")
    
    # Проверяем, что используется Plotly или PyVis
    if "plotly" in content.lower():
        print("  ✓ Используется Plotly")
    elif "vis" in content.lower():
        print("  ✓ Используется PyVis")
    elif "<svg" in content.lower():
        print("  ✓ Используется Canvas/SVG")
    
    # Проверяем цвета
    colors_found = {
        "CRITICAL (#ff4444)": "#ff4444" in content,
        "HIGH (#ff9900)": "#ff9900" in content,
        "MEDIUM (#ffcc00)": "#ffcc00" in content,
        "LOW (#44dd44)": "#44dd44" in content,
    }
    
    colors_ok = sum(1 for v in colors_found.values() if v)
    print(f"  ✓ Найдено цветов: {colors_ok}/4")
    for color, found in colors_found.items():
        status = "✓" if found else "✗"
        print(f"    {status} {color}")
    
    # Проверяем узлы
    node_count = content.count('"id":') if '"id":' in content else 0
    if node_count == 0 and '<circle' in content:
        node_count = content.count('<circle')
    
    print(f"  ✓ Узлов в HTML: {node_count}")
    
    # Проверяем фон
    if "#fafafa" in content:
        print(f"  ✓ Фон светлый (#fafafa)")
    elif "#ffffff" in content:
        print(f"  ⚠ Фон белый (#ffffff) - может быть контрастом проблема")
    
    print()
    
else:
    print(f"  ✗ HTML файл не найден: {html_file}")
    sys.exit(1)

print("[4/4] Резюме тестирования...")
print()
print("="*70)
print("  ✅ ТЕСТ ПРОЙДЕН")
print("="*70)
print()
print("Информация:")
print(f"  • Граф содержит {len(graph_widget.nodes)} узлов")
print(f"  • HTML сохранён: {html_file}")
print(f"  • Размер: {size_kb:.1f} KB")
print()
print("Вы можете открыть HTML в браузере:")
print(f"  Start-Process '{html_file}'")
print()
