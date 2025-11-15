#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nAUDIT v2.7 - Final Build with GPU & Hierarchy Support

Сборка финального exe включающего:
✅ GPU Detection & System Optimization (gpu_detector.py)
✅ Hierarchical Folder Clustering (graph_visualizer_v2_6.py updates)
✅ Error Display Fix (tree_widget.py dual-source compatibility)
✅ psutil dependency
"""

import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
VENV_PYTHON = PROJECT_ROOT / "v.naudit" / "Scripts" / "python.exe"

def run_command(cmd, description):
    """Выполняет команду и выводит результат"""
    print(f"\n{'='*70}")
    print(f"📦 {description}")
    print(f"{'='*70}\n")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
        if result.returncode == 0:
            print(f"\n✅ {description} - SUCCESS")
            return True
        else:
            print(f"\n❌ {description} - FAILED (code {result.returncode})")
            return False
    except Exception as e:
        print(f"\n❌ {description} - ERROR: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("  🚀 nAUDIT v2.7 BUILD - GPU + HIERARCHY + ERROR FIX")
    print("="*70)
    
    start_time = datetime.now()
    
    # Step 1: Clean old build
    print("\n[1/4] Cleaning old build artifacts...")
    build_dir = PROJECT_ROOT / "build"
    dist_dir = PROJECT_ROOT / "dist"
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("✅ Removed build/ directory")
    
    if (dist_dir / "nAUDIT.exe").exists():
        (dist_dir / "nAUDIT.exe").unlink()
        print("✅ Removed old nAUDIT.exe")
    
    # Step 2: Run pre-build checks
    print("\n[2/4] Running pre-build checks...")
    if not run_command(f'"{VENV_PYTHON}" pre_build_integration_test.py', "Integration Test"):
        print("\n❌ Pre-build checks failed - aborting build")
        return 1
    
    # Step 3: Run quality assurance
    print("\n[3/4] Running quality assurance...")
    if not run_command(f'"{VENV_PYTHON}" pre_build_qa_checks.py', "Quality Assurance"):
        print("\n❌ QA checks failed - aborting build")
        return 1
    
    # Step 4: Build executable
    print("\n[4/4] Building executable with PyInstaller...")
    if not run_command(f'"{VENV_PYTHON}" build_exe_ultimate.py', "PyInstaller Build"):
        print("\n❌ PyInstaller build failed")
        return 1
    
    # Verify build
    exe_path = dist_dir / "nAUDIT.exe"
    if exe_path.exists():
        exe_size_mb = exe_path.stat().st_size / (1024 * 1024)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        print("\n" + "="*70)
        print("  ✅ BUILD SUCCESSFUL - nAUDIT v2.7")
        print("="*70)
        print(f"\n📁 Output: {exe_path}")
        print(f"📊 Size: {exe_size_mb:.1f} MB")
        print(f"⏱️  Build time: {elapsed:.1f} seconds")
        print(f"\n✨ New Features in v2.7:")
        print(f"   ✅ GPU Acceleration Support")
        print(f"   ✅ Hierarchical Folder Clustering (recursive)")
        print(f"   ✅ Error Display Fix (dual-source compatibility)")
        print(f"   ✅ System Resource Optimization")
        print("\n🎉 Ready to test!")
        print("="*70 + "\n")
        return 0
    else:
        print("\n❌ Build failed - executable not found at", exe_path)
        return 1

if __name__ == "__main__":
    sys.exit(main())
