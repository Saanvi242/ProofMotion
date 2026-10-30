"""
algorithms/searching/binary_search.py
-------------------------------------
Step-by-step trace generation for Binary Search:
- Sorted number tiles
- LOW, MID, HIGH boundary markers
- Midpoint comparison highlight
- Eliminated half fades away (narrowing search zone)
- Matching element lights up in radiant green
"""

from typing import List, Tuple
from core.step_model import VisualizationStep, RenderData
from resources.theme import COLORS

PSEUDOCODE = [
    "procedure BinarySearch(A, target):",
    "    low = 0, high = length(A) - 1",
    "    while low <= high:",
    "        mid = (low + high) / 2",
    "        if A[mid] == target: return mid",
    "        else if A[mid] < target: low = mid + 1",
    "        else: high = mid - 1",
    "    return -1 // Not found",
]


def binary_search_trace(arr: List[int], target: int) -> Tuple[List[VisualizationStep], bool]:
    """
    Returns (steps, was_sorted). If arr was not sorted, it is sorted first
    and an introductory step explicitly informs the user.
    """
    is_sorted = arr == sorted(arr)
    a = sorted(arr)
    n = len(a)
    steps = []
    comparisons = 0
    step_num = 1

    def make_bars(low=None, mid=None, high=None, found_idx=None):
        bars = []
        for idx, val in enumerate(a):
            tag = ""
            if idx == found_idx:
                color = COLORS["success"]
                tag = "FOUND"
            elif idx == mid:
                color = COLORS["accent_gold"]
                tag = "MID"
            elif idx == low and idx == high:
                color = COLORS["accent_blue"]
                tag = "L,H"
            elif idx == low:
                color = COLORS["accent_blue"]
                tag = "LOW"
            elif idx == high:
                color = COLORS["accent_blue"]
                tag = "HIGH"
            elif low is not None and high is not None and low <= idx <= high:
                color = COLORS["accent_teal"]
                tag = ""
            else:
                color = COLORS["border_soft"]
                tag = ""
            bars.append({"val": val, "color": color, "tag": tag})
        return bars

    def make_search_data(low=None, mid=None, high=None, found_idx=None, status="", comparison=""):
        eliminated = []
        if low is not None and high is not None:
            eliminated = [i for i in range(n) if i < low or i > high]
        elif found_idx is None:
            eliminated = list(range(n))

        return {
            "type": "binary",
            "array": list(a),
            "target": target,
            "low": low,
            "mid": mid,
            "high": high,
            "found_index": found_idx,
            "eliminated_indices": eliminated,
            "status": status,
            "comparison": comparison,
        }

    if n == 0:
        steps.append(VisualizationStep(
            index=step_num,
            title="Empty Array",
            equation="Array is empty",
            explanation="Cannot search an empty collection.",
            values={"found": False, "found_index": -1, "comparisons": 0},
            pseudocode=PSEUDOCODE,
            pseudocode_line=1,
            metrics={"comparisons": 0, "found": False, "time_complexity": "O(log n)", "space_complexity": "O(1)"},
            render_data=RenderData(mode="search_tiles", bars=[], search_data=make_search_data(status="Array is empty", comparison="Target not found"))
        ))
        return steps, is_sorted

    if not is_sorted:
        steps.append(VisualizationStep(
            index=step_num,
            title="Input Array Sorted for Binary Search",
            equation=f"Original: {arr} ⟹ Sorted: {a}",
            explanation="Binary Search strictly requires a sorted collection. The array has been pre-sorted.",
            values={"original": list(arr), "sorted": list(a)},
            pseudocode=PSEUDOCODE,
            pseudocode_line=1,
            metrics={"comparisons": 0, "found": False, "time_complexity": "O(log n)", "space_complexity": "O(1)"},
            render_data=RenderData(
                mode="search_tiles",
                bars=make_bars(low=0, high=n - 1),
                search_data=make_search_data(low=0, high=n - 1, status="Array pre-sorted for Binary Search", comparison=f"Elements ordered ascending: {a}")
            )
        ))
        step_num += 1

    steps.append(VisualizationStep(
        index=step_num,
        title="Initialize Binary Search Boundaries",
        equation=f"low = 0, high = {n - 1}, target = {target}",
        explanation=f"Initialized search window: low=0 and high={n - 1}. Target = {target}.",
        values={"low": 0, "high": n - 1, "target": target},
        pseudocode=PSEUDOCODE,
        pseudocode_line=2,
        metrics={"comparisons": 0, "found": False, "time_complexity": "O(log n)", "space_complexity": "O(1)"},
        render_data=RenderData(
            mode="search_tiles",
            bars=make_bars(low=0, high=n - 1),
            search_data=make_search_data(
                low=0, high=n - 1,
                status=f"Active Zone: [0 .. {n - 1}]  |  Target: {target}",
                comparison=f"Initial boundaries set: low=0, high={n - 1}"
            )
        )
    ))

    low = 0
    high = n - 1

    while low <= high:
        mid = (low + high) // 2
        comparisons += 1
        step_num += 1
        val_mid = a[mid]

        steps.append(VisualizationStep(
            index=step_num,
            title=f"Calculate Midpoint: mid = ({low} + {high}) // 2 = {mid}",
            equation=f"mid = {mid},  A[mid] = {val_mid},  target = {target}",
            explanation=f"Current search window is [{low}..{high}]. Midpoint element is A[{mid}] = {val_mid}.",
            values={"low": low, "high": high, "mid": mid, "A[mid]": val_mid, "target": target},
            pseudocode=PSEUDOCODE,
            pseudocode_line=4,
            metrics={"comparisons": comparisons, "found": False, "time_complexity": "O(log n)", "space_complexity": "O(1)"},
            render_data=RenderData(
                mode="search_tiles",
                bars=make_bars(low=low, mid=mid, high=high),
                search_data=make_search_data(
                    low=low, mid=mid, high=high,
                    status=f"Inspecting Midpoint A[{mid}] = {val_mid} (Comparing with target {target})",
                    comparison=f"mid = ({low} + {high}) // 2 = {mid}  ⟹  A[{mid}] = {val_mid}"
                )
            )
        ))

        if val_mid == target:
            step_num += 1
            steps.append(VisualizationStep(
                index=step_num,
                title=f"Target Found! A[{mid}] == {target}",
                equation=f"A[{mid}] == {target} ⟹ return index {mid}",
                explanation=f"Target value {target} successfully located at index {mid} in {comparisons} comparison(s).",
                values={"found_index": mid, "comparisons": comparisons},
                pseudocode=PSEUDOCODE,
                pseudocode_line=5,
                metrics={"comparisons": comparisons, "found": True, "time_complexity": "O(log n)", "space_complexity": "O(1)"},
                render_data=RenderData(
                    mode="search_tiles",
                    bars=make_bars(found_idx=mid),
                    search_data=make_search_data(
                        low=low, mid=mid, high=high, found_idx=mid,
                        status=f"Match Found! Target {target} located at index [{mid}]",
                        comparison=f"A[{mid}] ({val_mid}) == {target}  ✓ Match Confirmed!"
                    )
                )
            ))
            return steps, is_sorted

        elif val_mid < target:
            step_num += 1
            old_low = low
            low = mid + 1
            steps.append(VisualizationStep(
                index=step_num,
                title=f"A[mid]={val_mid} < {target}: Eliminate Left Half",
                equation=f"{val_mid} < {target} ⟹ low = mid + 1 = {low}",
                explanation=f"Since array is sorted and {val_mid} < {target}, target must lie in the right half. Discarding [{old_low}..{mid}].",
                values={"new_low": low, "high": high},
                pseudocode=PSEUDOCODE,
                pseudocode_line=6,
                metrics={"comparisons": comparisons, "found": False, "time_complexity": "O(log n)", "space_complexity": "O(1)"},
                render_data=RenderData(
                    mode="search_tiles",
                    bars=make_bars(low=low, high=high),
                    search_data=make_search_data(
                        low=low, mid=mid, high=high,
                        status=f"A[{mid}]={val_mid} < {target} ⟹ Left half [{old_low}..{mid}] eliminated! Fading away.",
                        comparison=f"Narrowed Search Zone to [{low} .. {high}]"
                    )
                )
            ))
        else:
            step_num += 1
            old_high = high
            high = mid - 1
            steps.append(VisualizationStep(
                index=step_num,
                title=f"A[mid]={val_mid} > {target}: Eliminate Right Half",
                equation=f"{val_mid} > {target} ⟹ high = mid - 1 = {high}",
                explanation=f"Since array is sorted and {val_mid} > {target}, target must lie in the left half. Discarding [{mid}..{old_high}].",
                values={"low": low, "new_high": high},
                pseudocode=PSEUDOCODE,
                pseudocode_line=7,
                metrics={"comparisons": comparisons, "found": False, "time_complexity": "O(log n)", "space_complexity": "O(1)"},
                render_data=RenderData(
                    mode="search_tiles",
                    bars=make_bars(low=low, high=high if high >= low else None),
                    search_data=make_search_data(
                        low=low, mid=mid, high=high if high >= low else None,
                        status=f"A[{mid}]={val_mid} > {target} ⟹ Right half [{mid}..{old_high}] eliminated! Fading away.",
                        comparison=f"Narrowed Search Zone to [{low} .. {high}]"
                    )
                )
            ))

    step_num += 1
    steps.append(VisualizationStep(
        index=step_num,
        title="Target Not Found (low > high)",
        equation=f"Search space exhausted (low={low} > high={high}) ⟹ return -1",
        explanation=f"Search interval is empty. Target value {target} does not exist in array.",
        values={"found": False, "found_index": -1, "comparisons": comparisons},
        pseudocode=PSEUDOCODE,
        pseudocode_line=8,
        metrics={"comparisons": comparisons, "found": False, "time_complexity": "O(log n)", "space_complexity": "O(1)"},
        render_data=RenderData(
            mode="search_tiles",
            bars=make_bars(),
            search_data=make_search_data(
                low=low, high=high, found_idx=-1,
                status=f"Target {target} not found in array",
                comparison=f"Search zone exhausted: low ({low}) > high ({high}) ⟹ return -1"
            )
        )
    ))

    return steps, is_sorted
