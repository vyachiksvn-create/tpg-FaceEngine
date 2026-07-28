"""Session Report: summarize operator work."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SessionReport:
    started_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: datetime | None = None
    processed: int = 0
    confirmed: int = 0
    new_identity: int = 0
    skipped: int = 0
    rejected: int = 0
    errors: int = 0

    def finish(self) -> None:
        self.finished_at = datetime.utcnow()

    def print(self) -> None:
        print("\n" + "=" * 60)
        print("SESSION REPORT")
        print("=" * 60)
        print(f"Started:  {self.started_at}")
        print(f"Finished: {self.finished_at}")
        print(f"Processed:    {self.processed}")
        print(f"Confirmed:    {self.confirmed}")
        print(f"New identity: {self.new_identity}")
        print(f"Skipped:      {self.skipped}")
        print(f"Rejected:     {self.rejected}")
        print(f"Errors:       {self.errors}")
        print("=" * 60 + "\n")
