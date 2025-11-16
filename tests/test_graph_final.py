#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final test of graph visualization in real exe.
Create test project, run audit, verify graph nodes created.
ASCII-only output for Windows PowerShell compatibility.
"""

import sys
import os
import tempfile
import shutil
import subprocess
from pathlib import Path
import time

def print_header(text):
    print(f"\n{'='*60}")
    print(f"[TEST] {text}")
    print(f"{'='*60}")

def print_ok(text):
    print(f"[OK] {text}")

def print_error(text):
    print(f"[ERROR] {text}")

def print_info(text):
    print(f"[INFO] {text}")

def create_test_project():
    """Create a simple test project with Python files"""
    print_info("Creating test project...")
    
    test_root = Path(tempfile.gettempdir()) / "naudit_graph_test"
    
    # Clean if exists
    if test_root.exists():
        shutil.rmtree(test_root)
    
    test_root.mkdir(parents=True)
    
    # Create structure
    (test_root / "src").mkdir()
    (test_root / "src" / "main").mkdir()
    (test_root / "src" / "utils").mkdir()
    (test_root / "tests").mkdir()
    
    # Create test files
    files = {
        "src/__init__.py": "# Init",
        "src/main/__init__.py": "# Main package",
        "src/main/app.py": """import sys
from src.utils.helpers import helper_func

def main():
    result = helper_func()
    print(f"Result: {result}")
    return result

if __name__ == '__main__':
    main()
""",
        "src/utils/__init__.py": "# Utils",
        "src/utils/helpers.py": """def helper_func():
    '''Helper function with bug'''
    x = 10
    y = 0
    return x / y  # This will cause ZeroDivisionError

def another_helper():
    return helper_func()
""",
        "tests/__init__.py": "# Tests",
        "tests/test_app.py": """import unittest
from src.main.app import main

class TestApp(unittest.TestCase):
    def test_main(self):
        # This test should fail
        result = main()
        self.assertEqual(result, 42)

if __name__ == '__main__':
    unittest.main()
""",
    }
    
    for file_path, content in files.items():
        full_path = test_root / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding='utf-8')
    
    print_ok(f"Test project created at: {test_root}")
    print_info(f"  - 3 packages (src, src/main, src/utils)")
    print_info(f"  - 5 Python files")
    print_info(f"  - Intentional bugs for testing")
    
    return str(test_root)

def test_audit_imports():
    """Test if we can import nAUDIT components"""
    print_header("Testing nAUDIT Imports")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        
        from n_audit.core.engine import AuditEngine
        from n_audit.gui.graph_visualizer import GraphVisualizerWidget, FileNode
        
        print_ok("AuditEngine imported")
        print_ok("GraphVisualizerWidget imported")
        print_ok("FileNode imported")
        
        return True
    except Exception as e:
        print_error(f"Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_audit_run(project_root):
    """Run audit on test project"""
    print_header("Running Audit on Test Project")
    
    try:
        from n_audit.core.engine import AuditEngine
        
        print_info(f"Project root: {project_root}")
        
        engine = AuditEngine(project_root)
        print_ok("AuditEngine created")
        
        report = engine.run_audit()
        print_ok("Audit completed")
        
        # Check results
        code_issues = len(report.code_issues) if hasattr(report, 'code_issues') else 0
        security_issues = len(report.security_issues) if hasattr(report, 'security_issues') else 0
        
        print_info(f"  Code issues found: {code_issues}")
        print_info(f"  Security issues found: {security_issues}")
        print_info(f"  Total issues: {code_issues + security_issues}")
        
        if code_issues + security_issues == 0:
            print_error("No issues found - might be wrong")
            return False, report
        
        return True, report
        
    except Exception as e:
        print_error(f"Audit run failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_graph_population(report, project_root):
    """Test if graph can load report data"""
    print_header("Testing Graph Population")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from n_audit.gui.graph_visualizer import GraphVisualizerWidget
        
        # Create QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create widget
        widget = GraphVisualizerWidget()
        print_ok("GraphVisualizerWidget created")
        
        # Populate from report
        widget.populate_from_report(report, project_root)
        print_ok("populate_from_report() called")
        
        # Check nodes
        node_count = len(widget.nodes)
        edge_count = len(widget.edges)
        
        print_info(f"  Nodes created: {node_count}")
        print_info(f"  Edges created: {edge_count}")
        
        if node_count == 0:
            print_error("No nodes created!")
            return False
        
        print_ok(f"Graph has {node_count} nodes")
        return True
        
    except Exception as e:
        print_error(f"Graph population failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print_header("Final Graph Visualization Test")
    print_info("This test will verify the graph visualization system")
    print_info("Python version: " + sys.version.split()[0])
    print_info("Platform: " + sys.platform)
    
    results = []
    
    # Test 1: Imports
    results.append(("Imports", test_audit_imports()))
    
    if not results[-1][1]:
        print_error("Cannot continue without imports")
        return 1
    
    # Test 2: Create test project
    test_root = create_test_project()
    
    # Test 3: Run audit
    success, report = test_audit_run(test_root)
    results.append(("Audit Run", success))
    
    if not success or report is None:
        print_error("Cannot continue without audit report")
        return 1
    
    # Test 4: Populate graph
    success = test_graph_population(report, test_root)
    results.append(("Graph Population", success))
    
    # Summary
    print_header("Test Summary")
    all_passed = True
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {name}")
        if not result:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print_ok("All tests PASSED")
        print_info("Graph visualization is working correctly")
        print_info("The exe should display graphs when auditing projects")
        print_info("\nIf exe still shows blank page:")
        print_info("1. Run actual exe and load a project")
        print_info("2. Start audit")
        print_info("3. Check console for [GraphVisualizer] log messages")
        print_info("4. Verify populate_from_report() is being called")
        return 0
    else:
        print_error("Some tests FAILED")
        print_error("Graph visualization needs more investigation")
        return 1

if __name__ == '__main__':
    sys.exit(main())
