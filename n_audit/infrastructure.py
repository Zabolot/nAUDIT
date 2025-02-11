import os
import subprocess
from n_audit import utils

def run(args, reports_dir, configs_dir):
    print("[*] Проверка инфраструктуры и окружения...")
    # Сохранение переменных окружения
    with open(f"{configs_dir}/environment_vars.log", "w") as f:
        for key, value in os.environ.items():
            f.write(f"{key}={value}\n")
    
    # Сохранение списка установленных пакетов
    subprocess.run(["pip", "freeze"], check=False, stdout=open(f"{configs_dir}/requirements_snapshot.txt", "w"))
    
    # Проверка Docker (если установлен)
    if utils.check_command("docker"):
        subprocess.run(["docker-compose", "config"], check=False, stdout=open(f"{configs_dir}/docker_compose_validated.log", "w"))
    
    # Пример использования sqlfluff для анализа SQL файлов (если применимо)
    if utils.check_command("sqlfluff"):
        subprocess.run(["sqlfluff", "lint", f"{args.module}/db/"], check=False, stdout=open(f"{reports_dir}/sql_analysis.json", "w"))