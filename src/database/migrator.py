import os
import shutil
import time
from pathlib import Path
from typing import List, Tuple
from src.database.db import Database, get_db
from src.services.logging_service import logger

class DatabaseMigrator:
    """
    Handles SQLite database schema migrations:
    - Pre-migration backup
    - Tracking applied migrations via schema_migrations
    - Transactional execution
    """

    def __init__(self, db: Database):
        self.db = db

    def backup_database(self) -> str:
        db_path = Path(self.db.db_path)
        if not db_path.exists():
            return ""

        timestamp = int(time.time())
        backup_path = db_path.parent / f"{db_path.name}.backup_{timestamp}"
        shutil.copy2(db_path, backup_path)
        logger.info(f"Database backed up to {backup_path}")
        return str(backup_path)

    def init_migration_table(self):
        with self.db.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    applied_at REAL NOT NULL
                );
            """)
            conn.commit()

    def get_applied_versions(self) -> List[int]:
        self.init_migration_table()
        with self.db.get_connection() as conn:
            rows = conn.execute("SELECT version FROM schema_migrations ORDER BY version ASC").fetchall()
            return [r["version"] for r in rows]

    def run_migrations(self) -> bool:
        self.init_migration_table()
        applied = set(self.get_applied_versions())

        # Migration 1: Full v2.0 Normalized Schema
        if 1 not in applied:
            schema_path = Path(__file__).resolve().parent / "schema.sql"
            if not schema_path.exists():
                logger.error(f"Schema file not found at {schema_path}")
                return False

            self.backup_database()
            logger.info("Applying Migration 1: Full v2.0 Normalized Schema...")
            with open(schema_path, "r", encoding="utf-8") as f:
                ddl = f.read()

            with self.db.transaction() as conn:
                conn.executescript(ddl)
                conn.execute(
                    "INSERT INTO schema_migrations (version, name, applied_at) VALUES (?, ?, ?)",
                    (1, "v2_0_normalized_schema", time.time())
                )
            logger.info("Migration 1 applied successfully!")

        # Migration 2: Ensure delivery_orders has creator_user_id
        if 2 not in applied:
            with self.db.transaction() as conn:
                cols = [c[1] for c in conn.execute("PRAGMA table_info(delivery_orders)").fetchall()]
                if "creator_user_id" not in cols:
                    conn.execute("ALTER TABLE delivery_orders ADD COLUMN creator_user_id TEXT;")
                conn.execute(
                    "INSERT INTO schema_migrations (version, name, applied_at) VALUES (?, ?, ?)",
                    (2, "add_creator_user_id_to_orders", time.time())
                )
            logger.info("Migration 2 applied successfully!")

        return True


def run_database_migrations(db_path: str = None) -> bool:
    db = get_db(db_path)
    migrator = DatabaseMigrator(db)
    return migrator.run_migrations()
