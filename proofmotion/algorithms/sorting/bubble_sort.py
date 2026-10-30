"""
algorithms/sorting/bubble_sort.py
---------------------------------
Step-by-step trace generation for Bubble Sort.
"""

from typing import List, Dict, Any
from copy import deepcopy
from core.step_model import VisualizationStep, RenderData
from resources.theme import COLORS
from algorithms.sorting.sorting_events import SortEvent, SortEventType

PSEUDOCODE = [
    "procedure BubbleSort(A):",
    "    n = length(A)",
    "    for i from 0 to n - 1:",
    "        swapped = false",
    "        for j from 0 to n - i - 2:",
    "            if A[j] > A[j + 1]:",
    "                swap(A[j], A[j + 1])",
    "                swapped = true",
    "        if not swapped: break",
    "    return A",
]


def bubble_sort_trace(arr: List[int]) -> List[VisualizationStep]:
    a = list(arr)
    n = len(a)
    steps = []
    comparisons = 0
    swaps = 0

    def make_bars(comparing=None, swapping=None, sorted_from=None):
        comparing = comparing or []
        swapping = swapping or []
        bars = []
        for idx, val in enumerate(a):
            tag = ""
            if idx in swapping:
                color = COLORS["danger"]
                tag = "SWAP"
            elif idx in comparing:
                color = COLORS["accent_gold"]
                tag = "CMP"
            elif sorted_from is not None and idx >= sorted_from:
                color = COLORS["success"]
                tag = "SORTED"
            else:
                color = COLORS["accent_teal"]
            bars.append({"val": val, "color": color, "tag": tag})
        return bars

    step_num = 1
    # Initial state
    steps.append(VisualizationStep(
        index=step_num,
        title="Initial Array",
        equation="A = " + str(a),
        explanation=f"Starting Bubble Sort with array of {n} elements.",
        values={"array": list(a), "comparisons": 0, "swaps": 0},
        pseudocode=PSEUDOCODE,
        pseudocode_line=1,
        metrics={"comparisons": 0, "swaps_writes": 0, "time_complexity": "O(n²)", "space_complexity": "O(1)"},
        render_data=RenderData(mode="bars", bars=make_bars(), sort_event=SortEvent(SortEventType.INIT, array=list(a)))
    ))

    if n <= 1:
        step_num += 1
        steps.append(VisualizationStep(
            index=step_num,
            title="Sorted Array",
            equation="Array is already sorted.",
            explanation="Array has 0 or 1 element, trivially sorted.",
            values={"array": list(a)},
            pseudocode=PSEUDOCODE,
            pseudocode_line=10,
            metrics={"comparisons": 0, "swaps_writes": 0, "time_complexity": "O(1)", "space_complexity": "O(1)"},
            render_data=RenderData(mode="bars", bars=make_bars(sorted_from=0), sort_event=SortEvent(SortEventType.COMPLETE, array=list(a), sorted_indices=list(range(n))))
        ))
        return steps

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            comparisons += 1
            step_num += 1
            # Comparison step
            steps.append(VisualizationStep(
                index=step_num,
                title=f"Compare A[{j}] and A[{j+1}]",
                equation=f"A[{j}] ({a[j]}) > A[{j+1}] ({a[j+1]}) ?",
                explanation=f"Comparing element at index {j} (value {a[j]}) with index {j+1} (value {a[j+1]}).",
                values={"i": i, "j": j, "A[j]": a[j], "A[j+1]": a[j+1]},
                pseudocode=PSEUDOCODE,
                pseudocode_line=6,
                metrics={"comparisons": comparisons, "swaps_writes": swaps, "time_complexity": "O(n²)", "space_complexity": "O(1)"},
                render_data=RenderData(
                    mode="bars",
                    bars=make_bars(comparing=[j, j + 1], sorted_from=n - i),
                    sort_event=SortEvent(
                        SortEventType.COMPARE,
                        array=list(a),
                        indices=[j, j + 1],
                        comparing_indices=(j, j + 1),
                        sorted_indices=list(range(n - i, n)),
                        description=f"Compare A[{j}] and A[{j+1}]"
                    )
                )
            ))

            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
                swapped = True
                step_num += 1
                # Swap step
                steps.append(VisualizationStep(
                    index=step_num,
                    title=f"Swap A[{j}] and A[{j+1}]",
                    equation=f"swap(A[{j}], A[{j+1}]) ⟹ {a[j]}, {a[j+1]}",
                    explanation=f"Condition met: {a[j+1]} > {a[j]} was inverted, so we swap them.",
                    values={"swapped": True, "A": list(a)},
                    pseudocode=PSEUDOCODE,
                    pseudocode_line=7,
                    metrics={"comparisons": comparisons, "swaps_writes": swaps, "time_complexity": "O(n²)", "space_complexity": "O(1)"},
                    render_data=RenderData(
                        mode="bars",
                        bars=make_bars(swapping=[j, j + 1], sorted_from=n - i),
                        sort_event=SortEvent(
                            SortEventType.SWAP,
                            array=list(a),
                            indices=[j, j + 1],
                            swapping_indices=(j, j + 1),
                            sorted_indices=list(range(n - i, n)),
                            description=f"Swap A[{j}] and A[{j+1}]"
                        )
                    )
                ))

        if not swapped:
            step_num += 1
            steps.append(VisualizationStep(
                index=step_num,
                title="Early Termination",
                equation="swapped == false ⟹ break",
                explanation=f"No elements were swapped during pass {i+1}. The array is now fully sorted.",
                values={"early_stop": True},
                pseudocode=PSEUDOCODE,
                pseudocode_line=9,
                metrics={"comparisons": comparisons, "swaps_writes": swaps, "time_complexity": "O(n²)", "space_complexity": "O(1)"},
                render_data=RenderData(
                    mode="bars",
                    bars=make_bars(sorted_from=0),
                    sort_event=SortEvent(SortEventType.COMPLETE, array=list(a), sorted_indices=list(range(n)))
                )
            ))
            break

    # Final sorted step
    step_num += 1
    steps.append(VisualizationStep(
        index=step_num,
        title="Sort Complete",
        equation=f"Total Comparisons = {comparisons}, Total Swaps = {swaps}",
        explanation=f"Bubble Sort completed successfully in {comparisons} comparisons and {swaps} swaps.",
        values={"final_array": list(a), "comparisons": comparisons, "swaps": swaps},
        pseudocode=PSEUDOCODE,
        pseudocode_line=10,
        metrics={"comparisons": comparisons, "swaps_writes": swaps, "time_complexity": "O(n²)", "space_complexity": "O(1)"},
        render_data=RenderData(
            mode="bars",
            bars=make_bars(sorted_from=0),
            sort_event=SortEvent(SortEventType.COMPLETE, array=list(a), sorted_indices=list(range(n)))
        )
    ))

    return steps
