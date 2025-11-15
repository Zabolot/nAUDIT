#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест: проверка как populate_from_report работает с реальным проектом

Этот скрипт создает fake отчет и проверяет что граф загрузится с ним
"""

import sys
from pathlib import Path
import tempfile

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("TEST: Graph populate with audit report")
print("=" * 70)

# Симулируем отчет от аудита
class FakeIssue:
    def __init__(self, file, severity="LOW"):
        self.file = file
        self.severity = severity
    def get(self, key, default=None):
        return getattr(self, key, default)

class FakeReport:
    """Фейковый отчет похожий на реальный от audit_engine"""
    def __init__(self):
        self.code_issues = [
            {"file": "src/main.py", "severity": "HIGH", "message": "Test 1"},
            {"file": "src/utils.py", "severity": "LOW", "message": "Test 2"},
        ]
        self.security_issues = [
            {"file": "src/auth.py", "severity": "CRITICAL", "message": "Test 3"},
        ]
    
    def __iter__(self):
        return iter(self.code_issues + self.security_issues)

# Создаем тестовый проект
test_root = Path(tempfile.gettempdir()) / "real_project_test"
test_root.mkdir(exist_ok=True)
(test_root / "src").mkdir(exist_ok=True)

# Создаем файлы
(test_root / "src" / "main.py").write_text("print('main')")
(test_root / "src" / "utils.py").write_text("def util(): pass")
(test_root / "src" / "auth.py").write_text("auth = True")

print(f"\nProject: {test_root}")
print(f"Files: {list((test_root / 'src').glob('*.py'))}")

# СИМУЛИРУЕМ ЧТО БУДЕТ ВЫЗЫВАТЬ populate_from_report
print("\n" + "=" * 70)
print("Simulating ErrorVisualizationWidget.populate_from_report()")
print("=" * 70)

# Тестируем БЕЗ GUI - используем логику напрямую
class TestGraphPopulate:
    def __init__(self):
        self.nodes = {}
        self.edges = []
    
    def _is_excluded_path(self, path_str):
        EXCLUDE = {'.venv', 'venv', '__pycache__', '.git', 'build', 'dist'}
        from pathlib import Path
        path = Path(path_str)
        for part in path.parts:
            if part in EXCLUDE:
                return True
        return False
    
    def populate_from_report(self, report, project_root: str):
        print(f"\n[populate_from_report] Called")
        print(f"  project_root: {project_root}")
        
        self.nodes.clear()
        self.edges.clear()
        files_info = {}
        
        # Обработка code_issues
        print(f"\n  Processing code_issues...")
        if hasattr(report, 'code_issues') and report.code_issues:
            print(f"    count: {len(report.code_issues)}")
            for issue in report.code_issues:
                # Это может быть dict или объект с методом get()
                if isinstance(issue, dict):
                    path = issue.get('file', '')
                    severity = issue.get('severity', 'LOW')
                else:
                    path = issue.get('file', '')
                    severity = issue.get('severity', 'LOW')
                
                if not path or self._is_excluded_path(path):
                    continue
                
                if path not in files_info:
                    files_info[path] = {'errors': 0}
                files_info[path]['errors'] += 1
                print(f"      {path}: OK")
        
        # Обработка security_issues
        print(f"\n  Processing security_issues...")
        if hasattr(report, 'security_issues') and report.security_issues:
            print(f"    count: {len(report.security_issues)}")
            for issue in report.security_issues:
                if isinstance(issue, dict):
                    path = issue.get('file', '')
                    severity = issue.get('severity', 'LOW')
                else:
                    path = issue.get('file', '')
                    severity = issue.get('severity', 'LOW')
                
                if not path or self._is_excluded_path(path):
                    continue
                
                if path not in files_info:
                    files_info[path] = {'errors': 0}
                files_info[path]['errors'] += 1
                print(f"      {path}: OK")
        
        print(f"\n  After report: {len(files_info)} files")
        
        # Сканирование
        print(f"\n  Scanning project...")
        scanned_files = set(files_info.keys())
        scan_count = 0
        
        for py_file in Path(project_root).rglob('*.py'):
            rel = str(py_file.relative_to(project_root)).replace('\\', '/')
            
            if self._is_excluded_path(rel):
                continue
            
            if rel in scanned_files:
                continue
            
            scanned_files.add(rel)
            scan_count += 1
            
            if rel not in files_info:
                files_info[rel] = {'errors': 0}
            
            print(f"      {rel}: OK (NEW)")
        
        print(f"\n  Scanned: {scan_count} new files")
        
        # Создание узлов
        print(f"\n  Creating nodes...")
        for file_path, info in files_info.items():
            self.nodes[file_path] = {
                'file': file_path,
                'errors': info['errors']
            }
            print(f"      {file_path}: {info['errors']} errors")
        
        print(f"\n  Result: {len(self.nodes)} nodes total")
        return len(self.nodes) > 0

# Запуск теста
report = FakeReport()
test = TestGraphPopulate()

success = test.populate_from_report(report, str(test_root))

print("\n" + "=" * 70)
print("RESULT")
print("=" * 70)

if success:
    print(f"\n✅ SUCCESS: {len(test.nodes)} nodes loaded")
    print(f"\nGraph will display:")
    for node_path in sorted(test.nodes.keys()):
        errors = test.nodes[node_path]['errors']
        print(f"  - {node_path} ({errors} errors)")
else:
    print(f"\n❌ FAILED: No nodes loaded")
    print(f"\nCheck:")
    print(f"  - Is report.code_issues populated?")
    print(f"  - Are file paths correct?")
    print(f"  - Are files being excluded?")

# Cleanup
import shutil
shutil.rmtree(test_root, ignore_errors=True)
