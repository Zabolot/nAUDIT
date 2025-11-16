#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт запуска приложения с отладкой графа

Показывает все логи при загрузке проекта и отображении графа
"""

import sys
import os
from pathlib import Path

# Установить переменные окружения для отладки
os.environ['QT_DEBUG_PLUGINS'] = '1'
os.environ['PYTHONUNBUFFERED'] = '1'

print("=" * 80)
print("[START] nAUDIT WITH GRAPH DEBUG")
print("=" * 80)

print("\n[DIAGNOSTICS] Environment check...")
print(f"  Python: {sys.version}")
print(f"  Platform: {sys.platform}")
print(f"  Working dir: {os.getcwd()}")

try:
    from PyQt6.QtWidgets import QApplication
    print("  OK - PyQt6 loaded")
except Exception as e:
    print(f"  ERROR PyQt6: {e}")
    sys.exit(1)

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    print("  OK - QWebEngineView loaded")
except Exception as e:
    print(f"  ERROR QWebEngineView: {e}")
    sys.exit(1)

try:
    from PyQt6.QtWebChannel import QWebChannel
    print("  OK - QWebChannel loaded")
except Exception as e:
    print(f"  ERROR QWebChannel: {e}")
    sys.exit(1)

try:
    from n_audit.gui.main_window_v4 import MainWindow
    print("  OK - MainWindow loaded")
except Exception as e:
    print(f"  ERROR MainWindow: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[INIT] Starting Qt application...")
app = QApplication(sys.argv)

print("\n[CREATE] Creating main window...")
try:
    window = MainWindow()
    print("  OK - Window created")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[SHOW] Showing window...")
window.showMaximized()

print("\n" + "=" * 80)
print("[INSTRUCTIONS] What to do:")
print("=" * 80)
print("""
1. Select project folder (File - Open Project)
2. Click "Start Audit"
3. Open "Errors" tab
4. Click "Graph" button
5. Check: you should see graph with file nodes

IF GRAPH IS EMPTY:
- Check console logs for "[GraphVisualizer]" messages
- Check that files are shown in tree on left

IF YOU SEE "[GraphVisualizer] No nodes to render":
- populate_from_report didn't send data
- Check that tree has files with errors
""")

print("\n[RUN] Starting event loop...")
sys.exit(app.exec())
