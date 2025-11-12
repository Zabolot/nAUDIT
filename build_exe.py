"""
Скрипт для сборки .exe файла с помощью PyInstaller.
Создаёт одностоимий исполняемый файл с встроенными зависимостями.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def build_exe():
    """Сборка .exe файла"""
    
    # Определение путей
    project_root = Path(__file__).parent
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    spec_file = project_root / "nAUDIT.spec"
    
    print("=" * 60)
    print("nAUDIT - Сборка .exe файла")
    print("=" * 60)
    
    # Очистка старых сборок
    print("\n[1/5] Очистка старых сборок...")
    for dir_path in [dist_dir, build_dir]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  Удалена папка: {dir_path}")
    
    # Проверка PyInstaller
    print("\n[2/5] Проверка PyInstaller...")
    try:
        result = subprocess.run(["pyinstaller", "--version"], capture_output=True, encoding="utf-8")
        print(f"  PyInstaller версия: {result.stdout.strip()}")
    except FileNotFoundError:
        print("  [!] PyInstaller не установлен!")
        print("  Установите: pip install pyinstaller")
        return False
    
    # Определение точки входа
    entry_point = project_root / "n_audit" / "gui" / "main_app.py"
    if not entry_point.exists():
        print(f"  [!] Файл точки входа не найден: {entry_point}")
        return False
    
    print(f"  Точка входа: {entry_point}")
    
    # Получение дополнительных параметров
    print("\n[3/5] Сборка приложения...")
    
    # Список скрытых импортов (зависимости, которые PyInstaller может не обнаружить)
    hidden_imports = [
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "n_audit.core",
        "n_audit.code_analysis",
        "n_audit.security",
        "n_audit.tests_analysis",
        "n_audit.infrastructure",
        "n_audit.recommendations",
        "n_audit.visualizations",
        "n_audit.audit_manager",
        "n_audit.gui.main_window",
        "n_audit.gui.styles",
    ]
    
    # Построение команды PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",  # Один файл вместо папки
        "--windowed",  # Без консольного окна
        "--name=nAUDIT",  # Имя приложения
        "--icon=NONE",  # Можно добавить иконку
        f"--specpath={project_root}",
        "--distpath", str(dist_dir),
        "--buildpath", str(build_dir),
    ]
    
    # Добавление скрытых импортов
    for hidden_import in hidden_imports:
        cmd.extend(["--hidden-import", hidden_import])
    
    # Добавление точки входа
    cmd.append(str(entry_point))
    
    print(f"  Команда: {' '.join(cmd[:5])}...")
    
    # Запуск PyInstaller
    try:
        result = subprocess.run(cmd, cwd=project_root)
        if result.returncode != 0:
            print("  [!] Ошибка при сборке приложения")
            return False
    except Exception as e:
        print(f"  [!] Ошибка: {e}")
        return False
    
    # Проверка результата
    print("\n[4/5] Проверка результата...")
    exe_file = dist_dir / "nAUDIT.exe"
    
    if exe_file.exists():
        file_size = exe_file.stat().st_size / (1024 * 1024)  # Размер в МБ
        print(f"  ✓ Файл успешно создан: {exe_file}")
        print(f"  ✓ Размер: {file_size:.2f} МБ")
    else:
        print(f"  [!] Файл не найден: {exe_file}")
        return False
    
    # Итоги
    print("\n[5/5] Завершение...")
    print("\n" + "=" * 60)
    print("Сборка завершена успешно!")
    print("=" * 60)
    print(f"\n✓ Исполняемый файл: {exe_file}")
    print(f"✓ Вы можете запустить приложение, дважды щелкнув по файлу")
    print("\nДля распространения скопируйте nAUDIT.exe на целевой компьютер.")
    
    return True


def create_spec_file(project_root):
    """Создание файла спецификации PyInstaller"""
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    [r'{project_root / "n_audit" / "gui" / "main_app.py"}'],
    pathex=[r'{project_root}'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'n_audit.core',
        'n_audit.code_analysis',
        'n_audit.security',
        'n_audit.tests_analysis',
        'n_audit.infrastructure',
        'n_audit.recommendations',
        'n_audit.visualizations',
        'n_audit.audit_manager',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='nAUDIT',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    return spec_content


if __name__ == "__main__":
    success = build_exe()
    sys.exit(0 if success else 1)
