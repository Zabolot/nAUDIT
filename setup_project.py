#!/usr/bin/env python3
"""
Скрипт инициализации и быстрой установки nAUDIT
Выполняет все необходимые настройки для первого запуска
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def setup_project():
    """Полная настройка проекта"""
    
    print("=" * 70)
    print("🔧 nAUDIT 2.0 — Инициализация проекта")
    print("=" * 70)
    
    project_root = Path(__file__).parent
    
    # Шаг 1: Проверка Python версии
    print("\n[1/5] Проверка Python версии...")
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print(f"  ❌ Требуется Python 3.8+, найдена версия {python_version.major}.{python_version.minor}")
        return False
    print(f"  ✓ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Шаг 2: Создание виртуального окружения
    print("\n[2/5] Подготовка виртуального окружения...")
    venv_path = project_root / "v.naudit"
    if not venv_path.exists():
        print("  Создание виртуального окружения...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print(f"  ✓ Виртуальное окружение создано: {venv_path}")
    else:
        print(f"  ✓ Виртуальное окружение уже существует: {venv_path}")
    
    # Шаг 3: Установка зависимостей
    print("\n[3/5] Установка зависимостей...")
    
    requirements_file = project_root / "requirements.txt"
    if requirements_file.exists():
        print(f"  Установка из {requirements_file}...")
        # Определение pip для текущей платформы
        if sys.platform == "win32":
            pip_exe = venv_path / "Scripts" / "pip.exe"
        else:
            pip_exe = venv_path / "bin" / "pip"
        
        try:
            subprocess.run([str(pip_exe), "install", "--upgrade", "pip"], check=True)
            subprocess.run([str(pip_exe), "install", "-r", str(requirements_file)], check=True)
            print("  ✓ Зависимости установлены успешно")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Ошибка установки зависимостей: {e}")
            return False
    else:
        print(f"  ⚠️  Файл {requirements_file} не найден")
    
    # Шаг 4: Установка пакета в режиме разработки
    print("\n[4/5] Установка пакета nAUDIT...")
    try:
        if sys.platform == "win32":
            pip_exe = venv_path / "Scripts" / "pip.exe"
        else:
            pip_exe = venv_path / "bin" / "pip"
        
        subprocess.run([str(pip_exe), "install", "-e", "."], cwd=str(project_root), check=True)
        print("  ✓ Пакет установлен в режиме разработки")
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Ошибка установки пакета: {e}")
        return False
    
    # Шаг 5: Проверка установки
    print("\n[5/5] Проверка установки...")
    
    # Проверка GUI
    try:
        if sys.platform == "win32":
            python_exe = venv_path / "Scripts" / "python.exe"
        else:
            python_exe = venv_path / "bin" / "python"
        
        result = subprocess.run(
            [str(python_exe), "-c", "from n_audit.gui.main_app import main; print('✓ GUI OK')"],
            capture_output=True,
            encoding="utf-8",
            timeout=5
        )
        
        if result.returncode == 0:
            print("  " + result.stdout.strip())
        else:
            print(f"  ❌ Ошибка: {result.stderr}")
    except Exception as e:
        print(f"  ⚠️  Не удалось проверить GUI: {e}")
    
    # Финальный отчёт
    print("\n" + "=" * 70)
    print("✅ Инициализация завершена успешно!")
    print("=" * 70)
    
    print("\n📍 Следующие шаги:")
    print("\n1️⃣  Запуск GUI приложения:")
    
    if sys.platform == "win32":
        print(f"   .\\v.naudit\\Scripts\\python.exe -m n_audit.gui.main_app")
    else:
        print(f"   ./v.naudit/bin/python -m n_audit.gui.main_app")
    
    print("\n2️⃣  Или используйте команду (если путь в PATH):")
    print("   naudit-gui")
    
    print("\n3️⃣  Сборка .exe файла (Windows):")
    print("   .\\build_exe.ps1")
    
    print("\n📖 Документация:")
    print(f"   - Руководство пользователя: {project_root / 'docs' / 'USER_GUIDE.md'}")
    print(f"   - Техническая документация: {project_root / 'docs' / 'TECH_GUIDE.md'}")
    
    print("\n" + "=" * 70)
    
    return True


if __name__ == "__main__":
    try:
        success = setup_project()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Инициализация отменена пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
