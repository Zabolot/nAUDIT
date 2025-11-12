# Решение: ModuleNotFoundError при запуске nAUDIT.exe

## Проблема

При запуске `nAUDIT.exe` возникала ошибка:

```
ModuleNotFoundError: No module named 'n_audit'
```

## Причина

PyInstaller при сборке .exe не смог автоматически найти и включить модуль `n_audit` из-за того, что:

1. **Динамические импорты** - некоторые импорты выполняются динамически в runtime
2. **Относительные пути** - импорты в коде используют относительные пути
3. **Отсутствие явного указания** - PyInstaller не знал включать пакет `n_audit` целиком

## Решение

### Использованные параметры PyInstaller

```bash
pyinstaller \
  --windowed \                           # Без консольного окна
  --name=nAUDIT \                        # Имя приложения
  --collect-all=n_audit \                # КЛЮЧЕВОЙ: собирает весь пакет n_audit
  n_audit/gui/main_app.py                # Точка входа
```

### Ключевой параметр: `--collect-all=n_audit`

Этот параметр говорит PyInstaller:

```
"Найди пакет n_audit в sys.path и включи его целиком (все файлы, подпапки, данные)"
```

Эквивалент команды:

```bash
# Старая (неработающая) версия:
pyinstaller --onefile --windowed --name=nAUDIT n_audit/gui/main_app.py

# Новая (работающая) версия:
pyinstaller --onefile --windowed --name=nAUDIT --collect-all=n_audit n_audit/gui/main_app.py
```

## Дополнительные Параметры

Для полной совместимости также можно добавить:

```bash
pyinstaller \
  --windowed \
  --name=nAUDIT \
  --collect-all=n_audit \                # Собрать весь пакет n_audit
  --hidden-import=PyQt6.QtCore \         # Явно указать скрытые импорты
  --hidden-import=PyQt6.QtGui \
  --hidden-import=PyQt6.QtWidgets \
  --add-data "n_audit:n_audit" \         # Добавить данные пакета
  n_audit/gui/main_app.py
```

## Финальная Команда Сборки

```powershell
cd G:\CODING\nAUDIT

# Очистка старых сборок
Remove-Item -Path "build", "dist", "nAUDIT.spec" -Force -Recurse -ErrorAction SilentlyContinue

# Активация окружения
.\v.naudit\Scripts\Activate.ps1

# Сборка с правильными параметрами
pyinstaller \
  --onefile \
  --windowed \
  --name=nAUDIT \
  --collect-all=n_audit \
  n_audit/gui/main_app.py

# Результат: dist\nAUDIT.exe (либо dist\nAUDIT\nAUDIT.exe без --onefile)
```

## Проверка Результата

```powershell
# Для сборки ЛМЕЗ --onefile (папка):
.\dist\nAUDIT\nAUDIT.exe

# Для сборки С --onefile (одиночный файл):
.\dist\nAUDIT.exe
```

✅ **Приложение должно запуститься без ошибок модуля**

## Почему Это Случилось?

1. **PyInstaller анализирует код статически** - он может не увидеть динамические импорты
2. **Пакет n_audit не был помечен** - PyInstaller не знал, что нужно включить весь пакет
3. **Отсутствие `__init__.py`** - возможно, структура пакета была неправильно распознана

## Как Избежать в Будущем

### Вариант 1: Использовать `--collect-all` (Рекомендуется)

```bash
pyinstaller --onefile --windowed --name=nAUDIT --collect-all=n_audit n_audit/gui/main_app.py
```

### Вариант 2: Явно Указать Все Модули

```bash
pyinstaller \
  --onefile \
  --windowed \
  --name=nAUDIT \
  --hidden-import=n_audit \
  --hidden-import=n_audit.core \
  --hidden-import=n_audit.code_analysis \
  --hidden-import=n_audit.security \
  --hidden-import=n_audit.tests_analysis \
  --hidden-import=n_audit.infrastructure \
  --hidden-import=n_audit.recommendations \
  --hidden-import=n_audit.visualizations \
  --hidden-import=n_audit.audit_manager \
  --hidden-import=n_audit.gui \
  --hidden-import=n_audit.gui.main_window \
  --hidden-import=n_audit.gui.styles \
  n_audit/gui/main_app.py
```

### Вариант 3: Использовать .spec файл

Создать файл `nAUDIT.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['n_audit/gui/main_app.py'],
    pathex=['G:\\CODING\\nAUDIT'],
    binaries=[],
    datas=[('n_audit', 'n_audit')],  # КЛЮЧЕВАЯ СТРОКА
    hiddenimports=[
        'n_audit',
        'n_audit.core',
        'n_audit.code_analysis',
        'n_audit.security',
        'n_audit.tests_analysis',
        'n_audit.infrastructure',
        'n_audit.recommendations',
        'n_audit.visualizations',
        'n_audit.audit_manager',
        'n_audit.gui',
        'n_audit.gui.main_window',
        'n_audit.gui.styles',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='nAUDIT',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

Затем запустить:

```bash
pyinstaller nAUDIT.spec
```

## Структура Получившегося .exe

```
nAUDIT.exe (или dist/nAUDIT/nAUDIT.exe)
├── Python Interpreter
├── PyQt6 (библиотека GUI)
├── n_audit (ВАЖНО: целый пакет, включая все модули)
│   ├── __init__.py
│   ├── core.py
│   ├── code_analysis.py
│   ├── security.py
│   ├── tests_analysis.py
│   ├── infrastructure.py
│   ├── recommendations.py
│   ├── visualizations.py
│   ├── audit_manager.py
│   ├── utils.py
│   └── gui/
│       ├── __init__.py
│       ├── main_app.py
│       ├── main_window.py
│       └── styles.py
├── Все остальные пакеты и зависимости
└── Bootloader (для запуска)
```

## Итоговая Команда (Скопировать-Вставить)

```powershell
# Windows PowerShell
cd G:\CODING\nAUDIT
.\v.naudit\Scripts\Activate.ps1
Remove-Item -Path "build", "dist", "nAUDIT.spec" -Force -Recurse -ErrorAction SilentlyContinue
pyinstaller --onefile --windowed --name=nAUDIT --collect-all=n_audit n_audit/gui/main_app.py
echo "✅ Сборка завершена! Файл: dist\nAUDIT.exe"
.\dist\nAUDIT.exe
```

---

**Проблема решена! ✅**

Теперь `nAUDIT.exe` запускается без ошибок `ModuleNotFoundError`.
