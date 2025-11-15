#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Улучшенная граф-визуализация проекта v2.2

УЛУЧШЕНИЯ:
- ✅ Исключение файлов из .venv, __pycache__, .git и т.д.
- ✅ Показ связей (импортов) между файлами
- ✅ Увеличенные расстояния между облаками папок
- ✅ Только цифры ошибок на узлах (без имен файлов)
- ✅ Цвета по папкам (детерминированные, не совпадают)
- ✅ Предотвращение наложения узлов (grid layout)
- ✅ Переключение между Plotly и PyVis рендерами
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

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSlider, QCheckBox, QComboBox, QSpinBox, QButtonGroup
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QUrl, QObject, pyqtSlot
from PyQt6.QtCore import QEvent
from PyQt6.QtWebEngineWidgets import QWebEngineView
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


# ════════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ════════════════════════════════════════════════════════════════

EXCLUDE_FOLDERS = {
    '.venv', 'venv', '.env',           # Виртуальные окружения
    '__pycache__', '.pyc', '.egg-info', # Python кэш
    '.git', '.github', '.gitignore',    # Git
    '.pytest_cache', '.tox',             # Тестирование
    'node_modules', '.npm',              # Node.js
    '.idea', '.vscode', '.sublime',     # IDE
    'build', 'dist', '.build',          # Сборка
    'htmlcov', '.coverage',             # Coverage отчеты
    '.mypy_cache', '.dmypy',            # MyPy кэш
}

EXCLUDE_FILES = {
    '.pyc', '.pyo', '.pyd',             # Python compiled
    '.so', '.dll', '.exe',              # Native
    '.egg-info', '.dist-info',          # Package info
}

FOLDER_COLORS = {
    # Цвета для разных типов папок (детерминированные по имени)
    # Будут генерироваться автоматически, это просто примеры
}

GRID_SPACING = 15.0                     # Расстояние между облаками папок
CLOUD_RADIUS = 3.0                      # Радиус внутри облака
MIN_NODE_DISTANCE = 2.0                 # Минимальное расстояние между узлами


# ════════════════════════════════════════════════════════════════
# КЛАССЫ
# ════════════════════════════════════════════════════════════════

@dataclass
class FileNode:
    """Узел графа (файл проекта)"""
    file_path: str
    lines_of_code: int
    errors_count: int
    max_severity: str
    folder: str
    imports: Set[str] = field(default_factory=set)


