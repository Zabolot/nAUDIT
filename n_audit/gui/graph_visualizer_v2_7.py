#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Граф-визуализация проекта v2.7 - УЛУЧШЕННАЯ С QThread-РЕНДЕРОМ

✨ КЛЮЧЕВЫЕ УЛУЧШЕНИЯ:
✅ QThread фоновый рендер HTML (без зависания UI)
✅ Отправка прогресса в реальном времени
✅ Исправлена синхронизация Tree ↔ Graph (двусторонняя)
✅ Исправлена отрисовка граней (edges) в Plotly/PyVis
✅ Исправлена группировка по папкам (иерархические облака)
✅ Правильное переключение между Plotly и PyVis
✅ Включено распознавание GPU (даже если torch в venv)
✅ Кэширование и инвалидация при смене режимов
"""

from __future__ import annotations
import sys
import tempfile
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
import json
import re
import hashlib
import math
from enum import Enum
from collections import defaultdict

# Qt imports - ВАЖНО: установить перед созданием QApplication
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QUrl, QObject, pyqtSlot, QThread, QSize, QMutex, QWaitCondition
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSlider, QCheckBox, QComboBox, QProgressDialog, QApplication
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtGui import QFont, QColor

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

# GPU detection - попробуем загрузить torch (даже если в venv)
HAS_TORCH = False
torch = None
try:
    import torch
    HAS_TORCH = True
    GPU_AVAILABLE = torch.cuda.is_available()
except Exception as e:
    GPU_AVAILABLE = False
    HAS_TORCH = False

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ════════════════════════════════════════════════════════════════

EXCLUDE_FOLDERS = {
    '.venv', 'venv', '.env', 'venv_test', '__pycache__',
    '.git', '.github', '.pytest_cache', '.tox', 'node_modules',
    '.idea', '.vscode', 'build', 'dist', 'htmlcov', '.coverage',
    '.mypy_cache', '.DS_Store', 'egg-info', 'v.naudit', 'Trash',
}

EXCLUDE_EXT = {'.egg-info', '.dist-info', '.pyd', '.so', '.dll', '.pyc', '.pyo', '.exe'}
EXCLUDE_FILES = {'setup.py', 'setup.cfg', 'pyproject.toml', 'requirements.txt', 'README.md'}

GRID_SPACING = 40.0
FOLDER_GROUP_SPACING = 150.0  # Увеличено для лучшего разделения облаков
MAX_NODES_PER_CLOUD = 50  # Макс узлов в одном облаке


# ════════════════════════════════════════════════════════════════
# ПЕРЕЧИСЛЕНИЯ И СТРУКТУРЫ
# ════════════════════════════════════════════════════════════════

class GraphRenderMode(Enum):
    PLOTLY = "plotly"
    PYVIS = "pyvis"


@dataclass
class FileNode:
    file_path: str
    lines_of_code: int
    errors_count: int
    max_severity: str
    folder: str
    imports: Set[str] = field(default_factory=set)
    error_types: Dict[str, int] = field(default_factory=dict)
    depends_on: Set[str] = field(default_factory=set)
    
    def get_display_text(self) -> str:
        """Получить текст для отображения на узле графа"""
        if self.errors_count > 0:
            return str(self.errors_count)
        else:
            return "✓"  # Галочка для чистых файлов, лучше визуально
    
    def get_node_color(self, folder_colors: Dict[str, str], severity_colors: Dict[str, str] = None) -> str:
        """Получить цвет узла с приоритизацией папка > серьезность
        
        Папки дают основной цвет для группировки файлов.
        Серьезность может использоваться как вторичный признак (оттенок, прозрачность и т.д.)
        """
        # Приоритет 1: папка (для визуальной группировки)
        folder_color = folder_colors.get(self.folder)
        if folder_color:
            return folder_color
        
        # Приоритет 2: серьезность (если папка не определена)
        if severity_colors and self.max_severity in severity_colors:
            return severity_colors[self.max_severity]
        
        # Fallback: зелёный для чистых файлов (OK)
        return '#90EE90'


# ════════════════════════════════════════════════════════════════
# QThread РЕНДЕР
# ════════════════════════════════════════════════════════════════

class GraphRenderThread(QThread):
    """Фоновый поток для рендеринга графа HTML"""
    progress = pyqtSignal(int, str)  # процент, сообщение
    finished = pyqtSignal(str)  # html content
    error = pyqtSignal(str)  # сообщение об ошибке
    
    def __init__(self):
        super().__init__()
        self.render_func = None
        self.render_args = None
        self.mutex = QMutex()
        self.cancel_requested = False
    
    def set_render_task(self, func, args=()):
        """Установить функцию рендеринга"""
        self.mutex.lock()
        try:
            self.render_func = func
            self.render_args = args
            self.cancel_requested = False
        finally:
            self.mutex.unlock()
    
    def request_cancel(self):
        """Запросить отмену"""
        self.mutex.lock()
        try:
            self.cancel_requested = True
        finally:
            self.mutex.unlock()
    
    def run(self):
        """Выполнить рендеринг в фоне"""
        try:
            self.mutex.lock()
            try:
                if self.cancel_requested:
                    return
                func = self.render_func
                args = self.render_args
            finally:
                self.mutex.unlock()
            
            if func is None:
                self.error.emit("Функция рендеринга не установлена")
                return
            
            self.progress.emit(10, "Инициализация...")
            
            # Вызываем функцию с возможностью отправки прогресса
            html_content = func(self, *args) if args else func(self)
            
            self.progress.emit(90, "Завершение...")
            self.finished.emit(html_content)
            
        except Exception as e:
            self.error.emit(f"Ошибка рендеринга: {str(e)}")
            logger.exception("Render error")


class GraphNodeBridge(QObject):
    """Мост между JS графа и Python UI"""
    node_clicked = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
    
    @pyqtSlot(str)
    def onNodeClicked(self, file_path: str):
        """Обработчик клика на узел из JS"""
        self.node_clicked.emit(file_path)


# ════════════════════════════════════════════════════════════════
# ОСНОВНОЙ ВИДЖЕТ ГРАФА
# ════════════════════════════════════════════════════════════════

class GraphVisualizerWidget(QWidget):
    """Интерактивная граф-визуализация с QThread рендером"""
    
    # Сигналы
    file_selected = pyqtSignal(str)  # Файл выбран в графе
    focus_on_file = pyqtSignal(str)  # Нужно сфокусировать на файле в дереве
    render_progress = pyqtSignal(int, str)
    
    def __init__(self):
        super().__init__()
        
        # Данные
        self.nodes: Dict[str, FileNode] = {}
        self.edges: List[Tuple[str, str]] = []
        self.folder_colors: Dict[str, str] = {}
        self.severity_colors = {
            'CRITICAL': '#FF0000',
            'HIGH': '#FF6600',
            'MEDIUM': '#FFD700',
            'LOW': '#87CEEB',
            'OK': '#90EE90'
        }
        self.graph = nx.Graph() if nx else None
        
        # Параметры UI
        self.scale_factor = 1.0
        self.current_render_mode = GraphRenderMode.PLOTLY
        self.current_severity_filter = "Все"
        self.show_labels_mode = False
        self.show_edges_mode = True
        self.is_initializing = True
        self.project_root = None
        
        # Кэширование
        self._cached_html = {}  # Кэш: (mode, filter) -> html
        self._last_pos = {}
        
        # QThread рендер
        self.render_thread = GraphRenderThread()
        self.render_thread.progress.connect(self._on_render_progress)
        self.render_thread.finished.connect(self._on_render_finished)
        self.render_thread.error.connect(self._on_render_error)
        self.render_thread.start()
        
        # UI компоненты
        self.web_view = None
        self.web_channel = None
        self.bridge = None
        self.progress_dialog = None
        
        self._setup_ui()
        self.is_initializing = False
        
        logger.info("[GraphVisualizer v2.7] ✅ Инициализирован с QThread рендером")
    
    def _setup_ui(self):
        """Создать интерфейс"""
        layout = QVBoxLayout()
        
        # Верхняя панель управления
        top_layout = QHBoxLayout()
        
        # Режим рендеринга
        top_layout.addWidget(QLabel("🎨 Режим:"))
        self.render_combo = QComboBox()
        self.render_combo.addItems(["Plotly (Plotly.js)", "PyVis (Interactive)"])
        self.render_combo.currentIndexChanged.connect(self._on_render_changed)
        top_layout.addWidget(self.render_combo)
        
        top_layout.addSpacing(20)
        
        # Показывать имена
        self.show_labels_chk = QCheckBox("📝 Имена")
        self.show_labels_chk.setChecked(False)
        self.show_labels_chk.stateChanged.connect(self._on_labels_toggled)
        top_layout.addWidget(self.show_labels_chk)
        
        # Показывать связи
        self.show_edges_chk = QCheckBox("🔗 Связи")
        self.show_edges_chk.setChecked(True)
        self.show_edges_chk.stateChanged.connect(self._on_edges_toggled)
        top_layout.addWidget(self.show_edges_chk)
        
        top_layout.addSpacing(20)
        
        # Фильтр по серьезности
        top_layout.addWidget(QLabel("🚨 Уровень:"))
        self.severity_combo = QComboBox()
        self.severity_combo.addItems(["Все", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
        self.severity_combo.currentIndexChanged.connect(self._on_severity_changed)
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
        top_layout.addWidget(self.scale_slider)
        
        # Кнопка обновления
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self._on_refresh)
        top_layout.addWidget(refresh_btn)
        
        # Статистика
        self.stats_label = QLabel("📊 Узлов: 0 | Связей: 0 | Облаков: 0")
        top_layout.addWidget(self.stats_label)
        
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # WebView для графа
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(600)
        
        # QWebChannel
        self.bridge = GraphNodeBridge()
        self.bridge.node_clicked.connect(self._on_node_clicked_from_graph)
        
        self.web_channel = QWebChannel()
        self.web_channel.registerObject("graph_bridge", self.bridge)
        self.web_view.page().setWebChannel(self.web_channel)
        
        layout.addWidget(self.web_view)
        self.setLayout(layout)
    
    def populate_from_report(self, report, project_root: str):
        """Загрузить граф из отчёта"""
        logger.info(f"[GraphVisualizer v2.7] [LOAD] Загружаю отчёт из {project_root}")
        
        self.project_root = project_root
        self.nodes.clear()
        self.edges.clear()
        self.graph = nx.Graph() if nx else None
        self._cached_html.clear()  # Инвалидируем кэш
        
        files_info = {}
        
        # Собрать все Python файлы
        try:
            project_path = Path(project_root)
            python_files = set()
            
            if project_path.exists():
                for py_file in project_path.rglob("*.py"):
                    file_path = str(py_file.relative_to(project_path)).replace('\\', '/')
                    
                    if not self._is_excluded_path(file_path):
                        python_files.add(file_path)
                        if file_path not in files_info:
                            files_info[file_path] = {
                                'errors': 0,
                                'max_severity': 'OK',
                                'error_types': defaultdict(int),
                                'lines': 0,
                            }
            
            logger.info(f"[GraphVisualizer v2.7] 📁 Найдено Python файлов: {len(python_files)}")
        except Exception as e:
            logger.error(f"[GraphVisualizer] ⚠️ Ошибка сканирования: {e}")
        
        # Собрать ошибки
        code_issues = getattr(report, 'code_issues', None) or \
                      (getattr(report, 'metrics', None) and getattr(report.metrics, 'code_issues', None))
        
        if code_issues:
            for issue in code_issues:
                try:
                    if isinstance(issue, dict):
                        file_path = str(issue.get('file', '')).replace('\\', '/')
                        severity = issue.get('severity', 'LOW')
                    else:
                        file_path = str(getattr(issue, 'file', '')).replace('\\', '/')
                        severity = getattr(issue, 'severity', 'LOW')
                    
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
                    files_info[file_path]['error_types'][severity] += 1
                    
                    sev_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
                    curr = sev_order.get(files_info[file_path]['max_severity'], 0)
                    new = sev_order.get(severity, 0)
                    if new > curr:
                        files_info[file_path]['max_severity'] = severity
                except Exception:
                    pass
        
        # Создать узлы
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
        
        # Создать связи
        for file_path, node in self.nodes.items():
            for imported_module in node.imports:
                for other_file_path in self.nodes.keys():
                    if file_path == other_file_path:
                        continue
                    
                    other_file_lower = other_file_path.lower().replace('\\', '/')
                    if f"/{imported_module}/" in f"/{other_file_lower}/" or \
                       other_file_lower.endswith(f"/{imported_module}.py"):
                        
                        edge = (file_path, other_file_path)
                        if edge not in self.edges:
                            self.edges.append(edge)
                            node.depends_on.add(other_file_path)
                            
                            if self.graph:
                                self.graph.add_edge(file_path, other_file_path)
        
        # Обновить статистику
        cloud_count = len(self.folder_colors)
        self.stats_label.setText(
            f"📊 Узлов: {len(self.nodes)} | Связей: {len(self.edges)} | Облаков: {cloud_count}"
        )
        
        logger.info(f"[GraphVisualizer v2.7] ✅ Загружено узлов: {len(self.nodes)}, связей: {len(self.edges)}, облаков: {cloud_count}")
        
        # Отобразить граф
        self._render_graph()
    
    def _is_excluded_path(self, path_str: str) -> bool:
        """Проверить исключение пути"""
        path = Path(path_str)
        for part in path.parts:
            if part in EXCLUDE_FOLDERS:
                return True
        for ext in EXCLUDE_EXT:
            if str(path).endswith(ext):
                return True
        if path.name in EXCLUDE_FILES:
            return True
        return False
    
    def _get_folder_group(self, file_path: str) -> str:
        """Получить группу папки"""
        p = Path(file_path)
        parent = p.parent
        if str(parent) in ('.', ''):
            return 'root/'
        
        parts = [part for part in parent.parts if part not in EXCLUDE_FOLDERS]
        if not parts:
            return 'root/'
        
        folder = '/'.join(parts).strip('/') + '/'
        return folder
    
    def _extract_imports(self, file_path: str) -> Set[str]:
        """Парсить импорты"""
        imports = set()
        try:
            if self.project_root is None:
                return imports
            
            full_path = Path(self.project_root) / file_path
            if not full_path.exists() or full_path.suffix != '.py':
                return imports
            
            content = full_path.read_text(encoding='utf-8', errors='ignore')
            import_pattern = r'(?:from\s+([\w.]+)|import\s+([\w.]+))'
            for match in re.finditer(import_pattern, content):
                module = match.group(1) or match.group(2)
                if module:
                    root_module = module.split('.')[0]
                    if not root_module.startswith('_'):
                        imports.add(root_module)
        except Exception as e:
            logger.debug(f"Ошибка парсинга импортов {file_path}: {e}")
        
        return imports
    
    def _assign_folder_colors(self):
        """Присвоить цвета папкам"""
        folder_groups = defaultdict(int)
        
        for node in self.nodes.values():
            folder_group = node.folder
            folder_groups[folder_group] += 1
        
        hues = {
            "root/": 0,
            "n_audit/": 240,
            "src/": 240,
            "gui/": 120,
            "core/": 60,
            "models/": 300,
            "utils/": 30,
        }
        
        hue_offset = 0
        for folder in sorted(folder_groups.keys()):
            hue = next((h for k, h in hues.items() if folder.startswith(k) or k == folder), None)
            if hue is None:
                hue = (hue_offset * 45) % 360
                hue_offset += 1
            
            saturation = 70
            lightness = 55
            key = folder if folder.endswith('/') else f"{folder}/"
            self.folder_colors[key] = f"hsl({hue}, {saturation}%, {lightness}%)"
        
        logger.info(f"[GraphVisualizer] 🎨 Назначены цвета {len(self.folder_colors)} папкам")
    
    def _calculate_positions_with_clustering(self, G, filtered_nodes: List[str]) -> Dict[str, Tuple[float, float]]:
        """Рассчитать позиции с иерархической группировкой (облака)"""
        if len(filtered_nodes) == 0:
            return {}
        
        # Группируем узлы по папкам
        folder_to_nodes = defaultdict(list)
        for node in filtered_nodes:
            folder = self.nodes[node].folder
            folder_to_nodes[folder].append(node)
        
        # Строим граф для подграфов каждой папки
        pos = {}
        
        # Базовая раскладка для всех узлов
        try:
            base_pos = nx.spring_layout(
                G,
                k=2.0,
                iterations=50,
                seed=42,
                scale=100,
            )
        except Exception:
            base_pos = {node: (0, 0) for node in filtered_nodes}
        
        # Сохраняем базовые позиции
        self._last_pos = base_pos
        
        # Теперь применяем облачную группировку
        folders = sorted(folder_to_nodes.keys())
        cols = max(1, int(math.sqrt(len(folders))))
        
        for idx, (folder, nodes_in_folder) in enumerate(sorted(folder_to_nodes.items())):
            col = idx % cols
            row = idx // cols
            
            # Центр облака папки
            cloud_center_x = (col - cols/2 + 0.5) * FOLDER_GROUP_SPACING
            cloud_center_y = (row - int(len(folders)/cols)/2) * FOLDER_GROUP_SPACING
            
            # Размещаем узлы внутри облака
            cloud_radius = min(80, FOLDER_GROUP_SPACING / 3)
            
            for local_idx, node in enumerate(nodes_in_folder):
                if node in base_pos:
                    base_x, base_y = base_pos[node]
                    # Нормализуем
                    local_x = base_x * (cloud_radius / 100.0)
                    local_y = base_y * (cloud_radius / 100.0)
                else:
                    # Fallback - размещаем в круг
                    angle = 2 * math.pi * local_idx / len(nodes_in_folder)
                    local_x = math.cos(angle) * cloud_radius
                    local_y = math.sin(angle) * cloud_radius
                
                # Применяем смещение
                pos[node] = (
                    cloud_center_x + local_x,
                    cloud_center_y + local_y
                )
        
        # Применяем масштаб
        pos = {node: (x * self.scale_factor, y * self.scale_factor) 
               for node, (x, y) in pos.items()}
        
        logger.info(f"[GraphVisualizer] 🎯 Позиции рассчитаны: {len(pos)} узлов с облачной группировкой")
        return pos
    
    def _calculate_positions_gpu_accelerated(self, G, filtered_nodes: List[str]) -> Dict[str, Tuple[float, float]]:
        """Рассчитать позиции с GPU ускорением (если доступен torch/CUDA)
        
        Для больших графов (1000+ узлов) GPU может дать ускорение в 5-10x
        """
        if not HAS_TORCH or not GPU_AVAILABLE or len(filtered_nodes) < 100:
            # Возвращаемся на CPU если GPU недоступен или граф маленький
            return self._calculate_positions_with_clustering(G, filtered_nodes)
        
        try:
            import torch
            
            logger.info(f"[GraphVisualizer] 🚀 GPU расчёт позиций ({torch.cuda.get_device_name(0)})")
            
            # Преобразуем граф в матрицу смежности на GPU
            adj_matrix = torch.tensor(
                nx.to_numpy_array(G, nodelist=filtered_nodes, dtype=float),
                dtype=torch.float32,
                device='cuda'
            )
            
            # Инициализируем позиции случайно
            n_nodes = len(filtered_nodes)
            pos_gpu = torch.randn(n_nodes, 2, device='cuda') * 10
            
            # Несколько итераций force-directed алгоритма на GPU
            lr = 0.1
            for iteration in range(20):
                # Вычисляем силы отталкивания между всеми парами узлов
                distances = torch.cdist(pos_gpu, pos_gpu)
                distances[torch.eye(n_nodes, dtype=torch.bool, device='cuda')] = 1.0  # Избегаем деления на 0
                
                repulsion_forces = adj_matrix / (distances ** 2)
                
                # Применяем силы привлечения для соседних узлов
                attraction_forces = -adj_matrix * (distances - 1.0)
                
                # Суммарные силы
                forces = repulsion_forces + attraction_forces
                movement = forces.sum(dim=1)
                
                # Обновляем позиции
                pos_gpu = pos_gpu + lr * movement
                pos_gpu = torch.clamp(pos_gpu, -100, 100)  # Ограничиваем диапазон
            
            # Переносим обратно на CPU и преобразуем в dict
            pos_dict = {}
            pos_np = pos_gpu.cpu().numpy()
            for idx, node in enumerate(filtered_nodes):
                pos_dict[node] = tuple(pos_np[idx])
            
            # Применяем облачную группировку поверх GPU позиций
            folder_to_nodes = defaultdict(list)
            for node in filtered_nodes:
                folder = self.nodes[node].folder
                folder_to_nodes[folder].append(node)
            
            # Сдвигаем облака
            folders = sorted(folder_to_nodes.keys())
            cols = max(1, int(math.sqrt(len(folders))))
            cloud_offset = {}
            
            for idx, folder in enumerate(folders):
                col = idx % cols
                row = idx // cols
                offset_x = (col - cols/2 + 0.5) * FOLDER_GROUP_SPACING
                offset_y = (row - int(len(folders)/cols)/2) * FOLDER_GROUP_SPACING
                cloud_offset[folder] = (offset_x, offset_y)
            
            # Применяем смещения облаков
            final_pos = {}
            for node in filtered_nodes:
                folder = self.nodes[node].folder
                offset_x, offset_y = cloud_offset.get(folder, (0, 0))
                x, y = pos_dict[node]
                final_pos[node] = (x + offset_x, y + offset_y)
            
            logger.info(f"[GraphVisualizer] ✅ GPU позиции рассчитаны для {len(final_pos)} узлов")
            return final_pos
            
        except Exception as e:
            logger.warning(f"[GraphVisualizer] ⚠️ Ошибка GPU расчёта: {e}, возвращаюсь на CPU")
            return self._calculate_positions_with_clustering(G, filtered_nodes)
    
    def _generate_plotly_html(self, render_thread=None) -> str:
        """Генерировать Plotly HTML"""
        if not HAS_PLOTLY:
            return self._generate_error_html("Plotly не установлен")
        
        try:
            filtered_nodes = self._filter_nodes_by_severity()
            
            if not filtered_nodes:
                return self._generate_error_html("Нет узлов для отображения")
            
            # Проверяем кэш
            cache_key = (GraphRenderMode.PLOTLY, self.current_severity_filter)
            if cache_key in self._cached_html:
                logger.info("[GraphVisualizer] 💾 Используется кэшированный HTML (Plotly)")
                return self._cached_html[cache_key]
            
            if render_thread:
                render_thread.progress.emit(20, "Построение графа...")
            
            # Создаём граф
            G = nx.Graph()
            for file_path in filtered_nodes:
                node = self.nodes[file_path]
                G.add_node(file_path, errors=node.errors_count, severity=node.max_severity)
            
            if render_thread:
                render_thread.progress.emit(40, "Добавление связей...")
            
            # Добавляем связи
            if self.show_edges_mode:
                for source, target in self.edges:
                    if source in filtered_nodes and target in filtered_nodes:
                        G.add_edge(source, target)
            
            if render_thread:
                render_thread.progress.emit(50, "Расчёт позиций...")
            
            # Рассчитываем позиции (с GPU ускорением для больших графов)
            if len(filtered_nodes) > 500 and GPU_AVAILABLE:
                pos = self._calculate_positions_gpu_accelerated(G, filtered_nodes)
            else:
                pos = self._calculate_positions_with_clustering(G, filtered_nodes)
            
            if render_thread:
                render_thread.progress.emit(60, "Построение визуализации...")
            
            # Строим edge traces (оптимизированно)
            edge_trace_list = []
            
            if self.show_edges_mode and len(G.edges()) > 0:
                # Собираем все edge в один trace вместо создания trace на каждое edge
                edge_x = []
                edge_y = []
                edge_count = 0
                
                for source, target in G.edges():
                    if source in pos and target in pos:
                        x0, y0 = pos[source]
                        x1, y1 = pos[target]
                        
                        edge_x.extend([x0, x1, None])  # None разделяет линии
                        edge_y.extend([y0, y1, None])
                        edge_count += 1
                        
                        # Ограничиваем количество edges для оптимизации (макс. 5000)
                        if edge_count >= 5000:
                            logger.warning(f"[GraphVisualizer] ⚠️ Лимит edges достигнут (5000), остальные {len(G.edges()) - 5000} скрыты")
                            break
                
                if edge_x:  # Если есть edges
                    edge_trace = go.Scatter(
                        x=edge_x,
                        y=edge_y,
                        mode='lines',
                        line=dict(width=1, color='rgba(125,125,125,0.3)'),
                        hoverinfo='none',
                        showlegend=False,
                        name='edges'
                    )
                    edge_trace_list.append(edge_trace)
                    logger.info(f"[GraphVisualizer] 📍 Edges: {edge_count} линий в одном trace")
            

            # Узлы
            node_x = []
            node_y = []
            node_text = []
            node_size = []
            node_color = []
            node_hover_text = []
            customdata = []
            
            for file_path in filtered_nodes:
                if file_path not in pos:
                    continue
                
                x, y = pos[file_path]
                node_x.append(x)
                node_y.append(y)
                
                node = self.nodes[file_path]
                
                if self.show_labels_mode:
                    node_text.append(f"{node.file_path}\n{node.get_display_text()}")
                else:
                    node_text.append(node.get_display_text())
                
                size = max(10, min(30, 10 + node.errors_count))
                node_size.append(size)
                
                color = node.get_node_color(self.folder_colors, self.severity_colors)
                node_color.append(color)
                
                hover = f"<b>{node.file_path}</b><br>"
                hover += f"Ошибок: {node.errors_count}<br>"
                hover += f"Серьезность: {node.max_severity}<br>"
                hover += f"Папка: {node.folder}"
                node_hover_text.append(hover)
                
                customdata.append(file_path)
            
            if render_thread:
                render_thread.progress.emit(75, "Создание Plotly фигуры...")
            
            node_trace = go.Scatter(
                x=node_x,
                y=node_y,
                mode='markers+text',
                text=node_text,
                textposition='middle center',
                textfont=dict(size=10, color='white'),
                hovertext=node_hover_text,
                hoverinfo='text',
                customdata=customdata,
                marker=dict(
                    size=node_size,
                    color=node_color,
                    line=dict(width=2, color='white'),
                ),
                showlegend=False,
                name='nodes'
            )
            
            fig = go.Figure(data=edge_trace_list + [node_trace])
            
            fig.update_layout(
                title='📊 Граф ошибок проекта (облачная группировка)',
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='#f8f9fa',
                font=dict(size=11),
                height=600,
            )
            
            if render_thread:
                render_thread.progress.emit(85, "Конвертирование в HTML...")
            
            html_content = fig.to_html(include_plotlyjs='cdn')
            html_content = self._inject_qwebchannel_code(html_content)
            
            # Кэшируем
            self._cached_html[cache_key] = html_content
            
            if render_thread:
                render_thread.progress.emit(95, "Готово!")
            
            return html_content
        
        except Exception as e:
            logger.exception("Ошибка генерации Plotly")
            return self._generate_error_html(f"Ошибка: {str(e)}")
    
    def _generate_pyvis_html(self, render_thread=None) -> str:
        """Генерировать PyVis HTML"""
        if not HAS_PYVIS:
            return self._generate_error_html("PyVis не установлен")
        
        try:
            filtered_nodes = self._filter_nodes_by_severity()
            
            if not filtered_nodes:
                return self._generate_error_html("Нет узлов для отображения")
            
            # Проверяем кэш
            cache_key = (GraphRenderMode.PYVIS, self.current_severity_filter)
            if cache_key in self._cached_html:
                logger.info("[GraphVisualizer] 💾 Используется кэшированный HTML (PyVis)")
                return self._cached_html[cache_key]
            
            if render_thread:
                render_thread.progress.emit(20, "Создание PyVis сети...")
            
            net = Network(height='600px', directed=False)
            
            # ПОЛНОСТЬЮ отключаем все параметры физики и гравитации
            try:
                # Отключаем основную физику
                net.physics.enabled = False
                
                # Отключаем стабилизацию
                net.physics.stabilization.enabled = False
                net.physics.stabilization.iterations = 0
                net.physics.stabilization.fit = False
                
                # Отключаем гравитацию и другие силы
                net.physics.barnesHut.enabled = False
                net.physics.forceAtlas2Based.enabled = False
                net.physics.repulsion.enabled = False
                
                # Фиксируем все узлы
                net.set_options("""
                {
                    "physics": {
                        "enabled": false,
                        "barnesHut": {"enabled": false},
                        "forceAtlas2Based": {"enabled": false},
                        "repulsion": {"enabled": false},
                        "hierarchicalRepulsion": {"enabled": false},
                        "stabilization": {"enabled": false, "iterations": 0}
                    },
                    "interaction": {
                        "navigationButtons": true,
                        "keyboard": true
                    }
                }
                """)
            except Exception as e:
                logger.warning(f"[GraphVisualizer] ⚠️ Ошибка при отключении физики PyVis: {e}")
            
            if render_thread:
                render_thread.progress.emit(40, "Добавление узлов...")
            
            # Группируем узлы по папкам для раскраски
            G = nx.Graph()
            for file_path in filtered_nodes:
                node = self.nodes[file_path]
                G.add_node(file_path)
            
            if self.show_edges_mode:
                for source, target in self.edges:
                    if source in filtered_nodes and target in filtered_nodes:
                        G.add_edge(source, target)
            
            # Рассчитываем позиции (с GPU ускорением для больших графов)
            if len(filtered_nodes) > 500 and GPU_AVAILABLE:
                pos = self._calculate_positions_gpu_accelerated(G, filtered_nodes)
            else:
                pos = self._calculate_positions_with_clustering(G, filtered_nodes)
            
            # Добавляем узлы в PyVis
            for file_path in filtered_nodes:
                node = self.nodes[file_path]
                
                if self.show_labels_mode:
                    label = f"{node.file_path}\n{node.get_display_text()}"
                else:
                    label = node.get_display_text()
                
                color = node.get_node_color(self.folder_colors, self.severity_colors)
                size = max(15, min(50, 15 + node.errors_count * 2))
                folder_group = node.folder
                
                # Используем расчётные позиции
                x, y = pos.get(file_path, (0, 0))
                
                net.add_node(
                    file_path,
                    label=label,
                    title=file_path,
                    color=color,
                    size=size,
                    group=folder_group,
                    x=x * 10,  # PyVis масштабирует по-своему
                    y=y * 10,
                )
            
            if render_thread:
                render_thread.progress.emit(60, "Добавление связей...")
            
            # Добавляем связи (ограничиваем количество для оптимизации)
            edge_count = 0
            max_edges = 10000  # Макс. связей в PyVis
            
            if self.show_edges_mode:
                for source, target in self.edges:
                    if source in filtered_nodes and target in filtered_nodes:
                        try:
                            net.add_edge(source, target)
                            edge_count += 1
                            
                            # Ограничиваем количество для оптимизации
                            if edge_count >= max_edges:
                                logger.warning(f"[GraphVisualizer] ⚠️ Лимит edges достигнут ({max_edges}), остальные {len(self.edges) - edge_count} скрыты")
                                break
                        except Exception as e:
                            logger.warning(f"[GraphVisualizer] ⚠️ Ошибка при добавлении edge {source}->{target}: {e}")
            
            if edge_count > 0:
                logger.info(f"[GraphVisualizer] 📍 PyVis: добавлено {edge_count} связей")
            
            # ДОПОЛНИТЕЛЬНО: Убеждаемся что физика отключена ПОСЛЕ добавления edges
            # (PyVis может попытаться переделать позиции при добавлении edges)
            try:
                net.physics.enabled = False
                net.physics.stabilization.enabled = False
                net.show = False  # Отключаем автоматический показ
            except:
                pass
            
            if render_thread:
                render_thread.progress.emit(80, "Генерация HTML...")
            
            # Получаем HTML
            try:
                if hasattr(net, 'get_html'):
                    html_content = net.get_html()
                else:
                    temp_file = Path(tempfile.gettempdir()) / "naudit_pyvis_temp.html"
                    net.write_html(str(temp_file))
                    html_content = temp_file.read_text(encoding='utf-8')
            except Exception:
                temp_file = Path(tempfile.gettempdir()) / "naudit_pyvis_temp.html"
                net.write_html(str(temp_file))
                html_content = temp_file.read_text(encoding='utf-8')
            
            html_content = self._inject_qwebchannel_code(html_content)
            
            # Кэшируем
            self._cached_html[cache_key] = html_content
            
            if render_thread:
                render_thread.progress.emit(95, "Готово!")
            
            return html_content
        
        except Exception as e:
            logger.exception("Ошибка генерации PyVis")
            return self._generate_error_html(f"Ошибка PyVis: {str(e)}")
    
    def _filter_nodes_by_severity(self) -> List[str]:
        """Отфильтровать узлы по серьезности"""
        severity_filter = self.current_severity_filter
        
        # "Все" означает показать все узлы с ошибками И без ошибок
        if severity_filter == "Все":
            return list(self.nodes.keys())
        
        # Для конкретного фильтра показываем узлы с этой серьезностью и выше
        severity_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, 'OK': 0}
        filter_level = severity_order.get(severity_filter, 0)
        
        filtered = []
        for file_path, node in self.nodes.items():
            node_level = severity_order.get(node.max_severity, 0)
            # Включаем узлы с уровнем >= filter_level (то есть более серьезные ошибки)
            if node_level >= filter_level:
                filtered.append(file_path)
        
        logger.info(f"[GraphVisualizer] 🔍 Фильтрация: {len(filtered)}/{len(self.nodes)} узлов (фильтр: {severity_filter})")
        return filtered
    
    def _inject_qwebchannel_code(self, html_content: str) -> str:
        """Инжектировать JS для QWebChannel и отключения физики PyVis"""
        js_code = """
        <script>
        window.addEventListener('load', function() {
            // ⚠️ КРИТИЧНО: Отключаем физику PyVis после загрузки
            if (window.network) {
                try {
                    window.network.physics.enabled = false;
                    window.network.physics.barnesHut.enabled = false;
                    window.network.physics.forceAtlas2Based.enabled = false;
                    window.network.physics.repulsion.enabled = false;
                    window.network.physics.hierarchicalRepulsion.enabled = false;
                    window.network.physics.stabilization.enabled = false;
                    window.network.physics.stabilization.iterations = 0;
                    window.network.physics.stabilization.fit = false;
                    console.log('[PyVis] Physics полностью отключена в JavaScript');
                } catch(e) {
                    console.error('[PyVis] Ошибка отключения физики:', e);
                }
            }
            
            // Обработчик кликов Plotly
            var plot = document.querySelector('.plotly-graph-div');
            if (plot && plot.on) {
                plot.on('plotly_click', function(data) {
                    var point = data.points[0];
                    var filePath = null;
                    try {
                        if (point.customdata) filePath = point.customdata;
                        else if (point.text) filePath = point.text;
                    } catch(e) {}
                    if (filePath && window.graph_bridge) {
                        window.graph_bridge.onNodeClicked(String(filePath));
                    }
                });
            }
            
            // Обработчик кликов PyVis
            try {
                if (window.network && window.network.on) {
                    window.network.on('click', function(params) {
                        try {
                            if (params.nodes && params.nodes.length > 0) {
                                var id = params.nodes[0];
                                if (window.graph_bridge) {
                                    window.graph_bridge.onNodeClicked(String(id));
                                }
                            }
                        } catch(e) {}
                    });
                }
            } catch(e) {}
        });
        </script>
        """
        
        html_content = html_content.replace('</body>', js_code + '</body>')
        return html_content
    
    def _generate_error_html(self, error_message: str) -> str:
        """HTML сообщение об ошибке"""
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial; display: flex; align-items: center; justify-content: center;
                        height: 100vh; margin: 0; background: #f5f5f5; }}
                .error-box {{ background: white; padding: 40px; border-radius: 8px;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; max-width: 500px; }}
                .error-box h1 {{ color: #d32f2f; margin: 0 0 10px 0; }}
                .error-box p {{ color: #666; margin: 0; }}
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
        """Запустить рендеринг в фоновом потоке"""
        logger.info(f"[GraphVisualizer v2.7] 🎨 Запускаю рендеринг {self.current_render_mode.value}...")
        
        # Показываем прогресс диалог
        if self.progress_dialog is None:
            self.progress_dialog = QProgressDialog(
                "Рендеринг графа...",
                "Отмена",
                0,
                100,
                self
            )
            self.progress_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        self.progress_dialog.show()
        
        # Выбираем функцию рендера
        if self.current_render_mode == GraphRenderMode.PLOTLY:
            render_func = self._generate_plotly_html
        else:
            render_func = self._generate_pyvis_html
        
        # Запускаем в фоновом потоке
        self.render_thread.set_render_task(render_func)
        self.render_thread.start()
    
    def _on_render_progress(self, progress: int, message: str):
        """Получили прогресс из потока"""
        if self.progress_dialog:
            self.progress_dialog.setValue(progress)
            self.progress_dialog.setLabelText(message)
        self.render_progress.emit(progress, message)
    
    def _on_render_finished(self, html_content: str):
        """Рендер завершён"""
        try:
            self.web_view.setHtml(html_content)
            logger.info("[GraphVisualizer v2.7] ✅ Граф отрендерен")
        except Exception as e:
            logger.exception("Ошибка установки HTML")
        finally:
            if self.progress_dialog:
                self.progress_dialog.close()
    
    def _on_render_error(self, error_msg: str):
        """Ошибка при рендере"""
        logger.error(f"[GraphVisualizer] ❌ {error_msg}")
        if self.progress_dialog:
            self.progress_dialog.close()
        
        error_html = self._generate_error_html(error_msg)
        self.web_view.setHtml(error_html)
    
    def _on_render_changed(self, index: int):
        """Смена режима"""
        if self.is_initializing:
            return
        
        modes = [GraphRenderMode.PLOTLY, GraphRenderMode.PYVIS]
        self.current_render_mode = modes[index]
        
        # Инвалидируем кэш для другого режима
        self._cached_html.clear()
        
        logger.info(f"[GraphVisualizer] 🔄 Режим изменён на {self.current_render_mode.value}")
        self._render_graph()
    
    def _on_labels_toggled(self, state):
        self.show_labels_mode = (state == Qt.CheckState.Checked.value)
        self._cached_html.clear()  # Инвалидируем кэш
        self._render_graph()
    
    def _on_edges_toggled(self, state):
        self.show_edges_mode = (state == Qt.CheckState.Checked.value)
        self._cached_html.clear()
        self._render_graph()
    
    def _on_severity_changed(self, index: int):
        if self.is_initializing:
            return
        
        severity_levels = ["Все", "CRITICAL", "HIGH", "MEDIUM", "LOW"]
        self.current_severity_filter = severity_levels[index]
        
        self._cached_html.clear()
        logger.info(f"[GraphVisualizer] 🚨 Фильтр: {self.current_severity_filter}")
        self._render_graph()
    
    def _on_scale_changed(self, value: int):
        if self.is_initializing:
            return
        
        self.scale_factor = value / 100.0
        self._cached_html.clear()
        self._render_graph()
    
    def _on_refresh(self):
        logger.info("[GraphVisualizer] 🔄 Обновление графа...")
        self._cached_html.clear()
        self._render_graph()
    
    def _on_node_clicked_from_graph(self, file_path: str):
        """Узел нажат в графе - синхронизируем с деревом"""
        logger.info(f"[GraphVisualizer] 🖱️ Узел нажат: {file_path}")
        self.file_selected.emit(file_path)
    
    def focus_on_node(self, file_path: str):
        """Фокус и центровка на узел из дерева"""
        logger.info(f"[GraphVisualizer] 🎯 Фокусируюсь на: {file_path}")
        
        if file_path not in self.nodes:
            logger.warning(f"Файл не найден в графе: {file_path}")
            return
        
        # Получаем позицию
        pos = getattr(self, '_last_pos', {})
        
        if self.current_render_mode == GraphRenderMode.PLOTLY:
            if pos and file_path in pos:
                x, y = pos[file_path]
                dx, dy = 50.0, 50.0
                js = f"""
                (function() {{
                    var plot = document.querySelector('.plotly-graph-div');
                    if (!plot) return;
                    try {{
                        Plotly.restyle(plot, {{'marker.opacity': 0.25}});
                        Plotly.restyle(plot, {{'marker.opacity': 1}}, [plot.data.length-1]);
                        Plotly.relayout(plot, {{
                            'xaxis.range': [{x - dx}, {x + dx}],
                            'yaxis.range': [{y - dy}, {y + dy}]
                        }});
                    }} catch(e) {{}}
                }})();
                """
            else:
                js = """(function() {
                    var plot = document.querySelector('.plotly-graph-div');
                    if (!plot) return;
                    try { Plotly.restyle(plot, {'marker.opacity': 0.25}); } catch(e){}
                })();"""
        else:
            js = f"""
            if (window.network) {{
                try {{ 
                    window.network.selectNodes(['{file_path}']); 
                    window.network.fit(); 
                }} catch(e){{}}
            }}
            """
        
        self.web_view.page().runJavaScript(js)
    
    def highlight_file(self, file_path: str):
        """Выделить файл"""
        normalized_path = file_path.replace("\\", "/")
        
        if normalized_path not in self.nodes:
            logger.warning(f"Файл не найден в графе: {normalized_path}")
            return
        
        self.focus_on_node(normalized_path)
        logger.info(f"[GraphVisualizer] ✅ Выделен файл: {normalized_path}")
    
    def export_current_graph(self) -> Optional[Path]:
        """Экспортировать оба варианта графа (Plotly И PyVis) в папку reports/graphs/
        
        Returns:
            Path к папке с экспортированными графами или None
        """
        try:
            if not self.nodes:
                logger.warning("[GraphVisualizer] ⚠️ Граф пуст, нечего экспортировать")
                return None
            
            # Определяем папку экспорта
            reports_dir = Path.home() / ".naudit" / "reports"
            graphs_dir = reports_dir / "graphs"
            graphs_dir.mkdir(parents=True, exist_ok=True)
            
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            exported_files = []
            
            # Экспортируем Plotly версию
            try:
                html_plotly = self._generate_plotly_html()
                if html_plotly:
                    plotly_path = graphs_dir / f"graph_plotly_{timestamp}.html"
                    plotly_path.write_text(html_plotly, encoding='utf-8')
                    exported_files.append(plotly_path)
                    logger.info(f"[GraphVisualizer] ✅ Plotly граф экспортирован: {plotly_path}")
            except Exception as e:
                logger.error(f"[GraphVisualizer] ❌ Ошибка экспорта Plotly: {e}")
            
            # Экспортируем PyVis версию
            try:
                html_pyvis = self._generate_pyvis_html()
                if html_pyvis:
                    pyvis_path = graphs_dir / f"graph_pyvis_{timestamp}.html"
                    pyvis_path.write_text(html_pyvis, encoding='utf-8')
                    exported_files.append(pyvis_path)
                    logger.info(f"[GraphVisualizer] ✅ PyVis граф экспортирован: {pyvis_path}")
            except Exception as e:
                logger.error(f"[GraphVisualizer] ❌ Ошибка экспорта PyVis: {e}")
            
            if exported_files:
                logger.info(f"[GraphVisualizer] 📁 Графы экспортированы в: {graphs_dir}")
                return graphs_dir
            else:
                logger.warning("[GraphVisualizer] ⚠️ Не удалось создать ни один граф для экспорта")
                return None
            
        except Exception as e:
            logger.exception(f"[GraphVisualizer] ❌ Ошибка экспорта: {e}")
            return None
    
    def closeEvent(self, event):
        """Завершение виджета"""
        if self.render_thread and self.render_thread.isRunning():
            self.render_thread.request_cancel()
            self.render_thread.quit()
            self.render_thread.wait(5000)
        super().closeEvent(event)
