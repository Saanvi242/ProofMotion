"""
tests/test_studio_experiences.py
--------------------------------
Math and integration tests for Studio Filmstrip, Living Basis,
Homogeneous Lift, Pipeline Runway, and Bresenham decision fields.
"""

import sys
import unittest

import numpy as np
from PyQt5.QtWidgets import QApplication

from playground.scene_2d import Scene2D
from playground.models import composed_matrix_through, animated_composed_matrix
from playground.experiences import (
    living_basis_matrix, deform_points, living_basis_det,
    homogeneous_lift_point, lift_vertices, apply_homogeneous,
    pipeline_state, pipeline_matrix, world_to_grid, rasterize_polygon_edges,
)
import cgip.transformations as t2d
import cgip.rasterization as rast


class TestComposedMatrixThrough(unittest.TestCase):
    def setUp(self):
        self.scene = Scene2D()
        self.scene.clear()
        self.obj = self.scene.add_object("point", [(1.0, 0.0)])

    def test_negative_index_is_pose(self):
        self.scene.apply_translate(2.0, 0.0)
        np.testing.assert_allclose(
            composed_matrix_through(self.obj, -1, 1.0, dim=2),
            self.obj.pose_matrix(),
            atol=1e-9,
        )

    def test_full_index_matches_composed(self):
        self.scene.apply_translate(2.0, 0.0)
        self.scene.apply_rotate(90.0)
        np.testing.assert_allclose(
            composed_matrix_through(self.obj, 1, 1.0, dim=2),
            self.obj.composed_matrix(),
            atol=1e-9,
        )
        world = t2d.apply_transform(composed_matrix_through(self.obj, 1, 1.0, dim=2), [(1.0, 0.0)])[0]
        self.assertAlmostEqual(world[0], 0.0, places=6)
        self.assertAlmostEqual(world[1], 3.0, places=6)

    def test_prefix_after_first_op(self):
        self.scene.apply_translate(2.0, 0.0)
        self.scene.apply_rotate(90.0)
        prefix = composed_matrix_through(self.obj, 0, 1.0, dim=2)
        expected = t2d.translation_matrix(2.0, 0.0) @ self.obj.pose_matrix()
        np.testing.assert_allclose(prefix, expected, atol=1e-9)

    def test_t_zero_skips_last_included_op(self):
        self.scene.apply_translate(2.0, 0.0)
        self.scene.apply_rotate(90.0)
        np.testing.assert_allclose(
            composed_matrix_through(self.obj, 1, 0.0, dim=2),
            composed_matrix_through(self.obj, 0, 1.0, dim=2),
            atol=1e-9,
        )

    def test_animated_wrapper_uses_last_op(self):
        self.scene.apply_rotate(90.0)
        np.testing.assert_allclose(
            animated_composed_matrix(self.obj, 0.5, dim=2),
            composed_matrix_through(self.obj, 0, 0.5, dim=2),
            atol=1e-9,
        )


class TestLivingBasis(unittest.TestCase):
    def test_identity_preserves_points(self):
        pts = [(1.0, 2.0), (-3.0, 0.5)]
        out = deform_points(1, 0, 0, 1, pts)
        for a, b in zip(pts, out):
            self.assertAlmostEqual(a[0], b[0], places=9)
            self.assertAlmostEqual(a[1], b[1], places=9)

    def test_columns_are_basis_vectors(self):
        M = living_basis_matrix(2, 0.5, -1, 3)
        np.testing.assert_allclose(M[:, 0], [2, 0.5, 0], atol=1e-9)
        np.testing.assert_allclose(M[:, 1], [-1, 3, 0], atol=1e-9)

    def test_shear_maps_j_hat(self):
        # î = (1,0), ĵ = (1,1) shears x by y
        out = deform_points(1, 0, 1, 1, [(0.0, 1.0), (1.0, 0.0), (1.0, 1.0)])
        self.assertAlmostEqual(out[0][0], 1.0, places=6)
        self.assertAlmostEqual(out[0][1], 1.0, places=6)
        self.assertAlmostEqual(out[1][0], 1.0, places=6)
        self.assertAlmostEqual(out[1][1], 0.0, places=6)
        self.assertAlmostEqual(out[2][0], 2.0, places=6)
        self.assertAlmostEqual(out[2][1], 1.0, places=6)

    def test_det_zero_is_degenerate(self):
        self.assertAlmostEqual(living_basis_det(1, 2, 2, 4), 0.0, places=9)
        self.assertAlmostEqual(living_basis_det(1, 0, 0, 1), 1.0, places=9)


