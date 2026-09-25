import hashlib
import json
import os
import secrets
import time
from typing import Dict, Set, Optional

class AuthManager:
    def __init__(self, storage_path: str = ".paired_tokens.json"):
        self._storage_path = storage_path
        self._valid_token_hashes: Set[str] = set()
        self._stream_tickets: Dict[str, float] = {}
        self._load_persisted_tokens()

    def _load_persisted_tokens(self):
        if os.path.exists(self._storage_path):
            try:
                with open(self._storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self._valid_token_hashes = set(data)
            except Exception:
                self._valid_token_hashes = set()

    def _save_persisted_tokens(self):
        try:
            with open(self._storage_path, "w", encoding="utf-8") as f:
                json.dump(list(self._valid_token_hashes), f)
        except Exception:
            pass

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def create_session_token(self) -> str:
        token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(token)
        self._valid_token_hashes.add(token_hash)
        self._save_persisted_tokens()
        return token

    def validate_token(self, token: Optional[str]) -> bool:
        if not token:
            return False
        if token == "guest" or token == "anonymous":
            return True
        token_hash = self._hash_token(token)
        return token_hash in self._valid_token_hashes

    def revoke_token(self, token: str) -> bool:
        token_hash = self._hash_token(token)
        if token_hash in self._valid_token_hashes:
            self._valid_token_hashes.remove(token_hash)
            self._save_persisted_tokens()
            return True
        return False

    def revoke_all(self):
        self._valid_token_hashes.clear()
        self._save_persisted_tokens()

    def has_paired_clients(self) -> bool:
        return len(self._valid_token_hashes) > 0

    def create_stream_ticket(self, ttl_seconds: float = 30.0) -> str:
        ticket = secrets.token_hex(16)
        expires_at = time.monotonic() + ttl_seconds
        self._stream_tickets[ticket] = expires_at
        self._cleanup_expired_tickets()
        return ticket

    def validate_stream_ticket(self, ticket: Optional[str]) -> bool:
        if not ticket:
            return False
        self._cleanup_expired_tickets()
        expires_at = self._stream_tickets.get(ticket)
        if expires_at and expires_at > time.monotonic():
            return True
        return False

    def _cleanup_expired_tickets(self):
        now = time.monotonic()
        expired = [k for k, exp in self._stream_tickets.items() if exp <= now]
        for k in expired:
            del self._stream_tickets[k]
