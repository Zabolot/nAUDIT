#!/bin/bash
# audit.sh - Комплексный аудит Python проекта с расширенной аналитикой

# Конфигурация
OUTPUT_DIR="audit_results"
REPORTS_DIR="$OUTPUT_DIR/reports"
VENV_DIR=".audit_venv"
CONFIG_DIR="$OUTPUT_DIR/configs"

# Инициализация окружения
init_environment() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Инициализация аудита"
    mkdir -p {$REPORTS_DIR,$CONFIG_DIR}
    python3 -m venv $VENV_DIR
    source $VENV_DIR/bin/activate
    pip install -U pip wheel > /dev/null 2>&1
    pip install pylint mypy bandit safety coverage pipdeptree radon inspect4py pytest > $REPORTS_DIR/dependencies.log
}

# Статический анализ кода
run_code_analysis() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Статический анализ кода"
    
    pipdeptree --graph-output png > $REPORTS_DIR/dependency_graph.png 2>$REPORTS_DIR/dependency_errors.log
    radon cc bot -a -O $REPORTS_DIR/cyclomatic_complexity.log
    radon mi bot -O $REPORTS_DIR/maintainability_index.log
    flake8 bot --config=.flake8 > $REPORTS_DIR/style_issues.log
    pylint bot --rcfile=.pylintrc > $REPORTS_DIR/pylint_report.log
    mypy bot --strict --config-file mypy.ini > $REPORTS_DIR/type_checks.log
}

# Анализ безопасности
run_security_checks() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Анализ безопасности"
    
    bandit -r bot -f json -o $REPORTS_DIR/security_issues.json
    safety check --json > $REPORTS_DIR/vulnerabilities.json
    pip list --format=json > $REPORTS_DIR/installed_packages.json
    
    # Поиск секретов
    if command -v gitleaks >/dev/null; then
        gitleaks detect --source ./ -r $REPORTS_DIR/secrets_report.json
    fi
}

# Анализ тестов
run_test_analysis() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Анализ тестов"
    
    coverage run -m pytest tests/ -v > $REPORTS_DIR/tests_results.log
    coverage html -d $REPORTS_DIR/coverage_report
    coverage xml -o $REPORTS_DIR/coverage.xml
    pytest --durations=10 > $REPORTS_DIR/tests_performance.log
}

# Проверка конфигураций
check_configs() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Анализ конфигураций"
    
    env > $CONFIG_DIR/environment_vars.log
    docker inspect $(docker ps -q) > $CONFIG_DIR/docker_configs.log 2>/dev/null
    pip freeze > $CONFIG_DIR/requirements_snapshot.txt
    
    if command -v docker-compose >/dev/null; then
        docker-compose config > $CONFIG_DIR/docker_compose_validated.log
    fi
}

# Интеграция с внешними сервисами
run_external_services() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Интеграция с внешними сервисами"
    
    if [[ -n $SENTRY_DSN ]]; then
        curl -X POST $SENTRY_DSN -d @$REPORTS_DIR/security_issues.json --fail --silent --show-error
    fi
    
    if command -v cyclonedx-py >/dev/null; then
        cyclonedx-py -o $REPORTS_DIR/sbom.xml -f xml
    fi
    
    if command -v trivy >/dev/null; then
        trivy image --format template --template "@contrib/gitlab.tpl" -o $REPORTS_DIR/container_scanning.html ${DOCKER_IMAGE:-bot}
    fi
}

# Генерация отчета
generate_report() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Генерация итогового отчета"
    
    cat << EOF > $OUTPUT_DIR/full_report.md
### Статистика проекта
- Python файлов: $(find bot -name '*.py' | wc -l)
- Тестов: $(find tests -name '*.py' | wc -l)
- Объем кода: $(radon raw bot -s | awk '/Total lines/ {print $3}') строк

### Результаты аудита
$(cat $REPORTS_DIR/*.log | grep -E 'WARNING|ERROR|CRITICAL')
EOF

    if command -v pandoc >/dev/null; then
        pandoc $OUTPUT_DIR/full_report.md -o $OUTPUT_DIR/audit_report.pdf
    fi
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
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Аудит завершен. Результаты в: $OUTPUT_DIR"
}

# Обработка аргументов
while [[ $# -gt 0 ]]; do
    case $1 in
        --db) check_migrations ;;
        --security) ENABLE_SECURITY=true ;;
        *) echo "Неизвестная опция: $1"; exit 1 ;;
    esac
    shift
done

main