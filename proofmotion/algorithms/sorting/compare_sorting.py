"""
algorithms/sorting/compare_sorting.py
-------------------------------------
Side-by-side interactive comparison for sorting algorithms.
Executes any two sorting algorithms on the exact same array concurrently,
synchronizing their comparative operations, metrics, and pedagogical insights.
"""

from typing import List, Dict, Any, Optional
from copy import deepcopy
from core.step_model import VisualizationStep, RenderData
from algorithms.sorting.bubble_sort import bubble_sort_trace
from algorithms.sorting.selection_sort import selection_sort_trace
from algorithms.sorting.insertion_sort import insertion_sort_trace
from algorithms.sorting.merge_sort import merge_sort_trace
from algorithms.sorting.quick_sort import quick_sort_trace
from resources.theme import COLORS

SORT_RUNNERS = {
    "bubble_sort": bubble_sort_trace,
    "selection_sort": selection_sort_trace,
    "insertion_sort": insertion_sort_trace,
    "merge_sort": merge_sort_trace,
    "quick_sort": quick_sort_trace,
}

ALGO_INFO = {
    "bubble_sort": {"time_avg": "O(n²)", "space": "O(1)"},
    "selection_sort": {"time_avg": "O(n²)", "space": "O(1)"},
    "insertion_sort": {"time_avg": "O(n²)", "space": "O(1)"},
    "merge_sort": {"time_avg": "O(n log n)", "space": "O(n)"},
    "quick_sort": {"time_avg": "O(n log n)", "space": "O(log n)"},
}

ALGO_DISPLAY_NAMES = {
    "bubble_sort": "Bubble Sort",
    "selection_sort": "Selection Sort",
    "insertion_sort": "Insertion Sort",
    "merge_sort": "Merge Sort",
    "quick_sort": "Quick Sort",
}

NAME_TO_KEY = {
    "Bubble Sort": "bubble_sort",
    "Selection Sort": "selection_sort",
    "Insertion Sort": "insertion_sort",
    "Merge Sort": "merge_sort",
    "Quick Sort": "quick_sort",
    "bubble_sort": "bubble_sort",
    "selection_sort": "selection_sort",
    "insertion_sort": "insertion_sort",
    "merge_sort": "merge_sort",
    "quick_sort": "quick_sort",
}


