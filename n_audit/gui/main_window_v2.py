"""
Главное окно приложения nAUDIT с улучшенным интерфейсом и визуализацией.
Версия 2.1 - с прогресс-индикаторами и интерактивным отображением.
"""

import os
import sys
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QProgressBar, QTextEdit, QFileDialog, QComboBox, QGroupBox,
    QScrollArea, QFrame, QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QSpinBox, QCheckBox, QGridLayout, QProgressDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread, QSize
from PyQt6.QtGui import QFont, QColor, QTextCursor, QIcon, QPixmap
from PyQt6.QtCore import QTimer, Qt as QtCore_Qt

# Гибкие импорты для совместимости с PyInstaller
try:
    from n_audit.audit_manager import AuditManager, AuditPhase, AuditResult, AuditStatus
    from n_audit.gui.styles import MAIN_STYLESHEET, COLORS
except (ImportError, ModuleNotFoundError):
    try:
        from audit_manager import AuditManager, AuditPhase, AuditResult, AuditStatus
        from styles import MAIN_STYLESHEET, COLORS
    except (ImportError, ModuleNotFoundError):
        from ..audit_manager import AuditManager, AuditPhase, AuditResult, AuditStatus
        from .styles import MAIN_STYLESHEET, COLORS


class AuditWorker(QObject):
    """Рабочий класс для выполнения аудита в отдельном потоке"""
    finished = pyqtSignal()
    progress_updated = pyqtSignal(int, str)
    phase_updated = pyqtSignal(str, int, str)
    audit_completed = pyqtSignal(object)
    audit_error = pyqtSignal(str)

    def __init__(self, audit_manager: AuditManager):
        super().__init__()
        self.audit_manager = audit_manager
        self.audit_manager.set_callbacks(
            on_progress=self._on_progress,
            on_phase_update=self._on_phase_update,
            on_complete=self._on_complete,
            on_error=self._on_error
        )

    def run_audit(self):
        """Запуск аудита"""
        self.audit_manager.start_audit_async()

    def _on_progress(self, progress: int, message: str):
        self.progress_updated.emit(progress, message)

    def _on_phase_update(self, phase: AuditPhase):
        self.phase_updated.emit(phase.name, phase.progress, phase.message)

    def _on_complete(self, result: AuditResult):
        self.audit_completed.emit(result)
        self.finished.emit()

    def _on_error(self, error_msg: str):
        self.audit_error.emit(error_msg)
        self.finished.emit()


class ProgressIndicator(QWidget):
    """Красивый индикатор прогресса фазы"""
    def __init__(self, phase_name: str):
        super().__init__()
        self.phase_name = phase_name
        self.progress = 0
        self.status = "waiting"  # waiting, running, completed, failed
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Иконка статуса
        self.status_label = QLabel("⏳")
        self.status_label.setFont(QFont("Arial", 14))
        
        # Название фазы
        name_label = QLabel(self.phase_name)
        name_font = QFont()
        name_font.setBold(True)
        name_label.setFont(name_font)
        
        # Прогресс
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setMinimumWidth(200)
        
        # Статус текст
        self.status_text = QLabel("Ожидание...")
        
        layout.addWidget(self.status_label)
        layout.addWidget(name_label, 1)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_text)

    def set_progress(self, value: int):
        self.progress = value
        self.progress_bar.setValue(value)

    def set_status(self, status: str, message: str = ""):
        self.status = status
        if status == "waiting":
            self.status_label.setText("⏳")
            self.status_label.setStyleSheet("color: #999;")
        elif status == "running":
            self.status_label.setText("⚙️")
            self.status_label.setStyleSheet("color: #2196F3;")
        elif status == "completed":
            self.status_label.setText("✅")
            self.status_label.setStyleSheet("color: #4CAF50;")
        elif status == "failed":
            self.status_label.setText("❌")
            self.status_label.setStyleSheet("color: #F44336;")
        
        self.status_text.setText(message)


