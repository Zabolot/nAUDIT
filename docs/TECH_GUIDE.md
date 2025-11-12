# Техническая документация nAUDIT 2.0

## Архитектура

### Структура проекта

```
nAUDIT/
├── n_audit/
│   ├── __init__.py
│   ├── main.py                 # Точка входа CLI
│   ├── core.py                 # Основной управляющий модуль
│   ├── audit_manager.py        # Менеджер аудита (асинхронный)
│   ├── code_analysis.py        # Статический анализ кода
│   ├── security.py             # Проверка безопасности
│   ├── tests_analysis.py       # Анализ тестов
│   ├── infrastructure.py       # Проверка инфраструктуры
│   ├── recommendations.py      # Генерация рекомендаций
│   ├── visualizations.py       # Визуализации
│   ├── utils.py                # Утилиты
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_app.py         # Точка входа GUI
│   │   ├── main_window.py      # Главное окно (PyQt6)
│   │   └── styles.py           # Стили оформления
│   └── plugins/
│       └── sample_plugin.py    # Пример плагина
├── docs/
│   ├── USER_GUIDE.md           # Руководство пользователя
│   └── TECH_GUIDE.md           # Техническая документация
├── build_exe.py                # Скрипт сборки .exe
├── build_exe.ps1               # PowerShell сборщик
├── pyproject.toml              # Конфигурация проекта
├── requirements.txt            # Зависимости
└── README.md                   # Основная документация
```

### Компоненты системы

#### 1. Core модуль (core.py)

**Ответственность**: Оркестрация всех модулей аудита, управление директориями результатов

**Функции**:
- `setup_directories()` - создание директорий для результатов
- `load_plugins()` - загрузка пользовательских плагинов
- `run_all_checks(args)` - запуск полного аудита
- `generate_report()` - формирование итогового отчёта

#### 2. Audit Manager (audit_manager.py)

**Ответственность**: Управление асинхронным выполнением аудита, интеграция с GUI

**Ключевые классы**:
- `AuditStatus` (Enum) - статусы аудита
- `AuditPhase` (dataclass) - информация о фазе
- `AuditResult` (dataclass) - результаты аудита
- `AuditManager` - основной класс управления

**Особенности**:
- Многопоточность (threading)
- Обратные вызовы (callbacks) для GUI
- Отмена аудита в любой момент
- Прогрессирование по фазам

#### 3. Анализ кода (code_analysis.py)

**Инструменты**:
- `radon` - цикломатическая сложность
- `pylint` - статический анализ, стиль
- `flake8` - PEP8 проверка
- `mypy` - проверка типов

**Выход**: JSON файлы с результатами

#### 4. Проверка безопасности (security.py)

**Инструменты**:
- `bandit` - проверка уязвимостей кода
- `safety` - проверка уязвимостей зависимостей
- `gitleaks` - поиск секретов

**Выход**: JSON с категоризацией проблем

#### 5. Анализ тестов (tests_analysis.py)

**Инструменты**:
- `pytest` - запуск тестов
- `coverage` - анализ покрытия

**Выход**: JSON с метриками покрытия

#### 6. Проверка инфраструктуры (infrastructure.py)

**Проверяемые элементы**:
- Зависимости проекта
- Конфигурационные файлы
- Docker конфигурация
- SQL файлы (sqlfluff)
- Информация об окружении

#### 7. Рекомендации (recommendations.py)

**Функция**: Анализ результатов аудита и генерация конкретных рекомендаций

**Логика**:
- Анализ кода - рефакторинг высокосложных функций
- Безопасность - исправление уязвимостей
- Тесты - улучшение покрытия
- Общие рекомендации

#### 8. GUI (gui/)

**Технология**: PyQt6 (Python Qt bindings)

**Компоненты**:
- `main_app.py` - точка входа
- `main_window.py` - главное окно с 3 вкладками
- `styles.py` - современный минималистичный стиль

**Вкладки**:
1. Аудит - выбор проекта, параметры, запуск, лог
2. Результаты - оценка, статистика, рекомендации
3. Справка - встроенная документация

## Поток данных

```
Пользователь выбирает папку
    ↓
GUI → audit_manager.configure()
    ↓
audit_manager.start_audit_async() (создаёт отдельный поток)
    ↓
core.run_all_checks()
    ├─→ code_analysis.run() (radon, pylint, flake8, mypy)
    ├─→ security.run() (bandit, safety)
    ├─→ tests_analysis.run() (pytest, coverage)
    ├─→ infrastructure.run() (Docker, SQL, env)
    ├─→ recommendations.generate_advices()
    └─→ core.generate_report()
    ↓
Результаты сохраняются в JSON/HTML
    ↓
audit_manager вызывает callbacks
    ↓
GUI обновляет результаты на вкладке
```

