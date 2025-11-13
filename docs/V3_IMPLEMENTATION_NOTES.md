# Информация для будущих сессий

## 🔍 Архитектура v3

### Основной поток анализа:
```
main_app.py (точка входа)
    ↓
main_window_v3.py (GUI)
    ↓
audit_manager_v2.py (менеджер)
    ├── _find_python_files() - обнаружение кода
    ├── _run_audit() - запуск 6 фаз (ASYNC в потоке)
    │   ├── code_analysis.run()
    │   ├── security.run()
    │   ├── tests_analysis.run()
    │   ├── infrastructure.run()
    │   ├── recommendations.generate_advices()
    │   └── _load_results() - парсинг результатов
    └── on_result callback - возврат результата
```

### Критические файлы:
- `n_audit/audit_manager_v2.py` - логика анализа (576 строк)
- `n_audit/gui/main_window_v3.py` - интерфейс (700+ строк)
- `n_audit/gui/main_app.py` - точка входа
- `build_exe_simple.py` - сборка PyInstaller

### Зависимости:
- PyQt6 6.10.0 - GUI
- matplotlib 3.10.1 - графики
- pylint, flake8, mypy - анализ кода
- bandit, safety - проверка безопасности
- coverage, pytest - тесты

---

## 🎯 Ключевые алгоритмы

### Обнаружение пустых проектов:
```python
py_files = self._find_python_files(target_path)
has_code = len(py_files) > 0
```

### Расчет рейтинга:
```python
if not has_code:
    return 2.0  # Критическая оценка для пустых проектов

base = 10.0
code_penalty = min(0.3 * code_errors, 5.0)
security_penalty = min(0.8 * security_issues, 4.0)
coverage_bonus = 1.0 if coverage >= 80 else 0
rating = base - code_penalty - security_penalty + coverage_bonus
```

### Парсинг результатов:
```python
# pylint_full.json - список объектов с type, file, line, message
# vulnerabilities.json - количество уязвимостей
# coverage.json - процент покрытия тестами
```

---

## 🐛 Частые проблемы и решения

### Проблема: "UnicodeEncodeError: 'charmap' codec can't encode"
**Решение:**
```python
def _log(self, message: str):
    try:
        print(message, flush=True)
    except UnicodeEncodeError:
        print(message.encode('utf-8', errors='replace').decode('utf-8', errors='replace'), flush=True)
```

### Проблема: Результат всегда None
**Решение:** Использовать `on_result` callback, т.к. `_run_audit` выполняется в отдельном потоке:
```python
manager.on_result = lambda result: process(result)
manager.start_audit(path)
time.sleep(timeout)  # Ждём результата
```

### Проблема: Пустой экспорт JSON
**Решение:** Проверить пути к файлам результатов:
```python
reports_dir = os.path.join(target_path, ".audit_results", "reports")
# Файлы: pylint_full.json, security_issues.json, coverage.json
```

---

## 🔄 Следующие улучшения

### Краткосрочные (легко добавить):
- [ ] HTML экспорт (шаблон уже может быть в recommendations)
- [ ] Сравнение анализов (история + дельта)
- [ ] Фильтр проблем по типу
- [ ] Экспорт в CSV/Excel

### Среднесрочные (требует изменений):
- [ ] Параллельный анализ (использовать threading.Pool)
- [ ] Кэширование результатов
- [ ] Incremental анализ (только новые файлы)
- [ ] Интеграция с Git для анализа изменений

### Долгосрочные (архитектурные):
- [ ] REST API для запуска анализов
- [ ] WebUI вместо PyQt6
- [ ] Интеграция с CI/CD (GitHub Actions, GitLab CI)
- [ ] Хранение истории в БД (вместо JSON)
- [ ] Сравнение с эталонными метриками

---

## 📝 Структура данных

### AuditResult (dataclass):
```python
@dataclass
class AuditResult:
    total_issues: int              # Всего проблем
    code_issues: int               # Ошибки кода
    security_issues: int           # Уязвимости
    test_coverage: float           # % покрытия
    rating: float                  # 1.0-10.0
    recommendations: list          # 10 рекомендаций
    phases: Dict[str, Any]         # Статус каждой фазы
    issue_details: List[IssueDetail] # Детали каждой проблемы
    timestamp: str                 # Время анализа
    project_path: str              # Путь проекта
    files_analyzed: int            # Количество файлов
    python_files_count: int        # Python файлов
    has_code: bool                 # Есть ли Python код
    analysis_log: List[str]        # Логи анализа
```

### IssueDetail (dataclass):
```python
@dataclass
class IssueDetail:
    type: str                      # 'error', 'warning'
    file: str                      # Путь файла
    line: int                      # Строка
    column: int                    # Столбец
    message: str                   # Текст ошибки
    code: str                      # Код ошибки (E501, W291 и т.д.)
```

---

## 🧪 Как добавить новый анализатор

### Пример: интеграция новой утилиты

1. **Создать модуль** `n_audit/new_analyzer.py`:
```python
def run(args, reports_dir):
    # Запустить анализ
    results = some_tool.analyze(args.module)
    
    # Сохранить результаты
    output_file = os.path.join(reports_dir, "new_results.json")
    with open(output_file, 'w') as f:
        json.dump(results, f)
```

2. **Добавить фазу в audit_manager_v2.py**:
```python
try:
    self._log("🔍 Запуск new_analyzer.run()...")
    new_analyzer.run(args, reports_dir)
    self._log("✅ new_analyzer завершена")
except Exception as e:
    self._log(f"⚠️ Ошибка: {e}")
```

3. **Добавить парсинг результатов в _load_results()**:
```python
fpath = os.path.join(reports_dir, "new_results.json")
if os.path.exists(fpath):
    with open(fpath, 'r') as f:
        data = json.load(f)
    # Обработать data и добавить в issue_details
```

---

## 🛠️ Отладка

### Включить полную диагностику:
```python
# В audit_manager_v2.py уже есть полное логирование
# Включена функция _log() для всех операций
# Вывод в консоль + GUI Tab 4
```

### Проверить файлы результатов:
```bash
dir /s "project\.audit_results\reports\*"
type "project\.audit_results\reports\pylint_full.json" | head -20
```

### Отладить через Python:
```python
from n_audit.audit_manager_v2 import AuditManager

m = AuditManager()
m.verbose = True
m.start_audit("test_path")
# Добавить breakpoints в методы
```

---

## 📚 Ссылки на документацию

- SESSION_REPORT_V3_FINAL.md - полный отчет сессии
- QUICKSTART_V3.md - быстрый старт
- CHECKLIST_V3.md - проверочный список
- copilot-instructions.md - общие инструкции проекта

---

Последнее обновление: 13 ноября 2025
Версия: v3 (PRODUCTION READY)
