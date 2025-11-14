#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для построения nAUDIT v2.1.0 .exe

Использует PyInstaller для создания standalone exe.
Включает граф визуализацию, иерархическое древо и все компоненты v2.1.0.
"""

import sys
import subprocess
from pathlib import Path
import shutil
import os


def build_exe():
    """Построить .exe файл nAUDIT v2.1.0"""
    
    print("=" * 70)
    print("nAUDIT v2.1.0 - Построение .exe файла")
    print("=" * 70)
    
    # Путь к проекту
    project_root = Path(__file__).parent
    
    # Точка входа (используем main_app.py для совместимости)
    entry_point = project_root / "n_audit" / "gui" / "main_app.py"
    
    if not entry_point.exists():
        print(f"\n[!] Точка входа не найдена: {entry_point}")
        return False
    
    # Проверим существование основных компонентов
    print("\n[1/7] Проверка компонентов...")
    
    components_to_check = [
        ("n_audit", "Основной пакет"),
        ("n_audit/gui", "GUI компоненты"),
        ("n_audit/gui/main_app.py", "Точка входа"),
        ("n_audit/gui/main_window_v4.py", "Главное окно v4"),
        ("n_audit/gui/tree_widget.py", "Древо ошибок"),
        ("n_audit/gui/graph_visualizer.py", "Граф визуализатор"),
        ("n_audit/gui/error_visualization.py", "Панель ошибок"),
    ]
    
    for component, description in components_to_check:
        path = project_root / component
        if path.exists():
            print(f"  [OK] {description}: {component}")
        else:
            print(f"  [!] ОТСУТСТВУЕТ {description}: {component}")
    
    # Пути для сборки
    build_dir = project_root / 'build'
    dist_dir = project_root / 'dist'
    work_dir = build_dir / 'work'
    
    # Очищаем старые сборки
    print("\n[2/7] Очистка старых сборок...")
    
    for cleanup_dir in [dist_dir, work_dir]:
        if cleanup_dir.exists():
            print(f"  Удаляется: {cleanup_dir}")
            shutil.rmtree(cleanup_dir, ignore_errors=True)
    
    # Определяем путь к pyinstaller в venv
    print("\n[3/7] Проверка PyInstaller...")
    
    if sys.platform == "win32":
        pyinstaller_path = project_root / "v.naudit" / "Scripts" / "pyinstaller.exe"
    else:
        pyinstaller_path = project_root / "v.naudit" / "bin" / "pyinstaller"
    
    try:
        result = subprocess.run([str(pyinstaller_path), "--version"], 
                              capture_output=True, encoding="utf-8", timeout=5)
        if result.returncode == 0:
            print(f"  [OK] PyInstaller {result.stdout.strip()}")
        else:
            print(f"  [!] PyInstaller ошибка: {result.stderr}")
            return False
    except FileNotFoundError:
        print(f"  [!] PyInstaller не найден в: {pyinstaller_path}")
        return False
    
    # Скрытые импорты для v2.1.0
    print("\n[4/7] Подготовка параметров сборки...")
    
    hidden_imports = [
        # PyQt6 основные модули
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtWebEngineCore",
        "PyQt6.QtWebChannel",
        "PyQt6.QtNetwork",
        "PyQt6.QtPrintSupport",
        
        # nAUDIT основные модули
        "n_audit.core",
        "n_audit.core.project_analyzer",
        "n_audit.code_analysis",
        "n_audit.code_analysis.code_analyzer",
        "n_audit.security",
        "n_audit.security.security_analyzer",
        "n_audit.tests_analysis",
        "n_audit.infrastructure",
        "n_audit.recommendations",
        "n_audit.visualizations",
        "n_audit.visualizations.metrics_visualizer",
        "n_audit.audit_manager",
        
        # nAUDIT GUI модули (v2.1.0)
        "n_audit.gui",
        "n_audit.gui.main_app",
        "n_audit.gui.main_window_v4",
        "n_audit.gui.main_window_v3",
        "n_audit.gui.main_window_v2",
        "n_audit.gui.tree_widget",
        "n_audit.gui.graph_visualizer",
        "n_audit.gui.error_visualization",
        "n_audit.gui.metrics_visualizer",
        "n_audit.gui.styles",
        
        # Граф и визуализация (новое в v2.1.0)
        "networkx",
        "networkx.algorithms",
        "networkx.classes",
        "pyvis",
        "pyvis.network",
        "matplotlib",
        "matplotlib.backends",
        "matplotlib.backends.backend_qt5agg",
        "matplotlib.figure",
        "matplotlib.pyplot",
        "matplotlib.axes",
        
        # Вспомогательные модули
        "lxml",
        "lxml.etree",
        "PIL",
        "PIL.Image",
    ]
    
    print(f"  Скрытых импортов: {len(hidden_imports)}")
    print(f"  Точка входа: {entry_point}")
    print(f"  Выходной каталог: {dist_dir}")
    
    # Построение команды PyInstaller
    print("\n[5/7] Построение команды сборки...")
    
    cmd = [
        str(pyinstaller_path),
        "--onefile",                           # Один файл
        "--windowed",                          # Без консоли (GUI приложение)
        "--name=nAUDIT",                       # Имя exe файла
        f"--distpath={dist_dir}",              # Путь для .exe
        f"--workpath={work_dir}",              # Рабочая папка
        f"--specpath={build_dir}",             # Путь для .spec файла
        "--icon=NONE",                         # Можно добавить иконку позже
        "--noupx",                             # Отключить UPX сжатие для стабильности
    ]
    
    # Добавление скрытых импортов
    for hidden_import in hidden_imports:
        cmd.extend(["--hidden-import", hidden_import])
    
    # Точка входа в конце
    cmd.append(str(entry_point))
    
    print(f"  Команда: pyinstaller --onefile --windowed --name=nAUDIT ...")
    print(f"  Всего параметров: {len(cmd)}")
    
    # Запуск PyInstaller
    print("\n[6/7] Запуск PyInstaller (это может занять несколько минут)...")
    print("-" * 70)
    
    try:
        result = subprocess.run(cmd, cwd=str(project_root))
    except Exception as e:
        print(f"\n[!] Ошибка при запуске PyInstaller: {e}")
        return False
    
    print("-" * 70)
    
    # Проверка результата
    print("\n[7/7] Проверка результата...")
    
    exe_path = dist_dir / "nAUDIT.exe"
    
    if exe_path.exists():
        file_size = exe_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        
        print(f"  [OK] Файл успешно создан!")
        print(f"  [OK] Путь: {exe_path}")
        print(f"  [OK] Размер: {file_size_mb:.2f} МБ ({file_size:,} байт)")
        
        print("\n" + "=" * 70)
        print("Сборка завершена успешно!")
        print("=" * 70)
        print(f"\n[OK] Исполняемый файл готов к распространению")
        print(f"[OK] nAUDIT v2.1.0 .exe файл создан: {exe_path}")
        print(f"\nДля запуска приложения:")
        print(f"  - Двойной щелчок по nAUDIT.exe")
        print(f"  - Или выполнить: & '{exe_path}'")
        print(f"\nДля распространения:")
        print(f"  - Скопируйте nAUDIT.exe из папки {dist_dir}")
        print(f"  - Отправьте файл пользователям (размер: {file_size_mb:.0f} МБ)")
        
        return True
    else:
        print(f"  [!] Файл не найден: {exe_path}")
        print(f"  [!] Проверьте вывод выше на предмет ошибок")
        
        print("\n" + "=" * 70)
        print("Сборка завершена с ошибкой!")
        print("=" * 70)
        return False


if __name__ == '__main__':
    try:
        success = build_exe()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[!] Сборка отменена пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
