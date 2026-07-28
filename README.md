# FaceArchive

Платформа для распознавания лиц с модульной архитектурой и системой профилей.

## Версия

v0.1.0-alpha (Sprint 1)

## Возможности Sprint 1

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

## Быстрый старт

### 1. Клонирование

```bash
git clone https://github.com/facearchive/facearchive.git
cd facearchive/main/develop
```

### 2. Установка зависимостей

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Инициализация рабочего пространства

```bash
feature init --base-photos D:\Faces --incoming D:\Incoming
```

### 4. Импорт фотографий

```bash
feature import D:\Faces
```

### 5. Просмотр статистики

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
| `feature profile use <name>` | Переключить профиль |

## Профили

В конфигурации можно создавать профили с разными настройками:

- **default** — сбалансированные настройки для ежедневного использования
- **expert** — максимальная точность и детализация
- **fast** — максимальная скорость импорта

Каждый профиль содержит:
- Recognition: engine, model, threshold, use_gpu
- Search: index_type, top_k, merge_strategy
- Import: check_duplicates, compute_sha256, save_thumbnails, quality_check
- Quality: min_face_size, max_blur_threshold, max_yaw_angle, min_confidence
- GUI: theme, view_mode, thumbnail_size, language
- Performance: import_threads, cache_size, auto_build_index

## Структура проекта

```
FaceEngine/
├── main/
│   └── develop/
│       ├── feature/
│       │   ├── __init__.py
│       │   ├── config.py          # Конфигурация и профили
│       │   ├── cli.py             # CLI на Click
│       │   ├── database/
│       │   │   ├── __init__.py
│       │   │   ├── database.py    # DatabaseManager
│       │   │   ├── logger.py      # Настройка Loguru
│       │   │   └── models.py      # SQLAlchemy модели
│       │   ├── faiss/
│       │   │   ├── __init__.py
│       │   │   └── index.py       # Faiss индекс
│       │   ├── gui/
│       │   │   └── __init__.py    # Зарезервировано для Sprint 2
│       │   ├── import_/
│       │   │   ├── __init__.py
│       │   │   └── importer.py    # Импорт фотографий
│       │   └── recognition/
│       │       ├── __init__.py
│       │       └── engine.py      # InsightFace движок
│       ├── alembic/
│       │   ├── env.py
│       │   ├── script.py.mako
│       │   └── versions/          # Миграции
│       ├── config.yaml            # Основная конфигурация
│       ├── requirements.txt
│       ├── pyproject.toml
│       ├── README.md
│       ├── .gitignore
│       ├── scripts/
│       │   └── init_alembic.py    # Инициализация миграций
│       ├── tests/
│       │   ├── test_config.py
│       │   ├── test_database.py
│       │   ├── test_faiss.py
│       │   ├── test_recognition.py
│       │   ├── test_importer.py
│       │   └── test_cli.py
│       └── docs/
│           └── ARCHITECTURE.md
```

## Запуск тестов

```bash
pytest tests/ -v
```

## Миграции базы данных

Для создания новой миграции:

```bash
python scripts/init_alembic.py
alembic revision --autogenerate -m "описание"
alembic upgrade head
```

## Следующие шаги

- Sprint 2: GUI на PySide6, карточка человека, очередь обработки
- Sprint 3: Журнал изменений, резервное копирование, экспорт
- Sprint 4: Сборка EXE, автообновление индекса, GPU

## Лицензия

MIT