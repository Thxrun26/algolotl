"""Problem catalog + the two Notion views (by pattern, by data structure)."""
from fastapi import APIRouter, HTTPException
from ..core import store

router = APIRouter(prefix="/api", tags=["problems"])


@router.get("/catalog")
def catalog():
    """Full dataset: problems, patterns, ds groups, 30-day meta."""
    return store.load_catalog()


@router.get("/problems")
def problems(pattern: str | None = None, ds: str | None = None,
             difficulty: str | None = None, day: int | None = None):
    items = store.load_catalog()["problems"]
    if pattern: items = [p for p in items if p["pattern"] == pattern]
    if ds: items = [p for p in items if p["ds"] == ds]
    if difficulty: items = [p for p in items if p["difficulty"] == difficulty]
    if day: items = [p for p in items if p["day"] == day]
    return {"count": len(items), "problems": items}


@router.get("/problems/{pid}")
def problem(pid: str):
    p = store.problem_by_id(pid)
    if not p:
        raise HTTPException(404, "Problem not found")
    return p


@router.get("/notion/patterns")
def notion_patterns():
    data = store.load_catalog()
    by_id = {p["id"]: p for p in data["problems"]}
    return {k: {"name": v["name"], "problems": [by_id[i] for i in v["ids"]]}
            for k, v in data["patterns"].items()}


@router.get("/notion/ds")
def notion_ds():
    data = store.load_catalog()
    by_id = {p["id"]: p for p in data["problems"]}
    return {k: {"name": v["name"], "problems": [by_id[i] for i in v["ids"]]}
            for k, v in data["ds"].items()}
