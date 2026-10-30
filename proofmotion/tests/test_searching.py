"""
tests/test_searching.py
-----------------------
Unit tests for Linear and Binary Search.
"""

import unittest
from algorithms.searching.linear_search import linear_search_trace
from algorithms.searching.binary_search import binary_search_trace


class TestSearching(unittest.TestCase):
    def test_linear_search_present(self):
        arr = [10, 25, 30, 45, 50]
        steps = linear_search_trace(arr, 30)
        last_step = steps[-1]
        self.assertEqual(last_step.values.get("found_index"), 2)
        # Verify tile search_data
        self.assertIsNotNone(last_step.render_data.search_data)
        self.assertEqual(last_step.render_data.search_data["type"], "linear")
        self.assertEqual(last_step.render_data.search_data["found_index"], 2)

    def test_linear_search_absent(self):
        arr = [10, 25, 30, 45, 50]
        steps = linear_search_trace(arr, 99)
        last_step = steps[-1]
        self.assertEqual(last_step.values.get("found_index"), -1)
        self.assertEqual(last_step.render_data.search_data["found_index"], -1)

    def test_linear_search_empty(self):
        steps = linear_search_trace([], 42)
        last_step = steps[-1]
        self.assertEqual(last_step.values.get("found_index"), -1)

    def test_binary_search_present(self):
        arr = [5, 12, 19, 23, 35, 42, 60]
        steps, _ = binary_search_trace(arr, 23)
        last_step = steps[-1]
        self.assertEqual(last_step.values.get("found_index"), 3)
        # Verify tile search_data
        self.assertIsNotNone(last_step.render_data.search_data)
        self.assertEqual(last_step.render_data.search_data["type"], "binary")
        self.assertEqual(last_step.render_data.search_data["found_index"], 3)

    def test_binary_search_absent(self):
        arr = [5, 12, 19, 23, 35, 42, 60]
        steps, _ = binary_search_trace(arr, 50)
        last_step = steps[-1]
        self.assertFalse(last_step.values.get("found", False))

    def test_binary_search_auto_sorts_unsorted(self):
        arr = [42, 12, 5, 60, 23]
        steps, was_sorted = binary_search_trace(arr, 23)
        self.assertFalse(was_sorted)
        last_step = steps[-1]
        self.assertEqual(last_step.values.get("found_index"), 2) # in [5, 12, 23, 42, 60], 23 is index 2


if __name__ == "__main__":
    unittest.main()
