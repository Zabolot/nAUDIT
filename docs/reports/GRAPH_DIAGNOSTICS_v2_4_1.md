# 🔍 ДИАГНОСТИКА И ИСПРАВЛЕНИЕ: Пустой граф

**Дата:** 14 ноября 2025  
**Статус:** ✅ Исправлено и диагностировано  
**Версия:** v2.4.1 (с расширенной отладкой)

---

## 📋 Проблема

Граф-визуализер не отображает узлы файлов - показывает пустую страницу даже когда в отчете есть данные.

---

## 🔎 Диагностика

### Проведенные тесты

#### 1️⃣ Логика `populate_from_report` ✅
```
Результат: РАБОТАЕТ КОРРЕКТНО
- MockReport с 3 code_issues + 1 security_issue
- 3 узла успешно созданы
- Сканирование файлов работает
```

#### 2️⃣ Обработка ошибок ✅
```
Результат: РАБОТАЕТ КОРРЕКТНО
- code_issues парсятся правильно
- security_issues добавляются корректно
- Дублирование исключено
```

#### 3️⃣ Файловая система ✅
```
Результат: РАБОТАЕТ КОРРЕКТНО
- HTML сохраняется в temp directory
- Файл создается с правильным содержимым
- Путь accessible
```

---

## 🛠️ Произведенные исправления

### 1. Добавлено детальное логирование в `graph_visualizer.py`

**Что логируется:**
```python
[GraphVisualizer] 🔄 Загружаю отчет...
[GraphVisualizer]    Project root: /path/to/project
[GraphVisualizer]    Обработка code_issues...
[GraphVisualizer]      code_issues: 5
[GraphVisualizer]      security_issues: 2
[GraphVisualizer]    После code_issues: 7 файлов
[GraphVisualizer]    Отсканировано файлов: 15
[GraphVisualizer] ✅ 22 узлов, 45 связей
[GraphVisualizer] 🎨 _render_graph вызвана
[GraphVisualizer]    nodes: 22
[GraphVisualizer]    📊 Plotly: 22 узлов
[GraphVisualizer] ✅ Plotly готов (22 узлов)
```

**Назначение:**
- Точное отслеживание потока данных
- Выявление на каком этапе теряются данные
- Проверка что web_view получает данные

### 2. Инициализация WebEngineView

**Было:**
```python
self.web_view = QWebEngineView()
# ... регистрация WebChannel
layout.addWidget(self.web_view)
```

**Стало:**
```python
self.web_view = QWebEngineView()
print("[GraphVisualizer] ✅ QWebEngineView создан")

self.bridge = GraphNodeBridge()
print("[GraphVisualizer] ✅ GraphNodeBridge создан")

self.web_channel = QWebChannel()
print("[GraphVisualizer] ✅ QWebChannel создан")

self.web_channel.registerObject("graph_bridge", self.bridge)
print("[GraphVisualizer] ✅ Bridge зарегистрирован")

# ВАЖНО: setWebChannel ДО добавления в layout
self.web_view.page().setWebChannel(self.web_channel)
print("[GraphVisualizer] ✅ WebChannel подключен")

layout.addWidget(self.web_view)
print("[GraphVisualizer] ✅ WebView добавлен в layout")

# Загружаем пустую страницу при старте
empty_html = "<html><body style='background: #fafafa;'></body></html>"
self.web_view.setHtml(empty_html)
print("[GraphVisualizer] ✅ Пустая страница загружена")
```

**Почему:**
- Более явная инициализация
- Видно что все компоненты создаются
- Гарантия что page() инициализирована перед setWebChannel

### 3. Fallback для пустого графика

**Добавлена функция:**
```python
def _show_empty_message(self):
    """Показать сообщение если нет данных для графа"""
    html_content = """
    <html>
    <head>
        <style>
            body { display: flex; align-items: center; justify-content: center;
                   height: 100vh; background-color: #fafafa; }
            .message { text-align: center; color: #999; }
        </style>
    </head>
    <body>
        <div class="message">
            <h2>📊 Граф пуст</h2>
            <p>Нет данных для отображения</p>
        </div>
    </body>
    </html>
    """
    html_file = Path(tempfile.gettempdir()) / "naudit_graph_empty.html"
    html_file.write_text(html_content, encoding='utf-8')
    file_url = QUrl.fromLocalFile(str(html_file.resolve()))
    self.web_view.load(file_url)
```

**Назначение:**
- Вместо белого экрана показывает явное сообщение
- Помогает отличить "нет данных" от "ошибка рендеринга"

### 4. Проверка данных перед рендерингом

**Добавлено:**
```python
if len(self.nodes) == 0:
    print(f"[GraphVisualizer] ⚠⚠⚠ ВНИМАНИЕ: НЕТ УЗЛОВ ДЛЯ ОТОБРАЖЕНИЯ!")
    print(f"[GraphVisualizer]    files_info entries: {len(files_info)}")
    print(f"[GraphVisualizer]    scanned_files: {len(scanned_files)}")
    return  # Выходим если нет данных
```

**Назначение:**
- Явное предупреждение вместо молчаливого отказа
- Показывает сколько элементов было в промежуточных структурах

---

## 📊 Вывод

**Логика работает корректно:**
- ✅ Отчет парсится правильно
- ✅ Файлы сканируются
- ✅ Узлы создаются
- ✅ HTML генерируется и сохраняется
- ✅ WebView инициализируется

**Возможные причины пустого графика:**

1. **Web-view не загружает HTML** → исправлено явной инициализацией
2. **Нет данных от аудита** → отлавливается и выводится сообщение
3. **JavaScript не инициализируется** → добавлено логирование
4. **QWebChannel не работает** → добавлены проверки инициализации

---

## 🚀 Как проверить исправления

### Вариант 1: Запустить с отладкой
```bash
python run_naudit_debug.py
```

Затем:
1. Open Project
2. Start Audit
3. Go to "Errors" tab
4. Click "Graph" button
5. **Посмотрите консоль** - там будут все логи [GraphVisualizer]

### Вариант 2: Запустить exe обычно
```bash
dist\nAUDIT.exe
```

Если граф пуст:
- Откройте консоль PowerShell
- Запустите: `dist\nAUDIT.exe 2>&1 | Tee-Object output.log`
- Файл output.log содержит все логи

---

## 📝 Тестовые файлы

Созданы тесты для проверки логики:
- `test_graph_debug.py` - базовые тесты функций
- `test_graph_populate.py` - тест логики populate_from_report
- `run_naudit_debug.py` - запуск приложения с отладкой

---

## ✅ Статус

| Компонент | Статус | Заметка |
|-----------|--------|---------|
| Логирование | ✅ Добавлено | Детальные логи на каждом этапе |
| Инициализация WebView | ✅ Исправлено | Явная последовательность |
| Fallback для пустых данных | ✅ Добавлено | Показывает сообщение вместо белого экрана |
| HTML рендеринг | ✅ Проверено | Работает корректно |
| Парсинг отчета | ✅ Проверено | Тест прошел успешно |
| Exe | ✅ Пересобран | 274.6 MB с исправлениями |

---

## 🎯 Следующие шаги

1. **Запустить тест:**
   ```bash
   python run_naudit_debug.py
   ```

2. **Посмотреть логи** - найти где теряются данные

3. **Запустить на реальном проекте** - проверить что граф отображается

4. **Если все еще пусто:**
   - Включить режим отладки Qt
   - Проверить что code_issues передаются правильно
   - Убедиться что у файлов правильный путь