class TestHomogeneousLift(unittest.TestCase):
    def test_w1_is_height_one(self):
        self.assertEqual(homogeneous_lift_point(2.0, 3.0, 1.0), (2.0, 1.0, 3.0))

    def test_w0_sits_on_ground(self):
        self.assertEqual(homogeneous_lift_point(2.0, 3.0, 0.0), (2.0, 0.0, 3.0))

    def test_translate_then_lift(self):
        T = t2d.translation_matrix(1.0, 2.0)
        x, y, w = apply_homogeneous(T, 0.0, 0.0, 1.0)
        self.assertAlmostEqual(x, 1.0, places=9)
        self.assertAlmostEqual(y, 2.0, places=9)
        self.assertAlmostEqual(w, 1.0, places=9)
        lifted = lift_vertices([(0.0, 0.0)], 1.0, extra=T)
        self.assertAlmostEqual(lifted[0][0], 1.0, places=9)
        self.assertAlmostEqual(lifted[0][1], 1.0, places=9)
        self.assertAlmostEqual(lifted[0][2], 2.0, places=9)


class TestPipelineRunway(unittest.TestCase):
    def test_identity_keeps_vertices(self):
        verts = [(-1.0, -1.0), (1.0, -1.0), (0.0, 1.0)]
        M = pipeline_matrix(0.0, 1.0, 1.0, t=1.0)
        out = t2d.apply_transform(M, verts)
        for a, b in zip(verts, out):
            self.assertAlmostEqual(a[0], b[0], places=6)
            self.assertAlmostEqual(a[1], b[1], places=6)

    def test_clip_drops_outside(self):
        verts = [(-5.0, 0.0), (5.0, 0.0), (0.0, 4.0)]
        state = pipeline_state(verts, angle=0.0, sx=1.0, sy=1.0, clip_rect=(-2, -2, 2, 2), t=1.0)
        self.assertGreater(len(state["clipped"]), 0)
        for x, y in state["clipped"]:
            self.assertGreaterEqual(x, -2.01)
            self.assertLessEqual(x, 2.01)
            self.assertGreaterEqual(y, -2.01)
            self.assertLessEqual(y, 2.01)

    def test_pixels_match_bresenham_helper(self):
        verts = [(-2.0, -1.0), (2.0, -1.0), (0.0, 2.0)]
        state = pipeline_state(verts, angle=0.0, sx=1.0, sy=1.0, t=1.0)
        expected = rasterize_polygon_edges(state["clipped"] or state["transformed"])
        self.assertEqual(state["all_pixels"], expected)
        self.assertGreater(len(state["pixels"]), 0)

    def test_station_progression(self):
        verts = [(-1.5, -1.0), (1.5, -1.0), (0.0, 1.6)]
        self.assertEqual(pipeline_state(verts, t=0.1)["station"], 0)
        self.assertEqual(pipeline_state(verts, t=0.5)["station"], 1)
        self.assertEqual(pipeline_state(verts, t=0.9)["station"], 2)
        self.assertEqual(len(pipeline_state(verts, t=0.1)["pixels"]), 0)

    def test_world_to_grid_origin(self):
        gx, gy = world_to_grid(0.0, 0.0, grid_size=19, span=12.0)
        self.assertEqual(gx, 9)
        self.assertEqual(gy, 9)


class TestBresenhamDecision(unittest.TestCase):
    def test_line_steps_carry_decision(self):
        steps = rast.bresenham_line_trace(0, 0, 8, 4)
        mid = next(s for s in steps if s.render_data.pixel_grid.get("decision") is not None)
        pg = mid.render_data.pixel_grid
        self.assertEqual(pg["decision_kind"], "err")
        self.assertIn(pg["choice"], ("x", "y", "diagonal"))
        self.assertIn("lean", pg)

    def test_circle_steps_carry_decision(self):
        steps = rast.midpoint_circle_trace(10, 10, 6)
        mid = next(s for s in steps if s.render_data.pixel_grid.get("decision") is not None)
        pg = mid.render_data.pixel_grid
        self.assertEqual(pg["decision_kind"], "p")
        self.assertIn(pg["choice"], ("E", "SE"))


class TestStudioHostModes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_host_opens_all_modes(self):
        from playground.ui.playground_host import PlaygroundHost, STUDIO_MODES
        host = PlaygroundHost()
        host.show()
        for kind in STUDIO_MODES:
            host.open_mode(kind)
            self.assertEqual(host.current_mode(), kind)
            self.assertIsNotNone(host.stack.currentWidget())
        host.ws2d.scene.apply_translate(1.0, 0.0)
        host._send_to_runway(host.ws2d.scene.selected())
        self.assertEqual(host.current_mode(), "run")
        self.assertGreater(len(host._ws_run.vertices), 0)
        host.close()

    def test_filmstrip_bind_tracks_history(self):
        from playground.ui.filmstrip import StudioFilmstrip
        scene = Scene2D()
        obj = scene.selected()
        scene.apply_rotate(45.0)
        strip = StudioFilmstrip()
        strip.bind(obj)
        self.assertEqual(len(strip._frames), 2)
        self.assertEqual(strip._frames[0][1], -1)
        self.assertEqual(strip._frames[1][1], 0)


if __name__ == "__main__":
    unittest.main()
