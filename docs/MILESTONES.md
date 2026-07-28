# Milestones

## Alpha 0.1 — Recognition Engine Complete
**Date:** 2026-07-28

### Achieved
- Core architecture: Workspace, EventBus, History, Profiles
- Identity model with display_name, person_id, metadata
- ArchiveBuilder: import Known base into Workspace
- ImageLoader: Unicode-safe loading with np.fromfile + PIL fallback
- InsightFace integration: buffalo_l model, 512D embeddings
- Faiss search: IP metric with normalization, incremental updates
- RecognitionPipeline: detect → align → embed → search
- QualityAnalyzer: unified face quality scoring
- RejectManager: categorized rejection tracking
- ArchiveReport: detailed import statistics
- BenchmarkManager: build/recognition/search metrics
- DuplicateDetector: within-identity duplicate detection
- Validation Engine: RecognitionValidator, ThresholdTuner
- ArchiveDoctor: pre-import health checks
- CandidateInspector: Top-K review
- ExpertValidator: expert-labeled validation
- GoldDataset: reference dataset management
- ArchiveCalibration: intra/inter-identity distance analysis
- ThresholdAnalyzer: automatic threshold optimization

### Real-world validation
- Tested on D:\Base: 2388 photos, 50 imported in test mode
- Avg Top1 distance: 0.1813 (IP metric)
- Recommended operator_threshold: 0.1938 (conservative)
- Avg embedding time: ~256ms (CPU)
- Avg pipeline time: ~660ms (CPU)

### Next
- Sprint 6: Operator Desktop MVP
- Gold Validation Set creation
- Batch recognition optimization
- Full archive processing
