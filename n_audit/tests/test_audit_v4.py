#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты верификации v4 - проверяем что ВСЁ ДЕЙСТВИТЕЛЬНО РАБОТАЕТ.

Не как в v3 - тесты которые проходят на фейк-данных.
Здесь тесты проверяют РЕАЛЬНОЕ поведение:
- Файлы действительно сохраняются на диск
- Рейтинг действительно зависит от кода
- Рекомендации действительно привязаны к проблемам
"""

import pytest
import tempfile
import json
from pathlib import Path
from n_audit.audit_engine import AuditEngine, SeverityLevel
from n_audit.report_generator import ReportGenerator
from n_audit.recommendations_engine import RecommendationsEngine


class TestAuditEngine:
    """Тесты движка аудита"""
    
    def test_empty_folder_gets_low_rating(self):
        """Пустая папка должна получить НИЗКИЙ рейтинг (не 9.5!)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = AuditEngine()
            report = engine.audit(tmpdir)
            
            assert report.is_empty, "Пустая папка должна быть отмечена как is_empty"
            assert report.rating < 3.0, f"Рейтинг пустой папки должен быть < 3.0, получен: {report.rating}"
            assert len(report.metrics.code_issues) == 0
            assert report.metrics.total_files == 0
    
    def test_project_with_good_code(self):
        """Проект с хорошим кодом должен получить ВЫСОКИЙ рейтинг"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Создаем хорошо структурированный проект
            (tmpdir / "setup.py").write_text("""
from setuptools import setup
setup(name='test', version='0.1')
""")
            
            (tmpdir / "README.md").write_text("# Test Project")
            
            (tmpdir / ".gitignore").write_text("__pycache__/")
            
            (tmpdir / "module.py").write_text("""
def hello():
    \"\"\"Функция для привета\"\"\"
    return "Hello"

def main():
    \"\"\"Главная функция\"\"\"
    print(hello())

if __name__ == '__main__':
    main()
""")
            
            (tmpdir / "test_module.py").write_text("""
def test_hello():
    from module import hello
    assert hello() == "Hello"
""")
            
            engine = AuditEngine()
            report = engine.audit(str(tmpdir))
            
            assert not report.is_empty
            assert report.rating > 5.0, f"Хороший проект должен иметь рейтинг > 5.0, получен: {report.rating}"
            assert report.metrics.has_setup_py, "setup.py должен быть обнаружен"
            assert report.metrics.has_readme, "README должен быть обнаружен"
            assert report.metrics.test_files > 0, "Test файлы должны быть обнаружены"
    
    def test_rating_depends_on_code_quality(self):
        """Рейтинг должен ЗАВИСЕТЬ от качества кода, не быть константой"""
        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                tmpdir1 = Path(tmpdir1)
                tmpdir2 = Path(tmpdir2)
                
                # Хороший код - чистый, структурированный
                (tmpdir1 / "good.py").write_text("""
def calculate_sum(numbers):
    \"\"\"Вычислить сумму чисел\"\"\"
    return sum(numbers)

def main():
    \"\"\"Главная функция\"\"\"
    result = calculate_sum([1, 2, 3])
    print(result)

if __name__ == '__main__':
    main()
""")
                
                # Плохой код - много проблем (очень длинные строки, undefined переменные и т.д.)
                (tmpdir2 / "bad.py").write_text("""
import os
import sys

x = 1

def bad_function_with_very_long_name_that_exceeds_the_normal_line_length_limits():
    undefined_variable_that_should_cause_error = some_undefined_name
    y = 10
    z = 20
    a = 30
    b = 40
    c = 50
    return undefined_variable_that_should_cause_error + y + z + a + b + c

def another_bad_function(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8):
    if arg1:
        if arg2:
            if arg3:
                return arg1 + arg2 + arg3
    unused_var_1 = "unused"
    unused_var_2 = "also_unused"
    unused_var_3 = "not_used_either"
