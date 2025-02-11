import os
from n_audit import code_analysis, security, tests_analysis, infrastructure, visualizations, recommendations, utils

RESULTS_DIR = "audit_results"
REPORTS_DIR = os.path.join(RESULTS_DIR, "reports")
CONFIGS_DIR = os.path.join(RESULTS_DIR, "configs")

def setup_directories():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(CONFIGS_DIR, exist_ok=True)

def run_all_checks(args):
    print("[*] Инициализация аудита")
    setup_directories()

    # Проверка наличия внешних команд
    external_cmds = ["dot", "inspect4py", "safety", "gitleaks", "ag", "sqlfluff", "cyclonedx-py"]
    for cmd in external_cmds:
        if not utils.check_command(cmd):
            print(f"[WARNING] Не найдена утилита '{cmd}'. Рекомендуется установить её через пакетный менеджер системы.")

    # Запуск модулей анализа
    code_analysis.run(args, REPORTS_DIR)
    security.run(args, REPORTS_DIR)
    tests_analysis.run(args, REPORTS_DIR)
    infrastructure.run(args, REPORTS_DIR, CONFIGS_DIR)
    visualizations.generate_visualizations(REPORTS_DIR)
    
    # Генерация рекомендаций для улучшения кода и проекта
    recs = recommendations.generate_advices(REPORTS_DIR)
    
    # Формирование итогового отчёта с учётом выбранного уровня детализации
    generate_report(args.report_level, REPORTS_DIR, recs)
    
    print(f"[*] Отчёт аудита сформирован. Результаты сохранены в папке {RESULTS_DIR}")

def generate_report(report_level, reports_dir, recommendations_text):
    report_path = f"{reports_dir}/full_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Отчёт аудита nAUDIT\n\n")
        f.write("## Основные метрики\n")
        f.write("- Статический анализ кода завершён\n")
        f.write("- Проверка безопасности проведена\n")
        f.write("- Анализ тестового покрытия выполнен\n")
        f.write("- Проверка инфраструктуры выполнена\n\n")
        
        if report_level in ("full", "detailed"):
            f.write("## Детализированный отчёт\n")
            f.write("- Результаты radon, pylint, mypy, flake8 и inspect4py сохранены в отчётных файлах\n")
            f.write("- Выявленные уязвимости и рекомендации по безопасности опубликованы\n")
            f.write("- Анализ тестового покрытия с pytest и coverage сохранён\n")
            f.write("- Результаты проверки Docker, sqlfluff и окружения сохранены\n\n")
        
        f.write("## Рекомендации по улучшению проекта\n")
        f.write(recommendations_text)
        
        if report_level == "detailed":
            f.write("\n## Дополнительные советы для начинающих\n")
            f.write(
                "- Используйте виртуальные окружения для каждого проекта\n"
                "- Регулярно запускайте статический анализ кода для выявления ошибок\n"
                "- Следуйте рекомендациям по PEP8 и другим стандартам\n"
                "- Пишите тесты для каждого функционального блока и проверяйте покрытие\n"
            )