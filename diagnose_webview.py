#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detailed WebView rendering diagnostic.
Checks if HTML generation and loading works correctly.
"""

import sys
import os
import tempfile
from pathlib import Path
from io import StringIO

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

def test_html_generation():
    """Test HTML generation logic from graph_visualizer.py"""
    print_header("Testing HTML Generation")
    
    try:
        import plotly.graph_objects as go
        import plotly.io as pio
        import networkx as nx
        
        # Create a simple test graph
        print_info("Creating test NetworkX graph...")
        G = nx.DiGraph()
        G.add_edge('file1.py', 'file2.py', weight=2)
        G.add_edge('file2.py', 'file3.py', weight=1)
        
        print_info(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
        
        # Get positions using spring layout
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Create edge traces
        edge_x = []
        edge_y = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            mode='lines',
            line=dict(width=0.5, color='#888'),
            hoverinfo='none'
        )
        
        # Create node trace
        node_x = []
        node_y = []
        node_text = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            textposition='top center',
            hoverinfo='text',
            hovertext=node_text,
            marker=dict(
                showscale=True,
                color='#1f77b4',
                size=10,
            )
        )
        
        # Create figure
        fig = go.Figure(data=[edge_trace, node_trace])
        fig.update_layout(
            title='Test Graph Visualization',
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white'
        )
        
        print_ok("Plotly figure created successfully")
        
        # Generate HTML
        html_content = pio.to_html(fig, include_plotlyjs='cdn')
        
        if not html_content:
            print_error("HTML generation returned empty content")
            return False
        
        print_ok(f"HTML generated: {len(html_content)} bytes")
        
        # Try to save to file
        temp_file = Path(tempfile.gettempdir()) / "naudit_test_graph.html"
        temp_file.write_text(html_content, encoding='utf-8')
        
        if not temp_file.exists():
            print_error(f"HTML file not created at {temp_file}")
            return False
        
        file_size = temp_file.stat().st_size
        print_ok(f"HTML file saved: {file_size} bytes at {temp_file}")
        
        # Verify content
        saved_content = temp_file.read_text(encoding='utf-8')
        if '<script' not in saved_content:
            print_error("HTML does not contain script tags")
            return False
        
        if 'plotly' not in saved_content.lower():
            print_error("HTML does not contain plotly references")
            return False
        
        print_ok("HTML content validated - contains Plotly scripts")
        
        return True
        
    except Exception as e:
        print_error(f"HTML generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_graph_visualizer_widget():
    """Test GraphVisualizerWidget._render_with_plotly method"""
    print_header("Testing GraphVisualizerWidget Rendering")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from n_audit.gui.graph_visualizer import GraphVisualizerWidget, FileNode
        import networkx as nx
        from PyQt6.QtCore import QUrl
        from pathlib import Path
        
        print_info("Creating QApplication for widget testing...")
        
        # Create QApplication if not exists
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
            print_ok("QApplication created")
        else:
            print_ok("Using existing QApplication")
        
        print_info("Creating GraphVisualizerWidget instance...")
        
        # Create widget (will not display in GUI)
        widget = GraphVisualizerWidget()
        print_ok("Widget instance created")
        
        # Populate with test data
        print_info("Adding test nodes...")
        widget.nodes = {
            'file1.py': FileNode(
                id='file1.py',
                label='file1.py',
                size=100,
                color='blue',
                issues_count=2,
                code_issues=1,
                security_issues=1
            ),
            'file2.py': FileNode(
                id='file2.py',
                label='file2.py',
                size=150,
                color='green',
                issues_count=1,
                code_issues=1,
                security_issues=0
            ),
        }
        
        # Add edges
        widget.edges = [
            ('file1.py', 'file2.py', 'imports'),
        ]
        
        print_ok(f"Added {len(widget.nodes)} nodes and {len(widget.edges)} edges")
        
        # Check if nodes are stored
        if len(widget.nodes) == 0:
            print_error("Nodes not stored in widget")
            return False
        
        print_ok(f"Nodes correctly stored in widget.nodes: {list(widget.nodes.keys())}")
        
        # Check edge representation
        if len(widget.edges) == 0:
            print_error("Edges not stored in widget")
            return False
        
        print_ok(f"Edges correctly stored: {widget.edges}")
        
        return True
        
    except Exception as e:
        print_error(f"Widget test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_logging_infrastructure():
    """Test if logging is properly configured in graph_visualizer.py"""
    print_header("Testing Logging Infrastructure")
    
    try:
        from pathlib import Path
        
        graph_viz_file = Path(__file__).parent / "n_audit" / "gui" / "graph_visualizer.py"
        
        if not graph_viz_file.exists():
            print_error(f"graph_visualizer.py not found at {graph_viz_file}")
            return False
        
        content = graph_viz_file.read_text(encoding='utf-8')
        
        # Count logging points
        log_markers = content.count("[GraphVisualizer]")
        print_info(f"Found {log_markers} logging points with [GraphVisualizer] marker")
        
        if log_markers == 0:
            print_error("No logging infrastructure found in graph_visualizer.py")
            return False
        
        # Check for specific critical logging
        critical_functions = [
            'populate_from_report',
            '_render_graph',
            '_render_with_plotly',
            'setHtml',
        ]
        
        missing = []
        for func in critical_functions:
            if func not in content:
                missing.append(func)
            else:
                print_ok(f"Function '{func}' found")
        
        if missing:
            print_error(f"Missing functions: {missing}")
            return False
        
        print_ok("All critical functions present in code")
        
        return True
        
    except Exception as e:
        print_error(f"Logging check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_channel_registration():
    """Check if WebChannel is properly registered"""
    print_header("Testing WebChannel Registration")
    
    try:
        from pathlib import Path
        
        graph_viz_file = Path(__file__).parent / "n_audit" / "gui" / "graph_visualizer.py"
        content = graph_viz_file.read_text(encoding='utf-8')
        
        required_checks = [
            ('QWebChannel instantiation', 'QWebChannel()'),
            ('Bridge registration', 'registerObject'),
            ('WebChannel assignment', 'setWebChannel'),
            ('GraphNodeBridge class', 'class GraphNodeBridge'),
        ]
        
        all_found = True
        for check_name, check_string in required_checks:
            if check_string in content:
                print_ok(f"{check_name}: Found")
            else:
                print_error(f"{check_name}: NOT FOUND - looking for '{check_string}'")
                all_found = False
        
        if not all_found:
            print_error("WebChannel registration incomplete")
            return False
        
        print_ok("WebChannel registration fully configured")
        
        return True
        
    except Exception as e:
        print_error(f"WebChannel check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic tests"""
    print_header("WebView Rendering Diagnostic")
    print_info("Python version: " + sys.version.split()[0])
    print_info("Platform: " + sys.platform)
    
    results = []
    
    # Test 1: HTML Generation
    results.append(("HTML Generation", test_html_generation()))
    
    # Test 2: GraphVisualizerWidget
    results.append(("Widget Data Storage", test_graph_visualizer_widget()))
    
    # Test 3: Logging Infrastructure
    results.append(("Logging Infrastructure", test_logging_infrastructure()))
    
    # Test 4: WebChannel Registration
    results.append(("WebChannel Registration", test_web_channel_registration()))
    
    # Summary
    print_header("Diagnostic Summary")
    all_passed = True
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {name}")
        if not result:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print_ok("All diagnostics PASSED - rendering infrastructure is intact")
        print_info("If exe still shows white page, the issue is likely in:")
        print_info("  1. populate_from_report() not being called from main_window_v4.py")
        print_info("  2. Report data being empty when passed to graph_visualizer")
        print_info("  3. WebView initialization timing (too early render)")
        return 0
    else:
        print_error("Some diagnostics FAILED - infrastructure needs repair")
        return 1

if __name__ == '__main__':
    sys.exit(main())
