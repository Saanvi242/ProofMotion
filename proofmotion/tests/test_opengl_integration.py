"""
tests/test_opengl_integration.py
---------------------------------
Comprehensive unit and integration tests for ProofMotion's OpenGL 3D rendering pipeline:
- OpenGL3DWidget lifecycle, parameters, state updates, camera orbit, zoom, and pan.
- MainWindow dual-renderer container switching (QStackedWidget index 0: 2D QPainter, index 1: 3D QOpenGLWidget).
- ApplicationController module selection, parameter synchronization, and view navigation.
"""

import sys
import unittest
import numpy as np
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QEvent, QPoint
from PyQt5.QtGui import QMouseEvent

from ui.main_window import MainWindow
from graphics.opengl_widget import OpenGL3DWidget
from controllers.application_controller import ApplicationController
import cgip.projection_3d as p3d

from theorems.theorem_engine import TheoremEngine

# Ensure a single QApplication instance exists for GUI unit testing
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)


class TestOpenGLWidget(unittest.TestCase):
    def setUp(self):
        self.widget = OpenGL3DWidget()

    def tearDown(self):
        self.widget.deleteLater()

    def test_initial_state(self):
        self.assertEqual(self.widget.projection_mode, "perspective")
        self.assertEqual(self.widget.object_type, "cube")
        self.assertTrue(self.widget.show_grid)
        self.assertEqual(self.widget.tx, 0.0)
        self.assertEqual(self.widget.ty, 0.0)
        self.assertEqual(self.widget.tz, 0.0)
        self.assertEqual(self.widget.sx, 1.0)
        self.assertEqual(self.widget.sy, 1.0)
        self.assertEqual(self.widget.sz, 1.0)

    def test_set_projection_mode(self):
        self.widget.set_projection_mode("orthographic")
        self.assertEqual(self.widget.projection_mode, "orthographic")
        self.widget.set_projection_mode("perspective")
        self.assertEqual(self.widget.projection_mode, "perspective")

    def test_set_object_type(self):
        self.widget.set_object_type("pyramid")
        self.assertEqual(self.widget.object_type, "pyramid")
        self.widget.set_object_type("cube")
        self.assertEqual(self.widget.object_type, "cube")

    def test_set_transformations(self):
        self.widget.set_transformations(
            tx=2.5, ty=-1.0, tz=3.0,
            sx=1.5, sy=0.8, sz=2.0,
            rx=45.0, ry=30.0, rz=15.0
        )
        self.assertEqual(self.widget.tx, 2.5)
        self.assertEqual(self.widget.ty, -1.0)
        self.assertEqual(self.widget.tz, 3.0)
        self.assertEqual(self.widget.sx, 1.5)
        self.assertEqual(self.widget.sy, 0.8)
        self.assertEqual(self.widget.sz, 2.0)
        self.assertEqual(self.widget.rx, 45.0)
        self.assertEqual(self.widget.ry, 30.0)
        self.assertEqual(self.widget.rz, 15.0)

    def test_update_from_parameters(self):
        params = {
            "rx": 50.0,
            "ry": 60.0,
            "rz": 70.0,
            "tx": 1.2,
            "ty": 3.4,
            "tz": -2.0,
            "sx": 2.0,
            "sy": 2.0,
            "sz": 2.0,
            "camera_dist": 9.5,
            "shape": "pyramid",
            "projection": "orthographic"
        }
        self.widget.update_from_parameters(params)
        self.assertEqual(self.widget.rx, 50.0)
        self.assertEqual(self.widget.ry, 60.0)
        self.assertEqual(self.widget.rz, 70.0)
        self.assertEqual(self.widget.tx, 1.2)
        self.assertEqual(self.widget.ty, 3.4)
        self.assertEqual(self.widget.tz, -2.0)
        self.assertEqual(self.widget.camera_distance, 9.5)
        self.assertEqual(self.widget.object_type, "pyramid")
        self.assertEqual(self.widget.projection_mode, "orthographic")

    def test_left_drag_orbits_camera(self):
        start_az = self.widget.camera_azimuth
        start_el = self.widget.camera_elevation
        press = QMouseEvent(
            QEvent.MouseButtonPress, QPoint(120, 80), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier
        )
        move = QMouseEvent(
            QEvent.MouseMove, QPoint(180, 110), Qt.NoButton, Qt.LeftButton, Qt.NoModifier
        )
        self.widget.mousePressEvent(press)
        self.widget.mouseMoveEvent(move)
        self.assertNotEqual(self.widget.camera_azimuth, start_az)
        self.assertNotEqual(self.widget.camera_elevation, start_el)

    def test_camera_zoom_and_pan(self):
        init_dist = self.widget.camera_distance
        self.widget.zoom_in()
        self.assertLess(self.widget.camera_distance, init_dist)

        self.widget.zoom_out()
        self.widget.zoom_out()
        self.assertGreater(self.widget.camera_distance, init_dist * 0.85)

        self.widget.pan(10.0, -5.0)
        self.assertNotEqual(self.widget.camera_pan[0], 0.0)
        self.assertNotEqual(self.widget.camera_pan[1], 0.0)

        self.widget.reset_view()
        self.assertEqual(self.widget.camera_distance, 7.0)
        self.assertEqual(self.widget.camera_pan, [0.0, 0.0])

    def test_fov_and_scene_objects_api(self):
        self.widget.set_fov(60.0)
        self.assertEqual(self.widget.fov_deg, 60.0)
        self.widget.set_show_faces(False)
        self.assertFalse(self.widget.show_faces)
        self.widget.set_object_type("sphere")
        self.assertEqual(self.widget.object_type, "sphere")
        self.widget.set_object_type("cylinder")
        self.assertEqual(self.widget.object_type, "cylinder")
        import numpy as np
        payload = [{
            "id": "a",
            "kind": "cube",
            "model": np.eye(4),
            "selected": True,
            "color": (0.3, 0.7, 0.6),
        }]
        self.widget.set_scene_objects(payload)
        self.assertEqual(len(self.widget.scene_objects), 1)
        self.widget.set_scene_objects(None)
        self.assertIsNone(self.widget.scene_objects)

    def test_reset_transformations(self):
        self.widget.set_transformations(tx=5.0, ty=5.0, tz=5.0, sx=3.0, sy=3.0, sz=3.0)
        self.widget.reset_transformations()
        self.assertEqual(self.widget.tx, 0.0)
        self.assertEqual(self.widget.ty, 0.0)
        self.assertEqual(self.widget.tz, 0.0)
        self.assertEqual(self.widget.sx, 1.0)
        self.assertEqual(self.widget.sy, 1.0)
        self.assertEqual(self.widget.sz, 1.0)


