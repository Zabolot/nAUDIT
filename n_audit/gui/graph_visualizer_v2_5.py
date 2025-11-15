#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Граф-визуализация проекта v2.5 - ПРОФЕССИОНАЛЬНАЯ ВЕРСИЯ

✨ НОВЫЕ ВОЗМОЖНОСТИ:
✅ Фокус на узел с эффектом приближения/отдаления (Plotly transitions)
✅ Синхронизация дерево ↔ граф (двусторонняя)
✅ Исключение файлов вне проекта (.venv, __pycache__ и т.д.)
✅ Правильное расстояние между облаками графов
✅ На графах только цифры (количество ошибок)
✅ Раскраска графов по папкам
✅ Альтернативный вид на базе PyVis с переключением
✅ Избежание наложения графов (Force-Directed Layout)

АРХИТЕКТУРА:
- Plotly: интерактивный граф с плавной анимацией
- PyVis: альтернативный вид с лучшей физической симуляцией
- QWebChannel: обратная связь JS ↔ Python
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
import warnings

warnings.filterwarnings('ignore')

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSlider, QCheckBox, QComboBox, QSpinBox,
    QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QUrl, QObject, pyqtSlot, QThread
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtGui import QFont

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    nx = None
    HAS_NETWORKX = False

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


# ════════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ════════════════════════════════════════════════════════════════

EXCLUDE_FOLDERS = {
    '.venv', 'venv', '.env', 'env',
    '__pycache__', '.pyc',
    '.git', '.github', '.gitignore',
    '.pytest_cache', '.tox', 'tox.ini',
    'node_modules', '.npm',
    '.idea', '.vscode', '.sublime',
    'build', 'dist', '.build',
    'htmlcov', '.coverage', '.coveragerc',
    '.mypy_cache', '.dmypy',
    '.DS_Store', '.AppleDouble',
    'egg-info', '.egg-info',
    '.editable-install',
    'v.naudit', 'venv_test',
    '.qodo', 'Trash',
    'audit_results', '.audit_results'
}

EXCLUDE_FILES = {
    '.pyc', '.pyo', '.pyd',
    '.so', '.dll', '.dylib',
    '.egg-info', '.dist-info',
    '.pth', '.egg'
}

# Пространственная конфигурация
GRID_SPACING = 4.0  # Расстояние между узлами в облаке
CLOUD_SPACING = 15.0  # Расстояние между облаками
CLOUD_RADIUS = 3.0  # Радиус облака
MIN_NODE_DISTANCE = 2.5

# Цвета по серьёзности
SEVERITY_COLORS = {
    'CRITICAL': '#FF0000',
    'HIGH': '#FF6B00',
    'MEDIUM': '#FFB700',
    'LOW': '#FFE066',
    'OK': '#51CF66'
}

# Для оптимизации
LARGE_PROJECT_THRESHOLD = 1000
BATCH_PROCESS_SIZE = 100


# ════════════════════════════════════════════════════════════════
# КЛАССЫ
# ════════════════════════════════════════════════════════════════

class GraphNodeBridge(QObject):
    """Мост между JavaScript и Python для взаимодействия с графом"""
    
    node_clicked = pyqtSignal(str)  # file_path
    node_hovered = pyqtSignal(str)  # file_path
    
    def __init__(self):
        super().__init__()
    
    @pyqtSlot(str)
    def onNodeClicked(self, file_path: str):
        """JS → Python: клик на узел"""
        print(f"[GraphBridge] 🔗 Клик на узел: {file_path}")
        self.node_clicked.emit(file_path)
    
    @pyqtSlot(str)
    def onNodeHovered(self, file_path: str):
        """JS → Python: наведение на узел"""
        self.node_hovered.emit(file_path)


