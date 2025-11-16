# Graph Visualizer v2.6 — изменения и руководство

Краткое описание

- Файл: `n_audit/gui/graph_visualizer_v2_6.py`
- Цель: стабильная интерактивная визуализация зависимостей проекта с группировкой по папкам, поддержкой Plotly и PyVis, и опциональной GPU-ускоренной раскладкой.

Основные возможности

- Группировка по полному относительному пути папки (пример: `src/utils/`).
- Цвета папок автоматически назначаются и сохраняются в `folder_colors`.
- Узлы содержат `customdata` (реальный путь) для надежной синхронизации JS -> Python через QWebChannel.
- JS-обработчики для Plotly и PyVis вызывают `graph_bridge.onNodeClicked(path)`.
- Опциональный GPU layout: внутренняя реализация на PyTorch (если доступен CUDA), автоматический fallback на NetworkX.
- Простая индикация прогресса: `QProgressDialog` показывается во время генерации HTML (лениво создается).

Примечания по использованию

1. Запуск аудита и отображение графа
   - После получения отчета (AuditReport) вызвать:
     - `widget.populate_from_report(report, project_root)`
   - Виджет сам просканирует проект, соберет файлы, создаст узлы и связи и отобразит граф.

2. Синхронизация дерево ↔ граф
   - При клике на узел в графе вызывается сигнал `file_selected` (emit) с относительным путём файла.
   - При выборе файла в дереве можно вызывать `graph_widget.highlight_file(path)` или `graph_widget.focus_on_node(path)`.

3. GPU ускорение
   - Если доступен PyTorch и CUDA, библиотека попытается использовать `_compute_layout_torch` для ускорения расчёта позиций.
   - В логах выводится информация `GPU available: True/False`.

4. Проблемы в собранном exe
   - QWebEngine требует корректной инициализации: перед созданием `QApplication` важно установить
     `QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)` если используется WebEngine.
   - Для PyInstaller убедитесь, что hook'и для PyQt6 и Qt WebEngine включены, а также собрать ресурсы для PyVis/Plotly (если используете оффлайн-нагружаемые файлы).

5. Отладка и логи
   - Smoke-run: `smoke_run_cs_market_bot.py` (в корне проекта) запускает аудит на целевом проекте и пишет лог в `%USERPROFILE%\.naudit\logs\latest.log`.


Контракт (inputs/outputs)

- Вход: `AuditReport` (объект из `n_audit.audit_engine`), `project_root` — строка пути
- Выход: наполнение `self.nodes`, `self.edges`, `self.folder_colors` и отрисованный HTML в `QWebEngineView`.

Edge cases и рекомендации

- Проекты без Python-файлов: генерируется «нет узлов» информационная страница.
- Большие проекты (>300 файлов): рекомендовано включать GPU-ускорение или перенос рендера в фон (QThread) — планируется как отдельное улучшение.

