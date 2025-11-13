# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['G:\\CODING\\nAUDIT\\run_naudit_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('n_audit/gui', 'n_audit/gui')],
    hiddenimports=['PyQt6', 'matplotlib', 'pylint', 'flake8'],
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
    name='nAUDIT_v4',
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
)
