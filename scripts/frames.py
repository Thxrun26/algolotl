"""
Frame SIMULATORS — run the real algorithm and record each step as a visual
frame (array state, highlights, memory cards, what-happened / why-matters,
active code line, progress counter). This guarantees the visualizer is always
correct, exactly matching the reference UI (Two Sum brute + hashmap, etc.).
"""

def mem(label, value, sub):
    return {"label": label, "value": str(value), "sub": sub}

# ---------------------------------------------------------------- Two Sum brute
def two_sum_brute(nums, target):
    frames = []
    checked = 0
    total = len(nums) * (len(nums) - 1) // 2
    frames.append({
        "arr": nums, "hi": {"passed": []},
        "memory": [
            mem("i · FIRST INDEX", "not set", "Index of the first number in the pair"),
            mem("j · SECOND INDEX", "not set", "Index of the second number, always right of i"),
            mem("nums[i] + nums[j]", "not set", "What this pair actually adds up to"),
            mem("target", target, "The number the pair has to hit"),
        ],
        "what": f"We need two different positions whose values add up to {target}, and we must return their indices.",
        "why": "The brute force plan is the most literal reading of the problem: if the answer is some pair, then checking every pair must find it.",
        "line": 1, "counter": {"label": "pairs checked", "cur": 0, "max": total},
    })
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            checked += 1
            s = nums[i] + nums[j]
            hit = s == target
            frames.append({
                "arr": nums,
                "hi": {"first": i, "second": j, "passed": list(range(i)), "pair": [i, j] if hit else None},
                "memory": [
                    mem("i · FIRST INDEX", i, f"value = {nums[i]}"),
                    mem("j · SECOND INDEX", j, f"value = {nums[j]}"),
                    mem("nums[i] + nums[j]", s, "sum of the current pair"),
                    mem("target", target, "The number the pair has to hit"),
                ],
                "what": f"Check pair (i={i}, j={j}): {nums[i]} + {nums[j]} = {s}." + (" That's the target!" if hit else " Not the target, keep going."),
                "why": "Fixing i and sweeping j to its right tries every unordered pair exactly once.",
                "line": 3, "counter": {"label": "pairs checked", "cur": checked, "max": total},
            })
            if hit:
                return frames
    return frames

# --------------------------------------------------------------- Two Sum hashed
def two_sum_hash(nums, target):
    frames = []
    seen = {}
    frames.append({
        "arr": nums, "hi": {"stored": []},
        "memory": [
            mem("i · TODAY", "not set", "The single index we are standing on"),
            mem("nums[i]", "not set", "The number at the current index"),
            mem("need", "not set", "target - nums[i], the partner this needs"),
            mem("target", target, "The number the pair has to hit"),
        ],
        "what": "We create an empty map and will walk the array once, looking for two numbers that add to " + str(target) + ".",
        "why": 'The map answers one question instantly: "have I already passed a number equal to X, and where was it?" That single question replaces the entire inner loop.',
        "line": 1, "counter": {"label": "values read", "cur": 0, "max": len(nums)},
    })
    for i, x in enumerate(nums):
        need = target - x
        found = need in seen
        frames.append({
            "arr": nums,
            "hi": {"first": i, "stored": list(seen.values()), "pair": [seen[need], i] if found else None},
            "memory": [
                mem("i · TODAY", i, "current index"),
                mem("nums[i]", x, "number we're standing on"),
                mem("need", need, f"{target} - {x}"),
                mem("seen", "{" + ", ".join(f"{k}:{v}" for k, v in seen.items()) + "}", "value → index of everything passed"),
            ],
            "what": f"At index {i}, value {x}. Partner needed = {need}." + (f" Found it at index {seen[need]}!" if found else " Not seen yet, so remember this number."),
            "why": "Because we stored every earlier value, the partner check is O(1) — no rescanning.",
            "line": 4 if found else 6,
            "counter": {"label": "values read", "cur": i + 1, "max": len(nums)},
        })
        if found:
            return frames
        seen[x] = i
    return frames