class nAUDITMainWindow(QMainWindow):
    """Главное окно приложения nAUDIT v2.1"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("nAUDIT v2.1 - Профессиональный анализ кода")
        self.setGeometry(100, 100, 1400, 900)
        self.setWindowIcon(self._create_icon())

        # Инициализация менеджера аудита
        self.audit_manager = AuditManager()
        self.audit_worker = None
        self.worker_thread = None
        self.last_result = None

        # Флаги
        self.is_auditing = False

        # Создание интерфейса
        self._setup_ui()
        self.setStyleSheet(MAIN_STYLESHEET)

    def _create_icon(self):
        """Создание иконки приложения"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(COLORS['primary']))
        return QIcon(pixmap)

    def _setup_ui(self):
        """Создание пользовательского интерфейса"""
        # Главный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Главная раскладка
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Заголовок
        header_layout = QHBoxLayout()
        title_label = QLabel("nAUDIT v2.1")
        title_font = QFont()
        title_font.setPointSize(26)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {COLORS['primary']};")

        subtitle_label = QLabel("Профессиональный инструмент анализа и аудита Python проектов")
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle_label.setStyleSheet(f"color: {COLORS['text_light']};")
        subtitle_label.setFont(subtitle_font)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Вертикальный разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {COLORS['border']};")
        main_layout.addWidget(separator)

        # Создание вкладок
        tabs = QTabWidget()
        tabs.setStyleSheet(f"QTabWidget::pane {{ border: 1px solid {COLORS['border']}; }}")
        main_layout.addWidget(tabs)

        # Вкладка 1: Аудит
        audit_tab = self._create_audit_tab()
        tabs.addTab(audit_tab, "🔍 Аудит")

        # Вкладка 2: Результаты
        self.results_tab = self._create_results_tab()
        tabs.addTab(self.results_tab, "📊 Результаты")

        # Вкладка 3: История
        history_tab = self._create_history_tab()
        tabs.addTab(history_tab, "📜 История")

        # Вкладка 4: Справка
        help_tab = self._create_help_tab()
        tabs.addTab(help_tab, "❓ Справка")

    def _create_audit_tab(self) -> QWidget:
        """Создание вкладки аудита с красивым UI"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(15)

        # Группа: Выбор проекта
        project_group = QGroupBox("📁 Выбор проекта для анализа")
        project_layout = QVBoxLayout()

        path_layout = QHBoxLayout()
        path_label = QLabel("Путь к проекту:")
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Выберите папку с проектом...")
        browse_button = QPushButton("🔍 Обзор")
        browse_button.setMaximumWidth(120)
        browse_button.clicked.connect(self._on_browse_clicked)

        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_button)
        project_layout.addLayout(path_layout)

        # Информация о проекте
        info_layout = QHBoxLayout()
        self.files_label = QLabel("Файлов: 0")
        self.size_label = QLabel("Размер: 0 MB")
        info_layout.addWidget(self.files_label)
        info_layout.addWidget(self.size_label)
        info_layout.addStretch()
        project_layout.addLayout(info_layout)

        project_group.setLayout(project_layout)
        layout.addWidget(project_group)

        # Группа: Параметры аудита
        settings_group = QGroupBox("⚙️ Параметры аудита")
        settings_layout = QGridLayout()

        # Уровень отчёта
        level_label = QLabel("Уровень отчёта:")
        self.level_combo = QComboBox()
        self.level_combo.addItems(["Краткий (quick)", "Полный (full)", "Детальный (detailed)"])
        self.level_combo.setCurrentIndex(1)
        settings_layout.addWidget(level_label, 0, 0)
        settings_layout.addWidget(self.level_combo, 0, 1)

        # Формат экспорта
        format_label = QLabel("Формат отчёта:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["HTML", "JSON", "Both"])
        self.format_combo.setCurrentIndex(0)
        settings_layout.addWidget(format_label, 0, 2)
        settings_layout.addWidget(self.format_combo, 0, 3)

        # Опции
        self.auto_export_check = QCheckBox("Автоматически экспортировать отчёт")
        self.auto_export_check.setChecked(True)
        settings_layout.addWidget(self.auto_export_check, 1, 0, 1, 2)

        self.open_report_check = QCheckBox("Открыть отчёт после завершения")
        self.open_report_check.setChecked(False)
        settings_layout.addWidget(self.open_report_check, 1, 2, 1, 2)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Группа: Ход аудита - фазы
        progress_group = QGroupBox("📈 Прогресс аудита")
        progress_layout = QVBoxLayout()

        # Фазы прогресса
        self.phase_indicators = []
        phases = [
            "Статический анализ кода",
            "Проверка безопасности",
            "Анализ тестового покрытия",
            "Анализ инфраструктуры",
            "Генерация рекомендаций",
            "Формирование отчёта"
        ]
        
        for phase_name in phases:
            indicator = ProgressIndicator(phase_name)
            self.phase_indicators.append(indicator)
            progress_layout.addWidget(indicator)

        # Общий прогресс
        self.overall_progress_bar = QProgressBar()
        self.overall_progress_bar.setValue(0)
        self.overall_progress_bar.setMinimum(0)
        self.overall_progress_bar.setMaximum(100)
        self.overall_progress_bar.setTextVisible(True)
        self.overall_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ccc;
                border-radius: 5px;
                text-align: center;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 3px;
            }
        """)

        progress_layout.addWidget(QLabel("Общий прогресс:"))
        progress_layout.addWidget(self.overall_progress_bar)

        # Статус сообщение
        self.status_label = QLabel("✓ Готово к запуску")
        self.status_label.setStyleSheet(f"color: {COLORS['text_light']};")
        self.status_label.setFont(QFont("Arial", 11))
        progress_layout.addWidget(self.status_label)

        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        # Логи аудита
        log_group = QGroupBox("📋 Логи выполнения")
        log_layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet(f"background-color: {COLORS['white']}; font-family: 'Courier New'; font-size: 9pt;")

        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.start_button = QPushButton("▶ Начать аудит")
        self.start_button.setMinimumWidth(150)
        self.start_button.setMinimumHeight(45)
        self.start_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
            QPushButton:pressed {{
                background-color: #3d8b40;
            }}
        """)
        self.start_button.clicked.connect(self._on_start_audit)

        self.cancel_button = QPushButton("⊗ Отмена")
        self.cancel_button.setMinimumWidth(150)
        self.cancel_button.setMinimumHeight(45)
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: #da190b;
            }}
        """)
        self.cancel_button.clicked.connect(self._on_cancel_audit)
        self.cancel_button.setEnabled(False)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        layout.addStretch()

        return tab_widget

    def _create_results_tab(self) -> QWidget:
        """Создание вкладки результатов с графиками и анализом"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(15)

        # Верхняя строка - оценка и статистика
        top_layout = QHBoxLayout()

        # Группа: Оценка качества
        rating_group = QGroupBox("⭐ Оценка качества кода")
        rating_layout = QVBoxLayout()

        self.rating_label = QLabel("—")
        self.rating_label.setObjectName("ratingLabel")
        rating_font = QFont()
        rating_font.setPointSize(48)
        rating_font.setBold(True)
        self.rating_label.setFont(rating_font)
        self.rating_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rating_label.setStyleSheet("color: #FFA500;")

        rating_desc_layout = QVBoxLayout()
        self.rating_desc_label = QLabel("Аудит не выполнен")
        self.rating_desc_label.setObjectName("ratingDescLabel")
        self.rating_desc_label.setStyleSheet(f"color: {COLORS['text_light']};")
        self.rating_desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        rating_desc_layout.addWidget(self.rating_label)
        rating_desc_layout.addWidget(self.rating_desc_label)
        
        rating_group.setLayout(rating_desc_layout)
        top_layout.addWidget(rating_group, 1)

        # Группа: Статистика проблем (текстовое представление)
        chart_group = QGroupBox("🎯 Распределение проблем")
        chart_layout = QVBoxLayout()
        
        self.chart_text = QTextEdit()
        self.chart_text.setReadOnly(True)
        self.chart_text.setMinimumHeight(250)
        self.chart_text.setStyleSheet("font-family: 'Courier New'; font-size: 10pt;")
        chart_layout.addWidget(self.chart_text)
        
        chart_group.setLayout(chart_layout)
        top_layout.addWidget(chart_group, 2)

        layout.addLayout(top_layout)

        # Статистика
        stats_group = QGroupBox("📊 Детальная статистика")
        stats_layout = QVBoxLayout()

        # Таблица статистики
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["Метрика", "Значение"])
        self.stats_table.setMaximumHeight(200)
        self.stats_table.horizontalHeader().setStretchLastSection(True)

        stats_layout.addWidget(self.stats_table)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Рекомендации
        rec_group = QGroupBox("💡 Рекомендации по улучшению")
        rec_layout = QVBoxLayout()

        self.recommendations_text = QTextEdit()
        self.recommendations_text.setReadOnly(True)

        rec_layout.addWidget(self.recommendations_text)
        rec_group.setLayout(rec_layout)
        layout.addWidget(rec_group)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        export_button = QPushButton("💾 Экспортировать отчёт")
        export_button.setMinimumWidth(180)
        export_button.setMinimumHeight(40)
        export_button.clicked.connect(self._on_export_report)
        export_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #0b7dda;
            }}
        """)

        open_folder_button = QPushButton("📂 Открыть папку отчётов")
        open_folder_button.setMinimumWidth(180)
        open_folder_button.setMinimumHeight(40)
        open_folder_button.clicked.connect(self._on_open_reports_folder)
        open_folder_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #9C27B0;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #7b1fa2;
            }}
        """)

        button_layout.addWidget(export_button)
        button_layout.addWidget(open_folder_button)
        layout.addLayout(button_layout)

        return tab_widget

    def _create_history_tab(self) -> QWidget:
        """Создание вкладки истории анализов"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Дата", "Проект", "Оценка", "Статус"])
        self.history_table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(QLabel("История последних анализов"))
        layout.addWidget(self.history_table)

        return tab_widget

    def _create_help_tab(self) -> QWidget:
        """Создание вкладки справки"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)

        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setMarkdown("""
