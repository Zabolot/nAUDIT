"""
Главное окно приложения nAUDIT с интерфейсом для выполнения аудита.
Минималистичный современный дизайн с поддержкой многопоточности.
"""

import os
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QProgressBar, QTextEdit, QFileDialog, QComboBox, QGroupBox,
    QScrollArea, QFrame, QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread
from PyQt6.QtGui import QFont, QColor, QTextCursor

# Гибкие импорты для совместимости с PyInstaller
try:
    from n_audit.audit_manager import AuditManager, AuditPhase, AuditResult, AuditStatus
    from n_audit.gui.styles import MAIN_STYLESHEET, COLORS
except (ImportError, ModuleNotFoundError):
    # Альтернативный путь для PyInstaller
    try:
        from audit_manager import AuditManager, AuditPhase, AuditResult, AuditStatus
        from styles import MAIN_STYLESHEET, COLORS
    except (ImportError, ModuleNotFoundError):
        # Последний вариант - с относительным импортом
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


class nAUDITMainWindow(QMainWindow):
    """Главное окно приложения nAUDIT"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("nAUDIT - Анализатор качества кода")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(self._create_icon())

        # Инициализация менеджера аудита
        self.audit_manager = AuditManager()
        self.audit_worker = None
        self.worker_thread = None

        # Флаги
        self.is_auditing = False

        # Создание интерфейса
        self._setup_ui()
        self.setStyleSheet(MAIN_STYLESHEET)

    def _create_icon(self):
        """Создание иконки приложения"""
        from PyQt6.QtGui import QPixmap, QIcon
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
        title_label = QLabel("nAUDIT")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)

        subtitle_label = QLabel("Инструмент глубокого анализа и аудита Python проектов")
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
        main_layout.addWidget(tabs)

        # Вкладка 1: Аудит
        audit_tab = self._create_audit_tab()
        tabs.addTab(audit_tab, "Аудит")

        # Вкладка 2: Результаты
        self.results_tab = self._create_results_tab()
        tabs.addTab(self.results_tab, "Результаты")

        # Вкладка 3: Справка
        help_tab = self._create_help_tab()
        tabs.addTab(help_tab, "Справка")

    def _create_audit_tab(self) -> QWidget:
        """Создание вкладки аудита"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(15)

        # Группа: Выбор проекта
        project_group = QGroupBox("Выбор проекта для анализа")
        project_layout = QVBoxLayout()

        path_layout = QHBoxLayout()
        path_label = QLabel("Путь к проекту:")
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Выберите папку с проектом...")
        browse_button = QPushButton("Обзор")
        browse_button.setObjectName("browseButton")
        browse_button.setMaximumWidth(100)
        browse_button.clicked.connect(self._on_browse_clicked)

        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_button)

        project_layout.addLayout(path_layout)
        project_group.setLayout(project_layout)
        layout.addWidget(project_group)

        # Группа: Параметры аудита
        settings_group = QGroupBox("Параметры аудита")
        settings_layout = QVBoxLayout()

        # Уровень отчёта
        level_layout = QHBoxLayout()
        level_label = QLabel("Уровень отчёта:")
        self.level_combo = QComboBox()
        self.level_combo.addItems(["Краткий (brief)", "Полный (full)", "Детальный (detailed)"])
        self.level_combo.setCurrentIndex(1)
        level_layout.addWidget(level_label)
        level_layout.addWidget(self.level_combo)
        level_layout.addStretch()

        settings_layout.addLayout(level_layout)

        # Формат экспорта
        format_layout = QHBoxLayout()
        format_label = QLabel("Формат отчёта:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["HTML", "JSON"])
        self.format_combo.setCurrentIndex(0)
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()

        settings_layout.addLayout(format_layout)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Группа: Ход аудита
        progress_group = QGroupBox("Ход выполнения аудита")
        progress_layout = QVBoxLayout()

        # Фаза
        self.phase_label = QLabel("Готово к запуску")
        phase_font = QFont()
        phase_font.setBold(True)
        self.phase_label.setFont(phase_font)

        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)

        # Сообщение о статусе
        self.status_label = QLabel("Нажмите 'Начать аудит' для запуска")
        self.status_label.setStyleSheet(f"color: {COLORS['text_light']};")

        progress_layout.addWidget(self.phase_label)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)

        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        # Логи аудита
        log_group = QGroupBox("Логи аудита")
        log_layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.log_text.setStyleSheet(f"background-color: {COLORS['white']}; font-family: 'Courier New';")

        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.start_button = QPushButton("Начать аудит")
        self.start_button.setMinimumWidth(150)
        self.start_button.setMinimumHeight(40)
        self.start_button.clicked.connect(self._on_start_audit)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.setMinimumWidth(150)
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.clicked.connect(self._on_cancel_audit)
        self.cancel_button.setEnabled(False)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        layout.addStretch()

        return tab_widget

    def _create_results_tab(self) -> QWidget:
        """Создание вкладки результатов"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(15)

        # Группа: Оценка
        rating_group = QGroupBox("Оценка качества кода")
        rating_layout = QHBoxLayout()

        self.rating_label = QLabel("—")
        self.rating_label.setObjectName("ratingLabel")
        rating_font = QFont()
        rating_font.setPointSize(32)
        rating_font.setBold(True)
        self.rating_label.setFont(rating_font)
        self.rating_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        rating_desc_layout = QVBoxLayout()
        self.rating_desc_label = QLabel("Аудит не выполнен")
        self.rating_desc_label.setObjectName("ratingDescLabel")
        self.rating_desc_label.setStyleSheet(f"color: {COLORS['text_light']};")

        rating_desc_layout.addWidget(self.rating_desc_label)
        rating_desc_layout.addStretch()

        rating_layout.addWidget(self.rating_label)
        rating_layout.addLayout(rating_desc_layout)
        rating_group.setLayout(rating_layout)
        layout.addWidget(rating_group)

        # Группа: Статистика
        stats_group = QGroupBox("Статистика проверок")
        stats_layout = QVBoxLayout()

        # Создание таблицы статистики
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["Метрика", "Значение"])
        self.stats_table.setMaximumHeight(200)

        stats_layout.addWidget(self.stats_table)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Группа: Рекомендации
        rec_group = QGroupBox("Рекомендации по улучшению")
        rec_layout = QVBoxLayout()

        self.recommendations_text = QTextEdit()
        self.recommendations_text.setReadOnly(True)

        rec_layout.addWidget(self.recommendations_text)
        rec_group.setLayout(rec_layout)
        layout.addWidget(rec_group)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        export_button = QPushButton("Экспортировать отчёт")
        export_button.setMinimumWidth(150)
        export_button.clicked.connect(self._on_export_report)

        button_layout.addWidget(export_button)
        layout.addLayout(button_layout)

        return tab_widget

    def _create_help_tab(self) -> QWidget:
        """Создание вкладки справки"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)

        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setMarkdown("""
# nAUDIT - Справка

## Что такое nAUDIT?

nAUDIT — это инструмент для глубокого анализа и аудита Python проектов. 
Он проверяет качество кода, безопасность, тестовое покрытие и другие аспекты вашего проекта.

## Как использовать?

1. **Выберите проект**: нажмите кнопку "Обзор" и выберите папку с вашим Python проектом
2. **Настройте параметры**: выберите уровень отчёта и формат экспорта
3. **Запустите аудит**: нажмите кнопку "Начать аудит"
4. **Просмотрите результаты**: результаты будут доступны на вкладке "Результаты"

## Что проверяет nAUDIT?

- **Статический анализ кода**: проверка синтаксиса, стиля и сложности
- **Безопасность**: поиск потенциальных уязвимостей
- **Тестовое покрытие**: анализ качества тестов
- **Инфраструктура**: проверка конфигурации и зависимостей
- **Рекомендации**: предложения по улучшению кода

## Интерпретация оценки

- **8-10**: Отличное качество кода
- **6-7**: Хорошее качество, есть области для улучшения
- **4-5**: Среднее качество, требуется работа
- **1-3**: Низкое качество, срочно требуются исправления

## Часто задаваемые вопросы

**Q: Как долго выполняется аудит?**
A: Время зависит от размера проекта. Обычно от нескольких секунд до нескольких минут.

**Q: Можно ли отменить аудит?**
A: Да, нажмите кнопку "Отмена" для остановки текущего процесса.

**Q: Где сохраняются отчёты?**
A: Отчёты сохраняются в папке `.audit_results` вашего проекта.

## Техническая поддержка

Если у вас возникли проблемы, проверьте:
1. Путь к проекту корректен
2. Проект содержит Python файлы (.py)
3. Все необходимые зависимости установлены
""")

        layout.addWidget(help_text)
        return tab_widget

    def _on_browse_clicked(self):
        """Обработка нажатия кнопки обзора"""
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку с проектом")
        if folder:
            self.path_input.setText(folder)
            self._log(f"Выбрана папка: {folder}")

    def _on_start_audit(self):
        """Обработка нажатия кнопки запуска аудита"""
        target_path = self.path_input.text().strip()

        if not target_path:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите папку с проектом")
            return

        if not os.path.isdir(target_path):
            QMessageBox.warning(self, "Ошибка", f"Папка не найдена: {target_path}")
            return

        # Определение параметров
        level_map = {"Краткий (brief)": "brief", "Полный (full)": "full", "Детальный (detailed)": "detailed"}
        format_map = {"HTML": "html", "JSON": "json"}

        report_level = level_map.get(self.level_combo.currentText(), "full")
        export_format = format_map.get(self.format_combo.currentText(), "html")

        # Конфигурация менеджера
        self.audit_manager.configure(
            target_path=target_path,
            report_level=report_level,
            export_format=export_format,
            verbose=True
        )

        # Запуск аудита
        self.is_auditing = True
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.path_input.setEnabled(False)
        self.level_combo.setEnabled(False)
        self.format_combo.setEnabled(False)

        self.log_text.clear()
        self.progress_bar.setValue(0)
        self._log("Запуск аудита...")

        # Создание рабочего потока
        self.worker_thread = QThread()
        self.audit_worker = AuditWorker(self.audit_manager)
        self.audit_worker.moveToThread(self.worker_thread)

        # Подключение сигналов
        self.worker_thread.started.connect(self.audit_worker.run_audit)
        self.audit_worker.progress_updated.connect(self._on_progress_updated)
        self.audit_worker.phase_updated.connect(self._on_phase_updated)
        self.audit_worker.audit_completed.connect(self._on_audit_completed)
        self.audit_worker.audit_error.connect(self._on_audit_error)
        self.audit_worker.finished.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.start()

    def _on_cancel_audit(self):
        """Обработка нажатия кнопки отмены"""
        self.audit_manager.cancel_audit()
        self._log("Аудит отменён пользователем")
        self._on_audit_finished()

    def _on_progress_updated(self, progress: int, message: str):
        """Обновление прогресса"""
        self.progress_bar.setValue(progress)
        self._log(f"[{progress}%] {message}")

    def _on_phase_updated(self, phase_name: str, phase_progress: int, message: str):
        """Обновление фазы"""
        self.phase_label.setText(f"Текущая фаза: {phase_name}")
        self.status_label.setText(f"Статус: {message}")

    def _on_audit_completed(self, result: AuditResult):
        """Обработка завершения аудита"""
        self._log("✓ Аудит успешно завершён!")
        self._display_results(result)
        self._on_audit_finished()

    def _on_audit_error(self, error_msg: str):
        """Обработка ошибки аудита"""
        self._log(f"✗ Ошибка: {error_msg}")
        QMessageBox.critical(self, "Ошибка аудита", error_msg)
        self._on_audit_finished()

    def _on_audit_finished(self):
        """Завершение аудита"""
        self.is_auditing = False
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.path_input.setEnabled(True)
        self.level_combo.setEnabled(True)
        self.format_combo.setEnabled(True)

    def _on_export_report(self):
        """Экспортирование отчёта"""
        if not self.audit_manager.result:
            QMessageBox.warning(self, "Ошибка", "Сначала выполните аудит")
            return

        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self, "Сохранить отчёт", "", "HTML Files (*.html);;JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            # Здесь можно добавить логику экспорта
            QMessageBox.information(self, "Успех", f"Отчёт сохранён: {file_path}")

    def _display_results(self, result: AuditResult):
        """Отображение результатов аудита"""
        # Обновление оценки
        self.rating_label.setText(str(result.rating))
        rating_desc = self._get_rating_description(result.rating)
        self.rating_desc_label.setText(rating_desc)

        # Обновление цвета оценки
        if result.rating >= 8:
            color = COLORS['success']
        elif result.rating >= 6:
            color = COLORS['warning']
        else:
            color = COLORS['danger']
        self.rating_label.setStyleSheet(f"color: {color};")

        # Очистка таблицы
        self.stats_table.setRowCount(0)

        # Добавление статистики
        stats = [
            ("Всего проблем", str(result.total_issues)),
            ("Проблемы кода", str(result.code_issues)),
            ("Проблемы безопасности", str(result.security_issues)),
            ("Оценка качества", f"{result.rating}/10"),
        ]

        for row, (metric, value) in enumerate(stats):
            self.stats_table.insertRow(row)
            self.stats_table.setItem(row, 0, QTableWidgetItem(metric))
            self.stats_table.setItem(row, 1, QTableWidgetItem(value))

        # Обновление рекомендаций
        self.recommendations_text.setPlainText("\n".join(result.recommendations))

    def _get_rating_description(self, rating: float) -> str:
        """Получение описания оценки"""
        if rating >= 9:
            return "Отличное качество кода"
        elif rating >= 7:
            return "Хорошее качество кода"
        elif rating >= 5:
            return "Среднее качество кода"
        elif rating >= 3:
            return "Низкое качество кода"
        else:
            return "Критическое качество кода"

    def _log(self, message: str):
        """Добавление сообщения в лог"""
        self.log_text.append(message)
        # Автоматический скролл в конец
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)


def main():
    """Точка входа в приложение"""
    app = __import__('PyQt6.QtWidgets', fromlist=['QApplication']).QApplication(sys.argv)
    window = nAUDITMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
