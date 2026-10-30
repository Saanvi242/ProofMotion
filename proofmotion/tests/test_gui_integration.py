"""
tests/test_gui_integration.py
-----------------------------
GUI integration tests verifying PyQt widget interactions, module switching,
playback controls, parameter updates, and view events without crashes.
"""

import unittest
import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from controllers.application_controller import ApplicationController
from theorems.theorem_engine import TheoremEngine


class TestGUIIntegration(unittest.TestCase):
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

    def test_module_navigation(self):
        modules = ['theorems', 'algorithms', 'transformations', 'rasterization', 'clipping']
        for mod in modules:
            self.controller.on_module_selected(mod)
            self.assertEqual(self.controller.current_module, mod)
            self.assertGreater(len(self.controller.current_steps), 0)

    def test_apply_parameters_with_array_and_target(self):
        self.controller.on_module_selected('algorithms')
        self.controller.on_topic_selected('binary_search')

        # Type custom comma-separated array and target value
        arr_input = self.window.parameter_panel._inputs["array_input"]
        target_input = self.window.parameter_panel._inputs["target"]

        arr_input.setText("4, 8, 15, 16, 23, 30, 42, 55, 68")
        target_input.setText("42")

        # Click Apply Parameters
        self.window.parameter_panel._apply_btn.click()

        # Must NOT show validation error
        self.assertTrue(self.window.parameter_panel._error_label.isHidden())
        self.assertEqual(self.controller.current_parameters.get("target"), 42)
        self.assertEqual(self.controller.current_parameters.get("array_input"), "4, 8, 15, 16, 23, 30, 42, 55, 68")
        self.assertGreater(len(self.controller.current_steps), 0)

    def test_step_navigation_and_transport(self):
        self.controller.on_module_selected('theorems')
        total = len(self.controller.current_steps)
        self.assertGreater(total, 1)

        # Step forward
        self.controller.on_next_step()
        self.assertEqual(self.controller.current_step_index, 1)

        # Step back
        self.controller.on_previous_step()
        self.assertEqual(self.controller.current_step_index, 0)

        # Replay
        self.controller.on_replay()
        self.assertEqual(self.controller.current_step_index, 0)
        self.assertTrue(self.controller.is_playing)

        # Pause
        self.controller.on_play_pause()
        self.assertFalse(self.controller.is_playing)

    def test_algorithm_step_title_is_displayed(self):
        self.controller.on_module_selected('algorithms')
        step = self.controller.current_steps[0]
        self.assertTrue(step.title)
        self.assertEqual(self.window.equation_panel._step_title_label.text(), step.title)
        self.assertFalse(self.window.equation_panel._step_title_label.isHidden())

    def test_theorem_sidebar_selection_remains_readable(self):
        panel = self.window.theorem_panel
        selected_button = panel._buttons["circle_area"]
        selected_button.click()

        self.assertEqual(selected_button.property("selected"), "true")
        for label in selected_button.findChildren(type(panel._title_label)):
            self.assertEqual(label.property("selected"), "true")

        previous_button = panel._buttons["pythagorean"]
        previous_button.click()
        self.assertEqual(previous_button.property("selected"), "true")
        self.assertEqual(selected_button.property("selected"), "false")
        for label in selected_button.findChildren(type(panel._title_label)):
            self.assertEqual(label.property("selected"), "false")

    def test_zoom_and_pan(self):
        initial_zoom = self.window.visualization_widget._zoom
        self.controller.on_zoom_in()
        self.assertGreater(self.window.visualization_widget._zoom, initial_zoom)

        self.controller.on_pan_requested(15.0, -10.0)
        self.assertEqual(self.window.visualization_widget._pan, [15.0, -10.0])

        self.controller.on_reset_view()
        self.assertEqual(self.window.visualization_widget._zoom, 1.0)
        self.assertEqual(self.window.visualization_widget._pan, [0.0, 0.0])

    def test_algorithms_section_hides_zoom_controls(self):
        # In theorems module, zoom controls must be visible
        self.controller.on_module_selected('theorems')
        self.assertFalse(self.window.view_controls._zoom_in_btn.isHidden())
        self.assertFalse(self.window.view_controls._zoom_out_btn.isHidden())

        # Switch to algorithms module: zoom controls must be hidden
        self.controller.on_module_selected('algorithms')
        self.assertTrue(self.window.view_controls._zoom_in_btn.isHidden())
        self.assertTrue(self.window.view_controls._zoom_out_btn.isHidden())

        # Zoom in/out action in algorithms module should be ignored
        current_zoom = self.window.visualization_widget._zoom
        self.controller.on_zoom_in()
        self.assertEqual(self.window.visualization_widget._zoom, current_zoom)
        self.controller.on_zoom_out()
        self.assertEqual(self.window.visualization_widget._zoom, current_zoom)

        # Switch to transformations module: zoom controls must be restored
        self.controller.on_module_selected('transformations')
        self.assertFalse(self.window.view_controls._zoom_in_btn.isHidden())
        self.assertFalse(self.window.view_controls._zoom_out_btn.isHidden())

    def test_parameter_validation_error_handling(self):
        self.controller.on_module_selected('theorems')
        # Negative side length should trigger validation error gracefully
        self.controller.on_parameters_applied({"side_a": -5.0, "side_b": 4.0})
        self.assertFalse(self.window.parameter_panel._error_label.isHidden())
        self.assertIn("positive", self.window.parameter_panel._error_label.text().lower())

    def test_grid_toggle(self):
        viz = self.window.visualization_widget
        self.assertTrue(viz._show_grid)
        self.window.view_controls._grid_btn.setChecked(False)
        self.assertFalse(viz._show_grid)
        self.window.view_controls._grid_btn.setChecked(True)
        self.assertTrue(viz._show_grid)

    def test_timeline_step_selection(self):
        self.controller.on_module_selected('theorems')
        self.controller.on_topic_selected('pythagorean')
        self.assertGreater(len(self.controller.current_steps), 2)
        # Select step 2
        self.controller.on_step_selected(2)
        self.assertEqual(self.controller.current_step_index, 2)

    def test_parameter_reset(self):
        self.controller.on_module_selected('theorems')
        self.controller.on_topic_selected('pythagorean')
        # Change value
        self.window.parameter_panel._inputs["side_a"].setText("9.0")
        # Trigger reset
        self.window.parameter_panel._on_reset_clicked()
        self.assertEqual(float(self.window.parameter_panel._inputs["side_a"].text()), 3.0)



    def test_parameter_steppers(self):
        self.controller.on_module_selected('theorems')
        self.controller.on_topic_selected('pythagorean')
        edit = self.window.parameter_panel._inputs["side_a"]
        initial_val = float(edit.text())
        # Step up
        spec = next(s for s in self.window.parameter_panel._specs if s.key == "side_a")
        self.window.parameter_panel._on_step_change(spec, edit, 1)
        self.assertGreater(float(edit.text()), initial_val)
        # Step down
        self.window.parameter_panel._on_step_change(spec, edit, -1)
        self.assertEqual(float(edit.text()), initial_val)

    def test_parameter_quick_presets(self):
        self.controller.on_module_selected('theorems')
        self.controller.on_topic_selected('pythagorean')
        chips = self.window.parameter_panel._preset_chips
        self.assertGreater(len(chips), 0)
        # Click 5, 12, 13 (Triple)
        chips[1].click()
        self.assertEqual(float(self.window.parameter_panel._inputs["side_a"].text()), 5.0)
        self.assertEqual(float(self.window.parameter_panel._inputs["side_b"].text()), 12.0)
        self.assertEqual(self.controller.current_parameters.get("side_a"), 5.0)

    def test_fullscreen_canvas_toggle(self):
        """Verify Fullscreen toggle expands canvas by hiding sidebars/header, and restores cleanly."""
        self.assertFalse(self.window._is_canvas_fullscreen)
        self.assertFalse(self.window._header_widget.isHidden())
        self.assertFalse(self.window.theorem_panel.isHidden())
        self.assertFalse(self.window.parameter_panel.isHidden())
        self.assertFalse(self.window.equation_panel.isHidden())

        # Toggle Fullscreen on
        self.window.view_controls._fullscreen_btn.setChecked(True)
        self.assertTrue(self.window._is_canvas_fullscreen)
        self.assertTrue(self.window._header_widget.isHidden())
        self.assertTrue(self.window.theorem_panel.isHidden())
        self.assertTrue(self.window.parameter_panel.isHidden())
        self.assertTrue(self.window.equation_panel.isHidden())
        self.assertEqual(self.window.view_controls._fullscreen_btn.text(), "🗗 Exit Fullscreen")

        # Toggle Fullscreen off
        self.window.view_controls._fullscreen_btn.setChecked(False)
        self.assertFalse(self.window._is_canvas_fullscreen)
        self.assertFalse(self.window._header_widget.isHidden())
        self.assertFalse(self.window.theorem_panel.isHidden())
        self.assertFalse(self.window.parameter_panel.isHidden())
        self.assertFalse(self.window.equation_panel.isHidden())
        self.assertEqual(self.window.view_controls._fullscreen_btn.text(), "⛶ Fullscreen")

    def test_fractional_parameter_input_and_stepping(self):
        """Verify entering fractional/decimal numbers and stepping fractional values."""
        self.controller.on_topic_selected('circle_area')
        radius_input = self.window.parameter_panel._inputs["radius"]

        # Type fractional value 7.5
        radius_input.setText("7.5")
        self.window.parameter_panel._apply_btn.click()
        self.assertEqual(self.controller.current_parameters.get("radius"), 7.5)

        # Test stepping by 0.5
        self.window.parameter_panel._on_step_change(
            self.window.parameter_panel._specs[0], radius_input, 1
        )
        self.assertEqual(float(radius_input.text()), 8.0)


if __name__ == "__main__":
    unittest.main()
