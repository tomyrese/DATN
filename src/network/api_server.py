import os
import socket
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, Header, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response, JSONResponse
from src.config import RobotConfig, config
from src.network.protocol import (
    PairRequest, PairResponse, HealthResponse, InfoResponse, TelemetryMessage
)
from src.network.auth_manager import AuthManager
from src.network.pairing_manager import PairingManager
from src.network.websocket_manager import WebSocketManager
from src.network.camera_stream import CameraStreamManager
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
    app = FastAPI(title="Pi Robot Server", version="1.0.0", docs_url="/docs", redoc_url=None)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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
            serverVersion="1.0.0",
            paired=auth_manager.has_paired_clients()
        )

    @app.get("/api/v1/status")
    async def get_status():
        return robot_controller.get_telemetry_snapshot()

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

    @app.post("/api/v1/emergency-stop")
    async def post_emergency_stop():
        robot_controller.handle_remote_emergency_stop()
        return {"success": True, "state": robot_controller.state.value}

    @app.post("/api/v1/control/drive")
    async def post_control_drive(data: Dict[str, Any]):
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

    @app.post("/api/v1/emergency-reset")
    async def post_emergency_reset(token: str = Depends(verify_auth_token)):
        accepted, reason = robot_controller.handle_remote_emergency_reset()
        return {"success": accepted, "reason": reason, "state": robot_controller.state.value}

    @app.get("/api/v1/camera/ticket")
    async def get_camera_ticket(token: str = Depends(verify_auth_token)):
        ticket = auth_manager.create_stream_ticket(ttl_seconds=app_cfg.STREAM_TICKET_TTL)
        return {"ticket": ticket, "expiresIn": app_cfg.STREAM_TICKET_TTL}

    @app.get("/api/v1/camera/snapshot")
    async def get_camera_snapshot(
        authorization: Optional[str] = Header(None),
        token: Optional[str] = Query(None),
        ticket: Optional[str] = Query(None)
    ):
        req_token = authorization[7:].strip() if authorization and authorization.startswith("Bearer ") else token
        auth_ok = auth_manager.validate_token(req_token) or auth_manager.validate_stream_ticket(ticket)
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
        auth_ok = auth_manager.validate_token(req_token) or auth_manager.validate_stream_ticket(ticket)
        if not auth_ok:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="AUTH_REQUIRED")

        return StreamingResponse(
            camera_stream.generate_mjpeg_stream(),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )

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

    @app.get("/api/v1/logs/recent")
    async def get_recent_logs(token: str = Depends(verify_auth_token)):
        return {"logs": robot_controller.get_recent_logs()}

    @app.delete("/api/v1/session")
    async def delete_session(token: str = Depends(verify_auth_token)):
        auth_manager.revoke_token(token)
        return {"success": True, "message": "Session revoked"}

    # ==================== MALL & NAVIGATION APIS ====================
    @app.get("/api/v1/mall/pois")
    async def get_mall_pois(include_staff: bool = Query(False)):
        return {"pois": robot_controller.mall.get_pois(include_staff=include_staff)}

    @app.get("/api/v1/mall/delivery/orders")
    async def get_delivery_orders():
        return {"orders": robot_controller.mall.get_orders()}

    @app.post("/api/v1/mall/delivery/orders")
    async def create_delivery_order(data: Dict[str, Any]):
        creator = data.get("creatorName", "Nhân viên")
        pickup = data.get("pickupPoiId", "")
        dropoff = data.get("dropoffPoiId", "")
        desc = data.get("itemDescription", "Hàng hóa nội bộ")
        if not pickup or not dropoff:
            raise HTTPException(status_code=400, detail="Missing pickup or dropoff POI ID")
        order = robot_controller.mall.create_delivery_order(creator, pickup, dropoff, desc)
        robot_controller.log_event(f"New delivery order created: {order.order_id} ({order.pickup_poi_name} -> {order.dropoff_poi_name})")
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

    @app.post("/api/v1/mall/escort")
    async def request_escort_navigation(data: Dict[str, Any]):
        poi_id = data.get("targetPoiId")
        if not poi_id:
            raise HTTPException(status_code=400, detail="Missing targetPoiId")
        task = robot_controller.mall.request_escort(poi_id)
        if not task:
            raise HTTPException(status_code=404, detail="Target POI not found")
        robot_controller.log_event(f"Customer escort started to {task.target_name} ({task.target_floor})")
        return {"success": True, "task": task.__dict__}

    @app.delete("/api/v1/mall/escort")
    async def cancel_escort_navigation():
        ok = robot_controller.mall.cancel_escort()
        robot_controller.log_event("Customer escort cancelled")
        return {"success": ok}

    @app.get("/api/v1/mall/escort")
    async def get_escort_status():
        return {"task": robot_controller.mall.get_escort_status()}

    @app.post("/api/v1/mall/ai/ask")
    async def ask_mall_assistant(data: Dict[str, Any]):
        question = data.get("question", "")
        if not question:
            raise HTTPException(status_code=400, detail="Missing question")
        res = robot_controller.mall.ask_concierge(question)
        return res

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

    import mimetypes
    from pathlib import Path
    from fastapi.responses import HTMLResponse

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

