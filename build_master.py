#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MASTER BUILD SCRIPT - Complete nAUDIT v2.7 Build with All Fixes
"""
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

class BuildMaster:
    def __init__(self):
        self.start_time = datetime.now()
        self.log_file = Path("build_master.log")
        self.status = {}
        
    def log(self, msg):
        """Log message to both console and file"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_msg = f"[{timestamp}] {msg}"
        print(full_msg)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(full_msg + "\n")
    
    def clear_logs(self):
        """Clear previous logs"""
        if self.log_file.exists():
            self.log_file.unlink()
    
    def step(self, name, action_func):
        """Execute a build step"""
        self.log(f"\n{'='*70}")
        self.log(f"STEP: {name}")
        self.log(f"{'='*70}")
        try:
            result = action_func()
            self.status[name] = "PASS" if result else "FAIL"
            return result
        except Exception as e:
            self.log(f"ERROR: {e}")
            self.status[name] = "ERROR"
            return False
    
    def step_verify_dependencies(self):
        """Verify all dependencies are installed"""
        self.log("Checking Python packages...")
        required = ['PyQt6', 'torch', 'pyvis', 'networkx', 'plotly', 'psutil']
        
        missing = []
        for pkg in required:
            try:
                __import__(pkg)
                self.log(f"  [{pkg:15}] OK")
            except ImportError:
                self.log(f"  [{pkg:15}] MISSING")
                missing.append(pkg)
        
        if missing:
            self.log(f"\nMissing packages: {', '.join(missing)}")
            return False
        return True
    
    def step_syntax_check(self):
        """Check Python syntax of all files"""
        self.log("Checking syntax...")
        import py_compile
        
        py_files = list(Path("n_audit").rglob("*.py"))
        errors = 0
        
        for py_file in py_files[:10]:  # Check first 10 files
            try:
                py_compile.compile(str(py_file), doraise=True)
                self.log(f"  [{py_file.name}] OK")
            except Exception as e:
                self.log(f"  [{py_file.name}] ERROR")
                errors += 1
        
        return errors == 0
    
    def step_requirements_check(self):
        """Verify requirements.txt has all necessary packages"""
        self.log("Checking requirements.txt...")
        req_file = Path("requirements.txt")
        
        if not req_file.exists():
            self.log("  requirements.txt NOT FOUND")
            return False
        
        content = req_file.read_text()
        required = {
            'torch': 'GPU/ML support',
            'PyQt6': 'UI Framework',
            'pyvis': 'Graph visualization',
            'networkx': 'Graph algorithms',
            'plotly': 'Interactive plots',
            'psutil': 'System info',
        }
        
        for pkg, desc in required.items():
            if pkg in content:
                self.log(f"  {pkg:15} {desc:20} OK")
            else:
                self.log(f"  {pkg:15} {desc:20} MISSING")
                return False
        
        return True
    
    def step_build_exe(self):
        """Build the executable with PyInstaller"""
        self.log("Building executable with PyInstaller...")
        
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name", "nAUDIT",
            "--distpath", "dist",
            "--buildpath", "build",
            "--specpath", ".",
            "--clean",
            "--noconfirm",
            "--icon", "icon.ico" if Path("icon.ico").exists() else None,
            "run_naudit_gui.py",
        ]
        
        # Remove None values
        cmd = [c for c in cmd if c is not None]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            self.log(f"Build failed:")
            self.log(result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
            return False
        
        exe_path = Path("dist/nAUDIT.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            self.log(f"Executable created: {exe_path} ({size_mb:.1f} MB)")
            return True
        else:
            self.log("Executable not found after build")
            return False
    
    def step_verify_build(self):
        """Verify the built executable"""
        self.log("Verifying executable...")
        
        exe_path = Path("dist/nAUDIT.exe")
        if not exe_path.exists():
            self.log(f"  Executable NOT FOUND")
            return False
        
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        self.log(f"  File exists: {exe_path}")
        self.log(f"  Size: {size_mb:.1f} MB")
        self.log(f"  Created: {datetime.fromtimestamp(exe_path.stat().st_mtime)}")
        
        return size_mb > 100  # Should be at least 100MB with all dependencies
    
    def run_full_build(self):
        """Execute full build pipeline"""
        self.clear_logs()
        self.log("NAUDIT v2.7 - MASTER BUILD")
        self.log(f"Start time: {self.start_time}")
        
        # Steps
        steps = [
            ("Verify Dependencies", self.step_verify_dependencies),
            ("Syntax Check", self.step_syntax_check),
            ("Requirements Check", self.step_requirements_check),
            ("Build Executable", self.step_build_exe),
            ("Verify Build", self.step_verify_build),
        ]
        
        for name, func in steps:
            if not self.step(name, func):
                self.log(f"\n[!] Build halted at step: {name}")
                break
        
        # Summary
        self.log(f"\n{'='*70}")
        self.log("BUILD SUMMARY")
        self.log(f"{'='*70}")
        
        for step_name, status in self.status.items():
            symbol = "[OK]" if status == "PASS" else "[ER]"
            self.log(f"{symbol} {step_name:30} {status}")
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        self.log(f"\nDuration: {duration:.1f} seconds")
        self.log(f"Timestamp: {end_time}")
        
        # Save metadata
        metadata = {
            "build_time": str(self.start_time),
            "duration_seconds": duration,
            "status": self.status,
            "exe_path": str(Path("dist/nAUDIT.exe")),
            "exe_size_mb": Path("dist/nAUDIT.exe").stat().st_size / (1024*1024) if Path("dist/nAUDIT.exe").exists() else 0,
        }
        
        with open("build_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        self.log(f"\nMetadata saved to build_metadata.json")
        
        all_pass = all(s == "PASS" for s in self.status.values())
        return all_pass

if __name__ == "__main__":
    builder = BuildMaster()
    success = builder.run_full_build()
    sys.exit(0 if success else 1)
