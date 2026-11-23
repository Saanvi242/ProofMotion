"""
tests/test_algorithm_comparison.py
-----------------------------------
Unit and integration tests for Algorithm Comparison feature:
- Side-by-side sorting comparison (Bubble, Selection, Insertion, Merge, Quick)
- Side-by-side searching comparison (Linear Search vs Binary Search)
- AlgorithmEngine comparison hooks
- ApplicationController and ParameterPanel integration
- VisualizationWidget comparison rendering without crashes
"""

import unittest
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap, QPainter

from algorithms.sorting.compare_sorting import (
    compare_sorting_trace,
    SORT_RUNNERS,
    ALGO_INFO,
    ALGO_DISPLAY_NAMES,
)
from algorithms.searching.compare_searching import compare_searching_trace
from algorithms.algorithm_engine import AlgorithmEngine
from ui.main_window import MainWindow
from controllers.application_controller import ApplicationController
from theorems.theorem_engine import TheoremEngine
from graphics.visualization_widget import VisualizationWidget


class TestSortingComparison(unittest.TestCase):
    def test_compare_sorting_bubble_vs_quick(self):
        arr = [64, 34, 25, 12, 22, 11, 90]
        steps = compare_sorting_trace("bubble_sort", "quick_sort", arr)
        self.assertGreater(len(steps), 0)

        # Check step model integrity
        for step in steps:
            self.assertEqual(step.render_data.mode, "comparison")
            comp_data = step.render_data.comparison_data
            self.assertIsNotNone(comp_data)
            self.assertEqual(comp_data["type"], "sorting")
            self.assertIn("algo_1", comp_data)
            self.assertIn("algo_2", comp_data)
            self.assertIn("bars", comp_data["algo_1"])
            self.assertIn("bars", comp_data["algo_2"])

        # Check final step has sorted arrays and winner verdict
        final_step = steps[-1]
        final_comp = final_step.render_data.comparison_data
        expected_sorted = sorted(arr)
        bars1_vals = [b["val"] for b in final_comp["algo_1"]["bars"]]
        bars2_vals = [b["val"] for b in final_comp["algo_2"]["bars"]]
        self.assertEqual(bars1_vals, expected_sorted)
        self.assertEqual(bars2_vals, expected_sorted)
        self.assertTrue(final_comp["summary"]["is_finished"])
        self.assertIsNotNone(final_comp["summary"]["winner"])

    def test_compare_sorting_all_pairs(self):
        arr = [9, 3, 7, 1, 5, 8]
        expected_sorted = sorted(arr)
        pairs = [
            ("bubble_sort", "selection_sort"),
            ("insertion_sort", "merge_sort"),
            ("quick_sort", "bubble_sort"),
            ("selection_sort", "insertion_sort"),
            ("merge_sort", "quick_sort"),
        ]
        for a1, a2 in pairs:
            with self.subTest(pair=f"{a1}_vs_{a2}"):
                steps = compare_sorting_trace(a1, a2, arr)
                self.assertGreater(len(steps), 0)
                final_comp = steps[-1].render_data.comparison_data
                bars1_vals = [b["val"] for b in final_comp["algo_1"]["bars"]]
                bars2_vals = [b["val"] for b in final_comp["algo_2"]["bars"]]
                self.assertEqual(bars1_vals, expected_sorted)
                self.assertEqual(bars2_vals, expected_sorted)
                self.assertTrue(final_comp["algo_1"]["done"])
                self.assertTrue(final_comp["algo_2"]["done"])

    def test_compare_sorting_already_sorted(self):
        arr = [1, 2, 3, 4, 5, 6]
        steps = compare_sorting_trace("bubble_sort", "insertion_sort", arr)
        self.assertGreater(len(steps), 0)
        final_comp = steps[-1].render_data.comparison_data
        bars1_vals = [b["val"] for b in final_comp["algo_1"]["bars"]]
        bars2_vals = [b["val"] for b in final_comp["algo_2"]["bars"]]
        self.assertEqual(bars1_vals, arr)
        self.assertEqual(bars2_vals, arr)

    def test_compare_sorting_reverse_sorted(self):
        arr = [6, 5, 4, 3, 2, 1]
        steps = compare_sorting_trace("selection_sort", "quick_sort", arr)
        self.assertGreater(len(steps), 0)
        final_comp = steps[-1].render_data.comparison_data
        bars1_vals = [b["val"] for b in final_comp["algo_1"]["bars"]]
        bars2_vals = [b["val"] for b in final_comp["algo_2"]["bars"]]
        self.assertEqual(bars1_vals, [1, 2, 3, 4, 5, 6])
        self.assertEqual(bars2_vals, [1, 2, 3, 4, 5, 6])

    def test_compare_sorting_single_element_uses_default(self):
        # Arrays with < 2 elements fall back to standard benchmark array
        steps = compare_sorting_trace("bubble_sort", "quick_sort", [42])
        self.assertGreater(len(steps), 0)
        final_comp = steps[-1].render_data.comparison_data
        bars1_vals = [b["val"] for b in final_comp["algo_1"]["bars"]]
        bars2_vals = [b["val"] for b in final_comp["algo_2"]["bars"]]
        self.assertEqual(bars1_vals, bars2_vals)
        self.assertEqual(bars1_vals, sorted(bars1_vals))

    def test_compare_sorting_empty_array_uses_default(self):
        steps = compare_sorting_trace("bubble_sort", "merge_sort", [])
        self.assertGreater(len(steps), 0)
        final_comp = steps[-1].render_data.comparison_data
        bars1_vals = [b["val"] for b in final_comp["algo_1"]["bars"]]
        bars2_vals = [b["val"] for b in final_comp["algo_2"]["bars"]]
        self.assertEqual(bars1_vals, bars2_vals)
        self.assertEqual(bars1_vals, sorted(bars1_vals))

    def test_compare_sorting_invalid_algo_fallback(self):
        arr = [5, 2, 8]
        # Should gracefully fallback to bubble_sort and quick_sort
        steps = compare_sorting_trace("non_existent_1", "non_existent_2", arr)
        self.assertGreater(len(steps), 0)
        final_comp = steps[-1].render_data.comparison_data
        bars1_vals = [b["val"] for b in final_comp["algo_1"]["bars"]]
        self.assertEqual(bars1_vals, [2, 5, 8])