# --------------------------------------------------------------- Two pointers
def two_pointer_pair(nums, target):
    frames = []
    l, r = 0, len(nums) - 1
    while l < r:
        s = nums[l] + nums[r]
        hit = s == target
        frames.append({
            "arr": nums,
            "hi": {"ptr": {"l": l, "r": r}, "pair": [l, r] if hit else None},
            "memory": [
                mem("l · LEFT", l, f"value = {nums[l]}"),
                mem("r · RIGHT", r, f"value = {nums[r]}"),
                mem("sum", s, f"{nums[l]} + {nums[r]}"),
                mem("target", target, "goal"),
            ],
            "what": f"Sum of ends = {s}." + (" Match!" if hit else (" Too big → move right in." if s > target else " Too small → move left in.")),
            "why": "Because the array is sorted, moving the correct pointer always steps toward the answer.",
            "line": 4, "counter": {"label": "steps", "cur": len(frames) + 1, "max": len(nums)},
        })
        if hit:
            break
        if s < target:
            l += 1
        else:
            r -= 1
    return frames

# --------------------------------------------------------------- Sliding window
def sliding_window_unique(s):
    frames = []
    seen = set()
    l = 0
    best = 0
    arr = list(s)
    for r in range(len(arr)):
        while arr[r] in seen:
            seen.discard(arr[l]); l += 1
        seen.add(arr[r])
        best = max(best, r - l + 1)
        frames.append({
            "arr": arr,
            "hi": {"ptr": {"l": l, "r": r}, "window": list(range(l, r + 1))},
            "memory": [
                mem("l · WINDOW START", l, f"char = {arr[l]}"),
                mem("r · WINDOW END", r, f"char = {arr[r]}"),
                mem("window", "".join(arr[l:r + 1]), "current distinct run"),
                mem("best", best, "longest so far"),
            ],
            "what": f"Window '{''.join(arr[l:r+1])}' has all-unique chars, length {r-l+1}.",
            "why": "Each character enters and leaves the window at most once → linear time.",
            "line": 5, "counter": {"label": "chars scanned", "cur": r + 1, "max": len(arr)},
        })
    return frames

# --------------------------------------------------------------- Binary search
def binary_search(nums, target):
    frames = []
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        hit = nums[mid] == target
        frames.append({
            "arr": nums,
            "hi": {"ptr": {"lo": lo, "mid": mid, "hi": hi}, "pair": [mid] if hit else None},
            "memory": [
                mem("lo", lo, f"value = {nums[lo]}"),
                mem("mid", mid, f"value = {nums[mid]}"),
                mem("hi", hi, f"value = {nums[hi]}"),
                mem("target", target, "goal"),
            ],
            "what": f"Middle value {nums[mid]}." + (" Found it!" if hit else (" Too big → search left." if nums[mid] > target else " Too small → search right.")),
            "why": "Halving the range each step gives O(log n).",
            "line": 4, "counter": {"label": "probes", "cur": len(frames) + 1, "max": len(nums)},
        })
        if hit:
            break
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return frames

# --------------------------------------------------------------- Kadane
def kadane(nums):
    frames = []
    best = cur = nums[0]
    for i in range(1, len(nums)):
        cur = max(nums[i], cur + nums[i])
        best = max(best, cur)
        frames.append({
            "arr": nums,
            "hi": {"first": i, "window": []},
            "memory": [
                mem("i", i, f"value = {nums[i]}"),
                mem("cur", cur, "best sum ending here"),
                mem("best", best, "best overall"),
                mem("choice", "extend" if cur != nums[i] else "restart", "extend run or start fresh"),
            ],
            "what": f"At index {i}: running sum = {cur}, best = {best}.",
            "why": "If the running sum goes negative it can only hurt, so we restart.",
            "line": 4, "counter": {"label": "scanned", "cur": i + 1, "max": len(nums)},
        })
    return frames


SIMULATORS = {
    "two_sum_brute": two_sum_brute,
    "two_sum_hash": two_sum_hash,
    "two_pointer_pair": two_pointer_pair,
    "sliding_window_unique": sliding_window_unique,
    "binary_search": binary_search,
    "kadane": kadane,
}
