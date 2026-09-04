from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager

from v621_runtime_patch import install_db_patch as _install_v621_base


def _install_sqlite_fast_path() -> None:
    from cloud_db import CloudDatabase

    if getattr(CloudDatabase, "_v621_webopt_sqlite", False):
        return

    original_init = CloudDatabase.__init__

    def fast_init(self, path):
        self._v621_pragma_lock = threading.Lock()
        self._v621_wal_ready = False
        original_init(self, path)

    @contextmanager
    def fast_connect(self):
        conn = sqlite3.connect(
            self.path,
            timeout=60,
            check_same_thread=False,
            cached_statements=512,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=60000")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute("PRAGMA cache_size=-20000")
        try:
            conn.execute("PRAGMA mmap_size=134217728")
        except sqlite3.DatabaseError:
            pass
        if not getattr(self, "_v621_wal_ready", False):
            with self._v621_pragma_lock:
                if not self._v621_wal_ready:
                    conn.execute("PRAGMA journal_mode=WAL")
                    self._v621_wal_ready = True
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def workflows_for_records(self, project_id, record_kind, subtype, record_ids):
        ids = []
        seen = set()
        for value in record_ids or []:
            try:
                rid = int(value)
            except Exception:
                continue
            if rid > 0 and rid not in seen:
                seen.add(rid)
                ids.append(rid)
        if not ids:
            return {}
        out = {}
        with self.connect() as c:
            for start in range(0, len(ids), 400):
                chunk = ids[start:start + 400]
                marks = ",".join("?" for _ in chunk)
                rows = c.execute(
                    f"""SELECT * FROM approval_workflows
                           WHERE project_id=? AND record_kind=? AND subtype=?
                             AND record_id IN ({marks})""",
                    [project_id, record_kind, subtype, *chunk],
                ).fetchall()
                for row in rows:
                    out[int(row["record_id"])] = row
        return out

    CloudDatabase.__init__ = fast_init
    CloudDatabase.connect = fast_connect
    CloudDatabase.approval_workflows_for_records = workflows_for_records
    CloudDatabase._v621_webopt_sqlite = True


def _tune_gateway_cache() -> None:
    try:
        import v620_runtime_patch as v620
        v620._TTLS["me"] = 12.0
        v620._TTLS["list_record_files"] = 10.0
        v620._TTLS["record_file_counts"] = 30.0
        v620._TTLS["approval_users"] = 30.0
        v620._TTLS["list_users"] = 20.0
        v620._TTLS["root_info"] = 60.0
    except Exception:
        pass


def install_runtime() -> None:
    """Install V6.21 workflow compatibility + Railway web performance patches."""
    _install_v621_base()
    _tune_gateway_cache()
    _install_sqlite_fast_path()
