"""
Модуль проверки инфраструктуры и окружения.
Анализирует Docker, зависимости, переменные окружения и т.д.
"""

import os
import json
import subprocess
import glob
from n_audit import utils


def run(args, reports_dir, configs_dir):
    """Запуск проверок инфраструктуры"""
    print("[*] Проверка инфраструктуры и окружения...")

    # Сохранение зависимостей
    _save_requirements(configs_dir)

    # Проверка конфигурационных файлов
    _check_configuration_files(args, reports_dir, configs_dir)

    # Проверка Docker
    _check_docker(args, reports_dir, configs_dir)

    # Проверка SQL файлов
    _check_sql_files(args, reports_dir)

    # Сохранение информации об окружении
    _save_environment_info(configs_dir)

    print("[✓] Проверка инфраструктуры завершена")


def _save_requirements(configs_dir):
    """Сохранение снимка зависимостей"""
    print("  [*] Сохранение зависимостей...")
    try:
        result = subprocess.run(
            ["pip", "freeze"],
            capture_output=True,
            encoding="utf-8",
            timeout=30
        )

        with open(f"{configs_dir}/requirements_snapshot.txt", "w", encoding="utf-8") as f:
            f.write(result.stdout)

        lines = result.stdout.strip().split("\n")
        print(f"  [✓] Найдено {len(lines)} установленных пакетов")

    except Exception as e:
        print(f"  [!] Ошибка при сохранении зависимостей: {e}")


def _check_configuration_files(args, reports_dir, configs_dir):
    """Проверка конфигурационных файлов проекта"""
    print("  [*] Проверка конфигурационных файлов...")

    config_patterns = [
        "*.yml", "*.yaml",
        "*.toml",
        "*.ini",
        "*.conf",
        ".env*",
        "Dockerfile",
        "docker-compose.yml",
        "requirements*.txt",
        "setup.py",
        "setup.cfg"
    ]

    found_configs = []
    for pattern in config_patterns:
        for root, dirs, files in os.walk(args.module):
            for file in files:
                if file.lower().startswith(pattern.split("*")[0]) or file.lower().endswith(pattern.split("*")[-1]):
                    found_configs.append(os.path.join(root, file))

    config_report = {
        "found_configs": found_configs[:20],  # Первые 20
        "total_configs": len(found_configs)
    }

    with open(f"{configs_dir}/config_files.json", "w", encoding="utf-8") as f:
        json.dump(config_report, f, ensure_ascii=False, indent=2)

    print(f"  [✓] Найдено {len(found_configs)} файлов конфигурации")


def _check_docker(args, reports_dir, configs_dir):
    """Проверка Docker конфигурации"""
    print("  [*] Проверка Docker...")

    if not utils.check_command("docker"):
        print("  [!] Docker не установлен")
        return

    docker_report = {"installed": True, "images": [], "containers": []}

    try:
        # Информация об образах
        images_result = subprocess.run(
            ["docker", "images", "--format", "json"],
            capture_output=True,
            encoding="utf-8",
            timeout=30
        )

        if images_result.returncode == 0 and images_result.stdout.strip():
            try:
                images = [json.loads(line) for line in images_result.stdout.strip().split("\n")]
                docker_report["images"] = images[:10]  # Первые 10
            except json.JSONDecodeError:
                pass

        # Информация о контейнерах
        containers_result = subprocess.run(
            ["docker", "ps", "-a", "--format", "json"],
            capture_output=True,
            encoding="utf-8",
            timeout=30
        )

        if containers_result.returncode == 0 and containers_result.stdout.strip():
            try:
                containers = [json.loads(line) for line in containers_result.stdout.strip().split("\n")]
                docker_report["containers"] = containers[:10]  # Первые 10
            except json.JSONDecodeError:
                pass

        with open(f"{configs_dir}/docker_info.json", "w", encoding="utf-8") as f:
            json.dump(docker_report, f, ensure_ascii=False, indent=2)

        print(f"  [✓] Docker: {len(docker_report['images'])} образов, "
              f"{len(docker_report['containers'])} контейнеров")

    except subprocess.TimeoutExpired:
        print("  [!] Docker проверка превысила время выполнения")
    except Exception as e:
        print(f"  [!] Ошибка Docker: {e}")


def _check_sql_files(args, reports_dir):
    """Проверка SQL файлов с sqlfluff"""
    print("  [*] Проверка SQL файлов...")

    if not utils.check_command("sqlfluff"):
        print("  [!] sqlfluff не установлен")
        return

    # Поиск SQL файлов
    sql_files = []
    for root, dirs, files in os.walk(args.module):
        for file in files:
            if file.endswith(".sql"):
                sql_files.append(os.path.join(root, file))

    if not sql_files:
        print("  [!] SQL файлы не найдены")
        return

    try:
        result = subprocess.run(
            ["sqlfluff", "lint", *sql_files, "--format", "json"],
            capture_output=True,
            encoding="utf-8",
            timeout=60
        )

        sql_report = {"files_checked": len(sql_files), "issues": []}

        if result.stdout.strip():
            try:
                sql_issues = json.loads(result.stdout)
                sql_report["issues"] = sql_issues
            except json.JSONDecodeError:
                pass

        with open(f"{reports_dir}/sql_analysis.json", "w", encoding="utf-8") as f:
            json.dump(sql_report, f, ensure_ascii=False, indent=2)

        print(f"  [✓] sqlfluff: проверено {len(sql_files)} SQL файлов")

    except subprocess.TimeoutExpired:
        print("  [!] sqlfluff превысил время выполнения")
    except FileNotFoundError:
        print("  [!] sqlfluff не установлен")
    except Exception as e:
        print(f"  [!] Ошибка sqlfluff: {e}")


def _save_environment_info(configs_dir):
    """Сохранение информации об окружении"""
    print("  [*] Сохранение информации об окружении...")

    import platform
    import sys

    env_info = {
        "platform": platform.platform(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "environment_variables": {
            k: v for k, v in os.environ.items()
            if k.upper() in ["PYTHONPATH", "VIRTUAL_ENV", "PATH_PREFIX"]
        }
    }

    with open(f"{configs_dir}/environment_info.json", "w", encoding="utf-8") as f:
        json.dump(env_info, f, ensure_ascii=False, indent=2)

    print(f"  [✓] Python {sys.version.split()[0]} на {platform.system()}")