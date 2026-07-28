# Black Box Explain

## Концепция

Black Box Explain — это модуль, который объясняет, почему модель приняла то или иное решение.

## Цель

Прозрачность распознавания. Оператор должен понимать:
- Почему выбрана эта персона?
- Какое фото дало максимальный score?
- Какие факторы повлияли на решение?

## Интерфейс

```python
class BlackBoxExplainer:
    def explain(self, result: DecisionResult, candidates: list[Candidate]) -> Explanation:
        ...
```

## Структура Explanation

```python
@dataclass
class Explanation:
    identity_id: int | None
    confidence: float
    threshold_used: float
    strategy: str
    best_photo_id: int
    best_score: float
    votes: dict[int, int]
    factors: dict[str, float]
    text: str
```

## Пример вывода

```
Identity: 42
Confidence: 0.87 / 0.60
Strategy: hybrid
Best photo: #1234 (score=0.92)
Votes: {42: 8, 7: 2}
Factors:
  - blur: -0.02 (score=145)
  - yaw: -0.01 (angle=22°)
  - size: 0.00 (size=120px)
```

## Использование

1. В Desktop — панель объяснения
2. В History — запись explanation для каждого решения
3. В Studio — анализ паттернов ошибок

## Запланировано

- v0.3+ в DecisionEngine
- Экспорт explanation в JSON
- Визуализация в GUI
