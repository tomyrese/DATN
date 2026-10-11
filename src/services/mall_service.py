import os
import time
import uuid
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from src.database.db import Database, get_db
from src.security.auth_service import SessionInfo
from src.services.logging_service import logger

@dataclass
class PointOfInterest:
    id: str
    name: str
    category: str  # 'food', 'fashion', 'entertainment', 'utility', 'staff'
    floor: str     # 'T1'
    x: float       # 0.0 - 100.0 (percentage coordinates)
    y: float
    description: str
    is_staff_only: bool = False
    store_id: Optional[str] = None

@dataclass
class DeliveryOrder:
    order_id: str
    creator_name: str
    pickup_poi_id: str
    pickup_poi_name: str
    dropoff_poi_id: str
    dropoff_poi_name: str
    item_description: str
    status: str  # 'PENDING', 'MOVING_TO_PICKUP', 'ARRIVED_AT_PICKUP', 'DELIVERING', 'ARRIVED_AT_DROPOFF', 'COMPLETED', 'CANCELLED'
    created_at: float
    updated_at: float
    current_progress: int = 0
    phase_started_at: float = 0.0
    creator_user_id: Optional[str] = None

@dataclass
class EscortTask:
    task_id: str
    target_poi_id: str
    target_name: str
    target_floor: str
    status: str  # 'IDLE', 'NAVIGATING', 'ARRIVED', 'CANCELLED'
    started_at: float
    estimated_seconds: int = 25
    current_progress: int = 0
    target_x: float = 50.0
    target_y: float = 50.0

