import argparse 
import sys 
from n_audit import core

def main(): parser = argparse.ArgumentParser
    (description="nAUDIT — инструмент аудита Python проектов.") 
    parser.add_argument("--module", help="Модуль для анализа") 
    parser.add_argument("--exclude", help="Исключить директории или файлы") # можно добавить другие аргументы args = parser.parse_args()
    try:
        core.run_all_checks(args)
    except Exception as e:
        sys.exit(f"Ошибка выполнения: {e}")
        if name == "main": main()