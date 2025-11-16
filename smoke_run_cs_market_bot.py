#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smoke-run script: run audit on target project, populate GraphVisualizer and write summary log.
"""
import sys
import os
from pathlib import Path
from datetime import datetime
import logging

# Setup paths
PROJECT_TO_TEST = r"G:\CODING\cs market bot"
LOG_DIR = Path.home() / '.naudit' / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / 'latest.log'

# Setup logging
logger = logging.getLogger('naudit-smoke')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler)
console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(console)

logger.info('=== nAUDIT Smoke-run start ===')
logger.info(f'Target project: {PROJECT_TO_TEST}')

# Run audit
try:
    # Import AuditEngine
    from n_audit.audit_engine import AuditEngine
    engine = AuditEngine()
    logger.info('AuditEngine instantiated')

    report = engine.audit(PROJECT_TO_TEST)
    logger.info('Audit finished')

    # Summarize report
    try:
        total_files = report.metrics.total_files if hasattr(report, 'metrics') else 'unknown'
    except Exception:
        total_files = 'unknown'
    logger.info(f'Report summary: files={total_files}')

except Exception as e:
    logger.exception('Audit failed')
    sys.exit(2)

# Instantiate GraphVisualizer and populate (headless)
try:
    # PyQt app
    try:
        # Ensure Qt OpenGL sharing attribute is set before creating QCoreApplication
        # Importing PyQt6.QtCore to set AA_ShareOpenGLContexts is safe and does not create QCoreApplication
        from PyQt6.QtCore import QCoreApplication, Qt as _QtCore
        try:
            QCoreApplication.setAttribute(_QtCore.ApplicationAttribute.AA_ShareOpenGLContexts)
        except Exception:
            # best-effort: if this fails, continue and let imports raise a clear error
            pass

        from PyQt6.QtWidgets import QApplication
    except Exception:
        QApplication = None

    app = None
    if QApplication is not None:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

    # Import the graph visualizer v2_6
    try:
        from n_audit.gui.graph_visualizer_v2_6 import GraphVisualizerWidget
    except Exception as e:
        # Fallback to older module name
        from n_audit.gui.graph_visualizer import GraphVisualizerWidget

    widget = GraphVisualizerWidget()
    logger.info('GraphVisualizerWidget created')

    widget.populate_from_report(report, PROJECT_TO_TEST)
    node_count = len(widget.nodes)
    edge_count = len(widget.edges)
    folder_count = len(widget.folder_colors)

    logger.info(f'Graph populated: nodes={node_count}, edges={edge_count}, folders={folder_count}')

    # GPU attempt
    try:
        import torch
        has_torch = True
    except Exception:
        has_torch = False

    gpu_used = False
    try:
        if has_torch and torch.cuda.is_available():
            gpu_used = True
    except Exception:
        gpu_used = False

    logger.info(f'GPU available: {gpu_used} (torch_installed={has_torch})')

    # Add a compact JSON summary at the end
    summary = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'project': str(PROJECT_TO_TEST),
        'nodes': node_count,
        'edges': edge_count,
        'folders': folder_count,
        'gpu_available': gpu_used,
    }
    logger.info('SUMMARY: ' + str(summary))

except Exception as e:
    logger.exception('Graph population failed')
    sys.exit(3)

logger.info('=== nAUDIT Smoke-run finished ===')
print(f"Logs written to: {LOG_FILE}")
print('Done')
