# Lessons Learned — Alpha 0.1

## Architecture

- **Folder is not source of truth.** ADR-014: Identity Card holds the person's data; folders store photos only.
- **Unicode-safe loading is mandatory on Windows.** `cv2.imread()` fails on cyrillic paths; `np.fromfile()` + `cv2.imdecode()` is primary, PIL is fallback.
- **Thumbnails must handle RGBA.** PNG with alpha channel cannot be saved as JPEG directly; convert first.

## Recognition

- **Faiss metric matters.** L2 gave distances ~1.6 for similar faces; IP with L2-normalized vectors gives ~0.18, which matches expected face-embedding similarity scales.
- **CPU is slow.** ~256ms per embedding; 2388 photos = ~10 minutes on CPU. GPU or batch processing required for production.
- **Threshold must be archive-specific.** Generic 0.6 is useless; calibration on real data gives 0.1938.

## Operator Workflow

- **Unknown photos must not be lost.** Rename to timestamp-based names, preserve original filename in metadata, route to Review/Unknown.
- **Operator is part of the system.** ExpertValidator and GoldDataset turn human knowledge into measurable improvement.
- **Session reports matter.** Operators need feedback: processed, confirmed, new identities, skipped.

## Database

- **SQLAlchemy 2.0+ requires `DeclarativeBase`**, not `declarative_base()`.
- **Migrations must follow model changes.** Added person_id, quality_score, representative_photo_id, health_score via migration 003.
- **Session management.** `get_session()` as context manager prevents leaks; `expire_on_commit=False` keeps objects usable after commit.

## Testing

- **First test on real data is an audit, not a demo.** 2388 photos revealed Unicode, RGBA, and performance issues that unit tests would never catch.
- **Validation must use IP metric for InsightFace.** Otherwise distances are meaningless.
- **Expert validation is the ultimate benchmark.** Public datasets (LFW, etc.) do not reflect the operator's real knowledge of the archive.

## Next Steps

1. Preserve this state as `alpha-0.1-baseline`
2. Build Alpha 0.2 on new workspace layout (Inbox / Review / Reject / Base)
3. Implement Desktop GUI with Processing Queue
4. Run full 2388-photo validation to get real Top-1/Top-5 numbers
5. Test on 20k archive with monthly 300-400 photo increment
