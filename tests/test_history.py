from __future__ import annotations

import time

import pytest

from feature.core.history import ActionType, HistoryEntry, HistoryManager


class TestHistoryManager:
    def test_record_and_query(self, tmp_path):
        mgr = HistoryManager(tmp_path)
        mgr.start_session()
        mgr.record(HistoryEntry(
            action=ActionType.IDENTITY_CREATE,
            entity_type="identity",
            entity_id=1,
            description="Created identity",
        ))
        mgr.flush()
        results = mgr.query(action=ActionType.IDENTITY_CREATE)
        assert len(results) == 1
        assert results[0].entity_id == 1

    def test_query_by_entity(self, tmp_path):
        mgr = HistoryManager(tmp_path)
        mgr.start_session()
        mgr.record(HistoryEntry(action=ActionType.PHOTO_ADD, entity_type="photo", entity_id=10, description="Added"))
        mgr.record(HistoryEntry(action=ActionType.PHOTO_ADD, entity_type="photo", entity_id=20, description="Added"))
        mgr.flush()
        results = mgr.query(entity_type="photo", entity_id=10)
        assert len(results) == 1
        assert results[0].entity_id == 10

    def test_rollback_without_snapshot(self, tmp_path):
        mgr = HistoryManager(tmp_path)
        entry = HistoryEntry(action=ActionType.SYSTEM, entity_type="test", entity_id=1, description="test")
        assert mgr.rollback(entry) is False

    def test_session_isolation(self, tmp_path):
        mgr = HistoryManager(tmp_path)
        mgr.start_session("s1")
        mgr.record(HistoryEntry(action=ActionType.SYSTEM, entity_type="t", entity_id=1, description="s1"))
        mgr.flush()
        mgr.start_session("s2")
        mgr.record(HistoryEntry(action=ActionType.SYSTEM, entity_type="t", entity_id=2, description="s2"))
        mgr.flush()
        all_entries = mgr.query()
        assert len(all_entries) == 2