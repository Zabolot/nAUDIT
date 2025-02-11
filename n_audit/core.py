import os
import json
import importlib

from n_audit import code_analysis, security, tests_analysis, infrastructure, recommendations, utils
from . import visualizations

RESULTS_DIR = "audit_results"
REPORTS_DIR = os.path.join(RESULTS_DIR, "reports")
CONFIGS_DIR = os.path.join(RESULTS_DIR, "configs")

def setup_directories():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(CONFIGS_DIR, exist_ok=True)

def load_plugins():
    """
    Загружает дополнительные плагины из папки n_audit/plugins.
    Каждый плагин должен реализовывать функцию run_plugin_checks(args, reports_dir).
    """
    plugins = []
    plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
    if os.path.exists(plugins_dir):
        for filename in os.listdir(plugins_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]
                try:
                    mod = importlib.import_module(f"n_audit.plugins.{module_name}")
                    if hasattr(mod, "run_plugin_checks"):
                        plugins.append(mod)
                except Exception as e:
                    print(f"[WARNING] Не удалось загрузить плагин {module_name}: {e}")
    return plugins

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
    
    # Определение директории для анализа. Если не указано, анализируется текущая директория.
    target = args.module if args.module else "."
    
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
    
    # Запуск плагинов (если имеются). Плагины могут добавлять дополнительные проверки и визуализации.
    plugins = load_plugins()
    for plugin in plugins:
        try:
            plugin.run_plugin_checks(args, REPORTS_DIR)
        except Exception as e:
            print(f"[ERROR] Плагин {plugin.__name__} завершился с ошибкой: {e}")
    
    # Генерация рекомендаций
    recs = recommendations.generate_advices(REPORTS_DIR)
    # Генерация итогового отчета и вывод сводки
    generate_report(args.report_level, args.export_format, REPORTS_DIR, recs, args.verbose)

def generate_report(report_level, export_format, reports_dir, recommendations_text, verbose):
    summary = generate_summary(reports_dir)
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
            "<h2>Сводка аудита</h2>\n"
            f"<pre>{summary}</pre>\n"
            "</body></html>"
        )
        report_path = os.path.join(reports_dir, "full_report.html")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
        if verbose:
            print(f"[VERBOSE] HTML отчёт сформирован: {report_path}")
    else:  # JSON-отчёт
        report_data = {
            "title": "Отчёт аудита nAUDIT",
            "metrics": summary,
            "recommendations": recommendations_text,
            "details": "Содержимое логов анализа см. в папке с отчётом."
        }
        report_path = os.path.join(reports_dir, "full_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        if verbose:
            print(f"[VERBOSE] JSON отчёт сформирован: {report_path}")
    
    # Вывод сводки в терминал
    print("\n[*] Итоговая сводка аудита:")
    print(summary)

def generate_summary(reports_dir):
    """
    Формирует сводку аудита по итогам логов.
    Сканирует файлы с логами и возвращает краткую статистику:
      - Количество найденных ошибок (например, из pylint_report.log)
      - Проблемные модули (на основе наличия ошибок)
      - Рекомендации по дальнейшим действиям
    """
    summary_lines = []
    # Считаем ошибки из pylint_report.log
    pylint_log = os.path.join(reports_dir, "pylint_report.log")
    error_count = 0
    problem_modules = set()
    if os.path.exists(pylint_log):
        with open(pylint_log, "r", encoding="utf-8") as f:
            for line in f:
                if "ERROR" in line or "F0001" in line:
                    error_count += 1
                    parts = line.split()
                    if len(parts) >= 2:
                        problem_modules.add(parts[1])
    summary_lines.append(f"Ошибок в pylint: {error_count}")
    if problem_modules:
        summary_lines.append("Проблемные модули/файлы: " + ", ".join(problem_modules))
    else:
        summary_lines.append("Проблемные модули не выявлены.")
    
    # Сводка по безопасности (например, ошибки bandit/safety)
    security_file = os.path.join(reports_dir, "security_issues.json")
    sec_errors = 0
    if os.path.exists(security_file):
        try:
            with open(security_file, "r", encoding="utf-8") as f:
                sec_data = json.load(f)
                if "errors" in sec_data:
                    sec_errors = len(sec_data["errors"])
        except Exception:
            pass
    summary_lines.append(f"Ошибок в безопасности (bandit/safety): {sec_errors}")
    
    # Сводка по сложности кода из cyclomatic_complexity.log
    complexity_log = os.path.join(reports_dir, "cyclomatic_complexity.log")
    if os.path.exists(complexity_log):
        with open(complexity_log, "r", encoding="utf-8") as f:
            complexity_content = f.read().strip()
        if complexity_content:
            summary_lines.append("Замечания по сложности кода:")
            summary_lines.append(complexity_content)
        else:
            summary_lines.append("Анализ цикломатической сложности не выявил критических участков.")
    else:
        summary_lines.append("Файл с цикломатической сложностью не найден.")
    
    summary_lines.append("\nРекомендации:")
    summary_lines.append("  - Проверьте указанные проблемные места.")
    summary_lines.append("  - Обновите конфигурацию для устранения ошибок pylint и безопасности.")
    summary_lines.append("  - Расширьте модульное тестирование для повышения покрытия кода.")
    
    return "\n".join(summary_lines)