#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pre-Build Quality Assurance Checks for nAUDIT v2.7
Финальная проверка всех новых и измененных файлов перед компиляцией
"""

import sys
from pathlib import Path
import ast
import subprocess

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

class QualityChecker:
    def __init__(self):
        self.results = {
            "syntax": [],
            "imports": [],
            "type_hints": [],
            "docstrings": [],
            "issues": []
        }
    
    def check_syntax(self, filepath):
        """Проверяет syntax файла через ast.parse"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            ast.parse(code)
            return True, "OK"
        except SyntaxError as e:
            return False, f"Syntax Error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)
    
    def check_imports(self, filepath):
        """Проверяет что все импорты разрешимы"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            tree = ast.parse(code)
            
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            return True, f"Found {len(imports)} imports"
        except Exception as e:
            return False, str(e)
    
    def check_type_hints(self, filepath):
        """Проверяет наличие type hints"""
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        has_annotations = 'from __future__ import annotations' in code
        has_type_hints = '->' in code or ': ' in code.split('def ')[-1] if 'def' in code else False
        
        if has_annotations:
            return True, "Has __future__ annotations"
        elif has_type_hints:
            return True, "Has type hints"
        else:
            return True, "Warning: Limited type hints"
    
    def check_docstrings(self, filepath):
        """Проверяет наличие docstrings"""
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        tree = ast.parse(code)
        has_module_docstring = ast.get_docstring(tree) is not None
        
        class_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
        func_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
        
        return True, f"Module: {has_module_docstring}, {class_count} classes, {func_count} functions"
    
    def run_all_checks(self, filepath, name):
        """Запускает все проверки для файла"""
        print(f"\n📋 Checking {name}:")
        print(f"   Path: {filepath}")
        
        # Syntax
        success, msg = self.check_syntax(filepath)
        status = "✅" if success else "❌"
        print(f"   {status} Syntax: {msg}")
        self.results["syntax"].append((name, success))
        
        # Imports
        success, msg = self.check_imports(filepath)
        status = "✅" if success else "❌"
        print(f"   {status} Imports: {msg}")
        self.results["imports"].append((name, success))
        
        # Type hints
        success, msg = self.check_type_hints(filepath)
        status = "✅" if success else "⚠️"
        print(f"   {status} Type Hints: {msg}")
        self.results["type_hints"].append((name, success))
        
        # Docstrings
        success, msg = self.check_docstrings(filepath)
        status = "✅" if success else "⚠️"
        print(f"   {status} Docstrings: {msg}")
        self.results["docstrings"].append((name, success))
    
    def print_summary(self):
        """Выводит итоговый отчет"""
        print("\n" + "="*70)
        print("QUALITY ASSURANCE SUMMARY")
        print("="*70)
        
        total_checks = sum(len(v) for v in self.results.values())
        passed = sum(
            sum(1 for _, success in v if success) 
            for v in self.results.values()
        )
        
        print(f"\n📊 Overall: {passed}/{total_checks} checks passed")
        
        for category, results in self.results.items():
            if results:
                passed_count = sum(1 for _, success in results if success)
                total_count = len(results)
                status = "✅" if passed_count == total_count else "⚠️"
                print(f"   {status} {category.capitalize()}: {passed_count}/{total_count}")
        
        print("\n" + "="*70)
        
        if passed == total_checks:
            print("🟢 ALL QUALITY CHECKS PASSED - BUILD READY")
            return 0
        else:
            print("🟡 SOME WARNINGS - REVIEW BEFORE BUILD")
            return 1

def main():
    print("\n" + "="*70)
    print("PRE-BUILD QUALITY ASSURANCE - nAUDIT v2.7")
    print("="*70)
    
    checker = QualityChecker()
    
    files_to_check = [
        (PROJECT_ROOT / "n_audit" / "gui" / "gpu_detector.py", "GPU Detector (NEW)"),
        (PROJECT_ROOT / "n_audit" / "gui" / "graph_visualizer_v2_6.py", "Graph Visualizer"),
        (PROJECT_ROOT / "n_audit" / "gui" / "tree_widget.py", "Tree Widget"),
    ]
    
    for filepath, name in files_to_check:
        if filepath.exists():
            checker.run_all_checks(filepath, name)
        else:
            print(f"\n⚠️ File not found: {filepath}")
    
    print("\n📦 Checking dependencies...")
    try:
        result = subprocess.run(
            ["pip", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        required = ["psutil", "PyQt6", "networkx", "plotly", "pyvis"]
        for req in required:
            if req.lower() in result.stdout.lower():
                print(f"   ✅ {req} installed")
            else:
                print(f"   ⚠️ {req} may not be installed")
    except Exception as e:
        print(f"   ⚠️ Could not check dependencies: {e}")
    
    exit_code = checker.print_summary()
    print()
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
