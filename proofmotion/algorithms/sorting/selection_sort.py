"""
algorithms/sorting/selection_sort.py
------------------------------------
Step-by-step trace generation for Selection Sort.
"""

from typing import List
from core.step_model import VisualizationStep, RenderData
from resources.theme import COLORS
from algorithms.sorting.sorting_events import SortEvent, SortEventType

PSEUDOCODE = [
    "procedure SelectionSort(A):",
    "    n = length(A)",
    "    for i from 0 to n - 1:",
    "        min_idx = i",
    "        for j from i + 1 to n - 1:",
    "            if A[j] < A[min_idx]:",
    "                min_idx = j",
    "        if min_idx != i:",
    "            swap(A[i], A[min_idx])",
    "    return A",
]


def selection_sort_trace(arr: List[int]) -> List[VisualizationStep]:
    a = list(arr)
    n = len(a)
    steps = []
    comparisons = 0
    swaps = 0

    def make_bars(i_idx=None, min_idx=None, j_idx=None, sorted_up_to=-1, swapping=None):
        swapping = swapping or []
        bars = []
        for idx, val in enumerate(a):
            tag = ""
            if idx in swapping:
                color = COLORS["danger"]
                tag = "SWAP"
            elif idx <= sorted_up_to:
                color = COLORS["success"]
                tag = "SORTED"
            elif idx == min_idx:
                color = COLORS["accent_gold"]
                tag = "MIN"
            elif idx == j_idx:
                color = COLORS["accent_blue"]
                tag = "SCAN"
            elif idx == i_idx:
                color = COLORS["accent_gold_hover"]
                tag = "TARGET"
            else:
                color = COLORS["accent_teal"]
            bars.append({"val": val, "color": color, "tag": tag})
        return bars

    step_num = 1
    steps.append(VisualizationStep(
        index=step_num,
        title="Initial Array",
        equation="A = " + str(a),
        explanation=f"Starting Selection Sort with {n} elements.",
        values={"array": list(a)},
        pseudocode=PSEUDOCODE,
        pseudocode_line=1,
        metrics={"comparisons": 0, "swaps_writes": 0, "time_complexity": "O(n²)", "space_complexity": "O(1)"},
        render_data=RenderData(
            mode="bars",
            bars=make_bars(),
            sort_event=SortEvent(SortEventType.INIT, array=list(a), description="Initial array")
        )
    ))

    if n <= 1:
        step_num += 1
        steps.append(VisualizationStep(
            index=step_num,
            title="Sort Complete",
            equation="Array is sorted.",
            explanation="Array has 0 or 1 element, trivially sorted.",
            values={"final_array": list(a), "array": list(a)},
            pseudocode=PSEUDOCODE,
            pseudocode_line=10,
            metrics={"comparisons": 0, "swaps_writes": 0, "time_complexity": "O(1)", "space_complexity": "O(1)"},
            render_data=RenderData(
                mode="bars",
                bars=make_bars(sorted_up_to=n-1),
                sort_event=SortEvent(SortEventType.COMPLETE, array=list(a), sorted_indices=list(range(n)), description="Complete")
            )
        ))
        return steps

    for i in range(n):
        min_idx = i
        step_num += 1
        steps.append(VisualizationStep(
            index=step_num,
            title=f"Pass {i+1}: Assume Minimum at index {i}",
            equation=f"min_idx = {i}, value = {a[i]}",
            explanation=f"Assume the minimum in unsorted subarray A[{i}..{n-1}] is at index {i} (value {a[i]}).",
            values={"i": i, "min_idx": min_idx, "min_val": a[min_idx]},
            pseudocode=PSEUDOCODE,
            pseudocode_line=4,
            metrics={"comparisons": comparisons, "swaps_writes": swaps, "time_complexity": "O(n²)", "space_complexity": "O(1)"},
            render_data=RenderData(
                mode="bars",
                bars=make_bars(i_idx=i, min_idx=min_idx, sorted_up_to=i-1),
                sort_event=SortEvent(
                    SortEventType.SELECT_MIN,
                    array=list(a),
                    indices=[i],
                    min_index=min_idx,
                    sorted_indices=list(range(i)),
                    description=f"Assume min at {i}"
                )
            )
        ))

        for j in range(i + 1, n):
            comparisons += 1
            step_num += 1
            steps.append(VisualizationStep(
                index=step_num,
                title=f"Compare A[{j}] and A[min_idx={min_idx}]",
                equation=f"A[{j}] ({a[j]}) < A[{min_idx}] ({a[min_idx]}) ?",
                explanation=f"Scanning index {j} (value {a[j]}). Check if it is smaller than current minimum {a[min_idx]}.",
                values={"j": j, "min_idx": min_idx, "A[j]": a[j], "A[min_idx]": a[min_idx]},
                pseudocode=PSEUDOCODE,
                pseudocode_line=6,
                metrics={"comparisons": comparisons, "swaps_writes": swaps, "time_complexity": "O(n²)", "space_complexity": "O(1)"},
                render_data=RenderData(
                    mode="bars",
                    bars=make_bars(i_idx=i, min_idx=min_idx, j_idx=j, sorted_up_to=i-1),
                    sort_event=SortEvent(
                        SortEventType.COMPARE,
                        array=list(a),
                        indices=[j, min_idx],
                        comparing_indices=(j, min_idx),
                        min_index=min_idx,
                        sorted_indices=list(range(i)),
                        description=f"Compare A[{j}] and A[{min_idx}]"
                    )
                )
            ))

            if a[j] < a[min_idx]:
                min_idx = j
                step_num += 1
                steps.append(VisualizationStep(
                    index=step_num,
                    title=f"New Minimum Found at index {j}",
                    equation=f"min_idx = {j} (value = {a[j]})",
                    explanation=f"Found smaller element {a[j]} at index {j}. Updating min_idx to {j}.",
                    values={"min_idx": min_idx, "min_val": a[min_idx]},
                    pseudocode=PSEUDOCODE,
                    pseudocode_line=7,
                    metrics={"comparisons": comparisons, "swaps_writes": swaps, "time_complexity": "O(n²)", "space_complexity": "O(1)"},
                    render_data=RenderData(
                        mode="bars",
                        bars=make_bars(i_idx=i, min_idx=min_idx, sorted_up_to=i-1),
                        sort_event=SortEvent(
                            SortEventType.SELECT_MIN,
                            array=list(a),
                            indices=[min_idx],
                            min_index=min_idx,
                            sorted_indices=list(range(i)),
                            description=f"New min at {min_idx}"
                        )
                    )
                ))

        if min_idx != i:
            a[i], a[min_idx] = a[min_idx], a[i]
            swaps += 1
            step_num += 1
            steps.append(VisualizationStep(
                index=step_num,
                title=f"Swap Minimum A[{min_idx}] with A[{i}]",
                equation=f"swap(A[{i}], A[{min_idx}]) ⟹ {a[i]} into sorted position {i}",
                explanation=f"Swapped smallest unsorted value {a[i]} into index {i}.",
                values={"swapped": (i, min_idx)},
                pseudocode=PSEUDOCODE,
                pseudocode_line=9,
                metrics={"comparisons": comparisons, "swaps_writes": swaps, "time_complexity": "O(n²)", "space_complexity": "O(1)"},
                render_data=RenderData(
                    mode="bars",
                    bars=make_bars(swapping=[i, min_idx], sorted_up_to=i),
                    sort_event=SortEvent(
                        SortEventType.SWAP,
                        array=list(a),
                        indices=[i, min_idx],
                        swapping_indices=(i, min_idx),
                        min_index=i,
                        sorted_indices=list(range(i + 1)),
                        description=f"Swap min A[{min_idx}] with A[{i}]"
                    )
                )
            ))

    step_num += 1
    steps.append(VisualizationStep(
        index=step_num,
        title="Sort Complete",
        equation=f"Total Comparisons = {comparisons}, Total Swaps = {swaps}",
        explanation=f"Selection Sort complete: {comparisons} comparisons, {swaps} swaps.",
        values={"final_array": list(a)},
        pseudocode=PSEUDOCODE,
        pseudocode_line=10,
        metrics={"comparisons": comparisons, "swaps_writes": swaps, "time_complexity": "O(n²)", "space_complexity": "O(1)"},
        render_data=RenderData(
            mode="bars",
            bars=make_bars(sorted_up_to=n-1),
            sort_event=SortEvent(
                SortEventType.COMPLETE,
                array=list(a),
                sorted_indices=list(range(n)),
                description="Complete"
            )
        )
    ))

    return steps
