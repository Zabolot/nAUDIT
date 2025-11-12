"""
Модуль проверки безопасности кода.
Использует bandit, safety и другие инструменты для выявления уязвимостей.
"""

import json
import subprocess
import os


def run(args, reports_dir):
    """Запуск всех проверок безопасности"""
    print("[*] Запуск проверки безопасности...")

    # Запуск bandit
    _run_bandit_check(args, reports_dir)

    # Запуск safety
    _run_safety_check(reports_dir)

    print("[✓] Проверка безопасности завершена")


def _run_bandit_check(args, reports_dir):
    """Проверка безопасности с bandit"""
    print("  [*] Сканирование с bandit...")
    try:
        result = subprocess.run(
            ["bandit", "-r", args.module, "-f", "json", "-o", f"{reports_dir}/security_issues.json"],
            capture_output=True,
            encoding="utf-8",
            timeout=120
        )

        # Чтение результатов
        if os.path.exists(f"{reports_dir}/security_issues.json"):
            try:
                with open(f"{reports_dir}/security_issues.json", "r", encoding="utf-8") as f:
                    security_data = json.load(f)

                issues = security_data.get("results", [])
                metrics = security_data.get("metrics", {})

                high_severity = sum(1 for i in issues if i.get("severity") == "HIGH")
                medium_severity = sum(1 for i in issues if i.get("severity") == "MEDIUM")
                low_severity = sum(1 for i in issues if i.get("severity") == "LOW")

                print(f"  [✓] bandit: обнаружено проблем безопасности:")
                print(f"      - ВЫСОКИЙ приоритет: {high_severity}")
                print(f"      - СРЕДНИЙ приоритет: {medium_severity}")
                print(f"      - НИЗКИЙ приоритет: {low_severity}")
            except json.JSONDecodeError:
                print("  [!] Не удалось распарсить результаты bandit")
        else:
            print("  [!] Результаты bandit не найдены")

    except subprocess.TimeoutExpired:
        print("  [!] bandit превысил время выполнения")
    except FileNotFoundError:
        print("  [!] bandit не установлен. Установите: pip install bandit")
    except Exception as e:
        print(f"  [!] Ошибка bandit: {e}")


def _run_safety_check(reports_dir):
    """Проверка уязвимостей зависимостей с safety"""
    print("  [*] Проверка уязвимостей в зависимостях (safety)...")
    try:
        result = subprocess.run(
            ["safety", "check", "--json"],
            capture_output=True,
            encoding="utf-8",
            timeout=60
        )

        vulnerabilities = []
        if result.stdout.strip():
            try:
                vulnerabilities = json.loads(result.stdout) if result.stdout.strip() else []
            except json.JSONDecodeError:
                vulnerabilities = []

        with open(f"{reports_dir}/vulnerabilities.json", "w", encoding="utf-8") as f:
            json.dump({
                "vulnerabilities": vulnerabilities,
                "count": len(vulnerabilities)
            }, f, ensure_ascii=False, indent=2)

        if vulnerabilities:
            print(f"  [!] Обнаружено {len(vulnerabilities)} уязвимостей в зависимостях")
        else:
            print("  [✓] Уязвимостей в зависимостях не найдено")

    except subprocess.TimeoutExpired:
        print("  [!] safety превысил время выполнения")
    except FileNotFoundError:
        print("  [!] safety не установлен. Установите: pip install safety")
    except Exception as e:
        print(f"  [!] Ошибка safety: {e}")


def _run_gitleaks_check(args, reports_dir):
    """Проверка утечек секретов с gitleaks"""
    print("  [*] Проверка утечек секретов (gitleaks)...")
    try:
        result = subprocess.run(
            ["gitleaks", "detect", "--source", args.module, "--report-format", "json",
             "--report-path", f"{reports_dir}/gitleaks_report.json"],
            capture_output=True,
            encoding="utf-8",
            timeout=60
        )

        if os.path.exists(f"{reports_dir}/gitleaks_report.json"):
            print("  [✓] gitleaks: проверка завершена")
        else:
            print("  [!] gitleaks: результаты не найдены")

    except subprocess.TimeoutExpired:
        print("  [!] gitleaks превысил время выполнения")
    except FileNotFoundError:
        print("  [!] gitleaks не установлен")
    except Exception as e:
        print(f"  [!] Ошибка gitleaks: {e}")