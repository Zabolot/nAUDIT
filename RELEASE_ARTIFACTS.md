# nAUDIT v2.7.0

🎉 **Production Ready Release**

Дата релиза: 2025-11-16

## 📥 Загрузка

**nAUDIT.exe** (379.5 МБ)

### Проверка целостности

| Алгоритм | Хэш |
|----------|-----|
| MD5 | `fac573c50c8124e2939198931a5431f5` |
| SHA256 | `774a581898fd8e81eb0a6e92416beeb3a53f32bf724c745e5ed7d2dab07c20a3` |

**Как проверить (Windows PowerShell)**:
```powershell
# Вычислить SHA256
$(Get-FileHash "nAUDIT.exe" -Algorithm SHA256).Hash

# Вычислить MD5
$(Get-FileHash "nAUDIT.exe" -Algorithm MD5).Hash
```

**Как проверить (Linux/macOS)**:
```bash
# SHA256
sha256sum nAUDIT.exe

# MD5
md5sum nAUDIT.exe
```

---

## 🎯 Основные улучшения в v2.7

✅ **Отключение physics в PyVis** — стабильная работа граф-визуализации  
✅ **GPU-ускорение layout** — 3-4x быстрее на больших графах  
✅ **Синхронизация Tree↔Graph** — выбор в дереве центрирует на графе  
✅ **Экспорт обоих форматов** — PyVis + Plotly HTML  
✅ **Фоновый рендеринг** — QThread для отзывчивого UI  
✅ **Folder-priority coloring** — визуальная группировка по папкам  

### Полный список изменений

[→ Заметки о релизе v2.7](https://github.com/Zabolot/nAUDIT/blob/main/docs/RELEASE_NOTES_v2_7.md)  
[→ Руководство по установке](https://github.com/Zabolot/nAUDIT/blob/main/docs/INSTALLATION_GUIDE.md)

---

## 🚀 Быстрый старт

### Вариант 1: Готовый .exe (рекомендуется)

1. Скачайте `nAUDIT.exe` (397 МБ)
2. Дважды щелкните для запуска
3. Первый запуск: инициализация БД (10-30 сек)
4. Готово! 🎉

### Вариант 2: Сборка из исходников

```bash
git clone https://github.com/Zabolot/nAUDIT.git
cd nAUDIT
python -m venv v.naudit
# Активируйте окружение (см. README.md)
pip install -r requirements.txt
python -m n_audit.gui.main_window
```

---

## 📋 Требования

- Windows 7+ (32/64-bit) или Linux/macOS
- 4 ГБ оперативной памяти
- 500 МБ свободного места
- Интернет НЕ требуется

---

## 📊 Информация о файле

- **Размер**: 379.5 МБ
- **Формат**: x64 EXE (PyInstaller)
- **Python**: 3.8+
- **Статус**: Production Ready ✅

---

## ✅ Проверка качества

- ✅ Smoke tests: 6/6 passed
- ✅ Integration tests: Tree+Graph sync validated
- ✅ Performance tests: GPU acceleration verified
- ✅ Documentation: Complete and production-ready

---

## 🐛 Известные проблемы

- [Known Issues](https://github.com/Zabolot/nAUDIT/blob/main/docs/RELEASE_NOTES_v2_7.md#-известные-проблемы-и-ограничения)

---

## 📞 Поддержка

- 📖 [Документация](https://github.com/Zabolot/nAUDIT/blob/main/docs/)
- 📦 [Руководство по установке](https://github.com/Zabolot/nAUDIT/blob/main/docs/INSTALLATION_GUIDE.md)
- 🕸️ [Граф-визуализация v2.7](https://github.com/Zabolot/nAUDIT/blob/main/docs/GRAPH_VISUALIZER_V2_7_UPDATE.md)
- 💬 [Issues](https://github.com/Zabolot/nAUDIT/issues)

---

## 📜 Лицензия

MIT License — свободное использование в коммерческих и личных целях

---

**Спасибо за использование nAUDIT! 🙏**
