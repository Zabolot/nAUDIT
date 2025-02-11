import os
import json
import importlib

from n_audit import code_analysis, security, tests_analysis, infrastructure, recommendations, utils
from . import visualizations

RESULTS_DIR = "audit_results"
REPORTS_DIR = os.path.join(RESULTS_DIR, "reports")
CONFIGS_DIR = os.path.join(RESULTS_DIR, "configs")
HISTORY_FILE = os.path.join(CONFIGS_DIR, "audit_history.json")

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
    # Генерация итогового отчета и вывод сводки с историей
    generate_report(args.report_level, args.export_format, REPORTS_DIR, recs, args.verbose)

def calculate_rating(summary_metrics):
    """
    Рассчитывает оценку от 1 до 10 исходя из количества ошибок.
    В данном примере:
      - каждый pylint-ошибка снижает оценку на 0.5
      - каждая ошибка безопасности снижает оценку на 0.5
    Начальное значение 10, но не ниже 1.
    """
    base_rating = 10.0
    pylint_errors = summary_metrics.get("pylint_errors", 0)
    security_errors = summary_metrics.get("security_errors", 0)
    deduction = 0.5 * (pylint_errors + security_errors)
    rating = max(1, base_rating - deduction)
    return round(rating, 1)

def load_previous_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def update_audit_history(current_metrics, current_rating):
    history = load_previous_history()
    history["last_audit"] = {
        "metrics": current_metrics,
        "rating": current_rating
    }
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def generate_report(report_level, export_format, reports_dir, recommendations_text, verbose):
    summary, summary_metrics = generate_summary(reports_dir)
    current_rating = calculate_rating(summary_metrics)
    prev_history = load_previous_history()
    diff = {}
    if "last_audit" in prev_history:
        prev_metrics = prev_history["last_audit"]["metrics"]
        # Сравнение ошибок между аудитами
        diff["pylint_errors"] = summary_metrics.get("pylint_errors", 0) - prev_metrics.get("pylint_errors", 0)
        diff["security_errors"] = summary_metrics.get("security_errors", 0) - prev_metrics.get("security_errors", 0)
    else:
        diff["pylint_errors"] = 0
        diff["security_errors"] = 0
    
    # Обновление истории аудитов
    update_audit_history(summary_metrics, current_rating)
    
    rating_info = f"Общая оценка кода: {current_rating}/10"
    diff_info = (
        f"Изменение pylint ошибок: {'+' if diff['pylint_errors'] >= 0 else ''}{diff['pylint_errors']}\n"
        f"Изменение ошибок безопасности: {'+' if diff['security_errors'] >= 0 else ''}{diff['security_errors']}"
    )
    
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
            f"<pre>{summary}\n\n{rating_info}\n\nИзменения по сравнению с предыдущим аудитом:\n{diff_info}</pre>\n"
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
            "rating": current_rating,
            "differences": diff,
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
    print(rating_info)
    print("Изменения по сравнению с предыдущим аудитом:")
    print(diff_info)

def generate_summary(reports_dir):
    """
    Формирует сводку аудита по итогам логов.
    Возвращает кортеж (строковая сводка, словарь ключевых метрик)
    """
    summary_lines = []
    metrics = {"pylint_errors": 0, "security_errors": 0}
    
    # Считаем ошибки из pylint_report.log
    pylint_log = os.path.join(reports_dir, "pylint_report.log")
    error_count = 0
    problematic_files = set()
    if os.path.exists(pylint_log):
        with open(pylint_log, "r", encoding="utf-8") as f:
            for line in f:
                if "ERROR" in line or "F0001" in line:
                    error_count += 1
                    parts = line.split()
                    if len(parts) >= 2:
                        problematic_files.add(parts[1])
    metrics["pylint_errors"] = error_count
    summary_lines.append(f"Ошибок в pylint: {error_count}")
    if problematic_files:
        summary_lines.append("Проблемные модули/файлы: " + ", ".join(problematic_files))
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
    metrics["security_errors"] = sec_errors
    summary_lines.append(f"Ошибок в безопасности (bandit/safety): {sec_errors}")
    
    # Сложность кода
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
    
    return "\n".join(summary_lines), metrics