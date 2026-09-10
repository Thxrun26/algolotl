"""Auth: register, login, me. Local (email+password) with JWT.
Google OAuth path documented in README (needs client credentials)."""
from fastapi import APIRouter, HTTPException, status, Depends
from ..models.schemas import RegisterIn, LoginIn, TokenOut, UserOut
from ..core import store
from ..core.config import get_settings
from ..core.security import hash_password, verify_password, create_token
from .deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _issue(user: dict) -> TokenOut:
    s = get_settings()
    token = create_token(user["id"], s.secret_key, s.access_token_ttl_min * 60)
    return TokenOut(access_token=token, user=UserOut(**user))


@router.post("/register", response_model=TokenOut, status_code=201)
def register(body: RegisterIn):
    if store.get_user_by_email(body.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    user = store.create_user(body.email, body.name, hash_password(body.password))
    return _issue(user)


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn):
    user = store.get_user_by_email(body.email)
    if not user or not user.get("password_hash") or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    return _issue(user)


@router.get("/me", response_model=UserOut)
def me(user: dict = Depends(get_current_user)):
    return UserOut(**user)


@router.post("/demo", response_model=TokenOut)
def demo_login():
    """One-click demo account so anyone can try the platform instantly."""
    email = "demo@algolotl.dev"
    user = store.get_user_by_email(email) or store.create_user(email, "Demo Learner", None, provider="demo")
    return _issue(user)
