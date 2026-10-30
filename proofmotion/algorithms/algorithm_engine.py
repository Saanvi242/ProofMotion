"""
algorithms/algorithm_engine.py
------------------------------
Coordinator for Sorting and Searching Algorithm visualizations.
"""

from typing import List, Dict, Tuple, Any
from core.step_model import VisualizationStep
from algorithms.sorting.bubble_sort import bubble_sort_trace
from algorithms.sorting.selection_sort import selection_sort_trace
from algorithms.sorting.insertion_sort import insertion_sort_trace
from algorithms.sorting.merge_sort import merge_sort_trace
from algorithms.sorting.quick_sort import quick_sort_trace
from algorithms.searching.linear_search import linear_search_trace
from algorithms.searching.binary_search import binary_search_trace


ALGORITHMS = {
    "bubble_sort": {
        "name": "Bubble Sort",
        "category": "sorting",
        "description": "Repeatedly steps through the list, compares adjacent elements and swaps them if in wrong order.",
        "time_best": "O(n)", "time_avg": "O(n²)", "time_worst": "O(n²)", "space": "O(1)",
    },
    "selection_sort": {
        "name": "Selection Sort",
        "category": "sorting",
        "description": "Divides input into sorted and unsorted regions, repeatedly finding the minimum element.",
        "time_best": "O(n²)", "time_avg": "O(n²)", "time_worst": "O(n²)", "space": "O(1)",
    },
    "insertion_sort": {
        "name": "Insertion Sort",
        "category": "sorting",
        "description": "Builds sorted array one item at a time by inserting each into its proper place.",
        "time_best": "O(n)", "time_avg": "O(n²)", "time_worst": "O(n²)", "space": "O(1)",
    },
    "merge_sort": {
        "name": "Merge Sort",
        "category": "sorting",
        "description": "Divide-and-conquer algorithm that halves the list, sorts sublists, and merges them.",
        "time_best": "O(n log n)", "time_avg": "O(n log n)", "time_worst": "O(n log n)", "space": "O(n)",
    },
    "quick_sort": {
        "name": "Quick Sort",
        "category": "sorting",
        "description": "Selects a pivot, partitions elements into smaller and larger, and recurses.",
        "time_best": "O(n log n)", "time_avg": "O(n log n)", "time_worst": "O(n²)", "space": "O(log n)",
    },
    "linear_search": {
        "name": "Linear Search",
        "category": "searching",
        "description": "Sequentially checks every element in the list until target is found or end reached.",
        "time_best": "O(1)", "time_avg": "O(n)", "time_worst": "O(n)", "space": "O(1)",
    },
    "binary_search": {
        "name": "Binary Search",
        "category": "searching",
        "description": "Efficiently searches a sorted array by repeatedly halving the search interval.",
        "time_best": "O(1)", "time_avg": "O(log n)", "time_worst": "O(log n)", "space": "O(1)",
    },
}


class AlgorithmEngine:
    @staticmethod
    def get_algorithm_list():
        return [(k, v["name"], v["category"]) for k, v in ALGORITHMS.items()]

    @staticmethod
    def get_info(algo_key: str) -> Dict[str, Any]:
        return ALGORITHMS.get(algo_key, {})

    @staticmethod
    def run_sorting(algo_key: str, arr: List[int]) -> List[VisualizationStep]:
        if algo_key == "bubble_sort":
            return bubble_sort_trace(arr)
        elif algo_key == "selection_sort":
            return selection_sort_trace(arr)
        elif algo_key == "insertion_sort":
            return insertion_sort_trace(arr)
        elif algo_key == "merge_sort":
            return merge_sort_trace(arr)
        elif algo_key == "quick_sort":
            return quick_sort_trace(arr)
        raise ValueError(f"Unknown sorting algorithm: {algo_key}")

    @staticmethod
    def run_searching(algo_key: str, arr: List[int], target: int) -> List[VisualizationStep]:
        if algo_key == "linear_search":
            return linear_search_trace(arr, target)
        elif algo_key == "binary_search":
            steps, _ = binary_search_trace(arr, target)
            return steps
        raise ValueError(f"Unknown searching algorithm: {algo_key}")
