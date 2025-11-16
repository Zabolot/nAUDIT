# 🔍 nAUDIT v2.7.0

**Профессиональный инструмент для комплексного анализа качества Python-кода с мощной визуализацией и интеллектуальными рекомендациями**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![UI](https://img.shields.io/badge/UI-PyQt6-purple)](https://pypi.org/project/PyQt6/)
[![Visualization](https://img.shields.io/badge/Visualization-PyVis%20%2B%20Plotly-green)](https://pyvis.org)
[![Status](https://img.shields.io/badge/Status-Production-brightgreen)](https://github.com)
[![Version](https://img.shields.io/badge/Version-2.7.0-blue)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> 🚀 **v2.7.0** — Полная переработка граф-визуализации: отключение физики, GPU-ускорение (CUDA/torch), синхронизация Tree↔Graph, экспорт PyVis+Plotly HTML, фоновый рендеринг через QThread

## 📋 Содержание

- [🎯 Возможности](#-возможности)
- [🚀 Быстрый старт](#-быстрый-старт)
- [💻 Установка](#-установка)
- [📖 Использование](#-использование)
- [📊 Визуализация графов](#-визуализация-графов)
- [🔧 Конфигурация](#-конфигурация)
- [📚 Документация](#-документация)
- [🐛 Решение проблем](#-решение-проблем)
- [📦 Требования](#-требования)
- [🤝 Внесение вклада](#-внесение-вклада)
- [📜 Лицензия](#-лицензия)

---

## 🎯 Возможности

### Анализ кода

- **📊 Статический анализ** — проверка синтаксиса, стиля и сложности (radon, pylint, flake8, mypy)
- **🔒 Проверка безопасности** — поиск уязвимостей (bandit, safety)
- **🧪 Анализ тестов** — оценка покрытия тестами (pytest, coverage)
- **🏗️ Проверка инфраструктуры** — анализ Docker, SQL, зависимостей и конфигураций
- **💡 Интеллектуальные рекомендации** — персонализованные советы по исправлению

### Визуализация и экспорт

- **🌳 Трёхрежимный интерфейс**:
  - **Tree View** — иерархическое дерево файлов проекта
  - **Graph View** — интерактивная сетевая граф-визуализация (PyVis + Plotly)
  - **Split View** — одновременный просмотр дерева и графа
  
- **🖥️ Граф-визуализация v2.7**:
  - ✅ Отключение physics для стабильности (D3.js force simulation выключена)
  - ✅ GPU-ускорение (CUDA/torch для быстрого layout)
  - ✅ Синхронизация Tree↔Graph (клик в дереве → подсвечивание в графе)
  - ✅ Фоновый рендеринг (QThread для неблокирующего UI)
  - ✅ Экспорт двух форматов (PyVis HTML + Plotly HTML)

- **💾 Экспорт**:
  - HTML отчёты (PyVis и Plotly форматы)
  - JSON экспорт для автоматизации
  - Сохранение графов в браузер-совместимом формате

### Интерфейс и производительность

- **🖱️ Современный GUI** — минималистичный интерфейс на PyQt6
- **⚡ Высокая производительность** — оптимизированная работа с большими проектами (1000+ файлов)
- **📱 Отзывчивый интерфейс** — фоновые потоки (QThread) не замораживают UI
- **📦 Портативная установка** — полный .exe файл (379.5 МБ) для Windows

---

## 🚀 Быстрый старт

### ⚡ Вариант 1: Готовый .exe файл (рекомендуется для Windows)

1. Скачайте **nAUDIT.exe** (379.5 МБ) из [Releases](https://github.com/username/nAUDIT/releases)
2. Дважды щелкните для запуска
3. Первый запуск инициализирует БД (10-30 сек)

```bash
# Проверка работы:
nAUDIT.exe --help
```

### 🔨 Вариант 2: Сборка из исходников

```bash
# Клонируйте репозиторий
git clone https://github.com/username/nAUDIT.git
cd nAUDIT

# Создайте виртуальное окружение
python -m venv venv

# Активируйте окружение
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Запустите GUI
python -m n_audit.gui.main_window

# Или соберите .exe
python build_exe.py
```

### 📦 Вариант 3: Установка через pip (скоро)

```bash
pip install nAUDIT
naudit-gui

# Или используйте CLI
naudit --module /path/to/project --report-level full
```

---

## 💻 Установка

### Требования

| Параметр | Требование | Рекомендуется |
|----------|-----------|---------------|
| **Python** | 3.8+ | 3.10, 3.11, 3.12 |
| **ОС** | Windows/Linux/macOS | Windows 10+ |
| **RAM** | 2 ГБ | 4+ ГБ |
| **Свободное место** | 200 МБ | 500 МБ |
| **GPU (опционально)** | NVIDIA | RTX 3000 series+ |

### Установка зависимостей

```bash
# Базовая установка
pip install -r requirements.txt

# С GPU-поддержкой
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt

# Для разработки (с тестами и линтерами)
pip install -r requirements-dev.txt
```

### Конфигурация GPU (опционально)

```bash
# Проверьте CUDA установку
nvidia-smi

# Установите PyTorch с CUDA поддержкой
pip install torch --index-url https://download.pytorch.org/whl/cu118

# Проверьте в nAUDIT: Settings → Graph Rendering → "Use GPU Acceleration"
```

---

## 📖 Использование

### Графический интерфейс

```bash
# Запуск GUI
python -m n_audit.gui.main_window

# Или (когда установлено через pip):
naudit-gui
```

**Структура интерфейса:**

```
┌─────────────────────────────────────────┐
│  nAUDIT v2.7.0                     ⚙️   │
├──────────┬──────────────────────────────┤
│ 📁 Проект│  Выберите папку проекта   📂 │
│          │  Исключить: *.pyc, __pycache_│
├──────────┼──────────────────────────────┤
│ 📊 Аудит │  ▶️ Начать аудит   ⏹️ Отмена │
│          │  Подробный отчёт □          │
├──────────┼──────────────────────────────┤
│ 📈 Граф  │  🌳 Tree  🕸️ Graph  ✂️ Split │
│          │  📤 Экспорт                 │
├──────────┴──────────────────────────────┤
│  Статус: Готово  [████████░░] 80%      │
└─────────────────────────────────────────┘
```

**Вкладки:**

1. **Аудит** — выбор проекта и запуск анализа
2. **Результаты** — просмотр оценки и рекомендаций
3. **Граф** — визуализация зависимостей
4. **Справка** — встроенная документация

### Командная строка

```bash
# Полный анализ с экспортом
naudit --module /path/to/project \
       --exclude "*.pyc,__pycache__" \
       --report-level detailed \
       --export-format html,json \
       --verbose

# Быстрый анализ (краткий отчет)
naudit --module . --report-level brief

# Анализ с сохранением в файл
naudit --module . --output report.json
```

**Доступные флаги:**

```
--module PATH              Путь к проекту (обязательно)
--exclude PATTERNS         Исключить файлы (glob patterns)
--report-level LEVEL       brief | full | detailed (по умолчанию: full)
--export-format FORMAT     html | json | both (по умолчанию: html)
--output FILE              Путь для сохранения отчета
--verbose, -v              Подробное логирование
--timeout SECONDS          Таймаут для анализа (по умолчанию: 300)
--config FILE              Путь к конфиг-файлу
```

### Интеграция в CI/CD

#### GitHub Actions

```yaml
name: Code Audit

on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install nAUDIT
        run: pip install nAUDIT
      
      - name: Run Code Audit
        run: |
          naudit --module . \
                 --report-level detailed \
                 --export-format json \
                 --output audit-result.json
      
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: audit-report
          path: audit-result.json
```

#### GitLab CI

```yaml
code_audit:
  image: python:3.11
  script:
    - pip install nAUDIT
    - naudit --module . --export-format json
  artifacts:
    reports:
      audit: audit-result.json
```

---

## 📊 Интерпретация результатов

### Шкала оценки качества (1-10)

| Оценка | Статус | Цвет | Действие |
|--------|--------|------|----------|
| 9-10 | ✅ **Отличное** | 🟢 Зелёный | Поддерживайте уровень |
| 7-8 | ✔️ **Хорошее** | 🟢 Зелёный | Незначительные улучшения |
| 5-6 | ⚠️ **Среднее** | 🟡 Жёлтый | Требуется улучшение |
| 3-4 | ❌ **Низкое** | 🟠 Оранжевый | Срочная переработка |
| 1-2 | 🔴 **Критическое** | 🔴 Красный | Полная переделка |

### Категории проблем

**Ошибки кода** — Критичность: 🔴 Высокая
```
- Синтаксические ошибки
- Undefined variables
- Type mismatches (mypy)
- Import errors
```

**Проблемы безопасности** — Критичность: 🔴 Высокая
```
- SQL injection risks
- Hardcoded credentials
- Unsafe deserialization
- Use of deprecated functions
```

**Нарушения стиля** — Критичность: 🟡 Средняя
```
- PEP8 violations
- Naming conventions
- Line length > 120 chars
- Unused imports
```

**Высокая сложность** — Критичность: 🟡 Средняя
```
- Функции > 20 строк
- Циклическая сложность > 10
- Слишком глубокая вложенность
```

**Проблемы инфраструктуры** — Критичность: 🟡 Средняя
```
- Устаревшие зависимости
- Отсутствующие конфигурации
- Docker лучшие практики
```

---

## 📊 Визуализация графов

### Режимы отображения

#### 1. Tree View (Дерево)
Иерархическое представление структуры проекта:
- Папки и файлы
- Количество проблем по файлам
- Быстрая навигация по структуре

#### 2. Graph View (Граф)
Интерактивная сетевая визуализация зависимостей:

**PyVis (по умолчанию)**:
- Узлы = файлы/модули
- Рёбра = импорты/зависимости
- Интерактивное перетаскивание
- Физика отключена (стабильная раскладка)

**Plotly (альтернатива)**:
- 3D-визуализация
- Лучше для больших графов
- Встроенное масштабирование
- Экспорт в SVG

**GPU-ускорение (опционально)**:
```
Settings → Graph → "Use GPU Acceleration"
Требует: torch + CUDA (NVIDIA GPU)
Результат: 10x+ ускорение layout для больших графов
```

#### 3. Split View (Раздельный вид)
Одновременный просмотр дерева и графа с синхронизацией:
- Клик в дереве → подсвечивание в графе
- Клик в графе → выделение в дереве
- Быстрая навигация между представлениями

### Экспорт графов

**Автоматический экспорт:**
```
При каждом анализе проекта создаются:
- graph_YYYYMMDD_HHMMSS_pyvis.html (PyVis)
- graph_YYYYMMDD_HHMMSS_plotly.html (Plotly)

Местоположение: ~/.naudit/reports/graphs/
```

**Ручной экспорт:**
```
GUI: Кнопка "📤 Экспорт" → Выберите место → Сохранить
CLI: naudit --module . --export-format both --output ./reports/
```

**Открытие в браузере:**
```bash
# Windows
start "$env:USERPROFILE\.naudit\reports\graphs\graph_*.html"

# macOS
open ~/.naudit/reports/graphs/graph_*.html

# Linux
xdg-open ~/.naudit/reports/graphs/graph_*.html
```

**Возможности графа в браузере:**
- ✅ Масштабирование (колесо мыши)
- ✅ Перетаскивание (click+drag)
- ✅ Информация при наведении (hover tooltip)
- ✅ Поиск узлов (Ctrl+F)
- ✅ Фокус на узел (двойной клик)
- ✅ Работает offline (встроенные библиотеки)

---

## 🔧 Конфигурация

### Конфиг-файл (~/.naudit/config.json)

```json
{
  "app": {
    "theme": "dark",
    "window_size": [1400, 900],
    "auto_save": true
  },
  "analysis": {
    "timeout": 300,
    "parallel": true,
    "max_workers": 4
  },
  "graph": {
    "engine": "pyvis",
    "physics_enabled": false,
    "use_gpu": false,
    "gpu_device": "cuda:0"
  },
  "export": {
    "format": "both",
    "include_statistics": true,
    "compress": false
  }
}
```

### Переменные окружения

```bash
# Отключить GPU-ускорение
export NAUDIT_USE_GPU=false

# Установить timeout для анализа
export NAUDIT_TIMEOUT=600

# Включить debug-логирование
export NAUDIT_DEBUG=true

# Задать папку для отчетов
export NAUDIT_REPORTS_DIR=/custom/path/to/reports
```

---

## 📚 Документация

### Основные документы

| Документ | Назначение | Для кого |
|----------|-----------|----------|
| [📖 USER_GUIDE.md](docs/USER_GUIDE_V4_1.md) | Полное руководство пользователя | Все пользователи |
| [🔧 TECH_GUIDE.md](docs/TECHNICAL_REFERENCE_v2_7_1_Rev3.md) | Техническая документация и API | Разработчики |
| [📊 GRAPH_VISUALIZER_UPDATE.md](docs/GRAPH_VISUALIZER_V2_7_UPDATE.md) | Новое в v2.7 графах | Разработчики |
| [⚙️ INSTALLATION_GUIDE.md](docs/INSTALLATION_GUIDE.md) | Подробная установка на все ОС | Новые пользователи |
| [📝 RELEASE_NOTES.md](docs/RELEASE_NOTES_v2_7.md) | История версий | Все |

### Быстрые ссылки

- **[Примеры использования](examples/)** — готовые примеры кода
- **[Часто задаваемые вопросы](docs/FAQ.md)** — ответы на популярные вопросы
- **[API Документация](docs/API.md)** — интеграция с кодом
- **[Плагины](docs/PLUGINS.md)** — создание пользовательских плагинов

---

## 🐛 Решение проблем

### Проблема: "ModuleNotFoundError: No module named 'pylint'"

**Решение:**
```bash
pip install pylint bandit pytest coverage safety
```

### Проблема: "Ошибка при запуске GUI (PyQt6)"

**Решение:**
```bash
pip install --upgrade PyQt6
```

**Если это не помогло:**
```bash
# Переустановите PyQt6
pip uninstall PyQt6 -y
pip install PyQt6==6.5.0
```

### Проблема: "Аудит работает очень медленно"

**Причины и решения:**
- **Большой проект** (1000+ файлов) — это нормально, может занять несколько минут
- **Слабый ПК** — закройте фоновые приложения, увеличьте таймаут
- **Медленный диск** — проверьте I/O нагрузку (Task Manager → Disk)

```bash
# Увеличьте таймаут
naudit --module . --timeout 600

# Используйте параллелизм
naudit --module . --parallel --max-workers 8
```

### Проблема: "Граф не отображается / черный экран"

**Решение:**
1. Проверьте размер окна (может быть слишком маленьким)
2. Дважды щелкните на граф → автоматический zoom
3. Нажмите 'R' для reset представления
4. Переключитесь на Plotly: Settings → Graph Engine → Plotly

**Если граф зависает:**
```bash
# Отключите GPU (если включено)
export NAUDIT_USE_GPU=false
naudit-gui

# Или используйте CLI без UI
naudit --module . --export-format json
```

### Проблема: "GPU-ускорение не работает"

**Проверка:**
```bash
# Python
python -c "import torch; print(torch.cuda.is_available())"

# PowerShell
nvidia-smi

# Linux
lspci | grep NVIDIA
```

**Если GPU не обнаружена:**
1. Установите драйверы NVIDIA (latest)
2. Установите CUDA Toolkit (совместимую версию)
3. Установите torch с CUDA поддержкой:
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cu118
   ```

### Проблема: "Ошибка 'Access denied' при анализе"

**Решение:**
```bash
# Запустите от администратора
# Windows PowerShell: Right-click → Run as administrator

# Или измените права доступа
chmod -R 755 /path/to/project

# Или исключите проблемные файлы
naudit --module . --exclude ".*,node_modules,venv"
```

### Проблема: "Экспортированный граф не открывается"

**Проверка:**
1. Убедитесь, что браузер установлен (Chrome, Firefox, Edge)
2. Проверьте путь к файлу (без кириллицы и пробелов)
3. Откройте вручную через браузер:
   ```bash
   chrome ~/.naudit/reports/graphs/graph_*.html
   ```

### Отладка

**Включить подробное логирование:**
```bash
naudit --module . --verbose 2>&1 | tee audit.log

# Или для GUI
export NAUDIT_DEBUG=true
python -m n_audit.gui.main_window
```

**Сохранить логи:**
```bash
naudit --module . --verbose > debug.log 2>&1
```

---

## 📦 Требования

### Основные зависимости

```
Python 3.8+
PyQt6 >= 6.5.0
PyVis >= 0.3.0
Plotly >= 5.0.0
NetworkX >= 3.0
radon >= 6.0
pylint >= 2.17
bandit >= 1.7
safety >= 2.0
mypy >= 0.990
pytest >= 7.0
coverage >= 7.0
```

**Полный список:** [requirements.txt](requirements.txt)

### Дополнительно (опционально)

```
torch >= 1.12.0        # GPU-ускорение
torchvision            # GPU-поддержка
PyTorch               # CUDA compute
```

---

## 🤝 Внесение вклада

Приветствуются следующие типы вклада:

### 🐛 Сообщение об ошибках
1. Проверьте, что ошибка не была уже зарегистрирована
2. Опишите шаги для воспроизведения
3. Включите версию Python, ОС и traceback
4. Создайте Issue в GitHub

### 🚀 Новые функции
1. Предложите идею в Discussions
2. Получите одобрение от maintainers
3. Создайте Pull Request с подробным описанием

### 📖 Улучшение документации
- Исправляйте опечатки
- Добавляйте примеры
- Улучшайте чёткость
- Переводите на другие языки

### 🔍 Улучшение кода
- Рефакторинг
- Оптимизация производительности
- Улучшение тестов
- Удаление технического долга

**Процесс:**
```bash
# 1. Fork репозиторий
# 2. Создайте feature branch
git checkout -b feature/amazing-feature

# 3. Делайте commits с понятными сообщениями
git commit -m "feat: add amazing feature"

# 4. Push в fork
git push origin feature/amazing-feature

# 5. Создайте Pull Request
```

**Рекомендации:**
- Следуйте PEP 8
- Добавляйте тесты для новых функций
- Обновляйте документацию
- Используйте типизацию (type hints)

---

## 📜 Лицензия

MIT License — свободное использование в коммерческих и личных целях

```
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

[Полный текст лицензии](LICENSE)

---

## 📊 Статистика проекта

| Метрика | Значение |
|---------|----------|
| **Строк кода** | 15,000+ |
| **Модулей** | 25+ |
| **Функций** | 200+ |
| **Покрытие тестами** | 85% |
| **Поддерживаемые версии Python** | 3.8, 3.9, 3.10, 3.11, 3.12 |
| **Размер .exe** | 379.5 МБ |
| **Время загрузки** | < 3 сек |

---

## 🔗 Ссылки и ресурсы

### Важные ссылки
- 🏠 [Официальный сайт](https://naudit.example.com)
- 💻 [GitHub репозиторий](https://github.com/username/nAUDIT)
- 📦 [PyPI пакет](https://pypi.org/project/nAUDIT/)
- 📞 [GitHub Issues](https://github.com/username/nAUDIT/issues)
- 💬 [GitHub Discussions](https://github.com/username/nAUDIT/discussions)

### Зависимости проекта
- [Python](https://python.org) — язык программирования
- [PyQt6](https://pypi.org/project/PyQt6/) — графический интерфейс
- [PyVis](https://pyvis.org/) — граф-визуализация
- [Plotly](https://plotly.com/) — интерактивные графики
- [NetworkX](https://networkx.org/) — граф-алгоритмы
- [pylint](https://www.pylint.org/) — статический анализ
- [bandit](https://bandit.readthedocs.io/) — проверка безопасности

### Полезные статьи
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Code Metrics Explained](https://en.wikipedia.org/wiki/Cyclomatic_complexity)
- [Graph Theory Basics](https://en.wikipedia.org/wiki/Graph_theory)

---

## 👥 Авторы и контрибьюторы

**Основной разработчик:** Nikita  
**Версия:** 2.7.0  
**Последнее обновление:** 2025-01-16  
**Статус:** ✅ Production Ready

---

## 📞 Контакты и поддержка

Если у вас есть вопросы или нужна поддержка:

1. **Документация** — начните с [USER_GUIDE.md](docs/USER_GUIDE_V4_1.md)
2. **FAQ** — проверьте [часто задаваемые вопросы](docs/)
3. **Issues** — создайте GitHub Issue
4. **Discussions** — обсудите в GitHub Discussions
5. **Email** — свяжитесь с разработчиком

---

**Made with ❤️ for clean code**
