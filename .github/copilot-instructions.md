# AI Agent Instructions for UP Game Project

This is a Telegram card game bot with clan systems, battles, and achievements. Here's what you need to know to be productive in this codebase.

## Project Architecture

- **Core Game Logic** (`src/core/`): Contains game mechanics configuration and rules
  - `game_config.py`: Central configuration for game balance, rewards, and timing
  - Key configuration includes card rarities, upgrade costs, and XP progression

- **Database Models** (`src/models/`):
  - SQLAlchemy models in `models.py` define the data structure
  - Key entities: User, Card, UserCard, Clan, Battle, Event
  - Uses PostgreSQL with JSON fields for flexible data storage

- **Handlers** (`src/handlers/`):
  - Telegram command and callback handlers
  - Organized by feature: clan, game, profile
  - Example pattern: `@application.add_handler(CommandHandler("command", handler_func))`

- **Assets** (`assets/`):
  - Card images, backgrounds, frames organized by type
  - Used by `card_renderer.py` for dynamic card generation

## Key Workflows

### Development Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Environment Variables:
- Create `.env` file with `BOT_TOKEN` for Telegram API

### Running the Bot

- Main entry: `src/main.py`
- Bot uses single-instance check via `utils/process_manager.py`
- Handles graceful shutdown and PID cleanup

## Project Conventions

### Database Patterns
- Use SQLAlchemy relationships for related models
- JSON fields for flexible data (e.g., settings, achievements)
- Example from `User` model:
```python
achievements = Column(JSON, default=lambda: {"completed": [], "progress": {}})
```

### Handler Structure
- Command handlers prefix: `/command`
- Callback handlers pattern: `^feature_action`
- Always include error handling with user feedback

### Game Mechanics
- Card levels capped at 10 (see `GameConfig.MAX_CARD_LEVEL`)
- Daily resource and battle limits
- Rarity-based upgrade costs and probabilities

## Integration Points

- **Telegram Bot API**: Primary interface via `python-telegram-bot`
- **Image Processing**: Uses Pillow for card rendering
- **Database**: SQLAlchemy for ORM
- **Async Operations**: Uses `aiohttp` for background tasks

## Testing and Debugging

- Use `pytest` for testing (configured in `requirements.txt`)
- Code quality tools: black for formatting, pylint for linting
- Debug logging available throughout handlers

## Common Tasks

- Adding new card: Update `Card` model and create corresponding asset
- Implementing new feature: Add handler in appropriate file + register in `main.py`
- Modifying game balance: Update constants in `GameConfig`


## Общие рекомендации (Эти рекомендации важны при работе)

- Отвечай на русском языке.
- Не создавай новых файлов пока не убедишься, что отсутсвуют такие же по функционалу файлы, чтобы не создавать дубликатов и путаницу в проекте.
- Поддерживай чистоту и аккуратность в структуре проекта, делай код максимально продуктивным и удобным, чтобы проект был на современном уровне профессионального senior разработчика.
- При необходимости и полезности этого действия, можешь делать запрос на переименование и удаление файлов, если они лишние или полностью дублируют функции других файлов, но также можешь делать резервные копии уже созданных файлов. Также дай возможность перепроверить, внесенные тобой именения и запрашивай запуск бота для проверки.
- Твои ответы должны быть подробными и комплексными, старайся вместить как можно больше продуктивной и полезной работы в каждый ответ.
- При возникновении проблем с UTF-8 encoding и форматированием. Можешь использовать replace_string_in_file tool для доработки текста и кода при необходимости.
- Разобравшись с одной задачей, не спрашивая у меня разрешения, можешь переходить к решению других задач.
- Используй всю полноту квоты сообщения, отвечай и работай пока не убедишься, что в проекте отсутсвуют недочеты, недоработки и ошибки. На каждой стадии разработки проекта ты должен стремиться к финальному состоянию продукта и кода, к его идеалу.
- При внесении изменений, как-либо связанных с базами данных, незамедлительно проведи нужные действия с имеющимися файлами баз данных, для правильной работоспособности проекта. (В том числе миграции)
- При обнаружении файлов дубликатов с одинаковыми функциями, создай новую, улучшенную версию файла, объединив лучшее из обеих версий. Но не уменьшай функциональности без необходимости, сохраняя всё важное и нужное в этих файлов для проекта, то что уже используется в проекте.
- make sure they're up to date with the latest python-telegram-bot version.
- Прежде чем создавать новый файл, изучи все возможные импорты в проекте, где могли бы использоваться эти функции файла. И не создавай нового файла, пока не проверишь в каждой папке наличие похожего или дублирующего файла с похожим названием. Можешь проводить поиск по ключевым словам в названии файла или строк кода в самих файлах, чтобы облегчить поиск.
- Прежде чем работать с терминалом и вводить команды, например, вводить команду перезапуска бота для проверки изменений, каждый раз активируй виртуальную среду.
- Если изменения незначительные, не создавай нового файла, а улучши и доработай имеющийся.
- Если какой-то файл содержит импорты на файл, которого нет в проекте, не создавай этого файла, проверь наличие существующего файла с этой функциональностью и просто измени импорт.
- Документация должна быть написана на русском языке. Размещай документацию структурированно с использованием отдельной папки docs. Создавай файлы документации по каждой сессии и актуально изменяй существующую документацию, но не создавай обилие похожих файлов документации, лучше меньше этих файлов, но более высокого качества.