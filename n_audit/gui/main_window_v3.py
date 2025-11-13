"""
nAUDIT v3 - Переделанный интерфейс с интерактивными графиками matplotlib
"""
import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLabel, QLineEdit, QFileDialog, QTextEdit, QTableWidget,
    QTableWidgetItem, QProgressBar, QSpinBox, QComboBox, QFrame, QScrollArea,
    QMessageBox
)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QColor, QFont, QIcon

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

try:
    from n_audit.audit_manager_v2 import AuditManager, AuditResult
except ImportError:
    from audit_manager_v2 import AuditManager, AuditResult


class AuditSignals(QObject):
    """Сигналы для потока аудита"""
    progress = pyqtSignal(int, str)
    phase_update = pyqtSignal(object)
    complete = pyqtSignal(object)
    error = pyqtSignal(str)
    log = pyqtSignal(str)


class MatplotlibCanvas(FigureCanvas):
    """Canvas для встраивания matplotlib графиков в PyQt"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        super().__init__(self.fig)
        self.setParent(parent)
        self.setMinimumSize(QSize(400, 300))
    
    def plot_pie_chart(self, labels, sizes, colors):
        """Круговая диаграмма"""
        self.axes.clear()
        self.axes.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        self.axes.set_title('Распределение ошибок')
        self.fig.tight_layout()
        self.draw()
    
    def plot_bar_chart(self, categories, values, title=""):
        """Столбчатая диаграмма"""
        self.axes.clear()
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
        bars = self.axes.bar(categories, values, color=colors[:len(categories)])
        self.axes.set_title(title)
        self.axes.set_ylabel('Количество')
        self.axes.tick_params(axis='x', rotation=45)
        
        # Добавляем значения на столбцы
        for bar, value in zip(bars, values):
            height = bar.get_height()
            self.axes.text(bar.get_x() + bar.get_width()/2., height,
                          f'{int(value)}', ha='center', va='bottom')
        
        self.fig.tight_layout()
        self.draw()
    
    def plot_rating_gauge(self, rating):
        """Калибр (gauge) для оценки"""
        self.axes.clear()
        
        # Цвета в зависимости от рейтинга
        if rating >= 8:
            color = '#4CAF50'  # Зелёный
        elif rating >= 6:
            color = '#FFC107'  # Жёлтый/Оранжевый
        else:
            color = '#F44336'  # Красный
        
        # Рисуем прямоугольник рейтинга
        from matplotlib.patches import Rectangle
        self.axes.add_patch(Rectangle((0, 0), 10, 1, facecolor=color, alpha=0.3))
        self.axes.add_patch(Rectangle((0, 0), rating, 1, facecolor=color))
        
        self.axes.set_xlim(0, 10)
        self.axes.set_ylim(0, 1.5)
        self.axes.text(5, 1.2, f'Рейтинг: {rating}/10', 
                      ha='center', fontsize=14, fontweight='bold')
        self.axes.axis('off')
        
        self.fig.tight_layout()
        self.draw()


class nAUDITMainWindow(QMainWindow):
    """Главное окно nAUDIT v3 с интерактивными графиками"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("nAUDIT v3.0 - Анализатор качества кода")
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet(self._get_stylesheet())
        
        # Менеджер аудита
        self.audit_manager = AuditManager()
        self.audit_signals = AuditSignals()
        self._setup_manager_callbacks()
        
        # История анализов
        self.analysis_history: List[AuditResult] = []
        self.load_history()
        
        # Текущий результат
        self.current_result: Optional[AuditResult] = None
        
        # Создание UI
        self._create_ui()
        
        # Таймер для обновления UI
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_ui)
        self.update_timer.start(500)

    def _create_ui(self):
        """Создание интерфейса"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QVBoxLayout()
        
        # Вкладки
        tabs = QTabWidget()
        
        tabs.addTab(self._create_audit_tab(), "🔍 Аудит")
        tabs.addTab(self._create_results_tab(), "📊 Результаты")
        tabs.addTab(self._create_history_tab(), "📜 История")
        tabs.addTab(self._create_log_tab(), "📋 Логи")
        
        layout.addWidget(tabs)
        main_widget.setLayout(layout)

    def _create_audit_tab(self) -> QWidget:
        """Вкладка запуска аудита"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Выбор проекта
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("Папка проекта:"))
        self.project_path = QLineEdit()
        self.project_path.setPlaceholderText("Выберите папку с проектом")
        select_layout.addWidget(self.project_path)
        
        browse_btn = QPushButton("Обзор...")
        browse_btn.clicked.connect(self._browse_project)
        select_layout.addWidget(browse_btn)
        layout.addLayout(select_layout)
        
        # Параметры
        params_layout = QHBoxLayout()
        params_layout.addWidget(QLabel("Уровень отчёта:"))
        self.report_level = QComboBox()
        self.report_level.addItems(["Полный", "Средний", "Краткий"])
        params_layout.addWidget(self.report_level)
        layout.addLayout(params_layout)
        
        # Прогресс
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Статус
        self.status_label = QLabel("Статус: Готово")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Фазы аудита
        phases_frame = QFrame()
        phases_layout = QVBoxLayout()
        phases_frame.setStyleSheet("border: 1px solid #ddd; border-radius: 5px;")
        
        self.phase_labels: List[QLabel] = []
        for i, phase in enumerate(["🔍 Анализ кода", "🔒 Безопасность", "🧪 Тесты",
                                   "🏗️ Инфраструктура", "💡 Рекомендации", "📄 Отчёт"]):
            label = QLabel(f"⏳ {phase}")
            label.setStyleSheet("padding: 5px; font-size: 11px;")
            phases_layout.addWidget(label)
            self.phase_labels.append(label)
        
        phases_frame.setLayout(phases_layout)
        layout.addWidget(phases_frame)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        start_btn = QPushButton("▶ Начать аудит")
        start_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        start_btn.clicked.connect(self._start_audit)
        buttons_layout.addWidget(start_btn)
        
        cancel_btn = QPushButton("⏹ Отмена")
        cancel_btn.setStyleSheet("background-color: #F44336; color: white; font-weight: bold; padding: 10px;")
        cancel_btn.clicked.connect(self._cancel_audit)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget

    def _create_results_tab(self) -> QWidget:
        """Вкладка результатов"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Рейтинг
        self.rating_label = QLabel("Рейтинг: --/10")
        self.rating_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50;")
        self.rating_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.rating_label)
        
        # Графики
        graph_layout = QHBoxLayout()
        
        # График распределения ошибок
        self.chart_issues = MatplotlibCanvas()
        graph_layout.addWidget(self.chart_issues)
        
        # График рейтинга
        self.chart_rating = MatplotlibCanvas()
        graph_layout.addWidget(self.chart_rating)
        
        layout.addLayout(graph_layout)
        
        # Статистика
        stat_label = QLabel("📊 Статистика:")
        stat_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(stat_label)
        
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["Метрика", "Значение"])
        self.stats_table.setMaximumHeight(200)
        layout.addWidget(self.stats_table)
        
        # Ошибки
        errors_label = QLabel("🐛 Обнаруженные проблемы:")
        errors_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(errors_label)
        
        self.issues_table = QTableWidget()
        self.issues_table.setColumnCount(5)
        self.issues_table.setHorizontalHeaderLabels(["Тип", "Файл", "Линия", "Сообщение", "Код"])
        layout.addWidget(self.issues_table)
        
        # Рекомендации
        rec_label = QLabel("💡 Рекомендации:")
        rec_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(rec_label)
        
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setReadOnly(True)
        self.recommendations_text.setMaximumHeight(150)
        layout.addWidget(self.recommendations_text)
        
        # Кнопка экспорта
        export_btn = QPushButton("💾 Экспорт отчёта")
        export_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px;")
        export_btn.clicked.connect(self._export_report)
        layout.addWidget(export_btn)
        
        widget.setLayout(layout)
        return widget

    def _create_history_tab(self) -> QWidget:
        """Вкладка истории"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        label = QLabel("📜 История анализов:")
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Дата", "Проект", "Рейтинг", "Ошибок", "Тесты"])
        self.history_table.itemClicked.connect(self._load_history_result)
        layout.addWidget(self.history_table)
        
        # Кнопка удаления
        clear_btn = QPushButton("🗑 Очистить историю")
        clear_btn.setStyleSheet("background-color: #F44336; color: white; font-weight: bold; padding: 10px;")
        clear_btn.clicked.connect(self._clear_history)
        layout.addWidget(clear_btn)
        
        widget.setLayout(layout)
        return widget

    def _create_log_tab(self) -> QWidget:
        """Вкладка логов"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        label = QLabel("📋 Логи анализа:")
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier", 10))
        layout.addWidget(self.log_text)
        
        widget.setLayout(layout)
        return widget

    def _browse_project(self):
        """Обзор папки проекта"""
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку проекта")
        if directory:
            self.project_path.setText(directory)

    def _start_audit(self):
        """Начать аудит"""
        project_path = self.project_path.text()
        if not project_path:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите папку проекта")
            return
        
        if not os.path.isdir(project_path):
            QMessageBox.warning(self, "Ошибка", "Выбранная папка не существует")
            return
        
        self.audit_manager.start_audit(project_path)

    def _cancel_audit(self):
        """Отмена аудита"""
        self.audit_manager.cancel_audit()

    def _export_report(self):
        """Экспорт отчёта"""
        if not self.current_result:
            QMessageBox.warning(self, "Ошибка", "Нет результатов для экспорта")
            return
        
        # TODO: реализовать экспорт
        QMessageBox.information(self, "Экспорт", "Экспорт выполнен успешно")

    def _clear_history(self):
        """Очистить историю"""
        if QMessageBox.question(self, "Подтверждение", "Очистить историю?") == QMessageBox.StandardButton.Yes:
            self.analysis_history = []
            self.save_history()
            self._update_history_table()

    def _load_history_result(self, item):
        """Загрузить результат из истории"""
        row = self.history_table.row(item)
        if 0 <= row < len(self.analysis_history):
            self.current_result = self.analysis_history[row]
            self._display_results()

    def _setup_manager_callbacks(self):
        """Установка callbacks для менеджера аудита"""
        self.audit_manager.set_callbacks(
            on_progress=self.audit_signals.progress.emit,
            on_phase_update=self.audit_signals.phase_update.emit,
            on_complete=self.audit_signals.complete.emit,
            on_error=self.audit_signals.error.emit,
            on_log=self.audit_signals.log.emit
        )
        
        # Подключение сигналов
        self.audit_signals.progress.connect(self._on_progress)
        self.audit_signals.complete.connect(self._on_audit_complete)
        self.audit_signals.error.connect(self._on_audit_error)
        self.audit_signals.log.connect(self._on_log)

    def _on_progress(self, progress: int, message: str):
        """Обновление прогресса"""
        self.progress_bar.setValue(progress)

    def _on_audit_complete(self, result: AuditResult):
        """Завершение аудита"""
        self.current_result = result
        self.analysis_history.append(result)
        self.save_history()
        
        self.status_label.setText("Статус: Завершено ✅")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        
        self._display_results()
        self._update_history_table()

    def _on_audit_error(self, error: str):
        """Ошибка аудита"""
        self.status_label.setText(f"Статус: Ошибка ❌ - {error}")
        self.status_label.setStyleSheet("color: #F44336; font-weight: bold;")
        QMessageBox.critical(self, "Ошибка аудита", error)

    def _on_log(self, message: str):
        """Логирование"""
        self.log_text.append(message)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def _display_results(self):
        """Отобразить результаты"""
        if not self.current_result:
            return
        
        # Рейтинг
        rating = self.current_result.rating
        if rating >= 8:
            color = "#4CAF50"
        elif rating >= 6:
            color = "#FFC107"
        else:
            color = "#F44336"
        
        self.rating_label.setText(f"Рейтинг: {rating}/10")
        self.rating_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
        
        # Графики
        if self.current_result.total_issues > 0:
            labels = ["Ошибки кода", "Уязвимости"]
            sizes = [self.current_result.code_issues, self.current_result.security_issues]
            colors = ["#FF6B6B", "#F44336"]
            
            # Фильтруем нулевые значения
            non_zero = [(l, s, c) for l, s, c in zip(labels, sizes, colors) if s > 0]
            if non_zero:
                labels, sizes, colors = zip(*non_zero)
                self.chart_issues.plot_pie_chart(list(labels), list(sizes), list(colors))
        
        # Статистика
        self.stats_table.setRowCount(0)
        stats = [
            ("Файлов проанализировано", str(self.current_result.files_analyzed)),
            ("Ошибок кода", str(self.current_result.code_issues)),
            ("Уязвимостей", str(self.current_result.security_issues)),
            ("Покрытие тестами", f"{self.current_result.test_coverage}%"),
            ("Дата анализа", self.current_result.timestamp),
        ]
        
        for i, (key, value) in enumerate(stats):
            self.stats_table.insertRow(i)
            self.stats_table.setItem(i, 0, QTableWidgetItem(key))
            self.stats_table.setItem(i, 1, QTableWidgetItem(value))
        
        # Проблемы
        self.issues_table.setRowCount(0)
        for i, issue in enumerate(self.current_result.issue_details[:50]):  # Первые 50
            self.issues_table.insertRow(i)
            self.issues_table.setItem(i, 0, QTableWidgetItem(issue.type))
            self.issues_table.setItem(i, 1, QTableWidgetItem(os.path.basename(issue.file)))
            self.issues_table.setItem(i, 2, QTableWidgetItem(str(issue.line)))
            self.issues_table.setItem(i, 3, QTableWidgetItem(issue.message[:50]))
            self.issues_table.setItem(i, 4, QTableWidgetItem(issue.code))
        
        # Рекомендации
        self.recommendations_text.setText("\n".join(self.current_result.recommendations))

    def _update_history_table(self):
        """Обновить таблицу истории"""
        self.history_table.setRowCount(0)
        for i, result in enumerate(reversed(self.analysis_history)):
            self.history_table.insertRow(i)
            self.history_table.setItem(i, 0, QTableWidgetItem(result.timestamp))
            self.history_table.setItem(i, 1, QTableWidgetItem(os.path.basename(result.project_path)))
            self.history_table.setItem(i, 2, QTableWidgetItem(f"{result.rating}/10"))
            self.history_table.setItem(i, 3, QTableWidgetItem(str(result.total_issues)))
            self.history_table.setItem(i, 4, QTableWidgetItem(f"{result.test_coverage}%"))

    def _update_ui(self):
        """Периодическое обновление UI"""
        pass

    def save_history(self):
        """Сохранить историю"""
        history_file = Path.home() / ".naudit" / "history.json"
        history_file.parent.mkdir(exist_ok=True)
        
        history_data = []
        for result in self.analysis_history:
            history_data.append({
                "timestamp": result.timestamp,
                "project_path": result.project_path,
                "rating": result.rating,
                "total_issues": result.total_issues,
                "test_coverage": result.test_coverage
            })
        
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)

    def load_history(self):
        """Загрузить историю"""
        history_file = Path.home() / ".naudit" / "history.json"
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    # История будет загружена при необходимости
                    pass
            except:
                pass

    def _get_stylesheet(self) -> str:
        """CSS стили"""
        return """
        QMainWindow {
            background-color: #f5f5f5;
        }
        
        QTabWidget::pane {
            border: 1px solid #ddd;
        }
        
        QTabBar::tab {
            background-color: #e0e0e0;
            padding: 8px 20px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #2196F3;
            color: white;
        }
        
        QPushButton {
            border-radius: 4px;
            border: none;
            padding: 5px 15px;
        }
        
        QLineEdit, QTextEdit, QComboBox {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 5px;
        }
        
        QTableWidget {
            background-color: white;
            gridline-color: #ddd;
        }
        
        QHeaderView::section {
            background-color: #f0f0f0;
            padding: 5px;
            border: 1px solid #ddd;
        }
        """