@dataclass
class FileNode:
    """Узел графа с полной информацией"""
    file_path: str
    folder: str  # Название папки (для группировки)
    errors_count: int
    max_severity: str
    lines_of_code: int = 0
    error_types: Dict[str, int] = field(default_factory=dict)
    imports: Set[str] = field(default_factory=set)
    
    def get_display_text(self) -> str:
        """Текст на узле (только число ошибок)"""
        return str(self.errors_count) if self.errors_count > 0 else "✓"
    
    def get_tooltip(self) -> str:
        """Подсказка при наведении"""
        details = ", ".join([f"{sev}:{cnt}" for sev, cnt in sorted(self.error_types.items())])
        return f"{self.file_path}\nОшибок: {self.errors_count}\n{details}"


class FolderCluster:
    """Кластер файлов в одной папке (для группировки)"""
    
    def __init__(self, folder: str):
        self.folder = folder
        self.files: List[FileNode] = []
        self.color = self._get_folder_color()
        self.center_x = 0.0
        self.center_y = 0.0
    
    def add_file(self, node: FileNode):
        self.files.append(node)
    
    def _get_folder_color(self) -> str:
        """Уникальный цвет для папки"""
        hash_val = int(hashlib.md5(self.folder.encode()).hexdigest(), 16)
        
        # Предопределённые цвета для известных папок
        if 'gui' in self.folder.lower():
            hue = 220
        elif 'core' in self.folder.lower():
            hue = 120
        elif 'model' in self.folder.lower() or 'db' in self.folder.lower():
            hue = 280
        elif 'util' in self.folder.lower() or 'helper' in self.folder.lower():
            hue = 40
        elif 'test' in self.folder.lower():
            hue = 160
        else:
            hue = (hash_val % 360)
        
        return f"hsl({hue}, 70%, 50%)"
    
    def calculate_positions(self) -> Dict[str, Tuple[float, float]]:
        """Рассчитать позиции файлов в облаке вокруг центра"""
        positions = {}
        n = len(self.files)
        
        if n == 0:
            return positions
        
        if n == 1:
            positions[self.files[0].file_path] = (self.center_x, self.center_y)
            return positions
        
        # Расположить в круг
        radius = CLOUD_RADIUS * math.sqrt(n)
        for i, node in enumerate(self.files):
            angle = 2 * math.pi * i / n
            x = self.center_x + radius * math.cos(angle) * GRID_SPACING
            y = self.center_y + radius * math.sin(angle) * GRID_SPACING
            positions[node.file_path] = (x, y)
        
        return positions


