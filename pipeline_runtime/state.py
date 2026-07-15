"""Transactional SQLite state, locks, attempts, evidence, and cohorts."""

from __future__ import annotations

import json
import hashlib
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 2


class StateError(RuntimeError):
    """State is incompatible, locked, or cannot make the requested transition."""


def _now() -> datetime:
    return datetime.now(UTC)


def _stamp(value: datetime | None = None) -> str:
    return (value or _now()).isoformat()


class StateStore:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path, timeout=30)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.connection.execute("PRAGMA journal_mode=WAL")
        self._migrate()

    def _columns(self, table: str) -> set[str]:
        return {row["name"] for row in self.connection.execute(f"PRAGMA table_info({table})")}

    def _add_column(self, table: str, declaration: str) -> None:
        name = declaration.split()[0]
        if name not in self._columns(table):
            self.connection.execute(f"ALTER TABLE {table} ADD COLUMN {declaration}")

    def _migrate(self) -> None:
        version = int(self.connection.execute("PRAGMA user_version").fetchone()[0])
        if version > SCHEMA_VERSION:
            raise StateError(f"state schema {version} is newer than runtime schema {SCHEMA_VERSION}")
        with self.connection:
            self.connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    source_path TEXT NOT NULL,
                    source_hash TEXT NOT NULL,
                    state TEXT NOT NULL,
                    candidate_path TEXT,
                    accepted_path TEXT,
                    error_code TEXT,
                    error_detail TEXT,
                    thread_path TEXT,
                    prompt_hash TEXT,
                    run_id TEXT,
                    lease_owner TEXT,
                    lease_expires TEXT,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS transitions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_id TEXT NOT NULL REFERENCES entities(id),
                    from_state TEXT,
                    to_state TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    evidence_path TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    status TEXT NOT NULL,
                    processed INTEGER NOT NULL DEFAULT 0,
                    accepted INTEGER NOT NULL DEFAULT 0,
                    quarantined INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS attempts (
                    id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    entity_id TEXT NOT NULL REFERENCES entities(id),
                    stage TEXT NOT NULL,
                    prompt_id TEXT NOT NULL,
                    prompt_version TEXT NOT NULL,
                    prompt_hash TEXT NOT NULL,
                    status TEXT NOT NULL,
                    thread_path TEXT,
                    artifact_path TEXT,
                    error_code TEXT,
                    error_detail TEXT,
                    started_at TEXT NOT NULL,
                    finished_at TEXT
                );
                CREATE TABLE IF NOT EXISTS validator_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    entity_id TEXT NOT NULL REFERENCES entities(id),
                    attempt_id TEXT NOT NULL,
                    passed INTEGER NOT NULL,
                    evidence_json TEXT NOT NULL,
                    evidence_path TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS runner_lock (
                    singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
                    owner TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    acquired_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS promotion_records (
                    id TEXT PRIMARY KEY,
                    entity_id TEXT NOT NULL REFERENCES entities(id),
                    original_hash TEXT NOT NULL,
                    candidate_hash TEXT NOT NULL,
                    backup_path TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    finished_at TEXT
                );
                """
            )
            for declaration in (
                "accepted_path TEXT", "prompt_hash TEXT", "run_id TEXT", "lease_owner TEXT", "lease_expires TEXT"
            ):
                self._add_column("entities", declaration)
            if "created_at" not in self._columns("transitions"):
                self._add_column("transitions", "created_at TEXT")
                self.connection.execute("UPDATE transitions SET created_at=? WHERE created_at IS NULL", (_stamp(),))
            self.connection.execute("INSERT OR IGNORE INTO schema_migrations(version, applied_at) VALUES(?, ?)", (SCHEMA_VERSION, _stamp()))
            self.connection.execute(f"PRAGMA user_version={SCHEMA_VERSION}")

    def close(self) -> None:
        self.connection.close()

    def acquire_lock(self, owner: str, run_id: str, stale_seconds: int) -> None:
        now = _now()
        expires = _stamp(now + timedelta(seconds=stale_seconds))
        with self.connection:
            current = self.connection.execute("SELECT * FROM runner_lock WHERE singleton=1").fetchone()
            if current and datetime.fromisoformat(current["expires_at"]) > now:
                raise StateError(f"pipeline is locked by run {current['run_id']}")
            self.connection.execute("DELETE FROM runner_lock WHERE singleton=1")
            self.connection.execute("INSERT INTO runner_lock(singleton,owner,run_id,acquired_at,expires_at) VALUES(1,?,?,?,?)", (owner, run_id, _stamp(now), expires))

    def release_lock(self, owner: str, run_id: str) -> None:
        with self.connection:
            self.connection.execute("DELETE FROM runner_lock WHERE singleton=1 AND owner=? AND run_id=?", (owner, run_id))

    def start_run(self, run_id: str) -> None:
        with self.connection:
            self.connection.execute("INSERT INTO runs(id,started_at,status) VALUES(?,?,'running')", (run_id, _stamp()))

    def finish_run(self, run_id: str, status: str) -> None:
        summary = {row["state"]: row["count"] for row in self.connection.execute("SELECT state,COUNT(*) count FROM entities WHERE run_id=? GROUP BY state", (run_id,))}
        with self.connection:
            self.connection.execute(
                "UPDATE runs SET finished_at=?,status=?,processed=?,accepted=?,quarantined=? WHERE id=?",
                (_stamp(), status, sum(summary.values()), summary.get("accepted", 0) + summary.get("promoted", 0), summary.get("quarantined", 0), run_id),
            )

    def upsert_discovered(self, entity_id: str, source_path: str, source_hash: str, contract_hash: str) -> bool:
        old = self.connection.execute("SELECT source_hash,state,prompt_hash FROM entities WHERE id=?", (entity_id,)).fetchone()
        if old and old["source_hash"] == source_hash and old["prompt_hash"] == contract_hash:
            return False
        old_state = old["state"] if old else None
        with self.connection:
            self.connection.execute(
                """INSERT INTO entities(id,source_path,source_hash,state,prompt_hash,updated_at)
                   VALUES(?,?,?,'discovered',?,?)
                   ON CONFLICT(id) DO UPDATE SET source_path=excluded.source_path,source_hash=excluded.source_hash,
                   state='discovered',candidate_path=NULL,accepted_path=NULL,error_code=NULL,error_detail=NULL,
                   thread_path=NULL,prompt_hash=excluded.prompt_hash,run_id=NULL,lease_owner=NULL,lease_expires=NULL,updated_at=excluded.updated_at""",
                (entity_id, source_path, source_hash, contract_hash, _stamp()),
            )
            reason = "discovery"
            if old:
                reason = "source_revision_changed" if old["source_hash"] != source_hash else "pipeline_contract_changed"
            self._transition(entity_id, old_state, "discovered", reason)
        return True

    def _transition(self, entity_id: str, old: str | None, new: str, reason: str, evidence: str | None = None) -> None:
        self.connection.execute("UPDATE entities SET state=?,updated_at=? WHERE id=?", (new, _stamp(), entity_id))
        self.connection.execute(
            "INSERT INTO transitions(entity_id,from_state,to_state,reason,evidence_path,created_at) VALUES(?,?,?,?,?,?)",
            (entity_id, old, new, reason, evidence, _stamp()),
        )

    def transition(self, entity_id: str, new: str, reason: str, evidence: str | None = None) -> None:
        current = self.connection.execute("SELECT state FROM entities WHERE id=?", (entity_id,)).fetchone()
        if not current:
            raise StateError(f"unknown entity: {entity_id}")
        with self.connection:
            self._transition(entity_id, current["state"], new, reason, evidence)

    def eligible(self, limit: int) -> list[sqlite3.Row]:
        return self.connection.execute(
            "SELECT * FROM entities WHERE state IN ('discovered','retry_eligible') ORDER BY id LIMIT ?", (limit,)
        ).fetchall()

    def lease(self, entity_id: str, run_id: str, owner: str, seconds: int) -> None:
        expires = _stamp(_now() + timedelta(seconds=seconds))
        with self.connection:
            current = self.connection.execute("SELECT state FROM entities WHERE id=?", (entity_id,)).fetchone()
            if not current or current["state"] not in {"discovered", "retry_eligible"}:
                raise StateError(f"entity {entity_id} is not eligible")
            self.connection.execute("UPDATE entities SET run_id=?,lease_owner=?,lease_expires=? WHERE id=?", (run_id, owner, expires, entity_id))
            self._transition(entity_id, current["state"], "leased", "runner_lease")

    def recover_expired_leases(self) -> int:
        now = _stamp()
        rows = self.connection.execute("SELECT id FROM entities WHERE state='leased' AND lease_expires IS NOT NULL AND lease_expires<=?", (now,)).fetchall()
        with self.connection:
            for row in rows:
                self.connection.execute("UPDATE entities SET lease_owner=NULL,lease_expires=NULL WHERE id=?", (row["id"],))
                self._transition(row["id"], "leased", "retry_eligible", "lease_expired")
        return len(rows)

    def begin_attempt(self, attempt_id: str, run_id: str, entity_id: str, stage: str, prompt_id: str, prompt_version: str, prompt_hash: str) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO attempts(id,run_id,entity_id,stage,prompt_id,prompt_version,prompt_hash,status,started_at) VALUES(?,?,?,?,?,?,?,'running',?)",
                (attempt_id, run_id, entity_id, stage, prompt_id, prompt_version, prompt_hash, _stamp()),
            )

    def finish_attempt(self, attempt_id: str, status: str, *, thread: str | None = None, artifact: str | None = None, error: tuple[str, str] | None = None) -> None:
        with self.connection:
            self.connection.execute(
                "UPDATE attempts SET status=?,thread_path=?,artifact_path=?,error_code=?,error_detail=?,finished_at=? WHERE id=?",
                (status, thread, artifact, error[0] if error else None, error[1] if error else None, _stamp(), attempt_id),
            )

    def record_validation(self, run_id: str, entity_id: str, attempt_id: str, passed: bool, evidence: dict[str, Any], path: str) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO validator_results(run_id,entity_id,attempt_id,passed,evidence_json,evidence_path,created_at) VALUES(?,?,?,?,?,?,?)",
                (run_id, entity_id, attempt_id, int(passed), json.dumps(evidence, sort_keys=True), path, _stamp()),
            )

    def prepare_promotion(self, promotion_id: str, entity_id: str, original_hash: str, candidate_hash: str, backup_path: str) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO promotion_records(id,entity_id,original_hash,candidate_hash,backup_path,status,created_at) VALUES(?,?,?,?,?,'prepared',?)",
                (promotion_id, entity_id, original_hash, candidate_hash, backup_path, _stamp()),
            )

    def finish_promotion(self, promotion_id: str, status: str) -> None:
        with self.connection:
            self.connection.execute("UPDATE promotion_records SET status=?,finished_at=? WHERE id=?", (status, _stamp(), promotion_id))

    def latest_promotion(self, entity_id: str) -> dict[str, Any] | None:
        row = self.connection.execute("SELECT * FROM promotion_records WHERE entity_id=? ORDER BY created_at DESC LIMIT 1", (entity_id,)).fetchone()
        return dict(row) if row else None

    def set_outcome(
        self,
        entity_id: str,
        state: str,
        *,
        candidate: str | None = None,
        accepted: str | None = None,
        error: tuple[str, str] | None = None,
        thread: str | None = None,
        prompt_hash: str | None = None,
        source_hash: str | None = None,
        evidence: str | None = None,
    ) -> None:
        current = self.connection.execute("SELECT state FROM entities WHERE id=?", (entity_id,)).fetchone()
        if not current:
            raise StateError(f"unknown entity: {entity_id}")
        with self.connection:
            self.connection.execute(
                """UPDATE entities SET candidate_path=?,accepted_path=?,error_code=?,error_detail=?,thread_path=?,prompt_hash=?,
                   source_hash=COALESCE(?,source_hash),lease_owner=NULL,lease_expires=NULL,updated_at=? WHERE id=?""",
                (candidate, accepted, error[0] if error else None, error[1] if error else None, thread, prompt_hash, source_hash, _stamp(), entity_id),
            )
            self._transition(entity_id, current["state"], state, error[0] if error else "stage_complete", evidence or accepted or candidate or thread)

    def summary(self) -> dict[str, int]:
        return {row["state"]: row["count"] for row in self.connection.execute("SELECT state,COUNT(*) count FROM entities GROUP BY state")}

    def entity(self, entity_id: str) -> dict[str, Any] | None:
        row = self.connection.execute("SELECT * FROM entities WHERE id=?", (entity_id,)).fetchone()
        if not row:
            return None
        return {
            "entity": dict(row),
            "transitions": [dict(item) for item in self.connection.execute("SELECT * FROM transitions WHERE entity_id=? ORDER BY id", (entity_id,))],
            "attempts": [dict(item) for item in self.connection.execute("SELECT * FROM attempts WHERE entity_id=? ORDER BY started_at", (entity_id,))],
            "validations": [dict(item) for item in self.connection.execute("SELECT * FROM validator_results WHERE entity_id=? ORDER BY id", (entity_id,))],
            "promotions": [dict(item) for item in self.connection.execute("SELECT * FROM promotion_records WHERE entity_id=? ORDER BY created_at", (entity_id,))],
        }

    def failure_cohorts(self) -> list[dict[str, Any]]:
        rows = self.connection.execute("SELECT * FROM entities WHERE state='quarantined' ORDER BY id").fetchall()
        grouped: dict[str, dict[str, Any]] = {}
        for row in rows:
            attempt = self.connection.execute("SELECT stage FROM attempts WHERE entity_id=? ORDER BY started_at DESC LIMIT 1", (row["id"],)).fetchone()
            retry_count = self.connection.execute("SELECT COUNT(*) FROM attempts WHERE entity_id=?", (row["id"],)).fetchone()[0]
            path = Path(row["source_path"])
            size = path.stat().st_size if path.exists() else 0
            size_bucket = "small" if size < 10_000 else "medium" if size < 100_000 else "large"
            key_data = {
                "stage": attempt["stage"] if attempt else "preflight",
                "error_code": row["error_code"] or "unknown",
                "content_type": path.suffix.lower() or "unknown",
                "size_bucket": size_bucket,
                "contract_hash": row["prompt_hash"] or "unknown",
                "attempt_bucket": "retried" if retry_count > 1 else "first_attempt",
            }
            canonical = json.dumps(key_data, sort_keys=True)
            cohort_id = f"cohort-{hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:12]}"
            cohort = grouped.setdefault(cohort_id, {"cohort_id": cohort_id, "grouping": key_data, "count": 0, "entity_ids": [], "representative_rule": "first three stable entity IDs"})
            cohort["count"] += 1
            cohort["entity_ids"].append(row["id"])
        return list(grouped.values())

    def run_metrics(self, run_id: str | None = None) -> dict[str, Any]:
        run = self.connection.execute(
            "SELECT * FROM runs WHERE id=?" if run_id else "SELECT * FROM runs ORDER BY started_at DESC LIMIT 1",
            (run_id,) if run_id else (),
        ).fetchone()
        if not run:
            return {"run_id": run_id, "quality_measurement": "unknown"}
        started = datetime.fromisoformat(run["started_at"])
        finished = datetime.fromisoformat(run["finished_at"]) if run["finished_at"] else _now()
        seconds = max((finished - started).total_seconds(), 0.001)
        attempts = self.connection.execute(
            "SELECT stage,status,started_at,finished_at FROM attempts WHERE run_id=?", (run["id"],)
        ).fetchall()
        by_stage: dict[str, dict[str, Any]] = {}
        for row in attempts:
            stage = by_stage.setdefault(row["stage"], {"completed": 0, "failed": 0, "total_seconds": 0.0})
            stage[row["status"]] = stage.get(row["status"], 0) + 1
            if row["finished_at"]:
                stage["total_seconds"] += max((datetime.fromisoformat(row["finished_at"]) - datetime.fromisoformat(row["started_at"])).total_seconds(), 0)
        for stage in by_stage.values():
            count = stage.get("completed", 0) + stage.get("failed", 0)
            stage["mean_seconds"] = stage["total_seconds"] / count if count else None
        total_entities = self.connection.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        remaining = self.connection.execute("SELECT COUNT(*) FROM entities WHERE state IN ('discovered','retry_eligible','leased')").fetchone()[0]
        attempt_count = len(attempts)
        failed_attempts = sum(1 for row in attempts if row["status"] == "failed")
        terminal = run["accepted"] + run["quarantined"]
        return {
            "run_id": run["id"],
            "status": run["status"],
            "elapsed_seconds": seconds,
            "processed": run["processed"],
            "accepted": run["accepted"],
            "quarantined": run["quarantined"],
            "throughput_entities_per_minute": run["processed"] / seconds * 60,
            "acceptance_rate": run["accepted"] / terminal if terminal else None,
            "quarantine_rate": run["quarantined"] / terminal if terminal else None,
            "attempt_failure_rate": failed_attempts / attempt_count if attempt_count else None,
            "remaining_entities": remaining,
            "estimated_remaining_minutes": remaining / (run["processed"] / seconds * 60) if run["processed"] else None,
            "total_entities": total_entities,
            "attempts_by_stage": by_stage,
            "model_usage": "unknown unless supplied in thread captures",
            "quality_measurement": "unknown",
        }

    def retry_entities(self, entity_ids: list[str]) -> int:
        changed = 0
        with self.connection:
            for entity_id in entity_ids:
                row = self.connection.execute("SELECT state FROM entities WHERE id=?", (entity_id,)).fetchone()
                if row and row["state"] == "quarantined":
                    self._transition(entity_id, "quarantined", "retry_eligible", "approved_cohort_retry")
                    changed += 1
        return changed
