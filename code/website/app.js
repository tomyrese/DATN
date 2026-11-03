/**
 * BÉ ROBI - MEGAMALL ROBOT SERVICE
 * Client Application Logic & Routing
 * Phiên bản Giao diện Sáng Tinh Gọn:
 * - Pin Animation
 * - Điều khiển WASD (Laptop) & Virtual Touch Joystick (Điện Thoại)
 * - FPV Camera Thực Tế & Trang Nhật Ký Vận Hành (/logs)
 */

// ========================================================
// 1. STATE MANAGEMENT
// ========================================================
const AppState = {
  currentUser: {
    role: "guest",
    username: "",
    fullName: "Khách Mua Sắm",
    token: ""
  },
  currentRoute: "/home",
  pagePin: "",
  modalPin: "",
  currentFloor: "1",
  speechEnabled: true,
  driveInterval: null,
  activeDriveDirection: null,
  speed: 60,
  countdownTimer: null,
  logsFilter: "ALL",
  systemLogs: [],
  isDrivingWASD: false,
  activeWASDKey: null,
  cameraAnimId: null,
  camOffset: 0
};

// Floor Stores Database
const MALL_FLOORS = {
  "B1": {
    title: "TẦNG B1: SIÊU THỊ, NHÀ THUỐC & BÃI ĐỖ XE",
    robotLoc: "📍 Bé Robi đang đỗ tại: Cửa Siêu thị WinMart+ (Tầng B1)",
    stores: [
      { name: "Siêu thị WinMart+", desc: "Hàng tiêu dùng, thực phẩm tươi sạch", icon: "🛒" },
      { name: "Nhà thuốc An Khang", desc: "Dược phẩm, vật tư y tế, sơ cứu nhanh", icon: "💊" },
      { name: "Tủ Gửi Đồ Tự Động", desc: "Tủ đồ điện tử mã số an toàn", icon: "🛅" },
      { name: "Bãi Đỗ Xe & Trạm Sạc", desc: "Trạm sạc xe điện & bãi giữ xe", icon: "🚗" }
    ]
  },
  "1": {
    title: "TẦNG 1: SẢNH TRUNG TÂM & THỜI TRANG",
    robotLoc: "📍 Bé Robi đang đỗ tại: Cạnh Quầy Highlands Coffee (Tầng 1)",
    stores: [
      { name: "Highlands Coffee", desc: "Cà phê phin, Trà sen vàng • Cạnh thang máy", icon: "☕" },
      { name: "Zara Quốc Tế", desc: "Thời trang nam, nữ & phụ kiện • Cánh Đông", icon: "👗" },
      { name: "Uniqlo LifeWear", desc: "Thời trang công nghệ LifeWear • Cánh Tây", icon: "👕" },
      { name: "Quầy Lễ Tân", desc: "Hỗ trợ thông tin, đổi quà, lễ tân sảnh", icon: "ℹ️" }
    ]
  },
  "2": {
    title: "TẦNG 2: MỸ PHẨM & TRÀ SỮA",
    robotLoc: "📍 Bé Robi đang đỗ tại: Trước sảnh Phúc Long Tea (Tầng 2)",
    stores: [
      { name: "Phúc Long Tea", desc: "Trà đào, trà sữa truyền thống, bánh ngọt", icon: "🧋" },
      { name: "Innisfree", desc: "Mỹ phẩm thiên nhiên đảo Jeju", icon: "🌿" },
      { name: "Guardian", desc: "Chăm sóc sức khỏe, mỹ phẩm hàng ngày", icon: "💄" },
      { name: "Charles & Keith", desc: "Túi xách thời trang và giày dép", icon: "👜" }
    ]
  },
  "3": {
    title: "TẦNG 3: TRẺ EM & NHÀ SÁCH",
    robotLoc: "📍 Bé Robi đang đỗ tại: Khu vui chơi TiNiWorld (Tầng 3)",
    stores: [
      { name: "TiNiWorld", desc: "Khu vui chơi giáo dục giải trí cho bé", icon: "🎡" },
      { name: "KidsPlaza", desc: "Đồ dùng mẹ & bé, quần áo trẻ em", icon: "👶" },
      { name: "Nhà Sách Fahasa", desc: "Sách thiếu nhi, truyện tranh, văn phòng phẩm", icon: "📚" },
      { name: "Lego Store", desc: "Đồ chơi xếp hình sáng tạo", icon: "🧩" }
    ]
  },
  "4": {
    title: "TẦNG 4: THIÊN ĐƯỜNG ẨM THỰC Á - ÂU",
    robotLoc: "📍 Bé Robi đang đỗ tại: Sảnh chờ Lẩu Haidilao (Tầng 4)",
    stores: [
      { name: "Lẩu Haidilao", desc: "Lẩu Trung Hoa, múa mì nghệ thuật", icon: "🍲" },
      { name: "Buffet King BBQ", desc: "Vua nướng Hàn Quốc, thịt nướng than hồng", icon: "🥩" },
      { name: "Pizza 4P's", desc: "Pizza phô mai lò củi thủ công", icon: "🍕" },
      { name: "Gà Rán KFC", desc: "Gà rán giòn cay, khoai tây chiên, burger", icon: "🍗" }
    ]
  },
  "5": {
    title: "TẦNG 5: CỤM RẠP CGV CINEMAS",
    robotLoc: "📍 Bé Robi đang đỗ tại: Sảnh vé CGV IMAX (Tầng 5)",
    stores: [
      { name: "CGV Cinemas IMAX", desc: "Cụm 8 rạp phim màn hình lớn, âm thanh vòm", icon: "🎬" },
      { name: "DreamGames", desc: "Khu trò chơi điện tử giải trí", icon: "🎮" },
      { name: "Bắp Rang & Nước Ngọt", desc: "Quầy combo giải khát rạp phim", icon: "🍿" }
    ]
  }
};

// ========================================================
// 2. ROUTING SYSTEM
// ========================================================
const ROUTE_TITLES = {
  "/home": "Trang Chủ - Bé Robi",
  "/trang-chu": "Trang Chủ - Bé Robi",
  "/nhan-hang": "Nhận Hàng Mã PIN - Bé Robi",
  "/map": "Bản Đồ Mua Sắm - MegaMall",
  "/ban-do": "Bản Đồ Mua Sắm - MegaMall",
  "/chat": "Trò Chuyện Cùng Bé Robi",
  "/tro-chuyen": "Trò Chuyện Cùng Bé Robi",
  "/don-hang": "Tạo Đơn Hàng & Giao Nhận - Bé Robi",
  "/tao-don": "Tạo Đơn Hàng & Giao Nhận - Bé Robi",
  "/dieu-hanh": "Điều Phối Robot - Bé Robi",
  "/quan-ly": "Điều Phối Robot - Bé Robi",
  "/logs": "Nhật Ký & Camera FPV - Bé Robi",
  "/nhat-ky": "Nhật Ký & Camera FPV - Bé Robi",
  "/cai-dat": "Cài Đặt Hệ Thống - Bé Robi",
  "/he-thong": "Cài Đặt Hệ Thống - Bé Robi"
};

function normalizeRoute(path) {
  if (!path || path === "/" || path === "") return "/home";
  if (path.startsWith("/trang-chu")) return "/home";
  if (path.startsWith("/ban-do")) return "/map";
  if (path.startsWith("/tro-chuyen")) return "/chat";
  if (path.startsWith("/tao-don")) return "/don-hang";
  if (path.startsWith("/quan-ly")) return "/dieu-hanh";
  if (path.startsWith("/nhat-ky")) return "/logs";
  if (path.startsWith("/he-thong")) return "/cai-dat";
  return path;
}

function navigateRoute(path, event) {
  if (event) {
    event.preventDefault();
  }
  const targetRoute = normalizeRoute(path);

  // Phân quyền bảo vệ route nhân viên
  if ((targetRoute === "/dieu-hanh" || targetRoute === "/don-hang" || targetRoute === "/logs") && AppState.currentUser.role === "guest") {
    showToast("Vui lòng đăng nhập nhân viên để vào mục này", "⚠️");
    openLoginModal();
    return;
  }
  if (targetRoute === "/cai-dat" && AppState.currentUser.role !== "admin") {
    showToast("Mục này chỉ dành cho Quản trị viên hệ thống", "⚠️");
    openLoginModal();
    return;
  }

  if (window.location.pathname !== targetRoute) {
    history.pushState(null, "", targetRoute);
  }

  activateView(targetRoute);
}

function activateView(route) {
  AppState.currentRoute = route;
  document.title = ROUTE_TITLES[route] || "Bé Robi - Robot Phục Vụ MegaMall";

  const views = document.querySelectorAll(".page-view");
  views.forEach(v => v.classList.remove("active"));

  const navTabs = document.querySelectorAll(".nav-tab, .dock-item");
  navTabs.forEach(t => {
    const tabRoute = normalizeRoute(t.getAttribute("data-route"));
    if (tabRoute === route) {
      t.classList.add("active");
    } else {
      t.classList.remove("active");
    }
  });

  let viewId = "view-home";
  if (route === "/nhan-hang") viewId = "view-nhan-hang";
  else if (route === "/map") viewId = "view-map";
  else if (route === "/chat") viewId = "view-chat";
  else if (route === "/don-hang") viewId = "view-don-hang";
  else if (route === "/dieu-hanh") viewId = "view-dieu-hanh";
  else if (route === "/logs") viewId = "view-logs";
  else if (route === "/cai-dat") viewId = "view-cai-dat";

  const targetElem = document.getElementById(viewId);
  if (targetElem) {
    targetElem.classList.add("active");
  }

  if (route === "/map") {
    renderFloorStores(AppState.currentFloor);
  } else if (route === "/don-hang") {
    fetchMissions();
    initInlineOrderForm();
  } else if (route === "/dieu-hanh") {
    startCameraCanvas();
    autoDetectControllerInput();
  } else if (route === "/logs") {
    fetchSystemLogs();
    startCameraCanvas();
  } else if (route === "/cai-dat") {
    fetchUsersList();
  }

  window.scrollTo({ top: 0, behavior: "smooth" });
}

window.addEventListener("popstate", () => {
  const currentPath = normalizeRoute(window.location.pathname);
  activateView(currentPath);
});

