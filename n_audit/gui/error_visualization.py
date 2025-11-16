#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комбинированный визуализатор ошибок

Содержит:
- Иерархическое дерево ошибок (левая часть)
- Граф-визуализация проекта (правая часть)
- Возможность переключения между режимами просмотра
"""

from enum import Enum
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QStackedWidget, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal

from n_audit.gui.tree_widget import ErrorTreeWidget
from n_audit.gui.graph_visualizer_v2_7 import GraphVisualizerWidget
from pathlib import Path


class ViewMode(Enum):
    """Режимы просмотра"""
    TREE = "tree"      # Иерархическое дерево
    GRAPH = "graph"    # Граф-визуализация
    SPLIT = "split"    # Оба одновременно (дерево слева, граф справа)


class ErrorVisualizationWidget(QWidget):
    """
    Комбинированный визуализатор ошибок проекта
    
    Содержит несколько режимов просмотра:
    1. TREE - классическое иерархическое дерево
    2. GRAPH - интерактивная граф-визуализация всех файлов проекта
    3. SPLIT - оба режима одновременно (дерево + граф)
    """
    
    # Сигналы
    file_selected = pyqtSignal(str)  # Выбран файл
    view_mode_changed = pyqtSignal(ViewMode)  # Режим просмотра изменился
    
    def __init__(self):
        super().__init__()
        
        # Текущий режим
        self.current_mode = ViewMode.TREE
        
        # Компоненты для основных режимов
        self.tree_widget = ErrorTreeWidget()
        self.graph_widget = GraphVisualizerWidget()
        
        # Компоненты для split режима (отдельные экземпляры)
        self.tree_widget_split = ErrorTreeWidget()
        self.graph_widget_split = GraphVisualizerWidget()
        
        # UI
        self.init_ui()
    
    def init_ui(self):
        """Инициализировать UI"""
        layout = QVBoxLayout(self)
        
        # Панель управления режимами
        control_layout = QHBoxLayout()
        
        control_layout.addWidget(QLabel("Режим просмотра:"))
        
        # Кнопка "Дерево"
        self.tree_btn = QPushButton("🌳 Дерево")
        self.tree_btn.setCheckable(True)
        self.tree_btn.setChecked(True)
        self.tree_btn.clicked.connect(self._on_tree_mode)
        control_layout.addWidget(self.tree_btn)
        
        # Кнопка "Граф"
        self.graph_btn = QPushButton("🕸️  Граф")
        self.graph_btn.setCheckable(True)
        self.graph_btn.clicked.connect(self._on_graph_mode)
        control_layout.addWidget(self.graph_btn)
        
        # Кнопка "Оба"
        self.split_btn = QPushButton("📊 Оба")
        self.split_btn.setCheckable(True)
        self.split_btn.clicked.connect(self._on_split_mode)
        control_layout.addWidget(self.split_btn)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # Основной виджет с режимами
        self.stacked_widget = QStackedWidget()
        
        # Страница 1: Только дерево
        self.stacked_widget.addWidget(self.tree_widget)
        
        # Страница 2: Только граф
        self.stacked_widget.addWidget(self.graph_widget)
        
        # Страница 3: Оба (дерево слева, граф справа)
        split_widget = self._create_split_view()
        self.stacked_widget.addWidget(split_widget)
        
        layout.addWidget(self.stacked_widget)
        
        # Связываем сигналы
        self.tree_widget.issue_selected.connect(self._on_issue_selected)
        self.graph_widget.file_selected.connect(self.file_selected.emit)

        # ✅ НОВОЕ: Синхронизация дерева и графа
        # Когда выбран файл в основном дереве - выделяем в основном графе
        self.tree_widget.file_selected.connect(self._on_tree_file_selected)
        # Когда выбран файл в основном графе - выделяем в основном дереве
        if hasattr(self.graph_widget, 'file_selected'):
            self.graph_widget.file_selected.connect(self._on_graph_file_selected)

        # Для split режима: соединяем их между собой
        self.tree_widget_split.issue_selected.connect(self._on_issue_selected)
        self.graph_widget_split.file_selected.connect(self.file_selected.emit)
        self.tree_widget_split.file_selected.connect(self._on_tree_file_selected_split)
        if hasattr(self.graph_widget_split, 'file_selected'):
            self.graph_widget_split.file_selected.connect(self._on_graph_file_selected_split)
        
        # Устанавливаем начальную страницу
        self.stacked_widget.setCurrentIndex(0)
    
    def _create_split_view(self) -> QWidget:
        """Создать вид с деревом и графом рядом"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Левая часть - дерево (50%)
        layout.addWidget(self.tree_widget_split, 1)
        
        # Правая часть - граф (50%)
        layout.addWidget(self.graph_widget_split, 1)
        
        return widget
    
    def _on_tree_mode(self):
        """Переключиться на режим дерева"""
        if self.current_mode == ViewMode.TREE:
            return
        
        self.current_mode = ViewMode.TREE
        self.stacked_widget.setCurrentIndex(0)
        self._update_buttons()
        self.view_mode_changed.emit(ViewMode.TREE)
    
    def _on_graph_mode(self):
        """Переключиться на режим графа"""
        if self.current_mode == ViewMode.GRAPH:
            return
        
        self.current_mode = ViewMode.GRAPH
        self.stacked_widget.setCurrentIndex(1)
        self._update_buttons()
        self.view_mode_changed.emit(ViewMode.GRAPH)
        
        # Принудительный refresh когда переключаемся на граф
        print("[ErrorVisualizationWidget] ⚠ Переключаюсь на граф - refresh...")
        if hasattr(self.graph_widget, '_render_graph'):
            self.graph_widget._render_graph()
    
    def _on_split_mode(self):
        """Переключиться на режим оба"""
        if self.current_mode == ViewMode.SPLIT:
            return
        
        self.current_mode = ViewMode.SPLIT
        self.stacked_widget.setCurrentIndex(2)
        self._update_buttons()
        self.view_mode_changed.emit(ViewMode.SPLIT)
        
        # Принудительный refresh при переключении на split
        print("[ErrorVisualizationWidget] ⚠ Переключаюсь на split - refresh...")
        if hasattr(self.graph_widget_split, '_render_graph'):
            self.graph_widget_split._render_graph()

    def _on_tree_file_selected_split(self, file_path: str):
        """
        Синхронизация для split view: файл выбран в левом дереве split -> выделяем в правом графе split
        """
        if not file_path:
            return
        if hasattr(self.graph_widget_split, 'highlight_file'):
            self.graph_widget_split.highlight_file(file_path)

    def _on_graph_file_selected_split(self, file_path: str):
        """
        Синхронизация для split view: файл выбран в правом графе split -> выделяем в левом дереве split
        """
        if not file_path:
            return
        normalized_path = str(file_path).replace("\\", "/")
        if hasattr(self.tree_widget_split, 'select_item_by_path'):
            self.tree_widget_split.select_item_by_path(normalized_path)
    
    def _update_buttons(self):
        """Обновить состояние кнопок"""
        self.tree_btn.setChecked(self.current_mode == ViewMode.TREE)
        self.graph_btn.setChecked(self.current_mode == ViewMode.GRAPH)
        self.split_btn.setChecked(self.current_mode == ViewMode.SPLIT)
    
    def populate_from_report(self, report, project_root: str = "."):
        """
        Заполнить визуализацию из отчета
        
        Args:
            report: AuditReport с информацией об ошибках
            project_root: корень проекта
        """
        # Заполняем компоненты основных режимов
        # Сначала дерево (оно является источником истины по маппингу файлов->issues)
        self.tree_widget.populate_from_report(report, project_root)

        # Передаём карту files_with_issues в графы, чтобы избежать рассинхронизации
        files_map = getattr(self.tree_widget, 'files_with_issues', None)
        self.graph_widget.populate_from_report(report, project_root, files_with_issues=files_map)
        
        # Заполняем компоненты split режима
        self.tree_widget_split.populate_from_report(report, project_root)
        files_map_split = getattr(self.tree_widget_split, 'files_with_issues', None)
        self.graph_widget_split.populate_from_report(report, project_root, files_with_issues=files_map_split)
    
    def clear(self):
        """Очистить обе визуализации"""
        self.tree_widget.clear()
        self.graph_widget.clear()
        self.tree_widget_split.clear()
        self.graph_widget_split.clear()
    
    def get_all_issues(self):
        """Получить все ошибки (делегируем дереву)"""
        return self.tree_widget.get_all_issues()
    
    def filter_by_severity(self, min_severity: str):
        """Фильтровать по серьезности (делегируем обоим)"""
        self.tree_widget.filter_by_severity(min_severity)
        self.graph_widget.filter_by_severity(min_severity)
        self.tree_widget_split.filter_by_severity(min_severity)
        self.graph_widget_split.filter_by_severity(min_severity)
    
    def _on_issue_selected(self, issue):
        """Обработать выбор ошибки из дерева"""
        if hasattr(issue, 'file'):
            self.file_selected.emit(issue.file)
    
    def _on_tree_file_selected(self, file_path: str):
        """
        🔄 СИНХРОНИЗАЦИЯ: Файл выбран в дереве - выделить в графе
        """
        if not file_path:
            return
        
        # Выделяем файл в графе
        if self.current_mode == ViewMode.GRAPH:
            if hasattr(self.graph_widget, 'highlight_file'):
                self.graph_widget.highlight_file(file_path)
        elif self.current_mode == ViewMode.SPLIT:
            if hasattr(self.graph_widget_split, 'highlight_file'):
                self.graph_widget_split.highlight_file(file_path)
        
        import logging
        logging.getLogger(__name__).info(f"[Sync] 🔗 Дерево→Граф: {file_path}")
    
    def _on_graph_file_selected(self, file_path: str):
        """
        🔄 СИНХРОНИЗАЦИЯ: Файл выбран в графе - выделить в дереве
        """
        if not file_path:
            return
        
        # Нормализуем путь
        normalized_path = str(file_path).replace("\\", "/")
        
        # Выделяем в дереве
        if self.current_mode == ViewMode.TREE:
            if hasattr(self.tree_widget, 'select_item_by_path'):
                self.tree_widget.select_item_by_path(normalized_path)
        elif self.current_mode == ViewMode.SPLIT:
            if hasattr(self.tree_widget_split, 'select_item_by_path'):
                self.tree_widget_split.select_item_by_path(normalized_path)
        
        import logging
        logging.getLogger(__name__).info(f"[Sync] 🔗 Граф→Дерево: {normalized_path}")
    
    def _highlight_file_in_tree(self, tree_widget, file_path: str):
        """Выделить файл в дереве по пути"""
        # Пробуем прямое совпадение
        if file_path in tree_widget.file_tree_items:
            file_item = tree_widget.file_tree_items[file_path]
        else:
            # Попытка нормализовать путь относительно project_root
            try:
                normalized = tree_widget._normalize_path(file_path, getattr(tree_widget, 'project_root', '.'))
            except Exception:
                normalized = file_path.replace('\\', '/')

            file_item = None
            if normalized in tree_widget.file_tree_items:
                file_item = tree_widget.file_tree_items[normalized]
            else:
                # Попытка подобрать по basename
                target_basename = Path(file_path).name
                for k, itm in tree_widget.file_tree_items.items():
                    if Path(k).name == target_basename or k.endswith(normalized) or normalized.endswith(k):
                        file_item = itm
                        print(f"[ErrorVisualizationWidget] ⚠️ Fallback matched tree key: {k} for {file_path}")
                        break

            if file_item is None:
                print(f"[ErrorVisualizationWidget] ⚠️ Файл не найден в дереве: {file_path} (tried normalized: {normalized})")
                return
        tree = tree_widget.tree
        
        # Выделяем элемент
        tree.setCurrentItem(file_item)
        tree.scrollToItem(file_item)
        tree.expandItem(file_item)
        
        print(f"[ErrorVisualizationWidget] ✅ Файл выделен в дереве: {file_path}")
    
    def get_current_mode(self) -> ViewMode:
        """Получить текущий режим просмотра"""
        return self.current_mode
