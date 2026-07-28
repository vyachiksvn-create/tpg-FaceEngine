# Архитектура TPG FaceEngine

## Общая схема

```
┌─────────────────────────────────────────┐
│              Desktop                     │
│  MainWindow + Panels                     │
├─────────────────────────────────────────┤
│              TPG Core                    │
│  EventBus + Workspace + Profile +        │
│  PluginManager + History + Decision      │
├─────────────────────────────────────────┤
│  RecognitionEngine (InsightFace)        │
│  + FaissIndex                           │
├─────────────────────────────────────────┤
│  PhotoImporter (многопоточность)        │
├─────────────────────────────────────────┤
│  Storage                                 │
│  DatabaseManager (SQLAlchemy)           │
│  + ImportLog, QualityCheck              │
└─────────────────────────────────────────┘
```

## Домены

### Core
Слой, на котором строится всё остальное.

- **EventBus** — слабосвязанная коммуникация между модулями
- **WorkspaceManager** — управление несколькими независимыми архивами
- **ProfileManager** — профили, экспорт/импорт, снапшоты, откат
- **PluginManager** — единая регистрация и выбор движков
- **HistoryManager** — журнал действий с возможностью отката
- **DecisionEngine** — Smart Vote, Adaptive Threshold, объяснение решений

### Desktop
Рабочее место оператора.

- **MainWindow** — главное окно
- **Panels**:
  - CandidatePanel — проверка кандидатов
  - HistoryPanel — журнал действий
  - WorkspacePanel — управление workspace
  - ProfilePanel — управление профилями
  - Settings — настройки

### Recognition
Распознавание лиц.

- **RecognitionEngine** — единый интерфейс
- **Plugins**:
  - InsightFace (buffalo_l, buffalo_s)
  - ArcFace (планируется)
  - FaceNet (планируется)

### Search
Поиск ближайших соседей.

- **FaissIndex** — реализация на Faiss
- Поддержка: flat, IVF, HNSW

### Storage
Хранение данных.

- **DatabaseManager** — SQLAlchemy + SQLite
- **Models**: Identity, Photo, Embedding, ImportLog, QualityCheck
- **Logger** — Loguru
- Файловое хранилище: thumbnails, temp, backup, export

### Import
Импорт фотографий.

- **PhotoImporter** — многопоточный импорт
- Дедупликация по SHA256
- Оценка качества
- Сохранение миниатюр

### Plugins
Реализации плагинов.

### Studio
Лаборатория алгоритмов.

### Labs
Экспериментальные функции.

## Уровни данных

### Identity
- Уникальный идентификатор человека
- Полное имя, заметки
- Связь с Photo (1:N)

### Photo
- Файл фотографии
- SHA256 для дедупликации
- Миниатюра
- Связь с Identity (N:1) и Embedding (1:N)

### Embedding
- Вектор признаков лица
- Название модели
- Привязан к Photo

### ImportLog
- Журнал импорта
- Статус: pending, imported, duplicate, error, rejected
- Связь с Photo

### QualityCheck
- Оценка качества снимка
- Размытие, размер лица, угол поворота
- Привязан к Photo

## Профили

Каждый профиль содержит:
- Recognition: engine, model, threshold, use_gpu
- Search: index_type, top_k, merge_strategy
- Import: check_duplicates, compute_sha256, save_thumbnails, quality_check
- Quality: min_face_size, max_blur_threshold, max_yaw_angle, min_confidence
- GUI: theme, view_mode, thumbnail_size, language
- Performance: import_threads, cache_size, auto_build_index

## Импорт

1. Сканирование папки рекурсивно
2. Вычисление SHA256
3. Проверка дубликатов через ImportLog
4. Детекция лиц InsightFace
5. Оценка качества (опционально)
6. Сохранение миниатюры
7. Вычисление embedding
8. Запись в базу
9. Добавление в Faiss индекс

## Производительность

- Многопоточный импорт (ThreadPoolExecutor)
- Кэширование миниатюр
- Отложенное построение индекса
- Поддержка GPU через InsightFace

## Operator Workflow

См. `docs/OPERATOR_WORKFLOW.md`