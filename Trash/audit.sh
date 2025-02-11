#!/bin/bash
# audit.sh - Комплексный аудит Python проекта с расширенной аналитикой

# Конфигурация
OUTPUT_DIR="audit_results"
REPORTS_DIR="$OUTPUT_DIR/reports"
VENV_DIR=".audit_venv"
CONFIG_DIR="$OUTPUT_DIR/configs"
ENABLE_ALL=true

# Параметры скрипта
while [[ $# -gt 0 ]]; do
    case $1 in
        --modules) MODULES="$2"; shift ;;
        --exclude) EXCLUDE="$2"; shift ;;
        --db) CHECK_DB=true ;;
        --security) CHECK_SECURITY=true ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
    shift
done

# Инициализация окружения
init_environment() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Инициализация аудита"
    mkdir -p {$REPORTS_DIR,$CONFIG_DIR}
    python3 -m venv $VENV_DIR
    source $VENV_DIR/bin/activate
    pip install -U pip wheel > /dev/null 2>&1
    pip install pylint mypy bandit safety coverage pipdeptree radon inspect4py pytest > $REPORTS_DIR/dependencies.log
}

# Расширенный статический анализ кода
run_code_analysis() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Статический анализ кода"
    
    # Анализ зависимостей
    pipdeptree --graph-output png > $REPORTS_DIR/dependency_graph.png 2>$REPORTS_DIR/dependency_errors.log
    
    # Проверка циклических импортов
    python -c "import sys; from pylint import checkers; from pylint.lint import Run; Run([*sys.argv[1:]])" --disable=all --enable=cyclic-import bot/ > $REPORTS_DIR/cyclic_imports.log
    
    # Анализ сложности кода
    radon cc bot -a -O $REPORTS_DIR/cyclomatic_complexity.log
    radon mi bot -O $REPORTS_DIR/maintainability_index.log
    
    # Проверка стиля
    flake8 bot --config=.flake8 > $REPORTS_DIR/style_issues.log
    pylint bot --rcfile=.pylintrc > $REPORTS_DIR/pylint_report.log
    
    # Проверка типов
    mypy bot --strict --config-file mypy.ini > $REPORTS_DIR/type_checks.log
}

# Динамический анализ безопасности
run_security_checks() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Анализ безопасности"
    
    # Статический анализ кода
    bandit -r bot -f json -o $REPORTS_DIR/security_issues.json
    safety check --json > $REPORTS_DIR/vulnerabilities.json
    
    # Анализ зависимостей
    pip list --format=json > $REPORTS_DIR/installed_packages.json
}

# Анализ тестов и покрытия
run_test_analysis() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Анализ тестов"
    
    coverage run -m pytest tests/ -v > $REPORTS_DIR/tests_results.log
    coverage html -d $REPORTS_DIR/coverage_report
    coverage xml -o $REPORTS_DIR/coverage.xml
    
    # Анализ времени выполнения
    pytest --durations=10 > $REPORTS_DIR/tests_performance.log
}

# Проверка конфигураций и зависимостей
check_configs() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Анализ конфигураций"
    
    # Экспорт текущей конфигурации
    env > $CONFIG_DIR/environment_vars.log
    docker inspect $(docker ps -q) > $CONFIG_DIR/docker_configs.log
    pip freeze > $CONFIG_DIR/requirements_snapshot.txt
    
    # Проверка Docker Compose
    docker-compose config > $CONFIG_DIR/docker_compose_validated.log
}

# Проверка миграций БД
check_migrations() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Проверка миграций"
    
    alembic history > $REPORTS_DIR/migration_history.log
    alembic check || echo "Проблемы с миграциями" >> $REPORTS_DIR/db_issues.log
    sqlfluff lint bot/db/ --format json > $REPORTS_DIR/sql_analysis.json
}

