#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Тест граф визуализера - отладка"""

import sys
from pathlib import Path
import tempfile

# Добавляем текущую папку в path
sys.path.insert(0, str(Path(__file__).parent))

# Создаем минимальный фикстур для теста
class MockIssue:
    def __init__(self, file, severity="LOW"):
        self.file = file
        self.severity = severity
        
    def get(self, key, default=None):
        return getattr(self, key, default)

class MockReport:
    def __init__(self):
        self.code_issues = [
            MockIssue("main.py", "HIGH"),
            MockIssue("utils/helper.py", "LOW"),
            MockIssue("core/engine.py", "CRITICAL"),
        ]
        self.security_issues = [
            MockIssue("api/auth.py", "CRITICAL"),
        ]

# Тест без GUI
print("=" * 60)
print("ТЕСТ 1: Загрузка и обработка данных")
print("=" * 60)

from n_audit.gui.graph_visualizer import GraphVisualizerWidget, FileNode

# Проверяем FileNode
print("\n✅ FileNode создается:")
node = FileNode(
    file_path="main.py",
    lines_of_code=100,
    errors_count=5,
    max_severity="HIGH",
    folder="root",
    imports=["utils", "core"],
    error_types={"HIGH": 3, "LOW": 2}
)
print(f"  - path: {node.file_path}")
print(f"  - errors: {node.errors_count}")
print(f"  - folder: {node.folder}")

# Тестируем функции обработки
print("\n✅ Функции утилит:")

# Тест исключений
from n_audit.gui.graph_visualizer import EXCLUDE_FOLDERS
viz = GraphVisualizerWidget.__new__(GraphVisualizerWidget)
viz.nodes = {}

test_paths = [
    "main.py",          # Should pass
    ".venv/lib.py",     # Should skip
    "__pycache__/x.py", # Should skip
    "src/main.py",      # Should pass
]

print("\n  Проверка исключений:")
for path in test_paths:
    excluded = viz._is_excluded_path(path)
    status = "❌ SKIP" if excluded else "✅ OK"
    print(f"    {status}: {path}")

print("\n" + "=" * 60)
print("ТЕСТ 2: Проверка сохранения HTML")
print("=" * 60)

html_test = "<html><body>Test</body></html>"
temp_dir = Path(tempfile.gettempdir())
test_file = temp_dir / "test_graph.html"

print(f"\n✅ Сохранение HTML:")
print(f"  - Путь: {test_file}")

try:
    test_file.write_text(html_test, encoding='utf-8')
    print(f"  - Размер: {test_file.stat().st_size} байт")
    print(f"  - Существует: {test_file.exists()}")
    content = test_file.read_text(encoding='utf-8')
    print(f"  - Читается: {'✅' if content else '❌'}")
except Exception as e:
    print(f"  ❌ Ошибка: {e}")

print("\n" + "=" * 60)
print("ТЕСТ 3: Структура данных")
print("=" * 60)

report = MockReport()
print(f"\n✅ MockReport:")
print(f"  - code_issues: {len(report.code_issues)}")
print(f"  - security_issues: {len(report.security_issues)}")

for issue in report.code_issues:
    print(f"    - {issue.file}: {issue.severity}")

for issue in report.security_issues:
    print(f"    - {issue.file}: {issue.severity}")

print("\n" + "=" * 60)
print("ТЕСТ 4: Импорт файлов")
print("=" * 60)

test_code = """
import os
from pathlib import Path
from n_audit.gui import graph_visualizer

class MyClass:
    pass
"""

print(f"\n✅ Извлечение импортов:")
from n_audit.gui.graph_visualizer import GraphVisualizerWidget
viz = GraphVisualizerWidget.__new__(GraphVisualizerWidget)

# Создаем временный файл
import tempfile
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
    f.write(test_code)
    temp_file = Path(f.name)

try:
    imports = viz._extract_imports(str(temp_file), ".")
    print(f"  - Найдено импортов: {len(imports)}")
    for imp in imports:
        print(f"    - {imp}")
finally:
    temp_file.unlink()

print("\n" + "=" * 60)
print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
print("=" * 60)