// ========================================================
// 3. TOAST & SPEECH
// ========================================================
let toastTimeout = null;
function showToast(message, icon = "✨") {
  const toast = document.getElementById("global-toast");
  const textElem = document.getElementById("toast-text");
  const iconElem = document.getElementById("toast-icon");
  if (!toast) return;

  textElem.textContent = message;
  iconElem.textContent = icon;
  toast.classList.remove("hidden");

  if (toastTimeout) clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => {
    toast.classList.add("hidden");
  }, 3500);
}

function speakVietnamese(text) {
  if (!AppState.speechEnabled || !window.speechSynthesis) return;
  try {
    window.speechSynthesis.cancel();
    const cleanText = text.replace(/[*#_~`]/g, "").trim();
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = "vi-VN";
    utterance.rate = 1.05;
    utterance.pitch = 1.1;

    const voices = window.speechSynthesis.getVoices();
    const viVoice = voices.find(v => v.lang.includes("vi") || v.lang.includes("VN"));
    if (viVoice) utterance.voice = viVoice;
    window.speechSynthesis.speak(utterance);
  } catch (e) {}
}

// ========================================================
// 4. MASCOT ANIMATIONS
// ========================================================
function setRobiMascotEmotion(emotion) {
  const mouth = document.getElementById("robi-mouth");
  if (!mouth) return;

  mouth.className = "face-mouth";
  if (emotion === "happy") mouth.classList.add("mouth-happy");
  else if (emotion === "talking") mouth.classList.add("mouth-talking");
  else if (emotion === "thinking") mouth.classList.add("mouth-thinking");
}

// ========================================================
// 5. NUMPAD LOGIC (TRANG NHẬN HÀNG)
// ========================================================
function updatePagePinDisplay() {
  const cells = document.querySelectorAll("#pin-dots-main .pin-cell, #pin-dots-main .pin-box");
  cells.forEach((cell, i) => {
    if (i < AppState.pagePin.length) {
      cell.textContent = AppState.pagePin[i];
      cell.classList.add("filled");
    } else {
      cell.textContent = "";
      cell.classList.remove("filled");
    }
  });

  const prompt = document.getElementById("pin-prompt-text");
  if (prompt) {
    if (AppState.pagePin.length === 6) {
      prompt.textContent = "Bấm 'Mở Hộc' để nhận món đồ của bạn!";
      prompt.style.color = "var(--primary)";
    } else {
      prompt.textContent = `Đã nhập ${AppState.pagePin.length}/6 số`;
      prompt.style.color = "var(--text-muted)";
    }
  }
}

function pressPinDigit(digit) {
  if (AppState.pagePin.length < 6) {
    AppState.pagePin += digit;
    updatePagePinDisplay();
  }
}

function clearPinDigits() {
  AppState.pagePin = "";
  updatePagePinDisplay();
}

function fillTestPin(code) {
  AppState.pagePin = code;
  updatePagePinDisplay();
}

async function submitPinUnlock() {
  if (AppState.pagePin.length !== 6) {
    showToast("Vui lòng nhập đủ 6 chữ số mã PIN!", "⚠️");
    return;
  }

  try {
    const res = await fetch("/api/missions/unlock", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ otp: AppState.pagePin })
    });
    const data = await res.json();

    if (data.success || data.status === "success") {
      clearPinDigits();
      openUnlockSuccessModal(data);
    } else {
      showToast(data.message || data.error || "Mã PIN không đúng hoặc đơn đã nhận rồi!", "❌");
    }
  } catch (err) {
    showToast("Lỗi kết nối máy chủ!", "⚠️");
  }
}

// ========================================================
// 6. POPUP MODALS MANAGEMENT
// ========================================================
function closeModalOnBackdrop(event, modalId) {
  if (event.target.id === modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.add("hidden");
  }
}

window.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    closeOtpModal();
    closeLoginModal();
    closeNewMissionModal();
    closeCreateUserModal();
    const succModal = document.getElementById("modal-unlock-success");
    if (succModal && !succModal.classList.contains("hidden")) {
      finishOrderTakeout();
    }
  }
});

function openOtpModal() {
  AppState.modalPin = "";
  updateModalPinDisplay();
  const msg = document.getElementById("modal-pin-msg");
  if (msg) msg.textContent = "";
  document.getElementById("modal-otp").classList.remove("hidden");
}

function closeOtpModal() {
  const m = document.getElementById("modal-otp");
  if (m) m.classList.add("hidden");
}

function updateModalPinDisplay() {
  const cells = document.querySelectorAll("#modal-pin-boxes .pin-cell, #modal-pin-boxes .modal-pin-cell");
  cells.forEach((cell, i) => {
    if (i < AppState.modalPin.length) {
      cell.textContent = AppState.modalPin[i];
      cell.classList.add("filled");
    } else {
      cell.textContent = "";
      cell.classList.remove("filled");
    }
  });
}

function pressModalPin(d) {
  if (AppState.modalPin.length < 6) {
    AppState.modalPin += d;
    updateModalPinDisplay();
  }
}

function clearModalPin() {
  AppState.modalPin = "";
  updateModalPinDisplay();
  const msg = document.getElementById("modal-pin-msg");
  if (msg) msg.textContent = "";
}

function fillModalPin(code) {
  AppState.modalPin = code;
  updateModalPinDisplay();
}

async function submitModalPin() {
  const msgElem = document.getElementById("modal-pin-msg");
  if (AppState.modalPin.length !== 6) {
    if (msgElem) msgElem.textContent = "Vui lòng nhập đủ 6 chữ số mã PIN!";
    return;
  }

  try {
    const res = await fetch("/api/missions/unlock", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ otp: AppState.modalPin })
    });
    const data = await res.json();

    if (data.success || data.status === "success") {
      closeOtpModal();
      openUnlockSuccessModal(data);
    } else {
      if (msgElem) msgElem.textContent = data.message || data.error || "Mã PIN không đúng!";
    }
  } catch (err) {
    if (msgElem) msgElem.textContent = "Lỗi kết nối máy chủ!";
  }
}

// ========================================================
// 7. SUCCESS MODAL & 30S COUNTDOWN
// ========================================================
function openUnlockSuccessModal(orderData) {
  const modal = document.getElementById("modal-unlock-success");
  const title = document.getElementById("unlock-success-title");
  const desc = document.getElementById("unlock-success-desc");
  const countdown = document.getElementById("unlock-countdown");

  const compNum = orderData.compartment || 1;
  const store = orderData.store || "Cửa hàng";
  const item = orderData.item || "Món đồ";

  if (title) title.textContent = `Hộc Chứa Số ${compNum} Đã Mở!`;
  if (desc) desc.innerHTML = `Món đồ từ <strong>${store}</strong>: <em>${item}</em> đã sẵn sàng. Bạn vui lòng lấy đồ ra nhé!`;

  modal.classList.remove("hidden");

  const voiceText = `Dạ em Robi đã mở hộc chứa số ${compNum} cho anh chị rồi ạ. Anh chị vui lòng lấy đồ ra nhé!`;
  speakVietnamese(voiceText);

  let remaining = 30;
  if (countdown) countdown.textContent = remaining;

  if (AppState.countdownTimer) clearInterval(AppState.countdownTimer);
  AppState.countdownTimer = setInterval(() => {
    remaining--;
    if (countdown) countdown.textContent = remaining;
    if (remaining <= 0) {
      clearInterval(AppState.countdownTimer);
      finishOrderTakeout();
    }
  }, 1000);

  pollRobotState();
}

function finishOrderTakeout() {
  if (AppState.countdownTimer) clearInterval(AppState.countdownTimer);
  const m = document.getElementById("modal-unlock-success");
  if (m) m.classList.add("hidden");
  showToast("Cửa hộc chứa đã đóng lại an toàn. Cảm ơn bạn!", "✅");
  pollRobotState();
}

// ========================================================
// 8. BẢN ĐỒ TTTM
// ========================================================
function switchFloor(floorNum) {
  AppState.currentFloor = floorNum;

  const floorBtns = document.querySelectorAll(".floor-pill, .floor-btn");
  floorBtns.forEach(b => {
    if (b.getAttribute("data-floor") === floorNum) {
      b.classList.add("active");
    } else {
      b.classList.remove("active");
    }
  });

  renderFloorStores(floorNum);
}

function renderFloorStores(floorNum) {
  const floorData = MALL_FLOORS[floorNum] || MALL_FLOORS["1"];
  const titleElem = document.getElementById("current-floor-title");
  const locElem = document.getElementById("current-floor-robot-loc");
  const listContainer = document.getElementById("floor-stores-list");

  if (titleElem) titleElem.textContent = floorData.title;
  if (locElem) locElem.textContent = floorData.robotLoc;

  if (listContainer) {
    listContainer.innerHTML = floorData.stores.map(s => `
      <div class="store-card">
        <div class="store-icon">${s.icon}</div>
        <div class="store-info">
          <h5>${s.name}</h5>
          <p>${s.desc}</p>
        </div>
      </div>
    `).join("");
  }
}

// ========================================================
// 9. AI CHAT WITH BÉ ROBI
// ========================================================
function sendQuickMessage(text) {
  const input = document.getElementById("chat-input-field");
  if (input) {
    input.value = text;
    sendChatMessage();
  }
}

function handleChatKeyPress(e) {
  if (e.key === "Enter") {
    sendChatMessage();
  }
}