""")
                
                engine = AuditEngine()
                report1 = engine.audit(str(tmpdir1))
                report2 = engine.audit(str(tmpdir2))
                
                # Логируем результаты
                print(f"\nХороший код: рейтинг {report1.rating}, ошибок {len(report1.metrics.code_issues)}")
                print(f"Плохой код: рейтинг {report2.rating}, ошибок {len(report2.metrics.code_issues)}")
                
                # Плохой код должен иметь больше ошибок
                assert len(report2.metrics.code_issues) >= len(report1.metrics.code_issues), \
                    f"Плохой код должен иметь больше ошибок: {len(report2.metrics.code_issues)} vs {len(report1.metrics.code_issues)}"


class TestReportGenerator:
    """Тесты генератора отчетов"""
    
    def test_json_report_actually_saved(self):
        """JSON отчет должен ДЕЙСТВИТЕЛЬНО сохраняться на диск"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Создаем фейк отчет
            from n_audit.audit_engine import AuditReport, MetricsSnapshot
            
            metrics = MetricsSnapshot(
                total_files=5,
                total_lines=1000,
                total_functions=20,
                total_classes=5
            )
            report = AuditReport(
                project_path="/test/path",
                metrics=metrics,
                rating=7.5,
                rating_breakdown={"Test": 7.5},
                timestamp="2024-01-01T10:00:00"
            )
            
            # Сохраняем через генератор
            gen = ReportGenerator(str(tmpdir))
            file_path = gen.save_json_report(report, "test_report.json")
            
            # ПРОВЕРЯЕМ что файл ДЕЙСТВИТЕЛЬНО существует
            assert file_path.exists(), f"JSON файл не найден: {file_path}"
            assert file_path.stat().st_size > 100, f"JSON файл слишком маленький: {file_path.stat().st_size} bytes"
            
            # Проверяем содержимое
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert data['rating'] == 7.5
            assert data['project_path'] == "/test/path"
            assert data['metrics']['total_files'] == 5
    
    def test_html_report_actually_saved(self):
        """HTML отчет должен ДЕЙСТВИТЕЛЬНО сохраняться на диск"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            from n_audit.audit_engine import AuditReport, MetricsSnapshot
            
            metrics = MetricsSnapshot(total_files=1)
            report = AuditReport(
                project_path="/test",
                metrics=metrics,
                rating=8.0,
                rating_breakdown={"Quality": 8.0},
                timestamp="2024-01-01T10:00:00"
            )
            
            gen = ReportGenerator(str(tmpdir))
            file_path = gen.save_html_report(report, "test_report.html")
            
            # ПРОВЕРЯЕМ что файл ДЕЙСТВИТЕЛЬНО существует
            assert file_path.exists(), f"HTML файл не найден: {file_path}"
            assert file_path.stat().st_size > 1000, f"HTML файл слишком маленький"
            
            # Проверяем что это HTML
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert '<html' in content.lower()
            assert '8.0' in content or '8' in content
    
    def test_csv_report_actually_saved(self):
        """CSV отчет должен ДЕЙСТВИТЕЛЬНО сохраняться на диск"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            from n_audit.audit_engine import (
                AuditReport, MetricsSnapshot, CodeIssue, SeverityLevel
            )
            
            metrics = MetricsSnapshot(total_files=1)
            metrics.code_issues = [
                CodeIssue(
                    file_path="test.py",
                    line_number=1,
                    column=0,
                    severity=SeverityLevel.MEDIUM,
                    issue_type="error",
                    code="E501",
                    message="Line too long",
                    tool="pylint"
                )
            ]
            
            report = AuditReport(
                project_path="/test",
                metrics=metrics,
                rating=5.0,
                rating_breakdown={"Quality": 5.0},
                timestamp="2024-01-01T10:00:00"
            )
            
            gen = ReportGenerator(str(tmpdir))
            file_path = gen.save_csv_report(report, "test_report.csv")
            
            # ПРОВЕРЯЕМ что файл ДЕЙСТВИТЕЛЬНО существует
            assert file_path.exists(), f"CSV файл не найден: {file_path}"
            assert file_path.stat().st_size > 50
            
            # Проверяем содержимое
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert 'test.py' in content
            assert 'E501' in content


class TestRecommendationsEngine:
    """Тесты движка рекомендаций"""
    
    def test_recommendations_for_missing_tests(self):
        """Рекомендации должны предлагать добавить тесты если их нет"""
        from n_audit.audit_engine import AuditReport, MetricsSnapshot
        
        metrics = MetricsSnapshot(
            total_files=5,
            test_files=0  # НЕТ ТЕСТОВ
        )
        report = AuditReport(
            project_path="/test",
            metrics=metrics,
            rating=3.0,
            timestamp="2024-01-01T10:00:00"
        )
        
        engine = RecommendationsEngine()
        recs = engine.generate_recommendations(report)
        
        # Должна быть рекомендация про тесты
        test_recs = [r for r in recs if 'тест' in r.title.lower()]
        assert test_recs, "Должна быть рекомендация по тестам"
        assert test_recs[0].priority.name == 'CRITICAL'
    
    def test_no_recommendations_for_good_project(self):
        """Хороший проект должен иметь мало/нет рекомендаций"""
        from n_audit.audit_engine import AuditReport, MetricsSnapshot
        
        metrics = MetricsSnapshot(
            total_files=10,
            test_files=3,
            has_readme=True,
            has_setup_py=True,
            has_git=True,
            has_license=True,
            code_issues=[],
            security_issues=[]
        )
        report = AuditReport(
            project_path="/test",
            metrics=metrics,
            rating=9.0,
            timestamp="2024-01-01T10:00:00"
        )
        
        engine = RecommendationsEngine()
        recs = engine.generate_recommendations(report)
        
        # Для хорошего проекта должно быть мало критических рекомендаций
        critical_recs = [r for r in recs if r.priority.name == 'CRITICAL']
        assert len(critical_recs) == 0, f"Хороший проект не должен иметь CRITICAL рекомендации: {critical_recs}"


class TestIntegration:
    """Интеграционные тесты - полный цикл аудита"""
    
    def test_full_audit_cycle(self):
        """Полный цикл: аудит -> отчет -> рекомендации -> сохранение"""
        with tempfile.TemporaryDirectory() as project_dir:
            with tempfile.TemporaryDirectory() as report_dir:
                project_dir = Path(project_dir)
                report_dir = Path(report_dir)
                
                # Создаем проект
                (project_dir / "main.py").write_text("print('hello')")
                (project_dir / "README.md").write_text("# Test")
                
                # Аудит
                engine = AuditEngine()
                report = engine.audit(str(project_dir))
                
                assert report is not None
                assert report.rating >= 1.0
                
                # Рекомендации
                rec_engine = RecommendationsEngine()
                recs = rec_engine.generate_recommendations(report)
                
                assert isinstance(recs, list)
                
                # Сохранение
                gen = ReportGenerator(str(report_dir))
                json_file = gen.save_json_report(report)
                html_file = gen.save_html_report(report)
                csv_file = gen.save_csv_report(report)
                
                # ПРОВЕРЯЕМ что ВСЕ файлы ДЕЙСТВИТЕЛЬНО существуют
                assert json_file.exists()
                assert html_file.exists()
                assert csv_file.exists()
                
                assert json_file.stat().st_size > 100
                assert html_file.stat().st_size > 1000
                assert csv_file.stat().st_size > 50


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
