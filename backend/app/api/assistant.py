"""AI doubt-assistant. Uses an OpenAI-compatible LLM if a key is configured,
otherwise a built-in offline tutor that answers from the problem's own
teaching content (works with zero API key / zero cost)."""
from fastapi import APIRouter, Depends
from ..models.schemas import AssistantIn, AssistantOut
from ..core import store
from ..core.config import get_settings
from .deps import get_current_user

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


def _offline_answer(q: str, problem: dict | None) -> str:
    ql = q.lower()
    if problem:
        parts = [f"**{problem['title']}** — {problem['patternName']} ({problem['ds']})."]
        if problem.get("quickshot"):
            parts.append("⚡ Quick-shot: " + problem["quickshot"])
        if any(w in ql for w in ("complexity", "big o", "time", "space")) and problem.get("approaches"):
            for a in problem["approaches"]:
                parts.append(f"• {a['name']}: {a['bigO']}")
        if any(w in ql for w in ("hint", "stuck", "start", "how", "approach", "idea")) and problem.get("approaches"):
            opt = problem["approaches"][-1]
            parts.append("🧩 Optimal idea: " + opt["idea"])
            parts.append("Steps: " + " ".join(f"{i+1}) {s}" for i, s in enumerate(opt["steps"])))
        parts.append("🔗 Practice: " + problem["links"]["leetcode"])
        return "\n\n".join(parts)
    # generic
    tips = {
        "sliding window": "Sliding window: grow the right edge; shrink the left when a constraint breaks. Great for longest/shortest contiguous runs.",
        "two pointer": "On sorted data, converge from both ends; move the pointer that steps toward the target.",
        "binary search": "Sorted + a monotonic yes/no → halve the range each step. Watch your lo/mid/hi invariant.",
        "backtracking": "Choose → explore → un-choose. Prune branches that can't succeed.",
        "dp": "Define the state, the transition, and the base case. Start 1-D, then 2-D.",
        "recursion": "Trust the recursion: handle the base case, combine child results.",
    }
    for k, v in tips.items():
        if k in ql:
            return f"💡 {v}"
    return ("I'm your DSA tutor. Ask me about a pattern (sliding window, two pointers, "
            "binary search, DP, backtracking…) or open a problem and ask 'how do I start?'.")


def _llm_answer(q: str, problem: dict | None, s) -> str | None:
    try:
        import urllib.request, json
        ctx = ""
        if problem:
            ctx = f"Problem: {problem['title']} ({problem['patternName']}). Quick-shot: {problem.get('quickshot','')}."
        body = {
            "model": s.openai_model,
            "messages": [
                {"role": "system", "content": "You are a patient DSA tutor for a beginner who codes in Java. Be concise, teach the pattern, never dump full solutions unless asked."},
                {"role": "user", "content": f"{ctx}\n\nQuestion: {q}"},
            ],
            "temperature": 0.3,
        }
        req = urllib.request.Request(
            s.openai_base_url.rstrip("/") + "/chat/completions",
            data=json.dumps(body).encode(),
            headers={"Authorization": f"Bearer {s.openai_api_key}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
        return data["choices"][0]["message"]["content"]
    except Exception:
        return None


@router.post("", response_model=AssistantOut)
def ask(body: AssistantIn, user: dict = Depends(get_current_user)):
    s = get_settings()
    problem = store.problem_by_id(body.problem_id) if body.problem_id else None
    if s.openai_api_key:
        ans = _llm_answer(body.question, problem, s)
        if ans:
            return AssistantOut(answer=ans, source="llm")
    return AssistantOut(answer=_offline_answer(body.question, problem), source="offline-tutor")
