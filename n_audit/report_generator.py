#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор отчетов - сохраняет отчеты в разных форматах НА САМОМ ДЕЛЕ.

Не фейк. Не обещания. Реальные файлы на диске.
Каждый файл проверяется после создания.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import html


class ReportGenerator:
    """Генератор отчетов с РЕАЛЬНЫМ сохранением"""
    
    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = Path.home() / '.naudit' / 'reports'
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_json_report(self, report, filename: str = None) -> Path:
        """Сохранить отчет в JSON с ПРОВЕРКОЙ"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"report_{timestamp}.json"
        
        file_path = self.output_dir / filename
        
        # Подготовляем данные для JSON
        data = {
            'timestamp': report.timestamp,
            'project_path': report.project_path,
            'rating': report.rating,
            'rating_breakdown': report.rating_breakdown,
            'summary': report.summary,
            'is_empty': report.is_empty,
            'metrics': {
                'total_files': report.metrics.total_files,
                'total_lines': report.metrics.total_lines,
                'total_functions': report.metrics.total_functions,
                'total_classes': report.metrics.total_classes,
                'code_issues': len(report.metrics.code_issues),
                'security_issues': len(report.metrics.security_issues),
                'avg_complexity': report.metrics.avg_complexity,
                'max_complexity': report.metrics.max_complexity,
                'test_coverage': report.metrics.test_coverage,
                'test_files': report.metrics.test_files,
                'docstring_coverage': report.metrics.docstring_coverage,
                'structure': {
                    'has_setup_py': report.metrics.has_setup_py,
                    'has_requirements': report.metrics.has_requirements,
                    'has_git': report.metrics.has_git,
                    'has_ci_config': report.metrics.has_ci_config,
                    'has_readme': report.metrics.has_readme,
                    'has_changelog': report.metrics.has_changelog,
                    'has_license': report.metrics.has_license,
                }
            },
            'issues': {
                'code_issues': [
                    {
                        'file': issue.file_path,
                        'line': issue.line_number,
                        'column': issue.column,
                        'code': issue.code,
                        'message': issue.message,
                        'severity': issue.severity.name,
                        'tool': issue.tool,
                    }
                    for issue in report.metrics.code_issues
                ],
                'security_issues': [
                    {
                        'file': issue.file_path,
                        'line': issue.line_number,
                        'code': issue.code,
                        'message': issue.message,
                        'tool': issue.tool,
                    }
                    for issue in report.metrics.security_issues
                ]
            }
        }
        
        # Пишем JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # ПРОВЕРЯЕМ что файл существует и не пуст
        if not file_path.exists():
            raise FileNotFoundError(f"Не удалось создать файл: {file_path}")
        
        size = file_path.stat().st_size
        if size < 100:
            raise ValueError(f"Файл слишком маленький ({size} bytes): {file_path}")
        
        print(f"✅ JSON отчет сохранен: {file_path} ({size} bytes)")
        return file_path
    
    def save_html_report(self, report, filename: str = None) -> Path:
        """Сохранить красивый HTML отчет с ПРОВЕРКОЙ"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"report_{timestamp}.html"
        
        file_path = self.output_dir / filename
        
        # Определяем цвет по рейтингу
        if report.rating >= 8:
            rating_color = "#4CAF50"  # Зеленый
            rating_text = "Отличное"
        elif report.rating >= 6:
            rating_color = "#8BC34A"  # Светло-зеленый
            rating_text = "Хорошее"
        elif report.rating >= 4:
            rating_color = "#FFC107"  # Оранжевый
            rating_text = "Среднее"
        else:
            rating_color = "#F44336"  # Красный
            rating_text = "Плохое"
        
        # HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Отчет аудита nAUDIT</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .rating-block {{
            background: {rating_color};
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px;
            margin: 30px;
        }}
        
        .rating-value {{
            font-size: 3em;
            font-weight: bold;
            display: block;
        }}
        
        .rating-text {{
            font-size: 1.2em;
            margin-top: 10px;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        section {{
            margin-bottom: 40px;
        }}
        
        section h2 {{
            font-size: 1.8em;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .metric-card {{
            background: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .metric-card h3 {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        
        .metric-card .value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
        }}
        
        .breakdown {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
        }}
        
        .breakdown-item {{
            background: #f9f9f9;
            padding: 15px;
            border-radius: 6px;
            border-left: 3px solid #667eea;
        }}
        
        .breakdown-item .label {{
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}
        
        .breakdown-item .score {{
            font-size: 1.4em;
            color: #667eea;
        }}
        
        .issues-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        .issues-table th {{
            background: #f0f0f0;
            padding: 12px;
            text-align: left;
            font-weight: bold;
            border-bottom: 2px solid #ddd;
        }}
        
        .issues-table td {{
            padding: 12px;
            border-bottom: 1px solid #eee;
        }}
        
        .issues-table tr:hover {{
            background: #f9f9f9;
        }}
        
        .severity-critical {{ color: #f44336; font-weight: bold; }}
        .severity-high {{ color: #ff9800; font-weight: bold; }}
        .severity-medium {{ color: #ffc107; }}
        .severity-low {{ color: #4caf50; }}
        
        .summary-text {{
            background: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
            line-height: 1.6;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
        }}
        
        footer {{
            background: #f0f0f0;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #ddd;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 40px;
            color: #999;
        }}
        
        .empty-state svg {{
            width: 100px;
            height: 100px;
            margin-bottom: 20px;
            opacity: 0.5;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Отчет об аудите кода</h1>
            <p>nAUDIT v4.0 - Глубокий анализ проекта</p>
        </header>
        
        <div class="rating-block">
            <span class="rating-value">{report.rating:.1f}</span>
            <span class="rating-text">{rating_text} состояние проекта</span>
        </div>
        
        <div class="content">
            <!-- Проект -->
            <section>
                <h2>📁 Информация о проекте</h2>
                <div class="metric-card">
                    <strong>Путь:</strong> {html.escape(report.project_path)}
                </div>
                <div class="metric-card">
                    <strong>Дата анализа:</strong> {report.timestamp}
                </div>
            </section>
            
            <!-- Основные метрики -->
            <section>
                <h2>📈 Основные метрики</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>📄 Python файлов</h3>
                        <div class="value">{report.metrics.total_files}</div>
                    </div>
                    <div class="metric-card">
                        <h3>📝 Строк кода</h3>
                        <div class="value">{report.metrics.total_lines:,}</div>
                    </div>
                    <div class="metric-card">
                        <h3>⚙️ Функций</h3>
                        <div class="value">{report.metrics.total_functions}</div>
                    </div>
                    <div class="metric-card">
                        <h3>🏗️ Классов</h3>
                        <div class="value">{report.metrics.total_classes}</div>
                    </div>
                </div>
            </section>
            
            <!-- Оценки по компонентам -->
            <section>
                <h2>🎯 Оценка по компонентам</h2>
                <div class="breakdown">
"""
        
        for component, score in report.rating_breakdown.items():
            html_content += f"""
                    <div class="breakdown-item">
                        <div class="label">{component}</div>
                        <div class="score">{score:.1f}/10</div>
                    </div>
"""
        
        html_content += """
                </div>
            </section>
            
"""
        
        # Ошибки кода
        if report.metrics.code_issues:
            html_content += f"""
            <section>
                <h2>🔴 Проблемы в коде ({len(report.metrics.code_issues)})</h2>
                <table class="issues-table">
                    <tr>
                        <th>Файл</th>
                        <th>Строка</th>
                        <th>Код</th>
                        <th>Сообщение</th>
                        <th>Серьезность</th>
                    </tr>
"""
            for issue in sorted(report.metrics.code_issues, key=lambda x: (x.file_path, x.line_number))[:50]:
                severity_class = f"severity-{issue.severity.name.lower()}"
                html_content += f"""
                    <tr>
                        <td>{html.escape(Path(issue.file_path).name)}</td>
                        <td>{issue.line_number}</td>
                        <td><strong>{issue.code}</strong></td>
                        <td>{html.escape(issue.message[:60])}</td>
                        <td class="{severity_class}">{issue.severity.value}</td>
                    </tr>
"""
            
            if len(report.metrics.code_issues) > 50:
                html_content += f"""
                    <tr>
                        <td colspan="5" style="text-align: center; font-style: italic;">
                            ... и еще {len(report.metrics.code_issues) - 50} проблем
                        </td>
                    </tr>
"""
            
            html_content += """
                </table>
            </section>
"""
        
        # Проблемы безопасности
        if report.metrics.security_issues:
            html_content += f"""
            <section>
                <h2>⚠️ Проблемы безопасности ({len(report.metrics.security_issues)})</h2>
                <table class="issues-table">
                    <tr>
                        <th>Файл</th>
                        <th>Строка</th>
                        <th>Код</th>
                        <th>Сообщение</th>
                    </tr>
"""
            for issue in report.metrics.security_issues[:20]:
                html_content += f"""
                    <tr>
                        <td>{html.escape(Path(issue.file_path).name)}</td>
                        <td>{issue.line_number}</td>
                        <td><strong>{issue.code}</strong></td>
                        <td>{html.escape(issue.message)}</td>
                    </tr>
"""
            
            if len(report.metrics.security_issues) > 20:
                html_content += f"""
                    <tr>
                        <td colspan="4" style="text-align: center; font-style: italic;">
                            ... и еще {len(report.metrics.security_issues) - 20} проблем
                        </td>
                    </tr>
"""
            
            html_content += """
                </table>
            </section>
"""
        
        # Резюме
        html_content += f"""
            <section>
                <h2>📝 Резюме</h2>
                <div class="summary-text">{html.escape(report.summary)}</div>
            </section>
        </div>
        
        <footer>
            <p>Отчет сгенерирован nAUDIT v4.0 • {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</p>
        </footer>
    </div>
</body>
</html>
"""
        
        # Пишем HTML
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # ПРОВЕРЯЕМ что файл существует и не пуст
        if not file_path.exists():
            raise FileNotFoundError(f"Не удалось создать файл: {file_path}")
        
        size = file_path.stat().st_size
        if size < 1000:
            raise ValueError(f"Файл слишком маленький ({size} bytes): {file_path}")
        
        print(f"✅ HTML отчет сохранен: {file_path} ({size} bytes)")
        return file_path
    
    def save_csv_report(self, report, filename: str = None) -> Path:
        """Сохранить CSV отчет с ПРОВЕРКОЙ"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"issues_{timestamp}.csv"
        
        file_path = self.output_dir / filename
        
        lines = []
        lines.append("Файл,Строка,Колонка,Код,Сообщение,Тип,Серьезность,Инструмент")
        
        # Ошибки кода
        for issue in report.metrics.code_issues:
            line = f'{Path(issue.file_path).name},{issue.line_number},{issue.column},"{issue.code}","{issue.message}","code","{issue.severity.name}","{issue.tool}"'
            lines.append(line)
        
        # Проблемы безопасности
        for issue in report.metrics.security_issues:
            line = f'{Path(issue.file_path).name},{issue.line_number},0,"{issue.code}","{issue.message}","security","{issue.severity.name}","{issue.tool}"'
            lines.append(line)
        
        # Пишем CSV
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        # ПРОВЕРЯЕМ что файл существует и не пуст
        if not file_path.exists():
            raise FileNotFoundError(f"Не удалось создать файл: {file_path}")
        
        size = file_path.stat().st_size
        if size < 50:
            raise ValueError(f"Файл слишком маленький ({size} bytes): {file_path}")
        
        print(f"✅ CSV отчет сохранен: {file_path} ({size} bytes)")
        return file_path
    
    def list_reports(self) -> List[Path]:
        """Список всех отчетов"""
        reports = sorted(self.output_dir.glob("report_*.json"))
        return reports
    
    def verify_file_saved(self, file_path: Path, min_size: int = 100) -> bool:
        """Проверить что файл действительно сохранен"""
        if not file_path.exists():
            return False
        
        size = file_path.stat().st_size
        return size >= min_size
