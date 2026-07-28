# TPG FaceEngine

Платформа для распознавания лиц с модульной архитектурой, системой профилей и расширяемым ядром.

## Версия

v0.1.0-alpha (Sprint 2 — Core)

## Возможности Sprint 1 + Sprint 2 Core

### Sprint 1
- Архитектура проекта с модульной структурой
- Конфигурация через YAML с поддержкой нескольких профилей
- SQLite + SQLAlchemy 2.0 с типизацией
- Alembic для управления миграциями
- InsightFace для детекции и распознавания лиц
- Faiss для быстрого поиска ближайших соседей
- Логирование через Loguru
- CLI на Click
- Многопоточный импорт фотографий
- Дедупликация по SHA256
- Оценка качества снимков (размытие, размер лица)
- Система плагинов (распознавание, поиск, импорт)

### Sprint 2 Core
- **EventBus** — слабосвязанная коммуникация между модулями
- **WorkspaceManager** — управление несколькими независимыми архивами
- **ProfileManager** — профили, экспорт/импорт, снапшоты, откат
- **PluginManager** — единая регистрация и выбор движков
- **HistoryManager** — журнал действий с возможностью отката
- **DecisionEngine** — Smart Vote, Adaptive Threshold, объяснение решений

## Быстрый старт

### 1. Клонирование

```bash
git clone https://github.com/vyachiksvn-create/tpg-FaceEngine.git
cd tpg-FaceEngine
```

### 2. Установка зависимостей

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Рабочие пространства

```bash
# Создать workspace
feature workspace create MyArchive

# Активировать workspace
feature workspace activate MyArchive

# Список workspace
feature workspace list
```

### 4. Профили

```bash
# Список профилей
feature profile list

# Активировать профиль
feature profile activate expert

# Экспортировать профиль
feature profile export expert expert.json

# Импортировать профиль
feature profile import custom.json
```

### 5. Импорт фотографий

```bash
feature import D:\Faces
```

### 6. Статистика

```bash
feature info
```

## CLI Команды

| Команда | Описание |
|---------|----------|
| `feature init` | Инициализировать рабочее пространство |
| `feature import <folder>` | Импортировать фотографии |
| `feature search <image>` | Поиск похожих лиц |
| `feature info` | Статистика базы данных |
| `feature workspace create <name>` | Создать workspace |
| `feature workspace list` | Список workspace |
| `feature workspace activate <name>` | Активировать workspace |
| `feature workspace delete <name>` | Удалить workspace |
| `feature profile list` | Список профилей |
| `feature profile activate <name>` | Активировать профиль |
| `feature profile export <name> <path>` | Экспортировать профиль |
| `feature profile import <path>` | Импортировать профиль |

## Профили

В конфигурации можно создавать профили с разными настройками:

- **default** — сбалансированные настройки
- **expert** — максимальная точность и детализация
- **fast** — максимальная скорость импорта

## Структура проекта

```
tpg-FaceEngine/
├── feature/
│   ├── __init__.py
│   ├── config.py                 # Конфигурация (YAML + dataclasses)
│   ├── cli.py                    # CLI на Click
│   ├── core/
│   │   ├── __init__.py
│   │   ├── events.py             # EventBus
│   │   ├── workspace.py          # WorkspaceManager
│   │   ├── profile.py            # ProfileManager
│   │   ├── plugin.py             # PluginManager
│   │   ├── history.py            # HistoryManager
│   │   └── decision.py           # DecisionEngine
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py           # DatabaseManager
│   │   ├── logger.py             # Loguru
│   │   └── models.py             # SQLAlchemy модели
│   ├── faiss/
│   │   ├── __init__.py
│   │   └── index.py              # Faiss индекс
│   ├── gui/
│   │   └── __init__.py           # Зарезервировано для Sprint 3
│   ├── import_/
│   │   ├── __init__.py
│   │   └── importer.py           # Импорт фотографий
│   └── recognition/
│       ├── __init__.py
│       └── engine.py             # InsightFace движок
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/001_init.py
├── config.yaml
├── requirements.txt
├── pyproject.toml
├── .gitignore
├── scripts/
│   └── init_alembic.py
├── tests/
│   ├── test_config.py
│   ├── test_database.py
│   ├── test_faiss.py
│   ├── test_recognition.py
│   ├── test_importer.py
│   ├── test_cli.py
│   ├── test_events.py
│   ├── test_workspace.py
│   ├── test_profile.py
│   ├── test_decision.py
│   └── test_history.py
└── docs/
    └── ARCHITECTURE.md
```

## Запуск тестов

```bash
pytest tests/ -v
```

## Лицензия

MIT