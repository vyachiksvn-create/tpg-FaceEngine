# Workflow Builder

## Концепция

Workflow Builder — это визуальный конструктор пайплайнов обработки фотографий.

## Цель

Пользователь может собирать пайплайн из готовых блоков без написания кода.

## Примеры пайплайнов

### Simple Import
```
Load Photos → Detect Faces → Check Quality → Save
```

### Advanced Recognition
```
Load Photos → Detect Faces → Filter Blur → Embed → Search → Decision → Notify
```

### Batch Processing
```
Watch Folder → Queue → Process Parallel → Update Index → Backup
```

## Узлы (Nodes)

- **Input**: Load Folder, Load Photo, Watch Folder
- **Process**: Detect, Embed, Search, Decide, Filter
- **Output**: Save, Export, Notify, Log
- **Control**: If, Loop, Delay

## Интерфейс

- Drag & Drop
- Подключение выходов ко входам
- Настройка параметров каждого узла
- Сохранение как профиль

## Запланировано

- v1.0+ в TPG Studio
- Не в основной программе