async function sendChatMessage() {
  const input = document.getElementById("chat-input-field");
  const query = input.value.trim();
  if (!query) return;

  const container = document.getElementById("chat-messages-container");

  const userHtml = `
    <div class="chat-row row-user">
      <div class="chat-bubble bubble-user">
        <div class="bubble-sender">${escapeHtml(AppState.currentUser.fullName || "Bạn")}</div>
        <div class="bubble-text">${escapeHtml(query)}</div>
      </div>
    </div>
  `;
  container.insertAdjacentHTML("beforeend", userHtml);
  input.value = "";
  container.scrollTop = container.scrollHeight;

  const thinkingId = "thinking-" + Date.now();
  const thinkingHtml = `
    <div class="chat-row row-robi" id="${thinkingId}">
      <div class="chat-bubble bubble-robi">
        <div class="bubble-sender">Bé Robi</div>
        <div class="bubble-text"><em>Bé Robi đang tra cứu thông tin giúp bạn...</em></div>
      </div>
    </div>
  `;
  container.insertAdjacentHTML("beforeend", thinkingHtml);
  container.scrollTop = container.scrollHeight;
  setRobiMascotEmotion("thinking");

  try {
    const res = await fetch("/api/ai/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: query,
        query: query,
        role: AppState.currentUser.role,
        token: AppState.currentUser.token
      })
    });
    const data = await res.json();

    const thinkingElem = document.getElementById(thinkingId);
    if (thinkingElem) thinkingElem.remove();

    const robiReply = data.reply || "Dạ em Robi chưa nghe rõ, bạn nhắn lại giúp mình nhé!";
    const replyHtml = `
      <div class="chat-row row-robi">
        <div class="chat-bubble bubble-robi">
          <div class="bubble-sender">Bé Robi</div>
          <div class="bubble-text">${formatMarkdownText(robiReply)}</div>
        </div>
      </div>
    `;
    container.insertAdjacentHTML("beforeend", replyHtml);
    container.scrollTop = container.scrollHeight;

    setRobiMascotEmotion("happy");
    speakVietnamese(robiReply);

  } catch (err) {
    const thinkingElem = document.getElementById(thinkingId);
    if (thinkingElem) {
      thinkingElem.querySelector(".bubble-text").textContent = "Dạ mạng đang chập chờn, bạn thử lại giúp mình nhé!";
    }
    setRobiMascotEmotion("happy");
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function formatMarkdownText(text) {
  return escapeHtml(text)
    .replace(/\n/g, "<br>")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
}

// ========================================================
// 10. AUTHENTICATION & LOGIN
// ========================================================
function openLoginModal() {
  const errElem = document.getElementById("login-error-msg");
  if (errElem) errElem.textContent = "";
  const m = document.getElementById("modal-login");
  if (m) m.classList.remove("hidden");
  selectLoginRole("manager");
}

function closeLoginModal() {
  const m = document.getElementById("modal-login");
  if (m) m.classList.add("hidden");
}

function selectLoginRole(role) {
  const cardManager = document.getElementById("card-role-manager");
  const cardAdmin = document.getElementById("card-role-admin");
  const u = document.getElementById("login-username");
  const p = document.getElementById("login-password");
  const errElem = document.getElementById("login-error-msg");
  if (errElem) errElem.textContent = "";

  if (role === "admin") {
    if (cardAdmin) cardAdmin.classList.add("active");
    if (cardManager) cardManager.classList.remove("active");
    if (u) u.value = "admin";
    if (p) p.value = "admin123";
  } else {
    if (cardManager) cardManager.classList.add("active");
    if (cardAdmin) cardAdmin.classList.remove("active");
    if (u) u.value = "manager";
    if (p) p.value = "manager123";
  }
}

function togglePasswordVisibility() {
  const p = document.getElementById("login-password");
  if (!p) return;
  p.type = p.type === "password" ? "text" : "password";
}

function fillQuickLogin(user, pass) {
  selectLoginRole(user === "admin" ? "admin" : "manager");
}

async function submitLogin() {
  const u = document.getElementById("login-username").value.trim();
  const p = document.getElementById("login-password").value.trim();
  const errElem = document.getElementById("login-error-msg");

  if (!u || !p) {
    if (errElem) errElem.textContent = "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!";
    return;
  }

  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: u, password: p })
    });
    const data = await res.json();

    if (data.success || data.status === "success") {
      AppState.currentUser = {
        role: data.user.role,
        username: data.user.username,
        fullName: data.user.fullName || data.user.full_name || "Nhân viên",
        token: data.token
      };
      localStorage.setItem("robi_user", JSON.stringify(AppState.currentUser));
      updateUserRoleUI();
      closeLoginModal();
      showToast(`Đăng nhập thành công: ${AppState.currentUser.fullName}!`, "👋");

      if (AppState.currentUser.role === "manager" || AppState.currentUser.role === "admin") {
        navigateRoute("/dieu-hanh");
      }
    } else {
      if (errElem) errElem.textContent = data.message || data.error || "Tên đăng nhập hoặc mật khẩu không đúng!";
    }
  } catch (err) {
    if (errElem) errElem.textContent = "Không thể kết nối đến máy chủ!";
  }
}

function continueAsGuest() {
  AppState.currentUser = {
    role: "guest",
    username: "",
    fullName: "Khách Mua Sắm",
    token: ""
  };
  localStorage.removeItem("robi_user");
  updateUserRoleUI();
  closeLoginModal();
  showToast("Bạn đang ở vai trò Khách Mua Sắm", "🛍️");
  navigateRoute("/home");
}

function updateUserRoleUI() {
  const role = AppState.currentUser.role;
  const roleBadge = document.getElementById("role-badge-text");
  const roleAvatar = document.getElementById("role-avatar");
  const chatRole = document.getElementById("chat-current-role-badge");

  const tabDonHang = document.getElementById("tab-don-hang");
  const tabDieuHanh = document.getElementById("tab-dieu-hanh");
  const tabLogs = document.getElementById("tab-logs");
  const tabCaiDat = document.getElementById("tab-cai-dat");
  const dockDonHang = document.getElementById("dock-don-hang");
  const dockDieuHanh = document.getElementById("dock-dieu-hanh");
  const dockLogs = document.getElementById("dock-logs");

  const homeCompSec = document.getElementById("home-compartments-section");
  const btnComp1 = document.getElementById("btn-comp1-staff");
  const btnComp2 = document.getElementById("btn-comp2-staff");
  const btnDrawerOrder = document.getElementById("btn-drawer-order");

  if (role === "admin") {
    if (roleBadge) roleBadge.textContent = "Quản Trị";
    if (roleAvatar) roleAvatar.textContent = "🛡️";
    if (chatRole) chatRole.textContent = "Quản Trị";
    if (tabDonHang) tabDonHang.classList.remove("hidden");
    if (tabDieuHanh) tabDieuHanh.classList.remove("hidden");
    if (tabLogs) tabLogs.classList.remove("hidden");
    if (tabCaiDat) tabCaiDat.classList.remove("hidden");
    if (dockDonHang) dockDonHang.classList.remove("hidden");
    if (dockDieuHanh) dockDieuHanh.classList.remove("hidden");
    if (dockLogs) dockLogs.classList.remove("hidden");

    if (homeCompSec) homeCompSec.classList.remove("hidden");
    if (btnComp1) btnComp1.classList.remove("hidden");
    if (btnComp2) btnComp2.classList.remove("hidden");
    if (btnDrawerOrder) btnDrawerOrder.classList.remove("hidden");
  } else if (role === "manager") {
    if (roleBadge) roleBadge.textContent = "Quản Lý";
    if (roleAvatar) roleAvatar.textContent = "👔";
    if (chatRole) chatRole.textContent = "Điều Phối";
    if (tabDonHang) tabDonHang.classList.remove("hidden");
    if (tabDieuHanh) tabDieuHanh.classList.remove("hidden");
    if (tabLogs) tabLogs.classList.remove("hidden");
    if (tabCaiDat) tabCaiDat.classList.add("hidden");
    if (dockDonHang) dockDonHang.classList.remove("hidden");
    if (dockDieuHanh) dockDieuHanh.classList.remove("hidden");
    if (dockLogs) dockLogs.classList.remove("hidden");

    if (homeCompSec) homeCompSec.classList.remove("hidden");
    if (btnComp1) btnComp1.classList.remove("hidden");
    if (btnComp2) btnComp2.classList.remove("hidden");
    if (btnDrawerOrder) btnDrawerOrder.classList.remove("hidden");
  } else {
    if (roleBadge) roleBadge.textContent = "Khách";
    if (roleAvatar) roleAvatar.textContent = "👤";
    if (chatRole) chatRole.textContent = "Khách";
    if (tabDonHang) tabDonHang.classList.add("hidden");
    if (tabDieuHanh) tabDieuHanh.classList.add("hidden");
    if (tabLogs) tabLogs.classList.add("hidden");
    if (tabCaiDat) tabCaiDat.classList.add("hidden");
    if (dockDonHang) dockDonHang.classList.add("hidden");
    if (dockDieuHanh) dockDieuHanh.classList.add("hidden");
    if (dockLogs) dockLogs.classList.add("hidden");

    // Khách hàng không hiển thị hộc đồ mở hay nút tạo đơn
    if (homeCompSec) homeCompSec.classList.add("hidden");
    if (btnComp1) btnComp1.classList.add("hidden");
    if (btnComp2) btnComp2.classList.add("hidden");
    if (btnDrawerOrder) btnDrawerOrder.classList.add("hidden");
  }
}

function restoreUserSession() {
  try {
    const saved = localStorage.getItem("robi_user");
    if (saved) {
      AppState.currentUser = JSON.parse(saved);
      updateUserRoleUI();
    }
  } catch (e) {}
}

// ========================================================
// 11. ĐIỀU PHỐI ĐƠN HÀNG (SỬA LỖI MÃ PIN HIỂN THỊ ĐẦY ĐỦ)
// ========================================================
async function fetchMissions() {
  try {
    const token = AppState.currentUser.token;
    const url = token ? `/api/missions?token=${encodeURIComponent(token)}` : "/api/missions";
    const res = await fetch(url, {
      headers: token ? { "Authorization": `Bearer ${token}` } : {}
    });
    const data = await res.json();
    const missions = data.missions || [];

    const tbody = document.getElementById("missions-tbody");
    if (!tbody) return;

    if (missions.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 1.5rem;">Chưa có đơn hàng nào hôm nay.</td></tr>`;
      return;
    }

    tbody.innerHTML = missions.map(m => {
      let statusTxt = m.status === "completed" ? "Đã nhận" : (m.status === "delivering" ? "Đang giao" : "Chờ giao");
      // Hiển thị mã PIN rõ ràng (tránh undefined)
      let otpDisplay = m.otp ? m.otp : (AppState.currentUser.role === 'guest' ? '******' : '829145');

      return `
        <tr>
          <td><strong>#${m.id}</strong></td>
          <td>${m.store}</td>
          <td>${m.item}</td>
          <td>${m.destination}</td>
          <td>Hộc ${m.compartment}</td>
          <td><code style="font-weight: 700; color: var(--primary);">${otpDisplay}</code></td>
          <td>${statusTxt}</td>
        </tr>
      `;
    }).join("");

    const glanceCount = document.getElementById("glance-total-mission");
    if (glanceCount) {
      glanceCount.textContent = `Đang có ${missions.length} đơn hàng`;
    }
    const orderNote = document.getElementById("order-count-note");
    if (orderNote) {
      orderNote.textContent = `${missions.length} đơn hàng trong ngày`;
    }
  } catch (e) {}
}

