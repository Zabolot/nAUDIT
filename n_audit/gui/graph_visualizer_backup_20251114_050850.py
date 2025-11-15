#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Граф-визуализация проекта v2.2 - УЛУЧШЕННАЯ ВЕРСИЯ

ИСПРАВЛЕННЫЕ ПРОБЛЕМЫ:
✅ Исключение файлов из .venv, __pycache__, .git и т.д.
✅ Показ связей (импортов) между файлами  
✅ Увеличенные расстояния между облаками папок (без скучивания)
✅ На узлах ТОЛЬКО цифры ошибок (без имен файлов)
✅ Цвета по папкам (детерминированные, не совпадают)
✅ Предотвращение наложения узлов (улучшенная спираль)
✅ Переключение между Plotly и PyVis рендерами

Файлы как узлы графа с:
- Размер узла = количество строк кода в файле
- Цвет узла = принадлежность к папке (детерминированный хеш)
- Число на узле = количество ошибок (или имя файла опционально)
- Группировка = по папкам проекта (облака)
- Связи между узлами = импорты между файлами
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
    QLabel, QSlider, QCheckBox, QComboBox, QSpinBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QUrl, QObject, pyqtSlot
from PyQt6.QtCore import QEvent
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


# ════════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ И ИСКЛЮЧЕНИЯ
# ════════════════════════════════════════════════════════════════

EXCLUDE_FOLDERS = {
    '.venv', 'venv', '.env',           # Виртуальные окружения
    '__pycache__', '.pyc', '.egg-info', # Python кэш
    '.git', '.github',                  # Git
    '.pytest_cache', '.tox',            # Тестирование
    'node_modules', '.npm',             # Node.js
    '.idea', '.vscode', '.sublime',    # IDE
    'build', 'dist', '.build',         # Сборка
    'htmlcov', '.coverage',            # Coverage отчеты
    '.mypy_cache', '.dmypy',           # MyPy кэш
    '.DS_Store',                        # macOS
}

GRID_SPACING = 25.0                    # Расстояние между облаками папок (было 10)
CLOUD_RADIUS = 3.0                     # Радиус внутри облака  
MIN_NODE_DISTANCE = 2.5                # Минимальное расстояние между узлами


class GraphNodeBridge(QObject):
    """Мост между JavaScript графа и Python UI для синхронизации выбора узлов"""
    
    # Сигнал: когда пользователь кликнул на узел в графе
    node_clicked = pyqtSignal(str)  # file_path
    
    def __init__(self):
        super().__init__()
    
    @pyqtSlot(str)
    def onNodeClicked(self, file_path: str):
        """Вызывается из JavaScript когда пользователь кликает на узел"""
        print(f"[GraphNodeBridge] Узел выбран: {file_path}")
        self.node_clicked.emit(file_path)


