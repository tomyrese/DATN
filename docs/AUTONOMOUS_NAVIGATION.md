# ĐIỀU HƯỚNG TỰ HÀNH & ĐỊNH VỊ ODOMETRY (AUTONOMOUS NAVIGATION)

Tài liệu thiết kế thuật toán, mô hình động học, ước lượng quãng đường và cơ chế tuần tra tự động của Robot Tự Hành Trung Tâm Thương Mại.

---

## 1. MÔ HÌNH BẢN ĐỒ TOPOLOGICAL GRAPH

Hệ thống sử dụng biểu diễn bản đồ dạng đồ thị topo 2 chiều (2D Topological Metric Graph) thay vì grid map chiếm dụng bộ nhớ lớn, giúp lập kế hoạch tuyến đường tức thì (< 5ms) trên CPU Raspberry Pi 4.

### 1.1. Cấu trúc dữ liệu trong SQLite
- **`map_nodes`**: Lưu tọa độ metric $(x, y)$ tính theo mét trong không gian mặt sàn TTTM, gắn nhãn định danh (`node_center`, `node_poi_reception`, `node_poi_zara`, v.v.).
- **`map_edges`**: Lưu các đoạn đường nối giữa hai node, kèm chiều dài vật lý tính bằng mét ($d$), cờ hai chiều (`is_bidirectional`) và cờ khóa tạm thời (`is_blocked`).
- **`restricted_zones`**: Lưu vùng hình học chữ nhật cấm robot đi vào (ví dụ: bồn hoa, bậc thang, khu vực ẩm ướt trơn trượt).

### 1.2. Thuật toán tìm đường tối ưu A* (A-Star Shortest Path Planner)
- Lớp: `src/navigation/planner.py` (`AStarPlanner`).
- Hàm heuristic khoảng cách Euclid:
  $$h(n) = \sqrt{(x_n - x_{\text{goal}})^2 + (y_n - y_{\text{goal}})^2}$$
- Đảm bảo tính Admissible và Consistent, tìm ra tuyến đường có tổng quãng đường ngắn nhất.
- Khi một cạnh bị chặn (ví dụ phát hiện vật cản tĩnh hoặc có biển cảnh báo), cạnh đó được đánh dấu `is_blocked = True`, A* lập tức tính toán tuyến tránh thay thế theo cạnh song song mà không cần dừng toàn bộ chương trình.

---

## 2. ƯỚC LƯỢNG QUÃNG ĐƯỜNG ODOMETRY & GIỚI HẠN VẬT LÝ

> [!IMPORTANT]
> **CÔNG BỐ MINH BẠCH VỀ GIỚI HẠN PHẦN CỨNG (DATA HONESTY):**
> 
> Bốn động cơ DC hiện tại của robot **KHÔNG CÓ CẢM BIẾN QUANG QUAY ENCODER TRÊN TRỤC BÁNH XE**.
> Do đó, robot không thể đo lường trực tiếp số vòng quay thực tế của bánh xe. Toàn bộ vị trí $(x, y)$ và góc hướng $\theta$ (heading) được ước lượng thông qua mô hình động học vi sai (Dead-Reckoning Integration) dựa trên:
> 1. Thời gian phát xung điều khiển động cơ ($dt$).
> 2. Vận tốc dài danh định đã hiệu chuẩn ($v_{\text{max}} \approx 0.60\text{ m/s}$).
> 3. Vận tốc góc danh định ($\omega_{\text{max}} \approx 2.50\text{ rad/s}$).
> 4. Chiều dài cơ sở bánh xe ($L = 0.22\text{ m}$).
>
> Hệ thống **TUYỆT ĐỐI KHÔNG TUYÊN BỐ ĐÃ ĐỊNH VỊ CHÍNH XÁC TUYỆT ĐỐI**, mà luôn công khai:
> - Cờ trạng thái: `is_estimated = True`.
> - Chỉ số độ tin cậy: `confidence` giảm dần theo quãng đường di chuyển.
> - Gắn nhãn `[SIMULATED DEAD-RECKONING]` trên giao diện điều khiển.

