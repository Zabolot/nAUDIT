#!/bin/bash
# Скрипт для запуска nAUDIT на Linux/macOS
# Создаёт/активирует виртуальное окружение и запускает приложение

set -e

# Определение основной директории
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/v.naudit"
PYTHON_MIN_VERSION="3.8"

echo "════════════════════════════════════════════════════════════════"
echo "🚀 nAUDIT 2.0 — Инициализация и запуск"
echo "════════════════════════════════════════════════════════════════"

# Проверка версии Python
echo ""
echo "[1/3] Проверка Python..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "  ✓ Python $PYTHON_VERSION"

# Создание/активация виртуального окружения
echo ""
echo "[2/3] Подготовка окружения..."
if [ ! -d "$VENV_DIR" ]; then
    echo "  Создание виртуального окружения..."
    python3 -m venv "$VENV_DIR"
    echo "  ✓ Виртуальное окружение создано"
fi

# Активация виртуального окружения
source "$VENV_DIR/bin/activate"
echo "  ✓ Виртуальное окружение активировано"

# Установка зависимостей
echo ""
echo "[3/3] Установка зависимостей..."
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    pip install --upgrade pip > /dev/null 2>&1
    pip install -q -r "$PROJECT_DIR/requirements.txt"
    echo "  ✓ Зависимости установлены"
fi

# Установка пакета в режиме разработки
pip install -q -e "$PROJECT_DIR"
echo "  ✓ Пакет установлен"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ Инициализация завершена!"
echo "════════════════════════════════════════════════════════════════"

# Запуск GUI приложения
echo ""
echo "🔧 Запуск nAUDIT GUI..."
python -m n_audit.gui.main_app

# Деактивация окружения
deactivate 2>/dev/null || true
