"""Live progress tracking + daily revision queue (previous day's hard problems)."""
from fastapi import APIRouter, Depends
from ..models.schemas import StatusIn, RevisionIn
from ..core import store
from .deps import get_current_user

router = APIRouter(prefix="/api/progress", tags=["progress"])

SOLVED = {"Solved Solo", "Solved w/ Hint"}


@router.get("")
def my_progress(user: dict = Depends(get_current_user)):
    prog = store.get_progress(user["id"])
    rev = store.get_revision(user["id"])
    solved = sum(1 for v in prog.values() if v["status"] in SOLVED)
    return {"progress": prog, "revision": list(rev.keys()),
            "stats": {"solved": solved, "tracked": len(prog), "revisionCount": len(rev)}}


@router.post("/status")
def set_status(body: StatusIn, user: dict = Depends(get_current_user)):
    # "Needs Revision" auto-adds to the revision queue.
    entry = store.set_status(user["id"], body.problem_id, body.status, body.note)
    if body.status == "Needs Revision":
        store.set_revision(user["id"], body.problem_id, True)
    return {"ok": True, "entry": entry}


@router.post("/revision")
def toggle_revision(body: RevisionIn, user: dict = Depends(get_current_user)):
    store.set_revision(user["id"], body.problem_id, body.on)
    return {"ok": True}


@router.get("/revision/today")
def revision_today(user: dict = Depends(get_current_user)):
    """The daily revision: problems flagged 'Needs Revision' / harder ones,
    newest first, so you revisit yesterday's tough ones before new work."""
    rev = store.get_revision(user["id"])
    by_id = {p["id"]: p for p in store.load_catalog()["problems"]}
    items = sorted(rev.items(), key=lambda kv: kv[1], reverse=True)
    return {"count": len(items),
            "problems": [by_id[pid] for pid, _ in items if pid in by_id]}
