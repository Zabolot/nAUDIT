#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Диагностический аудит проекта nAUDIT v2.7
"""
import sys
from pathlib import Path

print("\n" + "="*70)
print("DIAGNOSTIC AUDIT - nAUDIT v2.7 Critical Issues")
print("="*70 + "\n")

# 1. CHECK GPU DETECTOR
print("[1] Checking GPU Detector Module...")
try:
    from n_audit.gui.gpu_detector import GPUDetector
    gpu = GPUDetector()
    result, info = gpu.detect_gpu()
    print(f"    Status: GPU Detected = {result}")
    if info:
        print(f"    GPU Info: {info}")
    else:
        print(f"    GPU Info: None (PyTorch might not be installed or CUDA unavailable)")
except Exception as e:
    print(f"    ERROR: {e}")

# 2. CHECK TREE WIDGET
print("\n[2] Checking Tree Widget Module...")
try:
    from n_audit.gui.tree_widget import ErrorTreeWidget
    print(f"    Status: Module imports successfully")
    
    # Check for populate_from_report method
    if hasattr(ErrorTreeWidget, 'populate_from_report'):
        print(f"    Method populate_from_report: EXISTS ✓")
    else:
        print(f"    Method populate_from_report: MISSING ✗")
    
    # Check for _build_file_tree method
    if hasattr(ErrorTreeWidget, '_build_file_tree'):
        print(f"    Method _build_file_tree: EXISTS ✓")
    else:
        print(f"    Method _build_file_tree: MISSING ✗")
        
except Exception as e:
    print(f"    ERROR: {e}")

# 3. CHECK GRAPH VISUALIZER
print("\n[3] Checking Graph Visualizer Module...")
try:
    from n_audit.gui.graph_visualizer_v2_6 import GraphVisualizerWidget, FileNode
    print(f"    Status: Module imports successfully")
    
    # Check methods
    methods_to_check = [
        'populate_from_report',
        '_calculate_positions',
        '_build_folder_hierarchy',
        '_apply_hierarchical_clustering',
        '_position_hierarchical_level',
        '_position_nodes_in_folder',
    ]
    
    for method_name in methods_to_check:
        if hasattr(GraphVisualizerWidget, method_name):
            print(f"    Method {method_name}: EXISTS ✓")
        else:
            print(f"    Method {method_name}: MISSING ✗")
    
    # Check FileNode dataclass
    print(f"    FileNode class: EXISTS ✓")
    print(f"    FileNode has 'folder' attribute: {hasattr(FileNode(), 'folder')}")
    
except Exception as e:
    print(f"    ERROR: {e}")

# 4. CHECK ERROR VISUALIZATION
print("\n[4] Checking Error Visualization Module...")
try:
    from n_audit.gui.error_visualization import ErrorVisualizationWidget
    print(f"    Status: Module imports successfully")
    
    # Check populate_from_report
    if hasattr(ErrorVisualizationWidget, 'populate_from_report'):
        print(f"    Method populate_from_report: EXISTS ✓")
    else:
        print(f"    Method populate_from_report: MISSING ✗")
        
except Exception as e:
    print(f"    ERROR: {e}")

# 5. CHECK REQUIREMENTS
print("\n[5] Checking requirements.txt...")
try:
    req_file = Path("requirements.txt")
    if req_file.exists():
        content = req_file.read_text()
        
        # Check for key packages
        packages = {
            'torch': 'PyTorch (GPU support)',
            'PyQt6': 'UI Framework',
            'pyvis': 'Graph Visualization',
            'networkx': 'Graph Algorithms',
            'plotly': 'Interactive Plots',
        }
        
        for pkg, desc in packages.items():
            if pkg in content:
                print(f"    {pkg:15} - {desc:25} ✓")
            else:
                print(f"    {pkg:15} - {desc:25} ✗ MISSING")
    else:
        print(f"    requirements.txt: NOT FOUND")
except Exception as e:
    print(f"    ERROR: {e}")

# 6. CHECK MAIN WINDOW
print("\n[6] Checking Main Window Integration...")
try:
    from n_audit.gui.main_window_v4 import MainWindowV4
    print(f"    Status: Module imports successfully")
    
    # Check if tree_widget is created
    if hasattr(MainWindowV4, '__init__'):
        print(f"    MainWindowV4.__init__: EXISTS ✓")
    else:
        print(f"    MainWindowV4.__init__: MISSING ✗")
        
except Exception as e:
    print(f"    ERROR: {e}")

# 7. CHECK AUDIT ENGINE
print("\n[7] Checking Audit Engine...")
try:
    from n_audit.audit_engine import AuditEngine
    print(f"    Status: Module imports successfully")
    
    # Check main methods
    if hasattr(AuditEngine, 'audit'):
        print(f"    Method audit: EXISTS ✓")
    else:
        print(f"    Method audit: MISSING ✗")
        
except Exception as e:
    print(f"    ERROR: {e}")

print("\n" + "="*70)
print("AUDIT COMPLETE")
print("="*70 + "\n")
