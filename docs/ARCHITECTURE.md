# Архитектура FaceArchive

## Общая схема

```
┌─────────────────────────────────────────┐
│              CLI / GUI                   │
├─────────────────────────────────────────┤
│  ConfigManager (профили, YAML)          │
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
class BaseRecognitionEngine(ABC):
    def detect_faces(self, image) -> list[FaceDetection]
    def get_embedding(self, image, face) -> np.ndarray
    def load_model(self) -> None
    def unload_model(self) -> None
```

### Search Plugin
Интерфейс:
```python
class BaseSearchIndex(ABC):
    def add_vectors(self, vectors, ids)
    def search(self, query_vector, top_k) -> list[tuple[int, float]]
    def save(self, path)
    def load(self, path)
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
