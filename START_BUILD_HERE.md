# START HERE - Сборка nAUDIT v2.1.0

## ⚡ ВЫПОЛНИ ОДНУ ИЗ КОМАНД НИЖЕ

### Вариант 1: Самый простой (1 клик)
```powershell
.\build.ps1
```

### Вариант 2: Копируй всю строку целиком
```powershell
cd g:\CODING\nAUDIT; . .\v.naudit\Scripts\Activate.ps1; python build_exe_fast.py
```

### Вариант 3: Стандартная команда
```powershell
python build_exe_fast.py
```

---

## ✅ Что произойдет

1. Активирует виртуальное окружение
2. Проверит компоненты (все 5 GUI компонентов найдены ✅)
3. Запустит сборку с PyInstaller
4. Создаст файл: `dist\nAUDIT.exe` (~220 MB)
5. Готово! 🎉

**Время:** 2-3 минуты

---

## 📚 Документация

Если нужна дополнительная информация:

- **Быстрый старт** → `QUICK_BUILD_GUIDE.md`
- **Полное руководство** → `BUILDER_GUIDE_V2_1.md`
- **Обзор системы** → `BUILDERS_SUMMARY.md`
- **Все команды** → `QUICK_COMMANDS.md`
- **Статус проекта** → `FINAL_BUILD_READY.md`

---

## 🆘 Проблемы

**PyInstaller не установлен?**
```powershell
pip install PyInstaller
```

**Все еще не работает?**
→ Откройте `BUILDER_GUIDE_V2_1.md` раздел "Troubleshooting"

---

## 🎯 ГЛАВНОЕ

Просто выполни команду выше и жди 3 минуты.

**Всё остальное сделается автоматически!** ✅
