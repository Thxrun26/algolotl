"""
Tiny thread-safe JSON store for users + progress. Zero-DB so it deploys
anywhere; the interface is swappable for MongoDB/Postgres later without
touching the API layer. Also loads the generated problems catalog.
"""
import json, os, threading, uuid
from typing import Optional
from .config import get_settings

_lock = threading.RLock()
_HERE = os.path.dirname(__file__)
_DATA_JSON = os.path.abspath(os.path.join(_HERE, "..", "data", "problems.json"))


# ---------------- problems catalog (read-only) ----------------
_catalog_cache = None


def load_catalog() -> dict:
    global _catalog_cache
    if _catalog_cache is None:
        with open(_DATA_JSON) as f:
            _catalog_cache = json.load(f)
    return _catalog_cache


def problem_by_id(pid: str) -> Optional[dict]:
    for p in load_catalog()["problems"]:
        if p["id"] == pid:
            return p
    return None


# ---------------- user + progress store (read/write) ----------------
def _store_path() -> str:
    d = get_settings().data_dir
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "db.json")


def _read() -> dict:
    p = _store_path()
    if not os.path.exists(p):
        return {"users": {}, "progress": {}, "revision": {}}
    with open(p) as f:
        return json.load(f)


def _write(db: dict) -> None:
    p = _store_path()
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump(db, f)
    os.replace(tmp, p)  # atomic


# users -------------------------------------------------
def get_user_by_email(email: str) -> Optional[dict]:
    with _lock:
        db = _read()
        for u in db["users"].values():
            if u["email"].lower() == email.lower():
                return u
        return None


def get_user(uid: str) -> Optional[dict]:
    with _lock:
        return _read()["users"].get(uid)


def create_user(email: str, name: str, password_hash: Optional[str], provider: str = "local") -> dict:
    with _lock:
        db = _read()
        uid = uuid.uuid4().hex
        user = {"id": uid, "email": email, "name": name,
                "password_hash": password_hash, "provider": provider}
        db["users"][uid] = user
        _write(db)
        return user


# progress ---------------------------------------------
def set_status(uid: str, pid: str, status: str, note: str = "") -> dict:
    with _lock:
        db = _read()
        up = db["progress"].setdefault(uid, {})
        up[pid] = {"status": status, "note": note, "ts": int(__import__("time").time())}
        _write(db)
        return up[pid]


def get_progress(uid: str) -> dict:
    with _lock:
        return _read()["progress"].get(uid, {})


def set_revision(uid: str, pid: str, on: bool) -> None:
    with _lock:
        db = _read()
        rev = db["revision"].setdefault(uid, {})
        if on:
            rev[pid] = int(__import__("time").time())
        else:
            rev.pop(pid, None)
        _write(db)


def get_revision(uid: str) -> dict:
    with _lock:
        return _read()["revision"].get(uid, {})
