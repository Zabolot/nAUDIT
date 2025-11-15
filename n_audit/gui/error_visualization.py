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
from n_audit.gui.graph_visualizer import GraphVisualizerWidget


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
        self.tree_widget.populate_from_report(report, project_root)
        self.graph_widget.populate_from_report(report, project_root)
        
        # Заполняем компоненты split режима
        self.tree_widget_split.populate_from_report(report, project_root)
        self.graph_widget_split.populate_from_report(report, project_root)
    
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
    
    def get_current_mode(self) -> ViewMode:
        """Получить текущий режим просмотра"""
        return self.current_mode
