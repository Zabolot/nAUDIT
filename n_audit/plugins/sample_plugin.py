def run_plugin_checks(args, reports_dir):
    """
    Пример дополнительного плагина. Здесь можно реализовать
    собственные проверки, визуализации или сбор дополнительных метрик.
    """
    print("[PLUGIN] Запуск sample_plugin для дополнительных проверок...")
    # Пример: создание файла с данными плагина
    output_file = reports_dir + "/sample_plugin_report.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("Sample plugin report:\nДополнительные проверки пройдены успешно.\n")