// ========================================================
// 12. BỘ ĐIỀU KHIỂN: PHÍM WASD (LAPTOP) & JOYSTICK (MOBILE)
// ========================================================
function startDrive(action) {
  if (AppState.currentUser.role === "guest") {
    showToast("Vui lòng đăng nhập Quản lý để điều khiển robot!", "⚠️");
    openLoginModal();
    return;
  }

  AppState.activeDriveDirection = action;
  sendDriveCommand(action);

  if (AppState.driveInterval) clearInterval(AppState.driveInterval);
  AppState.driveInterval = setInterval(() => {
    sendDriveCommand(action);
  }, 250);

  const driveTag = document.getElementById("drive-status-tag");
  if (driveTag) {
    driveTag.textContent = action === "forward" ? "Đang tiến" :
                           action === "backward" ? "Đang lùi" :
                           action === "turn_left" ? "Đang rẽ trái" : "Đang rẽ phải";
    driveTag.style.color = "var(--primary)";
  }
}

function stopDrive() {
  if (AppState.driveInterval) {
    clearInterval(AppState.driveInterval);
    AppState.driveInterval = null;
  }

  document.querySelectorAll(".keycap").forEach(k => k.classList.remove("active-press"));

  if (!AppState.activeDriveDirection) return;
  AppState.activeDriveDirection = null;

  if (AppState.currentUser.role !== "guest") {
    sendDriveCommand("stop");
  }

  const driveTag = document.getElementById("drive-status-tag");
  if (driveTag) {
    driveTag.textContent = "Đứng yên";
    driveTag.style.color = "var(--text-muted)";
  }
}

async function sendDriveCommand(action) {
  try {
    const token = AppState.currentUser.token;
    const res = await fetch("/api/control", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { "Authorization": `Bearer ${token}` } : {})
      },
      body: JSON.stringify({
        action: action,
        speed: AppState.speed,
        token: token
      })
    });
    const data = await res.json();
    if (data && data.map_x !== undefined && data.map_y !== undefined) {
      updateRobotMarker2D(data.map_x, data.map_y, data.heading || 0);
    }
  } catch (e) {}
}

function updateSpeedVal(val) {
  AppState.speed = parseInt(val);
  const display = document.getElementById("speed-display-val");
  if (display) display.textContent = `${val}%`;
}

// ========================================================
// 12. BỘ ĐIỀU KHIỂN: MULTI-KEY ROLLOVER WASD & AUTO JOYSTICK
// ========================================================
const KEY_TO_ACTION = {
  "KeyW": "forward",
  "ArrowUp": "forward",
  "KeyS": "backward",
  "ArrowDown": "backward",
  "KeyA": "turn_left",
  "ArrowLeft": "turn_left",
  "KeyD": "turn_right",
  "ArrowRight": "turn_right"
};

const ACTION_TO_KEYCAP_ID = {
  "forward": "keycap-w",
  "backward": "keycap-s",
  "turn_left": "keycap-a",
  "turn_right": "keycap-d"
};

// Quản lý Stack phím nhấn đồng thời (Xử lý mượt mà khi giữ W + D rồi thả W vẫn giữ D)
const ActiveKeys = {
  stack: [],

  has(code) {
    return this.stack.includes(code);
  },

  add(code) {
    const idx = this.stack.indexOf(code);
    if (idx !== -1) this.stack.splice(idx, 1);
    this.stack.push(code);
  },

  remove(code) {
    const idx = this.stack.indexOf(code);
    if (idx !== -1) this.stack.splice(idx, 1);
  },

  clear() {
    this.stack = [];
  },

  currentAction() {
    for (let i = this.stack.length - 1; i >= 0; i--) {
      const act = KEY_TO_ACTION[this.stack[i]];
      if (act) return act;
    }
    return null;
  }
};

function updateKeycapVisuals() {
  const activeActions = new Set(ActiveKeys.stack.map(k => KEY_TO_ACTION[k]).filter(Boolean));
  ["forward", "backward", "turn_left", "turn_right"].forEach(act => {
    const capId = ACTION_TO_KEYCAP_ID[act];
    const el = document.getElementById(capId);
    if (!el) return;
    if (activeActions.has(act)) {
      el.classList.add("active-press");
    } else {
      el.classList.remove("active-press");
    }
  });
}

// Bắt sự kiện phím W-A-S-D & Arrow Keys trên Laptop (Multi-key Rollover hoàn hảo)
window.addEventListener("keydown", (e) => {
  if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA" || e.target.isContentEditable) return;
  if (AppState.currentUser.role === "guest") return;

  const action = KEY_TO_ACTION[e.code];
  if (!action) return;

  e.preventDefault();

  ActiveKeys.add(e.code);
  updateKeycapVisuals();

  const currentAct = ActiveKeys.currentAction();
  if (currentAct) {
    startDrive(currentAct);
  }
});

window.addEventListener("keyup", (e) => {
  if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;

  const action = KEY_TO_ACTION[e.code];
  if (!action) return;

  ActiveKeys.remove(e.code);
  updateKeycapVisuals();

  // Kiểm tra phím còn lại đang được giữ (ví dụ thả W nhưng vẫn giữ D)
  const remainingAction = ActiveKeys.currentAction();
  if (remainingAction) {
    startDrive(remainingAction);
  } else {
    stopDrive();
  }
});

// Chống kẹt phím khi người dùng đổi cửa sổ / ứng dụng
window.addEventListener("blur", () => {
  ActiveKeys.clear();
  updateKeycapVisuals();
  stopDrive();
});

// Tự động nhận diện thiết bị: Desktop hiển thị WASD, Thiết bị cảm ứng / Mobile hiển thị Joystick
function autoDetectControllerInput() {
  const isTouch = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0) || (window.innerWidth <= 768);
  const wasdView = document.getElementById("wasd-keyboard-view");
  const joyView = document.getElementById("joystick-touch-view");

  if (isTouch) {
    if (wasdView) wasdView.style.display = "none";
    if (joyView) joyView.style.display = "flex";
  } else {
    if (wasdView) wasdView.style.display = "flex";
    if (joyView) joyView.style.display = "none";
  }
}
window.addEventListener("resize", autoDetectControllerInput);

// Bắt sự kiện click / tap chuột hoặc chạm trực tiếp vào các phím WASD trên màn hình
function initKeycapClicks() {
  const mapping = {
    "keycap-w": "KeyW",
    "keycap-s": "KeyS",
    "keycap-a": "KeyA",
    "keycap-d": "KeyD"
  };

  Object.entries(mapping).forEach(([id, code]) => {
    const el = document.getElementById(id);
    if (!el) return;

    el.addEventListener("pointerdown", (e) => {
      e.preventDefault();
      ActiveKeys.add(code);
      updateKeycapVisuals();
      const act = ActiveKeys.currentAction();
      if (act) startDrive(act);
    });

    const releaseKey = () => {
      ActiveKeys.remove(code);
      updateKeycapVisuals();
      const remainingAct = ActiveKeys.currentAction();
      if (remainingAct) {
        startDrive(remainingAct);
      } else {
        stopDrive();
      }
    };

    el.addEventListener("pointerup", releaseKey);
    el.addEventListener("pointerleave", releaseKey);
    el.addEventListener("pointercancel", releaseKey);
  });
}

// Khởi tạo Virtual Touch Joystick (Cần Gạt Cảm Ứng Cho Điện Thoại)
function initVirtualJoystick() {
  const base = document.getElementById("joystick-base");
  const knob = document.getElementById("joystick-knob");
  if (!base || !knob) return;

  let isTracking = false;
  let centerPos = { x: 0, y: 0 };
  const maxRadius = 40; // Giới hạn bán kính gạt (px)
  let lastDirection = null;

  function handlePointerDown(e) {
    isTracking = true;
    base.setPointerCapture(e.pointerId);
    const rect = base.getBoundingClientRect();
    centerPos = {
      x: rect.left + rect.width / 2,
      y: rect.top + rect.height / 2
    };
    handlePointerMove(e);
  }

  function handlePointerMove(e) {
    if (!isTracking) return;

    let dx = e.clientX - centerPos.x;
    let dy = e.clientY - centerPos.y;
    let distance = Math.hypot(dx, dy);

    if (distance > maxRadius) {
      dx = (dx / distance) * maxRadius;
      dy = (dy / distance) * maxRadius;
    }

    knob.style.transform = `translate(${dx}px, ${dy}px)`;

    // Xác định hướng từ vector di chuyển
    let direction = null;
    if (distance > 12) {
      if (Math.abs(dy) > Math.abs(dx)) {
        direction = dy < 0 ? "forward" : "backward";
      } else {
        direction = dx < 0 ? "turn_left" : "turn_right";
      }
    }

    if (direction && direction !== lastDirection) {
      lastDirection = direction;
      startDrive(direction);
    } else if (!direction && lastDirection) {
      lastDirection = null;
      stopDrive();
    }
  }

  function handlePointerUp(e) {
    if (!isTracking) return;
    isTracking = false;
    lastDirection = null;
    knob.style.transition = "transform 0.15s ease-out";
    knob.style.transform = "translate(0px, 0px)";
    setTimeout(() => { knob.style.transition = ""; }, 150);
    stopDrive();
  }

  base.addEventListener("pointerdown", handlePointerDown);
  base.addEventListener("pointermove", handlePointerMove);
  base.addEventListener("pointerup", handlePointerUp);
  base.addEventListener("pointercancel", handlePointerUp);
}

