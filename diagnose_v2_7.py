#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nAUDIT v2.7 - Diagnostic Tool
Инструмент для диагностики проблем с анализом
"""

import sys
from pathlib import Path

# Setup path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Диагностика системы"""
    
    print("\n" + "="*70)
    print("  nAUDIT v2.7 - DIAGNOSTIC TOOL")
    print("="*70 + "\n")
    
    # 1. Инициализация логирования
    print("[1/5] Initializing logging system...")
    try:
        from n_audit.core.logger import init_logging, get_logger, LoggerManager
        init_logging()
        logger = get_logger(__name__)
        logger.info("Logging system initialized")
        print("✅ Logging initialized")
        print(f"📁 Log directory: {LoggerManager.get_log_path()}\n")
    except Exception as e:
        print(f"❌ Failed to initialize logging: {e}\n")
        return 1
    
    # 2. Check GPU detection
    print("[2/5] Testing GPU detection...")
    try:
        from n_audit.gui.gpu_detector import GPUDetector
        logger.info("Testing GPU detection")
        
        resources = GPUDetector.get_system_resources()
        logger.info(f"System resources: CPU={resources.cpu_count}, RAM={resources.total_memory_gb:.1f}GB, GPU={resources.gpu_available}")
        
        print(f"✅ GPU Detection working")
        print(f"   OS: {resources.os_name}")
        print(f"   CPU Cores: {resources.cpu_count}")
        print(f"   Total RAM: {resources.total_memory_gb:.1f} GB")
        print(f"   Available RAM: {resources.available_memory_gb:.1f} GB")
        print(f"   GPU Available: {resources.gpu_available}")
        if resources.gpu_available and resources.gpu_info:
            print(f"   GPU Model: {resources.gpu_info.name}")
            print(f"   GPU Memory: {resources.gpu_info.memory_mb} MB")
        
        level = resources.get_optimization_level()
        print(f"   Optimization Level: {level}\n")
        logger.info(f"Optimization level: {level}")
        
    except Exception as e:
        print(f"❌ GPU detection error: {e}\n")
        logger.error(f"GPU detection error: {e}", exc_info=True)
    
    # 3. Test audit engine
    print("[3/5] Testing Audit Engine...")
    try:
        from n_audit.audit_engine import AuditEngine
        logger.info("Testing AuditEngine")
        
        engine = AuditEngine()
        logger.info("AuditEngine created successfully")
        print("✅ AuditEngine loaded\n")
        
    except Exception as e:
        print(f"❌ AuditEngine error: {e}\n")
        logger.error(f"AuditEngine error: {e}", exc_info=True)
        return 1
    
    # 4. Test tree widget imports
    print("[4/5] Testing Tree Widget...")
    try:
        from n_audit.gui.tree_widget import ErrorTreeWidget
        logger.info("Testing TreeWidget")
        
        print("✅ Tree Widget loaded\n")
        
    except Exception as e:
        print(f"❌ Tree Widget error: {e}\n")
        logger.error(f"Tree Widget error: {e}", exc_info=True)
    
    # 5. Test graph visualizer
    print("[5/5] Testing Graph Visualizer...")
    try:
        from n_audit.gui.graph_visualizer_v2_6 import GraphVisualizerWidget
        logger.info("Testing GraphVisualizer")
        
        print("✅ Graph Visualizer loaded\n")
        
    except Exception as e:
        print(f"❌ Graph Visualizer error: {e}\n")
        logger.error(f"Graph Visualizer error: {e}", exc_info=True)
    
    # Final summary
    print("="*70)
    print("  DIAGNOSTIC SUMMARY")
    print("="*70)
    print("""
✅ All critical components loaded successfully!

📋 IMPORTANT INFORMATION:
   - Logging is ACTIVE and monitoring all operations
   - Log file: $HOME/.naudit/logs/naudit_YYYYMMDD_HHMMSS.log
   - All errors will be recorded with full stack traces
   - GPU acceleration status: See above

🚀 NEXT STEPS:
   1. Check log file for detailed debug information
   2. If audit crashes, check logs for error details
   3. Report any errors found in logs with context

📞 TROUBLESHOOTING:
   - If you see errors: Check the log file
   - Log file location printed above
   - Share log file if reporting issues
""")
    
    logger.info("Diagnostic completed successfully")
    print("\n" + "="*70)
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
