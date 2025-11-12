"""
Точка входа nAUDIT для командной строки.
Поддерживает как GUI, так и CLI режимы работы.
"""

import argparse
import sys
from n_audit import core


def parse_args():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description="nAUDIT — инструмент глубокого аудита Python проектов.",
        epilog="Примеры использования:\n"
               "  naudit --module . --report-level full\n"
               "  naudit --module /path/to/project --export-format json\n"
               "  naudit-gui (запуск графического интерфейса)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--module",
        help="Анализировать конкретный модуль или директорию",
        default="."
    )

    parser.add_argument(
        "--exclude",
        help="Исключить файлы или директории (можно указать несколько)",
        nargs="*",
        default=[]
    )

    parser.add_argument(
        "--report-level",
        help="Уровень отчёта",
        choices=["brief", "full", "detailed"],
        default="full"
    )

    parser.add_argument(
        "--export-format",
        help="Формат экспорта отчёта",
        choices=["html", "json"],
        default="html"
    )

    parser.add_argument(
        "--verbose",
        help="Включить подробное логирование",
        action="store_true"
    )

    parser.add_argument(
        "--gui",
        help="Запустить графический интерфейс (используйте naudit-gui)",
        action="store_true"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="nAUDIT 2.0.0"
    )

    return parser.parse_args()


def main():
    """Главная функция"""
    args = parse_args()

    try:
        if args.gui:
            # Запуск GUI
            from n_audit.gui.main_app import main as gui_main
            gui_main()
        else:
            # Запуск CLI
            core.run_all_checks(args)
    except KeyboardInterrupt:
        print("\n\n⚠️  Аудит отменён пользователем", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()