# nAUDIT v2.1 - Справка

## Что такое nAUDIT?

nAUDIT — это **профессиональный инструмент** для глубокого анализа Python проектов. 
Он проверяет качество кода, безопасность, тестовое покрытие, инфраструктуру и выдаёт 
подробные рекомендации по улучшению.

## Что проверяет nAUDIT?

- **Статический анализ кода**: стиль, сложность, ошибки
- **Безопасность**: потенциальные уязвимости (Bandit)
- **Тестовое покрытие**: оценка качества и покрытия тестами
- **Инфраструктура**: зависимости, конфигурация, requirements
- **Рекомендации**: AI-powered предложения по улучшению

## Как использовать?

1. **Выберите проект**: нажмите "Обзор" и выберите папку
2. **Настройте параметры**: уровень отчёта и формат
3. **Запустите аудит**: нажмите "Начать аудит" 
4. **Просмотрите результаты**: перейдите на вкладку "Результаты"
5. **Экспортируйте отчёт**: сохраните результаты в HTML/JSON

## Интерпретация оценки

- **9-10** ✅ Отличное качество - поддерживайте уровень
- **7-8** ✔️ Хорошее качество - есть области для улучшения
- **5-6** ⚠️ Среднее качество - требуется работа
- **3-4** ❌ Низкое качество - срочно исправляйте
- **1-2** 🔴 Критично - переделывайте проект

