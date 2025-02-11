#!/bin/bash
# filepath: /f:/CryptoPenXL/CryptoPenetratorXL_Bot/run_audit.sh
# Если виртуальное окружение не существует – создать его
if [ ! -d "v.naudit" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv v.naudit
fi

# Активировать виртуальное окружение
echo "Activating virtual environment..."
source v.naudit/bin/activate

# Обновляем pip и устанавливаем зависимости, если требуется
pip install --upgrade pip
pip install -r requirements.txt

# Создаём директорию для отчётов
mkdir -p project_report

# Выполняем аудиторские проверки
tree -a -I 'v.naudit|__pycache__' -o project_report/structure.txt
pip freeze > project_report/requirements.txt
flake8 bot/ > project_report/style_issues.txt
pylint bot/ --output=project_report/pylint_report.txt
mypy bot/ --strict > project_report/type_checks.txt
bandit -r bot/ -f txt -o project_report/security_issues.txt
alembic history > project_report/alembic_history.txt
pytest --cov=bot --cov-report=html:project_report/coverage tests/
radon cc bot/ -a -O project_report/complexity.txt
radon mi bot/ -O project_report/maintainability.txt
pipdeptree --graph-output png > project_report/dependencies.png

# Архивировать результаты
zip -r project_report.zip project_report/

# Деактивировать виртуальное окружение
deactivate