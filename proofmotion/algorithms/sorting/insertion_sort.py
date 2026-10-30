"""
algorithms/sorting/insertion_sort.py
------------------------------------
Step-by-step trace generation for Insertion Sort.
"""

from typing import List
from core.step_model import VisualizationStep, RenderData
from resources.theme import COLORS
from algorithms.sorting.sorting_events import SortEvent, SortEventType

PSEUDOCODE = [
    "procedure InsertionSort(A):",
    "    n = length(A)",
    "    for i from 1 to n - 1:",
    "        key = A[i]",
    "        j = i - 1",
    "        while j >= 0 and A[j] > key:",
    "            A[j + 1] = A[j]",
    "            j = j - 1",
    "        A[j + 1] = key",
    "    return A",
]


def insertion_sort_trace(arr: List[int]) -> List[VisualizationStep]:
    a = list(arr)
    n = len(a)
    steps = []
    comparisons = 0
    writes = 0

    def make_bars(key_idx=None, j_idx=None, sorted_up_to=0, moving_idx=None):
        bars = []
        for idx, val in enumerate(a):
            tag = ""
            if idx == key_idx:
                color = COLORS["accent_gold"]
                tag = "KEY"
            elif idx == moving_idx:
                color = COLORS["danger"]
                tag = "SHIFT"
            elif idx == j_idx:
                color = COLORS["accent_blue"]
                tag = "CMP"
            elif idx <= sorted_up_to:
                color = COLORS["success"]
                tag = "SORTED"
            else:
                color = COLORS["accent_teal"]
            bars.append({"val": val, "color": color, "tag": tag})
        return bars

    step_num = 1
    steps.append(VisualizationStep(
        index=step_num,
        title="Initial Array",
        equation="A = " + str(a),
        explanation=f"Starting Insertion Sort with {n} elements. Index 0 is trivially a sorted subarray of size 1.",
        values={"array": list(a)},
        pseudocode=PSEUDOCODE,
        pseudocode_line=1,
        metrics={"comparisons": 0, "swaps_writes": 0, "time_complexity": "O(n²)", "space_complexity": "O(1)"},
        render_data=RenderData(
            mode="bars",
            bars=make_bars(sorted_up_to=0),
            sort_event=SortEvent(
                SortEventType.INIT,
                array=list(a),
                sorted_indices=[0] if n > 0 else [],
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
            pseudocode_line=10,
            metrics={"comparisons": 0, "swaps_writes": 0, "time_complexity": "O(1)", "space_complexity": "O(1)"},
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

    for i in range(1, n):
        key = a[i]
        step_num += 1
        steps.append(VisualizationStep(
            index=step_num,
            title=f"Select Key = A[{i}] ({key})",
            equation=f"key = A[{i}] = {key}",
            explanation=f"Picking element at index {i} (value {key}) to insert into sorted prefix A[0..{i-1}].",
            values={"i": i, "key": key},
            pseudocode=PSEUDOCODE,
            pseudocode_line=4,
            metrics={"comparisons": comparisons, "swaps_writes": writes, "time_complexity": "O(n²)", "space_complexity": "O(1)"},
            render_data=RenderData(
                mode="bars",
                bars=make_bars(key_idx=i, sorted_up_to=i-1),
                sort_event=SortEvent(
                    SortEventType.SELECT_MIN,
                    array=list(a),
                    key_index=i,
                    indices=[i],
                    sorted_indices=list(range(i)),
                    description=f"Select key {key} at {i}"
                )
            )
        ))

        j = i - 1
        while j >= 0:
            comparisons += 1
            step_num += 1
            steps.append(VisualizationStep(
                index=step_num,
                title=f"Compare A[{j}] ({a[j]}) with Key ({key})",
                equation=f"A[{j}] ({a[j]}) > key ({key}) ?",
                explanation=f"Testing if A[{j}]={a[j]} is larger than key={key}.",
                values={"j": j, "A[j]": a[j], "key": key},
                pseudocode=PSEUDOCODE,
                pseudocode_line=6,
                metrics={"comparisons": comparisons, "swaps_writes": writes, "time_complexity": "O(n²)", "space_complexity": "O(1)"},
                render_data=RenderData(
                    mode="bars",
                    bars=make_bars(key_idx=i, j_idx=j, sorted_up_to=i-1),
                    sort_event=SortEvent(
                        SortEventType.COMPARE,
                        array=list(a),
                        key_index=i,
                        indices=[j, i],
                        comparing_indices=(j, i),
                        sorted_indices=list(range(i)),
                        description=f"Compare A[{j}] with key {key}"
                    )
                )
            ))

            if a[j] > key:
                a[j + 1] = a[j]
                writes += 1
                step_num += 1
                steps.append(VisualizationStep(
                    index=step_num,
                    title=f"Shift A[{j}] ({a[j]}) to index {j+1}",
                    equation=f"A[{j+1}] = A[{j}] ({a[j]})",
                    explanation=f"{a[j]} > {key}, so shift {a[j]} one spot to the right to open space.",
                    values={"shifted_to": j + 1, "value": a[j]},
                    pseudocode=PSEUDOCODE,
                    pseudocode_line=7,
                    metrics={"comparisons": comparisons, "swaps_writes": writes, "time_complexity": "O(n²)", "space_complexity": "O(1)"},
                    render_data=RenderData(
                        mode="bars",
                        bars=make_bars(moving_idx=j+1, j_idx=j, sorted_up_to=i-1),
                        sort_event=SortEvent(
                            SortEventType.SHIFT,
                            array=list(a),
                            moving_index=j,
                            target_index=j + 1,
                            indices=[j, j + 1],
                            sorted_indices=list(range(i)),
                            description=f"Shift {a[j+1]} to index {j+1}"
                        )
                    )
                ))
                j -= 1
            else:
                break

        a[j + 1] = key
        writes += 1
        step_num += 1
        steps.append(VisualizationStep(
            index=step_num,
            title=f"Insert Key ({key}) at index {j+1}",
            equation=f"A[{j+1}] = key ({key})",
            explanation=f"Found correct insertion position. Inserted key {key} at index {j+1}.",
            values={"inserted_at": j + 1, "key": key},
            pseudocode=PSEUDOCODE,
            pseudocode_line=9,
            metrics={"comparisons": comparisons, "swaps_writes": writes, "time_complexity": "O(n²)", "space_complexity": "O(1)"},
            render_data=RenderData(
                mode="bars",
                bars=make_bars(sorted_up_to=i),
                sort_event=SortEvent(
                    SortEventType.SWAP,
                    array=list(a),
                    target_index=j + 1,
                    indices=[j + 1],
                    sorted_indices=list(range(i + 1)),
                    description=f"Insert key {key} at {j+1}"
                )
            )
        ))

    step_num += 1
    steps.append(VisualizationStep(
        index=step_num,
        title="Sort Complete",
        equation=f"Total Comparisons = {comparisons}, Total Shifts/Writes = {writes}",
        explanation=f"Insertion Sort complete. {comparisons} comparisons and {writes} writes.",
        values={"final_array": list(a)},
        pseudocode=PSEUDOCODE,
        pseudocode_line=10,
        metrics={"comparisons": comparisons, "swaps_writes": writes, "time_complexity": "O(n²)", "space_complexity": "O(1)"},
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
