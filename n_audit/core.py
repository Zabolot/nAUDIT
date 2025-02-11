import os
from n_audit import code_analysis, security, tests_analysis, infrastructure, recommendations, utils
import json

from . import visualizations

RESULTS_DIR = "audit_results"
REPORTS_DIR = os.path.join(RESULTS_DIR, "reports")
CONFIGS_DIR = os.path.join(RESULTS_DIR, "configs")

def setup_directories():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(CONFIGS_DIR, exist_ok=True)

def run_all_checks(args):
    if args.verbose:
        print("[VERBOSE] Запуск полного аудита проекта.")
    else:
        print("[*] Инициализация аудита")
    setup_directories()
    
    # Вывод стартовой анимации (0%)
    visualizations.display_cat_animation(0)
    
    # Проверка наличия внешних команд
    external_cmds = ["dot", "inspect4py", "safety", "gitleaks", "ag", "sqlfluff", "cyclonedx-py"]
    for cmd in external_cmds:
        if not utils.check_command(cmd):
            print(f"[WARNING] Не найдена утилита '{cmd}'. Рекомендуется установить её через пакетный менеджер системы.")
    
    # Запуск модулей анализа с обновлением анимации
    code_analysis.run(args, REPORTS_DIR)
    visualizations.display_cat_animation(20)
    
    security.run(args, REPORTS_DIR)
    visualizations.display_cat_animation(40)
    
    tests_analysis.run(args, REPORTS_DIR)
    visualizations.display_cat_animation(60)
    
    infrastructure.run(args, REPORTS_DIR, CONFIGS_DIR)
    visualizations.display_cat_animation(80)
    
    visualizations.generate_visualizations(REPORTS_DIR)
    visualizations.display_cat_animation(90)
    
    # Генерация рекомендаций
    recs = recommendations.generate_advices(REPORTS_DIR)
    generate_report(args.report_level, args.export_format, REPORTS_DIR, recs, args.verbose)
    
    # Финальная анимация - полный прогресс
    visualizations.display_cat_animation(100)
    print(f"[*] Отчёт аудита сформирован. Результаты сохранены в папке {RESULTS_DIR}")

def generate_report(report_level, export_format, reports_dir, recommendations_text, verbose):
    report_path = os.path.join(reports_dir, "full_report.md")
    if export_format == "html":
        content = (
            "<html><head><meta charset='utf-8'><title>Отчёт аудита nAUDIT</title></head><body>\n"
            "<h1>Отчёт аудита nAUDIT</h1>\n"
            "<h2>Основные метрики</h2>\n"
            "<ul>\n"
            "<li>Статический анализ кода завершён</li>\n"
            "<li>Проверка безопасности проведена</li>\n"
            "<li>Анализ тестового покрытия выполнен</li>\n"
            "<li>Проверка инфраструктуры выполнена</li>\n"
            "</ul>\n"
        )
        if report_level in ("full", "detailed"):
            content += "<h2>Детализированный отчёт</h2>\n<p>Содержимое логов анализа см. в отдельных файлах.</p>\n"
        content += (
            "<h2>Рекомендации по улучшению проекта</h2>\n"
            f"<p>{recommendations_text.replace(chr(10), '<br>')}</p>\n"
        )
        if report_level == "detailed":
            content += (
                "<h2>Дополнительные советы для начинающих</h2>\n"
                "<ul>\n"
                "<li>Используйте виртуальные окружения для каждого проекта</li>\n"
                "<li>Регулярно проводите статический анализ кода</li>\n"
                "<li>Следуйте стандартам PEP8</li>\n"
                "<li>Пишите тесты для каждого функционального блока</li>\n"
                "</ul>\n"
            )
        content += "</body></html>"
        report_path = os.path.join(reports_dir, "full_report.html")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
        if verbose:
            print(f"[VERBOSE] HTML отчёт сформирован: {report_path}")
    else:  # JSON-отчёт
        report_data = {
            "title": "Отчёт аудита nAUDIT",
            "metrics": {
                "static_analysis": "завершён",
                "security_check": "проведена",
                "tests_analysis": "выполнен",
                "infrastructure_check": "выполнена"
            },
            "recommendations": recommendations_text,
            "details": "Содержимое логов анализа см. в папке с отчётом."
        }
        report_path = os.path.join(reports_dir, "full_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        if verbose:
            print(f"[VERBOSE] JSON отчёт сформирован: {report_path}")