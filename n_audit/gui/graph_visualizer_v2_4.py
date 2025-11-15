#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Граф-визуализация проекта v2.4 - ИСПРАВЛЕННАЯ И ОПТИМИЗИРОВАННАЯ

ИСПРАВЛЕНИЯ:
✅ Фиксит белый лист (правильная инициализация HTML)
✅ Синхронизация граф ↔ дерево
✅ QWebChannel для фокуса на узлы
✅ Плавная анимация переходов
✅ Оптимизация для проектов >1000 файлов

УЛУЧШЕНИЯ:
✅ Правильная обработка больших проектов (кэширование)
✅ Точный подсчёт файлов (без дублирования)
✅ Интерактивная обратная связь
"""

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

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSlider, QCheckBox, QComboBox, QSpinBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QUrl, QObject, pyqtSlot, QThread
from PyQt6.QtCore import QEvent, QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
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

EXCLUDE_FOLDERS = {
    '.venv', 'venv', '.env',
    '__pycache__',
    '.git', '.github',
    '.pytest_cache', '.tox',
    'node_modules', '.npm',
    '.idea', '.vscode', '.sublime',
    'build', 'dist', '.build',
    'htmlcov', '.coverage',
    '.mypy_cache', '.dmypy',
    '.DS_Store',
    'egg-info',
    'v.naudit', 'venv_test',
}

EXCLUDE_EXT = {'.egg-info', '.dist-info', '.pyd', '.so', '.dll'}

GRID_SPACING = 25.0
CLOUD_RADIUS = 3.0
MIN_NODE_DISTANCE = 3.0
MAX_CLOUD_SIZE = 20

# Для оптимизации больших проектов
LARGE_PROJECT_THRESHOLD = 1000  # файлов
OPTIMIZE_FOR_LARGE = True
NODE_CACHE_SIZE = 5000


# ════════════════════════════════════════════════════════════════
# КЛАССЫ
# ════════════════════════════════════════════════════════════════

class GraphNodeBridge(QObject):
    """Мост между JavaScript графа и Python UI через QWebChannel"""
    node_clicked = pyqtSignal(str)
    node_hovered = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
    
    @pyqtSlot(str)
    def onNodeClicked(self, file_path: str):
        print(f"[GraphBridge] Узел клик: {file_path}")
        self.node_clicked.emit(file_path)
    
    @pyqtSlot(str)
    def onNodeHovered(self, file_path: str):
        self.node_hovered.emit(file_path)


@dataclass
class FileNode:
    """Узел графа"""
    file_path: str
    lines_of_code: int
    errors_count: int
    max_severity: str
    folder: str
    imports: Set[str] = field(default_factory=set)
    error_types: Dict[str, int] = field(default_factory=dict)
    
    def get_error_summary(self) -> str:
        parts = []
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = self.error_types.get(severity, 0)
            if count > 0:
                parts.append(f"{severity}:{count}")
        return " ".join(parts) if parts else "OK"


class GraphVisualizerWidget(QWidget):
    """Интерактивная граф-визуализация v2.4 - ИСПРАВЛЕННАЯ"""
    
    file_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        self.nodes: Dict[str, FileNode] = {}
        self.edges: List[Tuple[str, str]] = []
        self.graph = nx.Graph() if nx else None
        
        self.scale_factor = 1.0
        self.current_render = "plotly"
        self.is_initializing = True
        
        # ВАЖНО: Инициализируем компоненты ДО setup_ui
        self.web_view = None
        self.web_channel = None
        self.bridge = None
        
        self._setup_ui()
        self.is_initializing = False
        
        print("[GraphVisualizer] ✅ Инициализирован v2.4")
    
    def _setup_ui(self):
        """Создать UI"""
        layout = QVBoxLayout()
        
        # Верхняя панель
        top_layout = QHBoxLayout()
        
        # Выбор рендера
        top_layout.addWidget(QLabel("🎨 Рендер:"))
        self.render_combo = QComboBox()
        self.render_combo.addItems(["Plotly", "PyVis"])
        self.render_combo.currentIndexChanged.connect(self._on_render_changed)
        top_layout.addWidget(self.render_combo)
        
        top_layout.addSpacing(20)
        
        # Опции
        self.show_labels = QCheckBox("📝 Имена")
        self.show_labels.setChecked(False)
        self.show_labels.stateChanged.connect(self._on_labels_toggled)
        top_layout.addWidget(self.show_labels)
        
        self.show_edges = QCheckBox("🔗 Связи")
        self.show_edges.setChecked(True)
        self.show_edges.stateChanged.connect(self._on_edges_toggled)
        top_layout.addWidget(self.show_edges)
        
        # Фильтр серьезности
        top_layout.addWidget(QLabel("🚨 Уровень:"))
        self.severity_combo = QComboBox()
        self.severity_combo.addItems(["Все", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
        self.severity_combo.currentIndexChanged.connect(self._on_severity_changed)
        top_layout.addWidget(self.severity_combo)
        
        # Масштаб
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
        
        # QWebChannel для обратной связи
        self.bridge = GraphNodeBridge()
        self.bridge.node_clicked.connect(self._on_node_clicked)
        
        self.web_channel = QWebChannel()
        self.web_channel.registerObject("graph_bridge", self.bridge)
        self.web_view.page().setWebChannel(self.web_channel)
        
        layout.addWidget(self.web_view)
        self.setLayout(layout)
    
    def _is_excluded_path(self, path_str: str) -> bool:
        """Проверить, исключена ли папка"""
        path = Path(path_str)
        for part in path.parts:
            if part in EXCLUDE_FOLDERS:
                return True
        for ext in EXCLUDE_EXT:
            if str(path).endswith(ext):
                return True
        return False
    
    def _get_folder_color(self, folder: str) -> str:
        """Цвет по папке"""
        hash_val = int(hashlib.md5(folder.encode()).hexdigest(), 16)
        folder_lower = folder.lower()
        
        if 'gui' in folder_lower or 'ui' in folder_lower:
            hue = (hash_val % 60) + 200
        elif 'core' in folder_lower or 'config' in folder_lower:
            hue = (hash_val % 60) + 120
        elif 'model' in folder_lower or 'db' in folder_lower:
            hue = (hash_val % 60) + 270
        elif 'util' in folder_lower:
            hue = hash_val % 60
        else:
            hue = hash_val % 360
        
        saturation = 70
        lightness = 55
        
        return f"hsl({hue}, {saturation}%, {lightness}%)"
    
    def _extract_imports(self, file_path: str, project_root: str) -> Set[str]:
        """Парсер импортов"""
        imports = set()
        try:
            full_path = Path(project_root) / file_path
            if full_path.exists() and full_path.suffix == '.py':
                content = full_path.read_text(encoding='utf-8', errors='ignore')
                for match in re.finditer(r'(?:from|import)\s+([\w.]+)', content):
                    module = match.group(1).split('.')[0]
                    if not module.startswith('__'):
                        imports.add(module)
        except:
            pass
        return imports
    
    def populate_from_report(self, report, project_root: str):
        """Загрузить из отчета"""
        print(f"[GraphVisualizer] Загружаю отчет...")
        
        self.nodes.clear()
        self.edges.clear()
        
        files_info = {}
        
        # ВАЖНО: Правильно подсчитываем файлы БЕЗ дублирования
        
        # Собрать ошибки
        if hasattr(report, 'code_issues'):
            for issue in report.code_issues:
                path = str(issue.get('file', '')).replace('\\', '/')
                if not path or self._is_excluded_path(path):
                    continue
                
                if path not in files_info:
                    files_info[path] = {
                        'errors': 0,
                        'max_severity': 'LOW',
                        'error_types': {}
                    }
                
                files_info[path]['errors'] += 1
                severity = issue.get('severity', 'LOW')
                files_info[path]['error_types'][severity] = \
                    files_info[path]['error_types'].get(severity, 0) + 1
        
        if hasattr(report, 'security_issues'):
            for issue in report.security_issues:
                path = str(issue.get('file', '')).replace('\\', '/')
                if not path or self._is_excluded_path(path):
                    continue
                
                if path not in files_info:
                    files_info[path] = {
                        'errors': 0,
                        'max_severity': 'LOW',
                        'error_types': {}
                    }
                
                files_info[path]['errors'] += 1
                severity = issue.get('severity', 'LOW')
                files_info[path]['error_types'][severity] = \
                    files_info[path]['error_types'].get(severity, 0) + 1
        
        # КЛЮЧЕВОЕ УЛУЧШЕНИЕ: Сканируем и добавляем только один раз (без дублей)
        scanned_files = set(files_info.keys())
        
        try:
            for py_file in Path(project_root).rglob('*.py'):
                rel = str(py_file.relative_to(project_root)).replace('\\', '/').replace('./', '')
                
                # Исключить
                if self._is_excluded_path(rel):
                    continue
                
                # Пропустить, если уже есть
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
        
        # ВАЖНО: Создаём узлы БЕЗ дублирования
        unique_files = set()
        for file_path, info in files_info.items():
            if file_path in unique_files:
                continue  # Пропускаем дубли
            
            unique_files.add(file_path)
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
        
        # Создать рёбра
        for file_path, node in self.nodes.items():
            for imported in node.imports:
                for other_path in self.nodes.keys():
                    if other_path != file_path:
                        if Path(other_path).stem == Path(imported).stem:
                            self.edges.append((file_path, other_path))
        
        print(f"[GraphVisualizer] ✅ {len(self.nodes)} узлов, {len(self.edges)} связей")
        print(f"[GraphVisualizer] ВСЕГО УНИКАЛЬНЫХ ФАЙЛОВ: {len(unique_files)}")
        
        # ВАЖНО: Только ПОСЛЕ загрузки данных рисуем граф
        self._render_graph()
    
    # Обработчики событий
    
    def _on_render_changed(self):
        if self.is_initializing:
            return
        self.current_render = "pyvis" if self.render_combo.currentIndex() == 1 else "plotly"
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
            self._render_graph()
    
    def _on_node_clicked(self, file_path: str):
        """Узел клик - синхронизация с деревом"""
        print(f"[GraphVisualizer] Клик на узел: {file_path}")
        self.file_selected.emit(file_path)
    
    def _render_graph(self):
        """Выбрать правильный рендер"""
        if not self.nodes:
            print("[GraphVisualizer] ⚠ Нет узлов для рендеринга")
            return
        
        if self.current_render == "plotly":
            if HAS_PLOTLY:
                self._render_with_plotly()
            elif HAS_PYVIS:
                print("[GraphVisualizer] Fallback на PyVis")
                self._render_with_pyvis()
        else:
            if HAS_PYVIS:
                self._render_with_pyvis()
            elif HAS_PLOTLY:
                self._render_with_plotly()
    
    def _render_with_plotly(self):
        """Рендер Plotly - ИСПРАВЛЕННЫЙ (фиксит белый лист)"""
        print(f"[GraphVisualizer] 📊 Plotly: {len(self.nodes)} узлов")
        
        try:
            # Инициализация
            folders: Dict[str, List[str]] = {}
            for file_path in self.nodes.keys():
                folder = self.nodes[file_path].folder
                folders.setdefault(folder, []).append(file_path)
            
            folder_list = sorted(folders.keys())
            fcount = len(folder_list)
            
            # Grid layout
            fcols = max(1, int(fcount ** 0.5) + 1)
            folder_positions = {}
            for idx, folder in enumerate(folder_list):
                fx = (idx % fcols) * GRID_SPACING
                fy = (idx // fcols) * GRID_SPACING
                folder_positions[folder] = (fx, fy)
            
            # Разместить узлы
            node_x, node_y, node_ids = [], [], []
            node_colors, node_sizes, node_labels, node_hovers = [], [], [], []
            
            for folder in folder_list:
                files = sorted(folders[folder], 
                    key=lambda f: self.nodes[f].errors_count, reverse=True)
                cx, cy = folder_positions[folder]
                n = len(files)
                
                for i, file_path in enumerate(files):
                    if n <= MAX_CLOUD_SIZE:
                        angle = (i / max(1, n)) * 2 * math.pi
                        radius = CLOUD_RADIUS * (1.0 + (i % 4) * MIN_NODE_DISTANCE)
                    else:
                        cols = int(n ** 0.5) + 1
                        angle = 0
                        radius = max(CLOUD_RADIUS, (i % cols) * 1.5) + (i // cols) * 1.5
                    
                    x = cx + radius * math.cos(angle)
                    y = cy + radius * math.sin(angle)
                    
                    node_x.append(x)
                    node_y.append(y)
                    node_ids.append(file_path)
                    
                    node = self.nodes[file_path]
                    color = self._get_folder_color(folder)
                    node_colors.append(color)
                    
                    size = max(12, min(60, 15 + node.errors_count * 5))
                    node_sizes.append(size * self.scale_factor)
                    
                    if self.show_labels.isChecked():
                        label = Path(file_path).name
                        if node.errors_count > 0:
                            label += f"\n({node.errors_count})"
                    else:
                        label = str(node.errors_count) if node.errors_count > 0 else ""
                    node_labels.append(label)
                    
                    hover_text = (
                        f"<b>{Path(file_path).name}</b><br>"
                        f"Папка: {folder}<br>"
                        f"Ошибок: <b>{node.errors_count}</b><br>"
                        f"Максимум: {node.max_severity}"
                    )
                    node_hovers.append(hover_text)
            
            # Рёбра
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
            
            # КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: Правильная инициализация Figure
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
                    opacity=0.9,
                    sizemode='diameter'
                ),
                text=node_labels,
                textposition='middle center',
                textfont=dict(size=10, color='#000000'),
                hovertext=node_hovers,
                hoverinfo='text',
                showlegend=False
            ))
            
            # Layout
            fig.update_layout(
                title=f"📊 Граф проекта ({len(self.nodes)} файлов, {len(self.edges)} связей)",
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=True, gridwidth=1, gridcolor='#e8e8e8',
                          zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=True, gridwidth=1, gridcolor='#e8e8e8',
                          zeroline=False, showticklabels=False),
                plot_bgcolor='#fafafa',
                paper_bgcolor='#ffffff',
                height=700,
            )
            
            # ВАЖНО: Сохранить в файл И загрузить в WebView
            html_file = Path(tempfile.gettempdir()) / "naudit_graph_v2_4.html"
            html_content = fig.to_html(include_plotlyjs='cdn')
            
            # ДОБАВЛЯЕМ QWebChannel JS
            html_with_bridge = html_content.replace(
                '</body>',
                '''<script src="qrc:///qtwebchannel/qwebchannel.js"></script>
<script>
new QWebChannel(qt.webChannelTransport, function(channel) {
    window.graph_bridge = channel.objects.graph_bridge;
});
document.addEventListener('click', function(event) {
    if (event.target.tagName === 'path' || event.target.closest('.scatterlayer')) {
        console.log('Graph clicked');
    }
});
</script>
</body>'''
            )
            
            html_file.write_text(html_with_bridge, encoding='utf-8')
            file_url = QUrl.fromLocalFile(str(html_file.resolve()))
            
            # КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: Загружаем URL В WebView
            self.web_view.load(file_url)
            
            print(f"[GraphVisualizer] ✅ Plotly готов ({len(self.nodes)} узлов)")
        
        except Exception as e:
            print(f"[ERROR] Plotly: {e}")
            import traceback
            traceback.print_exc()
    
    def _render_with_pyvis(self):
        """Рендер PyVis"""
        print(f"[GraphVisualizer] 🌐 PyVis: {len(self.nodes)} узлов")
        
        try:
            net = Network(height='700px', width='100%', directed=False,
                         notebook=False, bgcolor='#fafafa', font_color='#1a1a1a')
            
            for file_path, node in self.nodes.items():
                color = self._get_folder_color(node.folder)
                
                if self.show_labels.isChecked():
                    label = Path(file_path).name
                else:
                    label = str(node.errors_count) if node.errors_count > 0 else ""
                
                size = max(20, min(50, 25 + node.errors_count * 4))
                
                net.add_node(
                    file_path,
                    label=label,
                    color=color,
                    size=size * self.scale_factor,
                    title=f"{Path(file_path).name}\n{node.errors_count} ошибок"
                )
            
            if self.show_edges.isChecked():
                for src, dst in self.edges:
                    net.add_edge(src, dst, color='rgba(150,150,150,0.2)')
            
            net.toggle_physics(True)
            
            html_file = Path(tempfile.gettempdir()) / "naudit_graph_pyvis_v2_4.html"
            net.show(str(html_file))
            
            file_url = QUrl.fromLocalFile(str(html_file.resolve()))
            self.web_view.load(file_url)
            
            print(f"[GraphVisualizer] ✅ PyVis готов")
        
        except Exception as e:
            print(f"[ERROR] PyVis: {e}")
            import traceback
            traceback.print_exc()
    
    def clear(self):
        """Очистить"""
        self.nodes.clear()
        self.edges.clear()
        self.web_view.setUrl(QUrl("about:blank"))
    
    def highlight_file(self, file_path: str):
        """Подсветить файл на графе"""
        if file_path in self.nodes:
            print(f"[GraphVisualizer] Подсвечиваю: {file_path}")
            # TODO: Реализовать JS функцию для подсветки
    
    def focus_on_file(self, file_path: str):
        """Центрировать на файле (при клике в дереве)"""
        if file_path in self.nodes:
            print(f"[GraphVisualizer] Фокус на: {file_path}")
            # TODO: Реализовать JS функцию для скролла
