# Marketplace

## Концепция

Plugin Marketplace — это каталог плагинов для TPG FaceEngine, где пользователи могут находить, устанавливать и обновлять плагины распознавания, поиска и импорта.

## Цель

Расширяемость без переписывания ядра.

## Архитектура

```
Marketplace/
├── registry/          # Каталог плагинов
│   ├── index.json
│   └── packages/
├── installer/         # Установка и обновление
│   ├── resolver.py
│   ├── downloader.py
│   └── verifier.py
├── runtime/           # Загрузчик плагинов
│   ├── loader.py
│   └── sandbox.py
└── api/               # REST API для Marketplace
```

## Формат плагина

Каждый плагин — это ZIP-архив:

```
plugin.zip
├── manifest.json      # name, version, description, dependencies
├── plugin.py          # entry point
├── requirements.txt   # зависимости
└── README.md
```

### manifest.json

```json
{
  "name": "insightface-arcface",
  "version": "1.0.0",
  "kind": "recognition",
  "entry": "plugin.py",
  "dependencies": ["insightface>=0.7.0"],
  "min_core_version": "0.2.0"
}
```

## Безопасность

- Подпись плагинов (в будущем)
- Изоляция в sandbox
- Проверка зависимостей
- Откат при ошибке

## CLI

```bash
feature plugin search insightface
feature plugin install insightface-arcface
feature plugin list
feature plugin update --all
```

## Интеграция с PluginManager

```python
class MarketplacePluginManager(PluginManager):
    def install(self, source: str) -> PluginDescriptor:
        ...
    def uninstall(self, name: str) -> None:
        ...
    def update(self, name: str) -> None:
        ...
```

## Запланировано

- v1.0+ после стабильного PluginManager
- Сначала внутренний каталог
- Потом внешний реестр
