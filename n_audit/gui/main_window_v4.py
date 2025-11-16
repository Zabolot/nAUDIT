#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Главное окно v4 - профессиональный интерфейс с полной функциональностью.

Включает:
- Инструменты аудита
- Результаты с деревом ошибок
- Визуализация метрик
- Рекомендации
- Помощь и информация о программе
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QFileDialog, QLabel, QProgressBar, QTextEdit,
    QComboBox, QSpinBox, QCheckBox, QScrollArea, QFrame, QStatusBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor
from datetime import datetime
from pathlib import Path
import sys
import os
import logging

# Get logger
logger = logging.getLogger(__name__)

# Импортируем наши компоненты
try:
    from n_audit.audit_engine import AuditEngine
    from n_audit.report_generator import ReportGenerator
    from n_audit.recommendations_engine import RecommendationsEngine
    from n_audit.gui.error_visualization import ErrorVisualizationWidget
    from n_audit.gui.metrics_visualizer import MetricsVisualizer
except ImportError:
    # Если импорт не работает (dev режим)
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from n_audit.audit_engine import AuditEngine
    from n_audit.report_generator import ReportGenerator
    from n_audit.recommendations_engine import RecommendationsEngine
    from n_audit.gui.error_visualization import ErrorVisualizationWidget
    from n_audit.gui.metrics_visualizer import MetricsVisualizer


