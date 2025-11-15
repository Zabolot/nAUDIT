#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run exe with debugging output capture.
Captures logs to file for analysis.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

EXE_PATH = Path(__file__).parent / "dist" / "nAUDIT.exe"
LOG_FILE = Path(__file__).parent / "exe_debug_run.log"

print(f"[INFO] Running nAUDIT exe with debug output")
print(f"[INFO] Exe: {EXE_PATH}")
print(f"[INFO] Log: {LOG_FILE}")
print(f"[INFO] Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

if not EXE_PATH.exists():
    print(f"[ERROR] Exe not found: {EXE_PATH}")
    sys.exit(1)

print("[INFO] Starting exe...")
print("[INFO] Watch the terminal for [GraphVisualizer] logs")
print()
print("="*70)
print()

# Run exe and capture output
try:
    with open(LOG_FILE, 'w', encoding='utf-8') as log_f:
        process = subprocess.Popen(
            [str(EXE_PATH)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,  # Line buffering
            encoding='utf-8',
            errors='ignore'
        )
        
        # Print output in real-time and save to log
        for line in process.stdout:
            print(line, end='')
            log_f.write(line)
            log_f.flush()
        
        returncode = process.wait()
        
except KeyboardInterrupt:
    print("\n\n[INFO] Interrupted by user")
    try:
        process.terminate()
        process.wait(timeout=5)
    except:
        process.kill()
    returncode = -1

print()
print("="*70)
print()
print(f"[INFO] Exe finished with return code: {returncode}")
print(f"[INFO] Full output saved to: {LOG_FILE}")
print()

# Print summary of log
print("[INFO] Checking for [GraphVisualizer] messages in log...")
with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
    graph_logs = [line for line in content.split('\n') if '[GraphVisualizer]' in line]
    
    if graph_logs:
        print(f"[OK] Found {len(graph_logs)} GraphVisualizer log messages:")
        for log_line in graph_logs[:10]:  # Show first 10
            print(f"     {log_line}")
        if len(graph_logs) > 10:
            print(f"     ... and {len(graph_logs) - 10} more")
    else:
        print("[WARN] No [GraphVisualizer] messages found")

sys.exit(returncode)
