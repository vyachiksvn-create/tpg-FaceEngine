from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Protocol


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    job_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    name: str = ""
    status: JobStatus = JobStatus.PENDING
    progress: float = 0.0
    message: str = ""
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    finished_at: float | None = None
    error: str | None = None
    cancel_requested: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class JobHandler(Protocol):
    def run(self, job: Job, **kwargs: Any) -> None: ...


class JobManager:
    def __init__(self, event_bus: Any | None = None) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()
        self._event_bus = event_bus
        self._threads: dict[str, threading.Thread] = {}

    def submit(self, name: str, handler: JobHandler, **metadata: Any) -> Job:
        job = Job(name=name, metadata=metadata)
        with self._lock:
            self._jobs[job.job_id] = job
        thread = threading.Thread(target=self._run, args=(job, handler), daemon=True)
        self._threads[job.job_id] = thread
        thread.start()
        return job

    def cancel(self, job_id: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
        if not job:
            return False
        job.cancel_requested = True
        return True

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def list_jobs(self) -> list[Job]:
        with self._lock:
            return list(self._jobs.values())

    def _run(self, job: Job, handler: JobHandler) -> None:
        job.status = JobStatus.RUNNING
        job.started_at = time.time()
        if self._event_bus:
            self._event_bus.publish(Event(event_type="job.started", payload={"job_id": job.job_id, "name": job.name}))
        try:
            handler.run(job)
            if job.cancel_requested:
                job.status = JobStatus.CANCELLED
            else:
                job.status = JobStatus.COMPLETED
                job.progress = 100.0
        except Exception as exc:
            job.status = JobStatus.FAILED
            job.error = str(exc)
        finally:
            job.finished_at = time.time()
            if self._event_bus:
                self._event_bus.publish(
                    Event(
                        event_type="job.finished",
                        payload={
                            "job_id": job.job_id,
                            "name": job.name,
                            "status": job.status.value,
                            "error": job.error,
                        },
                    )
                )