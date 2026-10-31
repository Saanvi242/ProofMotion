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
        modules = ['algorithms', 'transformations', 'rasterization', 'clipping', 'curves', 'theorems']
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
        self.controller.on_module_selected('theorems')
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
        self.controller.on_module_selected('theorems')
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
        self.controller.on_module_selected('theorems')
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
        self.controller.on_module_selected('theorems')
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

    def test_playground_navigation_preserves_lessons(self):
        self.assertNotIn("playground", self.window._module_buttons)
        self.assertTrue(self.window.home_active())
        self.assertTrue(self.window._studio_open_btn.isHidden())
        self.assertTrue(self.window._studio_leave_btn.isHidden())

        self.controller.on_module_selected("playground")
        self.assertEqual(self.controller.current_module, "playground")
        self.assertTrue(self.window.playground_active())
        self.assertEqual(self.window._workspace_stack.currentIndex(), 2)
        self.assertTrue(self.window._nav_pill_bar.isHidden())
        self.assertTrue(self.window._studio_open_btn.isHidden())
        self.assertFalse(self.window._studio_leave_btn.isHidden())
        self.assertFalse(self.window._studio_mode_bar.isHidden())

        host = self.window.playground_host
        self.assertEqual(host.current_mode(), "2d")
        self.assertIs(host.stack.currentWidget(), host.ws2d)
        self.assertIsNotNone(host.ws2d.scene.selected())
        host.ws2d.scene.apply_translate(1.0, 0.5)
        obj = host.ws2d.scene.selected()
        self.assertGreater(len(obj.history), 0)

        self.controller.on_module_selected("theorems")
        self.assertFalse(self.window.playground_active())
        self.assertTrue(self.window.lessons_active())
        self.assertEqual(self.window._workspace_stack.currentIndex(), 1)
        self.assertGreater(len(self.controller.current_steps), 0)
        self.assertFalse(self.window.theorem_panel.isHidden())
        self.assertFalse(self.window.equation_panel.isHidden())
        self.assertTrue(self.window._nav_pill_bar.isHidden())
        self.assertFalse(self.window._studio_open_btn.isHidden())
        self.assertTrue(self.window._studio_leave_btn.isHidden())
        self.assertFalse(self.window._home_back_btn.isHidden())
        self.assertEqual(self.window._module_chip.text(), "Theorems")

    def test_playground_does_not_appear_in_lesson_catalog(self):
        self.assertNotIn("playground", self.controller._catalog)
        self.assertNotIn("playground", self.window._module_buttons)

    def test_studio_button_opens_canvas_directly(self):
        self.window.home_host.studioChosen.emit()
        self.assertTrue(self.window.playground_active())
        host = self.window.playground_host
        self.assertEqual(host.current_mode(), "2d")
        self.assertIs(host.stack.currentWidget(), host.ws2d)
        self.assertEqual(host.ws2d.hud.objectName(), "StudioMatrixHud")
        self.assertEqual(host.ws2d.rail.objectName(), "StudioToolRail")
        host.apply_starter("spin")
        obj = host.ws2d.scene.selected()
        self.assertIsNotNone(obj)
        self.assertGreater(len(obj.history), 0)
        self.assertEqual(host.ws2d.filmstrip.objectName(), "StudioFilmstrip")
        self.assertIn("basis", self.window._studio_mode_buttons)
        self.assertIn("lift", self.window._studio_mode_buttons)
        self.assertIn("run", self.window._studio_mode_buttons)

    def test_curves_module_in_learning_not_studio(self):
        self.assertIn("curves", self.window._module_buttons)
        self.assertIn("curves", self.controller._catalog)
        self.assertNotIn("playground", self.controller._catalog)

        self.controller.on_module_selected("curves")
        self.assertFalse(self.window.playground_active())
        keys = [t.key for t in self.controller._catalog["curves"]["items"]]
        self.assertEqual(keys, ["curve_bezier", "curve_bspline", "curve_hermite"])

        self.controller.on_topic_selected("curve_bezier")
        self.assertGreater(len(self.controller.current_steps), 0)
        rd = self.controller.current_steps[0].render_data
        self.assertEqual(rd.mode, "curves")
        self.assertIsNotNone(rd.curve_data)
        self.assertFalse(self.window.clipping_tab_bar.isHidden())
        self.assertEqual(self.window.clipping_tab_bar.current_tab(), "intro")

        self.controller.on_clipping_tab_changed("casteljau")
        self.assertEqual(self.window.clipping_tab_bar.current_tab(), "casteljau")
        self.assertGreater(len(self.controller.current_steps), 3)
        self.assertIn("pyramid", self.controller.current_steps[-1].render_data.curve_data)

        before = list(self.controller.current_parameters["p1x"] for _ in (0,))[0]
        self.controller.on_curve_handle_dragged("P1", 0.25, 3.5)
        self.assertEqual(self.controller.current_parameters["p1x"], 0.25)
        self.assertEqual(self.controller.current_parameters["p1y"], 3.5)
        self.assertNotEqual(before, 0.25)
        pyramid = self.controller.current_steps[0].render_data.curve_data["pyramid"]
        self.assertEqual(len(pyramid[0]), 4)

        self.controller.on_topic_selected("curve_bspline")
        self.assertEqual(self.controller.current_steps[0].render_data.curve_data["kind"], "bspline")
        self.controller.on_clipping_tab_changed("experiment")
        self.controller.on_curve_handle_dragged("P2", 1.0, -1.0)
        self.assertEqual(self.controller.current_parameters["p2x"], 1.0)

        self.controller.on_topic_selected("curve_hermite")
        self.controller.on_clipping_tab_changed("experiment")
        cd = self.controller.current_steps[0].render_data.curve_data
        self.assertEqual(cd["kind"], "hermite")
        p0x = float(self.controller.current_parameters["p0x"])
        p0y = float(self.controller.current_parameters["p0y"])
        self.controller.on_curve_handle_dragged("T0", p0x + 2.0, p0y + 1.0)
        self.assertAlmostEqual(self.controller.current_parameters["t0x"], 2.0)
        self.assertAlmostEqual(self.controller.current_parameters["t0y"], 1.0)

        self.controller.on_curve_t_changed(0.8)
        self.assertAlmostEqual(self.controller.current_parameters["t"], 0.8)

        # Existing clipping still works after visiting curves
        self.controller.on_module_selected("clipping")
        self.assertGreater(len(self.controller.current_steps), 0)
        self.assertEqual(self.controller.current_topic_key, "clip_cohen_sutherland")

    def test_boot_on_learn_studio_gateway(self):
        self.assertTrue(self.window.home_active())
        self.assertFalse(self.window.home_host.on_catalog())
        self.assertTrue(self.window._home_back_btn.isHidden())
        self.assertTrue(self.window._studio_open_btn.isHidden())
        self.assertTrue(self.window._nav_pill_bar.isHidden())

    def test_learn_catalog_opens_lesson_workspace(self):
        self.window.home_host.learnChosen.emit()
        self.assertTrue(self.window.home_active())
        self.assertTrue(self.window.home_host.on_catalog())
        self.assertFalse(self.window._home_back_btn.isHidden())
        self.assertEqual(self.window._home_back_btn.text(), "←  Home")
        self.assertIn("algorithms", self.window._module_buttons)
        self.assertIn("rasterization", self.window._module_buttons)

        self.window._module_buttons["algorithms"].clicked.emit("algorithms")
        self.assertTrue(self.window.lessons_active())
        self.assertEqual(self.controller.current_module, "algorithms")
        self.assertGreater(len(self.controller.current_steps), 0)
        self.assertEqual(self.window._module_chip.text(), "Algorithms")
        self.assertFalse(self.window._studio_open_btn.isHidden())
        self.assertEqual(self.window._home_back_btn.text(), "←  Learn")

        self.window._home_back_btn.click()
        self.assertTrue(self.window.home_active())
        self.assertTrue(self.window.home_host.on_catalog())

        self.window._home_back_btn.click()
        self.assertTrue(self.window.home_active())
        self.assertFalse(self.window.home_host.on_catalog())

    def test_rast_compare_is_in_catalog(self):
        self.controller.on_module_selected("rasterization")
        keys = [t.key for t in self.controller._catalog["rasterization"]["items"]]
        self.assertIn("rast_compare", keys)
        self.controller.on_topic_selected("rast_compare")
        self.assertGreater(len(self.controller.current_steps), 0)


if __name__ == "__main__":
    unittest.main()
