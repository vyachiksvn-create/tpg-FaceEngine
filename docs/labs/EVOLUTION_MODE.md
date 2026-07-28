# Evolution Mode

## Концепция

Evolution Mode — это автоматическое улучшение моделей и параметров на основе обратной связи оператора и метрик качества.

## Цель

Система сама подстраивается под конкретную базу фотографий.

## Механика

```
Operator confirms match
        │
        ▼
Record feedback (correct/incorrect)
        │
        ▼
Update metrics per identity/model
        │
        ▼
Adjust threshold per identity
        │
        ▼
Retrain / fine-tune (future)
```

## Данные для обучения

- Корректные совпадения
- Ошибочные отклонения
- Качество фото (blur, angle, size)
- Модель, которая дала результат

## Запланировано

- v1.0+ как экспериментальный режим
- Сначала логирование feedback
- Потом анализ и адаптация
