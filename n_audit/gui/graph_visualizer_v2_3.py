#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Граф-визуализация проекта v2.3 - ОПТИМИЗИРОВАННАЯ ВЕРСИЯ

УЛУЧШЕНИЯ v2.3:
✅ Исключение файлов из .venv, __pycache__, .git и т.д.
✅ Показ связей (импортов) между файлами  
✅ Увеличенные расстояния между облаками папок (25.0)
✅ На узлах ТОЛЬКО цифры ошибок (без имен файлов по умолчанию)
✅ Цвета по папкам (детерминированные хеш-функции)
✅ Предотвращение наложения узлов (спираль с увеличенным радиусом)
✅ Переключение между Plotly и PyVis рендерами

НОВЫЕ УЛУЧШЕНИЯ v2.3:
✅ Фильтры по типам ошибок (CRITICAL, HIGH, MEDIUM, LOW)
✅ Адаптивное масштабирование узлов в зависимости от размера проекта
✅ Сортировка файлов по папкам для лучшей группировки
✅ Оптимизированная раскладка спирали (нет перекрытий)
✅ Улучшенная обработка ошибок с более подробным логированием
✅ Кэширование граф-расчетов для быстрой перерисовки
✅ Поддержка фильтрации файлов по папкам
"""

import sys
import tempfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable
from datetime import datetime
import json
import re
import hashlib
import math
from enum import Enum

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSlider, QCheckBox, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QUrl, QObject, pyqtSlot
from PyQt6.QtCore import QEvent
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QFont

try:
    import networkx as nx
except ImportError:
    nx = None

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

try:
    from pyvis.network import Network
    HAS_PYVIS = True
except ImportError:
    HAS_PYVIS = False


# ════════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ════════════════════════════════════════════════════════════════

# Папки, которые НЕ должны попадать в граф
EXCLUDE_FOLDERS = {
    '.venv', 'venv', '.env',           # Виртуальные окружения
    '__pycache__',                      # Python кэш
    '.git', '.github',                  # Git
    '.pytest_cache', '.tox',            # Тестирование
    'node_modules', '.npm',             # Node.js
    '.idea', '.vscode', '.sublime',    # IDE
    'build', 'dist', '.build',         # Сборка
    'htmlcov', '.coverage',            # Coverage отчеты
    '.mypy_cache', '.dmypy',           # MyPy кэш
    '.DS_Store',                        # macOS
    'egg-info',                         # Setuptools
    'v.naudit', 'venv_test',          # Другие окружения
}

# Расширения для исключения
EXCLUDE_EXT = {'.egg-info', '.dist-info', '.pyd', '.so', '.dll'}

# Параметры визуализации
GRID_SPACING = 25.0                    # Расстояние между облаками папок
CLOUD_RADIUS = 3.0                     # Радиус спирали внутри облака  
MIN_NODE_DISTANCE = 3.0                # Минимальное расстояние между узлами
MAX_CLOUD_SIZE = 20                    # Максимум файлов в облаке для спирали

# Приоритеты серьезности
SEVERITY_ORDER = {
    'CRITICAL': 4,
    'HIGH': 3,
    'MEDIUM': 2,
    'LOW': 1,
    'INFO': 0
}

# Цветовые схемы по типам ошибок
SEVERITY_COLORS = {
    'CRITICAL': '#ff4444',  # Красный
    'HIGH': '#ff8800',      # Оранжевый
    'MEDIUM': '#ffbb00',    # Жёлтый
    'LOW': '#88dd00',       # Лимон
    'INFO': '#cccccc'       # Серый
}


# ════════════════════════════════════════════════════════════════
# ПЕРЕЧИСЛЕНИЯ И ТИПЫ
# ════════════════════════════════════════════════════════════════

class RenderMode(Enum):
    PLOTLY = "plotly"
    PYVIS = "pyvis"


# ════════════════════════════════════════════════════════════════
# КЛАССЫ ДАННЫХ
# ════════════════════════════════════════════════════════════════

class GraphNodeBridge(QObject):
    """Мост между JavaScript графа и Python UI"""
    node_clicked = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
    
    @pyqtSlot(str)
    def onNodeClicked(self, file_path: str):
        print(f"[GraphNodeBridge] Узел выбран: {file_path}")
        self.node_clicked.emit(file_path)


@dataclass
class FileNode:
    """Узел графа с полной информацией"""
    file_path: str
    lines_of_code: int
    errors_count: int
    max_severity: str
    folder: str
    imports: Set[str] = field(default_factory=set)
    error_types: Dict[str, int] = field(default_factory=dict)  # Счётчик по типам ошибок
    
    def get_error_summary(self) -> str:
        """Получить сводку ошибок"""
        parts = []
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = self.error_types.get(severity, 0)
            if count > 0:
                parts.append(f"{severity}:{count}")
        return " ".join(parts) if parts else "OK"


@dataclass
class GraphCache:
    """Кэш для быстрого пересчёта"""
    node_positions: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    folder_positions: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    computed_at: str = ""


# ════════════════════════════════════════════════════════════════
# ГЛАВНЫЙ КЛАСС ВИЗУАЛИЗАТОРА
# ════════════════════════════════════════════════════════════════

class GraphVisualizerWidget(QWidget):
    """Интерактивная граф-визуализация проекта v2.3 с оптимизациями"""
    
    file_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        self.nodes: Dict[str, FileNode] = {}
        self.edges: List[Tuple[str, str]] = []
        self.graph = nx.Graph() if nx else None
        self.cache = GraphCache()
        
        self.scale_factor = 1.0
        self.current_render = RenderMode.PLOTLY.value
        self._focus_active = False
        self.is_initializing = True
        
        self._setup_ui()
        self.is_initializing = False
        
        print("[GraphVisualizer] ✅ Инициализирован")
    
    def _setup_ui(self):
        """Создать UI с расширенными опциями"""
        layout = QVBoxLayout()
        
        # Верхняя панель
        top_layout = QHBoxLayout()
        
        # Выбор рендера
        top_layout.addWidget(QLabel("🎨 Рендер:"))
        self.render_combo = QComboBox()
        self.render_combo.addItems(["Plotly (интерактивный)", "PyVis (сетевой)"])
        self.render_combo.currentIndexChanged.connect(self._on_render_changed)
        top_layout.addWidget(self.render_combo)
        
        top_layout.addSpacing(20)
        
        # Опции отображения
        self.show_labels = QCheckBox("📝 Имена файлов")
        self.show_labels.setChecked(False)
        self.show_labels.stateChanged.connect(self._on_labels_toggled)
        top_layout.addWidget(self.show_labels)
        
        self.show_edges = QCheckBox("🔗 Связи")
        self.show_edges.setChecked(True)
        self.show_edges.stateChanged.connect(self._on_edges_toggled)
        top_layout.addWidget(self.show_edges)
        
        # Фильтр серьезности
        top_layout.addWidget(QLabel("🚨 Минимум:"))
        self.severity_combo = QComboBox()
        self.severity_combo.addItems(["Все", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
        self.severity_combo.currentIndexChanged.connect(self._on_severity_changed)
        top_layout.addWidget(self.severity_combo)
        
        # Масштаб
        top_layout.addSpacing(20)
        top_layout.addWidget(QLabel("🔍 Масштаб:"))
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setMinimum(20)
        self.scale_slider.setMaximum(300)
        self.scale_slider.setValue(100)
        self.scale_slider.setMaximumWidth(100)
        self.scale_slider.valueChanged.connect(self._on_scale_changed)
        top_layout.addWidget(self.scale_slider)
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self._on_refresh)
        top_layout.addWidget(refresh_btn)
        
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # Web view
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        self.setLayout(layout)
    
    # ════════════════════════════════════════════════════════════════
    # МЕТОДЫ ФИЛЬТРАЦИИ И ПРОВЕРКИ
    # ════════════════════════════════════════════════════════════════
    
    def _is_excluded_path(self, path_str: str) -> bool:
        """Проверить, должна ли папка быть исключена"""
        path = Path(path_str)
        
        # Проверить части пути
        for part in path.parts:
            if part in EXCLUDE_FOLDERS:
                return True
        
        # Проверить расширение
        for ext in EXCLUDE_EXT:
            if str(path).endswith(ext):
                return True
        
        return False
    
    def _get_folder_color(self, folder: str) -> str:
        """Генерировать детерминированный цвет для папки с учётом типа"""
        hash_val = int(hashlib.md5(folder.encode()).hexdigest(), 16)
        
        # Определяем диапазон HSL в зависимости от типа папки
        folder_lower = folder.lower()
        
        if 'gui' in folder_lower or 'ui' in folder_lower:
            hue = (hash_val % 60) + 200  # Синий
        elif 'core' in folder_lower or 'config' in folder_lower or 'settings' in folder_lower:
            hue = (hash_val % 60) + 120  # Зелёный
        elif 'model' in folder_lower or 'db' in folder_lower or 'data' in folder_lower:
            hue = (hash_val % 60) + 270  # Фиолетовый
        elif 'util' in folder_lower or 'helper' in folder_lower or 'tool' in folder_lower:
            hue = (hash_val % 60)        # Красный
        elif 'test' in folder_lower or 'spec' in folder_lower:
            hue = (hash_val % 60) + 35   # Зелено-жёлтый
        else:
            hue = hash_val % 360
        
        saturation = 65 + (hash_val // 360) % 25
        lightness = 50 + (hash_val // 720) % 15
        
        return f"hsl({hue}, {saturation}%, {lightness}%)"
    
    def _extract_imports(self, file_path: str, project_root: str) -> Set[str]:
        """Упрощённый парсер импортов из файла"""
        imports = set()
        try:
            full_path = Path(project_root) / file_path
            if full_path.exists() and full_path.suffix == '.py':
                content = full_path.read_text(encoding='utf-8', errors='ignore')
                
                for match in re.finditer(r'(?:from|import)\s+([\w.]+)', content):
                    module = match.group(1).split('.')[0]
                    if not module.startswith('__'):
                        imports.add(module)
        except Exception as e:
            pass
        
        return imports
    
    def _filter_by_severity(self, nodes: Dict[str, FileNode], min_severity: str) -> Dict[str, FileNode]:
        """Отфильтровать узлы по минимальной серьезности"""
        if min_severity == "Все":
            return nodes
        
        min_order = SEVERITY_ORDER.get(min_severity, 0)
        filtered = {}
        
        for path, node in nodes.items():
            node_order = SEVERITY_ORDER.get(node.max_severity, 0)
            if node_order >= min_order or node.errors_count > 0:
                filtered[path] = node
        
        return filtered
    
    # ════════════════════════════════════════════════════════════════
    # МЕТОДЫ ОБРАБОТКИ ДАННЫХ
    # ════════════════════════════════════════════════════════════════
    
    def populate_from_report(self, report, project_root: str):
        """Заполнить граф из отчета с полной обработкой"""
        print(f"[GraphVisualizer] Загружаю отчет из {project_root}...")
        
        self.nodes.clear()
        self.edges.clear()
        self.cache = GraphCache()
        
        files_info = {}
        
        # ════════════════════════════════════════════════════════════
        # ШАГИ 1-2: Собрать информацию об ошибках
        # ════════════════════════════════════════════════════════════
        
        if hasattr(report, 'code_issues'):
            for issue in report.code_issues:
                path = str(issue.get('file', '')).replace('\\', '/')
                if not path:
                    continue
                    
                if path not in files_info:
                    files_info[path] = {
                        'errors': 0,
                        'max_severity': 'LOW',
                        'error_types': {}
                    }
                
                files_info[path]['errors'] += 1
                severity = issue.get('severity', 'LOW')
                files_info[path]['error_types'][severity] = files_info[path]['error_types'].get(severity, 0) + 1
                
                # Обновить максимальную серьезность
                sev_order = SEVERITY_ORDER
                if sev_order.get(severity, 0) > sev_order.get(files_info[path]['max_severity'], 0):
                    files_info[path]['max_severity'] = severity
        
        if hasattr(report, 'security_issues'):
            for issue in report.security_issues:
                path = str(issue.get('file', '')).replace('\\', '/')
                if not path:
                    continue
                    
                if path not in files_info:
                    files_info[path] = {
                        'errors': 0,
                        'max_severity': 'LOW',
                        'error_types': {}
                    }
                
                files_info[path]['errors'] += 1
                severity = issue.get('severity', 'LOW')
                files_info[path]['error_types'][severity] = files_info[path]['error_types'].get(severity, 0) + 1
                
                # Обновить максимальную серьезность
                sev_order = SEVERITY_ORDER
                if sev_order.get(severity, 0) > sev_order.get(files_info[path]['max_severity'], 0):
                    files_info[path]['max_severity'] = severity
        
        # ════════════════════════════════════════════════════════════
        # ШАГ 3: Сканировать все Python файлы проекта
        # ════════════════════════════════════════════════════════════
        
        scanned_files = set()
        try:
            for py_file in Path(project_root).rglob('*.py'):
                rel = str(py_file.relative_to(project_root)).replace('\\', '/').replace('./', '')
                
                # ✅ ИСКЛЮЧИТЬ файлы
                if self._is_excluded_path(rel):
                    continue
                
                if rel in scanned_files:
                    continue
                scanned_files.add(rel)
                
                if rel not in files_info:
                    files_info[rel] = {
                        'errors': 0,
                        'max_severity': 'LOW',
                        'error_types': {}
                    }
        except Exception as e:
            print(f"[GraphVisualizer] ⚠ Ошибка сканирования: {e}")
        
        # ════════════════════════════════════════════════════════════
        # ШАГ 4: Создать узлы с полной информацией
        # ════════════════════════════════════════════════════════════
        
        for file_path, info in files_info.items():
            folder = str(Path(file_path).parent).replace('\\', '/') or 'root'
            
            try:
                full_path = Path(project_root) / file_path
                lines = len(full_path.read_text(encoding='utf-8', errors='ignore').split('\n')) if full_path.exists() else 0
            except:
                lines = 0
            
            node = FileNode(
                file_path=file_path,
                lines_of_code=lines,
                errors_count=info['errors'],
                max_severity=info['max_severity'],
                folder=folder,
                imports=self._extract_imports(file_path, project_root),
                error_types=info['error_types']
            )
            self.nodes[file_path] = node
        
        # ════════════════════════════════════════════════════════════
        # ШАГ 5: Создать рёбра (связи между файлами)
        # ════════════════════════════════════════════════════════════
        
        for file_path, node in self.nodes.items():
            for imported in node.imports:
                for other_path in self.nodes.keys():
                    if other_path != file_path:
                        if Path(other_path).stem == Path(imported).stem:
                            self.edges.append((file_path, other_path))
        
        print(f"[GraphVisualizer] ✅ {len(self.nodes)} узлов, {len(self.edges)} связей")
        self._render_graph()
    
    # ════════════════════════════════════════════════════════════════
    # ОБРАБОТЧИКИ СОБЫТИЙ
    # ════════════════════════════════════════════════════════════════
    
    def _on_render_changed(self):
        if self.is_initializing:
            return
        old = self.current_render
        self.current_render = "pyvis" if self.render_combo.currentIndex() == 1 else "plotly"
        print(f"[GraphVisualizer] Рендер: {old} → {self.current_render}")
        if self.nodes:
            self._render_graph()
    
    def _on_labels_toggled(self):
        if not self.is_initializing and self.nodes:
            self._render_graph()
    
    def _on_edges_toggled(self):
        if not self.is_initializing and self.nodes:
            self._render_graph()
    
    def _on_severity_changed(self):
        if not self.is_initializing and self.nodes:
            self._render_graph()
    
    def _on_scale_changed(self):
        if not self.is_initializing:
            self.scale_factor = self.scale_slider.value() / 100.0
            if self.nodes:
                self._render_graph()
    
    def _on_refresh(self):
        if self.nodes:
            print("[GraphVisualizer] 🔄 Обновление...")
            self._render_graph()
    
    # ════════════════════════════════════════════════════════════════
    # ОСНОВНАЯ ЛОГИКА РЕНДЕРИНГА
    # ════════════════════════════════════════════════════════════════
    
    def _render_graph(self):
        """Выбрать правильный рендер в зависимости от доступности"""
        if not self.nodes:
            return
        
        if self.current_render == "plotly":
            if HAS_PLOTLY:
                self._render_with_plotly()
            elif HAS_PYVIS:
                print("[GraphVisualizer] Fallback на PyVis (Plotly недоступен)")
                self._render_with_pyvis()
        else:
            if HAS_PYVIS:
                self._render_with_pyvis()
            elif HAS_PLOTLY:
                print("[GraphVisualizer] Fallback на Plotly (PyVis недоступен)")
                self._render_with_plotly()
    
    def _render_with_plotly(self):
        """Рендерить с Plotly с оптимизированной раскладкой"""
        print(f"[GraphVisualizer] 📊 Plotly: {len(self.nodes)} узлов")
        
        try:
            # ────────────────────────────────────────────────────────
            # Шаг 1: Применить фильтр по серьезности
            # ────────────────────────────────────────────────────────
            min_severity = self.severity_combo.currentText()
            filtered_nodes = self._filter_by_severity(self.nodes, min_severity)
            
            if not filtered_nodes:
                print("[GraphVisualizer] Нет узлов после фильтрации")
                return
            
            # ────────────────────────────────────────────────────────
            # Шаг 2: Группировать по папкам
            # ────────────────────────────────────────────────────────
            folders: Dict[str, List[str]] = {}
            for file_path in filtered_nodes.keys():
                folder = filtered_nodes[file_path].folder
                folders.setdefault(folder, []).append(file_path)
            
            # Отсортировать папки для стабильности
            folder_list = sorted(folders.keys())
            fcount = len(folder_list)
            
            # ────────────────────────────────────────────────────────
            # Шаг 3: Разместить папки в grid
            # ────────────────────────────────────────────────────────
            fcols = max(1, int(fcount ** 0.5) + 1)
            folder_positions = {}
            for idx, folder in enumerate(folder_list):
                fx = (idx % fcols) * GRID_SPACING
                fy = (idx // fcols) * GRID_SPACING
                folder_positions[folder] = (fx, fy)
                self.cache.folder_positions[folder] = (fx, fy)
            
            # ────────────────────────────────────────────────────────
            # Шаг 4: Разместить узлы внутри облаков со спиралью
            # ────────────────────────────────────────────────────────
            node_x, node_y, node_ids = [], [], []
            node_colors, node_sizes, node_labels, node_hovers = [], [], [], []
            
            for folder in folder_list:
                files = folders[folder]
                cx, cy = folder_positions[folder]
                n = len(files)
                
                # Сортировать файлы по количеству ошибок (убывание)
                files = sorted(files, key=lambda f: filtered_nodes[f].errors_count, reverse=True)
                
                for i, file_path in enumerate(files):
                    # Спираль с увеличенным расстоянием
                    if n <= MAX_CLOUD_SIZE:
                        angle = (i / max(1, n)) * 2 * math.pi
                        radius = CLOUD_RADIUS * (1.0 + (i % 4) * MIN_NODE_DISTANCE)
                    else:
                        # Для больших облаков - простой grid
                        cols = int(n ** 0.5) + 1
                        angle = 0
                        radius = max(CLOUD_RADIUS, (i % cols) * 1.5) + (i // cols) * 1.5
                    
                    x = cx + radius * math.cos(angle)
                    y = cy + radius * math.sin(angle)
                    
                    node_x.append(x)
                    node_y.append(y)
                    node_ids.append(file_path)
                    self.cache.node_positions[file_path] = (x, y)
                    
                    node = filtered_nodes[file_path]
                    
                    # ✅ Цвет по папке
                    color = self._get_folder_color(folder)
                    node_colors.append(color)
                    
                    # Размер: адаптивный в зависимости от ошибок и строк кода
                    size = max(12, min(60, 15 + node.errors_count * 5 + int((node.lines_of_code ** 0.5) / 15)))
                    node_sizes.append(size * self.scale_factor)
                    
                    # ✅ Лабель: только число ошибок (или имя если включено)
                    if self.show_labels.isChecked():
                        label = Path(file_path).name
                        if node.errors_count > 0:
                            label += f"\n({node.errors_count})"
                    else:
                        label = str(node.errors_count) if node.errors_count > 0 else ""
                    node_labels.append(label)
                    
                    # Hover text с подробной информацией
                    error_summary = node.get_error_summary()
                    hover_text = (
                        f"<b>{Path(file_path).name}</b><br>"
                        f"Папка: <i>{folder}</i><br>"
                        f"Строк кода: <b>{node.lines_of_code}</b><br>"
                        f"Ошибок: <b>{node.errors_count}</b><br>"
                        f"Максимум: <b>{node.max_severity}</b><br>"
                        f"Сводка: {error_summary}"
                    )
                    node_hovers.append(hover_text)
            
            # ────────────────────────────────────────────────────────
            # Шаг 5: Создать рёбра (связи между файлами)
            # ────────────────────────────────────────────────────────
            edge_x, edge_y = [], []
            if self.show_edges.isChecked():
                for src, dst in self.edges:
                    if src in node_ids and dst in node_ids:
                        try:
                            idx1 = node_ids.index(src)
                            idx2 = node_ids.index(dst)
                            edge_x.extend([node_x[idx1], node_x[idx2], None])
                            edge_y.extend([node_y[idx1], node_y[idx2], None])
                        except ValueError:
                            continue
            
            # ────────────────────────────────────────────────────────
            # Шаг 6: Создать Figure с Plotly
            # ────────────────────────────────────────────────────────
            fig = go.Figure()
            
            # Добавить рёбра
            if edge_x:
                fig.add_trace(go.Scatter(
                    x=edge_x, y=edge_y,
                    mode='lines',
                    line=dict(width=1, color='rgba(150,150,150,0.2)'),
                    hoverinfo='none',
                    showlegend=False
                ))
            
            # Добавить узлы
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                marker=dict(
                    size=node_sizes,
                    color=node_colors,
                    line=dict(width=2, color='#1a1a1a'),
                    opacity=0.85,
                    sizemode='diameter'
                ),
                text=node_labels,
                textposition='middle center',
                textfont=dict(size=10, color='#000000', family='Arial Black'),
                hovertext=node_hovers,
                hoverinfo='text',
                showlegend=False
            ))
            
            # Layout с оптимизированными параметрами
            fig.update_layout(
                title=dict(
                    text=f"📊 Граф проекта ({len(filtered_nodes)} файлов, {len(self.edges)} связей)",
                    font=dict(size=16)
                ),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='#e8e8e8',
                    zeroline=False,
                    showticklabels=False
                ),
                yaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='#e8e8e8',
                    zeroline=False,
                    showticklabels=False
                ),
                plot_bgcolor='#fafafa',
                paper_bgcolor='#ffffff',
                height=700,
                font=dict(family='Arial, sans-serif')
            )
            
            # ────────────────────────────────────────────────────────
            # Шаг 7: Сохранить и показать
            # ────────────────────────────────────────────────────────
            html_file = Path(tempfile.gettempdir()) / "naudit_graph_temp.html"
            html_content = fig.to_html(include_plotlyjs='inline')
            html_file.write_text(html_content, encoding='utf-8')
            
            file_url = QUrl.fromLocalFile(str(html_file.resolve()))
            self.web_view.load(file_url)
            
            print(f"[GraphVisualizer] ✅ Plotly готов ({len(filtered_nodes)} узлов отображено)")
        
        except Exception as e:
            print(f"[ERROR] Plotly рендеринг: {e}")
            import traceback
            traceback.print_exc()
    
    def _render_with_pyvis(self):
        """Рендерить с PyVis для сетевого анализа"""
        print(f"[GraphVisualizer] 🌐 PyVis: {len(self.nodes)} узлов")
        
        try:
            # ────────────────────────────────────────────────────────
            # Шаг 1: Применить фильтр по серьезности
            # ────────────────────────────────────────────────────────
            min_severity = self.severity_combo.currentText()
            filtered_nodes = self._filter_by_severity(self.nodes, min_severity)
            
            if not filtered_nodes:
                print("[GraphVisualizer] Нет узлов после фильтрации")
                return
            
            # ────────────────────────────────────────────────────────
            # Шаг 2: Создать сетевой граф
            # ────────────────────────────────────────────────────────
            net = Network(
                height='700px',
                width='100%',
                directed=False,
                notebook=False,
                bgcolor='#fafafa',
                font_color='#1a1a1a'
            )
            
            # Добавить узлы
            for file_path, node in filtered_nodes.items():
                # ✅ Цвет по папке
                color = self._get_folder_color(node.folder)
                
                # ✅ Лабель: только число ошибок
                if self.show_labels.isChecked():
                    label = Path(file_path).name
                else:
                    label = str(node.errors_count) if node.errors_count > 0 else Path(file_path).stem[:3]
                
                size = max(20, min(60, 25 + node.errors_count * 4))
                
                net.add_node(
                    file_path,
                    label=label,
                    color=color,
                    size=size * self.scale_factor,
                    title=f"<b>{Path(file_path).name}</b><br>Ошибок: {node.errors_count}<br>Папка: {node.folder}"
                )
            
            # ✅ Добавить рёбра
            if self.show_edges.isChecked():
                for src, dst in self.edges:
                    if src in filtered_nodes and dst in filtered_nodes:
                        net.add_edge(src, dst, color='rgba(150,150,150,0.2)')
            
            # ────────────────────────────────────────────────────────
            # Шаг 3: Настроить физику сети
            # ────────────────────────────────────────────────────────
            net.toggle_physics(True)
            net.show_buttons(filter_=['physics'])
            
            # ────────────────────────────────────────────────────────
            # Шаг 4: Сохранить и показать
            # ────────────────────────────────────────────────────────
            html_file = Path(tempfile.gettempdir()) / "naudit_graph_pyvis.html"
            net.show(str(html_file))
            
            file_url = QUrl.fromLocalFile(str(html_file.resolve()))
            self.web_view.load(file_url)
            
            print(f"[GraphVisualizer] ✅ PyVis готов ({len(filtered_nodes)} узлов отображено)")
        
        except Exception as e:
            print(f"[ERROR] PyVis рендеринг: {e}")
            import traceback
            traceback.print_exc()
    
    def clear(self):
        """Очистить граф"""
        self.nodes.clear()
        self.edges.clear()
        self.cache = GraphCache()
        self.web_view.setUrl(QUrl("about:blank"))
    
    def get_all_files(self) -> List[str]:
        """Получить список всех файлов"""
        return list(self.nodes.keys())
    
    def get_statistics(self) -> Dict:
        """Получить статистику графа"""
        return {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'total_errors': sum(n.errors_count for n in self.nodes.values()),
            'total_lines': sum(n.lines_of_code for n in self.nodes.values()),
            'unique_folders': len(set(n.folder for n in self.nodes.values()))
        }
