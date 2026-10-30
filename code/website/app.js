// ==============================================================================
// ROBOT CARRIER WEB DASHBOARD LOGIC
// ==============================================================================

const speedSlider = document.getElementById("speed-slider");
const speedVal = document.getElementById("speed-val");
const motorDirDisplay = document.getElementById("motor-direction");
const motorSpeedDisplay = document.getElementById("motor-speed-display");
const driverStateDisplay = document.getElementById("driver-state");
const logOutput = document.getElementById("log-output");
const connBadge = document.getElementById("connection-badge");
const connText = document.getElementById("connection-text");

let currentSpeed = parseInt(speedSlider.value, 10);
let isAutoTesting = false;

// 1. Cập nhật Slider Tốc độ
speedSlider.addEventListener("input", (e) => {
  currentSpeed = parseInt(e.target.value, 10);
  speedVal.textContent = `${currentSpeed}%`;
});

// 2. Gửi Lệnh Điều Khiển Bánh Trái
async function sendMotorCmd(action, overrideSpeed = null) {
  const speed = overrideSpeed !== null ? overrideSpeed : currentSpeed;
  highlightButton(action);

  try {
    const url = `/api/motor/left?action=${encodeURIComponent(action)}&speed=${speed}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP Error ${res.status}`);

    const data = await res.json();
    
    // Cập nhật giao diện
    motorDirDisplay.textContent = data.direction;
    motorSpeedDisplay.textContent = `${data.speed}%`;
    driverStateDisplay.textContent = data.enabled ? "ENABLED" : "STANDBY";

    // Phối màu hiển thị trạng thái
    if (data.direction === "FORWARD") {
      motorDirDisplay.style.color = "#10b981";
    } else if (data.direction === "REVERSE") {
      motorDirDisplay.style.color = "#00f2fe";
    } else if (data.direction === "BRAKE") {
      motorDirDisplay.style.color = "#f59e0b";
    } else {
      motorDirDisplay.style.color = "#9ca3af";
    }

    addLog(`[LỆNH] Bánh trái -> ${action.toUpperCase()} (${speed}%)`, "cmd");
    setOnlineStatus(true);
  } catch (err) {
    console.error("Lỗi gửi lệnh:", err);
    addLog(`[LỖI] Không thể gửi lệnh: ${err.message}`, "warn");
    setOnlineStatus(false);
  }
}

// 3. Quy trình Kiểm tra Tự động (Auto Test)
async function runAutoTest() {
  if (isAutoTesting) return;
  isAutoTesting = true;
  addLog("=== BẮT ĐẦU QUY TRÌNH AUTO TEST ===", "info");

  const steps = [
    { action: "enable", text: "Bước 1: Bật Driver STBY", delay: 1000 },
    { action: "forward", speed: 50, text: "Bước 2: Quay TIẾN 50% trong 2.5s", delay: 2500 },
    { action: "brake", text: "Bước 3: Hãm phanh khẩn cấp trong 1.5s", delay: 1500 },
    { action: "reverse", speed: 50, text: "Bước 4: Quay LÙI 50% trong 2.5s", delay: 2500 },
    { action: "stop", text: "Bước 5: Thả trôi dừng tự nhiên", delay: 1000 },
    { action: "forward", speed: 80, text: "Bước 6: Tăng tốc tiến 80% trong 2s", delay: 2000 },
    { action: "brake", text: "Bước 7: Phanh kết thúc", delay: 1000 },
    { action: "stop", text: "Hoàn tất kiểm tra!", delay: 0 }
  ];

  for (const step of steps) {
    addLog(`-> ${step.text}`, "info");
    await sendMotorCmd(step.action, step.speed || currentSpeed);
    if (step.delay > 0) {
      await new Promise(r => setTimeout(r, step.delay));
    }
  }

  isAutoTesting = false;
  addLog("=== AUTO TEST HOÀN TẤT THÀNH CÔNG ===", "info");
}

// 4. Bàn phím điều khiển (Keyboard Shortcuts)
window.addEventListener("keydown", (e) => {
  // Tránh lặp khi giữ phím
  if (e.repeat) return;

  const key = e.key.toUpperCase();
  if (key === "W") {
    sendMotorCmd("forward");
  } else if (key === "S") {
    sendMotorCmd("reverse");
  } else if (key === "B") {
    sendMotorCmd("brake");
  } else if (key === " " || key === "X") {
    e.preventDefault();
    sendMotorCmd("stop");
  } else if (key === "+" || key === "=") {
    currentSpeed = Math.min(100, currentSpeed + 10);
    speedSlider.value = currentSpeed;
    speedVal.textContent = `${currentSpeed}%`;
    addLog(`Đã tăng tốc độ: ${currentSpeed}%`, "sys");
  } else if (key === "-" || key === "_") {
    currentSpeed = Math.max(20, currentSpeed - 10);
    speedSlider.value = currentSpeed;
    speedVal.textContent = `${currentSpeed}%`;
    addLog(`Đã giảm tốc độ: ${currentSpeed}%`, "sys");
  }
});

// 5. Hiệu ứng nút bấm
function highlightButton(action) {
  const btnMap = {
    forward: document.getElementById("btn-forward"),
    reverse: document.getElementById("btn-reverse"),
    brake: document.getElementById("btn-brake"),
    stop: document.getElementById("btn-stop")
  };

  Object.values(btnMap).forEach(b => b && b.classList.remove("active"));
  if (btnMap[action]) {
    btnMap[action].classList.add("active");
    setTimeout(() => btnMap[action].classList.remove("active"), 300);
  }
}

// 6. Ghi Nhật ký (Live Logs)
function addLog(msg, type = "sys") {
  const now = new Date();
  const timeStr = now.toTimeString().split(" ")[0];
  const div = document.createElement("div");
  div.className = `log-entry ${type}`;
  div.textContent = `[${timeStr}] ${msg}`;
  logOutput.appendChild(div);
  logOutput.scrollTop = logOutput.scrollHeight;
}

function clearLogs() {
  logOutput.innerHTML = "";
  addLog("Đã xóa nhật ký.", "sys");
}

// 7. Trạng thái kết nối
function setOnlineStatus(isOnline) {
  if (isOnline) {
    connBadge.style.background = "rgba(16, 185, 129, 0.15)";
    connBadge.style.borderColor = "rgba(16, 185, 129, 0.4)";
    connBadge.style.color = "#10b981";
    connText.textContent = "KẾT NỐI OK";
  } else {
    connBadge.style.background = "rgba(239, 68, 68, 0.15)";
    connBadge.style.borderColor = "rgba(239, 68, 68, 0.4)";
    connBadge.style.color = "#f87171";
    connText.textContent = "MẤT KẾT NỐI";
  }
}

// Kiểm tra định kỳ kết nối server
setInterval(async () => {
  try {
    const res = await fetch("/api/status");
    if (res.ok) {
      setOnlineStatus(true);
    } else {
      setOnlineStatus(false);
    }
  } catch {
    setOnlineStatus(false);
  }
}, 4000);
