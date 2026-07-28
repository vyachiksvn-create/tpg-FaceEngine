# Архитектура TPG FaceEngine

## Общая схема

```
┌─────────────────────────────────────────┐
│              CLI / GUI                   │
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
│  DatabaseManager (SQLAlchemy)           │
│  + ImportLog, QualityCheck              │
└─────────────────────────────────────────┘
```

## TPG Core

### EventBus
- Слабосвязанная коммуникация между модулями
- Подписка на события по типу
- Приоритеты обработчиков
- Поддержка одноразовых подписок

### WorkspaceManager
- Несколько независимых архивов
- Каждый workspace имеет свою БД, индекс, логи, бэкапы
- Быстрое переключение между архивами
- Реестр workspace'ов в JSON

### ProfileManager
- Профили как отдельные YAML-файлы
- Экспорт/импорт в JSON
- Snapshot и rollback
- Сравнение профилей (diff)

### PluginManager
- Единая регистрация движков
- Проверка интерфейсов (RecognitionPlugin, SearchPlugin)
- Динамический выбор движка без перезапуска

### HistoryManager
- Журнал всех действий в JSONL
- Сессии
- Фильтрация по типу, сущности, времени
- Snapshot для отката

### DecisionEngine
- Стратегии: max, vote, hybrid
- Cosine similarity как метрика
- Объяснение решений (black box)
- Адаптивный порог

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

## Плагины

### Recognition Plugin
Интерфейс:
```python
class RecognitionPlugin(Protocol):
    name: str
    def detect_faces(self, image) -> list[dict[str, Any]]
    def get_embedding(self, image, face) -> Any
    def load(self) -> None
    def unload(self) -> None
```

### Search Plugin
Интерфейс:
```python
class SearchPlugin(Protocol):
    name: str
    def add_vectors(self, vectors, ids) -> None
    def search(self, query, top_k) -> list[tuple[int, float]]
    def save(self, path) -> None
    def load(self, path) -> None
    def remove(self, ids) -> None
```

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