## Параметры анализа

- **Краткий**: быстрый скан без подробностей
- **Полный**: стандартный полный анализ (рекомендуется)
- **Детальный**: максимально подробный анализ (медленнее)

## Часто задаваемые вопросы

**Q: Как долго выполняется аудит?**
A: От 30 секунд до нескольких минут в зависимости от размера проекта.

**Q: Где сохраняются отчёты?**
A: В папке `.audit_results` вашего проекта.

**Q: Можно ли отменить аудит?**
A: Да, нажмите кнопку "Отмена".

---

**Версия**: 2.1 (Enhanced) | **Лицензия**: MIT | **Автор**: nAUDIT Team
""")

        layout.addWidget(help_text)
        return tab_widget

    def _on_browse_clicked(self):
        """Обработка нажатия кнопки обзора"""
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку с проектом")
        if folder:
            self.path_input.setText(folder)
            self._update_project_info(folder)

    def _update_project_info(self, path: str):
        """Обновление информации о проекте"""
        try:
            py_files = 0
            total_size = 0
            for root, dirs, files in os.walk(path):
                # Пропускаем скрытые папки и .venv, venv и т.д.
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', 'env', '__pycache__']]
                for file in files:
                    if file.endswith('.py'):
                        py_files += 1
                        total_size += os.path.getsize(os.path.join(root, file))
            
            size_mb = total_size / (1024 * 1024)
            self.files_label.setText(f"Python файлов: {py_files}")
            self.size_label.setText(f"Размер кода: {size_mb:.2f} MB")
        except Exception as e:
            pass

    def _on_start_audit(self):
        """Запуск аудита"""
        path = self.path_input.text().strip()
        if not path:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите папку с проектом")
            return

        if not os.path.isdir(path):
            QMessageBox.warning(self, "Ошибка", f"Папка не существует: {path}")
            return

        # Найти хотя бы один Python файл
        py_files = [f for f in os.listdir(path) if f.endswith('.py')]
        if not any(os.walk(path)):
            QMessageBox.warning(self, "Ошибка", "Папка не содержит Python файлы")
            return

        # Сброс UI
        self._reset_results_ui()
        self._reset_phase_indicators()

        # Конфигурация аудита
        self.audit_manager.configure(
            target_path=path,
            report_level=self.level_combo.currentText().split()[0].lower(),
            export_format=self.format_combo.currentText().lower(),
            verbose=True
        )

        # Запуск аудита в отдельном потоке
        self.is_auditing = True
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.path_input.setEnabled(False)
        self.level_combo.setEnabled(False)
        self.format_combo.setEnabled(False)

        self.worker_thread = QThread()
        self.audit_worker = AuditWorker(self.audit_manager)
        self.audit_worker.moveToThread(self.worker_thread)

        # Подключение сигналов
        self.worker_thread.started.connect(self.audit_worker.run_audit)
        self.audit_worker.finished.connect(self.worker_thread.quit)
        self.audit_worker.progress_updated.connect(self._on_progress_updated)
        self.audit_worker.phase_updated.connect(self._on_phase_updated)
        self.audit_worker.audit_completed.connect(self._on_audit_completed)
        self.audit_worker.audit_error.connect(self._on_audit_error)

        self.worker_thread.start()

    def _reset_phase_indicators(self):
        """Сброс индикаторов фаз"""
        for indicator in self.phase_indicators:
            indicator.set_status("waiting")
            indicator.set_progress(0)

    def _reset_results_ui(self):
        """Сброс UI результатов"""
        self.rating_label.setText("—")
        self.rating_desc_label.setText("Аудит выполняется...")
        self.stats_table.setRowCount(0)
        self.recommendations_text.clear()
        self.log_text.clear()
        self.overall_progress_bar.setValue(0)

    def _on_progress_updated(self, progress: int, message: str):
        """Обновление общего прогресса"""
        self.overall_progress_bar.setValue(progress)
        self.status_label.setText(f"⏳ {message}")
        self._add_log_message(message)

    def _on_phase_updated(self, phase_name: str, phase_progress: int, message: str):
        """Обновление текущей фазы"""
        # Найти индикатор для этой фазы
        for idx, indicator in enumerate(self.phase_indicators):
            if indicator.phase_name == phase_name:
                indicator.set_status("running", message)
                indicator.set_progress(phase_progress)
                break

    def _on_audit_completed(self, result: AuditResult):
        """Обработка завершения аудита"""
        self.last_result = result
        self.is_auditing = False
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.path_input.setEnabled(True)
        self.level_combo.setEnabled(True)
        self.format_combo.setEnabled(True)

        # Обновление результатов
        self._display_results(result)
        
        # Отметить все фазы как завершённые
        for indicator in self.phase_indicators:
            if indicator.status != "failed":
                indicator.set_status("completed")
                indicator.set_progress(100)

        self.status_label.setText("✅ Аудит завершён успешно!")
        self._add_log_message("✅ Аудит завершён успешно!")

        # Экспорт если нужно
        if self.auto_export_check.isChecked():
            self._on_export_report()

    def _on_audit_error(self, error_msg: str):
        """Обработка ошибки аудита"""
        self.is_auditing = False
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.path_input.setEnabled(True)
        self.status_label.setText(f"❌ Ошибка: {error_msg}")
        self._add_log_message(f"❌ Ошибка: {error_msg}")
        QMessageBox.critical(self, "Ошибка при аудите", error_msg)

    def _on_cancel_audit(self):
        """Отмена аудита"""
        self.audit_manager.cancel_audit()
        self.is_auditing = False
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.status_label.setText("⊗ Аудит отменён пользователем")
        self._add_log_message("⊗ Аудит отменён")

    def _display_results(self, result: AuditResult):
        """Отображение результатов аудита"""
        # Оценка
        rating_color = self._get_rating_color(result.rating)
        self.rating_label.setText(f"{result.rating}")
        self.rating_label.setStyleSheet(f"color: {rating_color};")
        
        rating_desc = self._get_rating_description(result.rating)
        self.rating_desc_label.setText(rating_desc)

        # Круговая диаграмма
        self._create_pie_chart(result.code_issues, result.security_issues)

        # Таблица статистики
        self._populate_stats_table(result)

        # Рекомендации
        if result.recommendations:
            recommendations_text = "\n\n".join(
                [f"• {rec}" for rec in result.recommendations[:10]]
            )
            self.recommendations_text.setText(recommendations_text)
        else:
            self.recommendations_text.setText("Рекомендаций нет - код в отличном состоянии!")

    def _populate_stats_table(self, result: AuditResult):
        """Заполнение таблицы статистики"""
        self.stats_table.setRowCount(0)
        
        stats = [
            ("Общее количество проблем", str(result.total_issues)),
            ("Проблемы в коде", str(result.code_issues)),
            ("Проблемы безопасности", str(result.security_issues)),
            ("Тестовое покрытие", f"{result.test_coverage:.1f}%"),
            ("Оценка качества", f"{result.rating}/10"),
            ("Дата анализа", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ]
        
        for idx, (metric, value) in enumerate(stats):
            self.stats_table.insertRow(idx)
            self.stats_table.setItem(idx, 0, QTableWidgetItem(metric))
            value_item = QTableWidgetItem(value)
            value_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.stats_table.setItem(idx, 1, value_item)

    def _create_pie_chart(self, code_issues: int, security_issues: int):
        """Создание текстового представления распределения проблем"""
        chart_text = "═══════════════════════════════\n"
        chart_text += "  РАСПРЕДЕЛЕНИЕ ПРОБЛЕМ\n"
        chart_text += "═══════════════════════════════\n\n"
        
        total = code_issues + security_issues
        
        if total == 0:
            chart_text += "✅ Проблем не найдено!\n"
            chart_text += "Код находится в отличном состоянии.\n"
        else:
            chart_text += f"Проблемы кода:        {code_issues}\n"
            chart_text += f"{'█' * int(code_issues / max(total, 1) * 20)}\n\n"
            
            chart_text += f"Проблемы безопасности: {security_issues}\n"
            chart_text += f"{'█' * int(security_issues / max(total, 1) * 20)}\n\n"
            
            chart_text += f"────────────────────────────\n"
            chart_text += f"Всего проблем: {total}\n"
        
        self.chart_text.setText(chart_text)

    def _get_rating_color(self, rating: float) -> str:
        """Получение цвета для оценки"""
        if rating >= 8:
            return "#4CAF50"  # Зелёный
        elif rating >= 6:
            return "#FFC107"  # Жёлтый
        elif rating >= 4:
            return "#FF9800"  # Оранжевый
        else:
            return "#F44336"  # Красный

    def _get_rating_description(self, rating: float) -> str:
        """Получение описания оценки"""
        if rating >= 8:
            return "✅ Отличное качество"
        elif rating >= 6:
            return "✔️ Хорошее качество"
        elif rating >= 4:
            return "⚠️ Среднее качество"
        elif rating >= 2:
            return "❌ Низкое качество"
        else:
            return "🔴 Критичное качество"

    def _add_log_message(self, message: str):
        """Добавление сообщения в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        # Прокрутка вниз
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def _on_export_report(self):
        """Экспорт отчёта"""
        if not self.last_result:
            QMessageBox.warning(self, "Ошибка", "Сначала проведите аудит")
            return

        path = self.path_input.text().strip()
        if not path:
            return

        results_dir = os.path.join(path, ".audit_results")
        reports_dir = os.path.join(results_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)

        try:
            # Создание отчёта
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # JSON экспорт
            if self.format_combo.currentText() in ["JSON", "Both"]:
                json_file = os.path.join(reports_dir, f"audit_report_{timestamp}.json")
                report_data = {
                    "timestamp": datetime.now().isoformat(),
                    "rating": self.last_result.rating,
                    "total_issues": self.last_result.total_issues,
                    "code_issues": self.last_result.code_issues,
                    "security_issues": self.last_result.security_issues,
                    "test_coverage": self.last_result.test_coverage,
                    "recommendations": self.last_result.recommendations,
                    "phases": self.last_result.phases
                }
                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(report_data, f, indent=2, ensure_ascii=False)
                self._add_log_message(f"✅ JSON отчёт сохранён: {json_file}")

            # HTML экспорт
            if self.format_combo.currentText() in ["HTML", "Both"]:
                html_file = os.path.join(reports_dir, f"audit_report_{timestamp}.html")
                html_content = self._generate_html_report(self.last_result)
                with open(html_file, "w", encoding="utf-8") as f:
                    f.write(html_content)
                self._add_log_message(f"✅ HTML отчёт сохранён: {html_file}")

            QMessageBox.information(self, "Успех", f"Отчёт сохранён в:\n{reports_dir}")

        except Exception as e:
            self._add_log_message(f"❌ Ошибка при экспорте: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при экспорте: {e}")

    def _generate_html_report(self, result: AuditResult) -> str:
        """Генерация HTML отчёта"""
        rating_color = self._get_rating_color(result.rating)
        rating_desc = self._get_rating_description(result.rating)
        
        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Отчёт nAUDIT</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #2196F3; padding-bottom: 10px; }}
        h2 {{ color: #2196F3; margin-top: 30px; }}
        .rating {{ font-size: 48px; font-weight: bold; color: {rating_color}; text-align: center; margin: 20px 0; }}
        .description {{ text-align: center; font-size: 18px; color: #666; margin: 10px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f9f9f9; font-weight: bold; }}
        tr:hover {{ background-color: #f5f5f5; }}
        .positive {{ color: #4CAF50; font-weight: bold; }}
        .negative {{ color: #F44336; font-weight: bold; }}
        .recommendations {{ background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Отчёт анализа nAUDIT v2.1</h1>
        
        <div class="rating">{result.rating}/10</div>
        <div class="description">{rating_desc}</div>
        
        <h2>Статистика</h2>
        <table>
            <tr>
                <th>Метрика</th>
                <th>Значение</th>
            </tr>
            <tr>
                <td>Общее количество проблем</td>
                <td class="{'positive' if result.total_issues == 0 else 'negative'}">{result.total_issues}</td>
            </tr>
            <tr>
                <td>Проблемы в коде</td>
                <td class="{'positive' if result.code_issues == 0 else 'negative'}">{result.code_issues}</td>
            </tr>
            <tr>
                <td>Проблемы безопасности</td>
                <td class="{'positive' if result.security_issues == 0 else 'negative'}">{result.security_issues}</td>
            </tr>
            <tr>
                <td>Тестовое покрытие</td>
                <td>{result.test_coverage:.1f}%</td>
            </tr>
            <tr>
                <td>Дата анализа</td>
                <td>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</td>
            </tr>
        </table>
        
        <h2>Рекомендации</h2>
        <div class="recommendations">
            {''.join([f'<p>✓ {rec}</p>' for rec in result.recommendations[:15]])}
        </div>
        
        <div class="footer">
            <p>Создано: nAUDIT v2.1 | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </div>
</body>
</html>"""
        return html

    def _on_open_reports_folder(self):
        """Открытие папки с отчётами"""
        path = self.path_input.text().strip()
        if not path:
            QMessageBox.warning(self, "Ошибка", "Выберите папку проекта")
            return

        reports_dir = os.path.join(path, ".audit_results", "reports")
        if os.path.exists(reports_dir):
            os.startfile(reports_dir)
        else:
            QMessageBox.warning(self, "Ошибка", "Папка отчётов не найдена")
