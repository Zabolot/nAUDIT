#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nAUDIT Ultimate Builder - PyInstaller build system

Объединяет лучшие практики из:
- build_exe_v4.py (архитектура)
- build_exe_final_v2_3.py (проверки и диагностика)
- build_exe_production.py (v2.1+ компоненты и Plotly/PyVis)

Поддерживает:
- PyQt6 6.10+ с WebEngine
- Plotly интерактивные графы
- PyVis физические симуляции
- NetworkX граф-анализ
- Полная граф-визуализация с синхронизацией дерева
"""

import sys
import subprocess
import shutil
import time
from pathlib import Path
from datetime import datetime


# ════════════════════════════════════════════════════════════════
# Configuration
# ════════════════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).parent
VENV_PYTHON = PROJECT_ROOT / "v.naudit" / "Scripts" / "python.exe"
ENTRY_POINT = PROJECT_ROOT / "run_naudit_gui.py"
OUTPUT_EXE = PROJECT_ROOT / "dist" / "nAUDIT.exe"

# ════════════════════════════════════════════════════════════════
# Colors and output
# ════════════════════════════════════════════════════════════════

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def print_step(step_num, total, text):
    print(f"[{step_num}/{total}] {text}")

def print_ok(text):
    print(f"  [OK] {text}")

def print_error(text):
    print(f"  [ERROR] {text}")

def print_warn(text):
    print(f"  [WARN] {text}")

def print_info(text):
    print(f"  [INFO] {text}")


# ════════════════════════════════════════════════════════════════
# Verification
# ════════════════════════════════════════════════════════════════

def verify_entry_point():
    """Verify entry point exists"""
    if not ENTRY_POINT.exists():
        print_error(f"Entry point not found: {ENTRY_POINT}")
        return False
    print_ok(f"Entry point exists: {ENTRY_POINT.name}")
    return True


def verify_n_audit_module():
    """Verify n_audit module structure"""
    n_audit_path = PROJECT_ROOT / "n_audit"
    
    if not n_audit_path.exists():
        print_error(f"n_audit module not found: {n_audit_path}")
        return False
    
    required_files = [
        "gui/main_window_v4.py",
        "gui/graph_visualizer.py",
        "gui/error_visualization.py",
        "gui/tree_widget.py",
    ]
    
    all_found = True
    for file_path in required_files:
        full_path = n_audit_path / file_path
        if full_path.exists():
            print_ok(f"Found: {file_path}")
        else:
            print_error(f"Missing: {file_path}")
            all_found = False
    
    return all_found


def verify_dependencies():
    """Verify all required dependencies"""
    print_info("Checking Python dependencies...")
    
    dependencies = [
        ("PyQt6", "PyQt6"),
        ("PyQt6.QtWebEngineWidgets", "PyQt6.QtWebEngineWidgets"),
        ("plotly", "plotly"),
        ("pyvis", "pyvis"),
        ("networkx", "networkx"),
        ("PyInstaller", "PyInstaller"),
    ]
    
    all_ok = True
    for display_name, import_name in dependencies:
        try:
            __import__(import_name)
            print_ok(f"{display_name}")
        except ImportError:
            print_error(f"{display_name} - NOT INSTALLED")
            all_ok = False
    
    return all_ok


def verify_pyinstaller_tools():
    """Verify PyInstaller is working"""
    print_info("Verifying PyInstaller...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            print_ok(f"PyInstaller: {version}")
            return True
        else:
            print_error("PyInstaller not working")
            return False
    except Exception as e:
        print_error(f"PyInstaller check failed: {e}")
        return False


# ════════════════════════════════════════════════════════════════
# Build System
# ════════════════════════════════════════════════════════════════

def clean_old_builds():
    """Clean old build artifacts"""
    print_info("Cleaning old builds...")
    
    # Remove old exe
    exe_path = PROJECT_ROOT / "dist" / "nAUDIT.exe"
    if exe_path.exists():
        exe_path.unlink()
        print_ok(f"Removed: {exe_path.name}")
    
    # Clean work directories
    for work_dir in [PROJECT_ROOT / "build" / "nAUDIT", 
                     PROJECT_ROOT / "build_v2_4"]:
        if work_dir.exists():
            shutil.rmtree(work_dir, ignore_errors=True)
            print_ok(f"Cleaned: {work_dir.name}")


def build_pyinstaller_command():
    """Build PyInstaller command with all parameters"""
    
    print_info("Building PyInstaller command...")
    
    n_audit_path = PROJECT_ROOT / "n_audit"
    dist_dir = PROJECT_ROOT / "dist"
    build_dir = PROJECT_ROOT / "build"
    
    # Base command
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--onefile",                              # Single exe file
        "--windowed",                             # GUI mode
        "--name=nAUDIT",                         # Exe name
        f"--distpath={str(dist_dir)}",
        f"--workpath={str(build_dir / 'work')}",
        f"--specpath={str(build_dir)}",
        "--noupx",                                # Disable UPX
        "-y",                                     # Overwrite without asking
    ]
    
    # Add data (n_audit module and assets)
    separator = ";" if sys.platform == "win32" else ":"
    cmd.append(f"--add-data={str(n_audit_path)}{separator}n_audit")
    cmd.append(f"--add-data={str(PROJECT_ROOT / 'assets')}{separator}assets")
    
    # Critical hidden imports for graph visualization
    critical_imports = [
        # PyQt6 core and web
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtWebEngineCore",
        "PyQt6.QtWebChannel",                    # CRITICAL for graph synchronization
        
        # Graph visualization
        "networkx",
        "networkx.algorithms",
        "pyvis",
        "pyvis.network",
        "plotly",
        "plotly.graph_objects",
        "plotly.offline",
        "plotly.io",
        
        # Code analysis
        "pylint.lint",
        "flake8.api.legacy",
        "bandit.main",
    ]
    
    for imp in critical_imports:
        cmd.append(f"--hidden-import={imp}")
    
    # Collect all data for complex packages
    cmd.extend([
        "--collect-all=PyQt6",
        "--collect-all=plotly",
        "--collect-all=pyvis",
        "--collect-submodules=pyvis",
        "--collect-submodules=plotly",
    ]
    )
    
    # Include PyVis templates (IMPORTANT for interactive graphs)
    try:
        pyvis_templates = Path(sys.prefix) / "Lib" / "site-packages" / "pyvis" / "templates"
        if pyvis_templates.exists():
            cmd.append(f"--add-data={str(pyvis_templates)}{separator}pyvis/templates")
            print_ok("Added PyVis templates")
    except:
        print_warn("Could not locate PyVis templates")
    
    # Entry point
    cmd.append(str(ENTRY_POINT))
    
    print_ok(f"Command built with {len(cmd)} arguments")
    return cmd


def run_pyinstaller(cmd):
    """Run PyInstaller build process"""
    
    print_info("Starting build process...")
    print()
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            timeout=900  # 15 minutes max
        )
        
        elapsed = time.time() - start_time
        return result.returncode, elapsed
        
    except subprocess.TimeoutExpired:
        print_error("Build timed out after 15 minutes")
        return 1, 900
    except Exception as e:
        print_error(f"Build error: {e}")
        return 1, 0


def verify_build_output():
    """Verify the build was successful"""
    
    if not OUTPUT_EXE.exists():
        print_error(f"Output exe not found: {OUTPUT_EXE}")
        return False
    
    size_mb = OUTPUT_EXE.stat().st_size / (1024 * 1024)
    mtime = OUTPUT_EXE.stat().st_mtime
    mod_time = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
    
    print_ok(f"Exe created: {OUTPUT_EXE.name}")
    print_ok(f"Size: {size_mb:.1f} MB")
    print_ok(f"Modified: {mod_time}")
    
    return True


# ════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════

def main():
    """Main build process"""
    
    print_header("nAUDIT Ultimate Builder")
    print_info(f"Python: {sys.version.split()[0]}")
    print_info(f"Platform: {sys.platform}")
    print_info(f"Project: {PROJECT_ROOT}")
    print()
    
    # Step 1: Verify prerequisites
    print_step(1, 7, "Verifying prerequisites")
    
    checks = [
        ("Entry point", verify_entry_point),
        ("n_audit module", verify_n_audit_module),
        ("Dependencies", verify_dependencies),
        ("PyInstaller tools", verify_pyinstaller_tools),
    ]
    
    all_ok = True
    for check_name, check_func in checks:
        print_info(f"Checking {check_name}...")
        if not check_func():
            print_error(f"{check_name} check failed")
            all_ok = False
        print()
    
    if not all_ok:
        print_error("Prerequisites not met")
        return False
    
    # Step 2: Clean old builds
    print_step(2, 7, "Cleaning old builds")
    clean_old_builds()
    print()
    
    # Step 3: Prepare output directories
    print_step(3, 7, "Preparing directories")
    
    dist_dir = PROJECT_ROOT / "dist"
    build_dir = PROJECT_ROOT / "build"
    
    dist_dir.mkdir(exist_ok=True)
    build_dir.mkdir(exist_ok=True)
    
    print_ok(f"Created: {dist_dir}")
    print_ok(f"Created: {build_dir}")
    print()
    
    # Step 4: Build command
    print_step(4, 7, "Building PyInstaller command")
    cmd = build_pyinstaller_command()
    print()
    
    # Step 5: Run PyInstaller
    print_step(5, 7, "Running PyInstaller")
    return_code, elapsed = run_pyinstaller(cmd)
    
    print()
    print(f"  Build completed in {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    print()
    
    # Step 6: Verify output
    print_step(6, 7, "Verifying build output")
    
    if return_code != 0:
        print_error(f"PyInstaller failed with return code {return_code}")
        return False
    
    if not verify_build_output():
        return False
    
    print()
    
    # Step 7: Final summary
    print_step(7, 7, "Build summary")
    
    print_header("BUILD SUCCESSFUL")
    print_ok(f"Executable: {OUTPUT_EXE}")
    print_ok(f"Size: {OUTPUT_EXE.stat().st_size / (1024 * 1024):.1f} MB")
    print_ok(f"Total time: {elapsed/60:.1f} minutes")
    print()
    print_info("You can now run the exe:")
    print_info(f'  & "{OUTPUT_EXE}"')
    print()
    
    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[FATAL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
