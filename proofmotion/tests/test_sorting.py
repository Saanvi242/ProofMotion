"""
tests/test_sorting.py
---------------------
Unit tests for Sorting Algorithms:
Bubble, Selection, Insertion, Merge, Quick Sort.
"""

import unittest
from algorithms.sorting.bubble_sort import bubble_sort_trace
from algorithms.sorting.selection_sort import selection_sort_trace
from algorithms.sorting.insertion_sort import insertion_sort_trace
from algorithms.sorting.merge_sort import merge_sort_trace
from algorithms.sorting.quick_sort import quick_sort_trace


class TestSorting(unittest.TestCase):
    def setUp(self):
        self.algorithms = [
            ("Bubble Sort", bubble_sort_trace),
            ("Selection Sort", selection_sort_trace),
            ("Insertion Sort", insertion_sort_trace),
            ("Merge Sort", merge_sort_trace),
            ("Quick Sort", quick_sort_trace),
        ]
        self.test_cases = [
            [],
            [42],
            [1, 2, 3, 4, 5],
            [5, 4, 3, 2, 1],
            [3, 1, 4, 1, 5, 9, 2, 6, 5], # duplicates
            [-10, 5, -3, 0, 12, -1],     # negative numbers
            [15, 3, 9, 8, 2, 10, 14, 7],
        ]

    def test_all_sorting_algorithms(self):
        for name, algo_func in self.algorithms:
            with self.subTest(algorithm=name):
                for arr in self.test_cases:
                    expected = sorted(arr)
                    steps = algo_func(arr)
                    self.assertGreater(len(steps), 0)
                    last_step = steps[-1]
                    final_arr = last_step.values.get("final_array", last_step.values.get("array"))
                    self.assertEqual(final_arr, expected, f"Failed on {name} with input {arr}")


if __name__ == "__main__":
    unittest.main()
