#!/usr/bin/env python3
"""
Pre-build environment checker for nAUDIT v2.1.0
Verifies all requirements before starting the build process
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def print_ok(text):
    print(f"[OK] {text}")

def print_warn(text):
    print(f"[WARN] {text}")

def print_error(text):
    print(f"[ERROR] {text}")

def check_python_version():
    """Check if Python version is 3.10+"""
    print_header("1. Python Version Check")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 10:
        print_ok(f"Python {version_str} (suitable for build)")
        return True
    else:
        print_error(f"Python {version_str} (requires 3.10+)")
        return False

def check_venv():
    """Check if virtual environment is active"""
    print_header("2. Virtual Environment Check")
    
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_ok(f"venv is active: {sys.prefix}")
        return True
    else:
        print_warn("venv is NOT active")
        print("To activate, run:")
        print("  . .\\v.naudit\\Scripts\\Activate.ps1")
        return False

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    print_header("3. PyInstaller Check")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", "PyInstaller"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    version = line.split(': ')[1]
                    print_ok(f"PyInstaller {version} installed")
                    return True
        
        print_error("PyInstaller not found")
        print("\nTo install, run:")
        print("  pip install PyInstaller --upgrade")
        return False
        
    except Exception as e:
        print_error(f"Failed to check PyInstaller: {e}")
        return False

def check_dependencies():
    """Check if all required packages are installed"""
    print_header("4. Dependencies Check")
    
    required = [
        "PyQt6",
        "PyQt6-WebEngine",
        "networkx",
        "pyvis",
        "matplotlib"
    ]
    
    all_ok = True
    
    for package in required:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        version = line.split(': ')[1]
                        print_ok(f"{package} {version}")
                        break
            else:
                print_warn(f"{package} - not found or error")
                all_ok = False
                
        except Exception as e:
            print_warn(f"{package} - check failed: {e}")
            all_ok = False
    
    return all_ok

def check_gui_components():
    """Check if all GUI components exist"""
    print_header("5. GUI Components Check")
    
    components = [
        "n_audit/gui/main_app.py",
        "n_audit/gui/main_window_v4.py",
        "n_audit/gui/tree_widget.py",
        "n_audit/gui/graph_visualizer.py",
        "n_audit/gui/error_visualization.py"
    ]
    
    all_ok = True
    project_root = Path.cwd()
    
    for component in components:
        file_path = project_root / component
        if file_path.exists():
            size = file_path.stat().st_size
            print_ok(f"{component} ({size} bytes)")
        else:
            print_error(f"{component} - NOT FOUND")
            all_ok = False
    
    return all_ok

def check_builders():
    """Check if builder files exist"""
    print_header("6. Builder Files Check")
    
    builders = [
        "build_exe_fast.py",
        "build_exe_v2_1.py",
        "build.ps1",
        "build.bat"
    ]
    
    all_ok = True
    project_root = Path.cwd()
    
    for builder in builders:
        file_path = project_root / builder
        if file_path.exists():
            size = file_path.stat().st_size
            print_ok(f"{builder} ({size} bytes)")
        else:
            print_error(f"{builder} - NOT FOUND")
            all_ok = False
    
    return all_ok

def check_disk_space():
    """Check if there's enough disk space"""
    print_header("7. Disk Space Check")
    
    try:
        import shutil
        disk_usage = shutil.disk_usage('.')
        free_gb = disk_usage.free / (1024**3)
        
        if free_gb >= 1:
            print_ok(f"Disk space available: {free_gb:.1f} GB (required: 1 GB)")
            return True
        else:
            print_error(f"Disk space: only {free_gb:.1f} GB available (required: 1 GB)")
            return False
            
    except Exception as e:
        print_warn(f"Could not check disk space: {e}")
        return True

def check_dist_folder():
    """Check and report dist folder"""
    print_header("8. Build Output Directory Check")
    
    dist_path = Path("dist")
    
    if dist_path.exists():
        files = list(dist_path.glob("*"))
        if files:
            print_warn(f"dist folder exists with {len(files)} items")
            print("These will be overwritten during build")
        else:
            print_ok("dist folder exists and is empty")
    else:
        print_ok("dist folder will be created during build")
    
    return True

def main():
    """Run all checks"""
    print("\n")
    print_header("nAUDIT v2.1.0 - Pre-Build Environment Checker")
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_venv),
        ("PyInstaller", check_pyinstaller),
        ("Dependencies", check_dependencies),
        ("GUI Components", check_gui_components),
        ("Builder Files", check_builders),
        ("Disk Space", check_disk_space),
        ("Build Directory", check_dist_folder)
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print_error(f"Check '{name}' failed: {e}")
            results[name] = False
    
    # Summary
    print_header("Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nChecks passed: {passed}/{total}\n")
    
    for name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    print("\n")
    
    if passed == total:
        print_header("Ready to Build!")
        print("All checks passed. You can now run:")
        print("  python build_exe_fast.py")
        print("\nOr use the launcher:")
        print("  .\\build.ps1")
        return 0
    else:
        print_header("Issues Found")
        print("Please fix the issues above before building.")
        print("\nMost common fixes:")
        print("  1. Activate venv: . .\\v.naudit\\Scripts\\Activate.ps1")
        print("  2. Install PyInstaller: pip install PyInstaller")
        print("  3. Install dependencies: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    exit_code = main()
    input("\nPress Enter to close...")
    sys.exit(exit_code)
