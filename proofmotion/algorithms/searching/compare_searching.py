"""
algorithms/searching/compare_searching.py
-----------------------------------------
Side-by-side interactive comparison between Linear Search and Binary Search.
Executes both searching paradigms on the exact same array and target value simultaneously,
demonstrating the exponential speedup of interval halving (O(log n)) over sequential scanning (O(n)).
"""

from typing import List, Dict, Any, Optional
from core.step_model import VisualizationStep, RenderData
from algorithms.searching.linear_search import linear_search_trace
from algorithms.searching.binary_search import binary_search_trace
from resources.theme import COLORS


def compare_searching_trace(arr: Optional[List[int]] = None,
                            target: int = 23) -> List[VisualizationStep]:
    """
    Generate synchronized side-by-side comparison steps between Linear Search and Binary Search
    for the exact same target value.
    """
    if not arr or len(arr) < 2:
        arr = [4, 8, 15, 16, 23, 30, 42, 55, 68]

    # For binary search, the array must be sorted; for fair comparison on unsorted, sort both
    sorted_arr = sorted(arr)
    
    linear_steps = linear_search_trace(sorted_arr, target)
    binary_steps, _ = binary_search_trace(sorted_arr, target)

    total_steps = max(len(linear_steps), len(binary_steps))

    lin_final = linear_steps[-1]
    bin_final = binary_steps[-1]
    tot_cmps_lin = lin_final.metrics.get("comparisons", 0)
    tot_cmps_bin = bin_final.metrics.get("comparisons", 0)

    ratio = tot_cmps_lin / max(1, tot_cmps_bin)

    steps: List[VisualizationStep] = []

    for i in range(total_steps):
        s_lin = linear_steps[min(i, len(linear_steps) - 1)]
        s_bin = binary_steps[min(i, len(binary_steps) - 1)]

        done_lin = (i >= len(linear_steps) - 1)
        done_bin = (i >= len(binary_steps) - 1)

        c_lin = s_lin.metrics.get("comparisons", 0)
        c_bin = s_bin.metrics.get("comparisons", 0)

        is_final = (i == total_steps - 1)

        comp_data = {
            "type": "searching",
            "target": target,
            "algo_1": {
                "key": "linear_search",
                "name": "Linear Search",
                "complexity": "O(n)",
                "space": "O(1)",
                "step": min(i + 1, len(linear_steps)),
                "total_steps": len(linear_steps),
                "done": done_lin,
                "comparisons": c_lin,
                "search_data": s_lin.render_data.search_data if (s_lin.render_data and s_lin.render_data.search_data) else {},
                "status_text": "Target Found!" if s_lin.metrics.get("found") else ("Done (Not Found)" if done_lin else s_lin.title),
                "event_line": getattr(s_lin, "equation", ""),
            },
            "algo_2": {
                "key": "binary_search",
                "name": "Binary Search",
                "complexity": "O(log n)",
                "space": "O(1)",
                "step": min(i + 1, len(binary_steps)),
                "total_steps": len(binary_steps),
                "done": done_bin,
                "comparisons": c_bin,
                "search_data": s_bin.render_data.search_data if (s_bin.render_data and s_bin.render_data.search_data) else {},
                "status_text": "Target Found!" if s_bin.metrics.get("found") else ("Done (Not Found)" if done_bin else s_bin.title),
                "event_line": getattr(s_bin, "equation", ""),
            },
            "summary": {
                "step": i + 1,
                "total_steps": total_steps,
                "is_finished": is_final,
                "winner": "Binary Search" if tot_cmps_bin < tot_cmps_lin else "Linear Search",
                "ratio": f"{ratio:.1f}×",
            }
        }

        if i == 0:
            title = f"Search Comparison — Linear vs Binary Search (Target = {target})"
            equation = f"Linear Search (O(n))  vs  Binary Search (O(log n))"
            explanation = (
                f"Sequential Scanning vs Interval Halving:\n\n"
                f"Both algorithms are searching for target value {target} inside a {len(sorted_arr)}-element array.\n\n"
                f"• Left: Linear Search checks elements sequentially one by one from left to right (Worst case: n comparisons).\n"
                f"• Right: Binary Search inspects the midpoint and eliminates half the search space on every comparison (Worst case: ⌈log₂ n⌉ + 1 comparisons).\n\n"
                f"Watch how rapidly Binary Search narrows the search boundary compared to Linear Search."
            )
        elif is_final:
            title = f"Search Comparison Complete — Binary Search Won"
            equation = f"Binary Search found target in {tot_cmps_bin} comparisons vs {tot_cmps_lin} for Linear Search ({ratio:.1f}× faster)!"
            explanation = (
                f"Search Efficiency Verdict:\n\n"
                f"• Binary Search: Found target in {len(binary_steps)} steps using only {tot_cmps_bin} comparisons.\n"
                f"• Linear Search: Completed in {len(linear_steps)} steps using {tot_cmps_lin} comparisons.\n\n"
                f"Theoretical Principle:\n"
                f"Because the array was sorted, Binary Search eliminated 50% of the candidate items at each decision step, "
                f"achieving logarithmic efficiency O(log n)."
            )
        else:
            title = f"Step {i + 1}/{total_steps} — Comparing Search Progress"
            equation = f"Linear Search: {c_lin} cmps | Binary Search: {c_bin} cmps"
            explanation = (
                f"Linear Search: {'Completed' if done_lin else s_lin.title}\n"
                f"Binary Search: {'Completed' if done_bin else s_bin.title}\n"
                f"Comparisons so far: Linear ({c_lin}) vs Binary ({c_bin})."
            )

        step_obj = VisualizationStep(
            index=i + 1,
            title=title,
            equation=equation,
            explanation=explanation,
            values={"target": target, "c_lin": c_lin, "c_bin": c_bin},
            render_data=RenderData(mode="comparison", comparison_data=comp_data),
            metrics={
                "Linear Search Comparisons": c_lin,
                "Binary Search Comparisons": c_bin,
                "Target Value": target,
                "Faster Method": "Binary Search",
            }
        )
        steps.append(step_obj)

    return steps
