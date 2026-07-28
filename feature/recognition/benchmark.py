"""Benchmark Manager for recognition performance metrics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BuildMetrics:
    persons_total: int = 0
    photos_total: int = 0
    imported: int = 0
    rejected: int = 0
    skipped: int = 0
    errors: int = 0
    build_time_s: float = 0.0
    avg_embedding_ms: float = 0.0
    median_embedding_ms: float = 0.0
    max_embedding_ms: float = 0.0
    embedding_count: int = 0


@dataclass
class RecognitionMetrics:
    total_processed: int = 0
    found: int = 0
    not_found: int = 0
    no_faces: int = 0
    errors: int = 0
    avg_search_ms: float = 0.0
    avg_pipeline_ms: float = 0.0
    total_search_time_s: float = 0.0
    total_pipeline_time_s: float = 0.0


@dataclass
class SearchMetrics:
    queries: int = 0
    total_time_s: float = 0.0
    avg_time_ms: float = 0.0
    min_time_ms: float = 0.0
    max_time_ms: float = 0.0
    results_found: int = 0
    no_results: int = 0


class BenchmarkManager:
    def __init__(self) -> None:
        self.build = BuildMetrics()
        self.recognition = RecognitionMetrics()
        self.search = SearchMetrics()
        self._search_times: list[float] = []
        self._pipeline_times: list[float] = []

    def record_search(self, time_ms: float, found: bool) -> None:
        self._search_times.append(time_ms)
        self.search.queries += 1
        self.search.total_time_s += time_ms / 1000.0
        self.search.avg_time_ms = sum(self._search_times) / len(self._search_times)
        self.search.min_time_ms = min(self._search_times)
        self.search.max_time_ms = max(self._search_times)
        if found:
            self.search.results_found += 1
        else:
            self.search.no_results += 1

    def record_pipeline(self, time_ms: float, found: bool) -> None:
        self._pipeline_times.append(time_ms)
        self.recognition.total_processed += 1
        self.recognition.total_pipeline_time_s += time_ms / 1000.0
        self.recognition.avg_pipeline_ms = sum(self._pipeline_times) / len(self._pipeline_times)
        if found:
            self.recognition.found += 1
        else:
            self.recognition.not_found += 1

    def print_report(self) -> None:
        print("\n" + "=" * 60)
        print("BENCHMARK REPORT")
        print("=" * 60)
        print("\n[Build]")
        print(f"  Persons:         {self.build.persons_total}")
        print(f"  Photos total:    {self.build.photos_total}")
        print(f"  Imported:        {self.build.imported}")
        print(f"  Rejected:        {self.build.rejected}")
        print(f"  Skipped:         {self.build.skipped}")
        print(f"  Errors:          {self.build.errors}")
        print(f"  Build time:      {self.build.build_time_s:.1f} s")
        if self.build.embedding_count > 0:
            print(f"  Avg embedding:   {self.build.avg_embedding_ms:.1f} ms")
            print(f"  Median embedding:{self.build.median_embedding_ms:.1f} ms")
            print(f"  Max embedding:   {self.build.max_embedding_ms:.1f} ms")
        print("\n[Recognition]")
        print(f"  Processed:       {self.recognition.total_processed}")
        print(f"  Found:           {self.recognition.found}")
        print(f"  Not found:       {self.recognition.not_found}")
        print(f"  No faces:        {self.recognition.no_faces}")
        print(f"  Errors:          {self.recognition.errors}")
        if self.recognition.avg_pipeline_ms > 0:
            print(f"  Avg pipeline:    {self.recognition.avg_pipeline_ms:.1f} ms")
        print("\n[Search]")
        print(f"  Queries:         {self.search.queries}")
        print(f"  Results found:   {self.search.results_found}")
        print(f"  No results:      {self.search.no_results}")
        if self.search.avg_time_ms > 0:
            print(f"  Avg search:      {self.search.avg_time_ms:.1f} ms")
            print(f"  Min search:      {self.search.min_time_ms:.1f} ms")
            print(f"  Max search:      {self.search.max_time_ms:.1f} ms")
        print("=" * 60 + "\n")
