from typing import Optional, List
from fastapi import Header, Query, HTTPException, status, Depends
from src.security.auth_service import AuthService, SessionInfo

_auth_service: Optional[AuthService] = None

def get_auth_service() -> AuthService:
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service

def extract_token(authorization: Optional[str] = Header(None), token: Optional[str] = Query(None)) -> Optional[str]:
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:].strip()
    if token:
        return token.strip()
    return None

def get_current_session(
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[SessionInfo]:
    req_token = extract_token(authorization, token)
    if not req_token:
        return None
    return auth_service.get_session(req_token)

def require_authenticated(
    session: Optional[SessionInfo] = Depends(get_current_session)
) -> SessionInfo:
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="AUTH_REQUIRED: Please log in to access this resource"
        )
    return session

def require_admin(
    session: SessionInfo = Depends(require_authenticated)
) -> SessionInfo:
    if session.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="FORBIDDEN: Admin privileges required"
        )
    return session

def require_staff_or_admin(
    session: SessionInfo = Depends(require_authenticated)
) -> SessionInfo:
    if session.role not in ("staff", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="FORBIDDEN: Staff or Admin privileges required"
        )
    return session

def check_store_access(session: SessionInfo, store_id: str) -> bool:
    """
    Validates whether the user has access to operate on the given store:
    - Admin: Always has access to all stores.
    - Staff: Only has access if store_id is in their assigned_store_ids list.
    - Guest: False.
    """
    if session.role == "admin":
        return True
    if session.role == "staff":
        return store_id in session.assigned_store_ids
    return False

def require_store_access(store_id: str, session: SessionInfo = Depends(require_staff_or_admin)) -> SessionInfo:
    if not check_store_access(session, store_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"FORBIDDEN: You do not have permission to manage store '{store_id}'"
        )
    return session
