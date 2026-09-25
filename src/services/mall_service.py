import os
import time
import uuid
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

@dataclass
class PointOfInterest:
    id: str
    name: str
    category: str  # 'food', 'fashion', 'entertainment', 'utility', 'staff'
    floor: str     # 'T1' (Single unified floor)
    x: float       # 0.0 - 100.0 (percentage coordinates on map)
    y: float
    description: str
    is_staff_only: bool = False

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
    current_progress: int = 0  # 0 - 100%
    phase_started_at: float = 0.0

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

class MallService:
    """
    Manages Shopping Mall Points of Interest (POIs), SQLite Persistent Delivery Orders,
    FIFO Delivery Queue for Multi-User concurrency, and Customer Escort Navigation.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            data_dir = Path(__file__).resolve().parent.parent.parent / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(data_dir / "mall_delivery.db")
        else:
            self.db_path = db_path

        self.pois: Dict[str, PointOfInterest] = self._init_default_pois()
        self.current_escort: Optional[EscortTask] = None
        self.active_order_id: Optional[str] = None
        self.robot_pos = {"x": 50.0, "y": 68.0, "floor": "T1", "heading": 0.0}

        self._init_db()
        self._load_active_order()

    @contextmanager
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS delivery_orders (
                    order_id TEXT PRIMARY KEY,
                    creator_name TEXT,
                    pickup_poi_id TEXT,
                    pickup_poi_name TEXT,
                    dropoff_poi_id TEXT,
                    dropoff_poi_name TEXT,
                    item_description TEXT,
                    status TEXT,
                    created_at REAL,
                    updated_at REAL,
                    current_progress INTEGER DEFAULT 0,
                    phase_started_at REAL DEFAULT 0.0
                )
            """)
            conn.commit()

    def _load_active_order(self):
        with self._get_conn() as conn:
            cursor = conn.execute(
                "SELECT order_id FROM delivery_orders WHERE status IN ('MOVING_TO_PICKUP', 'ARRIVED_AT_PICKUP', 'DELIVERING', 'ARRIVED_AT_DROPOFF') ORDER BY created_at ASC LIMIT 1"
            )
            row = cursor.fetchone()
            if row:
                self.active_order_id = row["order_id"]

    def _init_default_pois(self) -> Dict[str, PointOfInterest]:
        default_list = [
            # Khu Trung Tâm & Tiện Ích
            PointOfInterest("poi_reception", "Quầy Lễ Tân & CSKH", "utility", "T1", 50.0, 72.0, "Sảnh chính trung tâm, hỗ trợ đổi quà, chỉ đường và thông tin."),
            PointOfInterest("poi_wc", "Khu Vệ Sinh & Tiện Ích", "utility", "T1", 82.0, 72.0, "Nhà vệ sinh hiện đại Nam, Nữ và phòng chăm sóc em bé."),
            PointOfInterest("poi_elevator", "Thang Máy & Bãi Đỗ Xe", "utility", "T1", 18.0, 72.0, "Cụm thang máy lồng kính và lối xuống bãi đỗ xe."),

            # Khu Thời Trang Quốc Tế
            PointOfInterest("poi_uniqlo", "UNIQLO LifeWear", "fashion", "T1", 20.0, 24.0, "Thời trang phong cách Nhật Bản, trang phục nam, nữ và trẻ em."),
            PointOfInterest("poi_zara", "Thời Trang ZARA", "fashion", "T1", 80.0, 24.0, "Thương hiệu thời trang cao cấp Tây Ban Nha mới nhất."),

            # Khu Ẩm Thực & Cafe
            PointOfInterest("poi_highlands", "Highlands Coffee", "food", "T1", 20.0, 48.0, "Cà phê pha phin truyền thống, Freeze và bánh ngọt."),
            PointOfInterest("poi_kura_sushi", "Nhà Hàng Kura Sushi", "food", "T1", 50.0, 24.0, "Sushi băng chuyền công nghệ cao và ẩm thực Nhật."),

            # Khu Giải Trí
            PointOfInterest("poi_cgv", "Rạp Phim CGV Cinemas", "entertainment", "T1", 80.0, 48.0, "Cụm rạp chiếu phim IMAX & 4DX hiện đại bậc nhất."),

            # Khu Vực Nội Bộ Nhân Viên (Staff Only)
            PointOfInterest("poi_warehouse", "Kho Giao Nhận Hàng Nội Bộ", "staff", "T1", 90.0, 88.0, "Khu vực bốc dỡ và xuất nhập hàng hóa nội bộ.", is_staff_only=True),
        ]
        return {p.id: p for p in default_list}

    def get_pois(self, include_staff: bool = False) -> List[Dict[str, Any]]:
        return [
            asdict(p) for p in self.pois.values()
            if include_staff or not p.is_staff_only
        ]

    def get_poi(self, poi_id: str) -> Optional[PointOfInterest]:
        return self.pois.get(poi_id)

    # ==================== DELIVERY ORDERS & QUEUE (SQLITE PERSISTENCE) ====================
    def create_delivery_order(
        self,
        creator_name: str,
        pickup_poi_id: str,
        dropoff_poi_id: str,
        item_description: str
    ) -> DeliveryOrder:
        pickup = self.pois.get(pickup_poi_id)
        dropoff = self.pois.get(dropoff_poi_id)

        pickup_name = pickup.name if pickup else pickup_poi_id
        dropoff_name = dropoff.name if dropoff else dropoff_poi_id

        order_id = f"ORD-{int(time.time() * 1000) % 100000:05d}"
        now = time.time()

        # Check if robot is currently idle to start immediately, or place in queue
        should_start_now = self.active_order_id is None and (self.current_escort is None or self.current_escort.status != "NAVIGATING")
        initial_status = "MOVING_TO_PICKUP" if should_start_now else "PENDING"
        initial_progress = 0 if should_start_now else 0

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
            phase_started_at=now if should_start_now else 0.0
        )

        with self._get_conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO delivery_orders
                (order_id, creator_name, pickup_poi_id, pickup_poi_name, dropoff_poi_id, dropoff_poi_name, item_description, status, created_at, updated_at, current_progress, phase_started_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order.order_id, order.creator_name, order.pickup_poi_id, order.pickup_poi_name,
                order.dropoff_poi_id, order.dropoff_poi_name, order.item_description,
                order.status, order.created_at, order.updated_at, order.current_progress, order.phase_started_at
            ))
            conn.commit()

        if should_start_now:
            self.active_order_id = order_id

        return order

    def get_order(self, order_id: str) -> Optional[DeliveryOrder]:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM delivery_orders WHERE order_id = ?", (order_id,)).fetchone()
            if row:
                return DeliveryOrder(**dict(row))
        return None

    def get_active_order(self) -> Optional[DeliveryOrder]:
        if not self.active_order_id:
            # Try to fetch next in queue
            self._try_dispatch_next_in_queue()
        if self.active_order_id:
            return self.get_order(self.active_order_id)
        return None

    def _try_dispatch_next_in_queue(self) -> Optional[DeliveryOrder]:
        if self.current_escort and self.current_escort.status == "NAVIGATING":
            return None

        with self._get_conn() as conn:
            cursor = conn.execute(
                "SELECT * FROM delivery_orders WHERE status = 'PENDING' ORDER BY created_at ASC LIMIT 1"
            )
            row = cursor.fetchone()
            if row:
                order = DeliveryOrder(**dict(row))
                now = time.time()
                order.status = "MOVING_TO_PICKUP"
                order.updated_at = now
                order.phase_started_at = now
                order.current_progress = 0

                conn.execute(
                    "UPDATE delivery_orders SET status = ?, updated_at = ?, phase_started_at = ?, current_progress = ? WHERE order_id = ?",
                    (order.status, order.updated_at, order.phase_started_at, order.current_progress, order.order_id)
                )
                conn.commit()

                self.active_order_id = order.order_id
                return order
        return None

    def update_order_progress(self, order_id: str, progress: int):
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE delivery_orders SET current_progress = ?, updated_at = ? WHERE order_id = ?",
                (progress, time.time(), order_id)
            )
            conn.commit()

    def update_order_status(self, order_id: str, new_status: str, progress: Optional[int] = None) -> bool:
        now = time.time()
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM delivery_orders WHERE order_id = ?", (order_id,)).fetchone()
            if not row:
                return False

            old_order = DeliveryOrder(**dict(row))
            prog = progress if progress is not None else old_order.current_progress
            phase_start = now if new_status != old_order.status else old_order.phase_started_at

            conn.execute(
                "UPDATE delivery_orders SET status = ?, updated_at = ?, current_progress = ?, phase_started_at = ? WHERE order_id = ?",
                (new_status, now, prog, phase_start, order_id)
            )
            conn.commit()

        if new_status in ["COMPLETED", "CANCELLED"] and self.active_order_id == order_id:
            self.active_order_id = None
            # Dispatch next pending order in queue
            self._try_dispatch_next_in_queue()

        return True

    def get_orders(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM delivery_orders ORDER BY created_at DESC LIMIT 50").fetchall()
            return [dict(r) for r in rows]

    # ==================== ESCORT NAVIGATION (CUSTOMERS) ====================
    def request_escort(self, target_poi_id: str) -> Optional[EscortTask]:
        poi = self.pois.get(target_poi_id)
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
            estimated_seconds=20,
            current_progress=0
        )
        self.current_escort = task
        return task

    def get_escort_status(self) -> Optional[Dict[str, Any]]:
        if self.current_escort:
            return asdict(self.current_escort)
        return None

    def cancel_escort(self) -> bool:
        if self.current_escort:
            self.current_escort.status = "CANCELLED"
            self.current_escort = None
            return True
        return False

    # ==================== AI CONCIERGE Q&A ====================
    def ask_concierge(self, question: str) -> Dict[str, Any]:
        q = question.lower()

        # Toilet / WC
        if any(k in q for k in ["vệ sinh", "toilet", "wc", "nhà tắm", "rửa tay"]):
            return {
                "answer": "Nhà vệ sinh hiện đại nằm ở phía Đông sảnh Tầng 1 (cạnh cụm rạp CGV). Quý khách có thể yêu cầu tôi dẫn đường trực tiếp đến đó!",
                "suggested_poi_id": "poi_wc",
                "suggested_poi_name": "Khu Vệ Sinh & Tiện Ích"
            }

        # Coffee / Tea / Drinks
        if any(k in q for k in ["cafe", "cà phê", "highlands", "nước", "uống"]):
            return {
                "answer": "Quán Highlands Coffee nằm ở khu ẩm thực Tầng 1 với không gian thoáng mát và cà phê pha phin truyền thống. Quý khách muốn tôi dẫn đường đến đó không ạ?",
                "suggested_poi_id": "poi_highlands",
                "suggested_poi_name": "Highlands Coffee"
            }

        # Sushi / Food / Eating
        if any(k in q for k in ["sushi", "ăn", "lẩu", "nhà hàng", "kura"]):
            return {
                "answer": "Nhà hàng Kura Sushi nằm ngay trung tâm Tầng 1 với sushi băng chuyền tươi ngon. Bấm nút bên dưới để tôi đưa quý khách đến quán nhé!",
                "suggested_poi_id": "poi_kura_sushi",
                "suggested_poi_name": "Nhà Hàng Kura Sushi"
            }

        # Fashion / Clothes
        if any(k in q for k in ["quần áo", "thời trang", "uniqlo", "áo", "quần"]):
            return {
                "answer": "Cửa hàng UNIQLO LifeWear nằm ở cánh Tây Tầng 1 với đầy đủ các bộ sưu tập thời trang mới nhất. Quý khách bấm vào nút bên dưới để tôi dẫn đường nhé!",
                "suggested_poi_id": "poi_uniqlo",
                "suggested_poi_name": "UNIQLO LifeWear"
            }

        if any(k in q for k in ["zara", "váy", "đầm"]):
            return {
                "answer": "Showroom thời trang ZARA nằm ở cánh Đông Tầng 1. Quý khách có thể đi theo tôi để đến cửa hàng ngay!",
                "suggested_poi_id": "poi_zara",
                "suggested_poi_name": "Thời Trang ZARA"
            }

        # Cinema / Movies
        if any(k in q for k in ["phim", "cgv", "rạp", "cinema", "vé"]):
            return {
                "answer": "Cụm rạp CGV Cinemas nằm ở tầng 1 với phòng chiếu IMAX & 4DX hiện đại. Bấm nút dưới đây để tôi dẫn quý khách đến quầy vé!",
                "suggested_poi_id": "poi_cgv",
                "suggested_poi_name": "Rạp Phim CGV Cinemas"
            }

        # Elevator
        if any(k in q for k in ["thang máy", "bãi xe", "gửi xe", "đỗ xe", "xe"]):
            return {
                "answer": "Cụm Thang Máy lồng kính và lối xuống bãi đỗ xe nằm ở phía Tây Tầng 1. Tôi có thể dẫn quý khách đến ngay cửa thang máy!",
                "suggested_poi_id": "poi_elevator",
                "suggested_poi_name": "Thang Máy & Bãi Đỗ Xe"
            }

        # Reception
        if any(k in q for k in ["lễ tân", "cskh", "đổi quà", "hỏi đáp", "quầy"]):
            return {
                "answer": "Quầy Lễ Tân & Chăm Sóc Khách Hàng nằm ngay sảnh chính Tầng 1. Quý khách có thể đến để được tư vấn và đổi quà khuyến mãi!",
                "suggested_poi_id": "poi_reception",
                "suggested_poi_name": "Quầy Lễ Tân & CSKH"
            }

        # Default Mall Info
        return {
            "answer": "Trung tâm thương mại mở cửa từ 09:00 - 22:00 tất cả các ngày trong tuần. Miễn phí WiFi 'MALL_GUEST_FREE'. Quý khách có thể chạm vào bản đồ hoặc hỏi tôi về bất kỳ gian hàng nào!",
            "suggested_poi_id": None,
            "suggested_poi_name": None
        }
