#!/bin/bash
# audit.sh - Комплексный аудит Python проекта

# Конфигурация
OUTPUT_DIR="audit_results"
REPORTS_DIR="$OUTPUT_DIR/reports"
VENV_DIR=".audit_venv"
CONFIG_DIR="$OUTPUT_DIR/configs"

# Инициализация окружения
init_environment() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Инициализация аудита"
    mkdir -p {$REPORTS_DIR,$CONFIG_DIR}
    
    # Создание и активация venv
    python3 -m venv $VENV_DIR
    source $VENV_DIR/bin/activate
    
    # Установка основных зависимостей
    pip install -U pip wheel > /dev/null 2>&1
    pip install -r requirements.txt > $REPORTS_DIR/dependencies_install.log 2>&1
    
    # Установка инструментов анализа
    pip install pylint mypy bandit safety coverage pipdeptree radon \
        inspect4py pytest pydantic sqlalchemy > $REPORTS_DIR/tools_install.log 2>&1
}

check_migrations() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Проверка миграций БД"
    
    # Проверка истории миграций
    alembic history > $REPORTS_DIR/migration_history.log 2>&1 || echo "Ошибка миграций" >> $REPORTS_DIR/db_issues.log
    
    # Проверка согласованности схемы
    alembic check > $REPORTS_DIR/schema_consistency.log 2>&1 || echo "Несоответствие схемы" >> $REPORTS_DIR/db_issues.log
    
    # Анализ SQL-скриптов
    if command -v sqlfluff >/dev/null; then
        sqlfluff lint bot/db/ --format json > $REPORTS_DIR/sql_analysis.json
    fi
}

# Вывод итоговой сводки
print_summary() {
    echo
    echo "┌───────────────────────┐"
    echo "│ ИТОГОВАЯ СВОДКА АУДИТА│"
    echo "└───────────────────────┘"
    
    # Статистика проблем
    errors=$(grep -criE 'ERROR|FAILED' $REPORTS_DIR)
    warnings=$(grep -cri 'WARNING' $REPORTS_DIR)
    security_issues=$(jq '.results | length' $REPORTS_DIR/security_issues.json)
    
    # Основные метрики кода
    loc=$(radon raw bot -s | awk '/Total lines/ {print $3}')
    complexity=$(radon cc bot -a | grep -c ' M ')
    
    # Вывод сводки
    echo -e "\n📊 Основные метрики:"
    echo "• Объем кода: $loc строк"
    echo "• Высокая цикломатическая сложность в $complexity методах"
    
    echo -e "\n🚨 Проблемы:"
    echo "• Критические ошибки: $errors"
    echo "• Предупреждения: $warnings"
    echo "• Проблемы безопасности: $security_issues"
    
    # Рекомендации
    echo -e "\n💡 Рекомендации:"
    grep -hri 'suggestion:' $REPORTS_DIR | head -3
}

# Основной цикл выполнения
main() {
    init_environment
    
    run_code_analysis
    run_security_checks
    run_test_analysis
    check_configs
    run_external_services
    generate_report
    
    deactivate
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Аудит завершен. Результаты: $OUTPUT_DIR"
    print_summary
}

# Обработка аргументов
while [[ $# -gt 0 ]]; do
    case $1 in
        --db) check_migrations ;;
        --security) run_security_checks; exit 0 ;;
        *) echo "Неизвестная опция: $1"; exit 1 ;;
    esac
    shift
done

# Запуск основной программы
main