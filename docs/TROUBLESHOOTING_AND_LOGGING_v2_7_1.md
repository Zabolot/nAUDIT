# 🔧 nAUDIT v2.7.1 - Troubleshooting & Logging Guide

**Версия:** 2.7.1 (с улучшенным логированием)  
**Дата:** 15 November 2025  
**Статус:** 🟢 Production Ready

---

## 📋 Что было исправлено

### ✅ Исправлены критические проблемы:

1. **Программа вылетает при анализе с ошибками**
   - Добавлена полная обработка исключений во все методы
   - Поддержка обоих форматов данных (словарь и объект)
   - Graceful error handling с подробными логами

2. **Отсутствие логирования**
   - Добавлена система профессионального логирования
   - Все операции записываются в лог-файл
   - Цветной вывод в консоль для удобства

3. **Неподтвержденное использование GPU**
   - Добавлен диагностический скрипт
   - Всегда отображается информация об оптимизации
   - Логирование уровня оптимизации при старте

---

## 🚀 Использование (Новое!)

### 1. Запуск программы с логированием

Просто запустите как обычно:
```bash
nAUDIT.exe
```

ИЛИ из командной строки:
```bash
cd G:\CODING\nAUDIT
python run_naudit_gui.py
```

**При старте вы увидите:**
```
[*] Starting nAUDIT v4.0 GUI...
[*] Loading PyQt6...
[*] Initializing logging system...
[INFO] nAUDIT v2.7 logging initialized
[INFO] Log file: C:\Users\Nikita\.naudit\logs\naudit_20251115_163410.log
```

### 2. Проверка системы

Перед тем как анализировать большой проект, рекомендуется проверить систему:

```bash
python diagnose_v2_7.py
```

**Вы увидите:**
- ✅ Статус логирования
- ✅ Информацию о GPU
- ✅ Уровень оптимизации (HIGH/MEDIUM/LOW)
- ✅ Статус всех компонентов

---

## 📍 Где найти логи

### Расположение лог-файлов:

**Windows:**
```
C:\Users\[YourUsername]\.naudit\logs\naudit_YYYYMMDD_HHMMSS.log
```

**Linux:**
```
/home/[username]/.naudit/logs/naudit_YYYYMMDD_HHMMSS.log
```

**macOS:**
```
/Users/[username]/.naudit/logs/naudit_YYYYMMDD_HHMMSS.log
```

### Просмотр последних логов:

**Windows (PowerShell):**
```powershell
# Открыть папку логов
explorer $env:USERPROFILE\.naudit\logs

# Или просмотреть последний лог
Get-ChildItem $env:USERPROFILE\.naudit\logs | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | % { notepad $_.FullName }
```

**Linux/macOS:**
```bash
# Открыть папку логов
open ~/.naudit/logs

# Или просмотреть последний лог
tail -f ~/.naudit/logs/naudit_*.log | tail -100
```

---

## 🐛 Диагностика проблем

### Если программа вылетает при анализе:

#### Шаг 1: Запустите диагностику
```bash
python diagnose_v2_7.py
```

#### Шаг 2: Проанализируйте маленький проект
- Выберите проект с 5-10 файлами
- Смотрите вывод в консоли
- Проверяйте лог-файл на ошибки

#### Шаг 3: Проверьте лог-файл

Откройте последний файл в папке логов и ищите:

**CRITICAL или ERROR:**
```
[ERROR] Ошибка при обработке issue #3: AttributeError: 'dict' object has no attribute 'get'
```

#### Шаг 4: Общие причины вылетов

| Ошибка | Причина | Решение |
|--------|---------|----------|
| `MemoryError` | Мало памяти | Уменьшить project size, закрыть другие приложения |
| `RecursionError` | Глубокая рекурсия | Проект слишком сложный, есть циклические импорты |
| `UnicodeDecodeError` | Проблема с кодировкой файла | Файл в нечитаемой кодировке |
| `AttributeError` | Неправильная структура данных | Bug в коде, будет исправлен |
| `TypeError` | Неправильный тип данных | Несовместимое значение, будет исправлено |

---

## 📊 Понимание логов

### Структура логов:

```
[2025-11-15 16:34:10] DEBUG    [main_window_v4:320] Audit button clicked, path: G:\test_project
[2025-11-15 16:34:11] INFO     [main_window_v4:40] Starting audit for: G:\test_project
[2025-11-15 16:34:12] INFO     [tree_widget:175] Starting populate_from_report: G:\test_project
[2025-11-15 16:34:12] DEBUG    [tree_widget:182] Found code_issues at report.code_issues: 5 items
[2025-11-15 16:34:12] INFO     [tree_widget:238] Processed code issues: 5
[2025-11-15 16:34:12] INFO     [main_window_v4:340] Analysis complete: 5 issues in 2 files
```

