"""Archive build report."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ArchiveReport:
    persons_total: int = 0
    photos_total: int = 0
    imported: int = 0
    rejected: int = 0
    no_face: int = 0
    multiple_faces: int = 0
    cannot_read: int = 0
    corrupted: int = 0
    too_small: int = 0
    other: int = 0
    avg_embedding_ms: float = 0.0
    median_embedding_ms: float = 0.0
    max_embedding_ms: float = 0.0
    faiss_dimension: int = 512
    faiss_vectors: int = 0
    sqlite_identities: int = 0
    sqlite_photos: int = 0
    sqlite_embeddings: int = 0
    build_time_s: float = 0.0
    rejection_reasons: dict[str, int] = field(default_factory=dict)
    rejection_records: list[dict[str, Any]] = field(default_factory=list)

    def print(self) -> None:
        print("\n" + "=" * 60)
        print("ARCHIVE REPORT")
        print("=" * 60)
        print(f"Persons:            {self.persons_total}")
        print(f"Photos total:       {self.photos_total}")
        print(f"Imported:           {self.imported}")
        print(f"Rejected:           {self.rejected}")
        print("-" * 60)
        print(f"  No face:          {self.no_face}")
        print(f"  Multiple faces:   {self.multiple_faces}")
        print(f"  Cannot read:      {self.cannot_read}")
        print(f"  Corrupted:        {self.corrupted}")
        print(f"  Too small:        {self.too_small}")
        print(f"  Other:            {self.other}")
        print("-" * 60)
        if self.imported > 0:
            print(f"Embedding avg:      {self.avg_embedding_ms:.1f} ms")
            print(f"Embedding median:   {self.median_embedding_ms:.1f} ms")
            print(f"Embedding max:      {self.max_embedding_ms:.1f} ms")
        print("-" * 60)
        print(f"Faiss dimension:    {self.faiss_dimension}")
        print(f"Faiss vectors:      {self.faiss_vectors}")
        print("-" * 60)
        print(f"SQLite identities:  {self.sqlite_identities}")
        print(f"SQLite photos:      {self.sqlite_photos}")
        print(f"SQLite embeddings:  {self.sqlite_embeddings}")
        print("-" * 60)
        print(f"Build time:         {self.build_time_s:.1f} s")
        print("=" * 60 + "\n")
