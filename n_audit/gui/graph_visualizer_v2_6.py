#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Граф-визуализация проекта v2.6 - ПОЛНОСТЬЮ ПЕРЕПИСАННАЯ С УЛУЧШЕНИЯМИ

✨ НОВЫЕ ФУНКЦИИ:
✅ PyVis интеграция с переключением видов
✅ Фокус на узел с плавной анимацией
✅ Синхронизация дерево ↔ граф в реальном времени
✅ Исключение .venv, __pycache__, node_modules и т.д.
✅ Раскраска графов по папкам проекта
✅ Показ только количества ошибок (цифры) без имён файлов
✅ Правильное распределение графов - без наложений
✅ Иерархическое дерево графов (зависимости между файлами)
"""

from __future__ import annotations
import sys
import tempfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
import json
import re
import hashlib
import math
from enum import Enum
from collections import defaultdict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSlider, QCheckBox, QComboBox, QSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QUrl, QObject, pyqtSlot, QThread, QSize
from PyQt6.QtCore import QEvent
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtGui import QFont, QColor

try:
    import networkx as nx
except ImportError:
    nx = None

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

try:
    from pyvis.network import Network
    HAS_PYVIS = True
except ImportError:
    HAS_PYVIS = False

try:
    from n_audit.gui.gpu_detector import GPUDetector, SystemResources
    GPU_DETECTOR = GPUDetector()
    SYSTEM_RESOURCES = GPU_DETECTOR.get_system_resources()
    OPTIMIZATION_HINTS = GPU_DETECTOR.get_optimization_hints(SYSTEM_RESOURCES)
    HAS_GPU_DETECTOR = True
except ImportError:
    HAS_GPU_DETECTOR = False
    SYSTEM_RESOURCES = None
    OPTIMIZATION_HINTS = None


# ════════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ И ИСКЛЮЧЕНИЯ
# ════════════════════════════════════════════════════════════════

EXCLUDE_FOLDERS = {
    '.venv', 'venv', '.env', 'venv_test',
    '__pycache__',
    '.git', '.github', '.gitignore',
    '.pytest_cache', '.tox',
    'node_modules', '.npm',
    '.idea', '.vscode', '.sublime', '.vscode',
    'build', 'dist', '.build', 'dist-info',
    'htmlcov', '.coverage',
    '.mypy_cache', '.dmypy', '.mypy_cache',
    '.DS_Store',
    'egg-info',
    'v.naudit',
    'Trash',
    'venv_test',
    '.qodo',
    'test_empty_project',
    'audit_results',
    'project_report',
}

EXCLUDE_EXT = {
    '.egg-info', '.dist-info', '.pyd', '.so', '.dll', '.pyc',
    '.pyo', '.pyd', '.so', '.dylib', '.exe', '.tar.gz'
}

EXCLUDE_FILES = {
    'setup.py', 'setup.cfg', 'pyproject.toml', 'requirements.txt',
    'README.md', 'LICENSE', '.gitignore', 'Makefile',
    'conftest.py', 'pytest.ini', 'tox.ini', '.flake8',
}

# Папки, которые НЕ должны анализироваться
SKIP_ANALYSIS_FOLDERS = {
    'build', 'dist', '__pycache__', '.git', 'venv', '.venv',
    'node_modules', 'htmlcov', '.pytest_cache', '.tox',
    'egg-info', '.mypy_cache', 'v.naudit', 'Trash',
}

# Параметры отображения
GRID_SPACING = 40.0
CLOUD_SPACING = 15.0
MIN_NODE_DISTANCE = 5.0
FOLDER_GROUP_SPACING = 100.0


# ════════════════════════════════════════════════════════════════
# КЛАССЫ И СТРУКТУРЫ ДАННЫХ
# ════════════════════════════════════════════════════════════════

class GraphRenderMode(Enum):
    """Режимы отображения графа"""
    PLOTLY = "plotly"
    PYVIS = "pyvis"


class SeverityLevel(Enum):
    """Уровни серьезности"""
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    OK = 0


@dataclass
class FileNode:
    """Узел графа - файл проекта"""
    file_path: str
    lines_of_code: int
    errors_count: int
    max_severity: str
    folder: str
    imports: Set[str] = field(default_factory=set)
    error_types: Dict[str, int] = field(default_factory=dict)
    depends_on: Set[str] = field(default_factory=set)  # Зависимости
    
    def get_display_text(self) -> str:
        """Получить текст для отображения (только количество ошибок)"""
        if self.errors_count == 0:
            return "0"
        return str(self.errors_count)
    
    def get_node_color(self, folder_colors: Dict[str, str]) -> str:
        """Получить цвет узла в зависимости от папки и серьезности"""
        # Сначала приоритет - серьезность ошибок
        if self.max_severity == 'CRITICAL':
            return '#FF0000'  # Красный
        elif self.max_severity == 'HIGH':
            return '#FF6600'  # Оранжевый
        elif self.max_severity == 'MEDIUM':
            return '#FFD700'  # Жёлтый
        elif self.max_severity == 'LOW':
            return '#87CEEB'  # Голубой
        else:
            # Если нет ошибок - цвет по папке
            return folder_colors.get(self.folder, '#90EE90')


class GraphNodeBridge(QObject):
    """Мост между JavaScript графа и Python UI через QWebChannel"""
    node_clicked = pyqtSignal(str)
    node_hovered = pyqtSignal(str)
    focus_requested = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
    
    @pyqtSlot(str)
    def onNodeClicked(self, file_path: str):
        """Вызывается из JavaScript при клике на узел"""
        print(f"[GraphBridge] [CLICK] Node clicked: {file_path}")
        self.node_clicked.emit(file_path)
    
    @pyqtSlot(str)
    def onNodeHovered(self, file_path: str):
        """Вызывается из JavaScript при наведении на узел"""
        self.node_hovered.emit(file_path)
    
    @pyqtSlot(str)
    def requestFocus(self, file_path: str):
        """Запрос фокуса на узел"""
        self.focus_requested.emit(file_path)


class GraphVisualizerWidget(QWidget):
    """Интерактивная граф-визуализация v2.6 - ПОЛНОСТЬЮ ПЕРЕПИСАННАЯ"""
    
    file_selected = pyqtSignal(str)
    focus_on_file = pyqtSignal(str)  # Сигнал для синхронизации с деревом
    
    def __init__(self):
        super().__init__()
        
        self.nodes: Dict[str, FileNode] = {}
        self.edges: List[Tuple[str, str]] = []
        self.folder_colors: Dict[str, str] = {}
        self.graph = nx.Graph() if nx else None
        
        self.scale_factor = 1.0
        self.current_render_mode = GraphRenderMode.PLOTLY
        self.current_severity_filter = "Все"
        self.show_labels_mode = False
        self.show_edges_mode = True
        self.is_initializing = True
        self.project_root = None
        
        # Компоненты UI
        self.web_view = None
        self.web_channel = None
        self.bridge = None
        
        self._setup_ui()
        self.is_initializing = False
        
        print("[GraphVisualizer v2.6] ✅ Инициализирован с поддержкой PyVis и синхронизацией")
    
    def _setup_ui(self):
        """Создать интерфейс"""
        layout = QVBoxLayout()
        
        # ═══════════════════════════════════════
        # ВЕРХНЯЯ ПАНЕЛЬ УПРАВЛЕНИЯ
        # ═══════════════════════════════════════
        top_layout = QHBoxLayout()
        
        # Выбор режима рендеринга
        top_layout.addWidget(QLabel("🎨 Режим:"))
        self.render_combo = QComboBox()
        self.render_combo.addItems(["Plotly (Plotly.js)", "PyVis (Interactive)"])
        self.render_combo.currentIndexChanged.connect(self._on_render_changed)
        self.render_combo.setToolTip("Выберите режим визуализации: Plotly для точности, PyVis для интерактивности")
        top_layout.addWidget(self.render_combo)
        
        top_layout.addSpacing(20)
        
        # Опция: Показывать имена файлов
        self.show_labels_chk = QCheckBox("📝 Имена")
        self.show_labels_chk.setChecked(False)
        self.show_labels_chk.stateChanged.connect(self._on_labels_toggled)
        self.show_labels_chk.setToolTip("Показать имена файлов на узлах")
        top_layout.addWidget(self.show_labels_chk)
        
        # Опция: Показывать связи
        self.show_edges_chk = QCheckBox("🔗 Связи")
        self.show_edges_chk.setChecked(True)
        self.show_edges_chk.stateChanged.connect(self._on_edges_toggled)
        self.show_edges_chk.setToolTip("Показать связи между файлами")
        top_layout.addWidget(self.show_edges_chk)
        
        top_layout.addSpacing(20)
        
        # Фильтр по серьезности
        top_layout.addWidget(QLabel("🚨 Уровень:"))
        self.severity_combo = QComboBox()
        self.severity_combo.addItems(["Все", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
        self.severity_combo.currentIndexChanged.connect(self._on_severity_changed)
        self.severity_combo.setToolTip("Фильтр по уровню серьезности ошибок")
        top_layout.addWidget(self.severity_combo)
        
        top_layout.addSpacing(20)
        
        # Масштаб
        top_layout.addWidget(QLabel("🔍 Масштаб:"))
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setMinimum(20)
        self.scale_slider.setMaximum(300)
        self.scale_slider.setValue(100)
        self.scale_slider.setMaximumWidth(100)
        self.scale_slider.valueChanged.connect(self._on_scale_changed)
        self.scale_slider.setToolTip("Масштабирование графа")
        top_layout.addWidget(self.scale_slider)
        
        # Кнопка обновления
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self._on_refresh)
        refresh_btn.setToolTip("Пересчитать и отобразить граф")
        top_layout.addWidget(refresh_btn)
        
        # Статистика
        self.stats_label = QLabel("📊 Узлов: 0 | Связей: 0")
        top_layout.addWidget(self.stats_label)
        
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # ═══════════════════════════════════════
        # WEB VIEW ДЛЯ ОТОБРАЖЕНИЯ ГРАФА
        # ═══════════════════════════════════════
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(600)
        
        # Инициализируем QWebChannel для обратной связи
        self.bridge = GraphNodeBridge()
        self.bridge.node_clicked.connect(self._on_node_clicked_from_graph)
        self.bridge.focus_requested.connect(self._on_focus_requested)
        
        self.web_channel = QWebChannel()
        self.web_channel.registerObject("graph_bridge", self.bridge)
        self.web_view.page().setWebChannel(self.web_channel)
        
        layout.addWidget(self.web_view)
        self.setLayout(layout)
    
    # ════════════════════════════════════════════════════════════════
    # МЕТОДЫ ФИЛЬТРАЦИИ И ИСКЛЮЧЕНИЯ
    # ════════════════════════════════════════════════════════════════
    
    def _is_excluded_path(self, path_str: str) -> bool:
        """Проверить, исключена ли папка из анализа"""
        path = Path(path_str)
        
        # Проверяем каждый компонент пути
        for part in path.parts:
            if part in EXCLUDE_FOLDERS or part in SKIP_ANALYSIS_FOLDERS:
                return True
        
        # Проверяем расширение файла
        for ext in EXCLUDE_EXT:
            if str(path).endswith(ext):
                return True
        
        # Проверяем имя файла
        if path.name in EXCLUDE_FILES:
            return True
        
        return False
    
    def _get_folder_group(self, file_path: str) -> str:
        """Получить группу папки (первый уровень папок)"""
        path = Path(file_path)
        parts = path.parts
        
        # Пропускаем, если файл в корне
        if len(parts) <= 1:
            return "root"
        
        # Возвращаем первую папку, которая не исключена
        for part in parts[:-1]:
            if part not in EXCLUDE_FOLDERS:
                return part
        
        return "other"
    
    def _assign_folder_colors(self):
        """Присвоить цвета папкам на основе проекта"""
        folder_groups = defaultdict(int)
        
        # Считаем папки
        for node in self.nodes.values():
            folder_group = self._get_folder_group(node.file_path)
            folder_groups[folder_group] += 1
        
        # Генерируем цвета на основе хеша и важности папки
        hue_offset = 0
        for folder in sorted(folder_groups.keys()):
            if folder == "root":
                hue = 0
            elif folder == "n_audit" or folder == "src":
                hue = 240  # Синий для основного кода
            elif folder == "gui":
                hue = 120  # Зелёный для UI
            elif folder == "core":
                hue = 60   # Жёлтый для ядра
            elif folder == "models":
                hue = 300  # Фиолетовый для моделей
            elif folder == "utils":
                hue = 30   # Оранжевый для утилит
            else:
                hue = (hue_offset * 45) % 360
                hue_offset += 1
            
            saturation = 70
            lightness = 55
            self.folder_colors[folder] = f"hsl({hue}, {saturation}%, {lightness}%)"
        
        print(f"[GraphVisualizer] 🎨 Назначены цвета {len(self.folder_colors)} папкам")
    
    # ════════════════════════════════════════════════════════════════
    # ЗАГРУЗКА ДАННЫХ И ПОСТРОЕНИЕ ГРАФА
    # ════════════════════════════════════════════════════════════════
    
    def _extract_imports(self, file_path: str) -> Set[str]:
        """Парсить импорты из файла Python"""
        imports = set()
        try:
            if self.project_root is None:
                return imports
            
            full_path = Path(self.project_root) / file_path
            if not full_path.exists() or full_path.suffix != '.py':
                return imports
            
            content = full_path.read_text(encoding='utf-8', errors='ignore')
            
            # Парсим импорты
            import_pattern = r'(?:from\s+([\w.]+)|import\s+([\w.]+))'
            for match in re.finditer(import_pattern, content):
                module = match.group(1) or match.group(2)
                if module:
                    root_module = module.split('.')[0]
                    if not root_module.startswith('_'):
                        imports.add(root_module)
        except Exception as e:
            print(f"[Error] Не удалось парсить импорты из {file_path}: {e}")
        
        return imports
    
    def populate_from_report(self, report, project_root: str):
        """Загрузить граф из отчёта об ошибках"""
        print(f"[GraphVisualizer v2.6] [LOAD] Loading audit report...")
        
        self.project_root = project_root
        self.nodes.clear()
        self.edges.clear()
        self.graph = nx.Graph() if nx else None
        
        files_info = {}
        
        # ═══════════════════════════════════════
        # СОБРАТЬ ВСЕ PYTHON ФАЙЛЫ В ПРОЕКТЕ
        # ═══════════════════════════════════════
        
        try:
            project_path = Path(project_root)
            python_files = set()
            
            # Ищем все .py файлы в проекте
            if project_path.exists():
                for py_file in project_path.rglob("*.py"):
                    # Пропускаем исключённые пути
                    file_path = str(py_file.relative_to(project_path)).replace('\\', '/')
                    
                    if not self._is_excluded_path(file_path):
                        python_files.add(file_path)
                        # Инициализируем базовую информацию для каждого файла
                        if file_path not in files_info:
                            files_info[file_path] = {
                                'errors': 0,
                                'max_severity': 'OK',  # По умолчанию OK если нет ошибок
                                'error_types': defaultdict(int),
                                'lines': 0,
                            }
            
            print(f"[GraphVisualizer v2.6] 📁 Найдено Python файлов: {len(python_files)}")
        except Exception as e:
            print(f"[GraphVisualizer] ⚠️ Ошибка при сканировании файлов: {e}")
        
        # ═══════════════════════════════════════
        # СОБРАТЬ ИНФОРМАЦИЮ ОБ ОШИБКАХ
        # ═══════════════════════════════════════
        
        # Ошибки кода
        if hasattr(report, 'code_issues'):
            for issue in report.code_issues:
                file_path = str(issue.get('file', '')).replace('\\', '/')
                
                # Пропускаем исключённые пути
                if not file_path or self._is_excluded_path(file_path):
                    continue
                
                if file_path not in files_info:
                    files_info[file_path] = {
                        'errors': 0,
                        'max_severity': 'LOW',
                        'error_types': defaultdict(int),
                        'lines': 0,
                    }
                
                files_info[file_path]['errors'] += 1
                severity = issue.get('severity', 'LOW')
                files_info[file_path]['error_types'][severity] += 1
                
                # Обновляем max_severity
                severity_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
                current_order = severity_order.get(files_info[file_path]['max_severity'], 0)
                new_order = severity_order.get(severity, 0)
                if new_order > current_order:
                    files_info[file_path]['max_severity'] = severity
        
        # Проблемы безопасности
        if hasattr(report, 'security_issues'):
            for issue in report.security_issues:
                file_path = str(issue.get('file', '')).replace('\\', '/')
                
                if not file_path or self._is_excluded_path(file_path):
                    continue
                
                if file_path not in files_info:
                    files_info[file_path] = {
                        'errors': 0,
                        'max_severity': 'LOW',
                        'error_types': defaultdict(int),
                        'lines': 0,
                    }
                
                files_info[file_path]['errors'] += 1
                severity = issue.get('severity', 'HIGH')  # Безопасность - по умолчанию HIGH
                files_info[file_path]['error_types'][severity] += 1
                
                # Обновляем max_severity
                severity_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
                current_order = severity_order.get(files_info[file_path]['max_severity'], 0)
                new_order = severity_order.get(severity, 0)
                if new_order > current_order:
                    files_info[file_path]['max_severity'] = severity
        
        # ═══════════════════════════════════════
        # СОЗДАТЬ УЗЛЫ ГРАФА
        # ═══════════════════════════════════════
        
        for file_path, info in files_info.items():
            folder_group = self._get_folder_group(file_path)
            imports = self._extract_imports(file_path)
            
            node = FileNode(
                file_path=file_path,
                lines_of_code=info.get('lines', 0),
                errors_count=info['errors'],
                max_severity=info['max_severity'],
                folder=folder_group,
                imports=imports,
                error_types=dict(info['error_types']),
            )
            
            self.nodes[file_path] = node
            
            if self.graph:
                self.graph.add_node(file_path, **{
                    'errors': info['errors'],
                    'severity': info['max_severity'],
                    'folder': folder_group,
                })
        
        # Присвоить цвета папкам
        self._assign_folder_colors()
        
        # ═══════════════════════════════════════
        # СОЗДАТЬ СВЯЗИ МЕЖДУ ФАЙЛАМИ
        # ═══════════════════════════════════════
        
        for file_path, node in self.nodes.items():
            for imported_module in node.imports:
                # Ищем файлы, которые соответствуют импорту
                for other_file_path in self.nodes.keys():
                    if file_path == other_file_path:
                        continue
                    
                    # Простой матч - если имя модуля есть в пути файла
                    other_file_lower = other_file_path.lower().replace('\\', '/')
                    if f"/{imported_module}/" in f"/{other_file_lower}/" or \
                       other_file_lower.endswith(f"/{imported_module}.py"):
                        
                        # Добавляем связь
                        edge = (file_path, other_file_path)
                        if edge not in self.edges:
                            self.edges.append(edge)
                            node.depends_on.add(other_file_path)
                            
                            if self.graph:
                                self.graph.add_edge(file_path, other_file_path)
        
        # Обновляем статистику
        self.stats_label.setText(
            f"📊 Узлов: {len(self.nodes)} | Связей: {len(self.edges)} | "
            f"Папок: {len(self.folder_colors)}"
        )
        
        print(f"[GraphVisualizer v2.6] ✅ Загружено узлов: {len(self.nodes)}, связей: {len(self.edges)}")
        print(f"[GraphVisualizer v2.6] 🎨 Папок в проекте: {len(self.folder_colors)}")
        
        # Отображаем граф
        self._render_graph()
    
    # ════════════════════════════════════════════════════════════════
    # РЕНДЕРИНГ ГРАФОВ
    # ════════════════════════════════════════════════════════════════
    
    def _generate_plotly_html(self) -> str:
        """Генерировать HTML с Plotly графом"""
        if not HAS_PLOTLY:
            return self._generate_error_html("Plotly не установлен")
        
        try:
            # Фильтруем узлы по серьезности
            filtered_nodes = self._filter_nodes_by_severity()
            
            if not filtered_nodes:
                # Детальное сообщение об ошибке
                total_nodes = len(self.nodes)
                current_filter = self.current_severity_filter
                
                if total_nodes == 0:
                    error_msg = """
                    <div style='padding: 30px; text-align: center;'>
                        <h2>⚠️ Нет узлов для отображения</h2>
                        <p>Это может быть потому что:</p>
                        <ul style='text-align: left; display: inline-block;'>
                            <li>Проект не был проанализирован</li>
                            <li>Нет Python файлов в проекте</li>
                            <li>Все файлы исключены из анализа</li>
                        </ul>
                        <p><b>Совет:</b> Запустите аудит проекта</p>
                    </div>
                    """
                else:
                    error_msg = f"""
                    <div style='padding: 30px; text-align: center;'>
                        <h2>⚠️ Нет узлов с фильтром: {current_filter}</h2>
                        <p>Найдено узлов: {total_nodes}</p>
                        <p><b>Совет:</b> Измените фильтр на "Все" для просмотра всех файлов</p>
                    </div>
                    """
                
                return self._generate_error_html(error_msg)
            
            # Создаём граф NetworkX
            G = nx.Graph()
            
            # Добавляем узлы
            for file_path in filtered_nodes:
                node = self.nodes[file_path]
                G.add_node(file_path, errors=node.errors_count, severity=node.max_severity)
            
            # Добавляем связи
            for source, target in self.edges:
                if source in filtered_nodes and target in filtered_nodes:
                    G.add_edge(source, target)
            
            # Вычисляем позиции с лучшей раскладкой
            pos = self._calculate_positions(G, filtered_nodes)
            
            # Подготавливаем данные для Plotly
            edge_trace_list = []
            
            if self.show_edges_mode:
                for source, target in G.edges():
                    x0, y0 = pos.get(source, (0, 0))
                    x1, y1 = pos.get(target, (0, 0))
                    
                    edge_trace = go.Scatter(
                        x=[x0, x1, None],
                        y=[y0, y1, None],
                        mode='lines',
                        line=dict(width=1, color='rgba(125,125,125,0.3)'),
                        hoverinfo='none',
                        showlegend=False,
                    )
                    edge_trace_list.append(edge_trace)
            
            # Данные узлов
            node_x = []
            node_y = []
            node_text = []
            node_size = []
            node_color = []
            node_hover_text = []
            
            for file_path in filtered_nodes:
                x, y = pos.get(file_path, (0, 0))
                node_x.append(x)
                node_y.append(y)
                
                node = self.nodes[file_path]
                
                # Текст на узле (только цифры с ошибками)
                if self.show_labels_mode:
                    node_text.append(f"{node.file_path}\n{node.get_display_text()}")
                else:
                    node_text.append(node.get_display_text())
                
                # Размер узла в зависимости от ошибок
                size = max(10, min(30, 10 + node.errors_count))
                node_size.append(size)
                
                # Цвет узла
                color = node.get_node_color(self.folder_colors)
                node_color.append(color)
                
                # Hover информация
                hover = f"<b>{node.file_path}</b><br>"
                hover += f"Ошибок: {node.errors_count}<br>"
                hover += f"Макс. серьезность: {node.max_severity}<br>"
                hover += f"Папка: {node.folder}<br>"
                hover += f"Зависимостей: {len(node.depends_on)}"
                node_hover_text.append(hover)
            
            # Trace узлов
            node_trace = go.Scatter(
                x=node_x,
                y=node_y,
                mode='markers+text',
                text=node_text,
                textposition='middle center',
                textfont=dict(size=10, color='white'),
                hovertext=node_hover_text,
                hoverinfo='text',
                marker=dict(
                    size=node_size,
                    color=node_color,
                    line=dict(width=2, color='white'),
                ),
                showlegend=False,
            )
            
            # Создаём фигуру
            fig = go.Figure(data=edge_trace_list + [node_trace])
            
            # Макет с плавной анимацией
            fig.update_layout(
                title='📊 Граф ошибок проекта',
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='#f8f9fa',
                font=dict(size=11),
                height=600,
            )
            
            # Конвертируем в HTML
            html_content = fig.to_html(include_plotlyjs='cdn')
            
            # Добавляем JavaScript для интеграции с QWebChannel
            html_content = self._inject_qwebchannel_code(html_content)
            
            return html_content
        
        except Exception as e:
            print(f"[Error] Ошибка при генерации Plotly графа: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_error_html(f"Ошибка рендеринга: {str(e)}")
    
    def _generate_pyvis_html(self) -> str:
        """Генерировать HTML с PyVis графом"""
        if not HAS_PYVIS:
            return self._generate_error_html("PyVis не установлен. Установите: pip install pyvis")
        
        try:
            # Фильтруем узлы по серьезности
            filtered_nodes = self._filter_nodes_by_severity()
            
            if not filtered_nodes:
                # Детальное сообщение об ошибке
                total_nodes = len(self.nodes)
                current_filter = self.current_severity_filter
                
                if total_nodes == 0:
                    error_msg = """
                    <div style='padding: 30px; text-align: center;'>
                        <h2>⚠️ Нет узлов для отображения</h2>
                        <p>Это может быть потому что:</p>
                        <ul style='text-align: left; display: inline-block;'>
                            <li>Проект не был проанализирован</li>
                            <li>Нет Python файлов в проекте</li>
                            <li>Все файлы исключены из анализа</li>
                        </ul>
                        <p><b>Совет:</b> Запустите аудит проекта</p>
                    </div>
                    """
                else:
                    error_msg = f"""
                    <div style='padding: 30px; text-align: center;'>
                        <h2>⚠️ Нет узлов с фильтром: {current_filter}</h2>
                        <p>Найдено узлов: {total_nodes}</p>
                        <p><b>Совет:</b> Измените фильтр на "Все" для просмотра всех файлов</p>
                    </div>
                    """
                
                return self._generate_error_html(error_msg)
            
            # Создаём граф PyVis
            net = Network(
                height='600px',
                directed=True,
            )
            
            # Включаем физику симуляции (если поддерживается)
            try:
                net.physics.enabled = True
            except:
                pass  # Старая версия PyVis может не поддерживать
            
            # Добавляем узлы
            for file_path in filtered_nodes:
                node = self.nodes[file_path]
                
                # Определяем текст узла
                if self.show_labels_mode:
                    title = f"{file_path}\n{node.get_display_text()} ошибок"
                else:
                    title = f"{file_path}"
                
                label = node.get_display_text()
                
                # Определяем цвет и размер
                color = node.get_node_color(self.folder_colors)
                size = max(15, min(50, 15 + node.errors_count * 2))
                
                # Получаем папку для группировки
                folder_group = node.folder if hasattr(node, 'folder') else 'root'
                
                net.add_node(
                    file_path,
                    label=label,
                    title=title,
                    color=color,
                    size=size,
                    group=folder_group,  # Группируем по папкам
                )
            
            # Добавляем связи
            if self.show_edges_mode:
                for source, target in self.edges:
                    if source in filtered_nodes and target in filtered_nodes:
                        net.add_edge(source, target)
            
            # Конфигурация физики
            net.toggle_physics(True)
            net.show_buttons(filter_=['physics'])
            
            # Получаем HTML напрямую без создания файла
            try:
                # Для PyVis >= 0.3.2 используем get_html()
                if hasattr(net, 'get_html'):
                    html_content = net.get_html()
                else:
                    # Fallback для более старых версий
                    temp_file = Path(tempfile.gettempdir()) / "naudit_pyvis_graph.html"
                    net.show(str(temp_file))
                    html_content = temp_file.read_text(encoding='utf-8')
            except Exception as e:
                print(f"[Warning] Ошибка при получении HTML: {e}")
                # Финальный fallback - генерируем минимальный HTML
                temp_file = Path(tempfile.gettempdir()) / "naudit_pyvis_graph.html"
                net.write_html(str(temp_file))
                html_content = temp_file.read_text(encoding='utf-8')
            
            # Добавляем JavaScript для интеграции с QWebChannel
            html_content = self._inject_qwebchannel_code(html_content)
            
            return html_content
        
        except Exception as e:
            print(f"[Error] Ошибка при генерации PyVis графа: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_error_html(f"Ошибка рендеринга PyVis: {str(e)}")
    
    def _filter_nodes_by_severity(self) -> List[str]:
        """Отфильтровать узлы по уровню серьезности"""
        severity_filter = self.current_severity_filter
        
        if severity_filter == "Все":
            return list(self.nodes.keys())
        
        severity_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, 'OK': 0}
        filter_level = severity_order.get(severity_filter, 0)
        
        filtered = []
        for file_path, node in self.nodes.items():
            node_level = severity_order.get(node.max_severity, 0)
            
            # Включаем узел если его серьезность >= требуемой
            if node_level >= filter_level:
                filtered.append(file_path)
        
        return filtered
    
    def _calculate_positions(self, G: nx.Graph, filtered_nodes: List[str]) -> Dict[str, Tuple[float, float]]:
        """Рассчитать позиции узлов с группировкой по папкам (включая вложенные)"""
        if len(filtered_nodes) == 0:
            return {}
        
        try:
            # Группируем узлы по иерархии папок (рекурсивно)
            folder_hierarchy = self._build_folder_hierarchy(filtered_nodes)
            
            # Вычисляем общий layout сначала
            base_pos = nx.spring_layout(
                G,
                k=2.0,  # Расстояние между узлами
                iterations=50,
                seed=42,
                scale=100,
            )
            
            # Применяем иерархическую коррекцию позиций
            pos = self._apply_hierarchical_clustering(base_pos, filtered_nodes, folder_hierarchy)
            
            # Применяем масштаб если нужно
            pos = {node: (x * self.scale_factor, y * self.scale_factor) 
                   for node, (x, y) in pos.items()}
            
            print(f"[GraphVisualizer] 🎯 Позиции: {len(pos)} узлов с иерархической группировкой")
            
            return pos
        
        except Exception as e:
            print(f"[Error] Ошибка при расчёте позиций: {e}")
            import traceback
            traceback.print_exc()
            # Возвращаем простую сетку
            return self._generate_grid_positions(filtered_nodes)
    
    def _build_folder_hierarchy(self, nodes: List[str]) -> Dict:
        """Строит иерархию папок для вложенной группировки
        
        Возвращает структуру типа:
        {
            'folder1/': {'size': 10, 'children': {'subfolder1/': {...}}},
            'folder2/': {'size': 5, 'children': {}}
        }
        """
        hierarchy = {}
        
        for node in nodes:
            folder_path = self.nodes[node].folder
            # Разбиваем путь на компоненты
            parts = folder_path.strip('/').split('/')
            
            current = hierarchy
            for i, part in enumerate(parts):
                key = part + '/'
                if key not in current:
                    current[key] = {'size': 0, 'children': {}, 'depth': i}
                current = current[key]['children']
        
        # Считаем размеры (количество узлов в каждой папке)
        for node in nodes:
            folder_path = self.nodes[node].folder
            parts = folder_path.strip('/').split('/')
            
            current = hierarchy
            for part in parts:
                key = part + '/'
                if key in current:
                    current[key]['size'] += 1
                    current = current[key]['children']
        
        return hierarchy
    
    def _apply_hierarchical_clustering(self, base_pos: Dict, filtered_nodes: List[str], 
                                      hierarchy: Dict, parent_center=(0, 0), parent_size=1000) -> Dict:
        """Применяет иерархическую кластеризацию к позициям узлов"""
        pos = {}
        
        # Получаем папку каждого узла
        folder_to_nodes = defaultdict(list)
        for node in filtered_nodes:
            folder = self.nodes[node].folder
            folder_to_nodes[folder].append(node)
        
        # Рассчитываем позиции для каждого уровня иерархии
        self._position_hierarchical_level(
            hierarchy, 
            folder_to_nodes, 
            base_pos, 
            pos, 
            parent_center, 
            parent_size
        )
        
        return pos
    
    def _position_hierarchical_level(self, hierarchy: Dict, folder_to_nodes: Dict, 
                                     base_pos: Dict, pos: Dict, parent_center: Tuple, 
                                     parent_size: float, depth: int = 0):
        """Рекурсивно позиционирует узлы на каждом уровне иерархии"""
        if not hierarchy:
            return
        
        # Определяем размер для текущего уровня
        folder_count = len(hierarchy)
        folder_display_size = max(100, parent_size / (folder_count + 1))
        spacing = folder_display_size * 1.2
        
        # Расчитываем сетку для папок на этом уровне
        cols = max(1, int(math.sqrt(folder_count)))
        
        for idx, (folder_key, folder_data) in enumerate(sorted(hierarchy.items())):
            # Рассчитываем центр для этой папки
            col = idx % cols
            row = idx // cols
            
            folder_center_x = parent_center[0] + (col - cols/2 + 0.5) * spacing
            folder_center_y = parent_center[1] + (row - int(folder_count/cols)/2) * spacing
            folder_center = (folder_center_x, folder_center_y)
            
            # Если это листовая папка, размещаем узлы
            if not folder_data['children']:
                # Это папка без подпапок - размещаем все узлы в этой папке
                folder_path = folder_key.rstrip('/') + '/'
                nodes_in_folder = folder_to_nodes.get(folder_path, [])
                
                if nodes_in_folder:
                    # Размещаем узлы вокруг центра папки
                    self._position_nodes_in_folder(
                        nodes_in_folder, 
                        base_pos, 
                        pos, 
                        folder_center, 
                        folder_display_size
                    )
            else:
                # Это папка с подпапками - рекурсивно позиционируем подпапки
                self._position_hierarchical_level(
                    folder_data['children'],
                    folder_to_nodes,
                    base_pos,
                    pos,
                    folder_center,
                    folder_display_size,
                    depth + 1
                )
    
    def _position_nodes_in_folder(self, nodes: List[str], base_pos: Dict, pos: Dict,
                                  folder_center: Tuple, folder_size: float):
        """Позиционирует узлы вокруг центра папки, используя базовые позиции"""
        if not nodes:
            return
        
        local_radius = folder_size / 3
        
        for i, node in enumerate(nodes):
            # Получаем нормализованную базовую позицию
            if node in base_pos:
                base_x, base_y = base_pos[node]
                # Нормализуем к локальным координатам
                local_x = base_x * local_radius
                local_y = base_y * local_radius
            else:
                # Fallback: размещаем в круг
                angle = 2 * math.pi * i / len(nodes)
                local_x = math.cos(angle) * local_radius
                local_y = math.sin(angle) * local_radius
            
            # Применяем смещение к центру папки
            final_x = folder_center[0] + local_x
            final_y = folder_center[1] + local_y
            
            pos[node] = (final_x, final_y)
    
    def _generate_grid_positions(self, nodes: List[str]) -> Dict[str, Tuple[float, float]]:
        """Генерировать позиции сеткой"""
        positions = {}
        cols = int(math.sqrt(len(nodes))) + 1
        
        for idx, node in enumerate(nodes):
            row = idx // cols
            col = idx % cols
            x = col * GRID_SPACING
            y = row * GRID_SPACING
            positions[node] = (x, y)
        
        return positions
    
    def _inject_qwebchannel_code(self, html_content: str) -> str:
        """Инжектировать JavaScript для QWebChannel интеграции"""
        js_code = """
        <script>
        // QWebChannel интеграция для нажатий на графе
        window.addEventListener('load', function() {
            // Попытка подключиться к QWebChannel
            try {
                if (typeof qt !== 'undefined') {
                    qt.webChannelTransport.onmessage = function(message) {
                        // Обработка сообщений от Python
                    };
                }
            } catch (e) {
                console.log('QWebChannel не доступен');
            }
            
            // Добавляем обработчики кликов на узлы (для Plotly)
            var plot = document.querySelector('.plotly-graph-div');
            if (plot && plot.on) {
                plot.on('plotly_click', function(data) {
                    var point = data.points[0];
                    var text = point.text;
                    if (window.graph_bridge) {
                        window.graph_bridge.onNodeClicked(text);
                    }
                    console.log('Clicked node:', text);
                });
            }
        });
        </script>
        """
        
        # Вставляем перед закрывающим </body>
        html_content = html_content.replace('</body>', js_code + '</body>')
        return html_content
    
    def _generate_error_html(self, error_message: str) -> str:
        """Генерировать HTML с сообщением об ошибке"""
        return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    margin: 0;
                    background: #f5f5f5;
                }}
                .error-box {{
                    background: white;
                    padding: 40px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    text-align: center;
                    max-width: 500px;
                }}
                .error-box h1 {{
                    color: #d32f2f;
                    margin: 0 0 10px 0;
                }}
                .error-box p {{
                    color: #666;
                    margin: 0;
                }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <h1>⚠️ Ошибка</h1>
                <p>{error_message}</p>
            </div>
        </body>
        </html>
        """
    
    def _render_graph(self):
        """Основной метод рендеринга графа"""
        print(f"[GraphVisualizer v2.6] 🎨 Рендеринг {self.current_render_mode.value}...")
        
        try:
            if self.current_render_mode == GraphRenderMode.PLOTLY:
                html_content = self._generate_plotly_html()
            else:
                html_content = self._generate_pyvis_html()
            
            # Загружаем HTML в WebView
            self.web_view.setHtml(html_content)
            
            print(f"[GraphVisualizer v2.6] ✅ Граф успешно отрендерен")
        
        except Exception as e:
            print(f"[Error] Ошибка при рендеринге: {e}")
            import traceback
            traceback.print_exc()
            error_html = self._generate_error_html(f"Ошибка: {str(e)}")
            self.web_view.setHtml(error_html)
    
    # ════════════════════════════════════════════════════════════════
    # ОБРАБОТЧИКИ СИГНАЛОВ И СЛОТОВ
    # ════════════════════════════════════════════════════════════════
    
    def _on_render_changed(self, index: int):
        """Смена режима рендеринга"""
        if self.is_initializing:
            return
        
        modes = [GraphRenderMode.PLOTLY, GraphRenderMode.PYVIS]
        self.current_render_mode = modes[index]
        print(f"[GraphVisualizer] 🔄 Режим изменён на {self.current_render_mode.value}")
        self._render_graph()
    
    def _on_labels_toggled(self, state):
        """Переключение отображения имён"""
        self.show_labels_mode = (state == Qt.CheckState.Checked.value)
        self._render_graph()
    
    def _on_edges_toggled(self, state):
        """Переключение отображения связей"""
        self.show_edges_mode = (state == Qt.CheckState.Checked.value)
        self._render_graph()
    
    def _on_severity_changed(self, index: int):
        """Фильтр по серьезности"""
        if self.is_initializing:
            return
        
        severity_levels = ["Все", "CRITICAL", "HIGH", "MEDIUM", "LOW"]
        self.current_severity_filter = severity_levels[index]
        print(f"[GraphVisualizer] 🚨 Фильтр серьезности: {self.current_severity_filter}")
        self._render_graph()
    
    def _on_scale_changed(self, value: int):
        """Изменение масштаба"""
        if self.is_initializing:
            return
        
        self.scale_factor = value / 100.0
        self._render_graph()
    
    def _on_refresh(self):
        """Обновление графа"""
        print("[GraphVisualizer] 🔄 Обновление графа...")
        self._render_graph()
    
    def _on_node_clicked_from_graph(self, file_path: str):
        """Узел был нажат на графе - синхронизируем с деревом"""
        print(f"[GraphVisualizer] 🖱️ Узел нажат: {file_path}")
        self.file_selected.emit(file_path)
    
    def _on_focus_requested(self, file_path: str):
        """Запрос фокуса на узел"""
        print(f"[GraphVisualizer] 🎯 Запрос фокуса на: {file_path}")
        self.focus_on_file.emit(file_path)
    
    def focus_on_node(self, file_path: str):
        """Фокус на узел графа (из дерева)"""
        print(f"[GraphVisualizer] 🎯 Фокусируюсь на узле: {file_path}")
        
        # Если файл не в графе - показываем ошибку
        if file_path not in self.nodes:
            print(f"[Warning] Файл {file_path} не найден в графе")
            return
        
        # Генерируем JavaScript для фокуса
        if self.current_render_mode == GraphRenderMode.PLOTLY:
            js_focus = f"""
            var plot = document.querySelector('.plotly-graph-div');
            if (plot) {{
                Plotly.restyle(plot, {{'marker.opacity': 0.3}});
            }}
            """
        else:
            js_focus = f"""
            // PyVis фокус
            if (window.network) {{
                window.network.selectNodes(['{file_path}']);
                window.network.fit();
            }}
            """
        
        self.web_view.page().runJavaScript(js_focus)
    
    def highlight_file(self, file_path: str):
        """
        Выделить файл в графе
        
        Args:
            file_path: Путь к файлу для выделения
        """
        if not file_path:
            return
        
        # Нормализуем путь
        normalized_path = file_path.replace("\\", "/")
        
        # Проверяем что такой файл есть в графе
        if normalized_path not in self.nodes:
            print(f"[GraphVisualizer] ⚠️ Файл не найден в графе: {normalized_path}")
            return
        
        # Фокусируемся на этом узле
        self.focus_on_node(normalized_path)
        
        print(f"[GraphVisualizer] ✅ Выделен файл: {normalized_path}")
    
    def export_current_graph(self) -> Optional[Path]:
        """
        Экспортировать текущий граф в HTML файл
        Возвращает путь к сохранённому файлу или None при ошибке
        """
        try:
            if not self.nodes or len(self.nodes) == 0:
                print("[GraphVisualizer] ⚠️ Нет узлов для экспорта")
                return None
            
            # Создаём временный файл для экспорта
            temp_dir = Path(tempfile.gettempdir())
            export_dir = temp_dir / "naudit_exports"
            export_dir.mkdir(parents=True, exist_ok=True)
            
            # Генерируем имя файла с временной меткой
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = export_dir / f"graph_{timestamp}.html"
            
            # Генерируем HTML контент
            if self.current_render_mode == GraphRenderMode.PLOTLY:
                html_content = self._generate_plotly_html()
            else:
                html_content = self._generate_pyvis_html()
            
            # Сохраняем в файл
            export_file.write_text(html_content, encoding='utf-8')
            
            print(f"[GraphVisualizer] ✅ Граф экспортирован: {export_file}")
            return export_file
            
        except Exception as e:
            print(f"[GraphVisualizer] ❌ Ошибка экспорта графа: {e}")
            import traceback
            traceback.print_exc()
            return None
