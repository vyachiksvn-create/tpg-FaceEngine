# Alpha Test 01

**Date:** 2026-07-28  
**Tag:** alpha-0.1-baseline  
**Commit:** b952379  

## Archive

| Metric | Value |
|--------|-------|
| Source | D:\Base |
| Total photos | 2388 |
| Imported (test mode) | 50 |
| Rejected | 0 |
| Errors | 0 |
| Build time | 37.7s (50 photos) |
| Avg embedding | 256.3ms |

## Recognition

| Metric | Value |
|--------|-------|
| Unknown source | D:\Base\x |
| Unknown photos | 372 |
| Validated (test mode) | 50 |
| Found | 50 |
| Not found | 0 |
| Avg Top1 distance | 0.1813 (IP metric) |
| Avg pipeline | 660.9ms |
| Avg search | 8.3ms |

## Thresholds

| Parameter | Value |
|-----------|-------|
| Metric | Inner Product (normalized) |
| Operator threshold | 0.1938 |
| Auto confirm threshold | 0.1438 |
| Search threshold | 0.6 |
| Recommended policy | conservative |

## Environment

| Component | Version |
|-----------|---------|
| Python | 3.14 |
| InsightFace | 0.7.3 |
| Faiss | 1.14.3 (CPU) |
| SQLAlchemy | 2.0.51 |
| PySide6 | 6.11.1 |
| Hardware | CPU only |

## Observations

- Unicode paths handled via ImageLoader (np.fromfile + PIL fallback)
- RGBA PNG thumbnails require conversion before JPEG save
- CPU embedding ~256ms per photo; GPU expected ~10-20ms
- IP metric gives interpretable similarity scale for InsightFace embeddings
- 50-photo validation shows perfect recall in test set; full validation pending

## Files

- Reports: `reports/`
- Logs: `logs/`
- Metrics: `metrics/`
- Config snapshot: `config_snapshot/`
