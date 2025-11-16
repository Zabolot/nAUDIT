# nAUDIT v2.1.0 - КОМАНДЫ БЫСТРОГО ДОСТУПА

## 🚀 ГЛАВНАЯ КОМАНДА (СКОПИРУЙ И ВСТАВЬ)

```powershell
cd g:\CODING\nAUDIT; . .\v.naudit\Scripts\Activate.ps1; python build_exe_fast.py
```

---

## ⚡ БЫСТРЫЕ КОМАНДЫ

### Сборка (РЕКОМЕНДУЕТСЯ)
```powershell
python build_exe_fast.py
```

### Сборка (Полная версия)
```powershell
python build_exe_v2_1.py
```

### Через скрипт (Windows)
```powershell
.\build.ps1
# или
build.bat
```

---

## ✅ ПРОВЕРКА РЕЗУЛЬТАТА

### Файл создан?
```powershell
Test-Path dist\nAUDIT.exe
```

### Размер файла
```powershell
(Get-Item dist\nAUDIT.exe).Length / 1MB
```

### Запуск приложения
```powershell
& "dist\nAUDIT.exe"
```

---

## 🔧 ПОДГОТОВКА

### Активировать venv
```powershell
. .\v.naudit\Scripts\Activate.ps1
```

### Установить PyInstaller
```powershell
pip install PyInstaller --upgrade
```

### Проверить PyInstaller
```powershell
python -c "import PyInstaller; print('OK')"
```

---

## 📊 ИНФОРМАЦИЯ

### Версия Python
```powershell
python --version
```

### Версия PyInstaller
```powershell
pyinstaller --version
```

### Список файлов .exe
```powershell
dir dist\*.exe
```

---

## 📚 ДОКУМЕНТАЦИЯ

Откройте в редакторе:
- `BUILDERS_SUMMARY.md` - Полный обзор
- `BUILDER_GUIDE_V2_1.md` - Подробное руководство
- `QUICK_BUILD_GUIDE.md` - Быстрый старт

---

## 💾 ОЧИСТКА

### Удалить старые сборки
```powershell
Remove-Item -Recurse build, dist -ErrorAction SilentlyContinue
```

### Очистить кеш Python
```powershell
Remove-Item -Recurse __pycache__ -ErrorAction SilentlyContinue
```

---

## 📍 ПУТИ

### Текущий проект
```powershell
g:\CODING\nAUDIT
```

### Выходной файл .exe
```powershell
g:\CODING\nAUDIT\dist\nAUDIT.exe
```

### Виртуальное окружение
```powershell
g:\CODING\nAUDIT\v.naudit
```

---

## ⚙️ ОПЦИИ

### Полная вывод из PyInstaller
```powershell
python build_exe_v2_1.py  # Более подробный лог
```

### Быстрая сборка
```powershell
python build_exe_fast.py   # Минимальный лог
```

---

## 🎯 БЫСТРЫЙ CHECKLIST

- [ ] Активирован venv: `. .\v.naudit\Scripts\Activate.ps1`
- [ ] PyInstaller установлен: `pip install PyInstaller`
- [ ] Нет процессов Python
- [ ] Достаточно места на диске
- [ ] Запустить: `python build_exe_fast.py`
- [ ] Проверить: `Test-Path dist\nAUDIT.exe`
- [ ] Запустить: `& "dist\nAUDIT.exe"`

---

**ВСЁ, БОЛЕЕ НИЧЕГО НЕ НУЖНО! 🎉**

Просто выполните одну из команд выше и ждите результат.
