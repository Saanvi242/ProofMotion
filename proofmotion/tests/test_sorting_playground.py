"""
tests/test_sorting_playground.py
---------------------------------
Comprehensive test suite for the ProofMotion Animated Sorting Playground:
  - Event generation across all 5 sorting algorithms
  - Multi-theme rendering (Bouncing Balls, Floating Cubes, Marble Machine, Bars)
  - Animation interpolation and reduced-motion mode
  - Edge cases (empty, single, duplicates, negative numbers, reverse)
  - GUI view controls and parameter panel style synchronization
"""

import sys
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import QSize

from algorithms.sorting.sorting_events import SortEvent, SortEventType
from algorithms.sorting.bubble_sort import bubble_sort_trace
from algorithms.sorting.selection_sort import selection_sort_trace
from algorithms.sorting.insertion_sort import insertion_sort_trace
from algorithms.sorting.merge_sort import merge_sort_trace
from algorithms.sorting.quick_sort import quick_sort_trace
from graphics.sorting_renderer import SortingPlaygroundRenderer
from graphics.visualization_widget import VisualizationWidget
from ui.view_controls import ViewControls
from ui.parameter_panel import ParameterPanel
from models.theorem_state import Theorem, ParameterSpec, ParameterType

app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)


class TestSortingPlayground(unittest.TestCase):

    def setUp(self):
        self.algorithms = [
            ("bubble_sort", bubble_sort_trace),
            ("selection_sort", selection_sort_trace),
            ("insertion_sort", insertion_sort_trace),
            ("merge_sort", merge_sort_trace),
            ("quick_sort", quick_sort_trace),
        ]
        self.sample_arr = [24, 13, 9, 45, 18, 32, 5, 29]

    def test_semantic_sort_events_emitted(self):
        """Verify every sorting algorithm attaches a valid SortEvent on every step."""
        for name, algo_func in self.algorithms:
            with self.subTest(algorithm=name):
                steps = algo_func(self.sample_arr)
                self.assertGreater(len(steps), 0)

                # Check initial step
                init_step = steps[0]
                self.assertIsNotNone(init_step.render_data)
                self.assertIsNotNone(init_step.render_data.sort_event)
                self.assertEqual(init_step.render_data.sort_event.event_type, SortEventType.INIT)

                # Check final step
                last_step = steps[-1]
                self.assertIsNotNone(last_step.render_data.sort_event)
                self.assertEqual(last_step.render_data.sort_event.event_type, SortEventType.COMPLETE)
                self.assertEqual(len(last_step.render_data.sort_event.sorted_indices), len(self.sample_arr))

                # Check intermediate steps
                for step in steps:
                    rd = step.render_data
                    self.assertIsNotNone(rd)
                    self.assertIsNotNone(rd.bars)
                    self.assertIsNotNone(rd.sort_event)
                    self.assertIsInstance(rd.sort_event, SortEvent)

    def test_all_visual_styles_render_without_error(self):
        """Render all 4 styles to an offscreen QImage across key steps."""
        renderer = SortingPlaygroundRenderer()
        image = QImage(QSize(800, 600), QImage.Format_ARGB32)
        image.fill(0)

        for style_key, _ in SortingPlaygroundRenderer.STYLES:
            renderer.style = style_key
            for name, algo_func in self.algorithms:
                steps = algo_func([15, 8, 42, 23, 4])
                for step in [steps[0], steps[len(steps) // 2], steps[-1]]:
                    painter = QPainter(image)
                    try:
                        renderer.progress = 0.5
                        renderer.render(painter, 800, 600, step.render_data.bars, step.render_data.sort_event)
                    finally:
                        painter.end()

    def test_style_motions_are_distinct_on_swap(self):
        """Each style must use different kinematics, not a shared hop path."""
        from graphics.sorting_motion import motion_for

        event = SortEvent(
            SortEventType.SWAP,
            array=[4, 1],
            swapping_indices=(0, 1),
            indices=[0, 1],
        )
        centers = [80.0, 240.0]
        base_y = 200.0
        t = 0.45
        poses = {
            style: motion_for(style).pose(0, centers, base_y, event, t, False, 20.0)
            for style in ("balls", "marbles", "cars", "cubes", "bars")
        }

        self.assertLess(poses["balls"].y, base_y - 30.0, "balls should hop well above the floor")
        self.assertLess(abs(poses["marbles"].y - base_y), 12.0, "marbles should stay on the rail")
        self.assertGreater(abs(poses["marbles"].rotation_deg), 30.0, "marbles should roll")
        self.assertGreater(abs(poses["cars"].y - base_y), 5.0, "cars should change lanes while passing")
        self.assertGreater(abs(poses["cars"].rotation_deg), 15.0, "car wheels should rotate")
        self.assertLess(poses["cubes"].y, base_y - 20.0, "cubes should lift before sliding")
        self.assertAlmostEqual(poses["bars"].y, base_y, places=5)
        self.assertLess(poses["balls"].y, poses["marbles"].y - 20.0)

    def test_style_compare_behaviours_differ(self):
        from graphics.sorting_motion import motion_for

        event = SortEvent(
            SortEventType.COMPARE,
            array=[3, 8],
            comparing_indices=(0, 1),
            indices=[0, 1],
        )
        centers = [100.0, 200.0]
        base_y = 180.0
        t = 0.5
        ball = motion_for("balls").pose(0, centers, base_y, event, t, False, 20.0)
        marble = motion_for("marbles").pose(0, centers, base_y, event, t, False, 20.0)
        cube = motion_for("cubes").pose(0, centers, base_y, event, t, False, 20.0)
        self.assertLess(ball.y, base_y - 5.0)
        self.assertNotEqual(marble.x, centers[0])
        self.assertGreater(abs(cube.tilt_deg), 4.0)

    def test_reduced_motion_keeps_items_in_slots(self):
        from graphics.sorting_motion import motion_for

        event = SortEvent(SortEventType.SWAP, array=[2, 1], swapping_indices=(0, 1), indices=[0, 1])
        centers = [50.0, 150.0]
        for style in ("balls", "marbles", "cars", "cubes", "bars"):
            pose = motion_for(style).pose(0, centers, 100.0, event, 0.4, True, 16.0)
            self.assertAlmostEqual(pose.x, 50.0)
            self.assertAlmostEqual(pose.y, 100.0)

    def test_reduced_motion_mode(self):
        """Verify reduced motion disables interpolation displacement."""
        renderer = SortingPlaygroundRenderer()
        renderer.reduced_motion = True
        renderer.progress = 0.25

        image = QImage(QSize(600, 400), QImage.Format_ARGB32)
        painter = QPainter(image)
        try:
            steps = bubble_sort_trace([10, 5, 20])
            swap_step = next(s for s in steps if s.render_data.sort_event.is_swap())
            renderer.render(painter, 600, 400, swap_step.render_data.bars, swap_step.render_data.sort_event)
        finally:
            painter.end()

    def test_sorting_edge_cases(self):
        """Test empty arrays, single elements, duplicates, and reverse sorted arrays."""
        edge_cases = [
            [],
            [99],
            [1, 2, 3],
            [5, 4, 3, 2, 1],
            [-5, 0, 5, -10],
            [7, 7, 7, 7],
        ]
        renderer = SortingPlaygroundRenderer()
        image = QImage(QSize(600, 400), QImage.Format_ARGB32)

        for arr in edge_cases:
            for name, algo_func in self.algorithms:
                steps = algo_func(arr)
                self.assertGreater(len(steps), 0)
                painter = QPainter(image)
                try:
                    renderer.render(painter, 600, 400, steps[-1].render_data.bars, steps[-1].render_data.sort_event)
                finally:
                    painter.end()

    def test_view_controls_style_signals(self):
        """Verify ViewControls manages sorting controls and reduced-motion signals."""
        vc = ViewControls()
        vc.set_sorting_controls_visible(True)
        self.assertFalse(vc._style_container.isHidden())

        # Style dropdown is removed from top bar in favor of Explore parameters panel
        self.assertFalse(hasattr(vc, "_style_combo"))

        received_motion = []
        vc.reducedMotionToggled.connect(received_motion.append)
        vc._reduced_motion_btn.setChecked(True)
        self.assertEqual(received_motion, [True])

    def test_parameter_panel_style_synchronization(self):
        """Verify ParameterPanel generates style chips and synchronizes selection."""
        param_panel = ParameterPanel()
        sorting_item = Theorem(
            key="bubble_sort",
            display_name="Bubble Sort",
            short_description="Sorting",
            parameters=[
                ParameterSpec(key="array_input", label="Array", param_type=ParameterType.TEXT, default="10, 5, 20")
            ]
        )
        param_panel.set_theorem(sorting_item)

        received_styles = []
        param_panel.sortingStyleRequested.connect(received_styles.append)

        # Trigger style chip click
        param_panel._on_style_chip_clicked("bars", param_panel._style_chips[1][1])
        self.assertIn("bars", received_styles)

        # Programmatic update
        param_panel.set_current_sort_style("bars")
        self.assertEqual(param_panel._current_sort_style, "bars")


if __name__ == "__main__":
    unittest.main()