class TestDualRendererIntegration(unittest.TestCase):
    def setUp(self):
        self.engine = TheoremEngine()
        self.window = MainWindow(theorems=self.engine.get_theorems_list())
        self.controller = ApplicationController(self.window, engine=self.engine)

    def tearDown(self):
        self.controller._stop_playback()
        self.window.close()
        self.window.deleteLater()

    def test_stacked_widget_contains_both_renderers(self):
        # Index 0 must be 2D VisualizationWidget
        self.assertEqual(self.window.vis_stack.widget(0), self.window.visualization_widget)
        # Index 1 must be 3D OpenGL3DWidget
        self.assertEqual(self.window.vis_stack.widget(1), self.window.opengl_widget)

    def test_switching_renderer_mode(self):
        self.window.set_active_renderer("opengl")
        self.assertEqual(self.window.vis_stack.currentIndex(), 1)
        self.assertEqual(self.window.get_active_renderer(), "opengl")

        self.window.set_active_renderer("2d")
        self.assertEqual(self.window.vis_stack.currentIndex(), 0)
        self.assertEqual(self.window.get_active_renderer(), "2d")

    def test_module_selection_routes_to_correct_renderer(self):
        # Selecting 'projections_3d' automatically activates OpenGL
        self.controller.on_module_selected("projections_3d")
        self.assertEqual(self.window.get_active_renderer(), "opengl")
        self.assertEqual(self.window.vis_stack.currentIndex(), 1)

        # Selecting 2D modules automatically activates 2D QPainter
        self.controller.on_module_selected("transformations")
        self.assertEqual(self.window.get_active_renderer(), "2d")
        self.assertEqual(self.window.vis_stack.currentIndex(), 0)

        self.controller.on_module_selected("rasterization")
        self.assertEqual(self.window.get_active_renderer(), "2d")

        self.controller.on_module_selected("clipping")
        self.assertEqual(self.window.get_active_renderer(), "2d")

        self.controller.on_module_selected("theorems")
        self.assertEqual(self.window.get_active_renderer(), "2d")

        # Switching back to 3D Projections works smoothly
        self.controller.on_module_selected("projections_3d")
        self.assertEqual(self.window.get_active_renderer(), "opengl")

    def test_3d_topics_set_appropriate_projection_and_shape(self):
        self.controller.on_module_selected("projections_3d")

        self.controller.on_topic_selected("proj_cube_persp")
        self.assertEqual(self.window.opengl_widget.object_type, "cube")
        self.assertEqual(self.window.opengl_widget.projection_mode, "perspective")

        self.controller.on_topic_selected("proj_cube_ortho")
        self.assertEqual(self.window.opengl_widget.object_type, "cube")
        self.assertEqual(self.window.opengl_widget.projection_mode, "orthographic")

        self.controller.on_topic_selected("proj_pyramid")
        self.assertEqual(self.window.opengl_widget.object_type, "pyramid")
        self.assertEqual(self.window.opengl_widget.projection_mode, "perspective")

    def test_view_controls_propagate_to_opengl_in_3d_mode(self):
        self.controller.on_module_selected("projections_3d")
        init_dist = self.window.opengl_widget.camera_distance

        self.controller.on_zoom_in()
        self.assertLess(self.window.opengl_widget.camera_distance, init_dist)

        self.controller.on_reset_view()
        self.assertEqual(self.window.opengl_widget.camera_distance, 7.0)

        self.controller.on_pan_requested(15.0, 10.0)
        self.assertNotEqual(self.window.opengl_widget.camera_pan, [0.0, 0.0])

        self.controller.on_grid_toggled(False)
        self.assertFalse(self.window.opengl_widget.show_grid)
        self.controller.on_grid_toggled(True)
        self.assertTrue(self.window.opengl_widget.show_grid)


if __name__ == "__main__":
    unittest.main()