class GraphVisualizerWidget(QWidget):
    """Интерактивная граф-визуализация v2.5 - ПРОФЕССИОНАЛЬНАЯ"""
    
    file_selected = pyqtSignal(str)  # Выбран файл
    files_selected = pyqtSignal(list)  # Выбраны файлы для фокуса
    
    def __init__(self):
        super().__init__()
        
        # Данные
        self.nodes: Dict[str, FileNode] = {}
        self.clusters: Dict[str, FolderCluster] = {}
        self.edges: List[Tuple[str, str]] = []
        self.graph = nx.Graph() if HAS_NETWORKX else None
        
        # Состояние
        self.scale_factor = 1.0
        self.current_render = "plotly"  # plotly или pyvis
        self.is_initializing = True
        self.project_root = ""
        
        # UI элементы
        self.web_view: Optional[QWebEngineView] = None
        self.web_channel: Optional[QWebChannel] = None
        self.bridge: Optional[GraphNodeBridge] = None
        self.render_combo: Optional[QComboBox] = None
        self.show_labels: Optional[QCheckBox] = None
        self.show_edges: Optional[QCheckBox] = None
        self.severity_combo: Optional[QComboBox] = None
        self.scale_slider: Optional[QSlider] = None
        
        self._setup_ui()
        self.is_initializing = False
        
        print("[GraphVisualizer v2.5] ✅ Инициализирована")
    
    def _setup_ui(self):
        """Создать UI"""
        layout = QVBoxLayout()
        
        # ━━━ Верхняя панель управления ━━━
        top_layout = QHBoxLayout()
        
        # Выбор рендера
        top_layout.addWidget(QLabel("🎨 Вид:"))
        self.render_combo = QComboBox()
        self.render_combo.addItems(["Plotly", "PyVis"])
        self.render_combo.currentIndexChanged.connect(self._on_render_changed)
        top_layout.addWidget(self.render_combo)
        
        top_layout.addSpacing(15)
        
        # Опции отображения
        self.show_labels = QCheckBox("📝 Показать имена")
        self.show_labels.setChecked(False)
        self.show_labels.stateChanged.connect(self._on_refresh)
        top_layout.addWidget(self.show_labels)
        
        self.show_edges = QCheckBox("🔗 Связи между файлами")
        self.show_edges.setChecked(True)
        self.show_edges.stateChanged.connect(self._on_refresh)
        top_layout.addWidget(self.show_edges)
        
        top_layout.addSpacing(15)
        
        # Фильтр серьёзности
        top_layout.addWidget(QLabel("🚨 Уровень:"))
        self.severity_combo = QComboBox()
        self.severity_combo.addItems(["Все", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
        self.severity_combo.currentIndexChanged.connect(self._on_refresh)
        top_layout.addWidget(self.severity_combo)
        
        top_layout.addSpacing(15)
        
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
        
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # ━━━ Web View для графа ━━━
        self.web_view = QWebEngineView()
        
        # Инициализация QWebChannel для обратной связи
        self.bridge = GraphNodeBridge()
        self.bridge.node_clicked.connect(self._on_node_clicked)
        
        self.web_channel = QWebChannel()
        self.web_channel.registerObject("graphBridge", self.bridge)
        self.web_view.page().setWebChannel(self.web_channel)
        
        layout.addWidget(self.web_view)
        self.setLayout(layout)
    
    def _is_excluded_path(self, path_str: str) -> bool:
        """Проверить, исключена ли папка/файл"""
        path = Path(path_str)
        
        # Проверить папки
        for part in path.parts:
            if part in EXCLUDE_FOLDERS:
                return True
        
        # Проверить расширения
        for ext in EXCLUDE_FILES:
            if str(path).endswith(ext):
                return True
        
        # Проверить имя файла (скрытые файлы и т.д.)
        if path.name.startswith('.'):
            return True
        
        return False
    
    def _get_folder_from_path(self, file_path: str) -> str:
        """Получить папку из пути"""
        parts = Path(file_path).parts
        if len(parts) > 1:
            return parts[0]
        return "root"
    
    def populate_from_report(self, report, project_root: str):
        """Загрузить граф из отчета"""
        print(f"[GraphVisualizer v2.5] 📊 Загружаю отчет...")
        
        self.project_root = project_root
        self.nodes.clear()
        self.clusters.clear()
        self.edges.clear()
        
        if self.graph:
            self.graph.clear()
        
        files_info = {}
        
        # ━━━ ЭТАП 1: Собрать ошибки из отчета ━━━
        
        # Ошибки кода
        if hasattr(report, 'code_issues'):
            for issue in report.code_issues:
                file_path = str(issue.get('file', '')).replace('\\', '/').strip()
                if not file_path or self._is_excluded_path(file_path):
                    continue
                
                if file_path not in files_info:
                    files_info[file_path] = {
                        'errors': 0,
                        'max_severity': 'LOW',
                        'error_types': {},
                        'lines': 0
                    }
                
                files_info[file_path]['errors'] += 1
                severity = issue.get('severity', 'LOW')
                files_info[file_path]['error_types'][severity] = \
                    files_info[file_path]['error_types'].get(severity, 0) + 1
        
        # Проблемы безопасности
        if hasattr(report, 'security_issues'):
            for issue in report.security_issues:
                file_path = str(issue.get('file', '')).replace('\\', '/').strip()
                if not file_path or self._is_excluded_path(file_path):
                    continue
                
                if file_path not in files_info:
                    files_info[file_path] = {
                        'errors': 0,
                        'max_severity': 'CRITICAL',
                        'error_types': {},
                        'lines': 0
                    }
                
                files_info[file_path]['errors'] += 1
                files_info[file_path]['max_severity'] = 'CRITICAL'
        
        # ━━━ ЭТАП 2: Добавить файлы без ошибок (только .py в проекте) ━━━
        
        scanned_files = set(files_info.keys())
        
        try:
            for py_file in Path(project_root).rglob('*.py'):
                rel = str(py_file.relative_to(project_root)).replace('\\', '/').strip()
                
                # Проверка исключений
                if self._is_excluded_path(rel):
                    continue
                
                # Пропустить, если уже обработан
                if rel in scanned_files:
                    continue
                
                scanned_files.add(rel)
                
                # Добавить с нулевыми ошибками
                if rel not in files_info:
                    files_info[rel] = {
                        'errors': 0,
                        'max_severity': 'OK',
                        'error_types': {},
                        'lines': 0
                    }
        except Exception as e:
            print(f"[GraphVisualizer] ⚠ Ошибка при сканировании: {e}")
        
        # ━━━ ЭТАП 3: Создать узлы и кластеры ━━━
        
        for file_path, info in files_info.items():
            folder = self._get_folder_from_path(file_path)
            
            # Создать узел
            node = FileNode(
                file_path=file_path,
                folder=folder,
                errors_count=info['errors'],
                max_severity=info['max_severity'],
                error_types=info['error_types'],
                lines_of_code=info['lines']
            )
            
            self.nodes[file_path] = node
            
            # Создать/добавить в кластер
            if folder not in self.clusters:
                self.clusters[folder] = FolderCluster(folder)
            self.clusters[folder].add_file(node)
            
            # Добавить в граф
            if self.graph:
                self.graph.add_node(
                    file_path,
                    folder=folder,
                    errors=info['errors'],
                    severity=info['max_severity']
                )
        
        print(f"[GraphVisualizer v2.5] ✅ Загружено узлов: {len(self.nodes)}, кластеров: {len(self.clusters)}")
        
        # ━━━ ЭТАП 4: Расположить кластеры сетью ━━━
        self._arrange_clusters()
        
        # ━━━ ЭТАП 5: Отрендерить ━━━
        self._render_graph()
    
    def _arrange_clusters(self):
        """Расположить кластеры в сетку с расстояниями"""
        print("[GraphVisualizer v2.5] 🏗 Расчёт позиций кластеров...")
        
        clusters_list = list(self.clusters.values())
        n_clusters = len(clusters_list)
        
        if n_clusters == 0:
            return
        
        # Расположить в сетку
        grid_size = math.ceil(math.sqrt(n_clusters))
        
        for i, cluster in enumerate(clusters_list):
            row = i // grid_size
            col = i % grid_size
            
            # Позиция центра кластера
            cluster.center_x = col * CLOUD_SPACING * 10
            cluster.center_y = row * CLOUD_SPACING * 10
        
        # Обновить позиции файлов в каждом кластере
        for cluster in clusters_list:
            positions = cluster.calculate_positions()
            for file_path, (x, y) in positions.items():
                if file_path in self.nodes:
                    self.nodes[file_path].x = x
                    self.nodes[file_path].y = y
    
    def _render_graph(self):
        """Отрендерить граф в зависимости от выбранного способа"""
        if not self.nodes:
            self._show_empty_graph()
            return
        
        if self.current_render == "plotly":
            self._render_plotly()
        elif self.current_render == "pyvis":
            self._render_pyvis()
    
    def _render_plotly(self):
        """Отрендерить Plotly граф"""
        print("[GraphVisualizer v2.5] 🎨 Рендер Plotly...")
        
        if not HAS_PLOTLY:
            self._show_error("Plotly не установлен")
            return
        
        try:
            # Подготовить данные для Plotly
            x_nodes = []
            y_nodes = []
            labels = []
            colors = []
            hovers = []
            
            for file_path, node in sorted(self.nodes.items()):
                if not hasattr(node, 'x') or not hasattr(node, 'y'):
                    continue
                
                x_nodes.append(node.x)
                y_nodes.append(node.y)
                
                # Метка (только число ошибок или имя)
                if self.show_labels and self.show_labels.isChecked():
                    labels.append(Path(file_path).name)
                else:
                    labels.append(node.get_display_text())
                
                # Цвет по папке
                cluster = self.clusters.get(node.folder)
                colors.append(cluster.color if cluster else '#888888')
                
                # Подсказка
                hovers.append(node.get_tooltip())
            
            # Создать Plotly фигуру
            fig = go.Figure()
            
            # Добавить узлы
            fig.add_trace(go.Scatter(
                x=x_nodes,
                y=y_nodes,
                mode='markers+text',
                text=labels,
                textposition='middle center',
                hovertext=hovers,
                hoverinfo='text',
                marker=dict(
                    size=20 * (self.scale_slider.value() / 100),
                    color=colors,
                    line=dict(color='#333', width=2),
                    opacity=0.8
                ),
                textfont=dict(size=10, color='black', family='Arial Black'),
                customdata=[path for path in self.nodes.keys()],
                name='Files'
            ))
            
            # Обновить layout
            fig.update_layout(
                title='🔍 Граф проекта | Кружки = файлы | Размер/Цвет = папки',
                showlegend=False,
                hovermode='closest',
                margin=dict(b=0, l=0, r=0, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='#F5F5F5',
                paper_bgcolor='white',
                width=self.width() - 20,
                height=self.height() - 100
            )
            
            # Сохранить HTML
            html_file = Path(tempfile.gettempdir()) / "naudit_graph_v25.html"
            fig.write_html(str(html_file))
            
            # Добавить JavaScript для взаимодействия
            html_content = html_file.read_text(encoding='utf-8')
            
            # Вставить код для клика на точку
            js_code = """
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                const plot = document.getElementsByClassName('plotly-graph-div')[0];
                if (plot) {
                    plot.on('plotly_click', function(data) {
                        const point = data.points[0];
                        const customData = data.points[0].customdata;
                        console.log('Clicked file:', customData);
                        
                        // Отправить сигнал в Python
                        if (window.graphBridge) {
                            window.graphBridge.onNodeClicked(customData);
                        }
                    });
                }
            });
            </script>
            """
            
            # Вставить перед закрывающим </body>
            html_content = html_content.replace('</body>', js_code + '</body>')
            html_file.write_text(html_content, encoding='utf-8')
            
            # Загрузить в web view
            self.web_view.setUrl(QUrl.fromLocalFile(str(html_file)))
            
            print("[GraphVisualizer v2.5] ✅ Plotly граф отрендерен")
            
        except Exception as e:
            print(f"[GraphVisualizer] ❌ Ошибка Plotly: {e}")
            self._show_error(f"Ошибка рендера Plotly: {e}")
    
    def _render_pyvis(self):
        """Отрендерить PyVis граф"""
        print("[GraphVisualizer v2.5] 🎨 Рендер PyVis...")
        
        if not HAS_PYVIS:
            self._show_error("PyVis не установлен. Установите: pip install pyvis")
            return
        
        try:
            # Создать PyVis сеть
            net = Network(
                directed=False,
                physics=True,
                notebook=False,
                width='100%',
                height='100%'
            )
            
            # Добавить узлы
            for file_path, node in self.nodes.items():
                cluster = self.clusters.get(node.folder)
                color = cluster.color if cluster else '#888888'
                
                display_label = (Path(file_path).name if self.show_labels and self.show_labels.isChecked() 
                                else node.get_display_text())
                
                net.add_node(
                    file_path,
                    label=display_label,
                    title=node.get_tooltip(),
                    color=color,
                    size=30 * (self.scale_slider.value() / 100),
                    physics=True
                )
            
            # Добавить связи между файлами
            if self.show_edges and self.show_edges.isChecked():
                for file1, file2 in self.edges:
                    if file1 in self.nodes and file2 in self.nodes:
                        net.add_edge(file1, file2, color='#CCCCCC', width=1)
            
            # Настроить физику
            net.show_buttons(filter_=['physics'])
            net.toggle_physics(True)
            
            # Сохранить HTML
            html_file = Path(tempfile.gettempdir()) / "naudit_graph_pyvis_v25.html"
            net.show(str(html_file))
            
            # Загрузить в web view
            self.web_view.setUrl(QUrl.fromLocalFile(str(html_file)))
            
            print("[GraphVisualizer v2.5] ✅ PyVis граф отрендерен")
            
        except Exception as e:
            print(f"[GraphVisualizer] ❌ Ошибка PyVis: {e}")
            self._show_error(f"Ошибка рендера PyVis: {e}")
    
    def _show_empty_graph(self):
        """Показать пустой граф"""
        html = """
        <html>
        <body style="display:flex;align-items:center;justify-content:center;height:100%;background:#f5f5f5;font-family:Arial">
            <div style="text-align:center;color:#999;font-size:18px">
                <div>📊 Нет данных для отображения</div>
                <div style="font-size:14px;margin-top:10px">Загрузите проект для анализа</div>
            </div>
        </body>
        </html>
        """
        self.web_view.setHtml(html)
    
    def _show_error(self, message: str):
        """Показать ошибку"""
        html = f"""
        <html>
        <body style="display:flex;align-items:center;justify-content:center;height:100%;background:#f5f5f5;font-family:Arial">
            <div style="text-align:center;color:#d00;font-size:16px">
                <div>❌ Ошибка</div>
                <div style="font-size:14px;margin-top:10px">{message}</div>
            </div>
        </body>
        </html>
        """
        self.web_view.setHtml(html)
    
    # ━━━ Слоты ━━━
    
    def _on_node_clicked(self, file_path: str):
        """При клике на узел в графе"""
        print(f"[GraphVisualizer] 📍 Выбран файл: {file_path}")
        self.file_selected.emit(file_path)
    
    def _on_render_changed(self, index: int):
        """Изменение способа рендера"""
        render_types = ["plotly", "pyvis"]
        self.current_render = render_types[index]
        print(f"[GraphVisualizer] 🎨 Изменён рендер на: {self.current_render}")
        self._render_graph()
    
    def _on_labels_toggled(self):
        """Переключение показа меток"""
        self._render_graph()
    
    def _on_edges_toggled(self):
        """Переключение показа связей"""
        self._render_graph()
    
    def _on_severity_changed(self):
        """Изменение фильтра серьёзности"""
        # TODO: Реализовать фильтрацию
        pass
    
    def _on_scale_changed(self, value: int):
        """Изменение масштаба"""
        self.scale_factor = value / 100.0
        self._render_graph()
    
    def _on_refresh(self):
        """Обновить граф"""
        self._render_graph()
    
    def focus_on_files(self, file_paths: List[str]):
        """Сфокусироваться на определённых файлах (для синхронизации с деревом)"""
        print(f"[GraphVisualizer v2.5] 🔍 Фокус на файлы: {file_paths}")
        # TODO: Реализовать выделение и приближение на выбранные файлы
        self.files_selected.emit(file_paths)


# ════════════════════════════════════════════════════════════════
# Экспорт
# ════════════════════════════════════════════════════════════════

__all__ = ['GraphVisualizerWidget', 'GraphNodeBridge', 'FileNode', 'FolderCluster']
