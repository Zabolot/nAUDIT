#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интерактивное дерево ошибок - деталей просмотр всех проблем в проекте.

Пользователь может развернуть:
- По типу проблемы (Ошибки, Предупреждения, Безопасность)
- По файлу
- По конкретной ошибке с контекстом
"""

from PyQt6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QTextEdit, QSplitter, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal, QRect
from PyQt6.QtGui import QColor, QIcon, QFont, QPixmap
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class IssueCategory(Enum):
    """Категория проблемы"""
    ERROR = "🔴 Ошибки"
    WARNING = "🟠 Предупреждения"
    SECURITY = "⚠️ Безопасность"
    STYLE = "🟡 Стиль/Оформление"


@dataclass
class TreeIssue:
    """Проблема для отображения в дереве"""
    category: IssueCategory
    file_path: str
    line_number: int
    column: int
    code: str
    message: str
    context: str = ""
    severity: str = "medium"
    tool: str = ""


class ErrorTreeWidget(QWidget):
    """Интерактивное дерево для просмотра ошибок"""
    
    issue_selected = pyqtSignal(TreeIssue)  # Сигнал при выборе проблемы
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.issues: Dict[str, List[TreeIssue]] = {}
        self.tree_items: Dict[str, QTreeWidgetItem] = {}
        self.init_ui()
    
    def init_ui(self):
        """Инициализировать UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Информационная панель
        info_layout = QHBoxLayout()
        self.info_label = QLabel("Дерево ошибок: выберите элемент для деталей")
        info_layout.addWidget(self.info_label)
        layout.addLayout(info_layout)
        
        # Сплиттер для дерева и деталей
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Дерево ошибок
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Проблемы в коде")
        self.tree.itemSelectionChanged.connect(self._on_item_selected)
        self.tree.itemExpanded.connect(self._on_item_expanded)
        self.tree.itemCollapsed.connect(self._on_item_collapsed)
        splitter.addWidget(self.tree)
        
        # Панель деталей
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        self.details_title = QLabel()
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        self.details_title.setFont(font)
        details_layout.addWidget(self.details_title)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)
        
        splitter.addWidget(details_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
    
    def populate_from_report(self, report):
        """Заполнить дерево из отчета об аудите"""
        self.clear()
        
        if report.is_empty:
            self.tree.clear()
            item = QTreeWidgetItem(self.tree)
            item.setText(0, "Papka pusta - problem ne najdeno")
            return
        
        # Организуем ошибки по категориям
        issues_by_category = {}
        
        # Ошибки кода
        for issue in report.metrics.code_issues:
            category = self._get_category(issue.issue_type, issue.code)
            if category not in issues_by_category:
                issues_by_category[category] = []
            
            tree_issue = TreeIssue(
                category=category,
                file_path=issue.file_path,
                line_number=issue.line_number,
                column=issue.column,
                code=issue.code,
                message=issue.message,
                context=issue.context,
                severity=issue.severity.name,
                tool=issue.tool
            )
            issues_by_category[category].append(tree_issue)
        
        # Проблемы безопасности
        for issue in report.metrics.security_issues:
            category = IssueCategory.SECURITY
            if category not in issues_by_category:
                issues_by_category[category] = []
            
            tree_issue = TreeIssue(
                category=category,
                file_path=issue.file_path,
                line_number=issue.line_number,
                column=issue.column,
                code=issue.code,
                message=issue.message,
                severity=issue.severity.name,
                tool=issue.tool
            )
            issues_by_category[category].append(tree_issue)
        
        # Добавляем в дерево
        self.issues = issues_by_category
        
        for category in [IssueCategory.ERROR, IssueCategory.SECURITY, IssueCategory.WARNING, IssueCategory.STYLE]:
            if category not in issues_by_category:
                continue
            
            issues = issues_by_category[category]
            category_item = QTreeWidgetItem(self.tree)
            category_item.setText(0, f"{category.value} ({len(issues)})")
            category_item.setExpanded(True)
            self.tree_items[category.name] = category_item
            
            # Группируем по файлам
            by_file = {}
            for issue in issues:
                if issue.file_path not in by_file:
                    by_file[issue.file_path] = []
                by_file[issue.file_path].append(issue)
            
            # Добавляем файлы
            for file_path in sorted(by_file.keys()):
                file_issues = by_file[file_path]
                file_item = QTreeWidgetItem(category_item)
                file_item.setText(0, f"📄 {file_path} ({len(file_issues)})")
                
                # Добавляем ошибки
                for idx, issue in enumerate(file_issues):
                    issue_item = QTreeWidgetItem(file_item)
                    
                    # Иконка по серьезности
                    icon = self._get_icon(issue.severity)
                    issue_item.setText(0, f"{icon} Строка {issue.line_number}: {issue.code} - {issue.message[:50]}")
                    
                    # Сохраняем данные ошибки
                    issue_item.setData(0, Qt.ItemDataRole.UserRole, issue)
                    
                    # Цвет по серьезности
                    color = self._get_color(issue.severity)
                    issue_item.setForeground(0, color)
        
        # Обновляем инфо
        total_issues = sum(len(issues) for issues in issues_by_category.values())
        self.info_label.setText(f"Всего проблем: {total_issues}")
    
    def _on_item_selected(self):
        """Обработчик выбора элемента"""
        selected = self.tree.selectedItems()
        if not selected:
            return
        
        item = selected[0]
        issue = item.data(0, Qt.ItemDataRole.UserRole)
        
        if not issue:
            return
        
        # Показываем детали
        self._show_details(issue)
        self.issue_selected.emit(issue)
    
    def _on_item_expanded(self, item):
        """Обработчик расширения элемента"""
        # Обновляем иконку
        item.setText(0, item.text(0).replace("▶", "▼"))
    
    def _on_item_collapsed(self, item):
        """Обработчик свертывания элемента"""
        # Обновляем иконку
        item.setText(0, item.text(0).replace("▼", "▶"))
    
    def _show_details(self, issue: TreeIssue):
        """Показать детальную информацию об ошибке"""
        # Заголовок
        title = f"{issue.code} - {issue.message}"
        self.details_title.setText(title)
        
        # Детали
        details = f"""
<b>Файл:</b> {issue.file_path}<br>
<b>Строка:</b> {issue.line_number} (колонка {issue.column})<br>
<b>Инструмент:</b> {issue.tool}<br>
<b>Серьезность:</b> {issue.severity}<br>
<hr>
<b>Сообщение:</b><br>
{issue.message}<br>
"""
        
        if issue.context:
            details += f"<hr><b>Контекст кода:</b><br><pre>{issue.context}</pre>"
        
        self.details_text.setHtml(details)
    
    def _get_category(self, issue_type: str, code: str) -> IssueCategory:
        """Определить категорию по типу"""
        if issue_type == 'security':
            return IssueCategory.SECURITY
        
        if code and code[0] == 'E':
            return IssueCategory.ERROR
        
        if code and code[0] in ['W', 'C']:
            return IssueCategory.WARNING
        
        return IssueCategory.STYLE
    
    def _get_icon(self, severity: str) -> str:
        """Получить иконку по серьезности"""
        icons = {
            'CRITICAL': '🔴',
            'HIGH': '🟠',
            'MEDIUM': '🟡',
            'LOW': '🟢',
        }
        return icons.get(severity, '❓')
    
    def _get_color(self, severity: str) -> QColor:
        """Получить цвет по серьезности"""
        colors = {
            'CRITICAL': QColor('#ff4444'),
            'HIGH': QColor('#ff8844'),
            'MEDIUM': QColor('#ffcc44'),
            'LOW': QColor('#44aa44'),
        }
        return colors.get(severity, QColor('#888888'))
    
    def clear(self):
        """Очистить дерево"""
        self.tree.clear()
        self.issues.clear()
        self.tree_items.clear()
        self.details_title.setText("")
        self.details_text.setText("")
        self.info_label.setText("Дерево ошибок пусто")
    
    def filter_by_severity(self, min_severity: str):
        """Отфильтровать по минимальной серьезности"""
        severity_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        min_level = severity_order.get(min_severity, 0)
        
        # Скрываем элементы с меньшей серьезностью
        for i in range(self.tree.topLevelItemCount()):
            category_item = self.tree.topLevelItem(i)
            for j in range(category_item.childCount()):
                file_item = category_item.child(j)
                for k in range(file_item.childCount()):
                    issue_item = file_item.child(k)
                    issue = issue_item.data(0, Qt.ItemDataRole.UserRole)
                    if issue:
                        severity_level = severity_order.get(issue.severity, 0)
                        issue_item.setHidden(severity_level < min_level)
    
    def get_all_issues(self) -> List[TreeIssue]:
        """Получить все проблемы из дерева"""
        all_issues = []
        for issues in self.issues.values():
            all_issues.extend(issues)
        return all_issues
