# КОМПЛЕКСНЫЙ ФИКСЕР: GPU + Дерево ошибок + Синхронизация

## Проблема 1: GPU не обнаруживается в exe

### Корень проблемы
- PyTorch установлен в требованиях, но возможна проблема с инициализацией CUDA
- Функция `detect_gpu()` статическая и может не быть правильно вызвана

### Решение
1. Добавить детальное логирование GPU detection
2. Добавить fallback на прямую проверку через ctypes
3. Убедиться что PyInstaller правильно упаковывает torch.cuda

## Проблема 2: Ошибки не отображаются в дереве

### Корень проблемы
- Функция `populate_from_report()` существует и логирует корректно
- Возможно, дерево не очищается правильно или не вызывается `_build_file_tree()`

### Решение
1. Добавить явный вызов `_build_file_tree()` в конце `populate_from_report()`
2. Убедиться что `clear()` полностью чищит дерево
3. Добавить проверку на пустой список ошибок

## Проблема 3: Синхронизация дерева и графов

### Текущее состояние
- ErrorTreeWidget имеет сигнал `file_selected`
- ErrorVisualizationWidget имеет сигнал `file_selected`
- GraphVisualizerWidget должен прослушивать этот сигнал

### Решение
1. Добавить метод `highlight_file()` в GraphVisualizerWidget
2. Подключить сигнал `file_selected` дерева к методу графа
3. Добавить обратный сигнал от графа к дереву для двусторонней синхронизации

---

## Файлы для изменения
1. `n_audit/gui/gpu_detector.py` - Улучшить GPU detection
2. `n_audit/gui/tree_widget.py` - Исправить populate_from_report
3. `n_audit/gui/graph_visualizer_v2_6.py` - Добавить highlight_file
4. `n_audit/gui/error_visualization.py` - Добавить синхронизацию
5. `n_audit/gui/main_window_v4.py` - Проверить вызовы
