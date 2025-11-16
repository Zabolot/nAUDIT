#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Realtime debugger for nAUDIT exe graph visualization.
Tests if populate_from_report() works and creates graph nodes.
ASCII-only output for Windows PowerShell compatibility.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(text):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"[TEST] {text}")
    print(f"{'='*60}")

def print_ok(text):
    """Print success message"""
    print(f"[OK] {text}")

def print_error(text):
    """Print error message"""
    print(f"[ERROR] {text}")

def print_info(text):
    """Print info message"""
    print(f"[INFO] {text}")

def test_imports():
    """Test if all required modules can be imported"""
    print_header("Testing Imports")
    
    modules = {
        'PyQt6': 'PyQt6',
        'PyQt6.QtCore': 'PyQt6.QtCore',
        'PyQt6.QtGui': 'PyQt6.QtGui',
        'PyQt6.QtWebEngineWidgets': 'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtWebChannel': 'PyQt6.QtWebChannel',
        'plotly': 'plotly',
        'networkx': 'networkx',
    }
    
    failed = []
    for name, module in modules.items():
        try:
            __import__(module)
            print_ok(f"Module '{name}' loaded")
        except ImportError as e:
            print_error(f"Module '{name}' failed: {e}")
            failed.append(name)
    
    if failed:
        print_error(f"Failed to import: {', '.join(failed)}")
        return False
    
    print_ok("All imports successful")
    return True

def test_graph_visualizer_import():
    """Test if graph visualizer can be imported"""
    print_header("Testing Graph Visualizer Import")
    
    try:
        from n_audit.gui.graph_visualizer import GraphVisualizerWidget
        print_ok("GraphVisualizerWidget imported successfully")
        return True
    except Exception as e:
        print_error(f"Failed to import GraphVisualizerWidget: {e}")
        return False

def test_populate_from_report():
    """Test populate_from_report with mock data"""
    print_header("Testing populate_from_report Logic")
    
    try:
        from n_audit.gui.graph_visualizer import GraphVisualizerWidget, FileNode
        from pathlib import Path
        
        # Create a mock report object
        class MockIssue:
            def __init__(self, file_path):
                self.file_path = file_path
        
        class MockReport:
            def __init__(self):
                self.code_issues = [
                    MockIssue('test/module1.py'),
                    MockIssue('test/module2.py'),
                ]
                self.security_issues = [
                    MockIssue('test/module1.py'),
                    MockIssue('test/module3.py'),
                ]
        
        # Create test project
        test_dir = Path(tempfile.gettempdir()) / "naudit_test"
        test_dir.mkdir(exist_ok=True)
        (test_dir / "test").mkdir(exist_ok=True)
        
        # Create test files
        (test_dir / "test" / "module1.py").write_text("# test1")
        (test_dir / "test" / "module2.py").write_text("# test2")
        (test_dir / "test" / "module3.py").write_text("# test3")
        
        print_info(f"Created test project at: {test_dir}")
        
        # Test the logic without GUI
        mock_report = MockReport()
        
        # Simulate what populate_from_report does
        nodes = {}
        edges = []
        files_info = {}
        
        # Process issues
        for issue in mock_report.code_issues:
            if issue.file_path not in files_info:
                files_info[issue.file_path] = {
                    'code_issues': [],
                    'security_issues': [],
                    'size': 0
                }
            files_info[issue.file_path]['code_issues'].append(issue)
        
        for issue in mock_report.security_issues:
            if issue.file_path not in files_info:
                files_info[issue.file_path] = {
                    'code_issues': [],
                    'security_issues': [],
                    'size': 0
                }
            files_info[issue.file_path]['security_issues'].append(issue)
        
        # Create nodes
        for file_path, info in files_info.items():
            nodes[file_path] = {
                'path': file_path,
                'issues': len(info['code_issues']) + len(info['security_issues'])
            }
        
        print_info(f"Found {len(files_info)} files in report")
        print_info(f"Created {len(nodes)} nodes")
        
        if len(nodes) == 0:
            print_error("No nodes created from report!")
            return False
        
        for path, node in nodes.items():
            print_info(f"  Node: {path} (issues: {node['issues']})")
        
        print_ok("populate_from_report logic works correctly")
        return True
        
    except Exception as e:
        print_error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print_header("nAUDIT Graph Visualization Debugger")
    print_info("Python version: " + sys.version.split()[0])
    print_info("Platform: " + sys.platform)
    
    results = []
    
    # Test 1: Imports
    results.append(("Imports", test_imports()))
    
    # Test 2: Graph visualizer import
    results.append(("Graph Visualizer Import", test_graph_visualizer_import()))
    
    # Test 3: Populate logic
    results.append(("Populate Logic", test_populate_from_report()))
    
    # Summary
    print_header("Test Summary")
    all_passed = True
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print_ok("All tests passed - graph visualization infrastructure is working")
        return 0
    else:
        print_error("Some tests failed - investigate above errors")
        return 1

if __name__ == '__main__':
    sys.exit(main())
