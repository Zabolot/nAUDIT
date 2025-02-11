import json, subprocess

def run(args, reports_dir):
    print("[*] Запуск статического анализа кода...")
    
    # Запуск radon с JSON-выводом
    try:
        result = subprocess.run(
            ["python", "-m", "radon", "cc", args.module, "--json"],
            capture_output=True,
            check=True,
            encoding="utf-8"
        )
        # Сохранение полного отчёта
        with open(f"{reports_dir}/cyclomatic_complexity_full.json", "w", encoding="utf-8") as f:
            f.write(result.stdout)

        # Парсинг JSON и формирование сводки
        data = json.loads(result.stdout)
        summary_lines = []
        for file, metrics in data.items():
            if metrics:
                avg_cc = sum(item.get('complexity', 0) for item in metrics) / len(metrics)
                summary_lines.append(f"{file}: средняя цикломатическая сложность = {avg_cc:.1f}")
            else:
                summary_lines.append(f"{file}: данные отсутствуют")
        print("[*] Сводка статического анализа:")
        for line in summary_lines:
            print("  " + line)
    except subprocess.CalledProcessError:
        print("[ERROR] Ошибка выполнения radon. Проверьте установку и конфигурацию.")

    # Запуск pylint с JSON-выводом для сводки
    try:
        result = subprocess.run(
            ["python", "-m", "pylint", args.module, "--output-format=json"],
            capture_output=True,
            check=True,
            encoding="utf-8"
        )
        with open(f"{reports_dir}/pylint_full.json", "w", encoding="utf-8") as f:
            f.write(result.stdout)
        issues = json.loads(result.stdout)
        num_issues = len(issues)
        print(f"[*] pylint: обнаружено {num_issues} проблем.")
    except subprocess.CalledProcessError:
        print("[ERROR] pylint завершился с ошибками. Смотрите полный отчёт в файле.")

    # Дополнительно можно добавить вызовы mypy, flake8 и inspect4py с подобной обработкой.