def compare_sorting_trace(algo_1: str = "bubble_sort",
                          algo_2: str = "quick_sort",
                          arr: Optional[List[int]] = None) -> List[VisualizationStep]:
    """
    Generate synchronized side-by-side comparison steps between two sorting algorithms
    on the identical input array.
    """
    k1 = NAME_TO_KEY.get(str(algo_1).strip(), "bubble_sort")
    k2 = NAME_TO_KEY.get(str(algo_2).strip(), "quick_sort")

    if not arr or len(arr) < 2:
        arr = [34, 12, 89, 5, 23, 77, 45, 18, 62, 9]

    # Generate individual deterministic traces
    runner_1 = SORT_RUNNERS.get(k1, bubble_sort_trace)
    runner_2 = SORT_RUNNERS.get(k2, quick_sort_trace)
    trace_1 = runner_1(list(arr))
    trace_2 = runner_2(list(arr))

    name_1 = ALGO_DISPLAY_NAMES.get(k1, "Algorithm 1")
    name_2 = ALGO_DISPLAY_NAMES.get(k2, "Algorithm 2")

    info_1 = ALGO_INFO.get(k1, {})
    info_2 = ALGO_INFO.get(k2, {})

    total_steps = max(len(trace_1), len(trace_2))

    # Precalculate final metrics to determine overall winner
    final_1 = trace_1[-1]
    final_2 = trace_2[-1]
    tot_cmps_1 = final_1.metrics.get("comparisons", 0)
    tot_cmps_2 = final_2.metrics.get("comparisons", 0)
    tot_swaps_1 = final_1.metrics.get("swaps_writes", 0)
    tot_swaps_2 = final_2.metrics.get("swaps_writes", 0)

    if tot_cmps_1 < tot_cmps_2:
        overall_winner = name_1
        ratio = tot_cmps_2 / max(1, tot_cmps_1)
    elif tot_cmps_2 < tot_cmps_1:
        overall_winner = name_2
        ratio = tot_cmps_1 / max(1, tot_cmps_2)
    else:
        overall_winner = "Tie"
        ratio = 1.0

    steps: List[VisualizationStep] = []

    for i in range(total_steps):
        s1 = trace_1[min(i, len(trace_1) - 1)]
        s2 = trace_2[min(i, len(trace_2) - 1)]

        done_1 = (i >= len(trace_1) - 1)
        done_2 = (i >= len(trace_2) - 1)

        # Clone bars and ensure sorted coloring once completed
        raw_bars_1 = s1.render_data.bars if (s1.render_data and s1.render_data.bars) else []
        raw_bars_2 = s2.render_data.bars if (s2.render_data and s2.render_data.bars) else []

        bars_1 = [dict(b) for b in raw_bars_1]
        bars_2 = [dict(b) for b in raw_bars_2]

        if done_1:
            for b in bars_1:
                b["color"] = COLORS["success"]
                b["tag"] = "SORTED"

        if done_2:
            for b in bars_2:
                b["color"] = COLORS["success"]
                b["tag"] = "SORTED"

        c1 = s1.metrics.get("comparisons", 0)
        w1 = s1.metrics.get("swaps_writes", 0)
        c2 = s2.metrics.get("comparisons", 0)
        w2 = s2.metrics.get("swaps_writes", 0)

        # Real-time leader based on current comparisons
        if done_1 and not done_2:
            current_leader = f"{name_1} (Completed First)"
        elif done_2 and not done_1:
            current_leader = f"{name_2} (Completed First)"
        elif c1 < c2:
            current_leader = f"{name_1} ({c2 - c1} fewer comparisons)"
        elif c2 < c1:
            current_leader = f"{name_2} ({c1 - c2} fewer comparisons)"
        else:
            current_leader = "Even Pace"

        is_final = (i == total_steps - 1)

        comp_data = {
            "type": "sorting",
            "algo_1": {
                "key": k1,
                "name": name_1,
                "complexity": info_1.get("time_avg", "O(n²)"),
                "space": info_1.get("space", "O(1)"),
                "step": min(i + 1, len(trace_1)),
                "total_steps": len(trace_1),
                "done": done_1,
                "comparisons": c1,
                "swaps": w1,
                "bars": bars_1,
                "status_text": "Completed (Sorted)" if done_1 else getattr(s1, "title", "Processing"),
                "event_line": getattr(s1, "equation", ""),
            },
            "algo_2": {
                "key": k2,
                "name": name_2,
                "complexity": info_2.get("time_avg", "O(n log n)"),
                "space": info_2.get("space", "O(log n)"),
                "step": min(i + 1, len(trace_2)),
                "total_steps": len(trace_2),
                "done": done_2,
                "comparisons": c2,
                "swaps": w2,
                "bars": bars_2,
                "status_text": "Completed (Sorted)" if done_2 else getattr(s2, "title", "Processing"),
                "event_line": getattr(s2, "equation", ""),
            },
            "summary": {
                "step": i + 1,
                "total_steps": total_steps,
                "is_finished": is_final,
                "winner": overall_winner if is_final else current_leader,
                "ratio": f"{ratio:.1f}×" if overall_winner != "Tie" else "1.0×",
            }
        }

        # Step narratives
        if i == 0:
            title = f"Comparison Setup — {name_1} vs {name_2}"
            equation = f"{name_1} ({info_1.get('time_avg', 'O(n²)')})  vs  {name_2} ({info_2.get('time_avg', 'O(n log n)')})"
            explanation = (
                f"Side-by-Side Algorithm Benchmark:\n\n"
                f"Both {name_1} and {name_2} will process the exact same {len(arr)}-element array.\n\n"
                f"• Left: {name_1} — Average Complexity: {info_1.get('time_avg', 'O(n²)')}, Space: {info_1.get('space', 'O(1)')}\n"
                f"• Right: {name_2} — Average Complexity: {info_2.get('time_avg', 'O(n log n)')}, Space: {info_2.get('space', 'O(log n)')}\n\n"
                f"Observe how each algorithm organizes operations, how quickly it reduces disorder, "
                f"and which approach minimizes pairwise comparisons and array swaps."
            )
        elif is_final:
            title = f"Comparison Complete — {overall_winner} Faster"
            equation = f"Final Result: {overall_winner} finished with {ratio:.1f}× fewer comparisons!"
            explanation = (
                f"Execution Performance Summary:\n\n"
                f"• {name_1}: {tot_cmps_1} comparisons, {tot_swaps_1} swaps/writes in {len(trace_1)} steps.\n"
                f"• {name_2}: {tot_cmps_2} comparisons, {tot_swaps_2} swaps/writes in {len(trace_2)} steps.\n\n"
                f"Pedagogical Takeaway:\n"
                f"{overall_winner} outperforms {name_2 if overall_winner == name_1 else name_1} on this input "
                f"because its algorithmic structure ({info_1.get('time_avg') if overall_winner == name_1 else info_2.get('time_avg')}) "
                f"avoids redundant pairwise element scans across sorted prefixes/subarrays."
            )
        else:
            title = f"Step {i + 1}/{total_steps} — {name_1} vs {name_2}"
            equation = f"{name_1}: {c1} cmps, {w1} swaps  |  {name_2}: {c2} cmps, {w2} swaps"
            
            s1_msg = f"{name_1}: Completed in {len(trace_1)} steps." if done_1 else f"{name_1} (Step {i+1}/{len(trace_1)}): {s1.title}"
            s2_msg = f"{name_2}: Completed in {len(trace_2)} steps." if done_2 else f"{name_2} (Step {i+1}/{len(trace_2)}): {s2.title}"
            explanation = f"{s1_msg}\n{s2_msg}\n\nCurrent Comparisons Leader: {current_leader}."

        step_obj = VisualizationStep(
            index=i + 1,
            title=title,
            equation=equation,
            explanation=explanation,
            values={
                "algo_1": name_1,
                "algo_2": name_2,
                "cmps_1": c1,
                "cmps_2": c2,
                "swaps_1": w1,
                "swaps_2": w2,
                "done_1": done_1,
                "done_2": done_2,
            },
            render_data=RenderData(mode="comparison", comparison_data=comp_data),
            metrics={
                f"{name_1} Comparisons": c1,
                f"{name_1} Swaps": w1,
                f"{name_2} Comparisons": c2,
                f"{name_2} Swaps": w2,
                "Leading Algorithm": current_leader,
            }
        )
        steps.append(step_obj)

    return steps
