import os 
from n_audit.utils import check_command 
from n_audit.checks import code_analysis, security, tests_analysis, infrastructure

def run_all_checks(args): print("[*] Инициализация аудита") # Инициализация выходных директорий os.makedirs("audit_results/reports", exist_ok=True)

# Пример проверки наличия внешних команд с рекомендацией к установке
for cmd in ["dot", "inspect4py", "safety", "gitleaks", "ag", "sqlfluff", "cyclonedx-py"]:
    if not check_command(cmd):
        print(f"[WARNING] Не найдена утилита '{cmd}'. Рекомендуется установить её через пакетный менеджер системы.")

# Запуск проверки кода
code_analysis.run(args)
# Проверки безопасности
security.run(args)
# Анализ тестов
tests_analysis.run(args)
# Анализ инфраструктуры
infrastructure.run(args)

# Генерация визуализаций (проверка, если установлен networkx)
try:
    import networkx
    print("[*] Генерация визуализаций...")
    # Код генерации графов
except ImportError:
    print("[WARNING] Не установлен модуль networkx для генерации графиков.")

print("[*] Отчет аудита сформирован. Результаты сохранены в папке audit_results")