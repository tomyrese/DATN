import time
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict

@dataclass
class PointOfInterest:
    id: str
    name: str
    category: str  # 'food', 'fashion', 'entertainment', 'utility', 'staff'
    floor: str     # 'B1', 'T1', 'T2', 'T3'
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
    Manages Shopping Mall Points of Interest (POIs), Delivery Orders for Staff,
    Customer Escort Navigation, and Mall Information Q&A Assistant.
    """

    def __init__(self):
        self.pois: Dict[str, PointOfInterest] = self._init_default_pois()
        self.orders: Dict[str, DeliveryOrder] = {}
        self.active_order_id: Optional[str] = None
        self.current_escort: Optional[EscortTask] = None
        self.robot_pos = {"x": 50.0, "y": 80.0, "floor": "T1", "heading": 0.0}

    def _init_default_pois(self) -> Dict[str, PointOfInterest]:
        default_list = [
            # Tầng 1 (Sảnh chính & Thời trang)
            PointOfInterest("poi_reception", "Quầy Lễ Tân & CSKH", "utility", "T1", 50.0, 85.0, "Sảnh chính trung tâm, hỗ trợ đổi quà và hướng dẫn."),
            PointOfInterest("poi_highlands", "Highlands Coffee", "food", "T1", 20.0, 75.0, "Cà phê, bánh ngọt, không gian mở view sảnh."),
            PointOfInterest("poi_zara", "Cửa hàng Thời trang ZARA", "fashion", "T1", 80.0, 60.0, "Thời trang nam, nữ và trẻ em cao cấp."),
            PointOfInterest("poi_uniqlo", "UNIQLO LifeWear", "fashion", "T1", 25.0, 40.0, "Quần áo thời trang tiện dụng Nhật Bản."),
            PointOfInterest("poi_wc_t1", "Nhà Vệ Sinh Tầng 1", "utility", "T1", 88.0, 85.0, "Nhà vệ sinh nam/nữ, phòng em bé."),
            PointOfInterest("poi_elevator_t1", "Cụm Thang Máy T1", "utility", "T1", 50.0, 50.0, "Thang máy lên các tầng B1, T2, T3."),

            # Tầng 2 (Ẩm thực & Mua sắm)
            PointOfInterest("poi_phuclong", "Trà Sữa Phúc Long", "food", "T2", 30.0, 70.0, "Trà đào, trà sữa và cà phê truyền thống."),
            PointOfInterest("poi_kura_sushi", "Nhà Hàng Kura Sushi", "food", "T2", 70.0, 35.0, "Sushi băng chuyền công nghệ cao."),
            PointOfInterest("poi_adidas", "Adidas Originals Store", "fashion", "T2", 20.0, 35.0, "Giày thể thao, phụ kiện chính hãng."),
            PointOfInterest("poi_wc_t2", "Nhà Vệ Sinh Tầng 2", "utility", "T2", 88.0, 85.0, "Khu vệ sinh tiện nghi."),

            # Tầng 3 (Giải trí & Rạp chiếu phim)
            PointOfInterest("poi_cgv", "Rạp Chiếu Phim CGV Cinemas", "entertainment", "T3", 50.0, 30.0, "Phòng chiếu IMAX, Starium và quầy bắp nước."),
            PointOfInterest("poi_arcade", "Khu Vui Chơi TimeZone Arcade", "entertainment", "T3", 25.0, 60.0, "Máy game thùng, bắn súng, gắp thú."),
            PointOfInterest("poi_wc_t3", "Nhà Vệ Sinh Tầng 3", "utility", "T3", 88.0, 85.0, "Nhà vệ sinh tầng 3."),

            # Khu vực Nội bộ Nhân viên (Staff Only)
            PointOfInterest("poi_warehouse_b1", "Kho Vận Hàng Hóa Trung Tâm", "staff", "B1", 15.0, 20.0, "Khu vực xuất nhập và phân loại hàng hóa.", is_staff_only=True),
            PointOfInterest("poi_staff_counter", "Quầy Giao Nhận Nội Bộ T1", "staff", "T1", 85.0, 20.0, "Điểm tiếp nhận đơn hàng chuyển phát nhanh nội bộ.", is_staff_only=True),
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
        # Sort newest first
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
            target_floor=poi.floor,
            status="NAVIGATING",
            started_at=time.time(),
            estimated_seconds=40,
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
        
        # Keyword & Intent Matcher
        if any(w in q for w in ["vệ sinh", "toilet", "wc", "nhà tắm", "rửa tay"]):
            return {
                "answer": "Nhà vệ sinh có ở tất cả các tầng (T1, T2, T3) nằm ở góc hành lang phía Đông cạnh thang bộ. Bạn có thể nhấn nút 'Dẫn đường' để robot dẫn bạn đến ngay!",
                "suggested_poi_id": "poi_wc_t1",
                "suggested_poi_name": "Nhà Vệ Sinh Tầng 1"
            }
        
        if any(w in q for w in ["cà phê", "cafe", "coffee", "uống nước", "trà sữa", "highland", "phúc long"]):
            return {
                "answer": "Trung tâm có Highlands Coffee tại sảnh chính Tầng 1 và Trà Sữa Phúc Long tại Tầng 2. Bạn muốn robot dẫn tới địa điểm nào?",
                "suggested_poi_id": "poi_highlands",
                "suggested_poi_name": "Highlands Coffee (Tầng 1)"
            }

        if any(w in q for w in ["quần áo", "thời trang", "áo", "quần", "zara", "uniqlo", "adidas"]):
            return {
                "answer": "Khu mua sắm thời trang tập trung tại Tầng 1 và Tầng 2 với các thương hiệu ZARA, UNIQLO LifeWear và Adidas Originals Store.",
                "suggested_poi_id": "poi_zara",
                "suggested_poi_name": "Cửa hàng ZARA (Tầng 1)"
            }

        if any(w in q for w in ["phim", "cinema", "cgv", "chiếu phim", "vé xem phim"]):
            return {
                "answer": "Rạp chiếu phim CGV Cinemas nằm tại Tầng 3 với 6 phòng chiếu hiện đại. Suất chiếu mở từ 9:00 sáng đến 23:30 đêm.",
                "suggested_poi_id": "poi_cgv",
                "suggested_poi_name": "CGV Cinemas (Tầng 3)"
            }

        if any(w in q for w in ["ăn", "nhà hàng", "sushi", "cơm", "buffet", "ẩm thực"]):
            return {
                "answer": "Khu ẩm thực Tầng 2 có Nhà hàng Kura Sushi băng chuyền công nghệ cao và nhiều gian hàng ẩm thực hấp dẫn khác.",
                "suggested_poi_id": "poi_kura_sushi",
                "suggested_poi_name": "Nhà Hàng Kura Sushi (Tầng 2)"
            }

        if any(w in q for w in ["giờ mở cửa", "đóng cửa", "mấy giờ"]):
            return {
                "answer": "Trung tâm thương mại mở cửa đón khách từ 09:00 đến 22:00 hàng ngày (Rạp phim CGV và siêu thị mở tới 23:30).",
                "suggested_poi_id": "poi_reception",
                "suggested_poi_name": "Quầy Lễ Tân & CSKH"
            }

        if any(w in q for w in ["wifi", "mạng", "internet", "pass wifi"]):
            return {
                "answer": "WiFi miễn phí trong toàn bộ trung tâm là 'MALL-FREE-WIFI' (không cần mật khẩu, chỉ cần xác nhận điều khoản truy cập).",
                "suggested_poi_id": None,
                "suggested_poi_name": None
            }

        # Default fallback
        return {
            "answer": "Xin chào quý khách! Tôi là Robot Lễ Tân & Dẫn Đường. Quý khách có thể hỏi tôi về vị trí các cửa hàng, nhà hàng, nhà vệ sinh, rạp phim hoặc yêu cầu tôi dẫn đường trực tiếp.",
            "suggested_poi_id": "poi_reception",
            "suggested_poi_name": "Quầy Lễ Tân & CSKH"
        }
