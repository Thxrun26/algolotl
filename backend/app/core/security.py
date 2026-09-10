"""
Security primitives with ZERO external deps (stdlib only):
  - PBKDF2-HMAC-SHA256 password hashing (per-user salt, 200k iterations)
  - Compact HS256 JWTs (sign/verify) with expiry
  - Constant-time comparisons everywhere
This avoids vulnerable/unmaintained crypto libs and is easy to audit.
"""
import base64, hashlib, hmac, json, os, time
from typing import Optional

_PBKDF2_ROUNDS = 200_000


# ---------- base64url helpers ----------
def _b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64d(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


# ---------- password hashing ----------
def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _PBKDF2_ROUNDS)
    return f"pbkdf2_sha256${_PBKDF2_ROUNDS}${_b64e(salt)}${_b64e(dk)}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, rounds, salt_b64, hash_b64 = stored.split("$")
        if algo != "pbkdf2_sha256":
            return False
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), _b64d(salt_b64), int(rounds))
        return hmac.compare_digest(dk, _b64d(hash_b64))
    except Exception:
        return False


# ---------- JWT (HS256) ----------
def create_token(sub: str, secret: str, ttl_seconds: int, extra: Optional[dict] = None) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {"sub": sub, "iat": now, "exp": now + ttl_seconds}
    if extra:
        payload.update(extra)
    seg = _b64e(json.dumps(header, separators=(",", ":")).encode()) + "." + \
          _b64e(json.dumps(payload, separators=(",", ":")).encode())
    sig = hmac.new(secret.encode(), seg.encode(), hashlib.sha256).digest()
    return seg + "." + _b64e(sig)


def verify_token(token: str, secret: str) -> Optional[dict]:
    try:
        header_b64, payload_b64, sig_b64 = token.split(".")
        seg = f"{header_b64}.{payload_b64}"
        expected = hmac.new(secret.encode(), seg.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _b64d(sig_b64)):
            return None
        payload = json.loads(_b64d(payload_b64))
        if payload.get("exp", 0) < int(time.time()):
            return None
        return payload
    except Exception:
        return None
