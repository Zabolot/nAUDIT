#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pre-Build Integration Test for nAUDIT v2.7
Проверяет что все новые компоненты интегрированы корректно
"""

import sys
from pathlib import Path
import importlib.util

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def check_module_import(module_path, module_name):
    """Проверяет что модуль импортируется без ошибок"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None:
            return False, f"Cannot find module at {module_path}"
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return True, "OK"
    except Exception as e:
        return False, f"Import Error: {str(e)}"

def main():
    print("\n" + "="*70)
    print("  PRE-BUILD INTEGRATION TEST - nAUDIT v2.7")
    print("="*70 + "\n")
    
    tests = [
        # GPU Detector module
        (
            PROJECT_ROOT / "n_audit" / "gui" / "gpu_detector.py",
            "n_audit.gui.gpu_detector",
            "GPU Detector Module"
        ),
        # Graph Visualizer v2.6
        (
            PROJECT_ROOT / "n_audit" / "gui" / "graph_visualizer_v2_6.py",
            "n_audit.gui.graph_visualizer_v2_6",
            "Graph Visualizer v2.6"
        ),
        # Tree Widget
        (
            PROJECT_ROOT / "n_audit" / "gui" / "tree_widget.py",
            "n_audit.gui.tree_widget",
            "Tree Widget"
        ),
    ]
    
    passed = 0
    failed = 0
    
    for module_path, module_name, test_name in tests:
        if not module_path.exists():
            print(f"❌ {test_name}")
            print(f"   File not found: {module_path}\n")
            failed += 1
            continue
        
        success, message = check_module_import(module_path, module_name)
        
        if success:
            print(f"✅ {test_name}")
            print(f"   {message}\n")
            passed += 1
        else:
            print(f"❌ {test_name}")
            print(f"   {message}\n")
            failed += 1
    
    # Check requirements
    print("\nChecking requirements.txt for psutil...")
    req_file = PROJECT_ROOT / "requirements.txt"
    if req_file.exists():
        content = req_file.read_text()
        if "psutil" in content:
            print("✅ psutil found in requirements.txt\n")
            passed += 1
        else:
            print("❌ psutil NOT found in requirements.txt\n")
            failed += 1
    
    # Summary
    print("="*70)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*70 + "\n")
    
    if failed == 0:
        print("🟢 ALL INTEGRATION TESTS PASSED - READY TO BUILD!\n")
        return 0
    else:
        print("🔴 SOME TESTS FAILED - FIX ISSUES BEFORE BUILD!\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
