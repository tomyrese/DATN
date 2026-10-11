import os
import socket
import mimetypes
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, Header, HTTPException, status, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response, JSONResponse, HTMLResponse

from src.config import RobotConfig, config
from src.network.protocol import (
    PairRequest, PairResponse, HealthResponse, InfoResponse, TelemetryMessage,
    LoginRequest, LoginResponse
)
from src.network.auth_manager import AuthManager
from src.network.pairing_manager import PairingManager
from src.network.websocket_manager import WebSocketManager
from src.network.camera_stream import CameraStreamManager
from src.security.rbac import (
    get_current_session, require_authenticated, require_admin,
    require_staff_or_admin, check_store_access
)
from src.security.auth_service import SessionInfo
from src.services.logging_service import logger

def create_api_server(
    robot_controller: Any,
    auth_manager: AuthManager,
    pairing_manager: PairingManager,
    websocket_manager: WebSocketManager,
    camera_stream: CameraStreamManager,
    cfg: Optional[RobotConfig] = None
) -> FastAPI:
    app_cfg = cfg or config
    app = FastAPI(title="Pi Robot Mall Central Command Server", version="2.0.0", docs_url="/docs", redoc_url=None)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Legacy verify_auth_token helper for paired clients
    def verify_auth_token(authorization: Optional[str] = Header(None), token: Optional[str] = Query(None)) -> str:
        req_token = None
        if authorization and authorization.startswith("Bearer "):
            req_token = authorization[7:].strip()
        elif token:
            req_token = token.strip()

        if not req_token or not auth_manager.validate_token(req_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="AUTH_REQUIRED: Invalid or missing session token"
            )
        return req_token

    # ==================== AUTHENTICATION & SESSIONS ====================
    @app.post("/api/v1/auth/login", response_model=LoginResponse)
    async def post_login(req: LoginRequest, request: Request):
        client_ip = request.client.host if request.client else ""
        user_agent = request.headers.get("user-agent", "")
        session = robot_controller.auth_service.login(req.username, req.password, ip_address=client_ip, user_agent=user_agent)
        if not session:
            return LoginResponse(success=False, message="Tên đăng nhập hoặc mật khẩu không chính xác")

        # Also register with AuthManager for stream/pairing token compatibility
        auth_manager.sessions[session.token] = session.expires_at

        return LoginResponse(
            success=True,
            token=session.token,
            user={
                "id": session.user_id,
                "username": session.username,
                "fullName": session.full_name,
                "role": session.role,
                "assignedStoreIds": session.assigned_store_ids
            },
            message="Đăng nhập thành công"
        )

    @app.post("/api/v1/auth/logout")
    async def post_logout(session: SessionInfo = Depends(require_authenticated)):
        robot_controller.auth_service.logout(session.token)
        auth_manager.revoke_token(session.token)
        return {"success": True, "message": "Đã đăng xuất"}

    @app.get("/api/v1/auth/me")
    async def get_current_user_profile(session: Optional[SessionInfo] = Depends(get_current_session)):
        if not session:
            return {
                "authenticated": False,
                "role": "guest",
                "username": "Khách Tham Quan",
                "assignedStoreIds": []
            }
        return {
            "authenticated": True,
            "id": session.user_id,
            "username": session.username,
            "fullName": session.full_name,
            "role": session.role,
            "assignedStoreIds": session.assigned_store_ids
        }

    # ==================== ADMIN: USER & AUDIT MANAGEMENT ====================
    @app.get("/api/v1/admin/users")
    async def get_admin_users(admin: SessionInfo = Depends(require_admin)):
        users = robot_controller.auth_service.db.fetchall("""
            SELECT id, username, full_name, role, is_active, created_at
            FROM users
            ORDER BY created_at DESC
        """)
        # Attach assigned stores to staff users
        for u in users:
            if u["role"] == "staff":
                u["assignedStoreIds"] = robot_controller.auth_service.get_staff_store_ids(u["id"])
            else:
                u["assignedStoreIds"] = []
        return {"users": users}

    @app.post("/api/v1/admin/users")
    async def create_admin_user(data: Dict[str, Any], admin: SessionInfo = Depends(require_admin)):
        username = data.get("username", "").strip()
        password = data.get("password", "")
        full_name = data.get("fullName", "")
        role = data.get("role", "staff")
        store_ids = data.get("assignedStoreIds", [])

        if not username or not password or not full_name:
            raise HTTPException(status_code=400, detail="Missing required user fields")

        try:
            user = robot_controller.auth_service.create_user(
                username=username,
                password=password,
                full_name=full_name,
                role=role,
                store_ids=store_ids,
                creator_session=admin
            )
            return {"success": True, "user": user.__dict__}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.patch("/api/v1/admin/users/{user_id}/status")
    async def toggle_user_status(user_id: str, data: Dict[str, Any], admin: SessionInfo = Depends(require_admin)):
        is_active = data.get("isActive", True)
        ok = robot_controller.auth_service.set_user_active(user_id, is_active, admin)
        return {"success": ok}

    @app.get("/api/v1/admin/audit-logs")
    async def get_admin_audit_logs(admin: SessionInfo = Depends(require_admin)):
        logs = robot_controller.auth_service.db.fetchall("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 100")
        return {"logs": logs}

    @app.post("/api/v1/admin/backup-db")
    async def backup_database_admin(admin: SessionInfo = Depends(require_admin)):
        from src.database.migrator import DatabaseMigrator
        migrator = DatabaseMigrator(robot_controller.auth_service.db)
        backup_path = migrator.backup_database()
        robot_controller.auth_service.log_audit(
            user_id=admin.user_id,
            username=admin.username,
            role=admin.role,
            action="BACKUP_DATABASE",
            resource="DATABASE",
            details=f"Backup created at {backup_path}"
        )
        return {"success": True, "backupPath": backup_path}

    # ==================== HEALTH & TELEMETRY ====================
    @app.get("/api/v1/health", response_model=HealthResponse)
    async def get_health():
        return HealthResponse(
            status="ok" if robot_controller.running else "stopped",
            robotState=robot_controller.state.value,
            safetyState=robot_controller.safety.safety_state.value,
            camera=robot_controller.camera.is_alive(),
            detector=robot_controller.detector.runtime != "none",
            motor=robot_controller.motor.enabled,
            oled=robot_controller.oled.available,
            server=True
        )

    @app.get("/api/v1/info", response_model=InfoResponse)
    async def get_info():
        return InfoResponse(
            robotId=app_cfg.ROBOT_ID,
            robotName=app_cfg.ROBOT_NAME,
            apiVersion="v1",
            protocolVersion=1,
            hostname=socket.gethostname(),
            serverVersion="2.0.0",
            paired=auth_manager.has_paired_clients()
        )

    @app.get("/api/v1/status")
    async def get_status():
        return robot_controller.get_telemetry_snapshot()

    @app.get("/api/v1/config/public")
    async def get_public_config():
        return {
            "defaultSpeed": app_cfg.DEFAULT_SPEED,
            "speedRange": [-1.0, 1.0],
            "stopZone": {
                "xMin": app_cfg.STOP_ZONE_X_MIN,
                "xMax": app_cfg.STOP_ZONE_X_MAX,
                "minAreaRatio": app_cfg.PERSON_MIN_AREA_RATIO
            },
            "timeouts": {
                "driveCommand": app_cfg.DRIVE_COMMAND_TIMEOUT,
                "heartbeat": app_cfg.HEARTBEAT_INTERVAL,
                "connection": app_cfg.CONNECTION_TIMEOUT
            },
            "pairingTtl": app_cfg.PAIRING_CODE_TTL
        }

    # ==================== PAIRING (LEGACY & QR COMPATIBILITY) ====================
    @app.post("/api/v1/pair", response_model=PairResponse)
    async def post_pair(req: PairRequest):
        if not app_cfg.PAIRING_ENABLED:
            return PairResponse(
                success=False,
                robotId=app_cfg.ROBOT_ID,
                robotName=app_cfg.ROBOT_NAME,
                message="Pairing is disabled in configuration"
            )

        is_valid = pairing_manager.validate_code(req.pairCode)
        if is_valid:
            token = auth_manager.create_session_token()
            robot_controller.handle_pairing_success()
            return PairResponse(
                success=True,
                token=token,
                robotId=app_cfg.ROBOT_ID,
                robotName=app_cfg.ROBOT_NAME,
                message="Pairing successful"
            )
        else:
            return PairResponse(
                success=False,
                robotId=app_cfg.ROBOT_ID,
                robotName=app_cfg.ROBOT_NAME,
                message="PAIR_CODE_INVALID or expired"
            )

    @app.delete("/api/v1/session")
    async def delete_session(
        authorization: Optional[str] = Header(None),
        token: Optional[str] = Query(None)
    ):
        req_token = authorization[7:].strip() if authorization and authorization.startswith("Bearer ") else token
        if not req_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="AUTH_REQUIRED: Missing session token")
        auth_manager.revoke_token(req_token)
        robot_controller.auth_service.logout(req_token)
        return {"success": True, "message": "Session revoked"}

    # ==================== DRIVING & EMERGENCY STOPS ====================
    @app.post("/api/v1/emergency-stop")
    async def post_emergency_stop():
        # Public: Anyone (Guest, Staff, Admin) can trigger emergency stop!
        robot_controller.handle_remote_emergency_stop()
        return {"success": True, "state": robot_controller.state.value}

    @app.post("/api/v1/emergency-reset")
    async def post_emergency_reset(
        authorization: Optional[str] = Header(None),
        token: Optional[str] = Query(None)
    ):
        req_token = authorization[7:].strip() if authorization and authorization.startswith("Bearer ") else token
        sess = robot_controller.auth_service.get_session(req_token) if req_token else None
        is_paired = auth_manager.validate_token(req_token) if req_token else False

        if not is_paired and (not sess or sess.role not in ("staff", "admin")):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="AUTH_REQUIRED: Staff, Admin, or Paired device required")

        accepted, reason = robot_controller.handle_remote_emergency_reset()
        if sess:
            robot_controller.auth_service.log_audit(
                user_id=sess.user_id,
                username=sess.username,
                role=sess.role,
                action="EMERGENCY_RESET",
                resource="MOTOR",
                details=f"Result: {accepted}, reason: {reason}"
            )
        return {"success": accepted, "reason": reason, "state": robot_controller.state.value}

    @app.post("/api/v1/control/drive")
    async def post_control_drive(data: Dict[str, Any], session: SessionInfo = Depends(require_staff_or_admin)):
        direction = data.get("direction", "stop")
        speed = float(data.get("speed", app_cfg.DEFAULT_SPEED))
        from src.state import MovementCommand
        cmd_map = {
            "forward": MovementCommand.FORWARD,
            "backward": MovementCommand.BACKWARD,
            "left": MovementCommand.TURN_LEFT,
            "right": MovementCommand.TURN_RIGHT,
            "stop": MovementCommand.STOP,
        }
        cmd = cmd_map.get(direction.lower(), MovementCommand.STOP)
        robot_controller.handle_command(cmd, speed=speed)
        return {"success": True, "command": cmd.value, "speed": speed}

    # ==================== CAMERA STREAMING (STAFF & ADMIN ONLY) ====================
    @app.get("/api/v1/camera/ticket")
    async def get_camera_ticket(
        authorization: Optional[str] = Header(None),
        token: Optional[str] = Query(None)
    ):
        req_token = authorization[7:].strip() if authorization and authorization.startswith("Bearer ") else token
        sess = robot_controller.auth_service.get_session(req_token) if req_token else None
        is_paired = auth_manager.validate_token(req_token) if req_token else False

        if not is_paired and (not sess or sess.role not in ("staff", "admin")):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="AUTH_REQUIRED: Staff or Paired device required")

        ticket = auth_manager.create_stream_ticket(ttl_seconds=app_cfg.STREAM_TICKET_TTL)
        return {"ticket": ticket, "expiresIn": app_cfg.STREAM_TICKET_TTL}

    @app.get("/api/v1/camera/snapshot")
    async def get_camera_snapshot(
        authorization: Optional[str] = Header(None),
        token: Optional[str] = Query(None),
        ticket: Optional[str] = Query(None)
    ):
        req_token = authorization[7:].strip() if authorization and authorization.startswith("Bearer ") else token
        auth_ok = False
        if ticket and auth_manager.validate_stream_ticket(ticket):
            auth_ok = True
        elif req_token:
            sess = robot_controller.auth_service.get_session(req_token)
            if sess and sess.role in ("staff", "admin"):
                auth_ok = True
            elif auth_manager.validate_token(req_token):
                auth_ok = True

        if not auth_ok:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="AUTH_REQUIRED")

        jpeg_bytes = camera_stream.get_snapshot()
        return Response(content=jpeg_bytes, media_type="image/jpeg")

    @app.get("/api/v1/camera/mjpeg")
    async def get_camera_mjpeg(
        authorization: Optional[str] = Header(None),
        token: Optional[str] = Query(None),
        ticket: Optional[str] = Query(None)
    ):
        req_token = authorization[7:].strip() if authorization and authorization.startswith("Bearer ") else token
        # Validate ticket OR check staff/admin session token
        auth_ok = False
        if ticket and auth_manager.validate_stream_ticket(ticket):
            auth_ok = True
        elif req_token:
            sess = robot_controller.auth_service.get_session(req_token)
            if sess and sess.role in ("staff", "admin"):
                auth_ok = True
            elif auth_manager.validate_token(req_token):
                auth_ok = True

        if not auth_ok:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="FORBIDDEN: Camera live stream requires Staff or Admin privileges"
            )

        return StreamingResponse(
            camera_stream.generate_mjpeg_stream(),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )

    # ==================== MALL ENTITIES: FLOORS & STORES ====================
    @app.get("/api/v1/mall/floors")
    async def get_floors():
        return {"floors": robot_controller.mall.get_floors()}

    @app.get("/api/v1/mall/stores")
    async def get_stores():
        return {"stores": robot_controller.mall.get_stores()}

    @app.patch("/api/v1/mall/stores/{store_id}")
    async def patch_store(store_id: str, data: Dict[str, Any], session: SessionInfo = Depends(require_staff_or_admin)):
        if not check_store_access(session, store_id):
            raise HTTPException(status_code=403, detail="FORBIDDEN: You cannot edit another store's details")
        ok = robot_controller.mall.update_store(store_id, data)
        return {"success": ok}

    @app.get("/api/v1/mall/pois")
    async def get_mall_pois(include_staff: bool = Query(False)):
        return {"pois": robot_controller.mall.get_pois(include_staff=include_staff)}

    # ==================== PROMOTIONS (STORE-SCOPED RBAC) ====================
    @app.get("/api/v1/mall/promotions")
    async def get_promotions(store_id: Optional[str] = Query(None), active_only: bool = Query(True)):
        return {"promotions": robot_controller.mall.get_promotions(store_id=store_id, active_only=active_only)}

    @app.post("/api/v1/mall/promotions")
    async def create_promotion(data: Dict[str, Any], session: SessionInfo = Depends(require_staff_or_admin)):
        store_id = data.get("storeId", "")
        if not store_id:
            raise HTTPException(status_code=400, detail="Missing storeId")
        try:
            promo = robot_controller.mall.create_promotion(
                store_id=store_id,
                title=data.get("title", ""),
                description=data.get("description", ""),
                discount_percent=data.get("discountPercent"),
                promo_code=data.get("promoCode"),
                banner_url=data.get("bannerUrl"),
                start_time=float(data.get("startTime", time.time())),
                end_time=float(data.get("endTime", time.time() + 86400 * 30)),
                session=session
            )
            return {"success": True, "promotion": promo}
        except PermissionError as e:
            raise HTTPException(status_code=403, detail=str(e))

    @app.patch("/api/v1/mall/promotions/{promo_id}")
    async def update_promotion(promo_id: str, data: Dict[str, Any], session: SessionInfo = Depends(require_staff_or_admin)):
        try:
            ok = robot_controller.mall.update_promotion(promo_id, data, session)
            return {"success": ok}
        except PermissionError as e:
            raise HTTPException(status_code=403, detail=str(e))

    @app.delete("/api/v1/mall/promotions/{promo_id}")
    async def delete_promotion(promo_id: str, session: SessionInfo = Depends(require_staff_or_admin)):
        try:
            ok = robot_controller.mall.delete_promotion(promo_id, session)
            return {"success": ok}
        except PermissionError as e:
            raise HTTPException(status_code=403, detail=str(e))

    # ==================== NAVIGATION GRAPH & PATHFINDING ====================
    @app.get("/api/v1/mall/map/graph")
    async def get_navigation_graph():
        nodes = [{"id": n.id, "floorId": n.floor_id, "name": n.name, "x": n.x, "y": n.y, "nodeType": n.node_type} for n in robot_controller.navigator.graph.nodes.values()]
        edges = [{"id": e.id, "floorId": e.floor_id, "nodeA": e.node_a, "nodeB": e.node_b, "distanceM": e.distance_m, "isBidirectional": e.is_bidirectional, "isBlocked": e.is_blocked} for e in robot_controller.navigator.graph.edges.values()]
        zones = [{"id": z.id, "floorId": z.floor_id, "name": z.name, "xMin": z.x_min, "yMin": z.y_min, "xMax": z.x_max, "yMax": z.y_max} for z in robot_controller.navigator.graph.restricted_zones]
        return {
            "nodes": nodes,
            "edges": edges,
            "restrictedZones": zones,
            "patrol": robot_controller.navigator.patrol.get_status()
        }

    @app.get("/api/v1/mall/navigation/status")
    async def get_navigation_status():
        return {"navigation": robot_controller.navigator.get_snapshot()}

    @app.post("/api/v1/mall/navigation/cancel")
    async def cancel_active_navigation():
        robot_controller.navigator.cancel_navigation()
        robot_controller.mall.cancel_escort()
        return {"success": True}

    # ==================== ESCORT & DELIVERY MISSIONS ====================
    @app.post("/api/v1/mall/escort")
    async def request_escort_navigation(data: Dict[str, Any]):
        poi_id = data.get("targetPoiId")
        if not poi_id:
            raise HTTPException(status_code=400, detail="Missing targetPoiId")
        task = robot_controller.mall.request_escort(poi_id)
        if not task:
            raise HTTPException(status_code=404, detail="Target POI not found")

        # Plan physical A* navigation mission to POI
        robot_controller.navigator.plan_mission_to_poi(task.target_poi_id, task.target_name, task.target_x, task.target_y)
        robot_controller.log_event(f"Customer escort started to {task.target_name}")
        return {"success": True, "task": task.__dict__}

    @app.delete("/api/v1/mall/escort")
    async def cancel_escort_navigation():
        ok = robot_controller.mall.cancel_escort()
        robot_controller.navigator.cancel_navigation()
        robot_controller.log_event("Customer escort cancelled")
        return {"success": ok}

    @app.get("/api/v1/mall/escort")
    async def get_escort_status():
        return {"task": robot_controller.mall.get_escort_status()}

    @app.get("/api/v1/mall/delivery/orders")
    async def get_delivery_orders():
        return {"orders": robot_controller.mall.get_orders()}

    @app.post("/api/v1/mall/delivery/orders")
    async def create_delivery_order(data: Dict[str, Any], session: Optional[SessionInfo] = Depends(get_current_session)):
        creator = data.get("creatorName", session.full_name if session else "Nhân viên")
        pickup = data.get("pickupPoiId", "")
        dropoff = data.get("dropoffPoiId", "")
        desc = data.get("itemDescription", "Hàng hóa nội bộ")
        if not pickup or not dropoff:
            raise HTTPException(status_code=400, detail="Missing pickup or dropoff POI ID")
        order = robot_controller.mall.create_delivery_order(creator, pickup, dropoff, desc, creator_user_id=session.user_id if session else None)
        robot_controller.log_event(f"New delivery order created: {order.order_id}")
        return {"success": True, "order": order.__dict__}

    @app.patch("/api/v1/mall/delivery/orders/{order_id}")
    async def update_delivery_order_status(order_id: str, data: Dict[str, Any]):
        status_val = data.get("status")
        progress_val = data.get("progress")
        if not status_val:
            raise HTTPException(status_code=400, detail="Missing status")
        ok = robot_controller.mall.update_order_status(order_id, status_val, progress_val)
        if not ok:
            raise HTTPException(status_code=404, detail="Order not found")
        robot_controller.log_event(f"Order {order_id} status updated to {status_val}")
        return {"success": True}

    # ==================== AI CONCIERGE (OPENROUTER GROUNDED ASSISTANT) ====================
    @app.post("/api/v1/mall/ai/ask")
    async def ask_mall_assistant(data: Dict[str, Any], session: Optional[SessionInfo] = Depends(get_current_session)):
        question = data.get("question", "")
        if not question:
            raise HTTPException(status_code=400, detail="Missing question")
        role = session.role if session else "guest"
        store_ids = session.assigned_store_ids if session else None
        res = await robot_controller.ai_assistant.ask(question, role=role, store_ids=store_ids)
        return res

    # ==================== WEBSOCKET CONTROL ENDPOINT ====================
    @app.websocket("/ws/v1/control")
    async def websocket_control_endpoint(websocket: WebSocket, token: Optional[str] = Query(None)):
        auth_header = websocket.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()

        connected = await websocket_manager.connect(websocket, token)
        if not connected:
            return

        try:
            while True:
                data_text = await websocket.receive_text()
                await websocket_manager.handle_message(websocket, data_text)
        except WebSocketDisconnect:
            await websocket_manager.disconnect(websocket)
        except Exception as e:
            logger.warning(f"WebSocket error: {e}")
            await websocket_manager.disconnect(websocket)

    # ==================== STATIC SPA FRONTEND SERVING ====================
    dist_dir = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

    @app.get("/", response_class=HTMLResponse)
    async def serve_index():
        if dist_dir.exists() and (dist_dir / "index.html").exists():
            with open(dist_dir / "index.html", "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        return HTMLResponse(content="<h1>PI ROBOT Central Command</h1><p>Run 'npm run build' in frontend/ to generate UI.</p>")

    @app.get("/{file_path:path}")
    async def serve_static_file(file_path: str):
        if not file_path or file_path.startswith("api/") or file_path.startswith("ws/"):
            raise HTTPException(status_code=404, detail="Not Found")

        if dist_dir.exists():
            target_path = (dist_dir / file_path).resolve()
            if target_path.is_file() and str(target_path).startswith(str(dist_dir.resolve())):
                mime_type, _ = mimetypes.guess_type(str(target_path))
                with open(target_path, "rb") as f:
                    return Response(content=f.read(), media_type=mime_type or "application/octet-stream")

            # SPA fallback: return index.html for client-side routing
            index_path = dist_dir / "index.html"
            if index_path.exists():
                with open(index_path, "r", encoding="utf-8") as f:
                    return HTMLResponse(content=f.read())

        raise HTTPException(status_code=404, detail="File Not Found")

    return app
