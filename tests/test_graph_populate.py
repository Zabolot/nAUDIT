#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест логики populate_from_report без GUI
"""

import sys
from pathlib import Path
import tempfile

sys.path.insert(0, str(Path(__file__).parent))

class MockIssue:
    def __init__(self, file, severity="LOW"):
        self.file = file
        self.severity = severity
        
    def get(self, key, default=None):
        if key == 'file':
            return self.file
        elif key == 'severity':
            return self.severity
        return default

class MockReport:
    def __init__(self):
        self.code_issues = [
            MockIssue("src/main.py", "HIGH"),
            MockIssue("src/utils.py", "LOW"),
        ]
        self.security_issues = [
            MockIssue("src/auth.py", "CRITICAL"),
        ]

print("=" * 70)
print("ТЕСТ: Логика populate_from_report")
print("=" * 70)

# Создаем тестовый проект
test_root = Path(tempfile.gettempdir()) / "test_naudit_graph"
test_root.mkdir(exist_ok=True)

src_dir = test_root / "src"
src_dir.mkdir(exist_ok=True)

# Создаем файлы
(src_dir / "main.py").write_text("print('hello')")
(src_dir / "utils.py").write_text("def help(): pass")
(src_dir / "auth.py").write_text("pass")

print(f"\n✅ Тестовый проект: {test_root}")
print(f"   Файлы: {list(src_dir.glob('*.py'))}")

# Тестируем логику
report = MockReport()
print(f"\n✅ Mock report:")
print(f"   code_issues: {len(report.code_issues)}")
print(f"   security_issues: {len(report.security_issues)}")

# Симулируем populate_from_report
print("\n" + "=" * 70)
print("СЦЕНАРИЙ: populate_from_report вызывается")
print("=" * 70)

files_info = {}

# Обработка code_issues
print("\n[1] Обработка code_issues...")
for issue in report.code_issues:
    path = issue.get('file', '')
    if path not in files_info:
        files_info[path] = {'errors': 0}
    files_info[path]['errors'] += 1
    print(f"     ✅ Добавлен: {path}")

# Обработка security_issues
print("\n[2] Обработка security_issues...")
for issue in report.security_issues:
    path = issue.get('file', '')
    if path not in files_info:
        files_info[path] = {'errors': 0}
    files_info[path]['errors'] += 1
    print(f"     ✅ Добавлен: {path}")

print(f"\n   После report: {len(files_info)} файлов")
for file_path, info in files_info.items():
    print(f"     - {file_path}: {info['errors']} ошибок")

# Сканирование файлов
print("\n[3] Сканирование файлов в проекте...")
scanned_files = set(files_info.keys())
scan_count = 0

for py_file in test_root.rglob('*.py'):
    rel = str(py_file.relative_to(test_root)).replace('\\', '/')
    
    if rel in scanned_files:
        print(f"     ⚠ ПРОПУСК (уже есть): {rel}")
        continue
    
    scanned_files.add(rel)
    scan_count += 1
    
    if rel not in files_info:
        files_info[rel] = {'errors': 0}
    
    print(f"     ✅ Добавлен: {rel}")

print(f"\n   Отсканировано: {scan_count}")

# Создание узлов
print("\n[4] Создание узлов...")
nodes = {}
for file_path, info in files_info.items():
    nodes[file_path] = {
        'path': file_path,
        'errors': info['errors']
    }
    print(f"     ✅ Узел: {file_path} ({info['errors']} ошибок)")

print(f"\n{'=' * 70}")
print(f"РЕЗУЛЬТАТ: {len(nodes)} узлов создано")
print(f"{'=' * 70}")

if len(nodes) == 0:
    print("\n❌ ОШИБКА: nodes пуст!")
elif len(nodes) >= 3:
    print("\n✅ УСПЕХ: Достаточно узлов для отображения!")
    print(f"\n   Узлы которые будут отображены в графе:")
    for path in sorted(nodes.keys()):
        print(f"   - {path}")
else:
    print(f"\n⚠ ВНИМАНИЕ: Только {len(nodes)} узла, ожидали больше")

# Очистка
import shutil
shutil.rmtree(test_root, ignore_errors=True)
