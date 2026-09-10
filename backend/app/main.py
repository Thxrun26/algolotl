"""
Algolotl API — FastAPI app.
Mounts the static frontend, wires routers, adds security headers + CORS,
health checks, and serves auto OpenAPI docs at /docs and /redoc.
"""
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from .core.config import get_settings
from .core import store
from .api import auth, problems, progress, assistant

settings = get_settings()

app = FastAPI(
    title="Algolotl API",
    version="1.0.0",
    description="Pattern-first DSA learning platform — solve 120–150 problems in 30 days.",
)

# ---- CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- security headers ----
@app.middleware("http")
async def security_headers(request: Request, call_next):
    resp = await call_next(request)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    resp.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    if settings.is_prod:
        resp.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    return resp


# ---- routers ----
app.include_router(auth.router)
app.include_router(problems.router)
app.include_router(progress.router)
app.include_router(assistant.router)


# ---- health ----
@app.get("/api/health/live", tags=["health"])
def live():
    return {"status": "ok", "service": "algolotl"}


@app.get("/api/health/ready", tags=["health"])
def ready():
    try:
        n = len(store.load_catalog()["problems"])
        return {"status": "ok", "problems": n}
    except Exception as e:  # pragma: no cover
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=503)


# ---- static frontend ----
_WEB = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "web"))
if os.path.isdir(_WEB):
    app.mount("/static", StaticFiles(directory=_WEB), name="static")

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(os.path.join(_WEB, "index.html"))

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        # serve real files, else fall back to SPA shell (hash routing)
        candidate = os.path.join(_WEB, path)
        if path and os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(os.path.join(_WEB, "index.html"))
