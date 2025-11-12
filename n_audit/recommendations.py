"""
Модуль генерации рекомендаций на основе результатов аудита.
"""

import json
import os


def generate_advices(reports_dir):
    """
    Генерирует рекомендации на основе результатов аудита.
    Анализирует отчёты и предлагает конкретные действия.
    """
    recommendations = []

    # Анализ результатов кода
    code_issues = _analyze_code_issues(reports_dir)
    recommendations.extend(code_issues)

    # Анализ проблем безопасности
    security_issues = _analyze_security_issues(reports_dir)
    recommendations.extend(security_issues)

    # Анализ тестов
    test_issues = _analyze_test_coverage(reports_dir)
    recommendations.extend(test_issues)

    # Общие рекомендации
    general_recommendations = [
        "Регулярно проводите аудит кода для отслеживания изменений качества",
        "Используйте pre-commit hooks для автоматической проверки кода перед коммитом",
        "Поддерживайте актуальность документации вместе с кодом",
        "Внедрите CI/CD pipeline для автоматизации проверок качества",
        "Проводите регулярные code review между разработчиками",
    ]
    recommendations.extend(general_recommendations)

    return "\n".join([f"• {rec}" for rec in recommendations])


def _analyze_code_issues(reports_dir) -> list:
    """Анализ проблем кода на основе pylint отчётов"""
    recommendations = []
    pylint_file = os.path.join(reports_dir, "pylint_full.json")

    if not os.path.exists(pylint_file):
        return recommendations

    try:
        with open(pylint_file, "r", encoding="utf-8") as f:
            issues = json.load(f)

        if not isinstance(issues, list):
            return recommendations

        # Подсчёт типов ошибок
        error_count = sum(1 for i in issues if i.get("type") == "error")
        warning_count = sum(1 for i in issues if i.get("type") == "warning")
        convention_count = sum(1 for i in issues if i.get("type") == "convention")

        if error_count > 0:
            recommendations.append(
                f"Исправьте {error_count} критических ошибок pylint, которые могут привести к сбоям"
            )

        if warning_count > 0:
            recommendations.append(
                f"Обратите внимание на {warning_count} предупреждений pylint"
            )

        if convention_count > 10:
            recommendations.append(
                "Приведите код в соответствие со стандартом PEP8 (более 10 нарушений стиля)"
            )

        # Анализ цикломатической сложности
        cc_file = os.path.join(reports_dir, "cyclomatic_complexity_full.json")
        if os.path.exists(cc_file):
            with open(cc_file, "r", encoding="utf-8") as f:
                cc_data = json.load(f)

            high_complexity_count = 0
            for file_data in cc_data.values():
                if isinstance(file_data, dict):
                    for func_data in file_data.values():
                        if isinstance(func_data, dict) and func_data.get("complexity", 0) > 8:
                            high_complexity_count += 1

            if high_complexity_count > 0:
                recommendations.append(
                    f"Рефакторьте {high_complexity_count} функций с высокой цикломатической сложностью (> 8)"
                )

    except json.JSONDecodeError:
        pass
    except Exception as e:
        print(f"Ошибка анализа кода: {e}")

    return recommendations


def _analyze_security_issues(reports_dir) -> list:
    """Анализ проблем безопасности на основе bandit и safety отчётов"""
    recommendations = []

    # Анализ bandit отчёта
    security_file = os.path.join(reports_dir, "security_issues.json")
    if os.path.exists(security_file):
        try:
            with open(security_file, "r", encoding="utf-8") as f:
                security_data = json.load(f)

            issues = security_data.get("results", [])
            high_severity = sum(1 for i in issues if i.get("severity") == "HIGH")
            medium_severity = sum(1 for i in issues if i.get("severity") == "MEDIUM")

            if high_severity > 0:
                recommendations.append(
                    f"СРОЧНО: Исправьте {high_severity} критических проблем безопасности"
                )

            if medium_severity > 0:
                recommendations.append(
                    f"Устраните {medium_severity} проблем безопасности средней важности"
                )

        except json.JSONDecodeError:
            pass
        except Exception as e:
            print(f"Ошибка анализа безопасности: {e}")

    # Анализ safety отчёта
    vuln_file = os.path.join(reports_dir, "vulnerabilities.json")
    if os.path.exists(vuln_file):
        try:
            with open(vuln_file, "r", encoding="utf-8") as f:
                vuln_data = json.load(f)

            vuln_count = len(vuln_data.get("vulnerabilities", []))
            if vuln_count > 0:
                recommendations.append(
                    f"Обновите зависимости: обнаружено {vuln_count} уязвимостей"
                )

        except json.JSONDecodeError:
            pass
        except Exception as e:
            print(f"Ошибка анализа уязвимостей: {e}")

    return recommendations


def _analyze_test_coverage(reports_dir) -> list:
    """Анализ тестового покрытия"""
    recommendations = []

    # Здесь можно добавить анализ результатов coverage
    recommendations.append("Стремитесь к минимум 80% покрытию кода тестами")
    recommendations.append("Добавьте больше unit-тестов для критических функций")

    return recommendations