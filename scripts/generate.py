"""
Assemble the dataset: catalog (150) + flagship rich visualizers.
Emit:
  - backend/app/data/problems.json   (backend reads this)
  - web/data/problems.js             (frontend embeds window.ALGO)
Validates: unique ids, valid difficulty, flagship frames non-empty, day range.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from catalog import CATALOG, PATTERN_TO_DS, PATTERN_NAME, assign_days
from flagship import build_flagship

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, ".."))

DAY_META = {
    1: "Arrays & Hashing · Big-O", 2: "Hashing & Grouping", 3: "Prefix / Product",
    4: "Two Pointers", 5: "Two Pointers · Hard", 6: "Sliding Window",
    7: "🔁 Week 1 Review", 8: "Stack", 9: "Monotonic Stack", 10: "Binary Search",
    11: "Search on Answer", 12: "Linked List", 13: "Fast/Slow · Cycle",
    14: "🔁 Week 2 Review", 15: "Trees · DFS", 16: "Tree Properties",
    17: "Tree BFS", 18: "BST", 19: "Tries & Heap", 20: "Backtracking",
    21: "🔁 Week 3 Review", 22: "Graphs · Grid", 23: "Graphs · Topo",
    24: "Advanced Graphs", 25: "1-D DP", 26: "2-D DP", 27: "Greedy & Intervals",
    28: "🔁 Weak-Area Repair", 29: "🔁 Mock Interview", 30: "🎓 Final Assessment",
}


def clean_title(t):
    return t


def build():
    flagship = build_flagship()
    rows = assign_days(CATALOG)
    ids = set()
    problems = []
    for slug, title, diff, pattern, day in rows:
        assert slug not in ids, f"duplicate slug {slug}"
        assert diff in ("Easy", "Medium", "Hard"), f"bad difficulty {diff}"
        assert 1 <= day <= 30
        ids.add(slug)
        rich = flagship.get(slug)
        problems.append({
            "id": slug,
            "title": title,
            "difficulty": diff,
            "pattern": pattern,
            "patternName": PATTERN_NAME[pattern],
            "ds": PATTERN_TO_DS[pattern],
            "day": day,
            "links": {
                "leetcode": f"https://leetcode.com/problems/{slug}/",
                "neetcode": "https://neetcode.io/roadmap",
                "striver": "https://takeuforward.org/strivers-a2z-dsa-course/strivers-a2z-dsa-course-sheet-2/",
                "cci": "Cracking the Coding Interview",
            },
            "quickshot": rich["quickshot"] if rich else None,
            "dsExplainer": rich["dsExplainer"] if rich else None,
            "approaches": rich["approaches"] if rich else None,
            "hasViz": bool(rich),
        })

    # validate flagship frames
    flag_count = 0
    for p in problems:
        if p["approaches"]:
            flag_count += 1
            for a in p["approaches"]:
                assert a["frames"], f"{p['id']} approach {a['key']} has no frames"
                for f in a["frames"]:
                    assert "what" in f and "why" in f and "line" in f

    # patterns + ds groupings for the two Notion views
    patterns = {}
    ds_groups = {}
    for p in problems:
        patterns.setdefault(p["pattern"], {"name": p["patternName"], "ids": []})["ids"].append(p["id"])
        ds_groups.setdefault(p["ds"], {"name": p["ds"], "ids": []})["ids"].append(p["id"])

    days = [{"day": d, "topic": DAY_META.get(d, ""), "review": d in {7, 14, 21, 28, 29, 30}} for d in range(1, 31)]

    data = {
        "meta": {"name": "Algolotl", "total": len(problems), "flagship": flag_count, "days": 30},
        "problems": problems,
        "patterns": patterns,
        "ds": ds_groups,
        "dayMeta": days,
    }

    os.makedirs(os.path.join(ROOT, "backend/app/data"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "web/data"), exist_ok=True)
    with open(os.path.join(ROOT, "backend/app/data/problems.json"), "w") as f:
        json.dump(data, f)
    with open(os.path.join(ROOT, "web/data/problems.js"), "w") as f:
        f.write("window.ALGO = " + json.dumps(data) + ";\n")

    print(f"✓ {len(problems)} problems | {flag_count} flagship visualizers | "
          f"{len(patterns)} patterns | {len(ds_groups)} DS groups")
    # quick day distribution
    from collections import Counter
    dist = Counter(p["day"] for p in problems)
    print("  day spread:", dict(sorted(dist.items())))


if __name__ == "__main__":
    build()
