"""
Модуль анализа тестового покрытия.
Использует pytest и coverage для анализа тестов.
"""

import json
import subprocess
import os
import xml.etree.ElementTree as ET


def run(args, reports_dir):
    """Запуск анализа тестового покрытия"""
    print("[*] Запуск анализа тестового покрытия...")

    # Запуск pytest с coverage
    _run_pytest_coverage(args, reports_dir)

    # Анализ результатов
    _analyze_coverage_results(reports_dir)

    print("[✓] Анализ тестов завершён")


def _run_pytest_coverage(args, reports_dir):
    """Запуск pytest с анализом покрытия"""
    print("  [*] Запуск тестов с coverage...")

    try:
        # Проверка наличия тестов
        test_dir = os.path.join(args.module, "tests")
        if not os.path.exists(test_dir):
            print("  [!] Директория tests не найдена")
            return

        # Запуск coverage и pytest
        coverage_run = subprocess.run(
            ["coverage", "run", "-m", "pytest", test_dir, "-v", "--tb=short"],
            capture_output=True,
            encoding="utf-8",
            timeout=300
        )

        if coverage_run.returncode in (0, 1):  # 0 = успех, 1 = есть ошибки в тестах
            # Генерация отчёта coverage в JSON
            coverage_json = subprocess.run(
                ["coverage", "json", "-o", f"{reports_dir}/coverage_report.json"],
                capture_output=True,
                encoding="utf-8",
                timeout=60
            )

            # Генерация HTML отчёта
            coverage_html = subprocess.run(
                ["coverage", "html", "-d", f"{reports_dir}/coverage_html"],
                capture_output=True,
                encoding="utf-8",
                timeout=60
            )

            # Вывод отчёта coverage
            coverage_report = subprocess.run(
                ["coverage", "report"],
                capture_output=True,
                encoding="utf-8",
                timeout=60
            )

            # Сохранение результатов
            with open(f"{reports_dir}/tests_results.log", "w", encoding="utf-8") as f:
                f.write(coverage_run.stdout)
                f.write("\n\n=== Coverage Report ===\n")
                f.write(coverage_report.stdout)

            # Парсинг результатов
            if coverage_run.stdout:
                test_count = coverage_run.stdout.count(" PASSED") + coverage_run.stdout.count(" FAILED")
                passed_count = coverage_run.stdout.count(" PASSED")
                failed_count = coverage_run.stdout.count(" FAILED")

                print(f"  [✓] pytest: всего тестов={test_count}, пройдено={passed_count}, "
                      f"ошибок={failed_count}")

        else:
            print("  [!] pytest завершился с ошибкой")

    except subprocess.TimeoutExpired:
        print("  [!] pytest превысил время выполнения")
    except FileNotFoundError:
        print("  [!] pytest или coverage не установлены. Установите: pip install pytest coverage")
    except Exception as e:
        print(f"  [!] Ошибка pytest: {e}")


def _analyze_coverage_results(reports_dir):
    """Анализ результатов coverage"""
    print("  [*] Анализ результатов покрытия...")

    coverage_file = os.path.join(reports_dir, "coverage_report.json")
    if not os.path.exists(coverage_file):
        print("  [!] Файл покрытия не найден")
        return

    try:
        with open(coverage_file, "r", encoding="utf-8") as f:
            coverage_data = json.load(f)

        # Получение общего процента покрытия
        total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)
        total_lines = coverage_data.get("totals", {}).get("num_statements", 0)
        covered_lines = coverage_data.get("totals", {}).get("covered_lines", 0)

        print(f"  [✓] Общее покрытие: {total_coverage:.1f}% ({covered_lines}/{total_lines} строк)")

        # Анализ покрытия по файлам
        files = coverage_data.get("files", {})
        low_coverage_files = []
        for file_path, file_data in files.items():
            file_coverage = file_data.get("summary", {}).get("percent_covered", 0)
            if file_coverage < 50:
                low_coverage_files.append((file_path, file_coverage))

        if low_coverage_files:
            print(f"  [!] Файлы с низким покрытием (< 50%):")
            for file_path, coverage in low_coverage_files[:5]:
                print(f"      - {file_path}: {coverage:.1f}%")

    except json.JSONDecodeError:
        print("  [!] Не удалось распарсить файл покрытия")
    except Exception as e:
        print(f"  [!] Ошибка анализа покрытия: {e}")