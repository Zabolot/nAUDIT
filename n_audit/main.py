"""
nAUDIT v4.0 - Точка входа для запуска приложения.
Поддерживает GUI и CLI режимы работы.
"""

import argparse
import sys
from pathlib import Path


def parse_args():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description="nAUDIT v4.0 - Профессиональный аудит Python проектов",
        epilog="Примеры:\n"
               "  python -m n_audit --path . --export\n"
               "  python -m n_audit --gui (запуск графического интерфейса)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--path",
        help="Путь к папке проекта для аудита",
        default=".",
        type=str
    )

    parser.add_argument(
        "--export",
        help="Экспортировать отчет (JSON/HTML/CSV)",
        action="store_true"
    )

    parser.add_argument(
        "--gui",
        help="Запустить графический интерфейс",
        action="store_true"
    )

    parser.add_argument(
        "--json",
        help="Выводить результат в JSON",
        action="store_true"
    )

    parser.add_argument(
        "--verbose",
        help="Подробное логирование",
        action="store_true"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="nAUDIT v4.0.0"
    )

    return parser.parse_args()


def main_cli(args):
    """Запуск в режиме командной строки"""
    from n_audit.audit_engine import AuditEngine
    from n_audit.report_generator import ReportGenerator
    import json
    
    print("[*] nAUDIT v4.0 - Профессиональный аудит кода")
    print(f"[*] Проект: {args.path}")
    
    # Запускаем аудит
    engine = AuditEngine()
    report = engine.audit(args.path)
    
    # Выводим результаты
    print(f"\n[RESULT] Рейтинг: {report.rating:.1f}/10")
    
    for component, score in report.rating_breakdown.items():
        print(f"   {component}: {score:.1f}")
    
    print(f"\n[ISSUES] Ошибок: {len(report.metrics.code_issues)}")
    print(f"[ISSUES] Безопасность: {len(report.metrics.security_issues)}")
    
    if args.json:
        # Выводим JSON
        data = {
            'rating': report.rating,
            'breakdown': report.rating_breakdown,
            'issues': len(report.metrics.code_issues),
            'security_issues': len(report.metrics.security_issues),
        }
        print(json.dumps(data, indent=2, ensure_ascii=False))
    
    if args.export:
        # Экспортируем отчеты
        gen = ReportGenerator()
        try:
            json_file = gen.save_json_report(report)
            html_file = gen.save_html_report(report)
            csv_file = gen.save_csv_report(report)
            print(f"\n[EXPORT] Отчеты сохранены:")
            print(f"   JSON: {json_file}")
            print(f"   HTML: {html_file}")
            print(f"   CSV: {csv_file}")
        except Exception as e:
            print(f"\n[ERROR] Ошибка экспорта: {e}")


def main_gui():
    """Запуск в режиме GUI"""
    from PyQt6.QtWidgets import QApplication
    from n_audit.gui.main_window_v4 import MainWindowV4
    
    app = QApplication(sys.argv)
    window = MainWindowV4()
    window.show()
    sys.exit(app.exec())


def main():
    """Главная функция"""
    args = parse_args()
    
    try:
        if args.gui:
            main_gui()
        else:
            main_cli(args)
    except KeyboardInterrupt:
        print("\n[!] Отменено пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
