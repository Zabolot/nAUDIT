#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Визуализатор метрик - показывает РЕАЛЬНЫЕ данные в виде интерактивных графиков.

Не будет никаких пустых графиков. Только реальные данные.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional


class MetricsVisualizer(QWidget):
    """Визуализатор метрик с реальными графиками"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.report = None
        self.current_view = 'overview'
        self.init_ui()
    
    def init_ui(self):
        """Инициализировать UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Контрол выбора графика
        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("Показать:"))
        
        self.view_combo = QComboBox()
        self.view_combo.addItem("📊 Общее состояние", "overview")
        self.view_combo.addItem("🎯 Оценка по компонентам", "breakdown")
        self.view_combo.addItem("🔴 Распределение ошибок", "issues")
        self.view_combo.addItem("⚠️ Проблемы по типам", "types")
        self.view_combo.addItem("📈 Распределение по файлам", "files")
        self.view_combo.currentIndexChanged.connect(self._on_view_changed)
        
        control_layout.addWidget(self.view_combo)
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # Canvas для графиков
        self.figure = Figure(figsize=(8, 6), dpi=100, tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
    
    def set_report(self, report):
        """Установить отчет и отобразить графики"""
        self.report = report
        self._draw_overview()
    
    def _on_view_changed(self, index):
        """Обработчик изменения вида графика"""
        view_type = self.view_combo.itemData(index)
        
        self.figure.clear()
        
        if view_type == 'overview':
            self._draw_overview()
        elif view_type == 'breakdown':
            self._draw_breakdown()
        elif view_type == 'issues':
            self._draw_issues_distribution()
        elif view_type == 'types':
            self._draw_issues_by_type()
        elif view_type == 'files':
            self._draw_issues_by_file()
        
        self.canvas.draw()
    
    def _draw_overview(self):
        """Обзорный график - рейтинг и основные метрики"""
        if self.report.is_empty:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Papka pusta', 
                   ha='center', va='center', fontsize=16, transform=ax.transAxes)
            return
        
        # 2x2 сетка графиков
        # 1. Рейтинг как большой циферблат
        ax1 = self.figure.add_subplot(221)
        self._draw_rating_gauge(ax1)
        
        # 2. Основные метрики
        ax2 = self.figure.add_subplot(222)
        self._draw_metrics_bars(ax2)
        
        # 3. Распределение проблем по серьезности
        ax3 = self.figure.add_subplot(223)
        self._draw_severity_distribution(ax3)
        
        # 4. Структура проекта
        ax4 = self.figure.add_subplot(224)
        self._draw_project_structure(ax4)
    
    def _draw_rating_gauge(self, ax):
        """Циферблат рейтинга"""
        rating = self.report.rating
        
        # Круговая диаграмма "спидометра"
        colors = ['#f44336' if rating < 4 else '#ff9800' if rating < 6 else '#8bc34a' if rating < 8 else '#4caf50']
        ax.pie([rating, 10 - rating], 
               startangle=180,
               colors=colors + ['#e0e0e0'],
               wedgeprops=dict(width=0.5))
        
        ax.text(0, 0, f'{rating:.1f}', ha='center', va='center', 
               fontsize=24, fontweight='bold')
        ax.set_title('Рейтинг проекта')
    
    def _draw_metrics_bars(self, ax):
        """Столбики основных метрик"""
        metrics = [
            ('Файлы', min(self.report.metrics.total_files, 100)),
            ('Функции', min(self.report.metrics.total_functions, 100)),
            ('Классы', min(self.report.metrics.total_classes, 50)),
            ('Тесты', self.report.metrics.test_files * 10),
        ]
        
        labels = [m[0] for m in metrics]
        values = [m[1] for m in metrics]
        colors_bar = ['#667eea', '#764ba2', '#f093fb', '#4facfe']
        
        bars = ax.barh(labels, values, color=colors_bar)
        ax.set_xlabel('Количество')
        ax.set_title('Основные метрики')
        ax.set_xlim(0, max(values) * 1.1 if values else 10)
        
        # Добавляем значения на столбики
        for bar, value in zip(bars, values):
            ax.text(value, bar.get_y() + bar.get_height()/2, 
                   f' {int(value)}', va='center', fontsize=9)
    
    def _draw_severity_distribution(self, ax):
        """Распределение проблем по серьезности"""
        all_issues = self.report.metrics.code_issues + self.report.metrics.security_issues
        
        if not all_issues:
            ax.text(0.5, 0.5, '✓ Проблем не найдено', 
                   ha='center', va='center', fontsize=12, transform=ax.transAxes)
            ax.set_title('Распределение проблем')
            return
        
        severities = {}
        severity_colors = {
            'CRITICAL': '#f44336',
            'HIGH': '#ff9800',
            'MEDIUM': '#ffc107',
            'LOW': '#4caf50',
        }
        
        for issue in all_issues:
            sev = issue.severity.name
            severities[sev] = severities.get(sev, 0) + 1
        
        labels = list(severities.keys())
        sizes = list(severities.values())
        colors = [severity_colors.get(l, '#999999') for l in labels]
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                           startangle=90)
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Серьезность проблем')
    
    def _draw_project_structure(self, ax):
        """Наличие структурных элементов проекта"""
        elements = [
            ('README', self.report.metrics.has_readme),
            ('setup.py', self.report.metrics.has_setup_py),
            ('Git', self.report.metrics.has_git),
            ('Тесты', self.report.metrics.test_files > 0),
            ('Лицензия', self.report.metrics.has_license),
            ('CI/CD', self.report.metrics.has_ci_config),
        ]
        
        labels = [e[0] for e in elements]
        values = [1 if e[1] else 0 for e in elements]
        colors_struct = ['#4caf50' if v else '#ffcdd2' for v in values]
        
        bars = ax.bar(range(len(labels)), values, color=colors_struct)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_ylim(0, 1.2)
        ax.set_ylabel('✓ Наличие')
        ax.set_title('Структура проекта')
        
        # Скрываем оси
        ax.set_yticks([0, 1])
        ax.set_yticklabels(['✗', '✓'])
    
    def _draw_breakdown(self):
        """График оценки по компонентам"""
        if not self.report.rating_breakdown:
            return
        
        components = list(self.report.rating_breakdown.keys())
        scores = list(self.report.rating_breakdown.values())
        
        # Радарная диаграмма
        angles = np.linspace(0, 2 * np.pi, len(components), endpoint=False).tolist()
        scores_plot = scores + [scores[0]]
        angles_plot = angles + [angles[0]]
        
        ax = self.figure.add_subplot(111, projection='polar')
        ax.plot(angles_plot, scores_plot, 'o-', linewidth=2, color='#667eea')
        ax.fill(angles_plot, scores_plot, alpha=0.25, color='#667eea')
        ax.set_xticks(angles)
        ax.set_xticklabels(components)
        ax.set_ylim(0, 10)
        ax.set_yticks([2, 4, 6, 8, 10])
        ax.set_yticklabels(['2', '4', '6', '8', '10'])
        ax.set_title('Оценка по компонентам')
        ax.grid(True)
    
    def _draw_issues_distribution(self):
        """Распределение всех ошибок"""
        all_issues = self.report.metrics.code_issues + self.report.metrics.security_issues
        
        if not all_issues:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, '✓ Ошибок не найдено', 
                   ha='center', va='center', fontsize=16, transform=ax.transAxes)
            return
        
        # Группируем по типам
        issue_types = {}
        for issue in all_issues:
            itype = issue.tool
            issue_types[itype] = issue_types.get(itype, 0) + 1
        
        ax = self.figure.add_subplot(111)
        
        types_list = list(issue_types.keys())
        counts = list(issue_types.values())
        colors_type = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00d2fc']
        
        bars = ax.bar(types_list, counts, color=colors_type[:len(types_list)])
        ax.set_ylabel('Количество проблем')
        ax.set_title('Распределение ошибок по инструментам анализа')
        
        # Добавляем значения на столбики
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
    
    def _draw_issues_by_type(self):
        """Проблемы по типам"""
        all_issues = self.report.metrics.code_issues + self.report.metrics.security_issues
        
        if not all_issues:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, '✓ Проблем нет', 
                   ha='center', va='center', fontsize=16, transform=ax.transAxes)
            return
        
        issue_types_map = {
            'error': 'Ошибки',
            'warning': 'Предупреждения',
            'style_issue': 'Стиль',
            'security': 'Безопасность'
        }
        
        type_counts = {}
        for issue in all_issues:
            itype = issue_types_map.get(issue.issue_type, 'Другое')
            type_counts[itype] = type_counts.get(itype, 0) + 1
        
        ax = self.figure.add_subplot(111)
        labels = list(type_counts.keys())
        values = list(type_counts.values())
        colors_type = ['#f44336', '#ff9800', '#ffc107', '#ff5252']
        
        wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%',
                                           colors=colors_type[:len(labels)])
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Проблемы по типам')
    
    def _draw_issues_by_file(self):
        """Проблемы по файлам"""
        all_issues = self.report.metrics.code_issues + self.report.metrics.security_issues
        
        if not all_issues:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, '✓ Ошибок не найдено', 
                   ha='center', va='center', fontsize=16, transform=ax.transAxes)
            return
        
        # Группируем по файлам (берем только имена файлов)
        file_issues = {}
        for issue in all_issues:
            fname = issue.file_path.split('\\')[-1].split('/')[-1]
            file_issues[fname] = file_issues.get(fname, 0) + 1
        
        # Берем топ 10
        sorted_files = sorted(file_issues.items(), key=lambda x: x[1], reverse=True)[:10]
        
        ax = self.figure.add_subplot(111)
        if sorted_files:
            files = [f[0] for f in sorted_files]
            counts = [f[1] for f in sorted_files]
            
            colors_bar = plt.cm.Set3(np.linspace(0, 1, len(files)))
            bars = ax.barh(files, counts, color=colors_bar)
            
            ax.set_xlabel('Количество проблем')
            ax.set_title('Top 10 файлов с проблемами')
            
            # Добавляем значения
            for bar, count in zip(bars, counts):
                ax.text(count, bar.get_y() + bar.get_height()/2,
                       f' {count}', va='center')
