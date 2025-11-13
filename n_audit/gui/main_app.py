"""
Точка входа в GUI приложение nAUDIT.
"""

import sys
import os

# Убедимся, что родительская папка проекта в sys.path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def main():
    """Запуск GUI приложения"""
    import sys
    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError as e:
        print(f"Ошибка импорта PyQt6: {e}")
        sys.exit(1)
    
    try:
        # Пробуем разные варианты импорта для совместимости с PyInstaller
        try:
            from n_audit.gui.main_window_v3 import nAUDITMainWindow
        except (ImportError, ModuleNotFoundError):
            try:
                from gui.main_window_v3 import nAUDITMainWindow
            except (ImportError, ModuleNotFoundError):
                try:
                    from n_audit.gui.main_window_v2 import nAUDITMainWindow
                except (ImportError, ModuleNotFoundError):
                    import os
                    gui_path = os.path.dirname(os.path.abspath(__file__))
                    sys.path.insert(0, gui_path)
                    try:
                        from main_window_v3 import nAUDITMainWindow
                    except (ImportError, ModuleNotFoundError):
                        from main_window_v2 import nAUDITMainWindow
    except ImportError as e:
        print(f"Ошибка импорта интерфейса: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    try:
        app = QApplication(sys.argv)
        window = nAUDITMainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Критическая ошибка при запуске приложения: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
