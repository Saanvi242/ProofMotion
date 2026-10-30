"""
algorithms/sorting/merge_sort.py
--------------------------------
Step-by-step trace generation for Merge Sort.
"""

from typing import List
from core.step_model import VisualizationStep, RenderData
from resources.theme import COLORS
from algorithms.sorting.sorting_events import SortEvent, SortEventType

PSEUDOCODE = [
    "procedure MergeSort(A, left, right):",
    "    if left < right:",
    "        mid = (left + right) / 2",
    "        MergeSort(A, left, mid)",
    "        MergeSort(A, mid + 1, right)",
    "        Merge(A, left, mid, right)",
    "procedure Merge(A, left, mid, right):",
    "    copy left and right halves into L and R",
    "    merge sorted elements back into A[left..right]",
]


def merge_sort_trace(arr: List[int]) -> List[VisualizationStep]:
    a = list(arr)
    n = len(a)
    steps = []
    comparisons = 0
    writes = 0
    step_num = 1

    def make_bars(active_range=None, left_ptr=None, right_ptr=None, writing_idx=None):
        active_range = active_range or (-1, -1)
        bars = []
        for idx, val in enumerate(a):
            tag = ""
            if idx == writing_idx:
                color = COLORS["danger"]
                tag = "WRITE"
            elif idx == left_ptr or idx == right_ptr:
                color = COLORS["accent_gold"]
                tag = "CMP"
            elif active_range[0] <= idx <= active_range[1]:
                color = COLORS["accent_blue"]
                tag = "ACTIVE"
            else:
                color = COLORS["accent_teal"]
            bars.append({"val": val, "color": color, "tag": tag})
        return bars

    steps.append(VisualizationStep(
        index=step_num,
        title="Initial Array",
        equation="A = " + str(a),
        explanation=f"Starting Merge Sort on array with {n} elements. Recursively divides subarrays and merges them.",
        values={"array": list(a)},
        pseudocode=PSEUDOCODE,
        pseudocode_line=1,
        metrics={"comparisons": 0, "swaps_writes": 0, "time_complexity": "O(n log n)", "space_complexity": "O(n)"},
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
            pseudocode_line=6,
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

    def merge(left, mid, right):
        nonlocal step_num, comparisons, writes
        L = a[left:mid + 1]
        R = a[mid + 1:right + 1]

        step_num += 1
        steps.append(VisualizationStep(
            index=step_num,
            title=f"Merge Subarrays: [{left}..{mid}] and [{mid+1}..{right}]",
            equation=f"Merge L={L} and R={R}",
            explanation=f"Merging sorted left sublist A[{left}..{mid}] ({L}) and right sublist A[{mid+1}..{right}] ({R}).",
            values={"left": left, "mid": mid, "right": right, "L": L, "R": R},
            pseudocode=PSEUDOCODE,
            pseudocode_line=8,
            metrics={"comparisons": comparisons, "swaps_writes": writes, "time_complexity": "O(n log n)", "space_complexity": "O(n)"},
            render_data=RenderData(
                mode="bars",
                bars=make_bars(active_range=(left, right)),
                sort_event=SortEvent(
                    SortEventType.MERGE_SPLIT,
                    array=list(a),
                    active_range=(left, right),
                    aux_data={"L": list(L), "R": list(R), "mid": mid},
                    description=f"Merge [{left}..{mid}] and [{mid+1}..{right}]"
                )
            )
        ))

        i = 0
        j = 0
        k = left

        while i < len(L) and j < len(R):
            comparisons += 1
            step_num += 1
            steps.append(VisualizationStep(
                index=step_num,
                title=f"Compare L[{i}] ({L[i]}) and R[{j}] ({R[j]})",
                equation=f"L[{i}] ({L[i]}) <= R[{j}] ({R[j]}) ?",
                explanation=f"Comparing front of left sublist ({L[i]}) with front of right sublist ({R[j]}).",
                values={"L[i]": L[i], "R[j]": R[j], "k": k},
                pseudocode=PSEUDOCODE,
                pseudocode_line=9,
                metrics={"comparisons": comparisons, "swaps_writes": writes, "time_complexity": "O(n log n)", "space_complexity": "O(n)"},
                render_data=RenderData(
                    mode="bars",
                    bars=make_bars(active_range=(left, right), left_ptr=left + i, right_ptr=mid + 1 + j),
                    sort_event=SortEvent(
                        SortEventType.MERGE_COMPARE,
                        array=list(a),
                        active_range=(left, right),
                        indices=[left + i, mid + 1 + j],
                        comparing_indices=(left + i, mid + 1 + j),
                        aux_data={"L_val": L[i], "R_val": R[j], "target_k": k},
                        description=f"Compare L[{i}] ({L[i]}) and R[{j}] ({R[j]})"
                    )
                )
            ))

            if L[i] <= R[j]:
                a[k] = L[i]
                i += 1
            else:
                a[k] = R[j]
                j += 1

            writes += 1
            step_num += 1
            steps.append(VisualizationStep(
                index=step_num,
                title=f"Write {a[k]} to A[{k}]",
                equation=f"A[{k}] = {a[k]}",
                explanation=f"Placed smaller element {a[k]} into merged position A[{k}].",
                values={"k": k, "val": a[k]},
                pseudocode=PSEUDOCODE,
                pseudocode_line=9,
                metrics={"comparisons": comparisons, "swaps_writes": writes, "time_complexity": "O(n log n)", "space_complexity": "O(n)"},
                render_data=RenderData(
                    mode="bars",
                    bars=make_bars(active_range=(left, right), writing_idx=k),
                    sort_event=SortEvent(
                        SortEventType.MERGE_WRITE,
                        array=list(a),
                        active_range=(left, right),
                        target_index=k,
                        indices=[k],
                        aux_data={"written_val": a[k]},
                        description=f"Write {a[k]} to A[{k}]"
                    )
                )
            ))
            k += 1

        while i < len(L):
            a[k] = L[i]
            writes += 1
            step_num += 1
            steps.append(VisualizationStep(
                index=step_num,
                title=f"Copy remaining L[{i}] ({L[i]}) to A[{k}]",
                equation=f"A[{k}] = {a[k]}",
                explanation=f"Copied remaining element from left subarray into A[{k}].",
                values={"k": k, "val": a[k]},
                pseudocode=PSEUDOCODE,
                pseudocode_line=9,
                metrics={"comparisons": comparisons, "swaps_writes": writes, "time_complexity": "O(n log n)", "space_complexity": "O(n)"},
                render_data=RenderData(
                    mode="bars",
                    bars=make_bars(active_range=(left, right), writing_idx=k),
                    sort_event=SortEvent(
                        SortEventType.MERGE_WRITE,
                        array=list(a),
                        active_range=(left, right),
                        target_index=k,
                        indices=[k],
                        aux_data={"written_val": a[k]},
                        description=f"Copy remaining L[{i}] ({L[i]}) to A[{k}]"
                    )
                )
            ))
            i += 1
            k += 1

        while j < len(R):
            a[k] = R[j]
            writes += 1
            step_num += 1
            steps.append(VisualizationStep(
                index=step_num,
                title=f"Copy remaining R[{j}] ({R[j]}) to A[{k}]",
                equation=f"A[{k}] = {a[k]}",
                explanation=f"Copied remaining element from right subarray into A[{k}].",
                values={"k": k, "val": a[k]},
                pseudocode=PSEUDOCODE,
                pseudocode_line=9,
                metrics={"comparisons": comparisons, "swaps_writes": writes, "time_complexity": "O(n log n)", "space_complexity": "O(n)"},
                render_data=RenderData(
                    mode="bars",
                    bars=make_bars(active_range=(left, right), writing_idx=k),
                    sort_event=SortEvent(
                        SortEventType.MERGE_WRITE,
                        array=list(a),
                        active_range=(left, right),
                        target_index=k,
                        indices=[k],
                        aux_data={"written_val": a[k]},
                        description=f"Copy remaining R[{j}] ({R[j]}) to A[{k}]"
                    )
                )
            ))
            j += 1
            k += 1

    def divide(left, right):
        nonlocal step_num
        if left < right:
            mid = (left + right) // 2
            step_num += 1
            steps.append(VisualizationStep(
                index=step_num,
                title=f"Divide A[{left}..{right}] at mid={mid}",
                equation=f"Split [{left}..{mid}] and [{mid+1}..{right}]",
                explanation=f"Subarray A[{left}..{right}] divided into left half [{left}..{mid}] and right half [{mid+1}..{right}].",
                values={"left": left, "mid": mid, "right": right},
                pseudocode=PSEUDOCODE,
                pseudocode_line=3,
                metrics={"comparisons": comparisons, "swaps_writes": writes, "time_complexity": "O(n log n)", "space_complexity": "O(n)"},
                render_data=RenderData(
                    mode="bars",
                    bars=make_bars(active_range=(left, right)),
                    sort_event=SortEvent(
                        SortEventType.MERGE_SPLIT,
                        array=list(a),
                        active_range=(left, right),
                        aux_data={"mid": mid},
                        description=f"Divide [{left}..{mid}] and [{mid+1}..{right}]"
                    )
                )
            ))
            divide(left, mid)
            divide(mid + 1, right)
            merge(left, mid, right)

    divide(0, n - 1)

    step_num += 1
    # All sorted bars
    all_sorted = [{"val": v, "color": COLORS["success"], "tag": "SORTED"} for v in a]
    steps.append(VisualizationStep(
        index=step_num,
        title="Sort Complete",
        equation=f"Comparisons = {comparisons}, Writes = {writes}",
        explanation=f"Merge Sort finished: {comparisons} comparisons, {writes} writes.",
        values={"final_array": list(a)},
        pseudocode=PSEUDOCODE,
        pseudocode_line=6,
        metrics={"comparisons": comparisons, "swaps_writes": writes, "time_complexity": "O(n log n)", "space_complexity": "O(n)"},
        render_data=RenderData(
            mode="bars",
            bars=all_sorted,
            sort_event=SortEvent(
                SortEventType.COMPLETE,
                array=list(a),
                sorted_indices=list(range(n)),
                description="Complete"
            )
        )
    ))

    return steps