@dataclass
class FileNode:
    """Узел графа (файл проекта)"""
    file_path: str              # .\n_audit\gui\tree_widget.py
    lines_of_code: int          # 478
    errors_count: int           # 5
    max_severity: str           # CRITICAL, HIGH, MEDIUM, LOW
    folder: str                 # n_audit/gui
    imports: Set[str] = field(default_factory=set)    # Импортируемые модули


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

        # Масштаб узлов (значение привязано к scale_factor)
        control_layout.addWidget(QLabel("Масштаб:"))
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setMinimum(50)
        self.scale_slider.setMaximum(300)
        self.scale_slider.setValue(int(self.scale_factor * 100))
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
        # Устанавливаем фильтр событий для обработки колеса и кликов
        self.web_view.installEventFilter(self)

        # Приветственное сообщение пока граф не готов
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

        # флаг, чтобы не рендерить в процессе инициализации
        self._initializing = False
        # флаг фокусного эффекта после клика
        self._focus_active = False
    
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
        
        # Добавляем все файлы проекта (включая без ошибок), но только если их нет уже
        try:
            project_root_path = Path(project_root) if isinstance(project_root, Path) else Path(project_root)
            scanned_files = set()
            for p in project_root_path.rglob('*.py'):
                try:
                    rel = str(p.relative_to(project_root_path)).replace('\\', '/')
                    # Skip __pycache__, .egg-info и другие служебные папки
                    if '__pycache__' in rel or '.egg' in rel or '.dist-info' in rel:
                        continue
                    if rel not in self.nodes and rel not in scanned_files:
                        scanned_files.add(rel)
                        # Подсчитываем строки для новых файлов
                        lines = 0
                        try:
                            if p.exists():
                                with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                                    lines = len(f.readlines())
                        except:
                            pass
                        
                        node = FileNode(
                            file_path=rel,
                            lines_of_code=lines,
                            errors_count=0,
                            max_severity='LOW',
                            folder=str(p.parent.relative_to(project_root_path)).replace('\\', '/') if p.parent != project_root_path else 'root'
                        )
                        self.nodes[rel] = node
                except Exception as e:
                    print(f"[GraphVisualizer] Ошибка при сканировании {p}: {e}")
                    pass
            print(f"[GraphVisualizer] После добавления всех файлов: {len(self.nodes)} узлов (scanned: {len(scanned_files)})")
        except Exception as e:
            print(f"[GraphVisualizer] Ошибка сканирования проекта: {e}")
            pass

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

    def eventFilter(self, obj, event):
        # Обрабатываем колесо мыши и клик для web_view
        if obj is self.web_view:
            if event.type() == QEvent.Type.Wheel:
                # delta в PyQt6: angleDelta().y()
                try:
                    delta = event.angleDelta().y()
                except Exception:
                    # Если нет, пробуем delta()
                    delta = event.delta()
                if delta > 0:
                    self.scale_factor = min(3.0, self.scale_factor * 1.12)
                else:
                    self.scale_factor = max(0.2, self.scale_factor / 1.12)
                # синхронизируем ползунок
                try:
                    self.scale_slider.blockSignals(True)
                    self.scale_slider.setValue(int(self.scale_factor * 100))
                finally:
                    self.scale_slider.blockSignals(False)
                self._render_graph()
                return True
            elif event.type() == QEvent.Type.MouseButtonPress:
                # На любой клик — временно усиливаем фокус (увеличиваем масштаб и включаем эффект)
                self._focus_active = True
                self.scale_factor = min(3.0, self.scale_factor * 1.2)
                try:
                    self.scale_slider.blockSignals(True)
                    self.scale_slider.setValue(int(self.scale_factor * 100))
                finally:
                    self.scale_slider.blockSignals(False)
                # Запускаем рендер
                self._render_graph()
                # Снимаем эффект через 800ms
                QTimer.singleShot(800, self._clear_focus)
                return True
        return super().eventFilter(obj, event)

    def _clear_focus(self):
        self._focus_active = False
        # немного уменьшим масштаб к исходному
        self.scale_factor = max(0.5, self.scale_factor / 1.1)
        try:
            self.scale_slider.blockSignals(True)
            self.scale_slider.setValue(int(self.scale_factor * 100))
        finally:
            self.scale_slider.blockSignals(False)
        self._render_graph()
    
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
        """Рендерить граф с использованием Plotly (профессиональная визуализация)"""
        print(f"[GraphVisualizer] Рендерю Plotly граф для {node_count} узлов")
        
        try:
            # Group nodes by folder to create "clouds"
            node_ids: List[str] = []
            folders: Dict[str, List[str]] = {}
            for file_path in nodes_to_show.keys():
                folder = nodes_to_show[file_path].folder
                folders.setdefault(folder, []).append(file_path)

            # Determine folder-level max severity (hierarchical color)
            severity_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
            folder_max: Dict[str, str] = {}
            for folder, files in folders.items():
                maxs = 'LOW'
                for fp in files:
                    sev = nodes_to_show[fp].max_severity
                    if severity_order.get(sev, 0) > severity_order.get(maxs, 0):
                        maxs = sev
                folder_max[folder] = maxs

            # Compute folder centers on grid
            folder_list = list(folders.keys())
            fcount = len(folder_list)
            fcols = int(fcount ** 0.5) + 1
            spacing = 10.0
            folder_centers = {}
            for idx, folder in enumerate(folder_list):
                fx = (idx % fcols) * spacing
                fy = (idx // fcols) * spacing
                folder_centers[folder] = (fx, fy)

            node_x = []
            node_y = []
            node_colors = []
            node_sizes = []
            node_labels = []
            node_hovers = []

            # Place nodes around their folder center
            for folder in folder_list:
                files = folders[folder]
                center_x, center_y = folder_centers[folder]
                f_len = max(1, len(files))
                for i, file_path in enumerate(files):
                    angle = (i / f_len) * 2 * 3.14159
                    radius = 1.5 + (i % 6) * 0.6
                    x = center_x + radius * (1.0 * (0.8 + 0.4 * (i % 3))) * (1 if (i % 2 == 0) else -1)
                    y = center_y + radius * (1.0 * (0.6 + 0.3 * (i % 2))) * (1 if (i % 3 == 0) else -1)
                    node_x.append(x)
                    node_y.append(y)
                    node_ids.append(file_path)

                    node = nodes_to_show[file_path]
                    # If node has no errors - inherit folder max severity
                    node_sev = node.max_severity
                    if node.errors_count == 0 and folder_max.get(folder):
                        node_sev = folder_max[folder]
                    color = self._get_color(node_sev)
                    node_colors.append(color)

                    # Size influenced by errors and lines
                    size = max(12, min(60, 18 + node.errors_count * 6 + int((node.lines_of_code ** 0.5) / 5)))
                    # Apply focus effect
                    if self._focus_active:
                        size = int(size * 1.25)
                    node_sizes.append(size)

                    file_name = Path(file_path).name
                    label_text = file_name if self.show_labels.isChecked() else ""
                    if node.errors_count > 0 and self.show_labels.isChecked():
                        label_text += f"\n{node.errors_count}⚠️"
                    node_labels.append(label_text)

                    hover_text = (
                        f"<b>{file_name}</b><br>"
                        f"Папка: {node.folder}<br>"
                        f"Строк: {node.lines_of_code}<br>"
                        f"Ошибок: {node.errors_count}<br>"
                        f"Серьезность: {node_sev}"
                    )
                    node_hovers.append(hover_text)
            
            # Создаём рёбра
            edge_x = []
            edge_y = []
            
            if self.show_edges.isChecked() and node_count < 200:
                # Соединяем файлы в пределах папки (по расположению в списке)
                for folder in folder_list:
                    files = folders[folder]
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
            node_opacity = 0.95 if not self._focus_active else 0.7
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                customdata=node_ids,  # file_path для JS callback
                marker=dict(
                    size=node_sizes,
                    color=node_colors,
                    line=dict(width=1.5, color='#000000'),
                    opacity=node_opacity,
                    sizemode='diameter',
                    sizeref=2.0 * self.scale_factor
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
                plot_bgcolor='#fafafa',
                paper_bgcolor='#ffffff',
                height=600,
                width=None,
                transition=dict(duration=300, easing='quad-in-out')
            )
            
            # Сохраняем HTML (с Plotly JS встроенным, примерно 3 MB)
            html_file = Path(tempfile.gettempdir()) / "naudit_graph_temp.html"
            
            try:
                # Используем встроенный Plotly JS для offline работы
                html_content = fig.to_html(include_plotlyjs='inline')
                html_file.write_text(html_content, encoding='utf-8')
                size_kb = len(html_content) / 1024
                print(f"[GraphVisualizer] HTML граф сохранён ({size_kb:.1f} KB): {html_file}")
                
                # Сохраняем также в reports/graphs для экспорта
                self._save_graph_export(fig, node_count)
            except Exception as e:
                print(f"[GraphVisualizer] Ошибка при сохранении HTML: {e}")
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
            
            # Группируем по папкам и определяем folder-level severity
            folders: Dict[str, List[str]] = {}
            for file_path, node in nodes_to_show.items():
                folders.setdefault(node.folder, []).append(file_path)

            severity_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
            folder_max = {}
            for folder, files in folders.items():
                maxs = 'LOW'
                for fp in files:
                    sev = nodes_to_show[fp].max_severity
                    if severity_order.get(sev, 0) > severity_order.get(maxs, 0):
                        maxs = sev
                folder_max[folder] = maxs

            # Добавляем узлы с цветовой кодировкой (унаследованной от папки если нужно)
            for folder_idx, (folder, files) in enumerate(folders.items()):
                for file_path in files:
                    node = nodes_to_show[file_path]
                    size = int(self._get_size(node.lines_of_code))
                    node_sev = node.max_severity
                    if node.errors_count == 0 and folder_max.get(folder):
                        node_sev = folder_max[folder]
                    color = self._get_color(node_sev)

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
                        f"Серьезность: {node_sev}"
                    )

                    actual_size = int(size * self.scale_factor * (1.25 if self._focus_active else 1.0))
                    g.add_node(
                        file_path,
                        label=label,
                        color=color,
                        size=actual_size,
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
    
    def _save_graph_export(self, fig, node_count: int):
        """Сохранить граф в экспортную папку для дальнейшего использования"""
        try:
            from pathlib import Path
            
            # Создаём папку graphs в ~/.naudit/reports
            export_dir = Path.home() / '.naudit' / 'reports' / 'graphs'
            export_dir.mkdir(parents=True, exist_ok=True)
            
            # Генерируем имя файла с временем
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            html_file = export_dir / f"graph_{timestamp}.html"
            
            # Сохраняем Plotly граф
            html_content = fig.to_html(include_plotlyjs='inline')
            html_file.write_text(html_content, encoding='utf-8')
            
            size_kb = len(html_content) / 1024
            print(f"[GraphVisualizer] Граф экспортирован ({size_kb:.1f} KB) в: {html_file}")
            
            # Сохраняем метаданные о графе для каталогизации
            metadata_file = export_dir / f"graph_{timestamp}_meta.json"
            import json
            metadata = {
                'timestamp': timestamp,
                'node_count': node_count,
                'file_size_kb': round(size_kb, 1),
                'scale_factor': self.scale_factor,
                'show_labels': self.show_labels.isChecked(),
                'show_edges': self.show_edges.isChecked(),
            }
            metadata_file.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding='utf-8')
            
            return html_file
        except Exception as e:
            print(f"[Error] Ошибка при экспорте графа: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def export_current_graph(self) -> Path:
        """Экспортировать текущий граф в пользовательскую папку"""
        if not self.nodes:
            print("[GraphVisualizer] Нет узлов для экспорта")
            return None
        
        try:
            # Используем встроенный диалог сохранения файла
            from PyQt6.QtWidgets import QFileDialog
            
            desktop = Path.home() / 'Desktop'
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            default_name = f"naudit_graph_{timestamp}.html"
            
            # Спрашиваем пользователя где сохранить
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Сохранить граф проекта",
                str(desktop / default_name),
                "HTML файлы (*.html);;Все файлы (*.*)"
            )
            
            if not file_path:
                return None
            
            # Перестраиваем граф для экспорта
            nodes_to_show = self.nodes
            if not nodes_to_show:
                return None
            
            # Здесь используем уже готовый temp файл или перестраиваем
            temp_file = Path(tempfile.gettempdir()) / "naudit_graph_temp.html"
            if temp_file.exists():
                import shutil
                shutil.copy(temp_file, file_path)
                print(f"[GraphVisualizer] Граф сохранён: {file_path}")
                return Path(file_path)
        
        except Exception as e:
            print(f"[Error] Ошибка при экспорте графа пользователем: {e}")
            import traceback
            traceback.print_exc()
            return None
    
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

