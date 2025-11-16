# Скрипт для подготовки GitHub Release v2.7

## Что делает этот скрипт

1. Создаёт git tag v2.7
2. Вычисляет контрольные суммы файлов
3. Подготавливает описание릾e
4. Генерирует ссылку для создания release на GitHub

## Требования

- Git установлен и находится в PATH
- PowerShell (на Windows) или bash (на Linux/macOS)
- Доступ к репозиторию GitHub

## Использование

### Windows PowerShell

```powershell
# Активируйте виртуальное окружение (если нужно)
.\v.naudit\Scripts\activate.ps1

# Запустите скрипт
python prepare_release_v2_7.py
```

### Linux/macOS

```bash
# Активируйте виртуальное окружение (если нужно)
source v.naudit/bin/activate

# Запустите скрипт
python prepare_release_v2_7.py
```

## Результаты

После выполнения скрипта в корневой папке проекта будут созданы:
- `RELEASE_ARTIFACTS.md` — информация о релизе с контрольными суммами
- `.github/workflows/release_checklist.txt` — чеклист для проверки

## Следующие шаги

1. Загрузите .exe на GitHub Release вручную или используйте GitHub CLI:
   ```bash
   gh release create v2.7 dist/nAUDIT.exe --title "nAUDIT v2.7" --notes-file RELEASE_ARTIFACTS.md
   ```

2. Проверьте релиз на странице Releases: https://github.com/Zabolot/nAUDIT/releases

3. Обновите ссылки в README.md и документации

## Важно!

Это подготовительный скрипт. Для полного создания release используйте GitHub Web Interface или GitHub CLI.
