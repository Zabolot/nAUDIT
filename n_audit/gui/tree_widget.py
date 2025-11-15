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
import logging

# Get logger
logger = logging.getLogger(__name__)


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
    file_selected = pyqtSignal(str)  # Сигнал при выборе файла (для синхронизации с графом)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Данные
        self.all_issues: List[CodeIssueInfo] = []
        self.files_with_issues: Dict[str, List[CodeIssueInfo]] = {}  # file_path -> issues
        self.all_project_files: Set[str] = set()  # ✅ ВСЕ файлы проекта (с ошибками и без)
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
        try:
            self.clear()
            self.project_root = project_root
            
            logger.info(f"Starting populate_from_report: {project_root}")
            logger.info(f"Report type: {type(report)}")
            logger.info(f"Report attributes: {dir(report)[:10]}")  # Первые 10 атрибутов
            
            # Собираем все ошибки
            self.all_issues = []
            self.files_with_issues = {}
            self.all_project_files = set()  # ✅ ВСЕ файлы проекта (с ошибками и без)
            
            # Ошибки кода - ищем в разных местах (для совместимости)
            code_issues = []
            if hasattr(report, 'code_issues'):
                code_issues = report.code_issues
                logger.debug(f"Found code_issues at report.code_issues: {len(code_issues)} items")
            elif hasattr(report, 'metrics') and hasattr(report.metrics, 'code_issues'):
                code_issues = report.metrics.code_issues
                logger.debug(f"Found code_issues at report.metrics.code_issues: {len(code_issues)} items")
            else:
                logger.debug("No code_issues found in report")
            
            # Обработка ошибок кода с обработкой исключений
            for idx, issue in enumerate(code_issues):
                try:
                    # Поддерживаем оба формата: словарь и объект
                    if isinstance(issue, dict):
                        file_path = str(issue.get('file', '')).replace('\\', '/')
                        line_number = issue.get('line', 0)
                        column = issue.get('column', 0)
                        code = issue.get('code', '')
                        message = issue.get('message', '')
                        severity = issue.get('severity', 'LOW')
                        context = issue.get('context', '')
                        tool = issue.get('tool', '')
                    else:
                        # Объект с атрибутами
                        # Поддерживаем разные имена атрибутов у issue объектов
                        file_path = (getattr(issue, 'file', None) or getattr(issue, 'file_path', None)
                                     or getattr(issue, 'path', None) or getattr(issue, 'filename', None) or '')
                        file_path = str(file_path).replace('\\', '/')
                        line_number = (getattr(issue, 'line', None) or getattr(issue, 'line_number', 0) or 0)
                        column = (getattr(issue, 'column', None) or getattr(issue, 'col', 0) or 0)
                        code = (getattr(issue, 'code', None) or getattr(issue, 'rule', '') or '')
                        message = (getattr(issue, 'message', None) or getattr(issue, 'msg', '') or '')
                        severity_attr = getattr(issue, 'severity', None)
                        if severity_attr is None:
                            severity = 'LOW'
                        else:
                            try:
                                severity = severity_attr.name if hasattr(severity_attr, 'name') else str(severity_attr)
                            except Exception:
                                severity = str(severity_attr)
                        context = (getattr(issue, 'context', None) or '')
                        tool = (getattr(issue, 'tool', None) or getattr(issue, 'engine', '') or '')
                    
                    if not file_path:
                        logger.warning(f"Code issue #{idx} has empty file_path: {issue}")
                        continue
                    # Нормализуем путь относительно project_root, если возможно
                    normalized_path = self._normalize_path(file_path, project_root)

                    issue_info = CodeIssueInfo(
                        file_path=normalized_path,
                        line_number=line_number,
                        column=column,
                        code=code,
                        message=message,
                        severity=severity,
                        issue_type='code',
                        context=context,
                        tool=tool
                    )
                    self.all_issues.append(issue_info)
                    
                    # Группируем по файлам
                    if normalized_path not in self.files_with_issues:
                        self.files_with_issues[normalized_path] = []
                    self.files_with_issues[normalized_path].append(issue_info)
                    
                except Exception as e:
                    logger.error(f"Error processing code issue #{idx}: {e}", exc_info=True)
                    logger.error(f"Issue data: {issue}")
                    continue
            
            logger.info(f"Processed code issues: {len(self.all_issues)}")
            
            # Ошибки безопасности - ищем в разных местах
            security_issues = []
            if hasattr(report, 'security_issues'):
                security_issues = report.security_issues
                logger.debug(f"Found security_issues at report.security_issues: {len(security_issues)} items")
            elif hasattr(report, 'metrics') and hasattr(report.metrics, 'security_issues'):
                security_issues = report.metrics.security_issues
                logger.debug(f"Found security_issues at report.metrics.security_issues: {len(security_issues)} items")
            else:
                logger.debug("No security_issues found in report")
            
            # Обработка ошибок безопасности с обработкой исключений
            for idx, issue in enumerate(security_issues):
                try:
                    # Поддерживаем оба формата: словарь и объект
                    if isinstance(issue, dict):
                        file_path = str(issue.get('file', '')).replace('\\', '/')
                        line_number = issue.get('line', 0)
                        column = issue.get('column', 0)
                        code = issue.get('code', '')
                        message = issue.get('message', '')
                        severity = issue.get('severity', 'HIGH')
                        context = issue.get('context', '')
                        tool = issue.get('tool', '')
                    else:
                        # Объект с атрибутами
                        # Поддерживаем разные имена атрибутов у issue объектов
                        file_path = (getattr(issue, 'file', None) or getattr(issue, 'file_path', None)
                                     or getattr(issue, 'path', None) or getattr(issue, 'filename', None) or '')
                        file_path = str(file_path).replace('\\', '/')
                        line_number = (getattr(issue, 'line', None) or getattr(issue, 'line_number', 0) or 0)
                        column = (getattr(issue, 'column', None) or getattr(issue, 'col', 0) or 0)
                        code = (getattr(issue, 'code', None) or getattr(issue, 'rule', '') or '')
                        message = (getattr(issue, 'message', None) or getattr(issue, 'msg', '') or '')
                        severity_attr = getattr(issue, 'severity', None)
                        if severity_attr is None:
                            severity = 'HIGH'
                        else:
                            try:
                                severity = severity_attr.name if hasattr(severity_attr, 'name') else str(severity_attr)
                            except Exception:
                                severity = str(severity_attr)
                        context = (getattr(issue, 'context', None) or '')
                        tool = (getattr(issue, 'tool', None) or getattr(issue, 'engine', '') or '')
                    
                    if not file_path:
                        logger.warning(f"Security issue #{idx} has empty file_path: {issue}")
                        continue
                    # Нормализуем путь относительно project_root, если возможно
                    normalized_path = self._normalize_path(file_path, project_root)

                    issue_info = CodeIssueInfo(
                        file_path=normalized_path,
                        line_number=line_number,
                        column=column,
                        code=code,
                        message=message,
                        severity=severity,
                        issue_type='security',
                        context=context,
                        tool=tool
                    )
                    self.all_issues.append(issue_info)

                    if normalized_path not in self.files_with_issues:
                        self.files_with_issues[normalized_path] = []
                    self.files_with_issues[normalized_path].append(issue_info)
                    
                except Exception as e:
                    logger.error(f"Error processing security issue #{idx}: {e}", exc_info=True)
                    logger.error(f"Issue data: {issue}")
                    continue
            
            logger.info(f"Processed security issues: total now {len(self.all_issues)}")
            logger.info(f"Files with issues: {list(self.files_with_issues.keys())}")
            
            # ✅ НОВОЕ: Собираем ВСЕ файлы проекта (не только с ошибками)
            # Пытаемся получить список всех файлов из отчета
            self._collect_all_project_files(report)
            logger.info(f"Total project files collected: {len(self.all_project_files)}")
            
            # Теперь строим дерево папок/файлов
            self._build_file_tree()
            
            # Обновляем статистику
            total_issues = len(self.all_issues)
            total_files = len(self.files_with_issues)
            all_files_count = len(self.all_project_files)
            
            logger.info(f"Tree built: total_issues={total_issues}, files_with_issues={total_files}, all_files={all_files_count}")
            
            if total_issues == 0:
                self.info_label.setText(f"✓ Анализ завершён - ошибок не найдено! (Файлов: {all_files_count})")
                logger.info("No issues found")
            else:
                self.info_label.setText(f"📊 Анализ завершён: {total_issues} ошибок в {total_files} файлах (всего: {all_files_count})")
                logger.info(f"Analysis complete: {total_issues} issues in {total_files} files (total: {all_files_count})")
                
                # ✅ НОВОЕ: Автоматически выбираем первый файл с ошибками
                if self.files_with_issues:
                    first_file = list(self.files_with_issues.keys())[0]
                    logger.info(f"Auto-selecting first file with issues: {first_file}")

                    # Ищем item в дереве и выбираем его
                    target_item = None
                    if first_file in self.file_tree_items:
                        target_item = self.file_tree_items[first_file]
                    else:
                        # Попробуем найти по имени файла (basename) или по суффиксу
                        first_basename = Path(first_file).name
                        for k, it in self.file_tree_items.items():
                            if Path(k).name == first_basename or k.endswith(first_file) or first_file.endswith(k):
                                target_item = it
                                logger.info(f"Auto-select fallback matched tree key: {k} for requested {first_file}")
                                break

                    if target_item is not None:
                        self.tree.setCurrentItem(target_item)
                        self._on_tree_item_selected()
                        logger.info(f"Selected and highlighted file via fallback: {first_file}")
                    else:
                        logger.warning(f"Could not auto-select first file: {first_file}. No matching tree item found.")
            
            self.stats_label.setText(f"Файлов с ошибками: {total_files} | Всего ошибок: {total_issues} | Файлов: {all_files_count}")
            
        except Exception as e:
            logger.error(f"Critical error in populate_from_report: {e}", exc_info=True)
            self.info_label.setText(f"❌ Ошибка при обработке отчета: {e}")
            raise
    
    def _collect_all_project_files(self, report):
        """✅ НОВОЕ: Собрать ВСЕ файлы проекта из отчета"""
        # Добавляем файлы с ошибками
        for file_path in self.files_with_issues.keys():
            self.all_project_files.add(str(file_path).replace("\\", "/"))
        
        # Пытаемся получить все файлы из отчета (разные варианты)
        all_files_sources = []
        
        # Вариант 1: report.files
        if hasattr(report, 'files'):
            all_files_sources.append(report.files)
            logger.debug(f"Found files at report.files: {len(report.files)} items")
        
        # Вариант 2: report.metrics.files
        if hasattr(report, 'metrics') and hasattr(report.metrics, 'files'):
            all_files_sources.append(report.metrics.files)
            logger.debug(f"Found files at report.metrics.files: {len(report.metrics.files)} items")
        
        # Вариант 3: report.analyzed_files
        if hasattr(report, 'analyzed_files'):
            all_files_sources.append(report.analyzed_files)
            logger.debug(f"Found files at report.analyzed_files: {len(report.analyzed_files)} items")
        
        # Вариант 4: report.metrics.all_files
        if hasattr(report, 'metrics') and hasattr(report.metrics, 'all_files'):
            all_files_sources.append(report.metrics.all_files)
            logger.debug(f"Found files at report.metrics.all_files: {len(report.metrics.all_files)} items")
        
        # Обрабатываем каждый источник
        for all_files in all_files_sources:
            if all_files:
                for file_entry in all_files:
                    try:
                        # Поддерживаем разные форматы: строки и объекты
                        if isinstance(file_entry, dict):
                            file_path = file_entry.get('path') or file_entry.get('file') or file_entry.get('name')
                        elif isinstance(file_entry, str):
                            file_path = file_entry
                        else:
                            file_path = getattr(file_entry, 'path', None) or getattr(file_entry, 'file', None)
                        
                        if file_path:
                            # Нормализуем пути относительно project_root
                            normalized = self._normalize_path(str(file_path), getattr(self, 'project_root', '.'))
                            self.all_project_files.add(normalized)
                    except:
                        pass  # Пропускаем если не можем обработать
        
        logger.info(f"Collected {len(self.all_project_files)} total project files")

    def _normalize_path(self, file_path: str, project_root: str) -> str:
        """Нормализовать путь: привести к POSIX-формату и попытаться сделать относительным к project_root.

        Возвращает относительный путь (POSIX, без ведущего './') если файл находится внутри project_root,
        иначе возвращает абсолютный путь в POSIX-формате.
        """
        try:
            p = Path(file_path)
            project_root_path = Path(project_root or ".").resolve()

            # Если путь не абсолютный - попробуем разрешить относительно project_root
            if not p.is_absolute():
                candidate = (project_root_path / p).resolve()
            else:
                candidate = p.resolve()

            try:
                rel = candidate.relative_to(project_root_path)
                rel_str = str(rel).replace('\\', '/')
                # Strip leading './' if any
                if rel_str.startswith('./'):
                    rel_str = rel_str[2:]
                return rel_str
            except Exception:
                # Не удалось сделать относительным - вернуть абсолютный путь
                return str(candidate).replace('\\', '/')
        except Exception:
            return str(file_path).replace('\\', '/')
    
    def _build_file_tree(self):
        """Построить дерево файлов проекта с выделением ошибок
        
        ✅ НОВОЕ: Показывает ВСЕ файлы проекта, а не только с ошибками
        """
        logger.debug("_build_file_tree called")
        self.tree.clear()
        self.file_tree_items.clear()
        
        # ✅ Используем ВСЕ файлы проекта, а не только файлы с ошибками
        all_files_set = self.all_project_files if self.all_project_files else set(self.files_with_issues.keys())
        
        logger.debug(f"Found {len(self.all_project_files)} total files, {len(self.files_with_issues)} with issues")
        logger.info(f"Building file tree: {len(all_files_set)} total files to display")
        
        # Если есть файлы, строим дерево
        if all_files_set:
            all_files = sorted(all_files_set)
            logger.debug(f"Building tree for {len(all_files)} files (total in project)")
            
            # ✅ НОВОЕ: Добавляем корневую папку с общей статистикой ошибок
            total_issues = len(self.all_issues)
            total_files_with_issues = len(self.files_with_issues)
            
            root_item = QTreeWidgetItem(self.tree)
            root_icon = "🔍" if total_issues == 0 else "❌" if total_issues > 0 else "✓"
            root_item.setText(0, f"{root_icon} РЕЗУЛЬТАТЫ АУДИТА ({total_issues} ошибок в {total_files_with_issues} файлах)")
            root_item.setExpanded(True)
            
            # Делаем корневой элемент выделенным
            root_font = root_item.font(0)
            root_font.setBold(True)
            root_font.setPointSize(root_font.pointSize() + 1)
            root_item.setFont(0, root_font)
            
            if total_issues > 0:
                root_item.setForeground(0, QColor("#cc0000"))
                root_item.setBackground(0, QColor("#ffe0e0"))
            else:
                root_item.setForeground(0, QColor("#00aa00"))
                root_item.setBackground(0, QColor("#e0ffe0"))
            
            self._add_files_to_tree(all_files)
            logger.debug(f"Tree items after build: {len(self.file_tree_items)}")
        else:
            # Если нет файлов вообще
            logger.debug("No files found in project")
            item = QTreeWidgetItem(self.tree)
            item.setText(0, "📁 Проект пуст или не проанализирован")
    
    def _add_files_to_tree(self, files: List[str]):
        """Добавить файлы в дерево с иерархией папок"""
        root_items: Dict[str, QTreeWidgetItem] = {}  # папка -> item
        logger.debug(f"_add_files_to_tree called with {len(files)} files")
        
        for file_path in files:
            # Нормализуем путь (гарантируем POSIX-формат)
            normalized_path = str(file_path).replace("\\", "/")
            parts = normalized_path.split("/")
            logger.debug(f"Processing file: {normalized_path} ({len(parts)} parts)")
            
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
                    folder_item.setExpanded(True)  # ✅ Раскрыть папки автоматически
                    root_items[current_path] = folder_item
                    logger.debug(f"Created folder item: {current_path}")
                    current_parent = folder_item
                else:
                    current_parent = root_items[current_path]
            
            # Добавляем сам файл
            file_item = QTreeWidgetItem(current_parent)
            file_name = parts[-1]
            
            # Получаем количество ошибок (используем нормализованный ключ)
            issues_count = len(self.files_with_issues.get(normalized_path, []))
            logger.debug(f"Adding file item: {file_name} with {issues_count} issues")
            
            # Строим текст элемента
            icon = "📄"
            file_item.setText(0, f"{icon} {file_name} ({issues_count})")
            
            # Выделяем файлы с ошибками
            self._color_file_item(file_item, normalized_path, issues_count)
            
            # Сохраняем ссылку (используем нормализованный путь)
            self.file_tree_items[normalized_path] = file_item
            file_item.setData(0, Qt.ItemDataRole.UserRole, normalized_path)  # Сохраняем путь
    
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
        # Эмитируем сигнал для синхронизации с графом
        self.file_selected.emit(file_path)
    
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
        self.all_project_files.clear()  # ✅ Очистить все файлы
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
