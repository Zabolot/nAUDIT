"""
Стили и темы для GUI приложения nAUDIT.
Современный минималистичный дизайн.
"""

# Цветовая схема
COLORS = {
    "primary": "#2563EB",      # Синий
    "primary_dark": "#1E40AF", # Тёмный синий
    "success": "#10B981",      # Зелёный
    "warning": "#F59E0B",      # Оранжевый
    "danger": "#EF4444",       # Красный
    "neutral": "#6B7280",      # Серый
    "bg": "#F9FAFB",           # Светлый фон
    "bg_alt": "#F3F4F6",       # Альтернативный фон
    "text": "#111827",         # Тёмный текст
    "text_light": "#6B7280",   # Светлый текст
    "border": "#E5E7EB",       # Граница
    "white": "#FFFFFF",        # Белый
}

# Основной стиль приложения
MAIN_STYLESHEET = f"""
QMainWindow {{
    background-color: {COLORS['bg']};
}}

QWidget {{
    background-color: {COLORS['bg']};
    color: {COLORS['text']};
    font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
    font-size: 10pt;
}}

/* Кнопки */
QPushButton {{
    background-color: {COLORS['primary']};
    color: {COLORS['white']};
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    font-size: 10pt;
}}

QPushButton:hover {{
    background-color: {COLORS['primary_dark']};
}}

QPushButton:pressed {{
    background-color: {COLORS['primary_dark']};
    padding: 9px 15px 7px 17px;
}}

QPushButton:disabled {{
    background-color: {COLORS['neutral']};
    color: {COLORS['text_light']};
}}

/* Кнопка отмены */
QPushButton#cancelButton {{
    background-color: {COLORS['danger']};
}}

QPushButton#cancelButton:hover {{
    background-color: #DC2626;
}}

/* Кнопка обзора */
QPushButton#browseButton {{
    background-color: {COLORS['neutral']};
    color: {COLORS['white']};
}}

QPushButton#browseButton:hover {{
    background-color: #4B5563;
}}

/* Поле ввода */
QLineEdit {{
    background-color: {COLORS['white']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 8px;
    font-size: 10pt;
}}

QLineEdit:focus {{
    border: 2px solid {COLORS['primary']};
}}

/* Комбо-бокс */
QComboBox {{
    background-color: {COLORS['white']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 6px;
    font-size: 10pt;
}}

QComboBox::drop-down {{
    border: none;
    background-color: {COLORS['white']};
}}

QComboBox::down-arrow {{
    image: url(noimg);
}}

/* Чекбокс */
QCheckBox {{
    color: {COLORS['text']};
    spacing: 6px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {COLORS['border']};
    border-radius: 3px;
    background-color: {COLORS['white']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['primary']};
    border: 1px solid {COLORS['primary']};
}}

/* Прогресс-бар */
QProgressBar {{
    background-color: {COLORS['bg_alt']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    text-align: center;
    color: {COLORS['text']};
    height: 24px;
}}

QProgressBar::chunk {{
    background-color: {COLORS['primary']};
    border-radius: 3px;
}}

/* Таблица */
QTableWidget {{
    background-color: {COLORS['white']};
    alternate-background-color: {COLORS['bg_alt']};
    gridline-color: {COLORS['border']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
}}

QTableWidget::item:selected {{
    background-color: {COLORS['primary']};
    color: {COLORS['white']};
}}

QHeaderView::section {{
    background-color: {COLORS['bg_alt']};
    color: {COLORS['text']};
    padding: 6px;
    border: none;
    border-right: 1px solid {COLORS['border']};
    border-bottom: 1px solid {COLORS['border']};
}}

/* Текстовое поле */
QTextEdit, QPlainTextEdit {{
    background-color: {COLORS['white']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 8px;
    font-family: 'Courier New', monospace;
    font-size: 9pt;
}}

QTextEdit:focus, QPlainTextEdit:focus {{
    border: 2px solid {COLORS['primary']};
}}

/* Метки */
QLabel {{
    color: {COLORS['text']};
}}

QLabel#titleLabel {{
    font-size: 18pt;
    font-weight: bold;
    color: {COLORS['text']};
}}

QLabel#subtitleLabel {{
    font-size: 12pt;
    color: {COLORS['text_light']};
}}

QLabel#statusLabel {{
    font-weight: 500;
    padding: 4px 8px;
    border-radius: 3px;
}}

QLabel#statusLabel-success {{
    background-color: {COLORS['success']};
    color: {COLORS['white']};
}}

QLabel#statusLabel-warning {{
    background-color: {COLORS['warning']};
    color: {COLORS['white']};
}}

QLabel#statusLabel-error {{
    background-color: {COLORS['danger']};
    color: {COLORS['white']};
}}

/* Группа */
QGroupBox {{
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: 500;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px 0 3px;
}}

/* Вкладки */
QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
}}

QTabBar::tab {{
    background-color: {COLORS['bg_alt']};
    color: {COLORS['text']};
    padding: 8px 20px;
    margin-right: 2px;
    border: none;
}}

QTabBar::tab:selected {{
    background-color: {COLORS['white']};
    border-bottom: 2px solid {COLORS['primary']};
}}

/* Полоса прокрутки */
QScrollBar:vertical {{
    background-color: {COLORS['bg_alt']};
    width: 12px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['border']};
    border-radius: 6px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['neutral']};
}}

QScrollBar:horizontal {{
    background-color: {COLORS['bg_alt']};
    height: 12px;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS['border']};
    border-radius: 6px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {COLORS['neutral']};
}}

/* Спинбокс */
QSpinBox, QDoubleSpinBox {{
    background-color: {COLORS['white']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 4px;
}}
"""

# Стили для результатов аудита
RESULTS_STYLESHEET = f"""
QLabel#ratingLabel {{
    font-size: 28pt;
    font-weight: bold;
    color: {COLORS['primary']};
}}

QLabel#ratingDescLabel {{
    font-size: 11pt;
    color: {COLORS['text_light']};
}}

QLabel#issueCountLabel {{
    font-size: 14pt;
    font-weight: bold;
}}

QLabel#issueTypeLabel {{
    font-size: 10pt;
    color: {COLORS['text_light']};
}}
"""

# Стили для элементов статуса
STATUS_STYLESHEET = f"""
QLabel#successStatus {{
    color: {COLORS['success']};
    font-weight: bold;
}}

QLabel#warningStatus {{
    color: {COLORS['warning']};
    font-weight: bold;
}}

QLabel#errorStatus {{
    color: {COLORS['danger']};
    font-weight: bold;
}}

QLabel#infoStatus {{
    color: {COLORS['primary']};
    font-weight: bold;
}}
"""