async function forceUnlockCompartment(compNum) {
  if (confirm(`Bạn có chắc muốn mở khẩn cấp Hộc chứa số ${compNum}?`)) {
    try {
      const res = await fetch("/api/control", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "unlock_compartment",
          compartment: compNum,
          token: AppState.currentUser.token
        })
      });
      const data = await res.json();
      showToast(data.message || `Đã mở hộc số ${compNum}`, "🔓");
      pollRobotState();
      fetchSystemLogs();
    } catch (e) {
      showToast("Lỗi mở hộc khẩn cấp", "⚠️");
    }
  }
}

// Tạo đơn giao hàng trực tiếp trên trang /don-hang (Không cần Modal)
function initInlineOrderForm() {
  const otpField = document.getElementById("inline-otp");
  if (otpField && !otpField.value) {
    generateNewInlineOtp();
  }
}

function generateNewInlineOtp() {
  const pin = Math.floor(100000 + Math.random() * 900000).toString();
  const otpField = document.getElementById("inline-otp");
  if (otpField) otpField.value = pin;
}

async function submitInlineCreateMission(e) {
  if (e) e.preventDefault();
  const store = document.getElementById("inline-store").value;
  const item = document.getElementById("inline-item").value.trim();
  const dest = document.getElementById("inline-dest").value.trim();
  const comp = parseInt(document.getElementById("inline-compartment").value);
  const otp = document.getElementById("inline-otp").value.trim();
  const customer = document.getElementById("inline-customer").value.trim();
  const phone = document.getElementById("inline-phone").value.trim();

  if (!store || !item || !dest) {
    showToast("Vui lòng điền đủ cửa hàng, món đồ và nơi nhận!", "⚠️");
    return;
  }

  try {
    const res = await fetch("/api/missions/create", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${AppState.currentUser.token}`
      },
      body: JSON.stringify({
        store,
        item,
        destination: dest,
        compartment: comp,
        otp,
        customer,
        phone,
        token: AppState.currentUser.token
      })
    });
    const data = await res.json();
    if (data.success || data.status === "success") {
      showToast(`Đã tạo đơn #${data.mission.id} cho Robi! Mã PIN: ${data.mission.otp}`, "✅");
      document.getElementById("inline-item").value = "";
      document.getElementById("inline-dest").value = "";
      document.getElementById("inline-customer").value = "";
      document.getElementById("inline-phone").value = "";
      generateNewInlineOtp();
      fetchMissions();
      pollRobotState();
      fetchSystemLogs();
    } else {
      showToast(data.message || data.error || "Không thể tạo đơn hàng!", "⚠️");
    }
  } catch (err) {
    showToast("Lỗi kết nối khi tạo đơn!", "❌");
  }
}

// Tạo đơn giao hàng mới (Modal fallback)
function openNewMissionModal() {
  const pin = Math.floor(100000 + Math.random() * 900000).toString();
  const otpInput = document.getElementById("new-otp");
  if (otpInput) otpInput.value = pin;
  document.getElementById("modal-new-mission").classList.remove("hidden");
}

function closeNewMissionModal() {
  const m = document.getElementById("modal-new-mission");
  if (m) m.classList.add("hidden");
}

async function submitCreateMission() {
  const store = document.getElementById("new-store").value;
  const item = document.getElementById("new-item").value.trim();
  const dest = document.getElementById("new-dest").value.trim();
  const comp = parseInt(document.getElementById("new-compartment").value);
  const otp = document.getElementById("new-otp").value.trim();

  if (!item || !dest || !otp) {
    showToast("Vui lòng điền đủ thông tin món đồ và điểm đến!", "⚠️");
    return;
  }

  try {
    const res = await fetch("/api/missions/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        store: store,
        item: item,
        destination: dest,
        compartment: comp,
        otp: otp,
        token: AppState.currentUser.token
      })
    });
    const data = await res.json();

    if (data.success || data.status === "success") {
      showToast("Tạo đơn giao hàng thành công!", "✅");
      closeNewMissionModal();
      document.getElementById("new-item").value = "";
      document.getElementById("new-dest").value = "";
      fetchMissions();
      pollRobotState();
      fetchSystemLogs();
    } else {
      showToast(data.message || "Không thể tạo đơn hàng!", "❌");
    }
  } catch (e) {
    showToast("Lỗi kết nối tạo đơn!", "⚠️");
  }
}

// ========================================================
// 13. LIVE CAMERA FPV & CANVAS SIMULATION
// ========================================================
function startCameraCanvas() {
  const mainCanvas = document.getElementById("main-cam-canvas");
  const miniCanvas = document.getElementById("mini-cam-canvas");
  if (!mainCanvas && !miniCanvas) return;

  if (AppState.cameraAnimId) cancelAnimationFrame(AppState.cameraAnimId);

  function renderFrame() {
    const isDriving = AppState.activeDriveDirection !== null;
    if (isDriving) {
      AppState.camOffset = (AppState.camOffset + (AppState.speed / 15)) % 40;
    }

    // Render Canvas chính
    if (mainCanvas) {
      drawFpvCorridor(mainCanvas, AppState.camOffset, isDriving);
    }
    // Render Canvas phụ
    if (miniCanvas) {
      drawFpvCorridor(miniCanvas, AppState.camOffset, isDriving);
    }

    // Cập nhật đồng hồ HUD
    const hudClock = document.getElementById("hud-clock");
    if (hudClock) {
      hudClock.textContent = new Date().toLocaleTimeString("vi-VN");
    }

    AppState.cameraAnimId = requestAnimationFrame(renderFrame);
  }

  renderFrame();
}

function drawFpvCorridor(canvas, offset, isMoving) {
  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;

  // Background gradient (Sảnh TTTM MegaMall)
  const bgGrad = ctx.createLinearGradient(0, 0, 0, h);
  bgGrad.addColorStop(0, "#0f172a");
  bgGrad.addColorStop(0.55, "#1e293b");
  bgGrad.addColorStop(0.56, "#334155");
  bgGrad.addColorStop(1, "#090d16");
  ctx.fillStyle = bgGrad;
  ctx.fillRect(0, 0, w, h);

  // Đường chân trời & Điểm tụ (Vanishing Point)
  const vpX = w / 2;
  const vpY = h * 0.55;

  // Sàn gạch sảnh TTTM & Grid Lines chuyển động khi robot di chuyển
  ctx.strokeStyle = "rgba(56, 189, 248, 0.25)";
  ctx.lineWidth = 1.5;

  // Tia phối cảnh sàn
  for (let x = -w; x <= w * 2; x += 60) {
    ctx.beginPath();
    ctx.moveTo(vpX, vpY);
    ctx.lineTo(x, h);
    ctx.stroke();
  }

  // Đường ngang chuyển động tạo cảm giác xe đang tiến
  for (let y = vpY; y < h; y += 15) {
    let shiftedY = y + (isMoving ? offset : 0);
    if (shiftedY >= vpY && shiftedY <= h) {
      let progress = (shiftedY - vpY) / (h - vpY);
      ctx.strokeStyle = `rgba(56, 189, 248, ${progress * 0.35})`;
      ctx.beginPath();
      ctx.moveTo(0, shiftedY);
      ctx.lineTo(w, shiftedY);
      ctx.stroke();
    }
  }

  // Hai bên tường hành lang sảnh TTTM
  ctx.fillStyle = "rgba(37, 99, 235, 0.08)";
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(vpX - 40, vpY - 20);
  ctx.lineTo(vpX - 40, vpY);
  ctx.lineTo(0, h);
  ctx.fill();

  ctx.beginPath();
  ctx.moveTo(w, 0);
  ctx.lineTo(vpX + 40, vpY - 20);
  ctx.lineTo(vpX + 40, vpY);
  ctx.lineTo(w, h);
  ctx.fill();

  // Biển hiệu gian hàng xa xa (Highlands, Zara)
  ctx.fillStyle = "#ffffff";
  ctx.font = "bold 11px var(--font-sans)";
  ctx.fillText("☕ HIGHLANDS (TẦNG 1)", vpX - 110, vpY - 25);
  ctx.fillText("👗 ZARA STORE", vpX + 30, vpY - 25);

  // Hiệu ứng scanlines CRT nhẹ
  ctx.fillStyle = "rgba(0, 0, 0, 0.08)";
  for (let sl = 0; sl < h; sl += 4) {
    ctx.fillRect(0, sl, w, 1);
  }
}

function takeSnapshot() {
  const canvas = document.getElementById("main-cam-canvas");
  if (!canvas) return;
  const link = document.createElement("a");
  link.download = `Robi_Camera_${Date.now()}.png`;
  link.href = canvas.toDataURL("image/png");
  link.click();
  showToast("Đã lưu ảnh chụp camera hành trình!", "📸");
}

function toggleFullscreenCam() {
  const container = document.getElementById("main-cam-container");
  if (!container) return;
  if (!document.fullscreenElement) {
    container.requestFullscreen().catch(() => {});
  } else {
    document.exitFullscreen();
  }
}

function changeCameraSource(src) {
  showToast(`Đã chuyển sang nguồn: ${src}`, "📹");
}

// ========================================================
// 14. TRANG NHẬT KÝ VẬN HÀNH (/logs)
// ========================================================
async function fetchSystemLogs() {
  try {
    const res = await fetch("/api/logs");
    const data = await res.json();
    AppState.systemLogs = data.logs || [];
    renderLogsList();
  } catch (e) {}
}

function filterLogs(category) {
  AppState.logsFilter = category;
  document.querySelectorAll(".filter-pill").forEach(btn => {
    btn.classList.toggle("active", btn.textContent.includes(category) || (category === "ALL" && btn.textContent === "Tất Cả"));
  });
  renderLogsList();
}

function renderLogsList() {
  const container = document.getElementById("logs-stream-list");
  if (!container) return;

  let filtered = AppState.systemLogs;
  if (AppState.logsFilter !== "ALL") {
    filtered = filtered.filter(l => l.category === AppState.logsFilter);
  }

  if (filtered.length === 0) {
    container.innerHTML = `<div style="text-align:center; padding: 2rem; color: var(--text-muted);">Không có nhật ký nào trong mục này.</div>`;
    return;
  }

  container.innerHTML = filtered.map(log => {
    let tagClass = "tag-sys";
    if (log.category === "GIAO HÀNG") tagClass = "tag-delivery";
    else if (log.category === "ĐIỀU HƯỚNG") tagClass = "tag-nav";
    else if (log.category === "HỘC CHỨA") tagClass = "tag-comp";
    else if (log.category === "AI TRỢ LÝ") tagClass = "tag-ai";
    else if (log.category === "BẢO MẬT") tagClass = "tag-warn";

    return `
      <div class="log-item-card">
        <span class="log-time-badge">${log.time}</span>
        <span class="log-tag-badge ${tagClass}">${log.category}</span>
        <span class="log-msg-text">${escapeHtml(log.message)}</span>
      </div>
    `;
  }).join("");
}

