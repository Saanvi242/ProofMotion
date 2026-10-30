"""
algorithms/searching/linear_search.py
-------------------------------------
Step-by-step trace generation for Linear Search:
- Numbers as individual horizontal tiles
- Glowing scanner cursor moving sequentially left-to-right
- Non-matching elements fade away
- Matching element lights up in radiant green
"""

from typing import List
from core.step_model import VisualizationStep, RenderData
from resources.theme import COLORS

PSEUDOCODE = [
    "procedure LinearSearch(A, target):",
    "    for i from 0 to length(A) - 1:",
    "        if A[i] == target:",
    "            return i  // Found",
    "    return -1         // Not found",
]


def linear_search_trace(arr: List[int], target: int) -> List[VisualizationStep]:
    a = list(arr)
    n = len(a)
    steps = []
    comparisons = 0
    step_num = 1

    def make_bars(current_idx=None, found_idx=None, examined_indices=None):
        examined_indices = examined_indices or set()
        bars = []
        for idx, val in enumerate(a):
            tag = ""
            if idx == found_idx:
                color = COLORS["success"]
                tag = "FOUND"
            elif idx == current_idx:
                color = COLORS["accent_gold"]
                tag = "EXAMINE"
            elif idx in examined_indices:
                color = COLORS["border"]
                tag = "CHECKED"
            else:
                color = COLORS["accent_teal"]
            bars.append({"val": val, "color": color, "tag": tag})
        return bars

    def make_search_data(current_idx=None, found_idx=None, examined_indices=None, status="", comparison=""):
        return {
            "type": "linear",
            "array": list(a),
            "target": target,
            "current_index": current_idx,
            "found_index": found_idx,
            "examined_indices": list(examined_indices or []),
            "status": status,
            "comparison": comparison,
        }

    # Step 1: Initial state
    steps.append(VisualizationStep(
        index=step_num,
        title="Start Linear Search",
        equation=f"target = {target}, A = {a}",
        explanation=f"Searching for target value {target} sequentially through array of {n} elements.",
        values={"target": target, "array": list(a), "found_index": -1 if n == 0 else None},
        pseudocode=PSEUDOCODE,
        pseudocode_line=1,
        metrics={"comparisons": 0, "found": False, "time_complexity": "O(n)", "space_complexity": "O(1)"},
        render_data=RenderData(
            mode="search_tiles",
            bars=make_bars(),
            search_data=make_search_data(
                status=f"Ready to scan: Target is {target}",
                comparison=f"Scanner positioned at start of array ({n} items)"
            )
        )
    ))

    if n == 0:
        return steps

    examined = set()
    for i in range(n):
        comparisons += 1
        step_num += 1
        is_match = (a[i] == target)

        steps.append(VisualizationStep(
            index=step_num,
            title=f"Check A[{i}] == {target}",
            equation=f"A[{i}] ({a[i]}) == {target} ?",
            explanation=f"Scanning tile [{i}] (value {a[i]}). Comparing with target {target}.",
            values={"i": i, "val": a[i], "target": target},
            pseudocode=PSEUDOCODE,
            pseudocode_line=3,
            metrics={"comparisons": comparisons, "found": False, "time_complexity": "O(n)", "space_complexity": "O(1)"},
            render_data=RenderData(
                mode="search_tiles",
                bars=make_bars(current_idx=i, examined_indices=examined),
                search_data=make_search_data(
                    current_idx=i,
                    examined_indices=examined,
                    status=f"Scanning Tile [{i}]: Comparing value {a[i]} with {target}",
                    comparison=f"A[{i}] = {a[i]}  vs  target = {target}  {'✓ EQUAL' if is_match else '≠ NOT EQUAL'}"
                )
            )
        ))

        if is_match:
            step_num += 1
            steps.append(VisualizationStep(
                index=step_num,
                title=f"Target Found at index {i}",
                equation=f"A[{i}] == {target} ⟹ return index {i}",
                explanation=f"Match found! Element {target} is located at index {i} in {comparisons} comparison(s).",
                values={"found_index": i, "target": target},
                pseudocode=PSEUDOCODE,
                pseudocode_line=4,
                metrics={"comparisons": comparisons, "found": True, "time_complexity": "O(n)", "space_complexity": "O(1)"},
                render_data=RenderData(
                    mode="search_tiles",
                    bars=make_bars(found_idx=i, examined_indices=examined),
                    search_data=make_search_data(
                        current_idx=i,
                        found_idx=i,
                        examined_indices=examined,
                        status=f"Match Found! Target {target} located at index [{i}]",
                        comparison=f"A[{i}] == {target}  ✓ Match Confirmed!"
                    )
                )
            ))
            return steps

        examined.add(i)

    step_num += 1
    steps.append(VisualizationStep(
        index=step_num,
        title="Target Not Found",
        equation=f"return -1 (Target {target} not in array)",
        explanation=f"All {n} elements scanned. Target value {target} does not exist in the array.",
        values={"found_index": -1, "target": target},
        pseudocode=PSEUDOCODE,
        pseudocode_line=5,
        metrics={"comparisons": comparisons, "found": False, "time_complexity": "O(n)", "space_complexity": "O(1)"},
        render_data=RenderData(
            mode="search_tiles",
            bars=make_bars(examined_indices=examined),
            search_data=make_search_data(
                examined_indices=examined,
                found_idx=-1,
                status=f"Target {target} not found in array",
                comparison="All elements examined without match ⟹ return -1"
            )
        )
    ))

    return steps
