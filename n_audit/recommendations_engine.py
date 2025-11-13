#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Движок рекомендаций - предлагает исправления на основе РЕАЛЬНЫХ проблем, найденных в коде.

Каждая рекомендация:
- Привязана к конкретной ошибке
- Предлагает конкретное решение
- Показывает пример кода
- Объясняет почему это важно
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class RecommendationPriority(Enum):
    """Приоритет рекомендации"""
    CRITICAL = "🔴 КРИТИЧЕСКОЕ"
    HIGH = "🟠 ВЫСОКОЕ"
    MEDIUM = "🟡 СРЕДНЕЕ"
    LOW = "🟢 НИЗКОЕ"


@dataclass
class Recommendation:
    """Одна рекомендация"""
    priority: RecommendationPriority
    title: str                          # Название
    description: str                    # Описание проблемы
    solution: str                       # Решение
    code_example: str                   # Пример кода
    impact: str                         # Влияние на рейтинг
    related_issues: List[str] = None    # Коды ошибок которые решит
    
    def __post_init__(self):
        if self.related_issues is None:
            self.related_issues = []


class RecommendationsEngine:
    """Движок рекомендаций - анализирует реальные проблемы"""
    
    def generate_recommendations(self, report) -> List[Recommendation]:
        """Генерировать рекомендации на основе отчета"""
        recommendations = []
        
        # 1. Проблемы безопасности - КРИТИЧЕСКОЕ
        if report.metrics.security_issues:
            security_recs = self._generate_security_recommendations(report)
            recommendations.extend(security_recs)
        
        # 2. Критические ошибки кода
        critical_errors = [i for i in report.metrics.code_issues if i.severity.name == 'CRITICAL']
        if critical_errors:
            error_recs = self._generate_error_recommendations(critical_errors)
            recommendations.extend(error_recs)
        
        # 3. Отсутствие тестов
        if report.metrics.test_files == 0:
            recommendations.append(Recommendation(
                priority=RecommendationPriority.CRITICAL,
                title="Добавить тесты",
                description="В проекте не найдено тестов. Это критическая проблема для любого production кода.",
                solution="Создайте папку 'tests' и добавьте тесты для основных функций проекта.",
                code_example="""
# tests/test_example.py
import pytest
from your_module import function

def test_function():
    result = function(input_data)
    assert result == expected_value
    
def test_function_error_handling():
    with pytest.raises(ValueError):
        function(invalid_input)
""",
                impact="Покрытие тестами может улучшить рейтинг на 2-3 пункта",
                related_issues=[]
            ))
        
        # 4. Документация
        if not report.metrics.has_readme:
            recommendations.append(Recommendation(
                priority=RecommendationPriority.HIGH,
                title="Создать README.md",
                description="README.md помогает пользователям понять как использовать ваш проект.",
                solution="Создайте файл README.md с описанием, инструкциями установки и примерами.",
                code_example="""
# Название проекта

Краткое описание что делает проект.

## Установка

pip install -r requirements.txt

## Использование

from module import function
result = function(data)

## Лицензия

MIT
""",
                impact="README улучшит рейтинг на 0.5-1 пункт",
                related_issues=[]
            ))
        
        # 5. Структура проекта
        if not report.metrics.has_setup_py:
            recommendations.append(Recommendation(
                priority=RecommendationPriority.HIGH,
                title="Добавить setup.py или pyproject.toml",
                description="Это необходимо для распространения вашего пакета и управления зависимостями.",
                solution="Создайте setup.py с metadata о проекте.",
                code_example="""
# setup.py
from setuptools import setup

setup(
    name='my-project',
    version='0.1.0',
    description='Описание проекта',
    packages=['my_project'],
    install_requires=[
        'requests>=2.28.0',
    ],
)
""",
                impact="setup.py улучшит рейтинг на 0.5-1 пункт",
                related_issues=[]
            ))
        
        if not report.metrics.has_git:
            recommendations.append(Recommendation(
                priority=RecommendationPriority.MEDIUM,
                title="Инициализировать Git репозиторий",
                description="Git необходим для версионирования кода и сотрудничества.",
                solution="Запустите 'git init' и создайте .gitignore",
                code_example="""
git init
git add .
git commit -m "Initial commit"

# .gitignore
__pycache__/
*.py[cod]
*$py.class
venv/
.env
*.egg-info/
""",
                impact="Git репозиторий улучшит рейтинг на 0.5 пункта",
                related_issues=[]
            ))
        
        # 6. Стиль кода
        style_issues = [i for i in report.metrics.code_issues if 'style' in i.issue_type.lower()]
        if len(style_issues) > 10:
            recommendations.append(Recommendation(
                priority=RecommendationPriority.MEDIUM,
                title="Улучшить стиль кода",
                description=f"Найдено {len(style_issues)} проблем со стилем кода. Это влияет на читаемость.",
                solution="Используйте черный форматер для автоматического форматирования.",
                code_example="""
# Установка
pip install black pylint

# Форматирование
black .

# Проверка стиля
pylint your_module/
""",
                impact="Чистый стиль улучшит рейтинг на 0.5-1 пункт",
                related_issues=['W', 'C']
            ))
        
        # Сортируем по приоритету
        priority_order = {
            RecommendationPriority.CRITICAL: 0,
            RecommendationPriority.HIGH: 1,
            RecommendationPriority.MEDIUM: 2,
            RecommendationPriority.LOW: 3,
        }
        recommendations.sort(key=lambda r: priority_order.get(r.priority, 999))
        
        return recommendations
    
    def _generate_security_recommendations(self, report) -> List[Recommendation]:
        """Рекомендации по безопасности"""
        recs = []
        
        # Анализируем конкретные проблемы
        issue_codes = set(i.code for i in report.metrics.security_issues)
        
        if any('B' in code for code in issue_codes):
            recs.append(Recommendation(
                priority=RecommendationPriority.CRITICAL,
                title="Исправить проблемы безопасности",
                description="Найдены критические проблемы безопасности (hardcoded пароли, опасные функции и т.д.)",
                solution="Используйте переменные окружения для чувствительных данных, избегайте eval/exec.",
                code_example="""
# ❌ НЕПРАВИЛЬНО
password = "admin123"
exec(user_input)

# ✅ ПРАВИЛЬНО
import os
password = os.getenv('SECRET_PASSWORD')
# Используйте ast.literal_eval или json.loads вместо eval
""",
                impact="Исправление проблем безопасности критично для production",
                related_issues=['B' + str(i) for i in range(100, 700)]
            ))
        
        return recs
    
    def _generate_error_recommendations(self, errors) -> List[Recommendation]:
        """Рекомендации по ошибкам"""
        recs = []
        
        error_types = {}
        for error in errors:
            if error.code not in error_types:
                error_types[error.code] = []
            error_types[error.code].append(error)
        
        # Обрабатываем конкретные коды ошибок
        if 'F' in ''.join(error_types.keys()):  # Syntax errors
            recs.append(Recommendation(
                priority=RecommendationPriority.CRITICAL,
                title="Исправить синтаксические ошибки",
                description="Найдены синтаксические ошибки в коде. Код не сможет выполняться.",
                solution="Проверьте скобки, отступы, двоеточия и другие элементы синтаксиса.",
                code_example="""
# ❌ НЕПРАВИЛЬНО
def func()
    print("hello)

# ✅ ПРАВИЛЬНО
def func():
    print("hello")
""",
                impact="Исправление синтаксиса необходимо для работы кода",
                related_issues=['F' + str(i) for i in range(100, 999)]
            ))
        
        return recs
    
    def group_by_impact(self, recommendations: List[Recommendation]) -> Dict[str, List[Recommendation]]:
        """Группировать рекомендации по потенциальному улучшению рейтинга"""
        grouped = {}
        for rec in recommendations:
            if rec.priority not in grouped:
                grouped[rec.priority] = []
            grouped[rec.priority].append(rec)
        return grouped
