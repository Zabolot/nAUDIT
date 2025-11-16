#!/usr/bin/env python3
import sys
from pathlib import Path

# Ensure project path is importable
sys.path.insert(0, str(Path(__file__).parent))

from n_audit.gui.tree_widget import ErrorTreeWidget, CodeIssueInfo
from PyQt6.QtWidgets import QApplication

class MockIssueObj:
    def __init__(self, file_path, line, code, message, severity):
        self.file_path = file_path
        self.line_number = line
        self.column = 1
        self.code = code
        self.message = message
        self.severity = severity
        self.tool = 'mock'

class MockMetrics:
    def __init__(self):
        self.code_issues = [
            MockIssueObj('src/main.py', 10, 'E001', 'Error in main', type('S', (), {'name':'HIGH'})),
            MockIssueObj('src/utils.py', 20, 'E002', 'Error in utils', type('S', (), {'name':'LOW'})),
        ]
        self.security_issues = [
            MockIssueObj('src/main.py', 15, 'SEC001', 'Security problem', type('S', (), {'name':'CRITICAL'})),
        ]

class MockReport:
    def __init__(self):
        self.metrics = MockMetrics()

if __name__ == '__main__':
    app = QApplication.instance() or QApplication(sys.argv)
    widget = ErrorTreeWidget()
    report = MockReport()
    widget.populate_from_report(report, project_root='.')
    print('All issues:', len(widget.all_issues))
    print('Files with issues:', len(widget.files_with_issues))
    print('Files collected:', len(widget.all_project_files))
    for k in widget.files_with_issues:
        print(' -', k, '->', len(widget.files_with_issues[k]))
    sys.exit(0)