# Генерация отчета
generate_report() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Генерация итогового отчета"
    
    # Сборка метаданных
    echo "### Статистика проекта" > $OUTPUT_DIR/full_report.md
    echo "- Число Python файлов: $(find bot -name '*.py' | wc -l)" >> $OUTPUT_DIR/full_report.md
    echo "- Число тестов: $(find tests -name '*.py' | wc -l)" >> $OUTPUT_DIR/full_report.md
    echo "- Объем кода: $(radon raw bot -s | awk '/Total lines/ {print $3}') строк" >> $OUTPUT_DIR/full_report.md
    
    # Сбор результатов
    cat $REPORTS_DIR/*.log >> $OUTPUT_DIR/full_report.md
    pipdeptree

# Интеграция с внешними сервисами
run_external_services() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Интеграция с внешними сервисами"
    
    # Отправка результатов в Sentry (при наличии DSN)
    if [[ -n $SENTRY_DSN ]]; then
        echo "Отправка результатов в Sentry..."
        curl -X POST $SENTRY_DSN -d @$REPORTS_DIR/security_issues.json
    fi
    
    # Генерация SBOM
    cyclonedx-py -o $REPORTS_DIR/sbom.xml -f xml
    
    # Сканирование контейнеров
    if command -v trivy &> /dev/null; then
        trivy image --format template --template "@contrib/gitlab.tpl" -o $REPORTS_DIR/container_scanning.html ${DOCKER_IMAGE:-bot}
    fi
}

# Расширенная визуализация данных
generate_visualizations() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Генерация визуализаций"
    
    # Создание интерактивных графиков
    python3 -c "
import pandas as pd
from pyvis.network import Network
import ast

# Анализ зависимостей
with open('$REPORTS_DIR/dependency_graph.png') as f:
    net = Network(height='800px', width='100%')
    data = ast.literal_eval(f.read())
    for pkg in data:
        net.add_node(pkg['name'], label=pkg['name'])
        for dep in pkg['dependencies']:
            net.add_node(dep, label=dep)
            net.add_edge(pkg['name'], dep)
    net.show('$REPORTS_DIR/dependency_graph.html')
    "
}

# Анализ архитектуры проекта
analyze_architecture() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Анализ архитектуры проекта"
    
    inspect4py --num_processes 4 --directory bot --output_dir $REPORTS_DIR/architecture_analysis
    
    # Визуализация структуры модулей
    python3 -m pylint --rcfile=.pylintrc --generate-erd=$REPORTS_DIR/entity_relationship_diagram.svg bot
    
    # Анализ графа вызовов
    pycallgraph graphviz -- ./bot/main.py
    mv pycallgraph.png $REPORTS_DIR/call_graph.png
}

# Персонализированные проверки
custom_checks() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Выполнение специальных проверок"
    
    # Проверка безопасности JWT
    if grep -r "jwt.encode" bot/; then
        echo "Обнаружено прямое использование JWT без проверок!" >> $REPORTS_DIR/security_issues.log
    fi
    
    # Поиск жестко закодированных секретов
    gitleaks detect --source ./ -r $REPORTS_DIR/secrets_report.json
    
    # Анализ производительности
    pytest --benchmark-json=$REPORTS_DIR/benchmark_results.json tests/performance_tests/
}

# Расширенный таргетированный анализ
targeted_analysis() {
    local module=$1
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Глубокий анализ модуля: $module"
    
    # Специфический линт для модуля
    flake8 $module --config=.flake8 > $REPORTS_DIR/${module}_style_issues.log
    
    # Анализ тестового покрытия модуля
    coverage run --branch --include="$module/*" -m pytest tests/
    coverage html -d $REPORTS_DIR/${module}_coverage
    coverage xml -o $REPORTS_DIR/${module}_coverage.xml
    
    # Статический анализ безопасности модуля
    bandit -r $module -f json -o $REPORTS_DIR/${module}_security.json
}

# Анализ качества тестов
test_quality_checks() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Анализ качества тестов"
    
    # Проверка дублирующихся тестов
    pytest --dup -v tests/ > $REPORTS_DIR/duplicate_tests.log
    
    # Тест на наличие забытых skip/pass
    ag 'sleep\(|time\.sleep' tests/ >> $REPORTS_DIR/test_antipatterns.log
    ag 'TODO|FIXME' tests/ >> $REPORTS_DIR/test_todos.log
    
    # Проверка mock-объектов
    python3 -c "
from unittest.mock import Mock
import ast

with open('tests/test_*.py') as f:
    for node in ast.walk(ast.parse(f.read())):
        if isinstance(node, ast.Assign) and 'Mock' in node.targets:
            print('Найден прямой Mock без autospec:', node.lineno)
    " >> $REPORTS_DIR/mock_issues.log
}

export_report() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Экспорт отчета"
    
    # Конвертация в PDF
    pandoc $OUTPUT_DIR/full_report.md -o $OUTPUT_DIR/audit_report.pdf
    
    # Генерация HTML
    mkdir $OUTPUT_DIR/html_report
    python3 -c "
from dominate import document
from dominate.tags import *

doc = document(title='Audit Report')

with doc.head:
    link(rel='stylesheet', href='https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css')

with doc:
    div(cls='container', [
        h1('Audit Report', cls='mt-5 mb-4'),
        div(cls='row', [
            div(cls='col-md-6', [
                h3('Statistics'),
                pre(open('$OUTPUT_DIR/full_report.md').read())
            ]),
            div(cls='col-md-6', [
                h3('Visualizations'),
                img(src='dependency_graph.png', cls='img-fluid'),
                a('View Details', href='dependency_graph.html')
            ])
        ])
    ])
    
with open('$OUTPUT_DIR/html_report/index.html', 'w') as f:
    f.write(doc.render())
    "
}

main() {
    init_environment
    analyze_architecture
    run_code_analysis
    run_security_checks
    test_quality_checks
    run_external_services
    generate_visualizations
    custom_checks
    export_report
    
    if [[ $CHECK_DB == true ]]; then
        check_migrations
        check_db_schema
    fi
    
    deactivate
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Аудит завершен. Результаты в: $OUTPUT_DIR"
    exit 0
}

# Обработка аргументов и запуск
while [[ $# -gt 0 ]]; do
    case $1 in
        --module) targeted_analysis "$2"; shift ;;
        --full) ENABLE_ALL=true ;;
        --quick) ENABLE_ALL=false ;;
        --format) EXPORT_FORMAT="$2"; shift ;;
        *) echo "Неизвестная опция: $1"; exit 1 ;;
    esac
    shift
done

main