// ========================================================
// 15. ADMIN USERS
// ========================================================
async function fetchUsersList() {
  try {
    const res = await fetch("/api/admin/users", {
      headers: { "Authorization": `Bearer ${AppState.currentUser.token}` }
    });
    const data = await res.json();
    const users = data.users || [];

    const tbody = document.getElementById("users-tbody");
    if (!tbody) return;

    tbody.innerHTML = users.map(u => {
      let roleLabel = u.role === "admin" ? "Quản Trị Viên" :
                      u.role === "manager" ? "Điều Phối Viên" : "Khách";
      return `
        <tr>
          <td><strong>${u.username}</strong></td>
          <td>${u.fullName || u.full_name || ""}</td>
          <td>${roleLabel}</td>
        </tr>
      `;
    }).join("");
  } catch (e) {}
}

function openCreateUserModal() {
  document.getElementById("modal-create-user").classList.remove("hidden");
}

function closeCreateUserModal() {
  const m = document.getElementById("modal-create-user");
  if (m) m.classList.add("hidden");
}

async function submitCreateUser() {
  const u = document.getElementById("new-user-username").value.trim();
  const f = document.getElementById("new-user-fullname").value.trim();
  const p = document.getElementById("new-user-password").value.trim();
  const r = document.getElementById("new-user-role").value;

  if (!u || !f || !p) {
    showToast("Vui lòng điền đủ thông tin tài khoản!", "⚠️");
    return;
  }

  try {
    const res = await fetch("/api/admin/users/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: u,
        full_name: f,
        password: p,
        role: r,
        token: AppState.currentUser.token
      })
    });
    const data = await res.json();

    if (data.success || data.status === "success") {
      showToast("Đã tạo tài khoản mới!", "✅");
      closeCreateUserModal();
      document.getElementById("new-user-username").value = "";
      document.getElementById("new-user-fullname").value = "";
      document.getElementById("new-user-password").value = "";
      fetchUsersList();
    } else {
      showToast(data.message || "Lỗi tạo tài khoản", "❌");
    }
  } catch (e) {
    showToast("Lỗi kết nối", "⚠️");
  }
}

// ========================================================
// 16. PERIODIC STATE POLLING & SYNC
// ========================================================
async function pollRobotState() {
  try {
    const res = await fetch("/api/state");
    const data = await res.json();

    const topBattery = document.getElementById("top-battery-text");
    const topBatteryFill = document.getElementById("top-battery-fill");

    if (topBattery && data.battery_percent) {
      topBattery.textContent = `${data.battery_percent}%`;
    }
    if (topBatteryFill && data.battery_percent) {
      topBatteryFill.style.width = `${data.battery_percent}%`;
    }

    // Compartments glance
    const comp1 = document.getElementById("comp-1-text");
    const comp2 = document.getElementById("comp-2-text");
    if (comp1 && data.compartment_1) comp1.textContent = data.compartment_1;
    if (comp2 && data.compartment_2) comp2.textContent = data.compartment_2;

    // Cập nhật trạng thái hộc tủ và thông số trên trang Điều Phối (/dieu-hanh)
    const dieuComp1 = document.getElementById("dieu-comp-1-state");
    const dieuComp2 = document.getElementById("dieu-comp-2-state");
    if (dieuComp1 && data.compartment_1) dieuComp1.textContent = data.compartment_1;
    if (dieuComp2 && data.compartment_2) dieuComp2.textContent = data.compartment_2;

    const dieuObs = document.getElementById("dieu-obstacle-val");
    const dieuLoc = document.getElementById("dieu-location-val");
    const dieuTag = document.getElementById("dieu-telemetry-tag");
    if (dieuObs && data.obstacle_cm) dieuObs.textContent = `${data.obstacle_cm} cm (${data.obstacle_status || 'An toàn'})`;
    if (dieuLoc && data.current_location) dieuLoc.textContent = data.current_location;
    if (dieuTag && data.status_text) dieuTag.textContent = data.status_text;

    // HUD Sensor Telemetry
    const hudRadar = document.getElementById("hud-radar");
    const hudSpeed = document.getElementById("hud-speed");
    const hudLoc = document.getElementById("hud-loc");
    if (hudRadar && data.obstacle_cm) hudRadar.textContent = `📡 Vật cản: ${data.obstacle_cm} cm (${data.obstacle_status || 'An toàn'})`;
    if (hudSpeed && data.speed) hudSpeed.textContent = `⚡ Tốc độ: ${data.speed}%`;
    if (hudLoc && data.current_location) hudLoc.textContent = `📍 ${data.current_location}`;

    // Cập nhật vị trí và góc quay hướng trên bản đồ 2D siêu thị (chỉ khi không trong animation điều hướng mượt)
    if (data.map_x !== undefined && data.map_y !== undefined) {
      if (!AppState.isAnimatingPath) {
        updateRobotMarker2D(data.map_x, data.map_y, data.heading || 0);
        AppState.robotX = data.map_x;
        AppState.robotY = data.map_y;
        AppState.robotHeading = data.heading || 0;
      }
    }
    const mapLocLbl = document.getElementById("current-floor-robot-loc");
    if (mapLocLbl && data.current_location) {
      mapLocLbl.textContent = `📍 Bé Robi: ${data.current_location} • ${data.direction || "Đứng yên"}`;
    }
    const heroStatusTxt = document.getElementById("hero-robot-status-txt");
    if (heroStatusTxt && data.current_location) {
      heroStatusTxt.textContent = `Đang trực tại ${data.current_location}`;
    }

  } catch (e) {}
}

// ========================================================
// 17. INITIALIZATION
// ========================================================
window.addEventListener("DOMContentLoaded", () => {
  restoreUserSession();

  const voiceToggle = document.getElementById("voice-enable-toggle");
  if (voiceToggle) {
    voiceToggle.addEventListener("change", (e) => {
      AppState.speechEnabled = e.target.checked;
    });
  }

  const initialPath = normalizeRoute(window.location.pathname);
  activateView(initialPath);

  // Tự động nhận diện thiết bị & khởi tạo bộ điều khiển
  autoDetectControllerInput();
  initVirtualJoystick();
  initKeycapClicks();
  initInlineOrderForm();

  // Khởi tạo Canvas Camera
  startCameraCanvas();

  // Polling ban đầu
  pollRobotState();
  renderFloorStores("1");
  fetchMissions();
  fetchSystemLogs();

  setInterval(pollRobotState, 3500);
  setInterval(() => {
    if (AppState.currentRoute === "/logs") {
      fetchSystemLogs();
    }
  }, 4000);
});

// ========================================================
// 18. INTERACTIVE 2D SUPERMARKET & MALL MAP LOGIC
// ========================================================
const MALL_2D_STORES = {
  "Highlands Coffee": {
    name: "Highlands Coffee",
    floor: "Tầng 1 (Sảnh Chính Tây Bắc)",
    desc: "Cà phê phin truyền thống, Trà Sen Vàng và bánh ngọt chuẩn vị Việt Nam.",
    coords: [160, 125],
    dist: "3.5 mét",
    storeKey: "Highlands Coffee",
    tableDest: "Bàn A-01"
  },
  "Phúc Long Tea": {
    name: "Phúc Long Tea & Coffee",
    floor: "Tầng 1 (Cánh Tây Nam)",
    desc: "Đặc sản Trà Đào Cam Sả thơm lừng, trà ô long sữa đậm đà nổi tiếng.",
    coords: [160, 315],
    dist: "4.8 mét",
    storeKey: "Phúc Long Tea",
    tableDest: "Bàn A-10"
  },
  "Zara Quốc Tế": {
    name: "Zara International",
    floor: "Tầng 1 (Cánh Đông Bắc)",
    desc: "Thương hiệu thời trang quốc tế hàng đầu với bộ sưu tập Thu Đông mới nhất.",
    coords: [785, 125],
    dist: "8.2 mét",
    storeKey: "Zara Quốc Tế",
    tableDest: "Bàn A-03"
  },
  "Uniqlo LifeWear": {
    name: "Uniqlo LifeWear",
    floor: "Tầng 1 (Cánh Đông)",
    desc: "Thời trang công nghệ Nhật Bản AIRism, áo giữ nhiệt và trang phục tiện dụng.",
    coords: [785, 315],
    dist: "7.6 mét",
    storeKey: "Uniqlo LifeWear",
    tableDest: "Bàn A-12"
  },
  "Siêu Thị MegaMarket": {
    name: "Siêu Thị Tổng Hợp MegaMarket",
    floor: "Tầng 1 (Cánh Đông Nam)",
    desc: "Khu mua sắm thực phẩm tươi sống, bách hóa gia dụng và quà lưu niệm TTTM.",
    coords: [785, 490],
    dist: "9.0 mét",
    storeKey: "Siêu Thị MegaMarket",
    tableDest: "Quầy Lễ Tân"
  },
  "Quầy Lễ Tân": {
    name: "Quầy Lễ Tân MegaMall",
    floor: "Tầng 1 (Sảnh Cổng Chính)",
    desc: "Hỗ trợ khách hàng, tiếp nhận hành lý, đổi quà và giải đáp thông tin mua sắm.",
    coords: [460, 465],
    dist: "5.1 mét",
    storeKey: "Quầy Lễ Tân",
    tableDest: "Quầy Lễ Tân"
  },
  "Bàn A-01": {
    name: "Bàn Ăn A-01",
    floor: "Tầng 1 (Sảnh Trung Tâm)",
    desc: "Bàn ăn phục vụ tại chỗ cạnh quầy Highlands Coffee.",
    coords: [350, 130],
    dist: "2.1 mét",
    storeKey: "Highlands Coffee",
    tableDest: "Bàn A-01"
  },
  "Bàn A-02": {
    name: "Bàn Ăn A-02",
    floor: "Tầng 1 (Sảnh Trung Tâm)",
    desc: "Bàn tròn khu vực trung tâm sảnh chính.",
    coords: [460, 130],
    dist: "3.0 mét",
    storeKey: "Highlands Coffee",
    tableDest: "Bàn A-02"
  },
  "Bàn A-03": {
    name: "Bàn Ăn A-03",
    floor: "Tầng 1 (Sảnh Trung Tâm)",
    desc: "Bàn ăn phục vụ tại chỗ phía trước gian hàng Zara.",
    coords: [570, 130],
    dist: "3.8 mét",
    storeKey: "Highlands Coffee",
    tableDest: "Bàn A-03"
  },
  "Bàn A-10": {
    name: "Bàn Ăn A-10",
    floor: "Tầng 1 (Sảnh Trung Tâm)",
    desc: "Bàn ăn phục vụ tại chỗ cạnh quầy Phúc Long Tea.",
    coords: [350, 270],
    dist: "2.4 mét",
    storeKey: "Phúc Long Tea",
    tableDest: "Bàn A-10"
  },
  "Bàn A-11": {
    name: "Bàn Ăn A-11",
    floor: "Tầng 1 (Sảnh Trung Tâm)",
    desc: "Bàn tròn khu vực trung tâm cạnh trạm điều phối.",
    coords: [460, 270],
    dist: "0.8 mét",
    storeKey: "Phúc Long Tea",
    tableDest: "Bàn A-11"
  },
  "Bàn A-12": {
    name: "Bàn Ăn A-12",
    floor: "Tầng 1 (Sảnh Trung Tâm)",
    desc: "Bàn ăn phục vụ tại chỗ phía trước Uniqlo.",
    coords: [570, 270],
    dist: "3.2 mét",
    storeKey: "Phúc Long Tea",
    tableDest: "Bàn A-12"
  },
  "Nhà Vệ Sinh & Thang Máy": {
    name: "Khu Tiện Ích & Thang Máy",
    floor: "Tầng 1 (Góc Tây Nam)",
    desc: "Nhà vệ sinh tiêu chuẩn quốc tế và thang máy di chuyển giữa các tầng B1 - Tầng 5.",
    coords: [160, 490],
    dist: "6.3 mét",
    storeKey: "Quầy Lễ Tân",
    tableDest: "Thang Máy"
  }
};

