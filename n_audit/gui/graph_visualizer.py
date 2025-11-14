#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Граф-визуализация проекта (Graphical Visualization)

Файлы как узлы графа с:
- Размер узла = количество строк кода в файле
- Цвет узла = тип ошибок (зелёный/жёлтый/оранжевый/красный)
- Число на узле = количество ошибок
- Группировка = по папкам проекта
- Связи между узлами = импорты между файлами
"""

import sys
import tempfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
import json
import re

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSlider, QCheckBox, QComboBox, QSpinBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QFont

try:
    import networkx as nx
except ImportError:
    nx = None

# Пытаемся импортировать Plotly для лучшей визуализации
try:
    import plotly.graph_objects as go
    from plotly.offline import plot as plotly_plot
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# Fallback на PyVis если Plotly недоступен
try:
    from pyvis.network import Network
    HAS_PYVIS = True
except ImportError:
    HAS_PYVIS = False


@dataclass
class FileNode:
    """Узел графа (файл проекта)"""
    file_path: str              # .\n_audit\gui\tree_widget.py
    lines_of_code: int          # 478
    errors_count: int           # 5
    max_severity: str           # CRITICAL, HIGH, MEDIUM, LOW
    folder: str                 # n_audit/gui
    imports: Set[str] = field(default_factory=set)    # Импортируемые файлы


class GraphVisualizerWidget(QWidget):
    """
    Интерактивная граф-визуализация проекта
    
    Визуализирует файлы проекта как сеть узлов (nodes) с:
    - Размер узла: пропорционален строкам кода
    - Цвет узла: зависит от типа ошибок
    - Текст узла: имя файла + количество ошибок
    - Группировка: по папкам
    - Связи: между файлами с импортами
    """
    
    # Сигналы
    file_selected = pyqtSignal(str)  # Выбран файл
    
    def __init__(self):
        super().__init__()
        
        if Network is None:
            print("[Warning] PyVis не установлен - граф не будет работать")
        
        # Данные
        self.nodes: Dict[str, FileNode] = {}
        self.graph = nx.DiGraph() if nx else None  # Направленный граф
        
        # Состояние фильтра
        self.severity_filter = "Все"
        self.show_labels_enabled = True
        self.show_edges_enabled = True
        self.scale_factor = 1.0
        self.is_initializing = True  # Флаг для предотвращения рендеринга при инициализации
        
        # Таймер для дебаунсинга рендеринга
        self.render_timer = QTimer()
        self.render_timer.setSingleShot(True)
        self.render_timer.setInterval(500)  # 500ms задержка
        self.render_timer.timeout.connect(self._do_render_graph)
        
        # UI
        self.init_ui()
        
        # После инициализации UI разрешаем рендеринг
        self.is_initializing = False
    
    def init_ui(self):
        """Инициализировать UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Панель управления
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(5, 5, 5, 5)
        
        # Фильтр по серьезности
        control_layout.addWidget(QLabel("Фильтр:"))
        self.severity_filter_combo = QComboBox()
        self.severity_filter_combo.addItems(["Все", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
        self.severity_filter_combo.currentTextChanged.connect(self._on_filter_changed)
        self.severity_filter_combo.setMaximumWidth(120)
        control_layout.addWidget(self.severity_filter_combo)
        
        # Масштаб узлов
        control_layout.addWidget(QLabel("Масштаб:"))
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setMinimum(50)
        self.scale_slider.setMaximum(200)
        self.scale_slider.setValue(100)
        self.scale_slider.setMaximumWidth(150)
        self.scale_slider.setTickInterval(25)
        self.scale_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.scale_slider.valueChanged.connect(self._on_scale_changed)
        control_layout.addWidget(self.scale_slider)
        
        # Опции
        self.show_labels = QCheckBox("Метки")
        self.show_labels.setChecked(True)
        self.show_labels.stateChanged.connect(self._on_labels_toggled)
        control_layout.addWidget(self.show_labels)
        
        self.show_edges = QCheckBox("Связи")
        self.show_edges.setChecked(True)
        self.show_edges.stateChanged.connect(self._on_edges_toggled)
        control_layout.addWidget(self.show_edges)
        
        # Кнопка обновления
        refresh_btn = QPushButton("🔄")
        refresh_btn.setMaximumWidth(40)
        refresh_btn.setToolTip("Обновить граф")
        refresh_btn.clicked.connect(self._on_refresh)
        control_layout.addWidget(refresh_btn)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # Web view для визуализации
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(400)
        # Показываем приветственное сообщение
        welcome_html = """
        <html>
        <head><meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; background: #f5f5f5; padding: 40px; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
            h2 { color: #333; }
            p { color: #666; line-height: 1.6; }
        </style>
        </head>
        <body>
            <div class="container">
                <h2>🕸️ Граф визуализации</h2>
                <p>Здесь будет отображена интерактивная визуализация проекта.</p>
                <p>Граф будет загружен после завершения аудита...</p>
            </div>
        </body>
        </html>
        """
        self.web_view.setHtml(welcome_html)
        layout.addWidget(self.web_view)
    
    def populate_from_report(self, report, project_root: str = "."):
        """
        Заполнить граф из отчета аудита
        
        Args:
            report: AuditReport с информацией об ошибках
            project_root: корень проекта для вычисления путей
        """
        if self.graph is None:
            print("[GraphVisualizer] PyVis не установлен")
            return
        
        print(f"[GraphVisualizer] Загружаю граф из отчета...")
        
        # Очищаем старые данные
        self.nodes.clear()
        self.graph.clear()
        
        try:
            project_root = Path(project_root)
        except:
            project_root = Path(".")
        
        # Собираем информацию о файлах
        files_info = {}
        
        # Обрабатываем код-ошибки
        if hasattr(report.metrics, 'code_issues'):
            for issue in report.metrics.code_issues:
                file_path = issue.file_path
                if file_path not in files_info:
                    files_info[file_path] = {
                        'errors': [],
                        'lines_of_code': 0,
                        'max_severity': 'LOW'
                    }
                files_info[file_path]['errors'].append(issue)
        
        # Обрабатываем безопасность-ошибки
        if hasattr(report.metrics, 'security_issues'):
            for issue in report.metrics.security_issues:
                file_path = issue.file_path
                if file_path not in files_info:
                    files_info[file_path] = {
                        'errors': [],
                        'lines_of_code': 0,
                        'max_severity': 'LOW'
                    }
                files_info[file_path]['errors'].append(issue)
        
        # Конвертируем в FileNode'ы
        for file_path, info in files_info.items():
            try:
                # Определяем максимальную серьезность
                max_sev = 'LOW'
                severity_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
                for issue in info['errors']:
                    sev = getattr(issue, 'severity', 'LOW')
                    if severity_order.get(sev, 0) > severity_order.get(max_sev, 0):
                        max_sev = sev
                
                # Получаем папку
                file_path_obj = Path(file_path)
                folder = str(file_path_obj.parent) if file_path_obj.parent != Path('.') else 'root'
                
                # Пытаемся получить количество строк
                lines = 0
                try:
                    full_path = project_root / file_path if not Path(file_path).is_absolute() else Path(file_path)
                    if full_path.exists():
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = len(f.readlines())
                except:
                    pass
                
                # Создаём узел
                node = FileNode(
                    file_path=str(file_path),
                    lines_of_code=lines,
                    errors_count=len(info['errors']),
                    max_severity=max_sev,
                    folder=folder
                )
                
                self.nodes[file_path] = node
                
                # Добавляем в граф NetworkX
                self.graph.add_node(file_path)
            
            except Exception as e:
                print(f"[Warning] Ошибка при обработке {file_path}: {e}")
        
        print(f"[GraphVisualizer] Добавлено {len(self.nodes)} узлов")
        
        # Строим граф визуализацию
        self._render_graph()
    
    def _get_color(self, severity: str) -> str:
        """Получить цвет для узла по серьезности"""
        colors = {
            'CRITICAL': '#ff4444',  # Красный
            'HIGH': '#ff9900',      # Оранжевый
            'MEDIUM': '#ffcc00',    # Жёлтый
            'LOW': '#44dd44'        # Зелёный
        }
        return colors.get(severity, '#44dd44')
    
    def _get_size(self, lines: int) -> int:
        """Получить размер узла по количеству строк"""
        # Масштабируем от 20 до 50 в зависимости от количества строк
        # Формула: базовый размер 25 + sqrt(lines)/10
        base_size = 25
        scale = max(0, min(25, int((lines ** 0.5) / 2)))
        return int((base_size + scale) * self.scale_factor)
    
    def _render_graph(self):
        """Отложенный рендеринг графа (с дебаунсингом)"""
        # Перезапускаем таймер - если пользователь быстро меняет фильтры,
        # граф будет рендериться только один раз после 500ms паузы
        self.render_timer.stop()
        self.render_timer.start()
    
    def _do_render_graph(self):
        """Отрендерить граф в HTML"""
        if not self.nodes:
            print("[GraphVisualizer] Нечего рендерить")
            return
        
        try:
            # Применяем фильтр серьезности
            severity_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
            filter_text = self.severity_filter_combo.currentText()
            
            if filter_text != "Все":
                min_level = severity_order.get(filter_text, 0)
                nodes_to_show = {
                    path: node for path, node in self.nodes.items()
                    if severity_order.get(node.max_severity, 0) >= min_level
                }
            else:
                nodes_to_show = self.nodes
            
            node_count = len(nodes_to_show)
            
            if node_count == 0:
                self._show_empty_graph()
                return
            
            # Пытаемся использовать Plotly для лучшей визуализации
            if HAS_PLOTLY:
                self._render_with_plotly(nodes_to_show, node_count)
            elif HAS_PYVIS:
                self._render_with_pyvis(nodes_to_show, node_count)
            else:
                self._show_empty_graph()
                print("[GraphVisualizer] Ни Plotly ни PyVis не установлены")
        
        except Exception as e:
            print(f"[Error] Ошибка при рендеринге графа: {e}")
            import traceback
            traceback.print_exc()
            self._show_error_graph(str(e))
    
    def _render_with_plotly(self, nodes_to_show: Dict, node_count: int):
        """Рендерить граф с использованием Plotly"""
        print(f"[GraphVisualizer] Используюусь Plotly для рендеринга {node_count} узлов")
        
        try:
            # Создаём граф NetworkX для компоновки
            if nx is None:
                print("[GraphVisualizer] NetworkX не установлен, используем простую компоновку")
                graph = None
            else:
                graph = nx.DiGraph()
            
            # Данные узлов
            node_ids = list(nodes_to_show.keys())
            node_x = []
            node_y = []
            node_colors = []
            node_sizes = []
            node_labels = []
            node_hovers = []
            
            # Рассчитываем позиции узлов
            if graph is not None:
                for file_path in node_ids:
                    graph.add_node(file_path)
                
                try:
                    # Используем spring layout для лучшего распределения
                    pos = nx.spring_layout(graph, k=0.5, iterations=50, seed=42)
                    for file_path in node_ids:
                        if file_path in pos:
                            x, y = pos[file_path]
                            node_x.append(x)
                            node_y.append(y)
                        else:
                            node_x.append(0)
                            node_y.append(0)
                except:
                    # Fallback на простую сетку
                    cols = int(node_count ** 0.5) + 1
                    for i, file_path in enumerate(node_ids):
                        node_x.append((i % cols) * 2)
                        node_y.append((i // cols) * 2)
            else:
                # Простая сетка если NetworkX недоступен
                cols = int(node_count ** 0.5) + 1
                for i in range(node_count):
                    node_x.append((i % cols) * 2)
                    node_y.append((i // cols) * 2)
            
            # Собираем информацию об узлах
            for i, file_path in enumerate(node_ids):
                node = nodes_to_show[file_path]
                
                # Цвет узла
                color = self._get_color(node.max_severity)
                node_colors.append(color)
                
                # Размер узла
                size = max(15, min(50, 20 + node.errors_count * 5 + int((node.lines_of_code ** 0.5) / 10)))
                node_sizes.append(size)
                
                # Текст узла
                file_name = Path(file_path).name
                if self.show_labels.isChecked():
                    label_text = file_name
                    if node.errors_count > 0:
                        label_text += f"\n{node.errors_count}⚠️"
                    node_labels.append(label_text)
                else:
                    node_labels.append("")
                
                # Tooltip
                hover_text = (
                    f"<b>{file_name}</b><br>"
                    f"Папка: {node.folder}<br>"
                    f"Строк: {node.lines_of_code}<br>"
                    f"Ошибок: {node.errors_count}<br>"
                    f"Серьезность: {node.max_severity}"
                )
                node_hovers.append(hover_text)
            
            # Создаём рёбра
            edge_x = []
            edge_y = []
            
            if self.show_edges.isChecked() and node_count < 200:
                # Соединяем файлы с ошибками в одной папке
                folders = {}
                for file_path in node_ids:
                    node = nodes_to_show[file_path]
                    folder = node.folder
                    if folder not in folders:
                        folders[folder] = []
                    folders[folder].append(file_path)
                
                for folder, files in folders.items():
                    # Соединяем первые 2 файла в папке
                    for i in range(len(files) - 1):
                        idx1 = node_ids.index(files[i])
                        idx2 = node_ids.index(files[i + 1])
                        
                        edge_x.append(node_x[idx1])
                        edge_x.append(node_x[idx2])
                        edge_x.append(None)
                        
                        edge_y.append(node_y[idx1])
                        edge_y.append(node_y[idx2])
                        edge_y.append(None)
            
            # Создаём Figure
            fig = go.Figure()
            
            # Добавляем рёбра
            if edge_x:
                fig.add_trace(go.Scatter(
                    x=edge_x, y=edge_y,
                    mode='lines',
                    line=dict(width=0.5, color='#cccccc'),
                    hoverinfo='none',
                    showlegend=False
                ))
            
            # Добавляем узлы
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                marker=dict(
                    size=node_sizes,
                    color=node_colors,
                    line=dict(width=2, color='#000000'),
                    opacity=0.9,
                    sizemode='diameter'
                ),
                text=node_labels,
                textposition="middle center",
                textfont=dict(size=10, color='#000000', family='Arial'),
                hovertext=node_hovers,
                hoverinfo='text',
                showlegend=False
            ))
            
            # Конфигурируем layout
            fig.update_layout(
                title=f"Граф проекта ({node_count} файлов)",
                title_font_size=14,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                annotations=[],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='#fafafa',  # Светлый фон
                paper_bgcolor='#ffffff',
                height=600,
                width=None
            )
            
            # Сохраняем HTML
            html_file = Path(tempfile.gettempdir()) / "naudit_graph_temp.html"
            
            try:
                fig.write_html(str(html_file))
                print(f"[GraphVisualizer] Plotly HTML сохранен: {html_file}")
            except Exception as e:
                print(f"[GraphVisualizer] Ошибка при сохранении Plotly HTML: {e}")
                return
            
            # Загружаем в web view
            file_url = QUrl.fromLocalFile(str(html_file.resolve()))
            print(f"[GraphVisualizer] Загружаю HTML: {file_url.toString()}")
            self.web_view.load(file_url)
            
            print(f"[GraphVisualizer] Plotly граф отрендерен с {len(nodes_to_show)} узлами")
        
        except Exception as e:
            print(f"[Error] Ошибка при рендеринге с Plotly: {e}")
            import traceback
            traceback.print_exc()
    
    def _render_with_pyvis(self, nodes_to_show: Dict, node_count: int):
        """Рендерить граф с использованием PyVis (fallback)"""
        print(f"[GraphVisualizer] Используюсь PyVis для рендеринга {node_count} узлов")
        
        try:
            # Создаём Pyvis граф
            g = Network(
                height='600px',
                width='100%',
                directed=False,
                notebook=False,
                bgcolor='#fafafa',  # Светлый фон вместо белого
                font_color='#000000'
            )
            
            # Упрощаем физику для больших графов
            if node_count > 100:
                g.toggle_physics(False)
                print(f"[GraphVisualizer] Большой граф ({node_count} узлов) - физика отключена")
            else:
                g.barnes_hut(gravity=-30000, central_gravity=0.3, spring_length=200)
                g.toggle_physics(True)
            
            # Группируем по папкам
            folders = {}
            for file_path, node in nodes_to_show.items():
                folder = node.folder
                if folder not in folders:
                    folders[folder] = []
                folders[folder].append((file_path, node))
            
            # Генерируем цвета для папок
            folder_colors = self._generate_folder_colors(len(folders))
            
            # Добавляем узлы с цветовой кодировкой
            for folder_idx, (folder, files) in enumerate(folders.items()):
                for file_path, node in files:
                    size = self._get_size(node.lines_of_code)
                    color = self._get_color(node.max_severity)
                    
                    # Имя файла с количеством ошибок
                    file_name = Path(file_path).name
                    label = file_name if self.show_labels.isChecked() else ""
                    
                    if node.errors_count > 0 and self.show_labels.isChecked():
                        label += f"\n{node.errors_count}⚠️"
                    
                    title_text = (
                        f"<b>{file_name}</b><br>"
                        f"Папка: {folder}<br>"
                        f"Строк: {node.lines_of_code}<br>"
                        f"Ошибок: {node.errors_count}<br>"
                        f"Серьезность: {node.max_severity}"
                    )
                    
                    g.add_node(
                        file_path,
                        label=label,
                        color=color,
                        size=size,
                        title=title_text,
                        mass=1,
                        font={'size': 12, 'face': 'arial'},
                        borderWidth=1,
                        borderWidthSelected=3
                    )
            
            # Добавляем рёбра
            if self.show_edges.isChecked() and node_count < 200:
                for folder, files in folders.items():
                    file_paths = [fp for fp, _ in files]
                    for i in range(len(file_paths) - 1):
                        for j in range(i + 1, min(i + 3, len(file_paths))):
                            if nodes_to_show[file_paths[i]].errors_count > 0 and \
                               nodes_to_show[file_paths[j]].errors_count > 0:
                                g.add_edge(file_paths[i], file_paths[j], weight=0.5, color='#cccccc')
            
            # Сохраняем HTML
            html_file = Path(tempfile.gettempdir()) / "naudit_graph_temp.html"
            
            try:
                g.write_html(str(html_file), open_browser=False, notebook=False)
                print(f"[GraphVisualizer] PyVis HTML сохранен: {html_file}")
            except Exception as e:
                print(f"[GraphVisualizer] Ошибка PyVis: {e}")
                return
            
            # Загружаем в web view
            file_url = QUrl.fromLocalFile(str(html_file.resolve()))
            print(f"[GraphVisualizer] Загружаю HTML: {file_url.toString()}")
            self.web_view.load(file_url)
            
            print(f"[GraphVisualizer] PyVis граф отрендерен")
        
        except Exception as e:
            print(f"[Error] Ошибка при рендеринге с PyVis: {e}")
            import traceback
            traceback.print_exc()
    
    def _show_empty_graph(self):
        """Показать пустой граф с сообщением"""
        html = """
        <html>
        <head><meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 0; }
            .container { display: flex; align-items: center; justify-content: center; height: 600px; }
            .message { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center; }
            h2 { color: #333; margin: 0 0 10px 0; }
            p { color: #666; margin: 0; }
        </style>
        </head>
        <body>
            <div class="container">
                <div class="message">
                    <h2>🕸️ Граф визуализации</h2>
                    <p>Нет данных для отображения</p>
                    <p><small>Выполните аудит проекта</small></p>
                </div>
            </div>
        </body>
        </html>
        """
        self.web_view.setHtml(html)
    
    def _show_error_graph(self, error_msg: str):
        """Показать ошибку"""
        html = f"""
        <html>
        <head><meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; background: #fff3cd; margin: 0; padding: 0; }}
            .container {{ display: flex; align-items: center; justify-content: center; height: 600px; }}
            .message {{ background: white; padding: 30px; border-radius: 8px; border-left: 4px solid #ff6b6b; box-shadow: 0 2px 8px rgba(0,0,0,0.1); max-width: 500px; }}
            h2 {{ color: #ff6b6b; margin: 0 0 10px 0; }}
            p {{ color: #333; margin: 0; line-height: 1.6; }}
            code {{ background: #f0f0f0; padding: 2px 5px; border-radius: 3px; font-family: monospace; }}
        </style>
        </head>
        <body>
            <div class="container">
                <div class="message">
                    <h2>⚠️ Ошибка при рендеринге</h2>
                    <p><code>{error_msg}</code></p>
                    <p><small>Попробуйте обновить приложение или проверьте логи</small></p>
                </div>
            </div>
        </body>
        </html>
        """
        self.web_view.setHtml(html)
    
    def _render_with_canvas(self, nodes_to_show: Dict, node_count: int):
        """Рендерить граф с использованием Canvas/SVG (последняя попытка)"""
        print(f"[GraphVisualizer] Используюсь Canvas/SVG для рендеринга {node_count} узлов")
        
        try:
            # Рассчитываем позиции на сетке
            cols = int(node_count ** 0.5) + 1
            cell_width = 800 / cols
            cell_height = 600 / cols
            
            node_ids = list(nodes_to_show.keys())
            nodes_html = []
            
            for idx, file_path in enumerate(node_ids):
                node = nodes_to_show[file_path]
                
                # Позиция на сетке
                col = idx % cols
                row = idx // cols
                x = col * cell_width + cell_width / 2
                y = row * cell_height + cell_height / 2
                
                # Определяем размер и цвет
                size = max(30, min(60, 40 + node.errors_count * 3))
                color = self._get_color(node.max_severity)
                
                file_name = Path(file_path).name
                label = file_name[:15]  # Сокращаем имя
                
                # SVG для узла
                node_svg = f"""
                <g id="node_{idx}">
                    <circle cx="{x}" cy="{y}" r="{size}" fill="{color}" stroke="#000" stroke-width="2" opacity="0.9"/>
                    <text x="{x}" y="{y}" text-anchor="middle" dy="0.3em" font-size="11" fill="#000" font-weight="bold">{label}</text>
                    <title>{file_name} ({node.errors_count} ошибок)</title>
                </g>
                """
                nodes_html.append(node_svg)
            
            # Создаём SVG
            svg_content = f"""
            <svg width="100%" height="600" viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <style>
                        .node {{ cursor: pointer; }}
                        circle {{ transition: all 0.2s; }}
                        circle:hover {{ filter: drop-shadow(0 0 5px rgba(0,0,0,0.3)); }}
                    </style>
                </defs>
                <rect width="800" height="600" fill="#fafafa"/>
                {''.join(nodes_html)}
            </svg>
            """
            
            # Оборачиваем в HTML
            html = f"""
            <html>
            <head><meta charset="UTF-8">
            <style>
                body {{ margin: 0; padding: 0; background: #ffffff; }}
                .title {{ padding: 10px; background: #f0f0f0; border-bottom: 1px solid #ddd; font-size: 14px; font-weight: bold; }}
                svg {{ width: 100%; height: auto; }}
            </style>
            </head>
            <body>
                <div class="title">Граф проекта ({node_count} файлов)</div>
                {svg_content}
            </body>
            </html>
            """
            
            # Сохраняем HTML
            html_file = Path(tempfile.gettempdir()) / "naudit_graph_temp.html"
            html_file.write_text(html, encoding='utf-8')
            
            # Загружаем в web view
            file_url = QUrl.fromLocalFile(str(html_file.resolve()))
            self.web_view.load(file_url)
            
            print(f"[GraphVisualizer] Canvas/SVG граф отрендерен с {node_count} узлами")
        
        except Exception as e:
            print(f"[Error] Ошибка при рендеринге Canvas: {e}")
            self._show_empty_graph()
    
    def _generate_folder_colors(self, count: int) -> List[str]:
        """Сгенерировать цвета для папок"""
        if count == 0:
            return []
        
        # Используем HSV палитру для равномерного распределения цветов
        colors = []
        for i in range(count):
            hue = (i / count) * 360
            colors.append(f"hsl({hue}, 70%, 50%)")
        return colors
    
    def _on_filter_changed(self):
        """Фильтр по серьезности изменился"""
        if not self.is_initializing:
            self._render_graph()
    
    def _on_scale_changed(self):
        """Масштаб изменился"""
        if not self.is_initializing:
            self.scale_factor = self.scale_slider.value() / 100.0
            self._render_graph()
    
    def _on_labels_toggled(self):
        """Переключение меток"""
        if not self.is_initializing:
            self._render_graph()
    
    def _on_edges_toggled(self):
        """Переключение связей"""
        if not self.is_initializing:
            self._render_graph()
    
    def _on_refresh(self):
        """Обновить граф"""
        self._render_graph()
    
    def clear(self):
        """Очистить граф"""
        self.nodes.clear()
        if self.graph:
            self.graph.clear()
        self.web_view.setUrl(QUrl("about:blank"))
    
    def get_all_files(self) -> List[str]:
        """Получить все файлы в графе"""
        return list(self.nodes.keys())
    
    def filter_by_severity(self, min_severity: str):
        """
        Фильтровать файлы по минимальной серьезности
        
        Args:
            min_severity: CRITICAL, HIGH, MEDIUM, LOW
        """
        self.severity_filter_combo.setCurrentText(min_severity)

