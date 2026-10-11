import os
import tempfile
import pytest

from src.database.db import Database
from src.database.migrator import DatabaseMigrator
from src.database.seed import seed_database
from src.security.password import hash_password, verify_password
from src.security.auth_service import AuthService
from src.security.rbac import check_store_access

def test_password_hashing():
    pwd = "SecretPassword123!"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed)
    assert not verify_password("WrongPassword", hashed)

def test_auth_service_sessions_and_store_assignment():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_auth.db")
        db = Database(db_path=db_path)
        migrator = DatabaseMigrator(db)
        migrator.run_migrations()
        seed_database(db)

        auth = AuthService(db)

        # 1. Login with invalid credentials
        assert auth.login("admin", "wrong_password") is None

        # 2. Login as admin
        admin_sess = auth.login("admin", "Admin@123456")
        assert admin_sess is not None
        assert admin_sess.role == "admin"
        assert auth.get_session(admin_sess.token) is not None

        # 3. Create a staff user assigned to ZARA store
        new_staff = auth.create_user(
            username="staff_zara_test",
            password="password123",
            full_name="Nhân viên ZARA",
            role="staff",
            store_ids=["store_zara"],
            creator_session=admin_sess
        )
        assert new_staff.username == "staff_zara_test"

        # 4. Login as staff
        staff_sess = auth.login("staff_zara_test", "password123")
        assert staff_sess is not None
        assert staff_sess.role == "staff"
        assert "store_zara" in staff_sess.assigned_store_ids

        # 5. Check store scoping using check_store_access
        assert check_store_access(staff_sess, "store_zara") is True
        assert check_store_access(staff_sess, "store_uniqlo") is False

        # Admin can manage any store
        assert check_store_access(admin_sess, "store_uniqlo") is True

        # 6. Deactivate staff account
        auth.set_user_active(new_staff.id, False, admin_sess)
        deactivated_sess = auth.login("staff_zara_test", "password123")
        assert deactivated_sess is None

        # 7. Logout
        auth.logout(admin_sess.token)
        assert auth.get_session(admin_sess.token) is None