class GraphVisualizerWidget(QWidget):
    """Интерактивная граф-визуализация с Plotly и PyVis"""
    
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
        
        # Верхняя панель: выбор рендера и опции
        top_layout = QHBoxLayout()
        
        top_layout.addWidget(QLabel("Рендер:"))
        self.render_combo = QComboBox()
        self.render_combo.addItems(["Plotly (интерактивный)", "PyVis (сетевой)"])
        self.render_combo.currentIndexChanged.connect(self._on_render_changed)
        top_layout.addWidget(self.render_combo)
        
        top_layout.addSpacing(20)
        
        self.show_labels = QCheckBox("Показать имена файлов")
        self.show_labels.setChecked(False)
        self.show_labels.stateChanged.connect(self._on_labels_toggled)
        top_layout.addWidget(self.show_labels)
        
        self.show_edges = QCheckBox("Показать связи (импорты)")
        self.show_edges.setChecked(True)
        self.show_edges.stateChanged.connect(self._on_edges_toggled)
        top_layout.addWidget(self.show_edges)
        
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
        
        # Web view для отображения графа
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        self.setLayout(layout)
    
    def _is_excluded_path(self, path_str: str) -> bool:
        """Проверить, должна ли папка/файл быть исключена"""
        path = Path(path_str)
        
        # Проверить части пути
        for part in path.parts:
            if part in EXCLUDE_FOLDERS:
                return True
        
        # Проверить расширение
        for ext in EXCLUDE_FILES:
            if str(path).endswith(ext):
                return True
        
        return False
    
    def _get_folder_color(self, folder: str) -> str:
        """Генерировать детерминированный цвет для папки"""
        # Хешируем имя папки чтобы получить consistent цвет
        hash_val = int(hashlib.md5(folder.encode()).hexdigest(), 16)
        
        # Используем разные диапазоны HSL для разных типов папок
        if 'gui' in folder.lower():
            hue = (hash_val % 60) + 200  # Синий диапазон
        elif 'core' in folder.lower():
            hue = (hash_val % 60) + 120  # Зелёный диапазон
        elif 'model' in folder.lower():
            hue = (hash_val % 60) + 270  # Фиолетовый диапазон
        else:
            hue = hash_val % 360
        
        saturation = 70 + (hash_val // 360) % 20
        lightness = 50 + (hash_val // 720) % 20
        
        return f"hsl({hue}, {saturation}%, {lightness}%)"
    
    def _extract_imports(self, file_path: str, project_root: str) -> Set[str]:
        """Извлечь импорты из файла (упрощенный парсер)"""
        imports = set()
        try:
            full_path = Path(project_root) / file_path
            if full_path.exists() and full_path.suffix == '.py':
                content = full_path.read_text(encoding='utf-8', errors='ignore')
                
                # Найти import statements
                for match in re.finditer(r'(?:from|import)\s+([\w.]+)', content):
                    module = match.group(1)
                    # Пропустить встроенные модули
                    if not module.startswith('__'):
                        imports.add(module)
        except Exception:
            pass
        
        return imports
    
    def populate_from_report(self, report, project_root: str):
        """Заполнить граф из отчета аудита"""
        print(f"[GraphVisualizer] Загружаю граф из отчета для проекта: {project_root}")
        
        self.nodes.clear()
        self.edges.clear()
        
        files_info = {}
        
        # Собрать все файлы с ошибками из кода и безопасности
        for issue in report.code_issues:
            path = str(issue['file']).replace('\\', '/')
            
            if path not in files_info:
                files_info[path] = {
                    'errors': 0,
                    'max_severity': 'LOW',
                    'lines': 0,
                }
            files_info[path]['errors'] += 1
            
            # Обновить серьезность
            sev_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
            if sev_order.get(issue.get('severity', 'LOW'), 0) > \
               sev_order.get(files_info[path]['max_severity'], 0):
                files_info[path]['max_severity'] = issue.get('severity', 'LOW')
        
        for issue in report.security_issues:
            path = str(issue['file']).replace('\\', '/')
            
            if path not in files_info:
                files_info[path] = {
                    'errors': 0,
                    'max_severity': 'LOW',
                    'lines': 0,
                }
            files_info[path]['errors'] += 1
            
            sev_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
            if sev_order.get(issue.get('severity', 'LOW'), 0) > \
               sev_order.get(files_info[path]['max_severity'], 0):
                files_info[path]['max_severity'] = issue.get('severity', 'LOW')
        
        # Сканировать все файлы проекта
        scanned_files = set()
        try:
            for py_file in Path(project_root).rglob('*.py'):
                rel = str(py_file.relative_to(project_root)).replace('\\', '/').replace('./', '')
                
                # Пропустить исключённые файлы
                if self._is_excluded_path(rel):
                    continue
                
                # Дедупликация
                if rel in scanned_files:
                    continue
                scanned_files.add(rel)
                
                # Если файл не в списке ошибок, добавить с 0 ошибок
                if rel not in files_info:
                    files_info[rel] = {
                        'errors': 0,
                        'max_severity': 'LOW',
                        'lines': 0,
                    }
        except Exception as e:
            print(f"[GraphVisualizer] Ошибка сканирования: {e}")
        
        # Создать узлы
        for file_path, info in files_info.items():
            folder = str(Path(file_path).parent).replace('\\', '/')
            
            # Подсчитать строки кода
            try:
                full_path = Path(project_root) / file_path
                if full_path.exists():
                    lines = len(full_path.read_text(encoding='utf-8', errors='ignore').split('\n'))
                else:
                    lines = 0
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
        
        # Создать рёбра (связи между файлами)
        for file_path, node in self.nodes.items():
            for imported in node.imports:
                # Попытаться найти локальный файл
                for other_path in self.nodes.keys():
                    # Упрощенное сравнение: если именя файла совпадают
                    if other_path != file_path:
                        if Path(other_path).stem == Path(imported).stem or \
                           other_path.endswith(imported.replace('.', '/') + '.py'):
                            self.edges.append((file_path, other_path))
        
        print(f"[GraphVisualizer] Добавлено {len(self.nodes)} узлов, {len(self.edges)} связей")
        
        self._render_graph()
    
    def _on_render_changed(self):
        """Пользователь изменил выбор рендера"""
        if self.is_initializing:
            return
        
        old_render = self.current_render
        self.current_render = "pyvis" if self.render_combo.currentIndex() == 1 else "plotly"
        
        print(f"[GraphVisualizer] Переключение: {old_render} → {self.current_render}")
        
        if self.nodes:
            self._render_graph()
    
    def _on_labels_toggled(self):
        if not self.is_initializing:
            self._render_graph()
    
    def _on_edges_toggled(self):
        if not self.is_initializing:
            self._render_graph()
    
    def _on_scale_changed(self):
        if not self.is_initializing:
            self.scale_factor = self.scale_slider.value() / 100.0
            self._render_graph()
    
    def _on_refresh(self):
        self._render_graph()
    
    def _render_graph(self):
        """Отрендерить граф"""
        if not self.nodes:
            print("[GraphVisualizer] Нечего рендерить")
            return
        
        if self.current_render == "plotly":
            if HAS_PLOTLY:
                self._render_with_plotly()
            elif HAS_PYVIS:
                print("[GraphVisualizer] Plotly недоступен, используюсь PyVis")
                self._render_with_pyvis()
            else:
                self.web_view.setHtml("<p style='color:red'>❌ Plotly и PyVis не установлены</p>")
        else:
            if HAS_PYVIS:
                self._render_with_pyvis()
            elif HAS_PLOTLY:
                print("[GraphVisualizer] PyVis недоступен, используюсь Plotly")
                self._render_with_plotly()
            else:
                self.web_view.setHtml("<p style='color:red'>❌ PyVis и Plotly не установлены</p>")
    
    def _render_with_plotly(self):
        """Рендерить с Plotly - улучшенная версия"""
        print(f"[GraphVisualizer] Рендерю Plotly граф ({len(self.nodes)} узлов)")
        
        try:
            # Группировать по папкам
            folders: Dict[str, List[str]] = {}
            for file_path in self.nodes.keys():
                folder = self.nodes[file_path].folder
                folders.setdefault(folder, []).append(file_path)
            
            folder_list = sorted(folders.keys())
            fcount = len(folder_list)
            
            # Grid layout для папок (большие расстояния)
            fcols = max(1, int(fcount ** 0.5))
            folder_positions = {}
            for idx, folder in enumerate(folder_list):
                fx = (idx % fcols) * GRID_SPACING
                fy = (idx // fcols) * GRID_SPACING
                folder_positions[folder] = (fx, fy)
            
            # Разместить узлы внутри облаков (меньшие расстояния)
            node_x, node_y, node_ids = [], [], []
            node_colors, node_sizes, node_labels, node_hovers = [], [], [], []
            
            for folder in folder_list:
                files = folders[folder]
                cx, cy = folder_positions[folder]
                
                # Grid layout внутри папки (круг)
                n = len(files)
                for i, file_path in enumerate(files):
                    # Расставить по спирали чтобы не накладывались
                    angle = (i / max(1, n)) * 2 * 3.14159
                    radius = CLOUD_RADIUS * (1 + i % 3)
                    
                    x = cx + radius * __import__('math').cos(angle) * MIN_NODE_DISTANCE
                    y = cy + radius * __import__('math').sin(angle) * MIN_NODE_DISTANCE
                    
                    node_x.append(x)
                    node_y.append(y)
                    node_ids.append(file_path)
                    
                    node = self.nodes[file_path]
                    
                    # Цвет по папке
                    color = self._get_folder_color(folder)
                    node_colors.append(color)
                    
                    # Размер по ошибкам и строкам
                    size = max(10, min(50, 15 + node.errors_count * 4 + int((node.lines_of_code ** 0.5) / 10)))
                    node_sizes.append(size)
                    
                    # Лабель: только число ошибок (или имя, если выбрано)
                    if self.show_labels.isChecked():
                        label = Path(file_path).name
                        if node.errors_count > 0:
                            label += f"\n{node.errors_count}"
                    else:
                        label = str(node.errors_count) if node.errors_count > 0 else ""
                    node_labels.append(label)
                    
                    # Hover text
                    hover_text = (
                        f"<b>{Path(file_path).name}</b><br>"
                        f"Папка: {folder}<br>"
                        f"Строк: {node.lines_of_code}<br>"
                        f"Ошибок: {node.errors_count}<br>"
                        f"Серьезность: {node.max_severity}"
                    )
                    node_hovers.append(hover_text)
            
            # Создать рёбра (связи)
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
                    line=dict(width=1, color='rgba(200,200,200,0.5)'),
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
                height=600,
                width=None
            )
            
            # Сохранить и показать
            html_file = Path(tempfile.gettempdir()) / "naudit_graph_temp.html"
            html_content = fig.to_html(include_plotlyjs='inline')
            html_file.write_text(html_content, encoding='utf-8')
            
            file_url = QUrl.fromLocalFile(str(html_file.resolve()))
            self.web_view.load(file_url)
            
            print(f"[GraphVisualizer] ✅ Plotly граф отрендерен")
        
        except Exception as e:
            print(f"[Error] Ошибка Plotly: {e}")
            import traceback
            traceback.print_exc()
    
    def _render_with_pyvis(self):
        """Рендерить с PyVis - сетевой граф"""
        print(f"[GraphVisualizer] Рендерю PyVis граф ({len(self.nodes)} узлов)")
        
        try:
            net = Network(height='600px', width='100%', directed=False, notebook=False,
                         bgcolor='#fafafa', font_color='#000000')
            
            # Добавить узлы
            for file_path, node in self.nodes.items():
                # Цвет по папке
                color = self._get_folder_color(node.folder)
                
                # Label: только число ошибок
                if self.show_labels.isChecked():
                    label = Path(file_path).name
                else:
                    label = str(node.errors_count) if node.errors_count > 0 else ""
                
                # Размер
                size = max(15, min(50, 20 + node.errors_count * 3))
                
                net.add_node(
                    file_path,
                    label=label,
                    color=color,
                    size=size,
                    title=f"{Path(file_path).name}\n{node.errors_count} ошибок\nПапка: {node.folder}"
                )
            
            # Добавить рёбра
            if self.show_edges.isChecked():
                for src, dst in self.edges:
                    net.add_edge(src, dst, color='rgba(200,200,200,0.5)')
            
            # Сохранить и показать
            html_file = Path(tempfile.gettempdir()) / "naudit_graph_pyvis.html"
            net.show(str(html_file))
            
            file_url = QUrl.fromLocalFile(str(html_file.resolve()))
            self.web_view.load(file_url)
            
            print(f"[GraphVisualizer] ✅ PyVis граф отрендерен")
        
        except Exception as e:
            print(f"[Error] Ошибка PyVis: {e}")
            import traceback
            traceback.print_exc()
    
    def clear(self):
        """Очистить граф"""
        self.nodes.clear()
        self.edges.clear()
        self.web_view.setUrl(QUrl("about:blank"))
    
    def get_all_files(self) -> List[str]:
        """Получить все файлы"""
        return list(self.nodes.keys())
    
    def filter_by_severity(self, min_severity: str):
        """Фильтровать по серьезности"""
        severity_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        min_order = severity_order.get(min_severity, 0)
        
        filtered = {
            k: v for k, v in self.nodes.items()
            if severity_order.get(v.max_severity, 0) >= min_order
        }
        
        # Показать только отфильтрованные узлы
        print(f"[GraphVisualizer] Фильтр: {len(filtered)} из {len(self.nodes)} файлов")
