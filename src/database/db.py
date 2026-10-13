import os
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, List, Dict, Any, Generator

class Database:
    """
    SQLite Database Manager with:
    - Thread safety (RLock)
    - WAL Mode for high concurrency
    - Enforced Foreign Keys (PRAGMA foreign_keys = ON)
    - Row factory returning dict-like sqlite3.Row
    - Transaction context manager
    """

    _instance: Optional["Database"] = None
    _lock = threading.RLock()

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            data_dir = Path(__file__).resolve().parent.parent.parent / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(data_dir / "mall_delivery.db")
        else:
            p = Path(db_path).resolve()
            p.parent.mkdir(parents=True, exist_ok=True)
            self.db_path = str(p)

        self._thread_lock = threading.RLock()

    @classmethod
    def get_instance(cls, db_path: Optional[str] = None) -> "Database":
        with cls._lock:
            if db_path is not None:
                return cls(db_path)
            if cls._instance is None:
                cls._instance = cls(db_path)
            return cls._instance

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        with self._thread_lock:
            conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            try:
                conn.execute("PRAGMA foreign_keys = ON;")
                conn.execute("PRAGMA journal_mode = WAL;")
                conn.execute("PRAGMA busy_timeout = 10000;")
                conn.execute("PRAGMA synchronous = NORMAL;")
            except Exception:
                pass

            try:
                yield conn
            finally:
                conn.close()

    def execute(self, query: str, params: tuple = ()) -> int:
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.rowcount

    def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            row = conn.execute(query, params).fetchone()
            return dict(row) if row else None

    def fetchall(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        with self._thread_lock:
            conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            try:
                conn.execute("BEGIN TRANSACTION;")
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()


def get_db(db_path: Optional[str] = None) -> Database:
    return Database.get_instance(db_path)
