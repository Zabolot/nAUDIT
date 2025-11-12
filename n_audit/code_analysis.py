"""
Модуль статического анализа кода.
Выполняет проверку с использованием radon, pylint, mypy и других инструментов.
"""

import json
import subprocess
import os


def run(args, reports_dir):
    """Запуск всех проверок статического анализа кода"""
    print("[*] Запуск статического анализа кода...")

    # Запуск radon для анализа цикломатической сложности
    _run_radon_analysis(args, reports_dir)

    # Запуск pylint для анализа стиля и ошибок
    _run_pylint_analysis(args, reports_dir)

    # Запуск flake8 для проверки стиля
    _run_flake8_analysis(args, reports_dir)

    # Запуск mypy для проверки типов
    _run_mypy_analysis(args, reports_dir)

    print("[✓] Статический анализ завершён")


def _run_radon_analysis(args, reports_dir):
    """Анализ цикломатической сложности с radon"""
    print("  [*] Анализ цикломатической сложности (radon)...")
    try:
        result = subprocess.run(
            ["python", "-m", "radon", "cc", args.module, "--json"],
            capture_output=True,
            encoding="utf-8",
            timeout=60
        )

        complexity_data = {}
        if result.returncode == 0 and result.stdout.strip():
            try:
                complexity_data = json.loads(result.stdout)
                with open(f"{reports_dir}/cyclomatic_complexity_full.json", "w", encoding="utf-8") as f:
                    json.dump(complexity_data, f, ensure_ascii=False, indent=2)

                # Анализ сложности
                high_complexity_items = []
                for file, metrics in complexity_data.items():
                    if isinstance(metrics, dict):
                        for func_name, func_metrics in metrics.items():
                            if isinstance(func_metrics, dict):
                                complexity = func_metrics.get('complexity', 0)
                                if complexity > 8:  # Высокая сложность
                                    high_complexity_items.append({
                                        "file": file,
                                        "function": func_name,
                                        "complexity": complexity
                                    })

                print(f"  [✓] Найдено функций с высокой сложностью: {len(high_complexity_items)}")
            except json.JSONDecodeError:
                print("  [!] Не удалось распарсить вывод radon")
        else:
            print("  [!] radon не выдал результатов")

    except subprocess.TimeoutExpired:
        print("  [!] radon превысил время выполнения")
    except FileNotFoundError:
        print("  [!] radon не установлен. Установите: pip install radon")
    except Exception as e:
        print(f"  [!] Ошибка radon: {e}")


def _run_pylint_analysis(args, reports_dir):
    """Анализ стиля и ошибок с pylint"""
    print("  [*] Анализ кода (pylint)...")
    try:
        result = subprocess.run(
            ["python", "-m", "pylint", args.module, "--output-format=json"],
            capture_output=True,
            encoding="utf-8",
            timeout=120
        )

        if result.stdout.strip():
            try:
                issues = json.loads(result.stdout) if result.stdout.strip() else []
                with open(f"{reports_dir}/pylint_full.json", "w", encoding="utf-8") as f:
                    json.dump(issues, f, ensure_ascii=False, indent=2)

                # Подсчёт по типам
                error_count = sum(1 for i in issues if i.get("type") == "error")
                warning_count = sum(1 for i in issues if i.get("type") == "warning")
                convention_count = sum(1 for i in issues if i.get("type") == "convention")

                print(f"  [✓] pylint: ошибок={error_count}, предупреждений={warning_count}, "
                      f"нарушения стиля={convention_count}")
            except json.JSONDecodeError:
                print("  [!] Не удалось распарсить вывод pylint")
        else:
            print("  [✓] pylint: проблем не найдено")

    except subprocess.TimeoutExpired:
        print("  [!] pylint превысил время выполнения")
    except FileNotFoundError:
        print("  [!] pylint не установлен. Установите: pip install pylint")
    except Exception as e:
        print(f"  [!] Ошибка pylint: {e}")


def _run_flake8_analysis(args, reports_dir):
    """Анализ стиля с flake8"""
    print("  [*] Проверка стиля кода (flake8)...")
    try:
        result = subprocess.run(
            ["python", "-m", "flake8", args.module, "--format=json"],
            capture_output=True,
            encoding="utf-8",
            timeout=60
        )

        flake8_issues = []
        if result.stdout.strip():
            try:
                flake8_issues = json.loads(result.stdout) if result.stdout.strip() else []
                with open(f"{reports_dir}/flake8_report.json", "w", encoding="utf-8") as f:
                    json.dump(flake8_issues, f, ensure_ascii=False, indent=2)
                print(f"  [✓] flake8: обнаружено {len(flake8_issues)} проблем со стилем")
            except json.JSONDecodeError:
                print("  [!] Не удалось распарсить вывод flake8")
        else:
            print("  [✓] flake8: проблем не найдено")

    except subprocess.TimeoutExpired:
        print("  [!] flake8 превысил время выполнения")
    except FileNotFoundError:
        print("  [!] flake8 не установлен. Установите: pip install flake8")
    except Exception as e:
        print(f"  [!] Ошибка flake8: {e}")


def _run_mypy_analysis(args, reports_dir):
    """Анализ типов с mypy"""
    print("  [*] Проверка типов (mypy)...")
    try:
        result = subprocess.run(
            ["python", "-m", "mypy", args.module, "--json-report", reports_dir, "--no-error-summary"],
            capture_output=True,
            encoding="utf-8",
            timeout=60
        )

        if result.returncode == 0:
            print("  [✓] mypy: проблем с типами не найдено")
        else:
            print(f"  [!] mypy обнаружил проблемы с типами (код выхода: {result.returncode})")

    except subprocess.TimeoutExpired:
        print("  [!] mypy превысил время выполнения")
    except FileNotFoundError:
        print("  [!] mypy не установлен. Установите: pip install mypy")
    except Exception as e:
        print(f"  [!] Ошибка mypy: {e}")