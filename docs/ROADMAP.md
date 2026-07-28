# Roadmap

## v0.1.0-alpha — Foundation (готово)
- Архитектура проекта
- SQLite + SQLAlchemy
- Конфигурация YAML
- Alembic
- InsightFace
- Faiss
- Логирование
- CLI
- Юнит-тесты

## v0.2.0-alpha — Core + Desktop Foundation
Цель: стабильное ядро и минимальный рабочий интерфейс

### Sprint 1 (текущий)
- [x] EventBus
- [x] WorkspaceManager
- [x] ProfileManager
- [x] PluginManager
- [x] HistoryManager
- [x] DecisionEngine (базовый)
- [x] Реструктуризация по доменам
- [x] Desktop panels skeleton
- [x] OPERATOR_WORKFLOW.md

### Sprint 2
- [ ] Workspace: полная интеграция с DatabaseManager
- [ ] Backup Manager: бэкап БД + Faiss + profiles + logs
- [ ] History: запись всех действий через EventBus
- [ ] Profile: интеграция с CLI и Desktop
- [ ] Desktop: MainWindow на PySide6
- [ ] Desktop: Candidate Panel (функциональный)
- [ ] Desktop: Import Queue Panel
- [ ] Desktop: History Panel

### Sprint 3
- [ ] Importer: обработка 20 000 фото без ошибок
- [ ] Importer: инкрементальный импорт
- [ ] Importer: проверка качества
- [ ] Faiss: инкрементальное обновление индекса
- [ ] Faiss: автосохранение/загрузка
- [ ] Recognition: стабильный InsightFace buffalo_l/s
- [ ] Recognition: fallback на CPU

## v0.3.0-alpha — Operator Workflow
Цель: полноценное рабочее место оператора

### Sprint 4
- [ ] Desktop: полный MainWindow
- [ ] Desktop: Workspace Panel
- [ ] Desktop: Profile Panel
- [ ] Desktop: Settings Panel
- [ ] Desktop: Import Queue
- [ ] Desktop: Candidate Panel с подтверждением
- [ ] Desktop: History Panel с фильтрами

### Sprint 5
- [ ] Operator Workflow: импорт → поиск → подтверждение
- [ ] Operator Workflow: создание персоны
- [ ] Operator Workflow: переименование
- [ ] Operator Workflow: объединение персон
- [ ] Operator Workflow: удаление
- [ ] Operator Workflow: восстановление
- [ ] Undo/Redo базовый

### Sprint 6
- [ ] Keyboard shortcuts
- [ ] Theme support (system/dark/light)
- [ ] Performance: импорт 20k фото < 2 часов
- [ ] Performance: поиск < 100ms
- [ ] Memory: < 4GB для 20k фото

## v1.0.0 — Production Ready
Цель: программа, которой можно пользоваться каждый день

### Sprint 7
- [ ] PyInstaller: сборка в EXE
- [ ] Автообновление индекса
- [ ] Резервное копирование по расписанию
- [ ] Восстановление из backup
- [ ] Логирование в файл

### Sprint 8
- [ ] Тестирование на реальных 20k фото
- [ ] Исправление багов
- [ ] Оптимизация памяти
- [ ] Оптимизация скорости
- [ ] Документация пользователя

### Sprint 9
- [ ] Installer (Inno Setup / NSIS)
- [ ] Чек-лист установки
- [ ] Руководство оператора
- [ ] Поддержка GPU (опционально)

## v1.1.0+ — Extensions
- Smart Vote
- Adaptive Threshold
- Black Box Explain
- Batch Operations
- Advanced Quality Checks

## v1.2.0+ — Studio (зарезервировано)
- Benchmark Lab
- Sandbox
- Workflow Builder
- Model Comparison

## v2.0.0+ — Platform
- Plugin Marketplace
- REST API
- Web UI
- Evolution Mode
- Video Recognition
