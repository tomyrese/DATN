import os
import sqlite3
import tempfile
import pytest

from src.database.db import Database
from src.database.migrator import DatabaseMigrator
from src.database.seed import seed_database

def test_sqlite_foreign_keys_and_wal():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_schema.db")
        db = Database(db_path=db_path)

        # Check WAL mode
        mode = db.fetchone("PRAGMA journal_mode")["journal_mode"]
        assert mode.lower() == "wal"

        # Check Foreign Keys
        fk = db.fetchone("PRAGMA foreign_keys")["foreign_keys"]
        assert fk == 1

        # Run migrations
        migrator = DatabaseMigrator(db)
        migrator.run_migrations()
        assert max(migrator.get_applied_versions()) >= 2

        # Verify tables exist
        tables = [r["name"] for r in db.fetchall("SELECT name FROM sqlite_master WHERE type='table'")]
        assert "users" in tables
        assert "stores" in tables
        assert "map_nodes" in tables
        assert "map_edges" in tables
        assert "promotions" in tables
        assert "delivery_orders" in tables
        assert "audit_logs" in tables

        # Foreign Key constraint check: inserting promotion with non-existent store_id should fail
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("""
                INSERT INTO promotions (id, store_id, title, discount_percent, start_time, end_time)
                VALUES ('p1', 'non_existent_store', 'Sale', 10, '2026-01-01', '2026-12-31')
            """)

def test_database_backup_and_seed():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_backup.db")
        db = Database(db_path=db_path)
        migrator = DatabaseMigrator(db)
        migrator.run_migrations()

        seed_database(db)

        # Verify seed records
        admin = db.fetchone("SELECT * FROM users WHERE username = 'admin'")
        assert admin is not None
        assert admin["role"] == "admin"

        stores = db.fetchall("SELECT * FROM stores")
        assert len(stores) >= 5

        nodes = db.fetchall("SELECT * FROM map_nodes")
        assert len(nodes) >= 10

        # Backup creation
        backup_path = migrator.backup_database()
        assert os.path.exists(backup_path)
        assert os.path.getsize(backup_path) > 0
