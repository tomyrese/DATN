import time
import uuid
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

@dataclass
class EscortTask:
    task_id: str
    target_poi_id: str
    target_name: str
    target_floor: str
    status: str  # 'IDLE', 'NAVIGATING', 'ARRIVED', 'CANCELLED'
    started_at: float
    estimated_seconds: int = 45
    current_progress: int = 0

class MallService:
    """
    Manages Single-Floor Shopping Mall Points of Interest (POIs),
    Delivery Orders for Staff, Customer Escort Navigation, and Concierge Q&A.
    """

    def __init__(self):
        self.pois: Dict[str, PointOfInterest] = self._init_default_pois()
        self.orders: Dict[str, DeliveryOrder] = {}
        self.active_order_id: Optional[str] = None
        self.current_escort: Optional[EscortTask] = None
        self.robot_pos = {"x": 50.0, "y": 68.0, "floor": "T1", "heading": 0.0}

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
            PointOfInterest("poi_phuclong", "Trà Phúc Long", "food", "T1", 36.0, 48.0, "Trà sữa Ô Long, Trà đào và thức uống thanh mát."),
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

    # ==================== DELIVERY ORDERS (STAFF) ====================
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

        order_id = f"ORD-{int(time.time()) % 10000:04d}"
        now = time.time()
        order = DeliveryOrder(
            order_id=order_id,
            creator_name=creator_name or "Nhân viên",
            pickup_poi_id=pickup_poi_id,
            pickup_poi_name=pickup_name,
            dropoff_poi_id=dropoff_poi_id,
            dropoff_poi_name=dropoff_name,
            item_description=item_description or "Kiện hàng nội bộ",
            status="PENDING",
            created_at=now,
            updated_at=now,
            current_progress=5
        )
        self.orders[order_id] = order
        if not self.active_order_id:
            self.start_order_execution(order_id)
        return order

    def start_order_execution(self, order_id: str) -> bool:
        if order_id not in self.orders:
            return False
        self.active_order_id = order_id
        order = self.orders[order_id]
        order.status = "MOVING_TO_PICKUP"
        order.updated_at = time.time()
        order.current_progress = 25
        return True

    def update_order_status(self, order_id: str, new_status: str, progress: Optional[int] = None) -> bool:
        if order_id not in self.orders:
            return False
        order = self.orders[order_id]
        order.status = new_status
        order.updated_at = time.time()
        if progress is not None:
            order.current_progress = progress
        if new_status in ["COMPLETED", "CANCELLED"] and self.active_order_id == order_id:
            self.active_order_id = None
        return True

    def get_orders(self) -> List[Dict[str, Any]]:
        sorted_orders = sorted(self.orders.values(), key=lambda o: o.created_at, reverse=True)
        return [asdict(o) for o in sorted_orders]

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
            target_floor="Sảnh Chính",
            status="NAVIGATING",
            started_at=time.time(),
            estimated_seconds=35,
            current_progress=10
        )
        self.current_escort = task
        return task

    def cancel_escort(self) -> bool:
        if self.current_escort:
            self.current_escort.status = "CANCELLED"
            self.current_escort = None
            return True
        return False

    def get_escort_status(self) -> Optional[Dict[str, Any]]:
        if not self.current_escort:
            return None
        return asdict(self.current_escort)

    # ==================== AI CONCIERGE Q&A ====================
    def ask_concierge(self, question: str) -> Dict[str, Any]:
        q = question.lower().strip()
        
        if any(w in q for w in ["vệ sinh", "toilet", "wc", "nhà tắm", "rửa tay"]):
            return {
                "answer": "Khu vệ sinh trung tâm nằm ở Cánh Đông Nam (cạnh rạp CGV). Quý khách có thể nhấn nút 'Dẫn đường' để robot dẫn đi ngay!",
                "suggested_poi_id": "poi_wc",
                "suggested_poi_name": "Khu Vệ Sinh & Tiện Ích"
            }
        
        if any(w in q for w in ["cà phê", "cafe", "coffee", "highland"]):
            return {
                "answer": "Quán Highlands Coffee nằm ở Cánh Tây Nam sảnh chính với view thoáng mát và nhiều món nước ngon.",
                "suggested_poi_id": "poi_highlands",
                "suggested_poi_name": "Highlands Coffee"
            }

        if any(w in q for w in ["trà", "trà sữa", "phúc long"]):
            return {
                "answer": "Quầy Trà Phúc Long nằm ở Cánh Tây (gần Highlands Coffee). Quý khách muốn robot dẫn đến đó không ạ?",
                "suggested_poi_id": "poi_phuclong",
                "suggested_poi_name": "Trà Phúc Long"
            }

        if any(w in q for w in ["quần áo", "thời trang", "áo", "quần", "zara", "uniqlo"]):
            return {
                "answer": "Trung tâm có 2 gian hàng thời trang lớn: UNIQLO LifeWear (Cánh Tây Bắc) và ZARA (Cánh Đông Bắc).",
                "suggested_poi_id": "poi_zara",
                "suggested_poi_name": "Thời Trang ZARA"
            }

        if any(w in q for w in ["phim", "cinema", "cgv", "chiếu phim", "vé xem phim"]):
            return {
                "answer": "Cụm rạp CGV Cinemas nằm ở Cánh Đông sảnh chính với các suất chiếu mở từ 09:00 - 23:30.",
                "suggested_poi_id": "poi_cgv",
                "suggested_poi_name": "Rạp Phim CGV Cinemas"
            }

        if any(w in q for w in ["ăn", "sushi", "nhà hàng", "kura"]):
            return {
                "answer": "Nhà hàng Kura Sushi băng chuyền công nghệ cao nằm ở Cánh Bắc sảnh chính.",
                "suggested_poi_id": "poi_kura_sushi",
                "suggested_poi_name": "Nhà Hàng Kura Sushi"
            }

        if any(w in q for w in ["giờ mở cửa", "đóng cửa", "mấy giờ"]):
            return {
                "answer": "Trung tâm thương mại mở cửa đón khách từ 09:00 đến 22:00 hàng ngày (Rạp phim CGV mở tới 23:30).",
                "suggested_poi_id": "poi_reception",
                "suggested_poi_name": "Quầy Lễ Tân & CSKH"
            }

        if any(w in q for w in ["wifi", "mạng", "internet", "pass wifi"]):
            return {
                "answer": "WiFi miễn phí trong toàn bộ sảnh là 'MALL-FREE-WIFI' (không cần mật khẩu).",
                "suggested_poi_id": None,
                "suggested_poi_name": None
            }

        return {
            "answer": "Xin chào quý khách! Tôi là Robot Lễ Tân & Dẫn Đường. Quý khách có thể hỏi tôi về vị trí các cửa hàng, nhà hàng, WC hoặc yêu cầu dẫn đường trực tiếp.",
            "suggested_poi_id": "poi_reception",
            "suggested_poi_name": "Quầy Lễ Tân & CSKH"
        }