class TestSearchingComparison(unittest.TestCase):
    def test_compare_searching_found(self):
        arr = [10, 20, 30, 40, 50, 60, 70, 80]
        target = 60
        steps = compare_searching_trace(arr, target)
        self.assertGreater(len(steps), 0)

        for step in steps:
            self.assertEqual(step.render_data.mode, "comparison")
            comp_data = step.render_data.comparison_data
            self.assertEqual(comp_data["type"], "searching")
            self.assertEqual(comp_data["target"], target)
            self.assertIn("algo_1", comp_data)
            self.assertIn("algo_2", comp_data)

        final_comp = steps[-1].render_data.comparison_data
        self.assertTrue(final_comp["algo_1"]["done"])
        self.assertTrue(final_comp["algo_2"]["done"])
        self.assertTrue(final_comp["summary"]["is_finished"])
        s_data1 = final_comp["algo_1"]["search_data"]
        s_data2 = final_comp["algo_2"]["search_data"]
        self.assertEqual(s_data1.get("found_index"), 5)
        self.assertEqual(s_data2.get("found_index"), 5)
        # Binary search should take <= log2(8) + 1 = 4 comparisons vs 6 for linear
        self.assertLessEqual(final_comp["algo_2"]["comparisons"], final_comp["algo_1"]["comparisons"])

    def test_compare_searching_not_found(self):
        arr = [5, 15, 25, 35, 45]
        target = 99
        steps = compare_searching_trace(arr, target)
        self.assertGreater(len(steps), 0)

        final_comp = steps[-1].render_data.comparison_data
        self.assertTrue(final_comp["algo_1"]["done"])
        self.assertTrue(final_comp["algo_2"]["done"])
        s_data1 = final_comp["algo_1"]["search_data"]
        s_data2 = final_comp["algo_2"]["search_data"]
        self.assertEqual(s_data1.get("found_index"), -1)
        self.assertEqual(s_data2.get("found_index"), -1)

    def test_compare_searching_unsorted_input_gets_sorted(self):
        arr = [50, 20, 80, 10, 40]
        target = 40
        steps = compare_searching_trace(arr, target)
        self.assertGreater(len(steps), 0)
        final_comp = steps[-1].render_data.comparison_data
        # Input should be sorted to enable binary search
        s_data1 = final_comp["algo_1"]["search_data"]
        s_data2 = final_comp["algo_2"]["search_data"]
        self.assertEqual(s_data1.get("array"), [10, 20, 40, 50, 80])
        self.assertEqual(s_data2.get("array"), [10, 20, 40, 50, 80])
        self.assertEqual(s_data1.get("found_index"), 2)
        self.assertEqual(s_data2.get("found_index"), 2)

    def test_compare_searching_single_element(self):
        steps_found = compare_searching_trace([42], 42)
        self.assertGreater(len(steps_found), 0)
        final_found = steps_found[-1].render_data.comparison_data
        self.assertTrue(final_found["algo_1"]["done"])
        self.assertTrue(final_found["algo_2"]["done"])

        steps_absent = compare_searching_trace([42], 99)
        self.assertGreater(len(steps_absent), 0)
        final_absent = steps_absent[-1].render_data.comparison_data
        self.assertTrue(final_absent["algo_1"]["done"])
        self.assertTrue(final_absent["algo_2"]["done"])


