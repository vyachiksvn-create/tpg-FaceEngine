# TPG FaceEngine

Платформа для распознавания лиц с модульной архитектурой, системой профилей и расширяемым ядром.

## Версия

v0.1.0-alpha (Sprint 2 — Core + Structure)

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
│   ├── desktop/
│   │   ├── __init__.py
│   │   ├── main_window.py        # Main window
│   │   └── panels/
│   │       ├── __init__.py
│   │       ├── candidate_panel.py
│   │       ├── history_panel.py
│   │       ├── profile_panel.py
│   │       ├── settings.py
│   │       └── workspace_panel.py
│   ├── recognition/
│   │   ├── __init__.py
│   │   └── engine.py             # InsightFace движок
│   ├── search/
│   │   ├── __init__.py
│   │   └── index.py              # Faiss индекс
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── database.py           # DatabaseManager
│   │   ├── logger.py             # Loguru
│   │   └── models.py             # SQLAlchemy модели
│   ├── import_/
│   │   ├── __init__.py
│   │   └── importer.py           # Импорт фотографий
│   ├── plugins/
│   │   └── __init__.py           # Зарезервировано для плагинов
│   ├── studio/
│   │   └── __init__.py           # Зарезервировано для Studio
│   └── labs/
│       └── __init__.py           # Зарезервировано для Labs
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/001_init.py
├── config.yaml
├── requirements.txt
├── pyproject.toml
├── .gitignore
├── layouts/
│   └── default.layout.json
├── scripts/
│   ├── init_alembic.py
│   └── alpha_local_test.py
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
│   ├── test_history.py
│   └── manual/
│       ├── 001_build_archive.md
│       ├── 002_recognition_batch.md
│       ├── 003_operator_workflow.md
│       ├── 004_cancel_job.md
│       ├── 005_empty_folder.md
│       ├── 006_corrupted_image.md
│       ├── 007_duplicate_person.md
│       ├── 008_no_face.md
│       ├── 009_low_quality.md
│       └── 010_large_archive.md
└── docs/
    ├── ARCHITECTURE.md
    ├── OPERATOR_WORKFLOW.md
    ├── VISION.md
    ├── ROADMAP.md
    ├── DECISIONS.md
    ├── QUALITY.md
    ├── OBSERVATIONS.md
    ├── TEST_ENVIRONMENT.md
    ├── IDEAS.md
    └── labs/
        ├── STUDIO.md
        ├── SMART_VOTE.md
        ├── ADAPTIVE_THRESHOLD.md
        ├── BLACK_BOX.md
        ├── MARKETPLACE.md
        ├── EVOLUTION_MODE.md
        ├── WORKFLOW_BUILDER.md
        ├── BENCHMARK_LAB.md
        └── SANDBOX.md
```

## Документация

- `docs/ARCHITECTURE.md` — архитектура проекта
- `docs/OPERATOR_WORKFLOW.md` — сценарий работы оператора
- `docs/VISION.md` — миссия и принципы проекта
- `docs/ROADMAP.md` — план развития до v2.0
- `docs/DECISIONS.md` — архитектурные решения (ADR)
- `docs/QUALITY.md` — критерии качества и KPI
- `docs/OBSERVATIONS.md` — журнал наблюдений из эксплуатации
- `docs/TEST_ENVIRONMENT.md` — стенд для тестирования
- `docs/IDEAS.md` — backlog будущих идей
- `docs/labs/*.md` — концептуальные документы для будущих модулей

## Локальное тестирование

```bash
# Запуск против D:\Base
python scripts/alpha_local_test.py --known "D:\Base" --unknown "D:\Base\x" --workspace "D:\FaceEngine_Test\Workspace"
```

## Следующие шаги

- Alpha 0.1 "Operator Lab" — тестирование на реальной базе
- Сбор отчётов в `docs/OBSERVATIONS.md`
- Исправление ошибок уровней S1/S2
- Подготовка к Beta

## Лицензия

MIT