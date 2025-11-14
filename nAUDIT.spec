# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['G:\\CODING\\nAUDIT\\n_audit\\gui\\main_app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'PyQt6.QtWebEngineWidgets', 'PyQt6.QtWebEngineCore', 'n_audit.core', 'n_audit.code_analysis', 'n_audit.security', 'n_audit.tests_analysis', 'n_audit.infrastructure', 'n_audit.recommendations', 'n_audit.visualizations', 'n_audit.audit_manager', 'n_audit.gui.main_window_v4', 'n_audit.gui.tree_widget', 'n_audit.gui.graph_visualizer', 'n_audit.gui.error_visualization', 'n_audit.gui.metrics_visualizer', 'n_audit.gui.styles', 'networkx', 'pyvis', 'matplotlib'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='nAUDIT',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='NONE',
)