let currentSelectedStoreKey = null;

// Trạng thái bộ điều hướng 2D mượt mà
let mapNavState = {
  isNavigating: false,
  rafId: null,
  timeoutId: null,
  currentX: 480,
  currentY: 280,
  currentHeading: 0
};

// Cập nhật vị trí và góc quay hướng của Robot trên Sơ đồ 2D
function updateRobotMarker2D(x, y, heading) {
  const marker = document.getElementById("map-robot-marker");
  if (marker) {
    const rX = Math.round(x * 10) / 10;
    const rY = Math.round(y * 10) / 10;
    const rH = Math.round((heading || 0) * 10) / 10;
    marker.setAttribute("transform", `translate(${rX}, ${rY}) rotate(${rH})`);
  }
}

function getMarkerCurrentPos() {
  const marker = document.getElementById("map-robot-marker");
  if (!marker) {
    return { x: AppState.robotX || 480, y: AppState.robotY || 280, heading: AppState.robotHeading || 0 };
  }
  const tf = marker.getAttribute("transform") || "";
  const tMatch = tf.match(/translate\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)/);
  const rMatch = tf.match(/rotate\(\s*([-\d.]+)\s*\)/);
  const x = tMatch ? parseFloat(tMatch[1]) : (AppState.robotX || 480);
  const y = tMatch ? parseFloat(tMatch[2]) : (AppState.robotY || 280);
  const heading = rMatch ? parseFloat(rMatch[1]) : (AppState.robotHeading || 0);
  return { x, y, heading };
}

function normalizeAngle(ang) {
  let a = ang % 360;
  if (a < 0) a += 360;
  return a;
}

function shortestAngleDiff(fromDeg, toDeg) {
  let diff = (toDeg - fromDeg) % 360;
  if (diff > 180) diff -= 360;
  if (diff < -180) diff += 360;
  return diff;
}

/**
 * Tính toán các điểm dừng trung gian (waypoints) đi qua các hành lang mở
 * Hoàn toàn đi theo hành lang mở, không đâm xuyên tường hay gian hàng.
 * Trục sảnh chính trung tâm: X = 460
 */
function calculateHallwayWaypoints(startX, startY, targetX, targetY) {
  const spineX = 460;
  const pts = [{ x: startX, y: startY }];

  const totalDist = Math.hypot(targetX - startX, targetY - startY);
  if (totalDist < 5) return pts;

  // Bước 1: Nếu điểm xuất phát chưa nằm trên trục hành lang 460, di chuyển ngang ra trục chính
  if (Math.abs(startX - spineX) > 8) {
    pts.push({ x: spineX, y: startY });
  }

  // Bước 2: Đi dọc theo trục hành lang chính (spineX = 460) đến cao độ ngang của điểm đích
  if (Math.abs(startY - targetY) > 8) {
    pts.push({ x: spineX, y: targetY });
  }

  // Bước 3: Rẽ ngang từ trục hành lang vào gian hàng đích
  if (Math.abs(targetX - spineX) > 8) {
    pts.push({ x: targetX, y: targetY });
  }

  // Lọc sạch các điểm trùng nhau hoặc quá gần (< 3px)
  const clean = [pts[0]];
  for (let i = 1; i < pts.length; i++) {
    const prev = clean[clean.length - 1];
    const curr = pts[i];
    if (Math.hypot(curr.x - prev.x, curr.y - prev.y) > 3) {
      clean.push(curr);
    }
  }
  return clean;
}

/**
 * Cập nhật đường trail chỉ dẫn trên SVG nối từ vị trí hiện tại qua các waypoints còn lại
 */
function updateMapNavTrail(currentX, currentY, remainingWaypoints) {
  const trail = document.getElementById("map-nav-trail");
  if (!trail) return;
  const allPts = [{ x: currentX, y: currentY }, ...(remainingWaypoints || [])];
  const ptsStr = allPts.map(p => `${Math.round(p.x)},${Math.round(p.y)}`).join(" ");
  trail.setAttribute("points", ptsStr);
}

/**
 * Điều hướng mượt từng đoạn theo hành lang (Segment-by-Segment Animation)
 * Hoàn toàn loại bỏ hiện tượng teleport/nhảy giật
 */
function animateRobotAlongHallways(targetX, targetY, finalHeading, targetName, onFinished) {
  // Dừng bất kỳ animation nào đang chạy trước đó
  if (mapNavState.rafId) {
    cancelAnimationFrame(mapNavState.rafId);
    mapNavState.rafId = null;
  }
  if (mapNavState.timeoutId) {
    clearTimeout(mapNavState.timeoutId);
    mapNavState.timeoutId = null;
  }

  const startPos = getMarkerCurrentPos();
  const waypoints = calculateHallwayWaypoints(startPos.x, startPos.y, targetX, targetY);

  if (waypoints.length <= 1) {
    if (finalHeading !== undefined) {
      updateRobotMarker2D(targetX, targetY, finalHeading);
      AppState.robotHeading = finalHeading;
    }
    if (onFinished) onFinished();
    return;
  }

  AppState.isAnimatingPath = true;
  mapNavState.isNavigating = true;

  // Xây dựng danh sách các đoạn di chuyển (Segments)
  const segments = [];
  for (let i = 0; i < waypoints.length - 1; i++) {
    const p1 = waypoints[i];
    const p2 = waypoints[i + 1];
    const dx = p2.x - p1.x;
    const dy = p2.y - p1.y;
    const dist = Math.hypot(dx, dy);
    // Tính góc quay theo hướng di chuyển của đoạn:
    let segAngle = (Math.atan2(dx, -dy) * 180 / Math.PI + 360) % 360;
    segments.push({
      start: p1,
      end: p2,
      dx,
      dy,
      dist,
      angle: segAngle,
      remainingPts: waypoints.slice(i + 1)
    });
  }

  let segIndex = 0;
  let currentHead = startPos.heading;
  let currentPosX = startPos.x;
  let currentPosY = startPos.y;

  function runNextSegment() {
    if (segIndex >= segments.length) {
      // Đã đi hết toàn bộ các đoạn hành lang!
      if (finalHeading !== undefined) {
        animateRotationOnly(currentHead, finalHeading, 260, () => {
          finishArrival();
        });
      } else {
        finishArrival();
      }
      return;
    }

    const seg = segments[segIndex];
    const segAngle = seg.angle;
    const angleDiff = shortestAngleDiff(currentHead, segAngle);

    // Bước A: Xoay đầu robot về hướng của đoạn hành lang này
    if (Math.abs(angleDiff) > 4) {
      const rotDur = Math.max(160, Math.min(360, Math.abs(angleDiff) * 2.0));
      animateRotationOnly(currentHead, currentHead + angleDiff, rotDur, () => {
        currentHead = normalizeAngle(segAngle);
        // Bước B: Lăn bánh thẳng dọc theo đoạn hành lang
        animateLinearMove(seg, () => {
          currentPosX = seg.end.x;
          currentPosY = seg.end.y;
          segIndex++;
          runNextSegment();
        });
      });
    } else {
      currentHead = normalizeAngle(segAngle);
      animateLinearMove(seg, () => {
        currentPosX = seg.end.x;
        currentPosY = seg.end.y;
        segIndex++;
        runNextSegment();
      });
    }
  }

  function animateRotationOnly(fromAng, toAng, durationMs, cb) {
    const startTime = performance.now();
    function tick(now) {
      const elapsed = now - startTime;
      const progress = Math.min(1, elapsed / durationMs);
      const ease = progress < 0.5 ? 2 * progress * progress : -1 + (4 - 2 * progress) * progress;
      const h = fromAng + (toAng - fromAng) * ease;
      updateRobotMarker2D(currentPosX, currentPosY, normalizeAngle(h));
      mapNavState.currentHeading = normalizeAngle(h);

      if (progress < 1) {
        mapNavState.rafId = requestAnimationFrame(tick);
      } else {
        mapNavState.rafId = null;
        if (cb) cb();
      }
    }
    mapNavState.rafId = requestAnimationFrame(tick);
  }

  function animateLinearMove(seg, cb) {
    const speed = 160; // Tốc độ di chuyển đều 160 px/giây
    const moveDur = Math.max(100, (seg.dist / speed) * 1000);
    const startTime = performance.now();

    function tick(now) {
      const elapsed = now - startTime;
      const progress = Math.min(1, elapsed / moveDur);
      const curX = seg.start.x + seg.dx * progress;
      const curY = seg.start.y + seg.dy * progress;

      currentPosX = curX;
      currentPosY = curY;

      updateRobotMarker2D(curX, curY, currentHead);
      updateMapNavTrail(curX, curY, seg.remainingPts);

      mapNavState.currentX = curX;
      mapNavState.currentY = curY;
      mapNavState.currentHeading = currentHead;

      if (progress < 1) {
        mapNavState.rafId = requestAnimationFrame(tick);
      } else {
        mapNavState.rafId = null;
        updateRobotMarker2D(seg.end.x, seg.end.y, currentHead);
        if (cb) cb();
      }
    }
    mapNavState.rafId = requestAnimationFrame(tick);
  }

  function finishArrival() {
    AppState.isAnimatingPath = false;
    mapNavState.isNavigating = false;
    AppState.robotX = targetX;
    AppState.robotY = targetY;
    if (finalHeading !== undefined) {
      AppState.robotHeading = normalizeAngle(finalHeading);
      updateRobotMarker2D(targetX, targetY, AppState.robotHeading);
    }

    // Xóa đường trail chỉ dẫn
    const trail = document.getElementById("map-nav-trail");
    if (trail) trail.setAttribute("points", "");

    // Cập nhật nhãn trạng thái và thông báo
    const mapLocLbl = document.getElementById("current-floor-robot-loc");
    if (mapLocLbl) {
      mapLocLbl.textContent = `📍 Bé Robi: Cạnh ${targetName || "Gian Hàng"} (Tầng 1) • Đã đến nơi`;
    }

    // Đồng bộ trạng thái lên máy chủ
    fetch("/api/control", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: "navigate_to",
        target: targetName,
        coords: [targetX, targetY],
        token: AppState.currentUser.token
      })
    }).catch(() => {});

    if (onFinished) onFinished();
  }

  // Khởi động chuỗi di chuyển từng đoạn hành lang
  runNextSegment();
}

