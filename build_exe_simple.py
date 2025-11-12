#!/usr/bin/env python3
"""
Финальный скрипт сборки nAUDIT.exe - МИНИМАЛЬНЫЙ И НАДЕЖНЫЙ.
Решает все проблемы с ModuleNotFoundError используя только необходимые параметры.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def main():
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    print("=" * 70)
    print("[*] nAUDIT - FINAL EXECUTABLE BUILD")
    print("=" * 70)
    
    # Очистка старых сборок
    print("\n[1/3] Cleaning old builds...")
    for path in ["build", "dist"]:
        if (project_root / path).exists():
            shutil.rmtree(project_root / path)
            print(f"   OK Deleted: {path}/")
    
    for spec_file in project_root.glob("*.spec"):
        spec_file.unlink()
        print(f"   OK Deleted: {spec_file.name}")
    
    # Сборка - САМЫЙ ПРОСТОЙ И НАДЕЖНЫЙ СПОСОБ
    print("\n[2/3] Building application (takes 1-2 minutes)...")
    print("   Using: PyInstaller with --collect-all")
    print("   Parameters:")
    print("     * --onefile (single file)")
    print("     * --windowed (no console)")
    print("     * --collect-all=n_audit (all modules)")
    print("     * --collect-all=PyQt6 (all Qt6 libraries)")
    print()
    
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name=nAUDIT",
        "--collect-all=n_audit",
        "--collect-all=PyQt6",
        str(project_root / "n_audit" / "gui" / "main_app.py")
    ]
    
    result = subprocess.run(cmd, cwd=project_root)
    
    if result.returncode != 0:
        print("\n[ERROR] Build failed!")
        sys.exit(1)
    
    # Проверка результата
    print("\n[3/3] Verifying result...")
    exe_file = project_root / "dist" / "nAUDIT.exe"
    
    if exe_file.exists():
        size_mb = exe_file.stat().st_size / (1024 * 1024)
        print(f"   OK File created: {exe_file}")
        print(f"   OK Size: {size_mb:.1f} MB")
    else:
        print(f"   ERROR File not found: {exe_file}")
        sys.exit(1)
    
    # Итоги
    print("\n" + "=" * 70)
    print("[SUCCESS] Build completed successfully!")
    print("=" * 70)
    print(f"\nExecutable: {exe_file}")
    print(f"\nYou can now run the application:")
    print(f"   {exe_file}")
    print(f"\nOr share it with users - no dependencies required!")
    print()


if __name__ == "__main__":
    main()
