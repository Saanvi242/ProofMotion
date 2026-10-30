"""
algorithms/sorting/quick_sort.py
--------------------------------
Step-by-step trace generation for Quick Sort.
"""

from typing import List
from core.step_model import VisualizationStep, RenderData
from resources.theme import COLORS
from algorithms.sorting.sorting_events import SortEvent, SortEventType

PSEUDOCODE = [
    "procedure QuickSort(A, low, high):",
    "    if low < high:",
    "        pivot_index = Partition(A, low, high)",
    "        QuickSort(A, low, pivot_index - 1)",
    "        QuickSort(A, pivot_index + 1, high)",
    "procedure Partition(A, low, high):",
    "    pivot = A[high]",
    "    i = low - 1",
    "    for j from low to high - 1:",
    "        if A[j] <= pivot:",
    "            i = i + 1; swap(A[i], A[j])",
    "    swap(A[i + 1], A[high])",
    "    return i + 1",
]


def quick_sort_trace(arr: List[int]) -> List[VisualizationStep]:
    a = list(arr)
    n = len(a)
    steps = []
    comparisons = 0
    swaps = 0
    step_num = 1
    sorted_indices = set()

    def make_bars(active_range=None, pivot_idx=None, i_idx=None, j_idx=None, swapping=None):
        active_range = active_range or (-1, -1)
        swapping = swapping or []
        bars = []
        for idx, val in enumerate(a):
            tag = ""
            if idx in swapping:
                color = COLORS["danger"]
                tag = "SWAP"
            elif idx == pivot_idx:
                color = "#9C59D1" # Purple pivot
                tag = "PIVOT"
            elif idx == j_idx:
                color = COLORS["accent_gold"]
                tag = "SCAN"
            elif idx == i_idx:
                color = COLORS["accent_blue"]
                tag = "PART"
            elif idx in sorted_indices:
                color = COLORS["success"]
                tag = "SORTED"
            elif active_range[0] <= idx <= active_range[1]:
                color = COLORS["accent_teal"]
                tag = "ACTIVE"
            else:
                color = COLORS["border"]
            bars.append({"val": val, "color": color, "tag": tag})
        return bars

    steps.append(VisualizationStep(
        index=step_num,
        title="Initial Array",
        equation="A = " + str(a),
        explanation=f"Starting Quick Sort on array of {n} elements using Lomuto partition scheme.",
        values={"array": list(a)},
        pseudocode=PSEUDOCODE,
        pseudocode_line=1,
        metrics={"comparisons": 0, "swaps_writes": 0, "time_complexity": "O(n log n)", "space_complexity": "O(log n)"},
        render_data=RenderData(
            mode="bars",
            bars=make_bars(),
            sort_event=SortEvent(
                SortEventType.INIT,
                array=list(a),
                description="Initial array"
            )
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
            pseudocode_line=5,
            metrics={"comparisons": 0, "swaps_writes": 0, "time_complexity": "O(1)", "space_complexity": "O(1)"},
            render_data=RenderData(
                mode="bars",
                bars=make_bars(),
                sort_event=SortEvent(
                    SortEventType.COMPLETE,
                    array=list(a),
                    sorted_indices=list(range(n)),
                    description="Complete"
                )
            )
        ))
        return steps

    def partition(low, high):
        nonlocal step_num, comparisons, swaps
        pivot = a[high]
        step_num += 1
        steps.append(VisualizationStep(
            index=step_num,
            title=f"Select Pivot = A[{high}] ({pivot})",
            equation=f"pivot = A[{high}] = {pivot}",
            explanation=f"Chosen pivot element {pivot} at index {high}. Scanning subarray A[{low}..{high-1}].",
            values={"pivot": pivot, "low": low, "high": high},
            pseudocode=PSEUDOCODE,
            pseudocode_line=7,
            metrics={"comparisons": comparisons, "swaps_writes": swaps, "time_complexity": "O(n log n)", "space_complexity": "O(log n)"},
            render_data=RenderData(
                mode="bars",
                bars=make_bars(active_range=(low, high), pivot_idx=high),
                sort_event=SortEvent(
                    SortEventType.MARK_PIVOT,
                    array=list(a),
                    pivot_index=high,
                    active_range=(low, high),
                    sorted_indices=sorted(list(sorted_indices)),
                    description=f"Select pivot A[{high}] ({pivot})"
                )
            )
        ))

        i = low - 1
        for j in range(low, high):
            comparisons += 1
            step_num += 1
            steps.append(VisualizationStep(
                index=step_num,
                title=f"Compare A[{j}] ({a[j]}) <= Pivot ({pivot})",
                equation=f"A[{j}] ({a[j]}) <= {pivot} ?",
                explanation=f"Checking if element A[{j}]={a[j]} belongs to left partition (<= pivot).",
                values={"j": j, "A[j]": a[j], "pivot": pivot, "i": i},
                pseudocode=PSEUDOCODE,
                pseudocode_line=10,
                metrics={"comparisons": comparisons, "swaps_writes": swaps, "time_complexity": "O(n log n)", "space_complexity": "O(log n)"},
                render_data=RenderData(
                    mode="bars",
                    bars=make_bars(active_range=(low, high), pivot_idx=high, i_idx=i if i >= low else None, j_idx=j),
                    sort_event=SortEvent(
                        SortEventType.COMPARE,
                        array=list(a),
                        indices=[j, high],
                        comparing_indices=(j, high),
                        pivot_index=high,
                        active_range=(low, high),
                        sorted_indices=sorted(list(sorted_indices)),
                        description=f"Compare A[{j}] with pivot {pivot}"
                    )
                )
            ))

            if a[j] <= pivot:
                i += 1
                if i != j:
                    a[i], a[j] = a[j], a[i]
                    swaps += 1
                    step_num += 1
                    steps.append(VisualizationStep(
                        index=step_num,
                        title=f"Swap A[{i}] and A[{j}]",
                        equation=f"swap(A[{i}], A[{j}])",
                        explanation=f"Element {a[i]} <= pivot, swapped into smaller partition at index {i}.",
                        values={"swapped": (i, j)},
                        pseudocode=PSEUDOCODE,
                        pseudocode_line=11,
                        metrics={"comparisons": comparisons, "swaps_writes": swaps, "time_complexity": "O(n log n)", "space_complexity": "O(log n)"},
                        render_data=RenderData(
                            mode="bars",
                            bars=make_bars(active_range=(low, high), pivot_idx=high, swapping=[i, j]),
                            sort_event=SortEvent(
                                SortEventType.SWAP,
                                array=list(a),
                                indices=[i, j],
                                swapping_indices=(i, j),
                                pivot_index=high,
                                active_range=(low, high),
                                sorted_indices=sorted(list(sorted_indices)),
                                description=f"Swap A[{i}] and A[{j}]"
                            )
                        )
                    ))

        # Swap pivot into correct position i + 1
        pivot_pos = i + 1
        a[pivot_pos], a[high] = a[high], a[pivot_pos]
        swaps += 1
        sorted_indices.add(pivot_pos)

        step_num += 1
        steps.append(VisualizationStep(
            index=step_num,
            title=f"Place Pivot at Sorted Position {pivot_pos}",
            equation=f"swap(A[{pivot_pos}], A[{high}]) ⟹ Pivot {pivot} is in final sorted position!",
            explanation=f"Placed pivot {pivot} between elements smaller (left) and larger (right).",
            values={"pivot_final_pos": pivot_pos, "pivot": pivot},
            pseudocode=PSEUDOCODE,
            pseudocode_line=12,
            metrics={"comparisons": comparisons, "swaps_writes": swaps, "time_complexity": "O(n log n)", "space_complexity": "O(log n)"},
            render_data=RenderData(
                mode="bars",
                bars=make_bars(active_range=(low, high), swapping=[pivot_pos, high]),
                sort_event=SortEvent(
                    SortEventType.SWAP,
                    array=list(a),
                    indices=[pivot_pos, high],
                    swapping_indices=(pivot_pos, high),
                    pivot_index=pivot_pos,
                    active_range=(low, high),
                    sorted_indices=sorted(list(sorted_indices)),
                    description=f"Place pivot {pivot} at index {pivot_pos}"
                )
            )
        ))

        return pivot_pos

    def quick_sort(low, high):
        if low < high:
            pi = partition(low, high)
            quick_sort(low, pi - 1)
            quick_sort(pi + 1, high)
        elif low == high:
            sorted_indices.add(low)

    quick_sort(0, n - 1)
    for k in range(n):
        sorted_indices.add(k)

    step_num += 1
    steps.append(VisualizationStep(
        index=step_num,
        title="Sort Complete",
        equation=f"Total Comparisons = {comparisons}, Total Swaps = {swaps}",
        explanation=f"Quick Sort complete: {comparisons} comparisons, {swaps} swaps.",
        values={"final_array": list(a)},
        pseudocode=PSEUDOCODE,
        pseudocode_line=5,
        metrics={"comparisons": comparisons, "swaps_writes": swaps, "time_complexity": "O(n log n)", "space_complexity": "O(log n)"},
        render_data=RenderData(
            mode="bars",
            bars=[{"val": v, "color": COLORS["success"], "tag": "SORTED"} for v in a],
            sort_event=SortEvent(
                SortEventType.COMPLETE,
                array=list(a),
                sorted_indices=list(range(n)),
                description="Complete"
            )
        )
    ))

    return steps
