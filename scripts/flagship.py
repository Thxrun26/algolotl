"""
Flagship problems: rich, multi-approach, image-style visualizers.
Each approach carries its own simulated frames + Java code.
"""
from frames import SIMULATORS

JAVA = {
    "two_sum_brute": """int[] twoSum(int[] nums, int target) {
    for (int i = 0; i < nums.length; i++)
        for (int j = i + 1; j < nums.length; j++)
            if (nums[i] + nums[j] == target)
                return new int[]{ i, j };
    return new int[]{};
}""",
    "two_sum_hash": """int[] twoSum(int[] nums, int target) {
    Map<Integer,Integer> seen = new HashMap<>();
    for (int i = 0; i < nums.length; i++) {
        int need = target - nums[i];
        if (seen.containsKey(need))
            return new int[]{ seen.get(need), i };
        seen.put(nums[i], i);
    }
    return new int[]{};
}""",
    "tp_pair": """int[] twoSum(int[] a, int target) {
    int l = 0, r = a.length - 1;
    while (l < r) {
        int sum = a[l] + a[r];
        if (sum == target) return new int[]{ l, r };
        if (sum < target) l++;
        else r--;
    }
    return new int[]{};
}""",
    "sw_unique": """int lengthOfLongestSubstring(String s) {
    Set<Character> win = new HashSet<>();
    int l = 0, best = 0;
    for (int r = 0; r < s.length(); r++) {
        while (win.contains(s.charAt(r))) win.remove(s.charAt(l++));
        win.add(s.charAt(r));
        best = Math.max(best, r - l + 1);
    }
    return best;
}""",
    "bsearch": """int search(int[] nums, int target) {
    int lo = 0, hi = nums.length - 1;
    while (lo <= hi) {
        int mid = (lo + hi) >>> 1;
        if (nums[mid] == target) return mid;
        if (nums[mid] < target) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1;
}""",
    "kadane": """int maxSubArray(int[] nums) {
    int best = nums[0], cur = nums[0];
    for (int i = 1; i < nums.length; i++) {
        cur = Math.max(nums[i], cur + nums[i]);
        best = Math.max(best, cur);
    }
    return best;
}""",
}


def build_flagship():
    """Return {problem_id: {quickshot, dsExplainer, approaches[]}}"""
    out = {}

    out["two-sum"] = {
        "quickshot": "PATTERN: complement lookup. If you must find a pair that hits a target, don't recheck pairs — remember what you've seen in a Map so the partner is one lookup away.",
        "dsExplainer": "HashMap: a dictionary from key→value with average O(1) insert and lookup. Here we map each number's VALUE to its INDEX so we can instantly ask 'did I already see target - x?'.",
        "approaches": [
            {"key": "brute", "name": "Brute Force", "bigO": "O(n²)",
             "idea": "Test every pair until one adds up to the target.",
             "steps": ["Fix the first number, then try every number to its right as the partner.",
                       "Starting j at i + 1 avoids reusing an element and avoids repeating pairs."],
             "java": JAVA["two_sum_brute"],
             "frames": SIMULATORS["two_sum_brute"]([3, 2, 4, 7, 11], 9)},
            {"key": "optimal", "name": "Hash Map", "bigO": "O(n)",
             "idea": "Walk once, remembering every number you have already passed.",
             "steps": ["For the current number, the partner it needs is exactly target − nums[i].",
                       "Keep a map from value to index for every number already visited."],
             "java": JAVA["two_sum_hash"],
             "frames": SIMULATORS["two_sum_hash"]([3, 2, 4, 7, 11], 9)},
        ],
    }

    out["two-sum-ii-input-array-is-sorted"] = {
        "quickshot": "PATTERN: two pointers on sorted data. Sorted + pair-target ⇒ converge from both ends; the sort tells you which pointer to move.",
        "dsExplainer": "Two pointers: two indices (l, r) walking a sorted array. Moving l up increases the sum; moving r down decreases it — so you steer straight to the target.",
        "approaches": [
            {"key": "optimal", "name": "Two Pointers", "bigO": "O(n)",
             "idea": "Sum the two ends; too big → move right in, too small → move left in.",
             "steps": ["The array is sorted, so the ends give the extreme sums.",
                       "Each step eliminates one impossible pairing."],
             "java": JAVA["tp_pair"],
             "frames": SIMULATORS["two_pointer_pair"]([2, 7, 11, 15], 9)},
        ],
    }

    out["longest-substring-without-repeating-characters"] = {
        "quickshot": "PATTERN: variable sliding window. 'Longest/shortest contiguous run with a rule' ⇒ grow the right edge, shrink the left when the rule breaks.",
        "dsExplainer": "Sliding window + HashSet: the set holds the characters currently inside the window so duplicates are detected in O(1). The window [l..r] expands and contracts.",
        "approaches": [
            {"key": "optimal", "name": "Sliding Window", "bigO": "O(n)",
             "idea": "Expand the window to the right; on a duplicate, shrink from the left until it's unique again.",
             "steps": ["The set is the window's memory of which chars are inside.",
                       "Each index enters and leaves the window at most once → linear."],
             "java": JAVA["sw_unique"],
             "frames": SIMULATORS["sliding_window_unique"]("abcabcbb")},
        ],
    }

    out["binary-search"] = {
        "quickshot": "PATTERN: binary search. Sorted + a yes/no that flips once ⇒ halve the range each step.",
        "dsExplainer": "Binary search maintains an invariant window [lo, hi] that always contains the answer if it exists, shrinking it by half each probe → O(log n).",
        "approaches": [
            {"key": "optimal", "name": "Binary Search", "bigO": "O(log n)",
             "idea": "Look at the middle, then keep only the half that can contain the target.",
             "steps": ["Compare the midpoint to the target.",
                       "Discard the half that cannot possibly hold the answer."],
             "java": JAVA["bsearch"],
             "frames": SIMULATORS["binary_search"]([-1, 0, 3, 5, 9, 12], 9)},
        ],
    }

    out["maximum-subarray"] = {
        "quickshot": "PATTERN: Kadane / running optimum. Max contiguous sum ⇒ carry a running sum; drop it the moment it turns negative.",
        "dsExplainer": "Dynamic programming in O(1) space: 'best sum ending here' only depends on the previous 'best ending here', so two variables suffice.",
        "approaches": [
            {"key": "optimal", "name": "Kadane's Algorithm", "bigO": "O(n)",
             "idea": "At each element, either extend the current run or restart from this element.",
             "steps": ["A negative running sum can only hurt what comes next.",
                       "Track the best sum seen anywhere along the way."],
             "java": JAVA["kadane"],
             "frames": SIMULATORS["kadane"]([-2, 1, -3, 4, -1, 2, 1, -5, 4])},
        ],
    }

    return out
