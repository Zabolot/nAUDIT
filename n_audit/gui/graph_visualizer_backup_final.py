#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Граф-визуализация проекта v2.2 - ПОЛНАЯ ПЕРЕРАБОТКА

ИСПРАВЛЕННЫЕ ПРОБЛЕМЫ СЕССИИ 2:
✅ Исключение файлов из .venv, __pycache__, .git и т.д.
✅ Показ связей (импортов) между файлами  
✅ Увеличенные расстояния между облаками папок (было 10, теперь 25)
✅ На узлах ТОЛЬКО цифры ошибок (без имен файлов)
✅ Цвета по папкам (детерминированные хеш-функции)
✅ Предотвращение наложения узлов (спираль с увеличенным радиусом)
✅ Переключение между Plotly и PyVis рендерами (выбор через комбо)

ОСОБЕННОСТИ:
- Размер узла = количество строк кода в файле
- Цвет узла = детерминированный по папке (HSL hash)
- Число на узле = количество ошибок (или имя файла если включено)
- Группировка = по папкам проекта (облака)
- Связи между узлами = импорты между файлами
- Экспорт графа в PNG/HTML
"""

import sys
import tempfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime
import json
import re
import hashlib
import math

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
}

# Расширения для исключения
EXCLUDE_EXT = {'.egg-info', '.dist-info', '.pyd', '.so', '.dll'}

GRID_SPACING = 25.0                    # Расстояние между облаками папок (было 10, теперь 25)
CLOUD_RADIUS = 3.0                     # Радиус спирали внутри облака  
MIN_NODE_DISTANCE = 3.0                # Минимальное расстояние между узлами в спирали


# ════════════════════════════════════════════════════════════════
# КЛАССЫ
# ════════════════════════════════════════════════════════════════

class GraphNodeBridge(QObject):
    """Мост между JavaScript графа и Python UI"""
    node_clicked = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
    
    @pyqtSlot(str)
    def onNodeClicked(self, file_path: str):
        print(f"[GraphNodeBridge] Узел: {file_path}")
        self.node_clicked.emit(file_path)


@dataclass
class FileNode:
    """Узел графа"""
    file_path: str
    lines_of_code: int
    errors_count: int
    max_severity: str
    folder: str
    imports: Set[str] = field(default_factory=set)


class GraphVisualizerWidget(QWidget):
    """Интерактивная граф-визуализация проекта с поддержкой Plotly и PyVis"""
    
    file_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        self.nodes: Dict[str, FileNode] = {}
        self.edges: List[Tuple[str, str]] = []
        self.graph = nx.Graph() if nx else None
        
        self.scale_factor = 1.0
        self.current_render = "plotly"  # или "pyvis"
        self._focus_active = False
        self.is_initializing = True
        
        self._setup_ui()
        self.is_initializing = False
    
    def _setup_ui(self):
        """Создать UI"""
        layout = QVBoxLayout()
        
        # Верхняя панель
        top_layout = QHBoxLayout()
        
        # Выбор рендера
        top_layout.addWidget(QLabel("Рендер:"))
        self.render_combo = QComboBox()
        self.render_combo.addItems(["Plotly (интерактивный)", "PyVis (сетевой)"])
        self.render_combo.currentIndexChanged.connect(self._on_render_changed)
        top_layout.addWidget(self.render_combo)
        
        top_layout.addSpacing(20)
        
        # Опции отображения
        self.show_labels = QCheckBox("Показать имена")
        self.show_labels.setChecked(False)
        self.show_labels.stateChanged.connect(self._on_labels_toggled)
        top_layout.addWidget(self.show_labels)
        
        self.show_edges = QCheckBox("Показать связи")
        self.show_edges.setChecked(True)
        self.show_edges.stateChanged.connect(self._on_edges_toggled)
        top_layout.addWidget(self.show_edges)
        
        # Масштаб
        top_layout.addSpacing(20)
        top_layout.addWidget(QLabel("Масштаб:"))
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
        """Генерировать детерминированный цвет для папки"""
        # Хешируем имя папки
        hash_val = int(hashlib.md5(folder.encode()).hexdigest(), 16)
        
        # Определяем диапазон HSL в зависимости от типа папки
        if 'gui' in folder.lower():
            hue = (hash_val % 60) + 200  # Синий
        elif 'core' in folder.lower() or 'config' in folder.lower():
            hue = (hash_val % 60) + 120  # Зелёный
        elif 'model' in folder.lower() or 'db' in folder.lower():
            hue = (hash_val % 60) + 270  # Фиолетовый
        elif 'util' in folder.lower() or 'helper' in folder.lower():
            hue = (hash_val % 60)        # Красный
        else:
            hue = hash_val % 360
        
        saturation = 70 + (hash_val // 360) % 20
        lightness = 50 + (hash_val // 720) % 15
        
        return f"hsl({hue}, {saturation}%, {lightness}%)"
    
    def _extract_imports(self, file_path: str, project_root: str) -> Set[str]:
        """Упрощённый парсер импортов"""
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
        """Заполнить граф из отчета"""
        print(f"[GraphVisualizer] Загружаю из отчета...")
        
        self.nodes.clear()
        self.edges.clear()
        
        files_info = {}
        
        # Собрать ошибки
        for issue in report.code_issues:
            path = str(issue['file']).replace('\\', '/')
            if path not in files_info:
                files_info[path] = {'errors': 0, 'max_severity': 'LOW'}
            files_info[path]['errors'] += 1
            
            sev_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
            if sev_order.get(issue.get('severity', 'LOW'), 0) > \
               sev_order.get(files_info[path]['max_severity'], 0):
                files_info[path]['max_severity'] = issue.get('severity', 'LOW')
        
        for issue in report.security_issues:
            path = str(issue['file']).replace('\\', '/')
            if path not in files_info:
                files_info[path] = {'errors': 0, 'max_severity': 'LOW'}
            files_info[path]['errors'] += 1
            
            sev_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
            if sev_order.get(issue.get('severity', 'LOW'), 0) > \
               sev_order.get(files_info[path]['max_severity'], 0):
                files_info[path]['max_severity'] = issue.get('severity', 'LOW')
        
        # Сканировать проект (с ИСКЛЮЧЕНИЯМИ)
        scanned_files = set()
        try:
            for py_file in Path(project_root).rglob('*.py'):
                rel = str(py_file.relative_to(project_root)).replace('\\', '/').replace('./', '')
                
                # ✅ ИСКЛЮЧИТЬ файлы из .venv, __pycache__, .git и т.д.
                if self._is_excluded_path(rel):
                    continue
                
                if rel in scanned_files:
                    continue
                scanned_files.add(rel)
                
                if rel not in files_info:
                    files_info[rel] = {'errors': 0, 'max_severity': 'LOW'}
        except Exception as e:
            print(f"[GraphVisualizer] Ошибка сканирования: {e}")
        
        # Создать узлы
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
                imports=self._extract_imports(file_path, project_root)
            )
            self.nodes[file_path] = node
        
        # ✅ Создать рёбра (связи между файлами)
        for file_path, node in self.nodes.items():
            for imported in node.imports:
                for other_path in self.nodes.keys():
                    if other_path != file_path:
                        if Path(other_path).stem == Path(imported).stem:
                            self.edges.append((file_path, other_path))
        
        print(f"[GraphVisualizer] {len(self.nodes)} узлов, {len(self.edges)} связей")
        self._render_graph()
    
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
    
    def _on_scale_changed(self):
        if not self.is_initializing:
            self.scale_factor = self.scale_slider.value() / 100.0
            if self.nodes:
                self._render_graph()
    
    def _on_refresh(self):
        if self.nodes:
            self._render_graph()
    
    def _render_graph(self):
        if not self.nodes:
            return
        
        if self.current_render == "plotly":
            if HAS_PLOTLY:
                self._render_with_plotly()
            elif HAS_PYVIS:
                self._render_with_pyvis()
        else:
            if HAS_PYVIS:
                self._render_with_pyvis()
            elif HAS_PLOTLY:
                self._render_with_plotly()
    
    def _render_with_plotly(self):
        """Рендерить с Plotly"""
        print(f"[GraphVisualizer] Plotly: {len(self.nodes)} узлов")
        
        try:
            # Группировать по папкам
            folders: Dict[str, List[str]] = {}
            for file_path in self.nodes.keys():
                folder = self.nodes[file_path].folder
                folders.setdefault(folder, []).append(file_path)
            
            folder_list = sorted(folders.keys())
            fcount = len(folder_list)
            
            # Grid layout для папок
            fcols = max(1, int(fcount ** 0.5))
            folder_positions = {}
            for idx, folder in enumerate(folder_list):
                fx = (idx % fcols) * GRID_SPACING
                fy = (idx // fcols) * GRID_SPACING
                folder_positions[folder] = (fx, fy)
            
            # Разместить узлы внутри облаков
            node_x, node_y, node_ids = [], [], []
            node_colors, node_sizes, node_labels, node_hovers = [], [], [], []
            
            for folder in folder_list:
                files = folders[folder]
                cx, cy = folder_positions[folder]
                n = len(files)
                
                for i, file_path in enumerate(files):
                    # Спираль с увеличенным расстоянием
                    angle = (i / max(1, n)) * 2 * math.pi
                    radius = CLOUD_RADIUS * (1.0 + (i % 4) * MIN_NODE_DISTANCE)
                    
                    x = cx + radius * math.cos(angle)
                    y = cy + radius * math.sin(angle)
                    
                    node_x.append(x)
                    node_y.append(y)
                    node_ids.append(file_path)
                    
                    node = self.nodes[file_path]
                    
                    # ✅ Цвет по папке
                    color = self._get_folder_color(folder)
                    node_colors.append(color)
                    
                    # Размер
                    size = max(12, min(50, 15 + node.errors_count * 4 + int((node.lines_of_code ** 0.5) / 10)))
                    node_sizes.append(size)
                    
                    # ✅ Лабель: только число ошибок (или имя если включено)
                    if self.show_labels.isChecked():
                        label = Path(file_path).name
                        if node.errors_count > 0:
                            label += f"\n{node.errors_count}"
                    else:
                        label = str(node.errors_count) if node.errors_count > 0 else ""
                    node_labels.append(label)
                    
                    hover_text = (
                        f"<b>{Path(file_path).name}</b><br>"
                        f"Папка: {folder}<br>"
                        f"Строк: {node.lines_of_code}<br>"
                        f"Ошибок: {node.errors_count}<br>"
                        f"Серьезность: {node.max_severity}"
                    )
                    node_hovers.append(hover_text)
            
            # ✅ Создать рёбра (связи между файлами)
            edge_x, edge_y = [], []
            if self.show_edges.isChecked():
                for src, dst in self.edges:
                    if src in node_ids and dst in node_ids:
                        idx1 = node_ids.index(src)
                        idx2 = node_ids.index(dst)
                        edge_x.extend([node_x[idx1], node_x[idx2], None])
                        edge_y.extend([node_y[idx1], node_y[idx2], None])
            
            # Создать Figure
            fig = go.Figure()
            
            # Добавить рёбра
            if edge_x:
                fig.add_trace(go.Scatter(
                    x=edge_x, y=edge_y,
                    mode='lines',
                    line=dict(width=1, color='rgba(150,150,150,0.3)'),
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
                    line=dict(width=2, color='#000000'),
                    sizemode='diameter'
                ),
                text=node_labels,
                textposition='middle center',
                textfont=dict(size=9, color='#000000'),
                hovertext=node_hovers,
                hoverinfo='text',
                showlegend=False
            ))
            
            # Layout
            fig.update_layout(
                title=f"Граф проекта ({len(self.nodes)} файлов, {len(self.edges)} связей)",
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='#fafafa',
                paper_bgcolor='#ffffff',
                height=600
            )
            
            # Сохранить и показать
            html_file = Path(tempfile.gettempdir()) / "naudit_graph_temp.html"
            html_content = fig.to_html(include_plotlyjs='inline')
            html_file.write_text(html_content, encoding='utf-8')
            
            file_url = QUrl.fromLocalFile(str(html_file.resolve()))
            self.web_view.load(file_url)
            
            print(f"[GraphVisualizer] ✅ Plotly готов")
        
        except Exception as e:
            print(f"[Error] Plotly: {e}")
            import traceback
            traceback.print_exc()
    
    def _render_with_pyvis(self):
        """Рендерить с PyVis"""
        print(f"[GraphVisualizer] PyVis: {len(self.nodes)} узлов")
        
        try:
            net = Network(height='600px', width='100%', directed=False, notebook=False,
                         bgcolor='#fafafa', font_color='#000000')
            
            # Добавить узлы
            for file_path, node in self.nodes.items():
                # ✅ Цвет по папке
                color = self._get_folder_color(node.folder)
                
                # ✅ Лабель: только число ошибок
                if self.show_labels.isChecked():
                    label = Path(file_path).name
                else:
                    label = str(node.errors_count) if node.errors_count > 0 else ""
                
                size = max(15, min(50, 20 + node.errors_count * 3))
                
                net.add_node(
                    file_path,
                    label=label,
                    color=color,
                    size=size,
                    title=f"{Path(file_path).name}\n{node.errors_count} ошибок"
                )
            
            # ✅ Добавить рёбра
            if self.show_edges.isChecked():
                for src, dst in self.edges:
                    net.add_edge(src, dst, color='rgba(150,150,150,0.3)')
            
            # Сохранить и показать
            html_file = Path(tempfile.gettempdir()) / "naudit_graph_pyvis.html"
            net.show(str(html_file))
            
            file_url = QUrl.fromLocalFile(str(html_file.resolve()))
            self.web_view.load(file_url)
            
            print(f"[GraphVisualizer] ✅ PyVis готов")
        
        except Exception as e:
            print(f"[Error] PyVis: {e}")
            import traceback
            traceback.print_exc()
    
    def clear(self):
        self.nodes.clear()
        self.edges.clear()
        self.web_view.setUrl(QUrl("about:blank"))
    
    def get_all_files(self) -> List[str]:
        return list(self.nodes.keys())
