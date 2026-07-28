"""Desktop: Integration layer wiring pipeline, queue, and panels."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from loguru import logger

from feature.core.events import Event, EventBus
from feature.desktop.focus_mode import FocusModeController
from feature.desktop.panels.candidate_panel import CandidatePanel
from feature.desktop.panels.confirm_workflow import ConfirmWorkflow
from feature.desktop.panels.identity_card import IdentityCard
from feature.desktop.queue import QueueItem, QueueItemStatus, QueueModel
from feature.recognition.pipeline import RecognitionPipeline, ProcessingResult


class DesktopIntegration:
    def __init__(
        self,
        pipeline: RecognitionPipeline,
        queue: QueueModel,
        candidate_panel: CandidatePanel,
        identity_card: IdentityCard,
        confirm_workflow: ConfirmWorkflow,
        focus_mode: FocusModeController,
        event_bus: EventBus | None = None,
    ) -> None:
        self.pipeline = pipeline
        self.queue = queue
        self.candidate_panel = candidate_panel
        self.identity_card = identity_card
        self.confirm_workflow = confirm_workflow
        self.focus_mode = focus_mode
        self.event_bus = event_bus
        self._current_item: QueueItem | None = None
        self._bind_events()

    def _bind_events(self) -> None:
        if self.event_bus:
            self.event_bus.subscribe(self._on_photo_imported, event_type="photo.imported")
            self.event_bus.subscribe(self._on_job_finished, event_type="job.finished")

    def _on_photo_imported(self, event: Event) -> None:
        payload = event.payload or {}
        file_path = payload.get("file_path")
        if not file_path:
            return
        self.queue.add(QueueItem(item_id=event.event_id, file_path=file_path))
        logger.info(f"Queue updated: {file_path}")

    def _on_job_finished(self, event: Event) -> None:
        payload = event.payload or {}
        if payload.get("status") == "completed":
            logger.info(f"Job finished: {payload.get('name')}")

    def process_next(self) -> None:
        pending = self.queue.pending()
        if not pending:
            logger.info("Queue empty")
            return
        self._current_item = pending[0]
        self.queue.update_status(self._current_item.item_id, QueueItemStatus.PROCESSING)
        self._process_current()

    def _process_current(self) -> None:
        if not self._current_item:
            return
        photo_path = Path(self._current_item.file_path)
        result = self.pipeline.process_photo(photo_path)
        if result.status == "found":
            self._current_item.candidates = [
                {
                    "photo_id": c.photo_id,
                    "identity_id": c.identity_id,
                    "score": c.score,
                    "distance": c.distance,
                    "face_size": c.face_size,
                    "blur_score": c.blur_score,
                    "thumbnail_path": c.thumbnail_path,
                }
                for c in result.candidates
            ]
            self.queue.update_status(self._current_item.item_id, QueueItemStatus.FOUND)
            self.candidate_panel.show_candidates(self._current_item.candidates)
            self.confirm_workflow.show(len(result.candidates))
        else:
            self.queue.update_status(self._current_item.item_id, QueueItemStatus.SKIPPED)
            logger.warning(f"No candidates for {photo_path}")
            self.process_next()

    def confirm_current(self, identity_id: int | None) -> None:
        if not self._current_item:
            return
        self._current_item.selected_identity_id = identity_id
        self.queue.update_status(self._current_item.item_id, QueueItemStatus.CONFIRMED)
        self.identity_card.show_identity(identity_id or 0, f"Identity {identity_id}", 0, "now")
        if self.focus_mode.state.mode == FocusMode.FOCUS:
            self._advance()

    def new_person_current(self) -> None:
        if not self._current_item:
            return
        self.queue.update_status(self._current_item.item_id, QueueItemStatus.NEW_PERSON)
        if self.focus_mode.state.mode == FocusMode.FOCUS:
            self._advance()

    def skip_current(self) -> None:
        if not self._current_item:
            return
        self.queue.update_status(self._current_item.item_id, QueueItemStatus.SKIPPED)
        if self.focus_mode.state.mode == FocusMode.FOCUS:
            self._advance()

    def delete_current(self) -> None:
        if not self._current_item:
            return
        self.queue.update_status(self._current_item.item_id, QueueItemStatus.ERROR)
        if self.focus_mode.state.mode == FocusMode.FOCUS:
            self._advance()

    def _advance(self) -> None:
        self._current_item = None
        self.candidate_panel.show_candidates([])
        self.identity_card.clear()
        self.confirm_workflow.show(0)
        self.process_next()