### Уровни логирования:

- **DEBUG** - Детальная информация (используется для разработки)
- **INFO** - Важная информация о ходе выполнения ✅
- **WARNING** - Потенциальные проблемы ⚠️
- **ERROR** - Ошибки, но программа продолжает работать ❌
- **CRITICAL** - Критические ошибки (программа может вылететь) 💥

---

## 🎯 Optimization Levels

Программа автоматически выбирает уровень оптимизации:

### HIGH (Мощный ПК: GPU + 16+ GB RAM)
```
- Spring iterations: 100
- Max nodes: 5000
- Animations: ON
- Batch processing: ON
- Speed: FASTEST ⚡⚡⚡
```

### MEDIUM (Среднее оборудование: 8+ GB RAM)
```
- Spring iterations: 50
- Max nodes: 2000
- Animations: ON
- Batch processing: OFF
- Speed: GOOD ⚡⚡
```

### LOW (Слабое оборудование: < 8 GB RAM)
```
- Spring iterations: 30
- Max nodes: 1000
- Animations: OFF
- Batch processing: OFF
- Speed: SLOW ⚡
- BUT: Works reliably ✅
```

**Ваша система:** Определяется автоматически при старте (смотрите консоль)

---

## 💡 Tips & Tricks

### 1. Быстрый анализ большого проекта

Если программа медленная:
- Закройте все другие приложения
- Проверьте уровень оптимизации (`diagnose_v2_7.py`)
- Если LOW - попробуйте на другой машине или подождите дольше

### 2. Отладка проблем

Откройте 2 окна:
- Одно: запущенная программа
- Второе: командная строка смотрит лог
  ```bash
  tail -f C:\Users\Nikita\.naudit\logs\*.log
  ```

### 3. Сообщение об ошибке

Если находите баг:
1. Запустите диагностику
2. Воспроизведите ошибку
3. Откройте лог-файл
4. Скопируйте последние 50 строк лога
5. Приложите к отчету об ошибке

---

## 📋 Checklist Troubleshooting

Если программа вылетает:

- [ ] Запустил диагностику (`python diagnose_v2_7.py`)
- [ ] Проверил лог-файл (`C:\Users\..\.naudit\logs\`)
- [ ] Попробовал маленький проект (5-10 файлов)
- [ ] Закрыл другие приложения
- [ ] Перезагрузил программу
- [ ] Скопировал полный текст ошибки из лога
- [ ] Гугл'ил ошибку
- [ ] Готов к отчету об ошибке с лог-файлом

---

## 🆘 Получить помощь

### Когда сообщить об ошибке:

Напишите с информацией:
1. **Что делали:** "Анализировал проект X с Y файлами"
2. **Что произошло:** "Программа закрылась после 30 секунд"
3. **Симптомы:** "Никаких сообщений об ошибке"
4. **Система:** 
   - Windows 10/11, Linux, macOS?
   - Сколько RAM?
   - Есть ли GPU?
5. **Последние строки лога:** (20-30 строк)

```
[ПРИМЕР ОТЧЕТА]
Анализировал: G:\my_large_project (5000 файлов)
Что произошло: После 45 сек программа просто закрылась
Система: Windows 10, 16GB RAM, No GPU
Лог выше...
```

---

## 📚 Дополнительные ресурсы

- **Build Report:** BUILD_v2_7_SUCCESS_REPORT.md
- **Technical Details:** UPDATE_v2_7_GPU_HIERARCHY.md
- **Testing Guide:** TESTING_GUIDE_v2_7.md
- **Session Report:** SESSION_COMPLETION_FINAL.md

---

## 🎉 Что дальше?

### v2.7.1 (Этот релиз)
- ✅ Comprehensive logging
- ✅ Error handling
- ✅ Diagnostic tool
- ✅ Better error messages

### v2.8 (Планируется)
- 📋 Cache для ускорения повторного анализа
- 📋 Улучшенная обработка больших файлов
- 📋 Экспорт логов в HTML
- 📋 Статистика по времени анализа

---

**Версия:** 2.7.1  
**Статус:** 🟢 PRODUCTION READY  
**Качество:** ⭐⭐⭐⭐⭐ Professional  

**Главное:** Все ошибки теперь логируются! Проверяйте лог-файлы для диагностики 📝