class MallService:
    """
    Central Shopping Mall Business Logic Service.
    Interacts with SQLite Normalized Schema:
    - Stores, Floors, POIs
    - Store-scoped Promotions (RBAC: Staff can only edit their assigned store, Admin edits all)
    - Persistent Delivery Orders with FIFO Queue
    - Customer Escort Tasks
    - Mall FAQ Knowledge Base
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db = get_db(db_path)
        self._lock = threading.RLock()
        self.current_escort: Optional[EscortTask] = None
        self.active_order_id: Optional[str] = None
        self.active_order: Optional[DeliveryOrder] = None

        self._load_active_order()

    # ==================== STORES & FLOORS ====================
    def get_floors(self) -> List[Dict[str, Any]]:
        return self.db.fetchall("SELECT * FROM mall_floors ORDER BY level_index ASC")

    def get_stores(self, active_only: bool = True) -> List[Dict[str, Any]]:
        query = "SELECT * FROM stores" + (" WHERE is_active = 1" if active_only else "") + " ORDER BY name ASC"
        return self.db.fetchall(query)

    def get_store(self, store_id: str) -> Optional[Dict[str, Any]]:
        return self.db.fetchone("SELECT * FROM stores WHERE id = ?", (store_id,))

    def update_store(self, store_id: str, data: Dict[str, Any]) -> bool:
        allowed_keys = ["name", "description", "contact_phone", "opening_hours", "is_active"]
        updates = []
        params = []
        for k in allowed_keys:
            if k in data:
                updates.append(f"{k} = ?")
                params.append(data[k])
        if not updates:
            return False

        params.append(store_id)
        sql = f"UPDATE stores SET {', '.join(updates)} WHERE id = ?"
        return self.db.execute(sql, tuple(params)) > 0

    # ==================== POIS ====================
    def get_pois(self, include_staff: bool = False) -> List[Dict[str, Any]]:
        query = "SELECT id, name, category, floor_id as floor, x, y, description, is_staff_only, store_id FROM mall_pois"
        if not include_staff:
            query += " WHERE is_staff_only = 0"
        query += " ORDER BY name ASC"
        return self.db.fetchall(query)

    def get_poi(self, poi_id: str) -> Optional[PointOfInterest]:
        row = self.db.fetchone("SELECT * FROM mall_pois WHERE id = ?", (poi_id,))
        if not row:
            return None
        return PointOfInterest(
            id=row["id"],
            name=row["name"],
            category=row["category"],
            floor=row["floor_id"],
            x=float(row["x"]),
            y=float(row["y"]),
            description=row["description"] or "",
            is_staff_only=bool(row["is_staff_only"]),
            store_id=row["store_id"]
        )

    # ==================== PROMOTIONS (WITH RBAC STORE SCOPING) ====================
    def get_promotions(self, store_id: Optional[str] = None, active_only: bool = True) -> List[Dict[str, Any]]:
        now = time.time()
        sql = """
            SELECT p.*, s.name as store_name
            FROM promotions p
            JOIN stores s ON p.store_id = s.id
        """
        clauses = []
        params = []

        if store_id:
            clauses.append("p.store_id = ?")
            params.append(store_id)

        if active_only:
            clauses.append("p.is_active = 1 AND p.end_time >= ?")
            params.append(now)

        if clauses:
            sql += " WHERE " + " AND ".join(clauses)

        sql += " ORDER BY p.start_time DESC"
        return self.db.fetchall(sql, tuple(params))

    def create_promotion(
        self,
        store_id: str,
        title: str,
        description: str,
        discount_percent: Optional[int],
        promo_code: Optional[str],
        banner_url: Optional[str],
        start_time: float,
        end_time: float,
        session: SessionInfo
    ) -> Dict[str, Any]:
        # Validate store scoping
        if session.role == "staff" and store_id not in session.assigned_store_ids:
            raise PermissionError(f"Staff '{session.username}' is not authorized to manage promotions for store '{store_id}'")

        promo_id = f"prm_{int(time.time())}_{uuid.uuid4().hex[:4]}"
        now = time.time()

        self.db.execute("""
            INSERT INTO promotions (id, title, store_id, description, discount_percent, promo_code, banner_url, start_time, end_time, is_active, created_by, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            promo_id, title, store_id, description, discount_percent, promo_code,
            banner_url, start_time, end_time, 1, session.user_id, now, now
        ))

        logger.info(f"Promotion created: {promo_id} ('{title}') for store '{store_id}' by {session.username}")
        row = self.db.fetchone("SELECT * FROM promotions WHERE id = ?", (promo_id,))
        return dict(row) if row else {}

    def update_promotion(
        self,
        promo_id: str,
        data: Dict[str, Any],
        session: SessionInfo
    ) -> bool:
        promo = self.db.fetchone("SELECT * FROM promotions WHERE id = ?", (promo_id,))
        if not promo:
            return False

        # Validate store scoping
        if session.role == "staff" and promo["store_id"] not in session.assigned_store_ids:
            raise PermissionError(f"Staff '{session.username}' is not authorized to modify promotions for store '{promo['store_id']}'")

        allowed_keys = ["title", "description", "discount_percent", "promo_code", "banner_url", "start_time", "end_time", "is_active"]
        updates = ["updated_at = ?"]
        params = [time.time()]

        for k in allowed_keys:
            if k in data:
                updates.append(f"{k} = ?")
                params.append(data[k])

        params.append(promo_id)
        sql = f"UPDATE promotions SET {', '.join(updates)} WHERE id = ?"
        return self.db.execute(sql, tuple(params)) > 0

    def delete_promotion(self, promo_id: str, session: SessionInfo) -> bool:
        promo = self.db.fetchone("SELECT * FROM promotions WHERE id = ?", (promo_id,))
        if not promo:
            return False

        if session.role == "staff" and promo["store_id"] not in session.assigned_store_ids:
            raise PermissionError(f"Staff '{session.username}' is not authorized to delete promotions for store '{promo['store_id']}'")

        return self.db.execute("DELETE FROM promotions WHERE id = ?", (promo_id,)) > 0

    # ==================== DELIVERY ORDERS & FIFO QUEUE ====================
    def _load_active_order(self):
        with self._lock:
            row = self.db.fetchone(
                "SELECT * FROM delivery_orders WHERE status IN ('MOVING_TO_PICKUP', 'ARRIVED_AT_PICKUP', 'DELIVERING', 'ARRIVED_AT_DROPOFF') ORDER BY created_at ASC LIMIT 1"
            )
            if row:
                self.active_order = DeliveryOrder(**dict(row))
                self.active_order_id = self.active_order.order_id
            else:
                self.active_order = None
                self.active_order_id = None

    def create_delivery_order(
        self,
        creator_name: str,
        pickup_poi_id: str,
        dropoff_poi_id: str,
        item_description: str,
        creator_user_id: Optional[str] = None
    ) -> DeliveryOrder:
        pickup = self.get_poi(pickup_poi_id)
        dropoff = self.get_poi(dropoff_poi_id)

        pickup_name = pickup.name if pickup else pickup_poi_id
        dropoff_name = dropoff.name if dropoff else dropoff_poi_id

        order_id = f"ORD-{int(time.time()) % 10000:04d}-{uuid.uuid4().hex[:4].upper()}"
        now = time.time()

        with self._lock:
            should_start_now = self.active_order is None and (self.current_escort is None or self.current_escort.status != "NAVIGATING")
            initial_status = "MOVING_TO_PICKUP" if should_start_now else "PENDING"
            initial_progress = 0

            order = DeliveryOrder(
                order_id=order_id,
                creator_name=creator_name or "Nhân viên",
                pickup_poi_id=pickup_poi_id,
                pickup_poi_name=pickup_name,
                dropoff_poi_id=dropoff_poi_id,
                dropoff_poi_name=dropoff_name,
                item_description=item_description or "Kiện hàng nội bộ",
                status=initial_status,
                created_at=now,
                updated_at=now,
                current_progress=initial_progress,
                phase_started_at=now if should_start_now else 0.0,
                creator_user_id=creator_user_id
            )

            self.db.execute("""
                INSERT INTO delivery_orders
                (order_id, creator_name, creator_user_id, pickup_poi_id, pickup_poi_name, dropoff_poi_id, dropoff_poi_name, item_description, status, created_at, updated_at, current_progress, phase_started_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order.order_id, order.creator_name, order.creator_user_id, order.pickup_poi_id, order.pickup_poi_name,
                order.dropoff_poi_id, order.dropoff_poi_name, order.item_description,
                order.status, order.created_at, order.updated_at, order.current_progress, order.phase_started_at
            ))

            if should_start_now:
                self.active_order_id = order_id
                self.active_order = order

            return order

    def get_order(self, order_id: str) -> Optional[DeliveryOrder]:
        with self._lock:
            if self.active_order and self.active_order.order_id == order_id:
                return self.active_order
            row = self.db.fetchone("SELECT * FROM delivery_orders WHERE order_id = ?", (order_id,))
            return DeliveryOrder(**dict(row)) if row else None

    def get_active_order(self) -> Optional[DeliveryOrder]:
        with self._lock:
            if self.active_order and self.active_order.status in ('MOVING_TO_PICKUP', 'ARRIVED_AT_PICKUP', 'DELIVERING', 'ARRIVED_AT_DROPOFF'):
                return self.active_order
            return self._try_dispatch_next_in_queue()

    def _try_dispatch_next_in_queue(self) -> Optional[DeliveryOrder]:
        with self._lock:
            if self.current_escort and self.current_escort.status == "NAVIGATING":
                return None

            row = self.db.fetchone("SELECT * FROM delivery_orders WHERE status = 'PENDING' ORDER BY created_at ASC LIMIT 1")
            if row:
                order = DeliveryOrder(**dict(row))
                now = time.time()
                order.status = "MOVING_TO_PICKUP"
                order.updated_at = now
                order.phase_started_at = now
                order.current_progress = 0

                self.db.execute(
                    "UPDATE delivery_orders SET status = ?, updated_at = ?, phase_started_at = ?, current_progress = ? WHERE order_id = ?",
                    (order.status, order.updated_at, order.phase_started_at, order.current_progress, order.order_id)
                )

                self.active_order_id = order.order_id
                self.active_order = order
                logger.info(f"Dispatched next queued delivery order: {order.order_id}")
                return order

            self.active_order_id = None
            self.active_order = None
            return None

    def update_order_progress(self, order_id: str, progress: int):
        now = time.time()
        with self._lock:
            if self.active_order and self.active_order.order_id == order_id:
                self.active_order.current_progress = progress
                self.active_order.updated_at = now

            self.db.execute(
                "UPDATE delivery_orders SET current_progress = ?, updated_at = ? WHERE order_id = ?",
                (progress, now, order_id)
            )

    def update_order_status(self, order_id: str, new_status: str, progress: Optional[int] = None) -> bool:
        now = time.time()
        with self._lock:
            row = self.db.fetchone("SELECT * FROM delivery_orders WHERE order_id = ?", (order_id,))
            if not row:
                return False

            old_order = DeliveryOrder(**dict(row))
            prog = progress if progress is not None else old_order.current_progress
            phase_start = now if new_status != old_order.status else old_order.phase_started_at

            self.db.execute(
                "UPDATE delivery_orders SET status = ?, updated_at = ?, current_progress = ?, phase_started_at = ? WHERE order_id = ?",
                (new_status, now, prog, phase_start, order_id)
            )

            if self.active_order and self.active_order.order_id == order_id:
                self.active_order.status = new_status
                self.active_order.updated_at = now
                self.active_order.current_progress = prog
                self.active_order.phase_started_at = phase_start

            if new_status in ["COMPLETED", "CANCELLED"] and self.active_order_id == order_id:
                self.active_order_id = None
                self.active_order = None
                self._try_dispatch_next_in_queue()

            return True

    def get_orders(self) -> List[Dict[str, Any]]:
        with self._lock:
            rows = self.db.fetchall("SELECT * FROM delivery_orders ORDER BY created_at DESC LIMIT 50")
            orders = [dict(r) for r in rows]
            if self.active_order:
                for o in orders:
                    if o.get("order_id") == self.active_order.order_id:
                        o["current_progress"] = self.active_order.current_progress
                        o["status"] = self.active_order.status
                        o["updated_at"] = self.active_order.updated_at
            return orders

    # ==================== ESCORT NAVIGATION ====================
    def request_escort(self, target_poi_id: str) -> Optional[EscortTask]:
        poi = self.get_poi(target_poi_id)
        if not poi:
            return None

        task_id = f"ESC-{uuid.uuid4().hex[:6].upper()}"
        task = EscortTask(
            task_id=task_id,
            target_poi_id=target_poi_id,
            target_name=poi.name,
            target_floor="Sảnh Chính T1",
            status="NAVIGATING",
            started_at=time.time(),
            estimated_seconds=25,
            current_progress=0,
            target_x=poi.x,
            target_y=poi.y
        )
        self.current_escort = task
        logger.info(f"Customer Escort initiated to '{poi.name}' (Task ID: {task_id})")
        return task

    def get_escort_status(self) -> Optional[Dict[str, Any]]:
        if self.current_escort:
            return asdict(self.current_escort)
        return None

    def cancel_escort(self) -> bool:
        if self.current_escort:
            self.current_escort.status = "CANCELLED"
            self.current_escort = None
            logger.info("Customer escort cancelled")
            return True
        return False

    # ==================== FAQ & KNOWLEDGE BASE ====================
    def get_faq_items(self) -> List[Dict[str, Any]]:
        return self.db.fetchall("SELECT * FROM mall_faq WHERE is_active = 1")
