import argparse
import sys
from n_audit import core

def parse_args():
    parser = argparse.ArgumentParser(
        description="nAUDIT — инструмент глубокого аудита Python проектов."
    )
    parser.add_argument("--module", help="Анализировать конкретный модуль или директорию", default=".")
    parser.add_argument("--exclude", help="Исключить файлы или директории", nargs="*", default=[])
    parser.add_argument("--report-level", help="Уровень отчёта: brief, full или detailed", 
                        choices=["brief", "full", "detailed"], default="full")
    return parser.parse_args()

def main():
    args = parse_args()
    try:
        core.run_all_checks(args)
    except Exception as e:
        sys.exit(f"Ошибка выполнения: {e}")

if __name__ == "__main__":
    main()