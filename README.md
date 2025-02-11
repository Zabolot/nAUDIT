# nAUDIT
Python projects complex audit script

nAUDIT – это инструмент глубокого анализа и аудита Python проектов. Проект поддерживает:

. Статический анализ кода (pylint, radon, pipdeptree)
. Проверки безопасности (bandit, safety, cyclonedx-py)
. Анализ тестового покрытия (pytest, coverage)
. Анализ инфраструктуры (sqlfluff, Docker конфигурации)
. Генерацию визуализаций (использование networkx, pyvis, matplotlib)

## Установка

Рекомендуется установка через pip:
```bash
pip install nAUDIT
```

Также можно установить из исходников:
```bash
git clone https://github.com/your_username/nAUDIT.git
cd nAUDIT
pip install .
```

## Использование

После установки инструмент доступен через консольную команду:
```bash
naudit [options]
```

Например:
```bash
naudit --module bot.core --exclude tests
```

Если отсутствуют внешние утилиты, скрипт выведет рекомендации по их установке.