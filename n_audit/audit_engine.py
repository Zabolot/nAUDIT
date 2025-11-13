#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Настоящий аудит-движок с глубоким анализом и обоснованными метриками.

Этот модуль анализирует код РЕАЛЬНО, собирает РЕАЛЬНЫЕ данные,
и вычисляет ОБОСНОВАННЫЙ рейтинг на основе множества факторов.

Не будет никаких фейков, только правда.
"""

import os
import json
import subprocess
import re
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import statistics
from enum import Enum


class SeverityLevel(Enum):
    """Уровень серьезности проблемы"""
    CRITICAL = "🔴 КРИТИЧЕСКОЕ"      # Может привести к краху
    HIGH = "🟠 ВЫСОКОЕ"              # Серьезная проблема
    MEDIUM = "🟡 СРЕДНЕЕ"            # Требует внимания
    LOW = "🟢 НИЗКОЕ"                # Можно исправить позже


@dataclass
class CodeIssue:
    """Одна конкретная проблема в коде"""
    file_path: str                     # Путь к файлу
    line_number: int                   # Номер строки
    column: int                        # Номер столбца
    severity: SeverityLevel            # Серьезность
    issue_type: str                    # Тип (error, warning, style_issue)
    code: str                          # Код ошибки (E501, W291 и т.д.)
    message: str                       # Описание
    context: str = ""                  # Контекст (строка кода)
    tool: str = "unknown"              # Инструмент (pylint, flake8, mypy)
    
    @property
    def weight(self) -> float:
        """Вес этой ошибки для рейтинга"""
        weights = {
            SeverityLevel.CRITICAL: 10.0,
            SeverityLevel.HIGH: 5.0,
            SeverityLevel.MEDIUM: 2.0,
            SeverityLevel.LOW: 0.5,
        }
        return weights[self.severity]


@dataclass
class MetricsSnapshot:
    """Моментальный снимок метрик проекта"""
    total_files: int = 0               # Всего файлов Python
    total_lines: int = 0               # Всего строк кода
    total_functions: int = 0           # Функций
    total_classes: int = 0             # Классов
    
    # Качество кода
    code_issues: List[CodeIssue] = field(default_factory=list)
    avg_complexity: float = 0.0        # Средняя цикломатическая сложность
    max_complexity: int = 0            # Максимальная сложность
    
    # Безопасность
    security_issues: List[CodeIssue] = field(default_factory=list)
    unsafe_patterns: int = 0           # Опасные паттерны
    
    # Тесты
    test_coverage: float = 0.0         # % покрытия тестами
    test_files: int = 0                # Количество test файлов
    tests_count: int = 0               # Количество тестов
    
    # Документация
    docstring_coverage: float = 0.0    # % функций с документацией
    has_readme: bool = False           # Есть ли README
    has_changelog: bool = False        # Есть ли CHANGELOG
    has_license: bool = False          # Есть ли LICENSE
    
    # Структура проекта
    has_setup_py: bool = False         # setup.py
    has_requirements: bool = False     # requirements.txt
    has_git: bool = False              # .git
    has_ci_config: bool = False        # .github/workflows или .gitlab-ci.yml
    
    # Зависимости
    total_dependencies: int = 0        # Всего зависимостей
    vulnerable_dependencies: int = 0   # Уязвимых зависимостей
    
    def get_weighted_issue_count(self) -> float:
        """Получить взвешенное количество проблем"""
        all_issues = self.code_issues + self.security_issues
        return sum(issue.weight for issue in all_issues)


@dataclass
class AuditReport:
    """Полный отчет об аудите"""
    project_path: str
    metrics: MetricsSnapshot
    rating: float                      # 1.0 - 10.0
    rating_breakdown: Dict[str, float] = field(default_factory=dict)  # Компоненты оценки
    summary: str = ""                  # Текстовое резюме
    is_empty: bool = False             # Пуста ли папка
    timestamp: str = ""


class AuditEngine:
    """Ядро аудита - делает РЕАЛЬНЫЙ анализ"""
    
    def __init__(self):
        self.metrics = None
        self.report = None
        
    def audit(self, project_path: str) -> AuditReport:
        """Провести полный аудит проекта"""
        print(f"[AUDIT] Начинаю глубокий аудит: {project_path}")
        
        # Проверка наличия кода
        py_files = self._find_python_files(project_path)
        if not py_files:
            print(f"[WARN] В папке не найдено Python файлов")
            report = AuditReport(
                project_path=project_path,
                metrics=MetricsSnapshot(total_files=0),
                rating=2.0,
                is_empty=True,
                summary="Папка пуста или не содержит Python файлов"
            )
            return report
        
        # Инициализация метрик
        self.metrics = MetricsSnapshot(total_files=len(py_files))
        
        print(f"\n[METRICS] Собираю метрики...")
        print(f"  [1/7] Python файлы: {len(py_files)}")
        
        # 1. Базовая статистика
        self._collect_basic_metrics(py_files)
        print(f"  [2/7] Строки кода: {self.metrics.total_lines}")
        print(f"  [3/7] Функции/Классы: {self.metrics.total_functions}/{self.metrics.total_classes}")
        
        # 2. Анализ кода
        self._analyze_code_quality(project_path, py_files)
        print(f"  [4/7] Ошибки кода: {len(self.metrics.code_issues)}")
        
        # 3. Анализ безопасности
        self._analyze_security(project_path, py_files)
        print(f"  [5/7] Проблемы безопасности: {len(self.metrics.security_issues)}")
        
        # 4. Тесты и покрытие
        self._analyze_tests(project_path)
        print(f"  [6/7] Покрытие тестами: {self.metrics.test_coverage:.1f}%")
        
        # 5. Структура проекта
        self._analyze_structure(project_path)
        print(f"  [7/7] Структура: {'OK' if self.metrics.has_setup_py else 'NO'} setup, {'OK' if self.metrics.has_git else 'NO'} git")
        
        # Вычисление рейтинга
        rating, breakdown = self._calculate_rating()
        
        from datetime import datetime
        report = AuditReport(
            project_path=project_path,
            metrics=self.metrics,
            rating=rating,
            rating_breakdown=breakdown,
            summary=self._generate_summary(),
            timestamp=datetime.now().isoformat()
        )
        
        print(f"\n[FINAL] РЕЙТИНГ: {rating:.1f}/10")
        for component, score in breakdown.items():
            print(f"   {component}: {score:.1f}")
        
        self.report = report
        return report
    
    def _find_python_files(self, path: str) -> List[str]:
        """Найти все Python файлы в проекте"""
        py_files = []
        for root, dirs, files in os.walk(path):
            # Пропускаем папки
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'env']]
            for file in files:
                if file.endswith('.py'):
                    py_files.append(os.path.join(root, file))
        return sorted(py_files)
    
    def _analyze_syntax(self, py_files: List[str]):
        """Базовый анализ синтаксиса Python файлов"""
        for file_path in py_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Пытаемся скомпилировать как Python код
                try:
                    compile(content, file_path, 'exec')
                except SyntaxError as e:
                    self.metrics.code_issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=e.lineno or 0,
                        column=e.offset or 0,
                        severity=SeverityLevel.CRITICAL,
                        issue_type='error',
                        code='E901',
                        message=f"Syntax error: {e.msg}",
                        tool='python-ast'
                    ))
                
                # Проверяем на очень длинные строки
                for idx, line in enumerate(content.split('\n'), 1):
                    if len(line) > 120 and not line.strip().startswith('#'):
                        self.metrics.code_issues.append(CodeIssue(
                            file_path=file_path,
                            line_number=idx,
                            column=120,
                            severity=SeverityLevel.LOW,
                            issue_type='style_issue',
                            code='E501',
                            message=f"Line too long ({len(line)} > 120)",
                            tool='builtin'
                        ))
                
            except Exception as e:
                print(f"  [WARN] Error reading {file_path}: {e}")
    
    def _collect_basic_metrics(self, py_files: List[str]):
        """Собрать базовую статистику"""
        total_lines = 0
        functions = 0
        classes = 0
        
        for file_path in py_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                    total_lines += len(lines)
                    
                    # Считаем функции и классы
                    functions += len(re.findall(r'^\s*def\s+\w+\s*\(', content, re.MULTILINE))
                    classes += len(re.findall(r'^\s*class\s+\w+', content, re.MULTILINE))
            except Exception as e:
                print(f"  ⚠️ Ошибка чтения {file_path}: {e}")
        
        self.metrics.total_lines = total_lines
        self.metrics.total_functions = functions
        self.metrics.total_classes = classes
    
    def _analyze_code_quality(self, project_path: str, py_files: List[str]):
        """Анализ качества кода"""
        # Сначала базовый анализ синтаксиса
        self._analyze_syntax(py_files)
        
        # Используем pylint
        try:
            # Запускаем pylint в JSON режиме
            result = subprocess.run(
                ['pylint', '--output-format=json', '--disable=all', '--enable=E,W'] + py_files,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                issues = json.loads(result.stdout)
                for issue in issues:
                    severity = self._map_pylint_severity(issue.get('type', 'W'))
                    self.metrics.code_issues.append(CodeIssue(
                        file_path=issue.get('path', 'unknown'),
                        line_number=issue.get('line', 0),
                        column=issue.get('column', 0),
                        severity=severity,
                        issue_type=issue.get('type', 'warning'),
                        code=issue.get('symbol', ''),
                        message=issue.get('message', ''),
                        tool='pylint'
                    ))
        except Exception as e:
            print(f"  [INFO] pylint not available: {e}")
        
        # Используем flake8
        try:
            result = subprocess.run(
                ['flake8', '--format=json'] + py_files,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                issues = json.loads(result.stdout)
                for issue in issues:
                    code = issue.get('code', 'E999')
                    severity = SeverityLevel.MEDIUM if code[0] == 'E' else SeverityLevel.LOW
                    self.metrics.code_issues.append(CodeIssue(
                        file_path=issue.get('filename', 'unknown'),
                        line_number=issue.get('line_number', 0),
                        column=issue.get('column_number', 0),
                        severity=severity,
                        issue_type='style_issue',
                        code=code,
                        message=issue.get('text', ''),
                        tool='flake8'
                    ))
        except Exception as e:
            print(f"  [INFO] flake8 not available: {e}")
    
    def _analyze_security(self, project_path: str, py_files: List[str]):
        """Анализ безопасности"""
        try:
            result = subprocess.run(
                ['bandit', '--format=json', '-r', project_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                data = json.loads(result.stdout)
                for issue in data.get('results', []):
                    self.metrics.security_issues.append(CodeIssue(
                        file_path=issue.get('filename', 'unknown'),
                        line_number=issue.get('line_number', 0),
                        column=0,
                        severity=SeverityLevel.HIGH,
                        issue_type='security',
                        code=issue.get('test_id', 'B'),
                        message=issue.get('issue_text', ''),
                        tool='bandit'
                    ))
        except Exception as e:
            print(f"  [INFO] bandit not available: {e}")
    
    def _analyze_tests(self, project_path: str):
        """Анализ тестов и покрытия"""
        # Ищем test файлы
        test_files = []
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.startswith('test_') and file.endswith('.py'):
                    test_files.append(os.path.join(root, file))
        
        self.metrics.test_files = len(test_files)
        
        # Пытаемся запустить pytest с coverage
        try:
            result = subprocess.run(
                ['pytest', '--cov', '--cov-report=json', '-q'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Ищем файл .coverage или coverage.json
            coverage_file = Path(project_path) / ".coverage"
            json_coverage = Path(project_path) / "coverage.json"
            
            if json_coverage.exists():
                with open(json_coverage, 'r') as f:
                    data = json.load(f)
                    self.metrics.test_coverage = data.get('totals', {}).get('percent_covered', 0)
        except Exception as e:
            print(f"  [INFO] pytest/coverage not available: {e}")
            self.metrics.test_coverage = 0.0
    
    def _analyze_structure(self, project_path: str):
        """Анализ структуры проекта"""
        root = Path(project_path)
        
        self.metrics.has_setup_py = (root / 'setup.py').exists() or (root / 'pyproject.toml').exists()
        self.metrics.has_requirements = (root / 'requirements.txt').exists()
        self.metrics.has_git = (root / '.git').exists()
        self.metrics.has_readme = (root / 'README.md').exists() or (root / 'README.rst').exists()
        self.metrics.has_changelog = (root / 'CHANGELOG.md').exists() or (root / 'HISTORY.md').exists()
        self.metrics.has_license = (root / 'LICENSE').exists() or (root / 'LICENSE.md').exists()
        
        # Проверяем CI/CD
        self.metrics.has_ci_config = (
            (root / '.github' / 'workflows').exists() or
            (root / '.gitlab-ci.yml').exists() or
            (root / '.travis.yml').exists() or
            (root / 'tox.ini').exists()
        )
    
    def _calculate_rating(self) -> Tuple[float, Dict[str, float]]:
        """Вычислить рейтинг на основе РЕАЛЬНЫХ данных"""
        breakdown = {}
        
        # 1. Качество кода (35%)
        if self.metrics.total_lines > 0:
            issue_weight = self.metrics.get_weighted_issue_count()
            # Формула: базовый скор минус штраф за проблемы
            # На 1000 строк кода допустимо ~5 проблем
            acceptable_issues = max(1, self.metrics.total_lines / 1000 * 5)
            code_score = 10.0 - min(5.0, (issue_weight / acceptable_issues) * 5.0)
            code_score = max(1.0, code_score)
        else:
            code_score = 2.0
        
        breakdown['Качество кода'] = code_score
        
        # 2. Безопасность (30%)
        if self.metrics.security_issues:
            security_score = 10.0 - min(4.0, len(self.metrics.security_issues) * 2.0)
            security_score = max(1.0, security_score)
        else:
            security_score = 10.0
        
        breakdown['Безопасность'] = security_score
        
        # 3. Тесты (20%)
        if self.metrics.test_files > 0:
            # Награда за наличие тестов
            test_bonus = min(2.0, self.metrics.test_files * 0.5)
            test_score = 5.0 + test_bonus + (self.metrics.test_coverage / 100.0 * 3.0)
            test_score = min(10.0, test_score)
        else:
            test_score = 2.0
        
        breakdown['Тестирование'] = test_score
        
        # 4. Структура проекта (15%)
        structure_checks = sum([
            self.metrics.has_setup_py,
            self.metrics.has_requirements,
            self.metrics.has_readme,
            self.metrics.has_license,
            self.metrics.has_git,
            self.metrics.has_ci_config
        ])
        structure_score = 2.0 + (structure_checks / 6.0) * 8.0
        
        breakdown['Структура'] = structure_score
        
        # Взвешенная общая оценка
        rating = (
            code_score * 0.35 +
            security_score * 0.30 +
            test_score * 0.20 +
            structure_score * 0.15
        )
        
        return round(rating, 1), breakdown
    
    def _map_pylint_severity(self, pylint_type: str) -> SeverityLevel:
        """Преобразовать тип pylint в SeverityLevel"""
        mapping = {
            'error': SeverityLevel.CRITICAL,
            'fatal': SeverityLevel.CRITICAL,
            'warning': SeverityLevel.HIGH,
            'convention': SeverityLevel.LOW,
            'refactor': SeverityLevel.MEDIUM,
            'E': SeverityLevel.CRITICAL,
            'W': SeverityLevel.HIGH,
            'C': SeverityLevel.MEDIUM,
            'R': SeverityLevel.LOW,
        }
        return mapping.get(pylint_type.lower(), SeverityLevel.MEDIUM)
    
    def _generate_summary(self) -> str:
        """Создать текстовое резюме"""
        lines = []
        lines.append(f"Файлов: {self.metrics.total_files} | Строк: {self.metrics.total_lines}")
        lines.append(f"Функций: {self.metrics.total_functions} | Классов: {self.metrics.total_classes}")
        lines.append(f"Проблем кода: {len(self.metrics.code_issues)} | Безопасности: {len(self.metrics.security_issues)}")
        lines.append(f"Тесты: {self.metrics.test_files} файлов, покрытие {self.metrics.test_coverage:.1f}%")
        
        # Определяем статус
        issue_weight = self.metrics.get_weighted_issue_count()
        if issue_weight > 50:
            status = "CRITICAL - needs urgent attention"
        elif issue_weight > 20:
            status = "POOR - has serious issues"
        elif issue_weight > 5:
            status = "MEDIUM - has some issues"
        else:
            status = "GOOD - code is in order"
        
        lines.append(f"\nОценка: {status}")
        return "\n".join(lines)
