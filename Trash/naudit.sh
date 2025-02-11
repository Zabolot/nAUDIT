#!/bin/bash
# naudit.sh - Комплексный аудит Python проекта с расширенной аналитикой и кастомными проверками

# Конфигурация
OUTPUT_DIR="audit_results"
REPORTS_DIR="$OUTPUT_DIR/reports"
VENV_DIR=".audit_venv"
CONFIG_DIR="$OUTPUT_DIR/configs"
ENABLE_ALL=true
EXPORT_FORMAT="html"

# Инициализация окружения
init_environment() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Инициализация аудита"
    mkdir -p {$REPORTS_DIR,$CONFIG_DIR}
    
    python3 -m venv $VENV_DIR
    source $VENV_DIR/bin/activate
    
    pip install -U pip wheel > /dev/null 2>&1
    pip install pylint mypy bandit safety coverage pipdeptree radon \
        inspect4py pytest pydantic sqlalchemy sqlfluff cyclonedx-py \
        pyvis pandas gitleaks > $REPORTS_DIR/dependencies.log
}

# Расширенный статический анализ
run_code_analysis() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Статический анализ кода"
    
    pipdeptree --graph-output=dot | dot -Tpng > $REPORTS_DIR/dependency_graph.png
    radon cc bot -a -O $REPORTS_DIR/cyclomatic_complexity.log
    radon mi bot -O $REPORTS_DIR/maintainability_index.log
    flake8 bot --config=.flake8 > $REPORTS_DIR/style_issues.log
    pylint bot --rcfile=.pylintrc > $REPORTS_DIR/pylint_report.log
    mypy bot --strict --config-file mypy.ini > $REPORTS_DIR/type_checks.log
    
    # Анализ архитектуры
    inspect4py --num_processes 4 --directory bot --output_dir $REPORTS_DIR/architecture_analysis
}

# Комплексная проверка безопасности
run_security_checks() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Анализ безопасности"
    
    bandit -r bot -f json -o $REPORTS_DIR/security_issues.json
    safety check --json > $REPORTS_DIR/vulnerabilities.json
    pip list --format=json > $REPORTS_DIR/installed_packages.json
    
    # Поиск секретов и антипаттернов
    gitleaks detect --source ./ -r $REPORTS_DIR/secrets_report.json
    ag 'jwt.encode|os.environ.get|secret_key' bot/ > $REPORTS_DIR/security_antipatterns.log
}

# Анализ тестового покрытия
run_test_analysis() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Анализ тестов"
    
    coverage run -m pytest tests/ -v > $REPORTS_DIR/tests_results.log
    coverage html -d $REPORTS_DIR/coverage_report
    coverage xml -o $REPORTS_DIR/coverage.xml
    pytest --durations=10 > $REPORTS_DIR/tests_performance.log
    
    # Проверка качества тестов
    ag 'TODO|FIXME|sleep\(|Mock()' tests/ >> $REPORTS_DIR/test_antipatterns.log
}

# Проверка инфраструктуры
check_infrastructure() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Анализ инфраструктуры"
    
    env > $CONFIG_DIR/environment_vars.log
    pip freeze > $CONFIG_DIR/requirements_snapshot.txt
    
    # Docker анализ
    if command -v docker &> /dev/null; then
        docker inspect $(docker ps -q) > $CONFIG_DIR/docker_configs.log 2>/dev/null
        docker-compose config > $CONFIG_DIR/docker_compose_validated.log
    fi
    
    # Миграции БД
    if command -v alembic &> /dev/null; then
        alembic history > $REPORTS_DIR/migration_history.log
        alembic check > $REPORTS_DIR/schema_consistency.log 2>&1
        sqlfluff lint bot/db/ --format json > $REPORTS_DIR/sql_analysis.json
    fi
}

# Интеграция с внешними системами
run_integrations() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Интеграция с внешними системами"
    
    # SBOM генерация
    cyclonedx-py -o $REPORTS_DIR/sbom.xml -f xml
    
    # Сканирование контейнеров
    if command -v trivy &> /dev/null; then
        trivy image --format template --template "@contrib/gitlab.tpl" \
        -o $REPORTS_DIR/container_scanning.html ${DOCKER_IMAGE:-bot}
    fi
}

# Генерация визуализаций
generate_visualizations() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Генерация визуализаций"
    
    # Интерактивный граф зависимостей
    python3 -c "
import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()
with open('$REPORTS_DIR/dependency_graph.png', 'r') as f:
    for line in f:
        if '->' in line:
            parts = line.split('->')
            G.add_edge(parts[0].strip(), parts[1].strip())

plt.figure(figsize=(20,15))
nx.draw(G, with_labels=True, node_size=3000)
plt.savefig('$REPORTS_DIR/dependency_graph_interactive.png')
"
}

# Формирование отчета
generate_report() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Генерация итогового отчета"
    
    # Статистика
    total_lines=$(radon raw bot -s | awk '/Total lines/ {print $3}')
    test_coverage=$(coverage report | awk '/TOTAL/ {print $4}')
    
    # Сводка
    cat << EOF > $OUTPUT_DIR/full_report.md
# Отчет аудита

## Основные метрики
- Объем кода: $total_lines строк
- Тестовое покрытие: $test_coverage
- Выявлено проблем: $(grep -cri 'ERROR' $REPORTS_DIR)

## Рекомендации
$(awk '/suggestion:/ {print "- " $0}' $REPORTS_DIR/*.log | sort -u)

## Детали
$(for f in $REPORTS_DIR/*.log; do
  echo "### $(basename $f)\n\`\`\`\n$(head -n 20 $f)\n...\n\`\`\`\n"; done)
EOF

    # Экспорт
    if command -v pandoc &> /dev/null; then
        pandoc $OUTPUT_DIR/full_report.md -o $OUTPUT_DIR/audit_report.pdf
    fi
}

# Краткая сводка
print_summary() {
    echo -e "\n\033[1;36m=== ИТОГОВАЯ СВОДКА ===\033[0m"
    echo -e "\033[1;33mКритические проблемы:\033[0m $(grep -cri 'ERROR' $REPORTS_DIR)"
    echo -e "\033[1;33mПредупреждения:\033[0m      $(grep -cri 'WARNING' $REPORTS_DIR)"
    echo -e "\033[1;33mПроблемы безопасности:\033[0m $(jq '.results | length' $REPORTS_DIR/security_issues.json)"
    
    echo -e "\n\033[1;36mРекомендуемые действия:\033[0m"
    grep -hri 'suggestion:' $REPORTS_DIR | head -n 3 | sed 's/suggestion:/ -/'
}

# Обработка аргументов
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --module) MODULE="$2"; shift ;;
            --exclude) EXCLUDE="$2"; shift ;;
            --db) CHECK_DB=true ;;
            --security) CHECK_SECURITY=true ;;
            --format) EXPORT_FORMAT="$2"; shift ;;
            --quick) ENABLE_ALL=false ;;
            *) echo "Неизвестная опция: $1"; exit 1 ;;
        esac
        shift
    done
}

# Основной цикл
main() {
    parse_arguments "$@"
    init_environment
    run_code_analysis
    run_security_checks
    run_test_analysis
    check_infrastructure
    run_integrations
    generate_visualizations
    generate_report
    print_summary
    
    deactivate
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Результаты сохранены в: $OUTPUT_DIR"
}

main "$@"