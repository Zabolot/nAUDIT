# 📦 Руководство по установке nAUDIT v2.7

## Оглавление

- [Быстрая установка (.exe для Windows)](#быстрая-установка-exe-для-windows)
- [Установка из исходников](#установка-из-исходников)
- [Установка через pip](#установка-через-pip)
- [GPU-ускорение (опционально)](#gpu-ускорение-опционально)
- [Решение проблем](#решение-проблем)
- [Проверка установки](#проверка-установки)

---

## Быстрая установка (.exe для Windows)

**Рекомендуется для большинства пользователей Windows.**

### Требования

- Windows 7 или выше (32/64-bit)
- 4 ГБ оперативной памяти
- 500 МБ свободного места (для .exe + временных файлов)
- Интернет НЕ требуется после установки

### Шаги установки

1. **Скачайте .exe файл**
   - Перейдите на [GitHub Releases](https://github.com/Zabolot/nAUDIT/releases/latest)
   - Скачайте `nAUDIT.exe` (397 МБ)

2. **Запустите установку**
   - Дважды щелкните на `nAUDIT.exe`
   - Windows может показать предупреждение SmartScreen — нажмите "Подробнее" → "Всё равно запустить"

3. **Первый запуск**
   - Приложение инициализирует базу данных (может занять 10-30 сек)
   - Окно консоли покажет статус инициализации
   - После этого откроется главное окно приложения

4. **Готово!**
   - Приложение полностью готово к работе
   - Все необходимые зависимости встроены в .exe

### Где хранятся данные?

```
C:\Users\<YourUsername>\.naudit\
├── reports/                    # Результаты аудитов
│   ├── audit_*.json           # JSON отчёты аудитов
│   ├── graphs/                # Экспортированные графы
│   │   ├── graph_pyvis_*.html
│   │   └── graph_plotly_*.html
│   └── debug_graph_files_info.json  # Отладка
├── config.json                # Конфигурация приложения
└── naudit.db                  # База данных аудитов
```

---

## Установка из исходников

**Для разработчиков и опытных пользователей.**

### Требования

- Python 3.8 или выше
- Git
- PowerShell (для Windows) или bash (для Linux/macOS)
- 2 ГБ свободного места

### Пошаговая установка (Windows)

1. **Клонируйте репозиторий**
   ```powershell
   git clone https://github.com/Zabolot/nAUDIT.git
   cd nAUDIT
   ```

2. **Создайте виртуальное окружение**
   ```powershell
   python -m venv v.naudit
   .\v.naudit\Scripts\activate.ps1
   ```

3. **Установите зависимости**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Запустите приложение**
   ```powershell
   python -m n_audit.gui.main_window
   ```

### Пошаговая установка (macOS/Linux)

1. **Клонируйте репозиторий**
   ```bash
   git clone https://github.com/Zabolot/nAUDIT.git
   cd nAUDIT
   ```

2. **Создайте виртуальное окружение**
   ```bash
   python3 -m venv v.naudit
   source v.naudit/bin/activate
   ```

3. **Установите зависимости**
   ```bash
   pip install -r requirements.txt
   ```

4. **Запустите приложение**
   ```bash
   python -m n_audit.gui.main_window
   ```

### Сборка собственного .exe (Windows)

```powershell
# Активируйте окружение
.\v.naudit\Scripts\activate.ps1

# Запустите скрипт сборки
python build_exe.py

# Или используйте PowerShell скрипт
.\build_exe.ps1

# Результат: dist/nAUDIT.exe
```

---

## Установка через pip

**Для использования как библиотеки Python.**

```bash
pip install naudit

# Запуск GUI
naudit-gui

# Запуск CLI
naudit --module /path/to/project
```

---

## GPU-ускорение (опционально)

GPU-ускорение используется для быстрого расчёта позиций узлов на больших графах (> 500 узлов).

### Требования для GPU

- NVIDIA GPU (GeForce, Tesla, RTX и т.д.)
- CUDA Toolkit 11.8 или выше
- cuDNN (опционально)

### Установка CUDA Toolkit

**Windows:**
1. Скачайте [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads?target_os=Windows) для вашей OS
2. Установите все компоненты (CUDA, cuDNN, нужно зарегистрироваться)
3. Проверьте установку:
   ```
   nvidia-smi
   ```

**macOS:**
```bash
# На macOS поддержка CUDA ограничена, используйте Metal Performance Shaders
# Обновлено: металл уже встроен
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install nvidia-cuda-toolkit

# RHEL/CentOS
sudo yum install cuda-toolkit
```

### Установка PyTorch с CUDA

```bash
# GPU версия (автоматически выберет вашу CUDA)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Проверка установки
python -c "import torch; print(torch.cuda.is_available())"  # Должно быть True
```

### Проверка GPU-ускорения

После установки GPU будет автоматически использоваться если:
1. Граф содержит > 500 узлов
2. torch доступен в окружении
3. CUDA работает корректно

Вы увидите сообщение в логах:
```
[GPU] Using GPU-accelerated layout calculation...
```

---

## Решение проблем

### Проблема: "Module not found" при установке из исходников

**Решение:**
```powershell
# Убедитесь, что находитесь в папке проекта
cd /path/to/nAUDIT

# Активируйте виртуальное окружение
.\v.naudit\Scripts\activate.ps1

# Переустановите зависимости
pip install --upgrade -r requirements.txt
```

### Проблема: "PyQt6 ошибка при запуске"

**Решение:**
```powershell
# Переустановите PyQt6
pip uninstall PyQt6 PyQt6-WebEngine
pip install PyQt6>=6.0 PyQt6-WebEngine>=6.0
```

### Проблема: ".exe не запускается, ошибка VCRUNTIME140.dll"

**Решение:**
1. Установите Visual C++ Runtime:
   - Скачайте [Microsoft Visual C++ Runtime](https://support.microsoft.com/en-us/help/2977003)
   - Установите для вашей архитектуры (x64 или x86)

2. Или соберите .exe из исходников на вашей машине:
   ```powershell
   .\build_exe.ps1
   ```

### Проблема: "Граф не отображается в GUI"

**Решение:**
```powershell
# Проверьте наличие необходимых библиотек
pip install pyvis plotly networkx

# Проверьте экспортированные файлы вручную
# Откройте в браузере: C:\Users\<YourUsername>\.naudit\reports\graphs\graph_*.html

# Если HTML открывается в браузере, проблема в QWebEngineView
# Переустановите PyQt6-WebEngine
pip reinstall PyQt6-WebEngine
```

### Проблема: "Аудит очень медленно"

**Это нормально для больших проектов!**

Типичное время выполнения:
- 100 файлов: 5-10 сек
- 1000 файлов: 30-60 сек
- 10000 файлов: 2-5 мин
- 50000+ файлов: 10+ мин

**Советы по ускорению:**
1. Закройте фоновые приложения для освобождения RAM
2. Используйте GPU-ускорение для больших графов
3. Исключите ненужные папки (`.git`, `node_modules`, `venv` и т.д.)

### Проблема: "Ошибка CUDA: out of memory"

**Решение:**
```bash
# GPU-ускорение требует памяти. Если её недостаточно:
# 1. Закройте другие GPU-приложения
# 2. Используйте CPU-layout вместо GPU
# 3. Разделите большой проект на части

# Принудительное отключение GPU
# Изменить в коде: graph_visualizer_v2_7.py, строка где вызывается _calculate_positions_gpu_accelerated
```

---

## Проверка установки

### 1. Проверка Python

```bash
python --version
# Ожидается: Python 3.8 или выше
```

### 2. Проверка основных зависимостей

```bash
python -c "import PyQt6; print('✅ PyQt6')"
python -c "import networkx; print('✅ networkx')"
python -c "import pyvis; print('✅ pyvis')"
python -c "import plotly; print('✅ plotly')"
```

### 3. Проверка GPU (опционально)

```bash
python -c "import torch; print('GPU Available:', torch.cuda.is_available())"
```

### 4. Запуск тестов

```bash
# Из папки проекта
python -m pytest -v

# Или конкретный тест
python -m pytest test_graph_integration.py -v
```

### 5. Проверка GUI

```bash
# Запуск главного окна
python -m n_audit.gui.main_window

# Должно открыться главное окно приложения
```

---

## Обновление nAUDIT

### Обновление .exe

1. Скачайте новый .exe с [Releases](https://github.com/Zabolot/nAUDIT/releases/latest)
2. Запустите новый .exe (старая версия остановится автоматически)
3. Ваши данные сохранятся в `~/.naudit/`

### Обновление из исходников

```bash
# Обновите репозиторий
git pull origin main

# Обновите зависимости
pip install -r requirements.txt --upgrade

# Пересоберите .exe (если нужно)
python build_exe.py
```

---

## Часто задаваемые вопросы (FAQ)

**Q: Насколько безопасно скачивать .exe из GitHub?**
A: Полностью безопасно. Проект open-source, вы можете проверить исходный код и собрать .exe сами.

**Q: Можно ли установить на USB флешку?**
A: Да, просто скопируйте `nAUDIT.exe` на флешку. Он полностью портативен.

**Q: Будут ли обновления автоматическими?**
A: Нет, вам нужно вручную скачать новую версию. Старые версии остаются работающими.

**Q: Что если я случайно удалю `~/.naudit/` папку?**
A: Приложение автоматически пересоздаст её при следующем запуске. Все старые отчёты будут потеряны, но приложение продолжит работать.

**Q: Поддерживается ли установка в корневую папку Windows (C:\Program Files)?**
A: Технически да, но данные всё равно будут в `~/.naudit/` (AppData/Local/). Рекомендуется хранить .exe в обычной папке.

---

## Техническая поддержка

Если у вас возникли проблемы при установке:

1. **Проверьте [FAQ]** — ответ может быть здесь
2. **Посмотрите [Логи]** — `~/.naudit/logs/`
3. **Создайте Issue** на [GitHub](https://github.com/Zabolot/nAUDIT/issues)
4. **Прикрепите логи** — помощь в решении проблемы

---

**Версия документации**: 2.7  
**Последнее обновление**: 2025-11-16  
**Статус**: ✅ Актуально