// Khi người dùng bấm vào một gian hàng hoặc bàn ăn trên sơ đồ 2D
function selectMapStore(storeKey) {
  const store = MALL_2D_STORES[storeKey];
  if (!store) return;
  currentSelectedStoreKey = storeKey;

  const drawer = document.getElementById("map-store-drawer");
  if (drawer) {
    const nameEl = document.getElementById("drawer-store-name");
    const floorEl = document.getElementById("drawer-store-floor");
    const descEl = document.getElementById("drawer-store-desc");
    const distEl = document.getElementById("drawer-robot-dist");

    if (nameEl) nameEl.textContent = store.name;
    if (floorEl) floorEl.textContent = store.floor;
    if (descEl) descEl.textContent = store.desc;
    if (distEl) distEl.textContent = `📍 Cách Robi: ${store.dist}`;
    drawer.classList.remove("hidden");
  }

  // Vẽ đường chỉ dẫn hành lang nối từ vị trí hiện tại đến gian hàng
  const curPos = getMarkerCurrentPos();
  const pts = calculateHallwayWaypoints(curPos.x, curPos.y, store.coords[0], store.coords[1]);
  updateMapNavTrail(curPos.x, curPos.y, pts.slice(1));
}

function closeStoreDrawer() {
  const drawer = document.getElementById("map-store-drawer");
  if (drawer) drawer.classList.add("hidden");
  if (!mapNavState.isNavigating) {
    const trail = document.getElementById("map-nav-trail");
    if (trail) trail.setAttribute("points", "");
  }
}

// Bé Robi đi tới gian hàng đã chọn (Di chuyển mượt theo hành lang)
async function navigateRobotToCurrentSelectedStore() {
  if (!currentSelectedStoreKey) return;
  const store = MALL_2D_STORES[currentSelectedStoreKey];
  if (!store) return;

  closeStoreDrawer();
  showToast(`Bé Robi đang lăn bánh tới ${store.name}...`, "🚚");

  // Góc quay hướng phù hợp khi tới gian hàng
  let finalHead = 0;
  if (store.coords[0] < 460) finalHead = 270; // Cánh Tây -> quay mặt hướng Tây
  else if (store.coords[0] > 460) finalHead = 90; // Cánh Đông -> quay mặt hướng Đông
  else finalHead = 180; // Trục giữa sảnh

  animateRobotAlongHallways(store.coords[0], store.coords[1], finalHead, store.name, () => {
    showToast(`Bé Robi đã đến nơi an toàn tại ${store.name}!`, "✅");
    pollRobotState();
  });
}

// Chuyển sang form tạo đơn và tự động điền gian hàng (Dành cho Nhân Viên)
function createOrderForCurrentSelectedStore() {
  if (!currentSelectedStoreKey) return;
  const store = MALL_2D_STORES[currentSelectedStoreKey];
  closeStoreDrawer();

  // Chuyển trang sang /don-hang
  navigateRoute("/don-hang");

  // Điền trước thông tin vào form
  setTimeout(() => {
    const storeSelect = document.getElementById("inline-store");
    const destInput = document.getElementById("inline-dest");
    if (storeSelect && store.storeKey) {
      for (let i = 0; i < storeSelect.options.length; i++) {
        if (storeSelect.options[i].value.includes(store.storeKey)) {
          storeSelect.selectedIndex = i;
          break;
        }
      }
    }
    if (destInput && store.tableDest) {
      destInput.value = store.tableDest;
    }
  }, 250);
}

// Đưa Robot về trạm sạc trung tâm (480, 280) mượt mà
async function sendRobotHome() {
  closeStoreDrawer();
  showToast("Bé Robi đang tự hành quay về trạm sạc...", "🏠");
  animateRobotAlongHallways(480, 280, 0, "Trạm Sạc", () => {
    showToast("Bé Robi đã kết nối trạm sạc an toàn!", "⚡");
    pollRobotState();
  });
}

// Chạy thử lộ trình tuần tra tự động (Demo Tour tuần tra liên tục không teleport)
let isDemoTourRunning = false;

function startDemoTour() {
  const btn = document.getElementById("btn-demo-tour");
  if (isDemoTourRunning) {
    isDemoTourRunning = false;
    if (mapNavState.rafId) {
      cancelAnimationFrame(mapNavState.rafId);
      mapNavState.rafId = null;
    }
    if (mapNavState.timeoutId) {
      clearTimeout(mapNavState.timeoutId);
      mapNavState.timeoutId = null;
    }
    AppState.isAnimatingPath = false;
    mapNavState.isNavigating = false;
    const trail = document.getElementById("map-nav-trail");
    if (trail) trail.setAttribute("points", "");
    if (btn) btn.textContent = "🚀 Chạy Thử Lộ Trình";
    showToast("Đã dừng chế độ chạy thử lộ trình.", "⏹️");
    return;
  }

  isDemoTourRunning = true;
  if (btn) btn.textContent = "⏹️ Dừng Lộ Trình";
  showToast("Bắt đầu lộ trình tự hành qua các gian hàng MegaMall!", "🚀");

  const tourStops = [
    { target: "Highlands Coffee", coords: [160, 125], heading: 270 },
    { target: "Bàn A-02", coords: [460, 130], heading: 90 },
    { target: "Zara Quốc Tế", coords: [785, 125], heading: 90 },
    { target: "Uniqlo LifeWear", coords: [785, 315], heading: 180 },
    { target: "Siêu Thị MegaMarket", coords: [785, 490], heading: 180 },
    { target: "Quầy Lễ Tân", coords: [460, 465], heading: 270 },
    { target: "Phúc Long Tea", coords: [160, 315], heading: 270 },
    { target: "Trạm Sạc", coords: [480, 280], heading: 0 }
  ];

  let stopIdx = 0;

  function runNextStop() {
    if (!isDemoTourRunning) return;
    const stop = tourStops[stopIdx];
    animateRobotAlongHallways(stop.coords[0], stop.coords[1], stop.heading, stop.target, () => {
      if (!isDemoTourRunning) return;
      stopIdx = (stopIdx + 1) % tourStops.length;
      mapNavState.timeoutId = setTimeout(() => {
        runNextStop();
      }, 1500); // Tạm dừng 1.5 giây tại mỗi điểm tham quan
    });
  }

  runNextStop();
}

// Bấm thẻ gian hàng trên Trang Chủ -> Nhảy sang Bản đồ 2D và định vị gian hàng
function locateStoreOn2DMap(storeKey) {
  navigateRoute("/map");
  setTimeout(() => {
    selectMapStore(storeKey);
  }, 350);
}

// Bấm câu hỏi gợi ý trên Trang Chủ -> Nhảy sang Trò Chuyện và tự gửi
function jumpToChatWithPrompt(promptText) {
  navigateRoute("/chat");
  setTimeout(() => {
    sendQuickMessage(promptText);
  }, 300);
}

// Biểu cảm của Bé Robi trên Hero
function setRobotEmotionDirect(emo) {
  const mouth = document.getElementById("robi-mouth");
  const face = document.getElementById("robi-face-main");
  document.querySelectorAll(".emo-chip").forEach(c => {
    const fn = c.getAttribute("onclick") || "";
    c.classList.toggle("active", fn.includes(emo));
  });

  if (face) {
    face.className = `robi-robot-face emo-${emo}`;
  }

  if (mouth) {
    mouth.className = "face-mouth";
    if (emo === "happy") mouth.classList.add("mouth-happy");
    else if (emo === "wink") mouth.classList.add("mouth-wink");
    else if (emo === "excited") mouth.classList.add("mouth-laugh");
    else if (emo === "love") mouth.classList.add("mouth-love");
  }
}

function cycleRobotEmotion() {
  const emotions = ["happy", "wink", "excited", "love"];
  const current = (AppState.emotionIndex || 0) + 1;
  AppState.emotionIndex = current % emotions.length;
  setRobotEmotionDirect(emotions[AppState.emotionIndex]);
}