class AuditWorker(QThread):
    """Worker для запуска аудита в отдельном потоке"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path
        logger.info(f"AuditWorker created for: {project_path}")
    
    def run(self):
        try:
            logger.info(f"Starting audit for: {self.project_path}")
            self.progress.emit(f"Инициализация аудита...")
            
            engine = AuditEngine()
            logger.debug("AuditEngine created")
            
            self.progress.emit(f"Запуск анализа...")
            logger.info(f"Running AuditEngine.audit()")
            
            report = engine.audit(self.project_path)
            
            logger.info(f"Audit completed successfully")
            logger.info(f"Report generated: {type(report)}")
            
            # Логируем результаты
            if hasattr(report, 'metrics'):
                if hasattr(report.metrics, 'code_issues'):
                    logger.info(f"Code issues found: {len(report.metrics.code_issues)}")
                if hasattr(report.metrics, 'security_issues'):
                    logger.info(f"Security issues found: {len(report.metrics.security_issues)}")
            
            self.progress.emit(f"Завершено!")
            self.finished.emit(report)
            
        except Exception as e:
            error_msg = f"Ошибка аудита: {str(e)}"
            logger.error(f"Critical error in audit: {error_msg}", exc_info=True)
            logger.error(f"Exception type: {type(e).__name__}")
            self.error.emit(error_msg)
            self.progress.emit(f"Ошибка: {error_msg}")
            raise  # Re-raise для дальнейшего анализа


class MainWindowV4(QMainWindow):
    """Главное окно v4 - полный интерфейс"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("nAUDIT v4.0 - Профессиональный аудит кода")
        self.setGeometry(100, 100, 1400, 900)
        
        # Компоненты
        self.engine = AuditEngine()
        self.report_generator = ReportGenerator()
        self.recommendations_engine = RecommendationsEngine()
        
        self.current_report = None
        self.audit_worker = None
        
        # UI
        self.init_ui()
        self.setStyleSheet(self._get_stylesheet())
    
    def init_ui(self):
        """Инициализировать UI"""
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Панель инструментов
        toolbar_layout = QHBoxLayout()
        
        # Выбор папки
        self.path_label = QLabel("Папка не выбрана")
        self.path_label.setStyleSheet("color: #666; font-size: 11px;")
        toolbar_layout.addWidget(self.path_label)
        
        self.browse_button = QPushButton("📁 Выбрать папку")
        self.browse_button.clicked.connect(self._on_browse)
        toolbar_layout.addWidget(self.browse_button)
        
        self.audit_button = QPushButton("🔬 Запустить аудит")
        self.audit_button.clicked.connect(self._on_audit)
        self.audit_button.setEnabled(False)
        toolbar_layout.addWidget(self.audit_button)
        
        self.export_button = QPushButton("💾 Экспорт")
        self.export_button.clicked.connect(self._on_export)
        self.export_button.setEnabled(False)
        toolbar_layout.addWidget(self.export_button)
        
        toolbar_layout.addStretch()
        
        # Инфо кнопка
        self.info_button = QPushButton("ℹ️ Справка")
        self.info_button.clicked.connect(self._on_help)
        toolbar_layout.addWidget(self.info_button)
        
        layout.addLayout(toolbar_layout)
        
        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Вкладки
        self.tabs = QTabWidget()
        
        # Tab 1: Результаты
        self.results_widget = self._create_results_tab()
        self.tabs.addTab(self.results_widget, "📊 Результаты")
        
        # Tab 2: Ошибки (дерево + граф)
        self.tree_widget = ErrorVisualizationWidget()
        self.tabs.addTab(self.tree_widget, "🌳 Ошибки")
        
        # Tab 3: Визуализация
        self.visualizer = MetricsVisualizer()
        self.tabs.addTab(self.visualizer, "📈 Графики")
        
        # Tab 4: Рекомендации
        self.recommendations_widget = self._create_recommendations_tab()
        self.tabs.addTab(self.recommendations_widget, "💡 Рекомендации")
        
        # Tab 5: История
        self.history_widget = self._create_history_tab()
        self.tabs.addTab(self.history_widget, "📜 История")
        
        # Tab 6: О программе
        self.about_widget = self._create_about_tab()
        self.tabs.addTab(self.about_widget, "ℹ️ О программе")
        
        layout.addWidget(self.tabs)
        
        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе")
    
    def _create_results_tab(self) -> QWidget:
        """Создать вкладку с результатами"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Информация о проекте
        self.project_info = QTextEdit()
        self.project_info.setReadOnly(True)
        self.project_info.setPlaceholderText("Выберите папку и запустите аудит...")
        layout.addWidget(self.project_info)
        
        return widget
    
    def _create_recommendations_tab(self) -> QWidget:
        """Создать вкладку с рекомендациями"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Список рекомендаций
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setReadOnly(True)
        self.recommendations_text.setPlaceholderText("Рекомендации появятся после аудита...")
        layout.addWidget(self.recommendations_text)
        
        return widget
    
    def _create_history_tab(self) -> QWidget:
        """Создать вкладку с историей"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        layout.addWidget(self.history_text)
        
        self._update_history()
        
        return widget
    
    def _create_about_tab(self) -> QWidget:
        """Создать вкладку о программе"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Стилизованный текст
        about_text = """
        <h1 style="color: #667eea;">🔬 nAUDIT v4.0</h1>
        
        <h2>Профессиональный аудит кода на Python</h2>
        
        <p><b>Что это?</b></p>
        <p>nAUDIT - это мощный инструмент для глубокого анализа Python проектов. Программа проверяет:</p>
        <ul>
            <li>✅ Качество кода (стиль, сложность)</li>
            <li>✅ Безопасность (уязвимости, опасные паттерны)</li>
            <li>✅ Тестирование (покрытие, наличие тестов)</li>
            <li>✅ Структуру проекта (README, setup.py, Git)</li>
            <li>✅ Документация (docstrings, комментарии)</li>
        </ul>
        
        <p><b>Как использовать?</b></p>
        <ol>
            <li>Нажмите "📁 Выбрать папку"</li>
            <li>Выберите папку с Python кодом</li>
            <li>Нажмите "🔬 Запустить аудит"</li>
            <li>Смотрите результаты во вкладках</li>
            <li>Используйте 💾 Экспорт для сохранения отчета</li>
        </ol>
        
        <p><b>Вкладки:</b></p>
        <ul>
            <li>📊 <b>Результаты</b> - основной рейтинг и метрики</li>
            <li>🌳 <b>Ошибки</b> - интерактивное дерево всех проблем</li>
            <li>📈 <b>Графики</b> - красивая визуализация метрик</li>
            <li>💡 <b>Рекомендации</b> - конкретные советы по улучшению</li>
            <li>📜 <b>История</b> - список всех отчетов</li>
        </ul>
        
        <p><b>Интерпретация рейтинга:</b></p>
        <ul>
            <li>🔴 1.0-3.0 - Плохое состояние, нужны срочные правки</li>
            <li>🟠 3.0-5.0 - Есть проблемы, требует внимания</li>
            <li>🟡 5.0-7.0 - Среднее состояние, есть чему улучшаться</li>
            <li>🟢 7.0-10.0 - Хорошее состояние, качественный код</li>
        </ul>
        
        <p><b>Версия:</b> 4.0</p>
        <p><b>Лицензия:</b> MIT</p>
        <p><b>GitHub:</b> https://github.com/yourusername/naudit</p>
        
        <hr>
        <p style="color: #999; font-size: 11px;">
        nAUDIT использует: pylint, flake8, mypy, bandit, coverage<br>
        Интерфейс: PyQt6 | Графики: matplotlib
        </p>
        """
        
        about_label = QTextEdit()
        about_label.setReadOnly(True)
        about_label.setHtml(about_text)
        layout.addWidget(about_label)
        
        return widget
    
    def _on_browse(self):
        """Обработчик выбора папки"""
        path = QFileDialog.getExistingDirectory(self, "Выберите папку проекта")
        if path:
            self.selected_path = path
            self.path_label.setText(f"Папка: {Path(path).name}")
            self.audit_button.setEnabled(True)
            self.status_bar.showMessage(f"Выбрана папка: {path}")
    
    def _on_audit(self):
        """Запустить аудит"""
        if not hasattr(self, 'selected_path'):
            logger.warning("No path selected for audit")
            return
        
        logger.info(f"Audit button clicked, path: {self.selected_path}")
        
        self.progress_bar.setVisible(True)
        self.audit_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.status_bar.showMessage("Аудит в процессе...")
        
        self.audit_worker = AuditWorker(self.selected_path)
        self.audit_worker.finished.connect(self._on_audit_finished)
        self.audit_worker.error.connect(self._on_audit_error)
        self.audit_worker.start()
    
    def _on_audit_finished(self, report):
        """Обработчик завершения аудита"""
        try:
            logger.info("Audit finished successfully")
            self.current_report = report
            self.progress_bar.setVisible(False)
            self.audit_button.setEnabled(True)
            self.export_button.setEnabled(True)
            self.status_bar.showMessage("✅ Аудит завершен")
            
            logger.debug(f"Report type: {type(report)}")
            logger.debug(f"Report dir: {dir(report)}")
            
            # Обновляем все вкладки
            self._update_results()
            self._update_recommendations()
            self._update_history()
            
            # Дерево ошибок
            logger.info("Populating tree widget with report")
            self.tree_widget.populate_from_report(report, project_root=self.selected_path)
            
            # Графики
            logger.info("Setting report in visualizer")
            self.visualizer.set_report(report)
            
            logger.info("Audit process complete")
            
        except Exception as e:
            logger.error(f"Error in _on_audit_finished: {e}", exc_info=True)
            self._on_audit_error(f"Ошибка обработки результатов: {e}")
    
    def _on_audit_error(self, error):
        """Обработчик ошибки аудита"""
        logger.error(f"Audit error: {error}")
        
        self.progress_bar.setVisible(False)
        self.audit_button.setEnabled(True)
        self.status_bar.showMessage(f"❌ Ошибка: {error}")
        
        error_html = f"""
        <b>❌ Ошибка при аудите:</b><br>
        <pre style="color: red; font-family: monospace; white-space: pre-wrap;">
        {error}
        </pre>
        <br>
        <small style="color: gray;">
        <b>Подсказка:</b> Подробности ошибки записаны в логи.<br>
        Папка логов: {Path.home() / '.naudit' / 'logs'}<br>
        <b>Стандартные причины:</b><br>
        - В проекте есть файлы, которые невозможно разобрать<br>
        - Недостаточно памяти для анализа большого проекта<br>
        - Ошибка в анализаторе при обработке специальных синтаксисных конструкций
        </small>
        """
        self.project_info.setHtml(error_html)
    
    def _on_export(self):
        """Экспортировать отчет и граф"""
        if not self.current_report:
            return
        
        # Сохраняем все форматы отчета
        try:
            json_path = self.report_generator.save_json_report(self.current_report)
            html_path = self.report_generator.save_html_report(self.current_report)
            csv_path = self.report_generator.save_csv_report(self.current_report)
            
            # Экспортируем график если он доступен
            graph_path = None
            if self.tree_widget and hasattr(self.tree_widget, 'graph_widget'):
                try:
                    graph_path = self.tree_widget.graph_widget.export_current_graph()
                except Exception as e:
                    print(f"[Export] Ошибка при экспорте графа: {e}")
                    graph_path = None
            
            msg = f"""
            <b>✅ Отчеты успешно сохранены:</b><br><br>
            📄 JSON: {json_path}<br>
            📊 HTML: {html_path}<br>
            📋 CSV: {csv_path}<br>
            """
            
            if graph_path:
                # graph_path теперь может быть папкой с графами
                msg += f"📈 Графы: <a href='file:///{graph_path}'>{graph_path}</a><br>"
            else:
                msg += "<i style='color:#999'>📈 Графы: Не удалось создать графики для экспорта</i><br>"
            
            self.status_bar.showMessage("✅ Отчеты экспортированы")
        except Exception as e:
            msg = f"<b>❌ Ошибка при экспорте:</b><br>{e}"
            self.status_bar.showMessage(f"❌ Ошибка: {e}")
        
        self.project_info.setHtml(msg)
    
    def _on_help(self):
        """Показать справку"""
        self.tabs.setCurrentIndex(5)  # Вкладка о программе
    
    def _update_results(self):
        """Обновить результаты"""
        if not self.current_report:
            return
        
        report = self.current_report
        
        html = f"""
        <h2 style="color: #667eea;">📊 Результаты аудита</h2>
        
        <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 10px 0;">
            <h3 style="font-size: 1.5em; color: #333;">Рейтинг: <span style="color: #667eea; font-size: 2em;">{report.rating:.1f}/10</span></h3>
        </div>
        
        <h3>Основные метрики:</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background: #f9f9f9;">
                <td style="padding: 10px; border: 1px solid #ddd;"><b>Python файлов:</b></td>
                <td style="padding: 10px; border: 1px solid #ddd;">{report.metrics.total_files}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;"><b>Строк кода:</b></td>
                <td style="padding: 10px; border: 1px solid #ddd;">{report.metrics.total_lines:,}</td>
            </tr>
            <tr style="background: #f9f9f9;">
                <td style="padding: 10px; border: 1px solid #ddd;"><b>Функций:</b></td>
                <td style="padding: 10px; border: 1px solid #ddd;">{report.metrics.total_functions}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;"><b>Классов:</b></td>
                <td style="padding: 10px; border: 1px solid #ddd;">{report.metrics.total_classes}</td>
            </tr>
            <tr style="background: #f9f9f9;">
                <td style="padding: 10px; border: 1px solid #ddd;"><b>Ошибок кода:</b></td>
                <td style="padding: 10px; border: 1px solid #ddd;">{len(report.metrics.code_issues)}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;"><b>Проблем безопасности:</b></td>
                <td style="padding: 10px; border: 1px solid #ddd;">{len(report.metrics.security_issues)}</td>
            </tr>
            <tr style="background: #f9f9f9;">
                <td style="padding: 10px; border: 1px solid #ddd;"><b>Покрытие тестами:</b></td>
                <td style="padding: 10px; border: 1px solid #ddd;">{report.metrics.test_coverage:.1f}%</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;"><b>Тест-файлов:</b></td>
                <td style="padding: 10px; border: 1px solid #ddd;">{report.metrics.test_files}</td>
            </tr>
        </table>
        
        <h3 style="margin-top: 20px;">Оценка по компонентам:</h3>
        <ul>
        """
        
        for component, score in report.rating_breakdown.items():
            color = '#4caf50' if score >= 8 else '#ffc107' if score >= 6 else '#ff9800' if score >= 4 else '#f44336'
            html += f'<li><b>{component}:</b> <span style="color: {color}; font-weight: bold;">{score:.1f}/10</span></li>'
        
        html += f"""
        </ul>
        
        <h3 style="margin-top: 20px;">Структура проекта:</h3>
        <ul>
            <li>README.md: {'✅' if report.metrics.has_readme else '❌'}</li>
            <li>setup.py / pyproject.toml: {'✅' if report.metrics.has_setup_py else '❌'}</li>
            <li>Git репозиторий: {'✅' if report.metrics.has_git else '❌'}</li>
            <li>requirements.txt: {'✅' if report.metrics.has_requirements else '❌'}</li>
            <li>Лицензия: {'✅' if report.metrics.has_license else '❌'}</li>
            <li>CI/CD конфиг: {'✅' if report.metrics.has_ci_config else '❌'}</li>
        </ul>
        
        <h3 style="margin-top: 20px;">Резюме:</h3>
        <pre style="background: #f5f5f5; padding: 15px; border-radius: 8px; white-space: pre-wrap;">{report.summary}</pre>
        """
        
        self.project_info.setHtml(html)
    
    def _update_recommendations(self):
        """Обновить рекомендации"""
        if not self.current_report:
            return
        
        recs = self.recommendations_engine.generate_recommendations(self.current_report)
        
        html = "<h2>💡 Рекомендации</h2>"
        
        if not recs:
            html += "<p style='color: #999;'>✅ Рекомендаций нет - отличная работа!</p>"
        else:
            for i, rec in enumerate(recs, 1):
                priority_color = {
                    'CRITICAL': '#f44336',
                    'HIGH': '#ff9800',
                    'MEDIUM': '#ffc107',
                    'LOW': '#4caf50',
                }
                color = priority_color.get(rec.priority.name, '#999')
                
                html += f"""
                <div style="background: #f9f9f9; padding: 15px; margin: 10px 0; border-left: 4px solid {color}; border-radius: 4px;">
                    <h3 style="color: {color}; margin: 0 0 10px 0;">{rec.priority.value} - {rec.title}</h3>
                    <p><b>Проблема:</b> {rec.description}</p>
                    <p><b>Решение:</b> {rec.solution}</p>
                    <p><b>Влияние:</b> {rec.impact}</p>
                    <details>
                        <summary>📝 Пример кода</summary>
                        <pre style="background: #f0f0f0; padding: 10px; overflow-x: auto;"><code>{rec.code_example}</code></pre>
                    </details>
                </div>
                """
        
        self.recommendations_text.setHtml(html)
    
    def _update_history(self):
        """Обновить историю"""
        reports = self.report_generator.list_reports()
        
        html = "<h2>📜 История отчетов</h2>"
        
        if not reports:
            html += "<p style='color: #999;'>История пуста</p>"
        else:
            html += "<table style='width: 100%; border-collapse: collapse;'>"
            html += "<tr style='background: #f0f0f0;'><th style='padding: 10px; border: 1px solid #ddd;'>Отчет</th><th style='padding: 10px; border: 1px solid #ddd;'>Размер</th><th style='padding: 10px; border: 1px solid #ddd;'>Дата</th></tr>"
            
            for report_path in reversed(reports[-20:]):  # Последние 20
                size = report_path.stat().st_size / 1024
                date = report_path.stat().st_mtime
                from datetime import datetime
                date_str = datetime.fromtimestamp(date).strftime('%d.%m.%Y %H:%M')
                html += f"<tr><td style='padding: 10px; border: 1px solid #ddd;'>{report_path.name}</td><td style='padding: 10px; border: 1px solid #ddd;'>{size:.1f} KB</td><td style='padding: 10px; border: 1px solid #ddd;'>{date_str}</td></tr>"
            
            html += "</table>"
        
        self.history_text.setHtml(html)
    
    def _get_stylesheet(self) -> str:
        """Получить стиль приложения"""
        return """
        QMainWindow {
            background-color: #fafafa;
        }
        
        QPushButton {
            background-color: #667eea;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            cursor: pointer;
        }
        
        QPushButton:hover {
            background-color: #764ba2;
        }
        
        QPushButton:pressed {
            background-color: #5568d3;
        }
        
        QPushButton:disabled {
            background-color: #ccc;
            color: #999;
        }
        
        QTabWidget::pane {
            border: 1px solid #ddd;
        }
        
        QTabBar::tab {
            background-color: #e0e0e0;
            color: #333;
            padding: 8px 20px;
            border: 1px solid #ccc;
        }
        
        QTabBar::tab:selected {
            background-color: #667eea;
            color: white;
        }
        
        QTextEdit {
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: white;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        QLabel {
            color: #333;
        }
        
        QProgressBar {
            border: 1px solid #ddd;
            border-radius: 4px;
            height: 10px;
            background-color: #e0e0e0;
        }
        
        QProgressBar::chunk {
            background-color: #667eea;
        }
        
        QStatusBar {
            background-color: #f5f5f5;
            color: #333;
            border-top: 1px solid #ddd;
        }
        """


def main():
    """Запустить приложение"""
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = MainWindowV4()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
