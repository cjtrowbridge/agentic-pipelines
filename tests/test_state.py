import tempfile
import unittest
from pathlib import Path

from pipeline_runtime.state import StateError, StateStore


class StateTests(unittest.TestCase):
    def test_active_runner_lock_rejects_overlap(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            store = StateStore(Path(temporary) / "state.sqlite")
            store.acquire_lock("owner-a", "run-a", 60)
            with self.assertRaises(StateError):
                store.acquire_lock("owner-b", "run-b", 60)
            store.release_lock("owner-a", "run-a")
            store.acquire_lock("owner-b", "run-b", 60)
            store.release_lock("owner-b", "run-b")
            store.close()

    def test_expired_entity_lease_becomes_retry_eligible(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            store = StateStore(Path(temporary) / "state.sqlite")
            store.upsert_discovered("entity", "source.md", "hash", "contract")
            store.lease("entity", "run", "owner", 60)
            with store.connection:
                store.connection.execute("UPDATE entities SET lease_expires='2000-01-01T00:00:00+00:00' WHERE id='entity'")
            self.assertEqual(1, store.recover_expired_leases())
            self.assertEqual("retry_eligible", store.entity("entity")["entity"]["state"])
            store.close()


if __name__ == "__main__":
    unittest.main()
