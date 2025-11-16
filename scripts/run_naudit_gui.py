#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрый запуск nAUDIT v4.0 GUI из репозитория или .exe
"""

import sys
import os
from pathlib import Path

# Добавляем папку проекта в path для разработки
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Если запускается из .exe, импорты будут работать правильно
# Если из dev среды - добавляем путь

def main():
    """Главная функция запуска"""
    try:
        print("[*] Starting nAUDIT v4.0 GUI...")
        print(f"[*] Python: {sys.version.split()[0]}")
        print(f"[*] Executable path: {Path(__file__).absolute()}")
        
        # Инициализируем логирование ПЕРВЫМ
        print("[*] Initializing logging system...")
        from n_audit.core.logger import init_logging, get_logger
        init_logging()
        logger = get_logger(__name__)
        logger.info("=" * 70)
        logger.info("nAUDIT v2.7 GUI Started")
        logger.info(f"Python: {sys.version}")
        logger.info(f"Path: {Path(__file__).absolute()}")
        
        print("[*] Loading PyQt6...")
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        logger.debug("PyQt6 loaded successfully")
        
        print("[*] Loading GUI components...")
        from n_audit.gui.main_window_v4 import MainWindowV4
        logger.debug("GUI components loaded")
        
        print("[*] Initializing Qt Application...")
        app = QApplication(sys.argv)
        
        print("[*] Creating main window...")
        window = MainWindowV4()
        logger.info("Main window created")
        
        print("[*] Showing window...")
        window.show()
        logger.info("Main window shown")
        
        print("[*] Entering event loop...")
        logger.info("Entering event loop")
        exit_code = app.exec()
        
        print(f"[*] Application closed with code: {exit_code}")
        logger.info(f"Application exited with code: {exit_code}")
        logger.info("=" * 70)
        return exit_code
        
    except ImportError as e:
        print(f"[✗] Import error: {e}")
        print(f"[!] Make sure all dependencies are installed:")
        print(f"    pip install PyQt6 matplotlib pylint flake8 mypy bandit safety")
        return 1
        
    except Exception as e:
        print(f"[✗] Error: {e}")
        import traceback
        traceback.print_exc()
        try:
            logger.error(f"Application fatal error: {e}", exc_info=True)
        except:
            pass
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