## Интеграция с GUI

### Асинхронное выполнение

```python
# GUI запускает аудит
worker = AuditWorker(audit_manager)
worker_thread = QThread()
worker.moveToThread(worker_thread)

# Подключение сигналов
worker_thread.started.connect(worker.run_audit)
worker.progress_updated.connect(on_progress)
worker.phase_updated.connect(on_phase)
worker.audit_completed.connect(on_complete)
worker.audit_error.connect(on_error)

# Запуск
worker_thread.start()
```

### Обратные вызовы

```python
audit_manager.set_callbacks(
    on_progress=lambda progress, msg: print(f"{progress}%: {msg}"),
    on_phase_update=lambda phase: print(f"Фаза: {phase.name}"),
    on_complete=lambda result: display_results(result),
    on_error=lambda err: show_error_dialog(err)
)
```

## Создание пользовательских плагинов

### Структура плагина

```python
# plugins/my_plugin.py

def run_plugin_checks(args, reports_dir):
    """
    Функция плагина.
    args: объект с параметрами аудита
    reports_dir: папка для сохранения результатов
    """
    print("[PLUGIN] Выполнение моей проверки...")
    
    # Выполняем проверку
    results = {
        "checks_performed": 5,
        "issues_found": 2
    }
    
    # Сохраняем результаты
    import json
    with open(f"{reports_dir}/my_plugin.json", "w") as f:
        json.dump(results, f)
    
    print("[PLUGIN] ✓ Проверка завершена")
```

### Регистрация плагина

Просто поместите файл в папку `n_audit/plugins/` и он будет загружен автоматически.

## Стили и темирование

### Цветовая схема

```python
COLORS = {
    "primary": "#2563EB",      # Основной синий
    "success": "#10B981",      # Зелёный для успеха
    "warning": "#F59E0B",      # Оранжевый для предупреждения
    "danger": "#EF4444",       # Красный для ошибок
    "neutral": "#6B7280",      # Серый для нейтрального
}
```

### Стилизация элементов

Все стили хранятся в `gui/styles.py` и применяются в виде CSS для Qt:

```python
# Применение стиля
self.setStyleSheet(MAIN_STYLESHEET)
```

## Сборка .exe файла

### Процесс сборки

1. **build_exe.py** - основной скрипт сборки
2. **build_exe.ps1** - PowerShell обертка для Windows

### PyInstaller конфигурация

```python
# Скрытые импорты (которые PyInstaller не может обнаружить автоматически)
hidden_imports = [
    "PyQt6.QtCore",
    "PyQt6.QtGui",
    "PyQt6.QtWidgets",
    "n_audit.core",
    # и т.д.
]

# Команда сборки
pyinstaller --onefile --windowed --name=nAUDIT \
    --hidden-import=PyQt6.QtCore \
    n_audit/gui/main_app.py
```

## Производительность и оптимизация

### Многопоточность

- Аудит выполняется в отдельном потоке, не блокируя UI
- Каждая фаза может быть паузирована/отменена

### Кэширование

- Результаты аудита сохраняются в `.audit_results/`
- История аудитов хранится в `audit_history.json`

### Оптимизация внешних инструментов

- Использование JSON формата для максимальной производительности
- Таймауты для всех внешних процессов (30-120 сек)
- Параллельный запуск независимых проверок

## Отладка

### Включение подробного логирования

```python
audit_manager.configure(
    target_path="/path/to/project",
    verbose=True  # Включить подробные логи
)
```

### Логирование ошибок

```python
# В audit_manager.py
if self.verbose:
    import traceback
    print(traceback.format_exc())
```

## Тестирование

### Модульные тесты

```bash
pytest tests/ -v
```

### Проверка покрытия

```bash
coverage run -m pytest tests/
coverage report
```

## Известные ограничения

1. **pylint** может давать ложные предупреждения для динамических конструкций
2. **bandit** может пропускать некоторые уязвимости, требующих контекста
3. **Docker** проверки требуют установленного Docker на машине
4. **Большие проекты** (>5000 файлов) могут выполняться долго

## Будущие улучшения

- [ ] Параллельный запуск проверок
- [ ] Интеграция с Git для отслеживания изменений
- [ ] WebUI версия
- [ ] Интеграция с IDE (VS Code, PyCharm)
- [ ] Machine Learning для предсказания проблем
- [ ] Облачная синхронизация результатов

---

**Версия**: 2.0
**Последнее обновление**: 2025-01-13
