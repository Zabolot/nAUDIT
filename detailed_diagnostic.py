#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Детальная диагностика отображения ошибок и графов
"""
import sys
from pathlib import Path

print("\n" + "="*70)
print("DETAILED DIAGNOSTIC - Error Display & Graph Rendering")
print("="*70 + "\n")

# Test 1: Create a mock report and check tree rendering
print("[TEST 1] Testing Tree Widget Error Display...")
try:
    from n_audit.gui.tree_widget import ErrorTreeWidget, CodeIssueInfo
    from PyQt6.QtWidgets import QApplication
    
    # Create QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create mock report with errors
    class MockReport:
        code_issues = [
            {'file': 'src/main.py', 'line': 10, 'column': 5, 'code': 'E001', 'message': 'Error 1', 'severity': 'HIGH'},
            {'file': 'src/utils.py', 'line': 20, 'column': 10, 'code': 'E002', 'message': 'Error 2', 'severity': 'MEDIUM'},
        ]
        security_issues = [
            {'file': 'src/main.py', 'line': 15, 'column': 2, 'code': 'SEC001', 'message': 'Security Issue', 'severity': 'CRITICAL'},
        ]
    
    widget = ErrorTreeWidget()
    report = MockReport()
    widget.populate_from_report(report, project_root=".")
    
    # Check if tree has items
    all_issues = widget.all_issues
    files_with_issues = widget.files_with_issues
    
    print(f"    All Issues: {len(all_issues)} (expected 3)")
    print(f"    Files with Issues: {len(files_with_issues)} (expected 2)")
    
    if len(all_issues) == 3 and len(files_with_issues) == 2:
        print(f"    Status: PASS ✓")
    else:
        print(f"    Status: FAIL ✗")
        print(f"    Details:")
        for file_path, issues in files_with_issues.items():
            print(f"      {file_path}: {len(issues)} issues")
            
except Exception as e:
    print(f"    ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Check graph node folder assignment
print("\n[TEST 2] Testing Graph Node Folder Assignment...")
try:
    from n_audit.gui.graph_visualizer_v2_6 import FileNode, GraphVisualizerWidget
    
    # Create test nodes
    node1 = FileNode(
        file_path='src/main.py',
        lines_of_code=100,
        errors_count=2,
        max_severity='HIGH',
        folder='src/'
    )
    
    node2 = FileNode(
        file_path='tests/test_main.py',
        lines_of_code=50,
        errors_count=1,
        max_severity='LOW',
        folder='tests/'
    )
    
    print(f"    Node 1: {node1.file_path} -> folder={node1.folder}")
    print(f"    Node 2: {node2.file_path} -> folder={node2.folder}")
    
    if node1.folder == 'src/' and node2.folder == 'tests/':
        print(f"    Status: PASS ✓")
    else:
        print(f"    Status: FAIL ✗")
        
except Exception as e:
    print(f"    ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Check hierarchy building
print("\n[TEST 3] Testing Hierarchical Clustering...")
try:
    from n_audit.gui.graph_visualizer_v2_6 import GraphVisualizerWidget
    import math
    from collections import defaultdict
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    visualizer = GraphVisualizerWidget()
    
    # Manually set up nodes
    nodes = {
        'src/main.py': type('Node', (), {'folder': 'src/'}),
        'src/utils.py': type('Node', (), {'folder': 'src/'}),
        'tests/test_main.py': type('Node', (), {'folder': 'tests/'}),
        'tests/test_utils.py': type('Node', (), {'folder': 'tests/'}),
    }
    visualizer.nodes = nodes
    
    # Build hierarchy
    hierarchy = visualizer._build_folder_hierarchy(list(nodes.keys()))
    
    print(f"    Hierarchy structure:")
    for key, data in hierarchy.items():
        print(f"      {key}: size={data['size']}")
    
    # Check if hierarchy has folders
    if len(hierarchy) >= 2:
        print(f"    Status: PASS ✓ (Found {len(hierarchy)} top-level folders)")
    else:
        print(f"    Status: FAIL ✗ (Expected at least 2 folders)")
        
except Exception as e:
    print(f"    ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Check position calculation
print("\n[TEST 4] Testing Position Calculation for Hierarchical Layout...")
try:
    from n_audit.gui.graph_visualizer_v2_6 import GraphVisualizerWidget
    import networkx as nx
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    visualizer = GraphVisualizerWidget()
    
    # Create simple graph
    G = nx.Graph()
    G.add_nodes_from(['src/main.py', 'src/utils.py', 'tests/test_main.py', 'tests/test_utils.py'])
    
    # Set up nodes with folder info
    nodes_dict = {
        'src/main.py': type('Node', (), {'folder': 'src/'}),
        'src/utils.py': type('Node', (), {'folder': 'src/'}),
        'tests/test_main.py': type('Node', (), {'folder': 'tests/'}),
        'tests/test_utils.py': type('Node', (), {'folder': 'tests/'}),
    }
    visualizer.nodes = nodes_dict
    visualizer.graph = G
    visualizer.scale_factor = 1.0
    
    # Try to calculate positions
    filtered_nodes = list(nodes_dict.keys())
    positions = visualizer._calculate_positions(G, filtered_nodes)
    
    print(f"    Calculated positions for {len(positions)} nodes")
    
    if len(positions) == 4:
        print(f"    Position samples:")
        for node, (x, y) in list(positions.items())[:2]:
            print(f"      {node}: ({x:.1f}, {y:.1f})")
        print(f"    Status: PASS ✓")
    else:
        print(f"    Status: FAIL ✗ (Expected 4 positions, got {len(positions)})")
        
except Exception as e:
    print(f"    ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("DETAILED DIAGNOSTIC COMPLETE")
print("="*70 + "\n")
