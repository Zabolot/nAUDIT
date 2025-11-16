# 📦 Инструкция по созданию GitHub Release v2.7

**Статус**: ✅ Release готов к публикации

Файлы подготовлены:
- `RELEASE_ARTIFACTS.md` — Полное описание с контрольными суммами
- `release_metadata.json` — Метаданные для автоматизации
- Git tag: `v2.7.0` создан локально

---

## 🚀 Два способа создания Release

### Вариант 1: Через GitHub Web Interface (рекомендуется для новичков)

1. **Откройте страницу Releases**
   - Перейдите: https://github.com/Zabolot/nAUDIT/releases
   - Нажмите "Draft a new release" (или "Create a new release")

2. **Заполните информацию**
   - **Tag version**: `v2.7.0`
   - **Release title**: `nAUDIT v2.7.0 - Graph Visualizer Improvements`
   - **Description**: Скопируйте содержимое файла `RELEASE_ARTIFACTS.md`

3. **Загрузите файл**
   - В поле "Attach binaries" загрузите файл `dist/nAUDIT.exe`
   - Дождитесь загрузки (может занять 2-5 минут, 379 МБ)

4. **Опубликуйте Release**
   - Нажмите кнопку "Publish release"
   - ✅ Release готов!

---

### Вариант 2: Через GitHub CLI (для опытных пользователей)

#### Шаг 1: Установка GitHub CLI

**Windows (PowerShell):**
```powershell
# Используя Chocolatey
choco install gh

# Или используя Winget
winget install GitHub.cli
```

**macOS:**
```bash
brew install gh
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install gh

# Fedora
sudo dnf install gh
```

#### Шаг 2: Аутентификация

```bash
gh auth login
# Выберите GitHub.com
# Выберите HTTPS
# Аутентифицируйтесь через браузер
```

#### Шаг 3: Создание Release

```bash
# Из корневой папки проекта
gh release create v2.7.0 dist/nAUDIT.exe `
  --title "nAUDIT v2.7.0 - Graph Visualizer Improvements" `
  --notes-file RELEASE_ARTIFACTS.md
```

**На Linux/macOS:**
```bash
gh release create v2.7.0 dist/nAUDIT.exe \
  --title "nAUDIT v2.7.0 - Graph Visualizer Improvements" \
  --notes-file RELEASE_ARTIFACTS.md
```

#### Шаг 4: Проверка

```bash
# Просмотр созданного release
gh release view v2.7.0

# Проверка на GitHub
gh release view v2.7.0 --web
```

---

## ✅ Проверка Release

После создания release:

1. **На странице Releases**
   - https://github.com/Zabolot/nAUDIT/releases
   - Должен быть виден релиз v2.7.0
   - Файл `nAUDIT.exe` доступен для скачивания

2. **Проверка информации**
   - Название: `nAUDIT v2.7.0 - Graph Visualizer Improvements`
   - Описание с контрольными суммами присутствует
   - Файл можно скачать

3. **Контрольные суммы**
   ```
   MD5: fac573c50c8124e2939198931a5431f5
   SHA256: 774a581898fd8e81eb0a6e92416beeb3a53f32bf724c745e5ed7d2dab07c20a3
   ```

---

## 📢 После публикации Release

### 1. Обновите документацию

- [ ] README.md — добавьте ссылку на новый release
- [ ] docs/INSTALLATION_GUIDE.md — обновите версию
- [ ] docs/GRAPH_VISUALIZER_V2_7_UPDATE.md — убедитесь в актуальности

### 2. Объявите о Release

**GitHub**:
- [ ] Добавьте "announcement" label к release (опционально)

**Социальные сети** (опционально):
- [ ] Twitter/X: "#nAUDIT v2.7 — граф-визуализация с улучшениями!"
- [ ] LinkedIn: Обновление инструмента для аудита кода
- [ ] Reddit r/Python: Анонс нового релиза

**Форумы и сообщества** (опционально):
- [ ] Python discord серверы
- [ ] Хабр (если релевантно)
- [ ] Пикабу (если есть русская аудитория)

### 3. Мониторинг

- Отслеживайте количество скачиваний в разделе Insights
- Ответьте на вопросы пользователей в Issues
- Будьте готовы к v2.7.1 багфиксам

---

## 🔄 Если нужно обновить Release

### Обновить описание

```bash
gh release edit v2.7.0 --notes-file RELEASE_ARTIFACTS.md
```

### Добавить новый файл

```bash
# Загрузить дополнительный файл
gh release upload v2.7.0 path/to/additional/file.txt
```

### Удалить файл из Release

Используйте веб-интерфейс GitHub.

### Отменить Release (если что-то пошло не так)

```bash
gh release delete v2.7.0
```

---

## 📋 Чеклист

Перед публикацией release убедитесь:

- [x] .exe файл собран и находится в `dist/nAUDIT.exe`
- [x] Контрольные суммы вычислены
- [x] Git tag `v2.7.0` создан
- [x] RELEASE_ARTIFACTS.md подготовлен
- [x] release_metadata.json создан
- [x] Документация актуальна
- [ ] Release опубликован на GitHub
- [ ] Ссылка скопирована в README.md

---

## 📊 Информация о Release

| Параметр | Значение |
|----------|----------|
| Версия | 2.7.0 |
| Дата | 2025-11-16 |
| Файл | nAUDIT.exe |
| Размер | 379.5 МБ |
| MD5 | `fac573c50c8124e2939198931a5431f5` |
| SHA256 | `774a581898fd8e81eb0a6e92416beeb3a53f32bf724c745e5ed7d2dab07c20a3` |
| Git Tag | v2.7.0 |
| Статус | ✅ Готов к публикации |

---

## 🆘 Проблемы при создании Release

### Проблема: "файл слишком большой"

GitHub имеет лимит на размер файла при веб-загрузке (~2 ГБ).
379.5 МБ — это нормально, должно загружаться без проблем.

Если есть проблемы:
1. Используйте GitHub CLI (более надежный)
2. Попробуйте загрузить позже
3. Проверьте интернет-соединение

### Проблема: "404 Not Found"

Убедитесь, что:
- Вы в правильном репозитории
- Вы авторизованы в GitHub
- У вас есть права на создание releases

### Проблема: "Не могу найти gh команду"

Установите GitHub CLI:
- Windows: `choco install gh` или `winget install GitHub.cli`
- macOS: `brew install gh`
- Linux: `sudo apt install gh`

---

## 📞 Помощь

Если возникли вопросы при создании release:

1. Проверьте [GitHub Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases)
2. Посмотрите [GitHub CLI Documentation](https://cli.github.com/manual)
3. Создайте Issue в репозитории

---

**Версия инструкции**: 1.0  
**Последнее обновление**: 2025-11-16  
**Статус**: ✅ Готово к использованию
