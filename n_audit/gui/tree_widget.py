#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интерактивное дерево проекта с выделением файлов с ошибками.

Архитектура:
- Показывает структуру всех файлов проекта в виде дерева
- Файлы с ошибками выделены красным/оранжевым цветом
- При выборе файла отображается список ошибок в нём
- При выборе ошибки показываются её детали
"""

from PyQt6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QTextEdit, QSplitter, QHeaderView,
    QListWidget, QListWidgetItem, QTabWidget, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QIcon, QFont, QPixmap, QBrush
from dataclasses import dataclass
from typing import List, Dict, Optional, Set, Tuple
from enum import Enum
from pathlib import Path
import os


@dataclass
class CodeIssueInfo:
    """Информация об ошибке в коде"""
    file_path: str
    line_number: int
    column: int
    code: str
    message: str
    severity: str
    issue_type: str
    context: str = ""
    tool: str = ""


class ErrorTreeWidget(QWidget):
    """Интерактивное дерево проекта с выделением файлов с ошибками
    
    Компоненты:
    1. Левая панель: Дерево файлов проекта (файлы с ошибками выделены)
    2. Центральная панель: Список ошибок выбранного файла
    3. Правая панель: Детали выбранной ошибки
    """
    
    issue_selected = pyqtSignal(CodeIssueInfo)  # Сигнал при выборе ошибки
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Данные
        self.all_issues: List[CodeIssueInfo] = []
        self.files_with_issues: Dict[str, List[CodeIssueInfo]] = {}  # file_path -> issues
        self.project_root: str = ""
        self.file_tree_items: Dict[str, QTreeWidgetItem] = {}  # file_path -> item
        
        # Текущее выделение
        self.current_selected_file: Optional[str] = None
        self.current_selected_issue: Optional[CodeIssueInfo] = None
        
        # UI элементы
        self.tree: Optional[QTreeWidget] = None
        self.issues_list: Optional[QListWidget] = None
        self.details_title: Optional[QLabel] = None
        self.details_text: Optional[QTextEdit] = None
        self.info_label: Optional[QLabel] = None
        self.stats_label: Optional[QLabel] = None
        
        self.init_ui()
    
    def init_ui(self):
        """Инициализировать UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Информационная панель сверху
        info_layout = QHBoxLayout()
        self.info_label = QLabel("Анализ проекта: выберите файл для просмотра ошибок")
        self.stats_label = QLabel("")
        info_layout.addWidget(self.info_label)
        info_layout.addStretch()
        info_layout.addWidget(self.stats_label)
        layout.addLayout(info_layout)
        
        # Основной сплиттер: дерево | ошибки | детали
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- ЛЕВАЯ ЧАСТЬ: Дерево файлов ---
        tree_widget = QWidget()
        tree_layout = QVBoxLayout(tree_widget)
        tree_layout.setContentsMargins(0, 0, 0, 0)
        
        tree_label = QLabel("📁 Файлы проекта")
        tree_font = tree_label.font()
        tree_font.setBold(True)
        tree_label.setFont(tree_font)
        tree_layout.addWidget(tree_label)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Структура проекта")
        self.tree.itemSelectionChanged.connect(self._on_tree_item_selected)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        tree_layout.addWidget(self.tree)
        
        main_splitter.addWidget(tree_widget)
        
        # --- СРЕДНЯЯ ЧАСТЬ: Список ошибок ---
        issues_widget = QWidget()
        issues_layout = QVBoxLayout(issues_widget)
        issues_layout.setContentsMargins(0, 0, 0, 0)
        
        issues_label = QLabel("🐛 Ошибки в файле")
        issues_font = issues_label.font()
        issues_font.setBold(True)
        issues_label.setFont(issues_font)
        issues_layout.addWidget(issues_label)
        
        self.issues_list = QListWidget()
        self.issues_list.itemSelectionChanged.connect(self._on_issue_selected)
        issues_layout.addWidget(self.issues_list)
        
        main_splitter.addWidget(issues_widget)
        
        # --- ПРАВАЯ ЧАСТЬ: Детали ошибки ---
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setContentsMargins(0, 0, 0, 0)
        
        details_label = QLabel("📝 Детали ошибки")
        details_font = details_label.font()
        details_font.setBold(True)
        details_label.setFont(details_font)
        details_layout.addWidget(details_label)
        
        self.details_title = QLabel()
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(11)
        self.details_title.setFont(title_font)
        self.details_title.setWordWrap(True)
        details_layout.addWidget(self.details_title)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)
        
        main_splitter.addWidget(details_widget)
        
        # Установяем пропорции
        main_splitter.setStretchFactor(0, 2)  # Дерево: 2x место
        main_splitter.setStretchFactor(1, 2)  # Ошибки: 2x место
        main_splitter.setStretchFactor(2, 3)  # Детали: 3x место
        
        layout.addWidget(main_splitter)
    
    def populate_from_report(self, report, project_root: str = "."):
        """Заполнить дерево из отчета об аудите
        
        Args:
            report: AuditReport с metrics содержащими ошибки
            project_root: Корневая папка проекта
        """
        self.clear()
        self.project_root = project_root
        
        if report.is_empty:
            self.info_label.setText("✓ Ошибок не найдено!")
            return
        
        # Собираем все ошибки
        self.all_issues = []
        self.files_with_issues = {}
        
        # Ошибки кода
        for issue in report.metrics.code_issues:
            issue_info = CodeIssueInfo(
                file_path=issue.file_path,
                line_number=issue.line_number,
                column=issue.column,
                code=issue.code,
                message=issue.message,
                severity=issue.severity.name,
                issue_type=issue.issue_type,
                context=issue.context,
                tool=issue.tool
            )
            self.all_issues.append(issue_info)
            
            # Группируем по файлам
            if issue.file_path not in self.files_with_issues:
                self.files_with_issues[issue.file_path] = []
            self.files_with_issues[issue.file_path].append(issue_info)
        
        # Ошибки безопасности
        for issue in report.metrics.security_issues:
            issue_info = CodeIssueInfo(
                file_path=issue.file_path,
                line_number=issue.line_number,
                column=issue.column,
                code=issue.code,
                message=issue.message,
                severity=issue.severity.name,
                issue_type='security',
                context=issue.context,
                tool=issue.tool
            )
            self.all_issues.append(issue_info)
            
            if issue.file_path not in self.files_with_issues:
                self.files_with_issues[issue.file_path] = []
            self.files_with_issues[issue.file_path].append(issue_info)
        
        # Теперь строим дерево папок/файлов
        self._build_file_tree()
        
        # Обновляем статистику
        total_issues = len(self.all_issues)
        total_files = len(self.files_with_issues)
        self.info_label.setText(f"📊 Анализ завершён: {total_issues} ошибок в {total_files} файлах")
        self.stats_label.setText(f"Файлов с ошибками: {total_files} | Всего ошибок: {total_issues}")
    
    def _build_file_tree(self):
        """Построить дерево файлов проекта с выделением ошибок"""
        self.tree.clear()
        self.file_tree_items.clear()
        
        # Получаем уникальные файлы и сортируем их
        all_files_set: Set[str] = set()
        for file_path in self.files_with_issues.keys():
            all_files_set.add(file_path)
        
        # Если есть файлы, строим дерево
        if all_files_set:
            all_files = sorted(all_files_set)
            self._add_files_to_tree(all_files)
        else:
            # Если нет ошибок в файлах, показываем сообщение
            item = QTreeWidgetItem(self.tree)
            item.setText(0, "📁 Нет файлов с ошибками")
    
    def _add_files_to_tree(self, files: List[str]):
        """Добавить файлы в дерево с иерархией папок"""
        root_items: Dict[str, QTreeWidgetItem] = {}  # папка -> item
        
        for file_path in files:
            # Нормализуем путь
            normalized_path = file_path.replace("\\", "/")
            parts = normalized_path.split("/")
            
            current_parent = self.tree
            current_path = ""
            
            # Проходим по каждой части пути (папки)
            for i, part in enumerate(parts[:-1]):  # Все кроме последнего (файл)
                current_path += part + "/"
                
                # Ищем или создаем папку
                if current_path not in root_items:
                    folder_item = QTreeWidgetItem(current_parent)
                    folder_item.setText(0, f"📁 {part}")
                    folder_item.setFont(0, self._get_folder_font())
                    root_items[current_path] = folder_item
                    current_parent = folder_item
                else:
                    current_parent = root_items[current_path]
            
            # Добавляем сам файл
            file_item = QTreeWidgetItem(current_parent)
            file_name = parts[-1]
            
            # Получаем количество ошибок
            issues_count = len(self.files_with_issues.get(file_path, []))
            
            # Строим текст элемента
            icon = "📄"
            file_item.setText(0, f"{icon} {file_name} ({issues_count})")
            
            # Выделяем файлы с ошибками
            self._color_file_item(file_item, file_path, issues_count)
            
            # Сохраняем ссылку
            self.file_tree_items[file_path] = file_item
            file_item.setData(0, Qt.ItemDataRole.UserRole, file_path)  # Сохраняем путь
    
    def _color_file_item(self, item: QTreeWidgetItem, file_path: str, issues_count: int):
        """Раскрасить элемент файла в зависимости от количества/серьезности ошибок"""
        if file_path not in self.files_with_issues:
            return
        
        issues = self.files_with_issues[file_path]
        
        # Определяем цвет по максимальной серьезности
        max_severity = self._get_max_severity(issues)
        
        if max_severity == "CRITICAL":
            bg_color = QColor("#ffe0e0")
            text_color = QColor("#cc0000")
        elif max_severity == "HIGH":
            bg_color = QColor("#ffe8cc")
            text_color = QColor("#cc6600")
        elif max_severity == "MEDIUM":
            bg_color = QColor("#fffacc")
            text_color = QColor("#ccaa00")
        else:  # LOW
            bg_color = QColor("#e8ffe8")
            text_color = QColor("#00cc00")
        
        item.setBackground(0, QBrush(bg_color))
        item.setForeground(0, text_color)
        
        # Делаем текст болдом
        font = item.font(0)
        font.setBold(True)
        item.setFont(0, font)
    
    def _get_max_severity(self, issues: List[CodeIssueInfo]) -> str:
        """Получить максимальную серьезность из списка ошибок"""
        severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        max_level = 0
        max_severity = "LOW"
        
        for issue in issues:
            level = severity_order.get(issue.severity, 0)
            if level > max_level:
                max_level = level
                max_severity = issue.severity
        
        return max_severity
    
    def _get_folder_font(self) -> QFont:
        """Получить шрифт для папок"""
        font = QFont()
        font.setItalic(True)
        return font
    
    def _on_tree_item_selected(self):
        """Обработчик выбора элемента в дереве"""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        
        if not file_path:
            return
        
        # Выбран файл
        self.current_selected_file = file_path
        self._update_issues_list(file_path)
    
    def _update_issues_list(self, file_path: str):
        """Обновить список ошибок для файла"""
        self.issues_list.clear()
        
        if file_path not in self.files_with_issues:
            return
        
        issues = self.files_with_issues[file_path]
        
        # Сортируем по номеру строки
        issues_sorted = sorted(issues, key=lambda x: x.line_number)
        
        for issue in issues_sorted:
            item_text = f"Строка {issue.line_number}: [{issue.code}] {issue.message[:60]}"
            list_item = QListWidgetItem(item_text)
            
            # Выделяем иконкой по серьезности
            severity_icon = self._get_severity_icon(issue.severity)
            list_item.setText(f"{severity_icon} {item_text}")
            
            # Сохраняем данные ошибки
            list_item.setData(Qt.ItemDataRole.UserRole, issue)
            
            self.issues_list.addItem(list_item)
    
    def _on_issue_selected(self):
        """Обработчик выбора ошибки в списке"""
        selected_items = self.issues_list.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        issue = item.data(Qt.ItemDataRole.UserRole)
        
        if not issue:
            return
        
        self.current_selected_issue = issue
        self._show_issue_details(issue)
        self.issue_selected.emit(issue)
    
    def _show_issue_details(self, issue: CodeIssueInfo):
        """Показать детальную информацию об ошибке"""
        # Заголовок
        title = f"{issue.code}: {issue.message}"
        self.details_title.setText(title)
        self.details_title.setStyleSheet(f"color: {self._get_color_hex(issue.severity)};")
        
        # Детали
        severity_icon = self._get_severity_icon(issue.severity)
        
        details_html = f"""
<b>{severity_icon} {issue.severity}</b> · {issue.tool}<br>
<br>
<b>📁 Файл:</b> {issue.file_path}<br>
<b>📍 Позиция:</b> строка {issue.line_number}, столбец {issue.column}<br>
<b>🏷️ Код:</b> {issue.code}<br>
<b>📋 Тип:</b> {issue.issue_type}<br>
<hr>
<b>Описание:</b><br>
{issue.message}<br>
"""
        
        if issue.context:
            # Форматируем контекст кода
            context_lines = issue.context.split('\n')
            context_html = "<pre style='background: #f5f5f5; padding: 10px; border-radius: 4px;'>"
            for line in context_lines:
                context_html += line + "\n"
            context_html += "</pre>"
            details_html += f"<hr><b>Контекст кода:</b><br>{context_html}"
        
        self.details_text.setHtml(details_html)
    
    def _get_severity_icon(self, severity: str) -> str:
        """Получить иконку по серьезности"""
        icons = {
            "CRITICAL": "🔴",
            "HIGH": "🟠",
            "MEDIUM": "🟡",
            "LOW": "🟢",
        }
        return icons.get(severity, "❓")
    
    def _get_color_hex(self, severity: str) -> str:
        """Получить HEX цвет по серьезности"""
        colors = {
            "CRITICAL": "#ff4444",
            "HIGH": "#ff8844",
            "MEDIUM": "#ffcc44",
            "LOW": "#44aa44",
        }
        return colors.get(severity, "#888888")
    
    def clear(self):
        """Очистить дерево"""
        self.tree.clear()
        self.issues_list.clear()
        self.all_issues.clear()
        self.files_with_issues.clear()
        self.file_tree_items.clear()
        self.details_title.setText("")
        self.details_text.setText("")
        self.info_label.setText("Дерево проекта: пусто")
        self.stats_label.setText("")
        self.current_selected_file = None
        self.current_selected_issue = None
    
    def get_all_issues(self) -> List[CodeIssueInfo]:
        """Получить все проблемы"""
        return self.all_issues
    
    def filter_by_severity(self, min_severity: str):
        """Отфильтровать ошибки по минимальной серьезности"""
        severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        min_level = severity_order.get(min_severity, 0)
        
        # Скрываем файлы с меньшей серьезностью
        for file_path, item in self.file_tree_items.items():
            issues = self.files_with_issues.get(file_path, [])
            max_severity = self._get_max_severity(issues)
            max_level = severity_order.get(max_severity, 0)
            item.setHidden(max_level < min_level)
