import time
import math
from src.database.db import Database, get_db
from src.security.password import hash_password
from src.services.logging_service import logger

def seed_database(db: Database = None):
    db = db or get_db()
    now = time.time()

    with db.transaction() as conn:
        # 1. Seed Floors
        row = conn.execute("SELECT COUNT(1) FROM mall_floors").fetchone()
        if row[0] == 0:
            conn.execute("""
                INSERT INTO mall_floors (id, name, level_index, map_image_url, width_m, height_m, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("floor_t1", "Tầng 1 - Sảnh Thương Mại", 1, "/assets/maps/floor1.svg", 100.0, 100.0, now))

        # 2. Seed Stores
        row = conn.execute("SELECT COUNT(1) FROM stores").fetchone()
        if row[0] == 0:
            stores = [
                ("store_uniqlo", "UNIQLO LifeWear", "fashion", "floor_t1", 20.0, 24.0, 16.0, 14.0, "Thời trang phong cách Nhật Bản, trang phục nam, nữ và trẻ em.", "028 3822 1234", "09:30 - 22:00", 1, now),
                ("store_zara", "Thời Trang ZARA", "fashion", "floor_t1", 80.0, 24.0, 16.0, 14.0, "Thương hiệu thời trang cao cấp Tây Ban Nha mới nhất.", "028 3822 5678", "09:30 - 22:00", 1, now),
                ("store_highlands", "Highlands Coffee", "food", "floor_t1", 20.0, 48.0, 14.0, 12.0, "Cà phê pha phin truyền thống, Freeze và bánh ngọt.", "028 3822 9999", "07:00 - 22:30", 1, now),
                ("store_kura_sushi", "Nhà Hàng Kura Sushi", "food", "floor_t1", 50.0, 24.0, 16.0, 14.0, "Sushi băng chuyền công nghệ cao và ẩm thực Nhật.", "028 3822 7777", "10:00 - 22:00", 1, now),
                ("store_cgv", "Rạp Phim CGV Cinemas", "entertainment", "floor_t1", 80.0, 48.0, 18.0, 16.0, "Cụm rạp chiếu phim IMAX & 4DX hiện đại bậc nhất.", "1900 6017", "08:30 - 23:30", 1, now),
                ("store_warehouse", "Kho Giao Nhận Hàng Nội Bộ", "staff", "floor_t1", 90.0, 88.0, 12.0, 12.0, "Khu vực bốc dỡ và xuất nhập hàng hóa nội bộ.", "028 3822 0000", "24/7", 1, now),
            ]
            conn.executemany("""
                INSERT INTO stores (id, name, category, floor_id, x, y, width, height, description, contact_phone, opening_hours, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, stores)

        # 3. Seed Users
        row = conn.execute("SELECT COUNT(1) FROM users").fetchone()
        if row[0] == 0:
            users = [
                ("usr_admin", "admin", hash_password("Admin@123456"), "Quản Trị Viên Hệ Thống", "admin", 1, now, now),
                ("usr_staff_uniqlo", "staff_uniqlo", hash_password("Staff@123456"), "Nhân viên Uniqlo", "staff", 1, now, now),
                ("usr_staff_highlands", "staff_highlands", hash_password("Staff@123456"), "Nhân viên Highlands", "staff", 1, now, now),
                ("usr_staff_zara", "staff_zara", hash_password("Staff@123456"), "Nhân viên ZARA", "staff", 1, now, now),
            ]
            conn.executemany("""
                INSERT INTO users (id, username, password_hash, full_name, role, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, users)

            # Assign staff to stores
            assignments = [
                ("asn_uniqlo", "usr_staff_uniqlo", "store_uniqlo", now),
                ("asn_highlands", "usr_staff_highlands", "store_highlands", now),
                ("asn_zara", "usr_staff_zara", "store_zara", now),
            ]
            conn.executemany("""
                INSERT INTO staff_store_assignments (id, user_id, store_id, created_at)
                VALUES (?, ?, ?, ?)
            """, assignments)

        # 4. Seed Mall POIs
        row = conn.execute("SELECT COUNT(1) FROM mall_pois").fetchone()
        if row[0] == 0:
            pois = [
                ("poi_reception", "Quầy Lễ Tân & CSKH", "utility", "floor_t1", 50.0, 72.0, "Sảnh chính trung tâm, hỗ trợ đổi quà, chỉ đường và thông tin.", 0, None, now),
                ("poi_wc", "Khu Vệ Sinh & Tiện Ích", "utility", "floor_t1", 82.0, 72.0, "Nhà vệ sinh hiện đại Nam, Nữ và phòng chăm sóc em bé.", 0, None, now),
                ("poi_elevator", "Thang Máy & Bãi Đỗ Xe", "utility", "floor_t1", 18.0, 72.0, "Cụm thang máy lồng kính và lối xuống bãi đỗ xe.", 0, None, now),
                ("poi_uniqlo", "UNIQLO LifeWear", "fashion", "floor_t1", 20.0, 24.0, "Thời trang phong cách Nhật Bản, trang phục nam, nữ và trẻ em.", 0, "store_uniqlo", now),
                ("poi_zara", "Thời Trang ZARA", "fashion", "floor_t1", 80.0, 24.0, "Thương hiệu thời trang cao cấp Tây Ban Nha mới nhất.", 0, "store_zara", now),
                ("poi_highlands", "Highlands Coffee", "food", "floor_t1", 20.0, 48.0, "Cà phê pha phin truyền thống, Freeze và bánh ngọt.", 0, "store_highlands", now),
                ("poi_kura_sushi", "Nhà Hàng Kura Sushi", "food", "floor_t1", 50.0, 24.0, "Sushi băng chuyền công nghệ cao và ẩm thực Nhật.", 0, "store_kura_sushi", now),
                ("poi_cgv", "Rạp Phim CGV Cinemas", "entertainment", "floor_t1", 80.0, 48.0, "Cụm rạp chiếu phim IMAX & 4DX hiện đại bậc nhất.", 0, "store_cgv", now),
                ("poi_warehouse", "Kho Giao Nhận Hàng Nội Bộ", "staff", "floor_t1", 90.0, 88.0, "Khu vực bốc dỡ và xuất nhập hàng hóa nội bộ.", 1, "store_warehouse", now),
            ]
            conn.executemany("""
                INSERT INTO mall_pois (id, name, category, floor_id, x, y, description, is_staff_only, store_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, pois)

        # 5. Seed Map Nodes & Edges (Navigation Graph)
        row = conn.execute("SELECT COUNT(1) FROM map_nodes").fetchone()
        if row[0] == 0:
            nodes = [
                # Central hub & corridors
                ("node_center", "floor_t1", "Ngã tư Trung tâm", 50.0, 50.0, "intersection", now),
                ("node_north", "floor_t1", "Hành lang Bắc", 50.0, 32.0, "corridor", now),
                ("node_south", "floor_t1", "Hành lang Nam (Sảnh đón)", 50.0, 68.0, "entrance", now),
                ("node_west", "floor_t1", "Hành lang Tây", 30.0, 50.0, "corridor", now),
                ("node_east", "floor_t1", "Hành lang Đông", 70.0, 50.0, "corridor", now),

                # Nodes near POIs
                ("node_poi_uniqlo", "floor_t1", "Cửa hàng Uniqlo", 25.0, 28.0, "poi", now),
                ("node_poi_zara", "floor_t1", "Cửa hàng ZARA", 75.0, 28.0, "poi", now),
                ("node_poi_kura", "floor_t1", "Nhà hàng Kura Sushi", 50.0, 28.0, "poi", now),
                ("node_poi_highlands", "floor_t1", "Highlands Coffee", 25.0, 48.0, "poi", now),
                ("node_poi_cgv", "floor_t1", "Rạp CGV Cinemas", 75.0, 48.0, "poi", now),
                ("node_poi_reception", "floor_t1", "Quầy Lễ Tân", 50.0, 70.0, "poi", now),
                ("node_poi_wc", "floor_t1", "Khu WC", 80.0, 70.0, "poi", now),
                ("node_poi_elevator", "floor_t1", "Thang Máy", 20.0, 70.0, "poi", now),
                ("node_poi_warehouse", "floor_t1", "Kho Nội Bộ", 85.0, 85.0, "poi", now),
            ]
            conn.executemany("""
                INSERT INTO map_nodes (id, floor_id, name, x, y, node_type, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, nodes)

            # Node map dict for edge distance calculation
            node_map = {n[0]: (n[3], n[4]) for n in nodes}

            def calc_dist(n1, n2):
                x1, y1 = node_map[n1]
                x2, y2 = node_map[n2]
                return round(math.sqrt((x1 - x2)**2 + (y1 - y2)**2), 2)

            edges_spec = [
                # Central cross
                ("node_center", "node_north"),
                ("node_center", "node_south"),
                ("node_center", "node_west"),
                ("node_center", "node_east"),

                # North connections
                ("node_north", "node_poi_kura"),
                ("node_north", "node_poi_uniqlo"),
                ("node_north", "node_poi_zara"),

                # West connections
                ("node_west", "node_poi_highlands"),
                ("node_west", "node_poi_uniqlo"),
                ("node_west", "node_poi_elevator"),

                # East connections
                ("node_east", "node_poi_cgv"),
                ("node_east", "node_poi_zara"),
                ("node_east", "node_poi_wc"),
                ("node_east", "node_poi_warehouse"),

                # South connections
                ("node_south", "node_poi_reception"),
                ("node_south", "node_poi_elevator"),
                ("node_south", "node_poi_wc"),
            ]

            edge_rows = []
            for i, (na, nb) in enumerate(edges_spec):
                dist = calc_dist(na, nb)
                edge_rows.append((f"edge_{i+1}", "floor_t1", na, nb, dist, 1, 0, now))

            conn.executemany("""
                INSERT INTO map_edges (id, floor_id, node_a, node_b, distance_m, is_bidirectional, is_blocked, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, edge_rows)

        # 6. Seed Restricted Zones
        row = conn.execute("SELECT COUNT(1) FROM restricted_zones").fetchone()
        if row[0] == 0:
            conn.execute("""
                INSERT INTO restricted_zones (id, floor_id, name, x_min, y_min, x_max, y_max, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ("zone_construction", "floor_t1", "Khu Vực Thi Công Kỹ Thuật", 85.0, 5.0, 95.0, 15.0, 1, now))

        # 7. Seed Patrol Routes
        row = conn.execute("SELECT COUNT(1) FROM patrol_routes").fetchone()
        if row[0] == 0:
            conn.execute("""
                INSERT INTO patrol_routes (id, name, floor_id, description, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("patrol_main_concourse", "Tuyến Tuần Tra Sảnh Chính T1", "floor_t1", "Tuần tra định kỳ giữa sảnh trung tâm, khu ẩm thực và giải trí", 1, now))

            waypoints = [
                ("wp_1", "patrol_main_concourse", "node_center", 1, 10),
                ("wp_2", "patrol_main_concourse", "node_west", 2, 8),
                ("wp_3", "patrol_main_concourse", "node_north", 3, 8),
                ("wp_4", "patrol_main_concourse", "node_east", 4, 8),
                ("wp_5", "patrol_main_concourse", "node_south", 5, 10),
            ]
            conn.executemany("""
                INSERT INTO patrol_route_waypoints (id, route_id, node_id, sequence_order, dwell_seconds)
                VALUES (?, ?, ?, ?, ?)
            """, waypoints)

        # 8. Seed Promotions
        row = conn.execute("SELECT COUNT(1) FROM promotions").fetchone()
        if row[0] == 0:
            promos = [
                ("promo_uniqlo_summer", "Ưu Đãi LifeWear Mùa Hè - Giảm 20% AIRism", "store_uniqlo", "Giảm 20% toàn bộ áo thun chống nắng và trang phục làm mát AIRism", 20, "AIRISM20", "/assets/promos/uniqlo.jpg", now - 86400, now + 86400*14, 1, "usr_staff_uniqlo", now, now),
                ("promo_highlands_combo", "Mua 1 Tặng 1 Phin Sữa Tươi Cà Phê Moka", "store_highlands", "Áp dụng khung giờ vàng 08:00 - 11:00 sáng mỗi ngày", 50, "HLFREEZE", "/assets/promos/highlands.jpg", now - 86400, now + 86400*30, 1, "usr_staff_highlands", now, now),
                ("promo_cgv_popcorn", "Combo Bắp Nước Khủng Ngày Thứ 4 Vui Vẻ", "store_cgv", "Giảm 30% khi mua vé xem phim kèm bắp phô mai và nước ngọt", 30, "CGVWED", "/assets/promos/cgv.jpg", now - 86400, now + 86400*60, 1, "usr_admin", now, now),
            ]
            conn.executemany("""
                INSERT INTO promotions (id, title, store_id, description, discount_percent, promo_code, banner_url, start_time, end_time, is_active, created_by, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, promos)

        # 9. Seed Mall FAQ
        row = conn.execute("SELECT COUNT(1) FROM mall_faq").fetchone()
        if row[0] == 0:
            faqs = [
                ("faq_wifi", "tiện ích", "Mật khẩu Wi-Fi của trung tâm thương mại là gì?", "Quý khách kết nối mạng Wi-Fi 'MALL_GUEST_FREE' hoàn toàn miễn phí không cần mật khẩu. Vui lòng nhấn 'Kết Nối' trên trang chào mừng.", None, 1, now),
                ("faq_hours", "thông tin", "Giờ mở cửa và đóng cửa của trung tâm thương mại là khi nào?", "Trung tâm thương mại mở cửa đón khách từ 09:00 sáng đến 22:00 tối tất cả các ngày trong tuần (kể cả Thứ Bảy, Chủ Nhật và ngày lễ). Cụm rạp CGV mở cửa đến 23:30.", None, 1, now),
                ("faq_parking", "tiện ích", "Bãi gửi xe ô tô và xe máy nằm ở đâu?", "Bãi đỗ xe nằm ở tầng hầm B1 (dành cho xe máy) và B2/B3 (dành cho ô tô). Quý khách có thể đi thang máy lồng kính phía Tây để xuống tầng hầm.", "poi_elevator", 1, now),
                ("faq_rewards", "dịch vụ", "Làm sao để đổi quà và tích điểm thẻ thành viên?", "Quý khách vui lòng mang hóa đơn mua sắm đến Quầy Lễ Tân & Chăm Sóc Khách Hàng tại sảnh chính Tầng 1 để được hướng dẫn tích điểm đổi quà nhé!", "poi_reception", 1, now),
                ("faq_wc", "tiện ích", "Nhà vệ sinh gần nhất ở đâu?", "Nhà vệ sinh sạch sẽ, hiện đại nằm ở phía Đông Tầng 1 (kế bên cụm rạp CGV) và có phòng chăm sóc em bé riêng.", "poi_wc", 1, now),
            ]
            conn.executemany("""
                INSERT INTO mall_faq (id, category, question, answer, suggested_poi_id, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, faqs)

        # 10. Seed Robot Entity
        row = conn.execute("SELECT COUNT(1) FROM robots").fetchone()
        if row[0] == 0:
            conn.execute("""
                INSERT INTO robots (id, name, status, battery_level, current_floor_id, x, y, heading, confidence, is_simulated, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ("RBT01", "Pi Robot Trung Tâm Thương Mại", "IDLE", 98.0, "floor_t1", 50.0, 70.0, 0.0, 1.0, 1, now))

        # 11. Seed System Settings
        row = conn.execute("SELECT COUNT(1) FROM system_settings").fetchone()
        if row[0] == 0:
            settings = [
                ("openrouter_model", "google/gemini-2.0-flash-exp:free", "Mô hình ngôn ngữ mặc định OpenRouter", now),
                ("patrol_idle_timeout_sec", "300", "Thời gian rảnh rỗi trước khi tự động tuần tra (giây)", now),
                ("default_speed", "0.35", "Tốc độ lái xe tiêu chuẩn", now),
                ("max_speed", "0.50", "Giới hạn tốc độ tối đa cho phép", now),
                ("emergency_stop_latched", "false", "Trạng thái chốt dừng khẩn cấp", now),
            ]
            conn.executemany("""
                INSERT INTO system_settings (key, value, description, updated_at)
                VALUES (?, ?, ?, ?)
            """, settings)

    logger.info("Database seeded successfully with initial entities!")
