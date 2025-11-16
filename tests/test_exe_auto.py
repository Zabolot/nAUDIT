#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated exe testing - creates test project and runs through audit
"""

import sys
import tempfile
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# Create test project in temp directory
test_root = Path(tempfile.gettempdir()) / "naudit_automated_test"

print("[INFO] Creating test project for exe testing...")

if test_root.exists():
    shutil.rmtree(test_root)

test_root.mkdir(parents=True)

# Create test files with intentional errors
files = {
    "main.py": """
import sys
import math
import unused_module

def divide(a, b):
    return a / b  # Potential division by zero

def main():
    result = divide(10, 0)  # Will cause error
    print(f'Result: {result}')
    
if __name__ == '__main__':
    main()
""",
    "utils.py": """
def helper():
    x = 10
    y = 0
    return x / y  # Another division by zero

class MyClass:
    def __init__(self):
        self.value = None
    
    def process(self):
        return self.value.upper()  # Potential attribute error
""",
    "config.py": """
import os
import sys

DEBUG = True
VERSION = "1.0"

# Hard-coded password
PASSWORD = "admin123"  # Security issue

def load_config():
    return {
        'key': 'value',
        'secret': 'leaked_secret'  # Security issue
    }
""",
}

for file_name, content in files.items():
    (test_root / file_name).write_text(content.strip())

print(f"[OK] Test project created: {test_root}")
print(f"[OK] Files: {', '.join(files.keys())}")
print()

# Now we would normally open the exe in GUI mode and:
# 1. Open project
# 2. Run audit
# 3. Check graph
# But since we can't automate GUI, we'll just print instructions

print("="*70)
print("AUTOMATED TEST SETUP COMPLETE")
print("="*70)
print()
print("Test project location:")
print(f"  {test_root}")
print()
print("To manually test the exe:")
print()
print("1. Start exe:")
print(f"   & .\\dist\\nAUDIT.exe")
print()
print("2. Open project:")
print(f"   File -> Open Project -> {test_root}")
print()
print("3. Run audit:")
print(f"   Start -> Run Audit (or similar)")
print()
print("4. Check graph display:")
print(f"   - Should show 3 files (main.py, utils.py, config.py)")
print(f"   - Files should be colored")
print(f"   - Errors should be counted")
print()
print("5. Look for [GraphVisualizer] logs:")
print(f"   - Should show node creation")
print(f"   - Should show graph rendering")
print()
print("Common test cases:")
print("  [OK] Graph displays without white page")
print("  [OK] Nodes created for all files")
print("  [OK] Colors assigned by folder")
print("  [OK] Error counts visible")
print("  [OK] Can switch between Plotly/PyVis")
print("  [OK] Click on nodes selects in tree")
print("  [OK] Click on tree highlights on graph")
print()
