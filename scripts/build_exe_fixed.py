#!/usr/bin/env python3
"""
Исправленный скрипт для сборки nAUDIT.exe с полной поддержкой всех модулей.
Решает все проблемы с ModuleNotFoundError.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def log(msg, level="INFO"):
    """Логирование с уровнем"""
    levels = {"INFO": "ℹ️ ", "OK": "✅ ", "ERROR": "❌ ", "WARN": "⚠️  "}
    print(f"{levels.get(level, '')} {msg}")


def cleanup_old_builds(project_root):
    """Удаление старых сборок"""
    log("Очистка старых сборок...", "INFO")
    for path in ["build", "dist", "*.spec"]:
        if path.endswith(".spec"):
            spec_file = project_root / "nAUDIT.spec"
            if spec_file.exists():
                spec_file.unlink()
                log(f"  Удалён {spec_file}", "OK")
        else:
            dir_path = project_root / path
            if dir_path.exists():
                shutil.rmtree(dir_path)
                log(f"  Удалена папка {path}/", "OK")


def verify_structure(project_root):
    """Проверка структуры проекта"""
    log("Проверка структуры проекта...", "INFO")
    
    required_files = [
        "n_audit/__init__.py",
        "n_audit/gui/__init__.py",
        "n_audit/gui/main_app.py",
        "n_audit/gui/main_window.py",
        "n_audit/gui/styles.py",
        "n_audit/audit_manager.py",
        "n_audit/core.py",
        "n_audit/code_analysis.py",
        "n_audit/security.py",
        "n_audit/tests_analysis.py",
        "n_audit/infrastructure.py",
        "n_audit/recommendations.py",
        "n_audit/visualizations.py",
        "n_audit/utils.py",
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            log(f"  ✓ {file_path}", "OK")
        else:
            log(f"  ✗ {file_path} - ОТСУТСТВУЕТ!", "ERROR")
            all_exist = False
    
    if not all_exist:
        log("Ошибка: некоторые файлы отсутствуют!", "ERROR")
        return False
    
    return True


def create_build_command(project_root):
    """Создание полной команды PyInstaller с правильными параметрами"""
    
    # Все необходимые скрытые импорты
    hidden_imports = [
        # PyQt6 компоненты
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        
        # Пакеты анализа (только установленные)
        "radon",
        "bandit",
        "safety",
        "sqlfluff",
        "pytest",
        "coverage",
        
        # Служебные пакеты
        "pydantic",
        "networkx",
        "pyvis",
        "matplotlib",
        "dependency_injector",
        
        # Модули n_audit (КРИТИЧНО!)
        "n_audit",
        "n_audit.core",
        "n_audit.code_analysis",
        "n_audit.security",
        "n_audit.tests_analysis",
        "n_audit.infrastructure",
        "n_audit.recommendations",
        "n_audit.visualizations",
        "n_audit.audit_manager",
        "n_audit.utils",
        "n_audit.gui",
        "n_audit.gui.main_app",
        "n_audit.gui.main_window",
        "n_audit.gui.styles",
    ]
    
    # Параметры PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",                            # Один файл
        "--windowed",                           # Без консоли
        "--name=nAUDIT",                        # Имя приложения
        f"--distpath={project_root / 'dist'}",  # Папка вывода
        f"--workpath={project_root / 'build'}", # Папка сборки
        f"--specpath={project_root}",            # Папка .spec файла
        "--noconfirm",                          # Без подтверждения
        "--collect-all=n_audit",                # КЛЮЧЕВОЙ: собрать весь пакет
        "--collect-all=PyQt6",                  # Собрать весь PyQt6
    ]
    
    # Добавить все скрытые импорты
    for hidden_import in hidden_imports:
        cmd.extend(["--hidden-import", hidden_import])
    
    # Добавить данные пакета
    cmd.extend([
        "--add-data", f"{project_root / 'n_audit'}:n_audit",
    ])
    
    # Точка входа
    cmd.append(str(project_root / "n_audit" / "gui" / "main_app.py"))
    
    return cmd


def build_exe(project_root):
    """Собрать .exe файл"""
    log("=" * 70, "INFO")
    log("nAUDIT - Сборка .exe файла (ИСПРАВЛЕННАЯ VERSION)", "INFO")
    log("=" * 70, "INFO")
    
    # 1. Очистка
    cleanup_old_builds(project_root)
    
    # 2. Проверка структуры
    log("\n", "INFO")
    if not verify_structure(project_root):
        return False
    
    # 3. Проверка PyInstaller
    log("\nПроверка PyInstaller...", "INFO")
    try:
        result = subprocess.run(
            ["pyinstaller", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        log(f"  PyInstaller: {result.stdout.strip()}", "OK")
    except Exception as e:
        log(f"  Ошибка: {e}", "ERROR")
        return False
    
    # 4. Сборка
    log("\nСборка приложения...", "INFO")
    cmd = create_build_command(project_root)
    
    log(f"  Команда: pyinstaller [множество параметров] n_audit/gui/main_app.py", "INFO")
    log(f"  Параметры включают:", "INFO")
    log(f"    - --onefile (один файл)", "INFO")
    log(f"    - --collect-all=n_audit (весь пакет)", "INFO")
    log(f"    - --collect-all=PyQt6 (весь PyQt6)", "INFO")
    log(f"    - Множество --hidden-import параметров", "INFO")
    log(f"  Запуск...", "INFO")
    
    try:
        result = subprocess.run(cmd, cwd=project_root, timeout=300)
        if result.returncode != 0:
            log(f"  Ошибка при сборке (код {result.returncode})", "ERROR")
            return False
    except subprocess.TimeoutExpired:
        log("  Сборка заняла слишком много времени (>5 минут)", "ERROR")
        return False
    except Exception as e:
        log(f"  Неожиданная ошибка: {e}", "ERROR")
        return False
    
    # 5. Проверка результата
    log("\nПроверка результата...", "INFO")
    exe_file = project_root / "dist" / "nAUDIT.exe"
    
    if exe_file.exists():
        size_mb = exe_file.stat().st_size / (1024 * 1024)
        log(f"  ✓ Файл создан: {exe_file}", "OK")
        log(f"  ✓ Размер: {size_mb:.2f} МБ", "OK")
    else:
        log(f"  ✗ Файл не найден: {exe_file}", "ERROR")
        return False
    
    # 6. Итоги
    log("\n" + "=" * 70, "INFO")
    log("УСПЕХ! Сборка завершена", "OK")
    log("=" * 70, "INFO")
    log(f"\n✓ Исполняемый файл: {exe_file}", "OK")
    log(f"✓ Размер: {size_mb:.2f} МБ", "OK")
    log("\nДля запуска:", "INFO")
    log(f"  {exe_file}", "INFO")
    log("\nИли двойной клик в файловом менеджере", "INFO")
    
    return True


def main():
    """Главная функция"""
    project_root = Path(__file__).parent.absolute()
    
    # Переходим в папку проекта
    os.chdir(project_root)
    
    success = build_exe(project_root)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