### 2.1. Phương trình vi sai động học (Runge-Kutta 2nd Order Integration)
- Lớp: `src/navigation/odometry.py` (`DeadReckoningOdometry`).
- Vận tốc tuyến tính của cụm bánh trái và bánh phải:
  $$v_L = u_L \times v_{\text{max}}, \quad v_R = u_R \times v_{\text{max}}$$
- Vận tốc dài và vận tốc góc của trọng tâm robot:
  $$v = \frac{v_R + v_L}{2}, \quad \omega = \frac{v_R - v_L}{L}$$
- Tích phân vị trí với phép xấp xỉ góc hướng trung bình:
  $$\Delta \theta = \omega \times \Delta t, \quad \theta_{\text{mid}} = \theta + \frac{\Delta \theta}{2}$$
  $$\Delta x = v \times \cos(\theta_{\text{mid}}) \times \Delta t, \quad \Delta y = v \times \sin(\theta_{\text{mid}}) \times \Delta t$$
  $$x \leftarrow x + \Delta x, \quad y \leftarrow y + \Delta y, \quad \theta \leftarrow (\theta + \Delta \theta) \pmod{2\pi}$$

### 2.2. Suy giảm độ tin cậy (Confidence Decay) và Neo lại mốc (Landmark Re-anchoring)
- Độ tin cậy ban đầu khi đứng yên tại trạm sạc: $\text{confidence} = 1.0$ ($100\%$).
- Khi robot di chuyển, độ tin cậy suy giảm theo quãng đường tích lũy $\Delta s$ và thời gian $\Delta t$ do trượt bánh và hao hụt điện áp:
  $$\text{Decay} = (\Delta s \times 0.015) + (\Delta t \times 0.002)$$
- Khi robot đến đúng vị trí quầy Lễ Tân, Trạm sạc hoặc điểm POI có thẻ QR/mốc vật lý, hàm `anchor_to_node()` được gọi để hiệu chỉnh lại tọa độ $(x, y)$ và reset $\text{confidence} = 1.0$.

---

## 3. CƠ CHẾ TUẦN TRA TỰ HÀNH KHI NGHỈ 5 PHÚT (IDLE CONCOURSE PATROL)

- Lớp: `src/navigation/patrol_controller.py` (`PatrolController`).

### 3.1. Điều kiện kích hoạt tự động
Robot tự động bắt đầu tuần tra sảnh trung tâm khi thỏa mãn đồng thời:
1. Robot ở trạng thái không có lệnh điều khiển thủ công và không có nhiệm vụ dẫn đường / giao hàng trong thời gian $\ge 300\text{ giây}$ (5 phút).
2. Hệ thống an toàn đang ở trạng thái `CLEAR` (cảm biến siêu âm và camera không bị chặn).
3. Động cơ và pin ở trạng thái hoạt động bình thường, không có lệnh dừng khẩn cấp E-stop.

### 3.2. Chu trình tuần tra
- Tuyến đường tuần tra được cấu hình trong bảng `patrol_routes` và `patrol_route_waypoints`:
  `node_south` (Sảnh đón) $\rightarrow$ `node_center` (Ngã tư) $\rightarrow$ `node_east` $\rightarrow$ `node_north` $\rightarrow$ `node_west`.
- Tại mỗi waypoint, robot có thời gian dừng quan sát và tương tác với khách (Dwell Time: $10 - 20\text{ giây}$).
- Khi hoàn thành chu trình, robot lặp lại tuyến hoặc quay về trạm sạc nghỉ.

### 3.3. Cơ chế ngắt ưu tiên (Priority Task Interruption)
- Khi có bất kỳ yêu cầu dẫn đường mới từ khách tham quan (`POST /api/v1/mall/escort`), đơn giao hàng nội bộ (`POST /api/v1/mall/delivery/orders`), hoặc thao tác điều khiển thủ công từ nhân viên:
  1. Hàm `patrol.stop_patrol(reason="...")` lập tức được kích hoạt.
  2. Robot chuyển đổi trạng thái mượt mà sang nhiệm vụ ưu tiên mà không bị xung đột lệnh.
  3. Sau khi nhiệm vụ kết thúc và robot nghỉ 5 phút tiếp theo, chu trình tuần tra mới được thiết lập lại.
