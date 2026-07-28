# Test Environment

Воспроизводимость тестов зависит от воспроизводимости стенда.

## Стенд Alpha 0.1 "Operator Lab"

### Аппаратное обеспечение
- **CPU:** 
- **RAM:** 
- **GPU:** 
- **Диск:** 

### Программное обеспечение
- **OS:** Windows 11 Pro
- **Python:** 
- **InsightFace:** 
- **Faiss:** 
- **CUDA/cuDNN:** 

### Данные для тестирования
- **Known:** `D:\Base\` — база известных персон
- **Unknown:** `D:\Base\x\` — входящие неизвестные фотографии
- **Workspace:** `D:\FaceEngine_Test\Workspace\`

### Профиль тестирования
- **Recognition:** buffalo_l / buffalo_s
- **Search:** flat / IVF / HNSW
- **Import threads:** 
- **GPU:** 

### Правила
1. Боевой архив `D:\Base` доступен только для чтения.
2. Все результаты пишутся в `D:\FaceEngine_Test\Workspace\`.
3. Никаких изменений оригиналов.
4. После каждого теста заполняется `docs/OBSERVATIONS.md`.
5. Критические ошибки (S1, S2) фиксируются в `docs/KNOWN_ISSUES.md`.
