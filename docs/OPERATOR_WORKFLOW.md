# Operator Workflow

## Overview

This document describes the standard operator workflow for TPG FaceEngine Alpha.

## Workspace Layout

```
D:\FaceEngine
├── Base
│   └── known person archives
├── Inbox
│   └── new photos from operators
├── Review
│   ├── Unknown
│   └── NeedConfirm
├── Reject
│   ├── NoFace
│   ├── BadQuality
│   └── Errors
├── Workspace
│   ├── database
│   ├── faiss
│   ├── cache
│   └── logs
└── Reports
```

## Standard Flow

1. Operator places new photos into `Inbox`.
2. System analyzes each photo.
3. Results are sorted into:
   - `Review/NeedConfirm` — matched candidates awaiting operator decision
   - `Review/Unknown` — no match found
   - `Reject/*` — technical failures
4. Operator confirms matches or creates new identities.
5. Confirmed photos are added to `Base` and embeddings are updated.

## Unknown Person Lifecycle

```
Inbox
  ↓
Recognition
  ↓
No Match
  ↓
Generate Unknown ID
  ↓
Rename to YYYYMMDD_HHMMSS_UNKNOWN_NNNNNN.ext
  ↓
Move to Review/Unknown
  ↓
Operator review
  ↓
Create Identity
  ↓
Base
```

## Unknown Grouping

Photos without matches can be grouped by similarity to help operator identify the same unknown person across multiple images.

## Naming Convention

Unknown files use timestamp-based names to preserve chronological order and simplify manual lookup.

Original filenames are preserved in metadata.
