import pytest
import time
from starlette.testclient import TestClient
from src.config import RobotConfig
from src.services.robot_controller import RobotController

@pytest.fixture
def test_setup():
    cfg = RobotConfig(SIMULATION_MODE=True, PAIRING_CODE_TTL=60.0)
    robot = RobotController(cfg)
    # Clean delivery orders for test isolation
    robot.mall.db.execute("UPDATE delivery_orders SET status = 'COMPLETED' WHERE status NOT IN ('COMPLETED', 'CANCELLED')")
    robot.mall.active_order = None
    robot.mall.active_order_id = None
    robot.start(start_server=False)
    tc = TestClient(robot.api_app)
    yield tc, robot
    robot.shutdown()

# ==================== 1. GUEST EXPERIENCE & SECURITY AUDIT ====================

def test_guest_public_access_and_security(test_setup):
    tc, robot = test_setup
    
    # 1.1 Health & info accessible publicly
    health = tc.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    # 1.2 Stores and POIs accessible
    stores = tc.get("/api/v1/mall/stores")
    assert stores.status_code == 200
    store_list = stores.json()["stores"]
    assert len(store_list) >= 6

    pois = tc.get("/api/v1/mall/pois?include_staff=false")
    assert pois.status_code == 200
    poi_list = pois.json()["pois"]
    assert len(poi_list) >= 8
    assert all(not p.get("is_staff_only") for p in poi_list)

    # 1.3 Active promotions accessible
    promos = tc.get("/api/v1/mall/promotions")
    assert promos.status_code == 200
    assert isinstance(promos.json()["promotions"], list)

    # 1.4 AI Assistant answering guest questions with grounded data
    ai_res = tc.post("/api/v1/mall/ai/ask", json={"question": "Nhà vệ sinh gần nhất ở đâu?"})
    assert ai_res.status_code == 200
    data = ai_res.json()
    assert "answer" in data

    # 1.5 Security: Guest CANNOT access admin users without auth
    admin_users = tc.get("/api/v1/admin/users")
    assert admin_users.status_code in (401, 403)

    # 1.6 Security: Guest CANNOT access camera stream ticket without staff/admin auth
    cam_ticket = tc.get("/api/v1/camera/ticket")
    assert cam_ticket.status_code in (401, 403)


# ==================== 2. STAFF SCOPED ACCESS & RBAC ENFORCEMENT ====================

def test_staff_authentication_and_store_scoping(test_setup):
    tc, robot = test_setup

    # 2.1 Login as staff_uniqlo with valid seed password
    login_res = tc.post("/api/v1/auth/login", json={
        "username": "staff_uniqlo",
        "password": "Staff@123456"
    })
    assert login_res.status_code == 200
    data = login_res.json()
    assert data["success"] is True
    staff_token = data["token"]
    assert "store_uniqlo" in data["user"]["assignedStoreIds"]
    headers = {"Authorization": f"Bearer {staff_token}"}

    # 2.2 Staff CAN update their assigned store (store_uniqlo)
    update_own = tc.patch(
        "/api/v1/mall/stores/store_uniqlo",
        headers=headers,
        json={"opening_hours": "09:00 - 22:30", "contact_phone": "1900 1122"}
    )
    assert update_own.status_code == 200
    assert update_own.json()["success"] is True

    # 2.3 Staff CANNOT update another store (store_highlands) -> must return 403 Forbidden!
    update_other = tc.patch(
        "/api/v1/mall/stores/store_highlands",
        headers=headers,
        json={"opening_hours": "06:00 - 23:00"}
    )
    assert update_other.status_code == 403

    # 2.4 Staff CAN create promotion for their assigned store
    create_own_promo = tc.post(
        "/api/v1/mall/promotions",
        headers=headers,
        json={
            "storeId": "store_uniqlo",
            "title": "Ưu Đãi Đặc Quyền Thu Đông",
            "description": "Giảm giá 20% cho áo khoác phao Ultra Light Down",
            "discountPercent": 20,
            "promoCode": "AUTUMN20",
            "startTime": time.time(),
            "endTime": time.time() + 86400 * 7
        }
    )
    assert create_own_promo.status_code == 200
    assert create_own_promo.json()["success"] is True

    # 2.5 Staff CANNOT create promotion for unassigned store (store_zara) -> 403 Forbidden!
    create_other_promo = tc.post(
        "/api/v1/mall/promotions",
        headers=headers,
        json={
            "storeId": "store_zara",
            "title": "Unauthorized Promo",
            "description": "Attempting illegal promo creation",
            "discountPercent": 50
        }
    )
    assert create_other_promo.status_code == 403

    # 2.6 Staff CANNOT access admin user management
    admin_access = tc.get("/api/v1/admin/users", headers=headers)
    assert admin_access.status_code == 403


# ==================== 3. ADMIN FULL CAPABILITIES ====================

def test_admin_full_management(test_setup):
    tc, robot = test_setup

    # 3.1 Login as admin
    login_res = tc.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "Admin@123456"
    })
    assert login_res.status_code == 200
    admin_data = login_res.json()
    assert admin_data["success"] is True
    admin_token = admin_data["token"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 3.2 Admin CAN list all user accounts
    users_res = tc.get("/api/v1/admin/users", headers=headers)
    assert users_res.status_code == 200
    user_list = users_res.json()["users"]
    assert len(user_list) >= 2
    assert any(u["username"] == "admin" for u in user_list)

    # 3.3 Admin CAN toggle user active status
    staff_user = next(u for u in user_list if u["role"] == "staff")
    toggle_res = tc.patch(
        f"/api/v1/admin/users/{staff_user['id']}/status",
        headers=headers,
        json={"isActive": False}
    )
    assert toggle_res.status_code == 200
    assert toggle_res.json()["success"] is True

    # Restore active
    tc.patch(
        f"/api/v1/admin/users/{staff_user['id']}/status",
        headers=headers,
        json={"isActive": True}
    )

    # 3.4 Admin CAN view audit logs
    audit_res = tc.get("/api/v1/admin/audit-logs", headers=headers)
    assert audit_res.status_code == 200
    assert isinstance(audit_res.json()["logs"], list)

    # 3.5 Admin CAN backup SQLite database safely
    backup_res = tc.post("/api/v1/admin/backup-db", headers=headers)
    assert backup_res.status_code == 200
    assert backup_res.json()["success"] is True
    assert "backupPath" in backup_res.json()

    # 3.6 Admin CAN acquire camera streaming ticket
    ticket_res = tc.get("/api/v1/camera/ticket", headers=headers)
    assert ticket_res.status_code == 200
    ticket = ticket_res.json()["ticket"]
    assert len(ticket) > 10

    # Snapshot with ticket
    snap_res = tc.get(f"/api/v1/camera/snapshot?ticket={ticket}")
    assert snap_res.status_code == 200
    assert snap_res.headers["content-type"] == "image/jpeg"

    # 3.7 Emergency Stop and Reset
    estop_res = tc.post("/api/v1/emergency-stop")
    assert estop_res.status_code == 200
    assert estop_res.json()["success"] is True

    reset_res = tc.post("/api/v1/emergency-reset", headers=headers)
    assert reset_res.status_code == 200
    assert reset_res.json()["success"] is True
