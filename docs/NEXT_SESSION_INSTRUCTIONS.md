# Инструкции для следующей сессии

## 📌 Текущее состояние (v3)

✅ **PRODUCTION READY**
- Все баги исправлены
- 3/3 тесты пройдены
- .exe собран и работает
- Документация полная

## 🎯 Когда и что тестировать

### Если нужно:
1. **Быстро проверить функциональность**: запустить `test_audit_v2_diagnostic.py`
2. **Проверить новые изменения**: обновить тесты в `test_audit_v2_diagnostic.py`
3. **Пересобрать .exe**: запустить `build_exe_simple.py`

### Если что-то сломалось:
1. Проверить логи в Tab 4 (Логи)
2. Запустить диагностику: `python test_audit_v2_diagnostic.py`
3. Смотреть в файл `.audit_results/reports/` целевого проекта

## 🔧 Частые модификации

### Добавить новый анализатор:
1. Создать файл в `n_audit/new_tool.py`
2. Добавить фазу в `audit_manager_v2.py` (строка ~260)
3. Добавить парсинг результатов в `_load_results()` (строка ~380)
4. Пересобрать: `python build_exe_simple.py`

### Улучшить GUI:
1. Редактировать `n_audit/gui/main_window_v3.py`
2. Пересобрать: `python build_exe_simple.py`

### Изменить формулу рейтинга:
1. Редактировать `_calculate_rating()` в `audit_manager_v2.py`
2. Обновить `test_audit_v2_diagnostic.py` если нужно
3. Пересобрать: `python build_exe_simple.py`

## 🚀 Команды для разработки

```bash
# Активировать виртуальное окружение
.\v.naudit\Scripts\Activate.ps1

# Запустить диагностику
python test_audit_v2_diagnostic.py

# Запустить GUI из источника
python -m n_audit.gui.main_app

# Пересобрать .exe
python build_exe_simple.py

# Запустить .exe
.\dist\nAUDIT_v3.exe

# Проверить синтаксис Python
python -m py_compile n_audit/audit_manager_v2.py
python -m py_compile n_audit/gui/main_window_v3.py
```

## 📝 Важные переменные окружения

```powershell
# Для правильной кодировки вывода
$env:PYTHONIOENCODING='utf-8'

# Для отладки (если нужно)
$env:PYTHONUNBUFFERED='1'
```

## 🐛 Типовые баги и как их исправлять

### Bug: "ModuleNotFoundError: No module named 'n_audit'"
**Решение:** Убедиться, что работаешь из папки `G:\CODING\nAUDIT`

### Bug: "ImportError: PyQt6 not found"
**Решение:** Активировать виртуальное окружение: `.\v.naudit\Scripts\Activate.ps1`

### Bug: "No module named 'matplotlib'"
**Решение:** Пересобрать .exe: `python build_exe_simple.py`

### Bug: "has_code always False"
**Решение:** Проверить функцию `_find_python_files()` в `audit_manager_v2.py`

### Bug: "Рейтинг не изменяется"
**Решение:** Убедиться что `has_code` флаг правильно установлен (проверить лог Tab 4)

## 🎨 Структура для новых фич

### Добавить новую вкладку в GUI:
```python
# В main_window_v3.py, после создания tabs:
new_tab = QWidget()
new_layout = QVBoxLayout()
# ... добавить виджеты ...
new_tab.setLayout(new_layout)
self.tabs.addTab(new_tab, "📌 Новая вкладка")
```

### Добавить новый callback:
```python
# В audit_manager_v2.py, в __init__:
self.on_new_callback: Optional[Callable] = None

# При вызове:
if self.on_new_callback:
    self.on_new_callback(data)

# В GUI:
manager.on_new_callback = lambda data: self.handle_new_callback(data)
```

## 🔍 Файлы для быстрого понимания

1. **Начать с** `n_audit/audit_manager_v2.py` - основная логика
2. **Затем** `n_audit/gui/main_window_v3.py` - интерфейс
3. **Потом** `build_exe_simple.py` - сборка
4. **В конце** `test_audit_v2_diagnostic.py` - тесты

## 📊 Метрики качества для поддержки

- **Время сборки**: ~2-3 минуты
- **Размер .exe**: должен быть ~130 MB
- **Время анализа** на n_audit: 1-2 минуты
- **Занимаемая память**: ~300-500 MB во время работы

Если значительно выше - есть утечка памяти или проблема с производительностью.

## 🎓 Документация для прочтения

В порядке приоритета:
1. `QUICKSTART_V3.md` - как запустить
2. `SESSION_REPORT_V3_FINAL.md` - что было сделано
3. `CHECKLIST_V3.md` - проверочный список
4. `docs/V3_IMPLEMENTATION_NOTES.md` - технические детали
5. `copilot-instructions.md` - общие правила проекта

## ✅ Перед деплоем

- [ ] Все тесты пройдены: `python test_audit_v2_diagnostic.py`
- [ ] Нет синтаксических ошибок: `python -m py_compile n_audit/*.py`
- [ ] .exe собран: `python build_exe_simple.py`
- [ ] .exe запускается: `.\dist\nAUDIT_v3.exe`
- [ ] Документация обновлена

## 🚨 Emergency Recovery

Если все сломалось:

```bash
# Очистить кэш Python
rm -r n_audit/__pycache__ n_audit/gui/__pycache__

# Пересобрать виртуальное окружение
rm -r v.naudit
python -m venv v.naudit
.\v.naudit\Scripts\Activate.ps1
pip install -r requirements.txt

# Пересобрать .exe с нуля
rm -r build dist *.spec
python build_exe_simple.py
```

## 📞 Важные контакты кода

- **Если ошибка при парсинге результатов**: смотреть `_load_results()` в `audit_manager_v2.py`
- **Если не работает callback**: смотреть `on_result` в `audit_manager_v2.py` и `_on_audit_complete()` в `main_window_v3.py`
- **Если GUI не обновляется**: смотреть `AuditSignals` в `main_window_v3.py`
- **Если .exe не собирается**: смотреть `build_exe_simple.py` и логи PyInstaller

---

Дата: 13 ноября 2025  
Версия: v3  
Статус: Production Ready  
Следующий шаг: Опциональная оптимизация производительности