class TestAlgorithmEngineComparisonIntegration(unittest.TestCase):
    def test_engine_has_comparison_keys(self):
        self.assertIn("compare_sorting", AlgorithmEngine.ALGORITHMS)
        self.assertIn("compare_searching", AlgorithmEngine.ALGORITHMS)

    def test_engine_run_sorting_comparison(self):
        steps = AlgorithmEngine.run_sorting_comparison(
            "merge_sort", "quick_sort", [4, 2, 9, 1]
        )
        self.assertGreater(len(steps), 0)
        self.assertEqual(steps[0].render_data.mode, "comparison")

    def test_engine_run_searching_comparison(self):
        steps = AlgorithmEngine.run_searching_comparison(
            [2, 4, 6, 8, 10], 6
        )
        self.assertGreater(len(steps), 0)
        self.assertEqual(steps[0].render_data.mode, "comparison")


class TestGUIComparisonIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self):
        self.engine = TheoremEngine()
        self.window = MainWindow(theorems=self.engine.get_theorems_list())
        self.controller = ApplicationController(self.window, engine=self.engine)

    def tearDown(self):
        self.controller._stop_playback()
        self.window.close()

    def test_controller_sorting_comparison_topic_selection(self):
        self.controller.on_module_selected("sorting")
        self.controller.on_topic_selected("compare_sorting")
        self.assertEqual(self.controller.current_topic_key, "compare_sorting")
        self.assertGreater(len(self.controller.current_steps), 0)
        step0 = self.controller.current_steps[0]
        self.assertEqual(step0.render_data.mode, "comparison")

    def test_controller_searching_comparison_topic_selection(self):
        self.controller.on_module_selected("searching")
        self.controller.on_topic_selected("compare_searching")
        self.assertEqual(self.controller.current_topic_key, "compare_searching")
        self.assertGreater(len(self.controller.current_steps), 0)
        step0 = self.controller.current_steps[0]
        self.assertEqual(step0.render_data.mode, "comparison")

    def test_sorting_comparison_parameter_customization(self):
        self.controller.on_module_selected("sorting")
        self.controller.on_topic_selected("compare_sorting")

        panel = self.window.parameter_panel
        if "algo_1" in panel._inputs:
            panel._inputs["algo_1"].setCurrentText("Insertion Sort")
        if "algo_2" in panel._inputs:
            panel._inputs["algo_2"].setCurrentText("Selection Sort")
        if "array_input" in panel._inputs:
            panel._inputs["array_input"].setText("50, 10, 40, 20, 30")

        panel._apply_btn.click()

        self.assertGreater(len(self.controller.current_steps), 0)
        final_step = self.controller.current_steps[-1]
        comp = final_step.render_data.comparison_data
        self.assertEqual(comp["algo_1"]["name"], "Insertion Sort")
        self.assertEqual(comp["algo_2"]["name"], "Selection Sort")
        bars1_vals = [b["val"] for b in comp["algo_1"]["bars"]]
        self.assertEqual(bars1_vals, [10, 20, 30, 40, 50])

    def test_searching_comparison_parameter_customization(self):
        self.controller.on_module_selected("searching")
        self.controller.on_topic_selected("compare_searching")

        panel = self.window.parameter_panel
        if "array_input" in panel._inputs:
            panel._inputs["array_input"].setText("3, 7, 12, 19, 25, 33")
        if "target" in panel._inputs:
            panel._inputs["target"].setText("19")

        panel._apply_btn.click()

        self.assertGreater(len(self.controller.current_steps), 0)
        final_step = self.controller.current_steps[-1]
        comp = final_step.render_data.comparison_data
        self.assertEqual(comp["algo_1"]["search_data"].get("found_index"), 3)
        self.assertEqual(comp["algo_2"]["search_data"].get("found_index"), 3)

    def test_comparison_bar_changes_algorithms(self):
        self.controller.on_module_selected("sorting")
        self.controller.on_topic_selected("compare_sorting")
        self.assertFalse(self.window.comparison_bar.isHidden())

        # Select Merge Sort vs Quick Sort using ComparisonBar
        self.window.comparison_bar.set_algorithms("Merge Sort", "Quick Sort", emit=True)

        final_step = self.controller.current_steps[-1]
        comp = final_step.render_data.comparison_data
        self.assertEqual(comp["algo_1"]["name"], "Merge Sort")
        self.assertEqual(comp["algo_2"]["name"], "Quick Sort")

    def test_comparison_bar_swap(self):
        self.controller.on_module_selected("sorting")
        self.controller.on_topic_selected("compare_sorting")
        self.window.comparison_bar.set_algorithms("Bubble Sort", "Quick Sort", emit=True)

        # Click swap
        self.window.comparison_bar.swap_btn.click()

        final_step = self.controller.current_steps[-1]
        comp = final_step.render_data.comparison_data
        self.assertEqual(comp["algo_1"]["name"], "Quick Sort")
        self.assertEqual(comp["algo_2"]["name"], "Bubble Sort")

    def test_start_sorting_comparison_from_single_topic(self):
        self.controller.on_module_selected("sorting")
        self.controller.on_topic_selected("merge_sort")
        self.assertTrue(self.window.comparison_bar.isHidden())

        # Directly start comparison of Merge Sort vs Quick Sort
        self.controller.start_sorting_comparison("Merge Sort", "Quick Sort")
        self.assertEqual(self.controller.current_topic_key, "compare_sorting")
        self.assertFalse(self.window.comparison_bar.isHidden())

        final_step = self.controller.current_steps[-1]
        comp = final_step.render_data.comparison_data
        self.assertEqual(comp["algo_1"]["name"], "Merge Sort")
        self.assertEqual(comp["algo_2"]["name"], "Quick Sort")


class TestVisualizationWidgetComparisonRendering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_render_sorting_comparison_steps(self):
        widget = VisualizationWidget()
        widget.resize(1100, 750)
        steps = compare_sorting_trace("bubble_sort", "quick_sort", [45, 12, 89, 34, 23, 78, 56])
        pixmap = QPixmap(1100, 750)

        # Render first, mid, and final steps
        for step_idx in [0, len(steps) // 2, len(steps) - 1]:
            widget.set_render_data(steps[step_idx].render_data)
            painter = QPainter(pixmap)
            widget.render(painter)
            painter.end()

    def test_render_searching_comparison_steps(self):
        widget = VisualizationWidget()
        widget.resize(1100, 750)
        steps = compare_searching_trace([5, 10, 15, 20, 25, 30, 35, 40], 25)
        pixmap = QPixmap(1100, 750)

        for step_idx in [0, len(steps) // 2, len(steps) - 1]:
            widget.set_render_data(steps[step_idx].render_data)
            painter = QPainter(pixmap)
            widget.render(painter)
            painter.end()


if __name__ == "__main__":
    unittest.main()
