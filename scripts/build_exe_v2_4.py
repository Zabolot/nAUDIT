#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для построения nAUDIT v2.4 .exe - ФИКСИРОВАННЫЙ
Используется run_naudit_gui.py как точка входа (как в v4)
Добавлены улучшения:
- Синхронизация граф ↔ дерево
- QWebChannel для фокуса на узлы
- Оптимизация для больших проектов
- Плавные переходы
"""

import sys
import subprocess
from pathlib import Path
import shutil


def build_exe():
    """Построить .exe"""
    print("[*] Собираю nAUDIT v2.4 executable...")
    
    # Путь к проекту
    project_root = Path(__file__).parent
    
    # Точка входа (ключевое улучшение - используем run_naudit_gui.py)
    entry_point = project_root / "run_naudit_gui.py"
    
    if not entry_point.exists():
        print(f"[✗] Точка входа не найдена: {entry_point}")
        return False
    
    # Полный путь к n_audit модулю
    n_audit_path = project_root / "n_audit"
    if not n_audit_path.exists():
        print(f"[✗] Модуль n_audit не найден: {n_audit_path}")
        return False
    
    # Пути для сборки
    build_dir = project_root / 'build_v2_4'
    dist_dir = project_root / 'dist'
    work_dir = build_dir / 'work'
    
    # Очищаем старые сборки
    exe_name = 'nAUDIT.exe'
    exe_path = dist_dir / exe_name
    
    if exe_path.exists():
        print(f"[*] Удаляю старую версию: {exe_name}")
        try:
            exe_path.unlink()
        except Exception as e:
            print(f"[!] Не удалось удалить: {e}")
    
    if work_dir.exists():
        print("[*] Очищаю рабочую папку...")
        shutil.rmtree(work_dir, ignore_errors=True)
    
    # Создаём папку dist если её нет
    dist_dir.mkdir(exist_ok=True)
    build_dir.mkdir(exist_ok=True)
    
    # Команда PyInstaller
    cmd = [
        'pyinstaller',
        '--onefile',                              # Один файл
        '--windowed',                             # БЕЗ консоли (GUI приложение)
        '--name=nAUDIT',                          # Имя exe
        f'--distpath={dist_dir}',                 # Путь для exe
        f'--workpath={work_dir}',                 # Рабочая папка
        f'--specpath={build_dir}',
        
        # Данные
        f'--add-data={n_audit_path}:n_audit',
        f'--add-data={project_root / "assets"}:assets',
        
        # Скрытые импорты (PyQt6)
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtGui',
        '--hidden-import=PyQt6.QtWidgets',
        '--hidden-import=PyQt6.QtWebEngineWidgets',
        '--hidden-import=PyQt6.QtWebChannel',      # ВАЖНО для QWebChannel
        
        # Графики и визуализация
        '--hidden-import=matplotlib.backends.backend_qt5agg',
        '--hidden-import=matplotlib.figure',
        '--hidden-import=matplotlib.pyplot',
        '--hidden-import=matplotlib.axes',
        
        # Анализ кода
        '--hidden-import=pylint.lint',
        '--hidden-import=flake8.api.legacy',
        
        # Граф библиотеки
        '--hidden-import=plotly',
        '--hidden-import=plotly.graph_objects',
        '--hidden-import=plotly.express',
        '--hidden-import=pyvis',
        '--hidden-import=pyvis.network',
        '--hidden-import=networkx',
        '--hidden-import=jinja2',
        '--collect-all=pyvis',
        
        # Сбор необходимых данных
        '--collect-all=PyQt6',
        '--collect-all=matplotlib',
        '--collect-all=plotly',
        
        # Оптимизация размера
        '--noupx',                                # Без UPX сжатия
        '--log-level=INFO',
        
        str(entry_point),
    ]
    
    print(f"[*] Точка входа: {entry_point}")
    print(f"[*] Выходной файл: {exe_path}")
    print(f"[*] Режим: --onefile --windowed")
    print()
    
    print("[*] Запускаю PyInstaller...")
    print("[*] (это может занять несколько минут)")
    print("-" * 80)
    
    result = subprocess.run(cmd)
    
    print("-" * 80)
    print()
    
    if result.returncode == 0:
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"[✓] УСПЕШНО!")
            print(f"[✓] Файл: {exe_path.name}")
            print(f"[✓] Размер: {size_mb:.1f} MB")
            print()
            print(f"Запуск: {exe_path}")
            return True
        else:
            print(f"[✗] Файл не создан")
            return False
    else:
        print(f"[✗] Ошибка сборки (код: {result.returncode})")
        return False


if __name__ == '__main__':
    success = build_exe()
    sys.exit(0 if success else 1)
