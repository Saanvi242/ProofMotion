"""
tests/test_playground_2d.py
---------------------------
Unit tests for the 2D Interactive Graphics Playground scene, sequential
transforms, clipping, and inspector/matrix synchronization.
"""

import unittest
import numpy as np

from playground.scene_2d import Scene2D
from playground.math_sync import inspector_payload_2d, make_rotation_challenge_2d, format_matrix
import cgip.transformations as t2d
import cgip.clipping as clip


class TestPlayground2D(unittest.TestCase):
    def setUp(self):
        self.scene = Scene2D()
        self.scene.clear()

    def test_default_then_add_triangle(self):
        obj = self.scene.add_object("triangle")
        self.assertEqual(obj.kind, "triangle")
        self.assertEqual(len(obj.local_vertices), 3)
        self.assertEqual(self.scene.selected_id, obj.id)

    def test_pose_matches_trs_composition(self):
        obj = self.scene.add_object("point", [(1.0, 0.0)])
        self.scene.set_pose(tx=2.0, ty=1.0, rotation=90.0, sx=1.0, sy=1.0)
        world = obj.world_vertices()[0]
        expected = t2d.apply_transform(obj.pose_matrix(), [(1.0, 0.0)])[0]
        self.assertAlmostEqual(world[0], expected[0], places=6)
        self.assertAlmostEqual(world[1], expected[1], places=6)
        # T(2,1) · R(90) · (1,0) = T(2,1) · (0,1) = (2,2)
        self.assertAlmostEqual(world[0], 2.0, places=6)
        self.assertAlmostEqual(world[1], 2.0, places=6)

    def test_sequential_translate_then_rotate(self):
        obj = self.scene.add_object("point", [(1.0, 0.0)])
        self.scene.apply_translate(2.0, 0.0)
        self.scene.apply_rotate(90.0)
        world = obj.world_vertices()[0]
        # Apply T then R: (1,0) -> (3,0) -> (0,3)
        self.assertAlmostEqual(world[0], 0.0, places=6)
        self.assertAlmostEqual(world[1], 3.0, places=6)
        composed = t2d.compose_transformations(
            t2d.translation_matrix(2.0, 0.0),
            t2d.rotation_matrix(90.0),
        )
        np.testing.assert_allclose(obj.composed_matrix(), composed, atol=1e-9)

    def test_inspector_matrix_matches_rendered_vertices(self):
        obj = self.scene.add_object("triangle")
        self.scene.apply_scale(1.5, 0.5)
        self.scene.apply_translate(-1.0, 2.0)
        payload = inspector_payload_2d(obj)
        np.testing.assert_allclose(payload["matrix"], obj.composed_matrix())
        self.assertEqual(payload["world"], obj.world_vertices())
        rebuilt = t2d.apply_transform(payload["matrix"], obj.local_vertices)
        for a, b in zip(rebuilt, payload["world"]):
            self.assertAlmostEqual(a[0], b[0], places=6)
            self.assertAlmostEqual(a[1], b[1], places=6)
        self.assertIn("[", payload["matrix_str"])
        self.assertEqual(payload["multiply"]["equation"], "M = M_op · M_prev")
        np.testing.assert_allclose(
            payload["multiply"]["result_matrix"],
            payload["multiply"]["op_matrix"] @ payload["multiply"]["prev_matrix"],
            atol=1e-9,
        )

    def test_reflection_and_reset(self):
        obj = self.scene.add_object("point", [(3.0, 4.0)])
        self.scene.apply_reflect("X-axis")
        wx, wy = obj.world_vertices()[0]
        self.assertAlmostEqual(wx, 3.0, places=6)
        self.assertAlmostEqual(wy, -4.0, places=6)
        self.scene.reset_selected()
        wx, wy = obj.world_vertices()[0]
        self.assertAlmostEqual(wx, 3.0, places=6)
        self.assertAlmostEqual(wy, 4.0, places=6)
        self.assertEqual(len(obj.history), 0)

    def test_world_drag_without_history_updates_pose(self):
        obj = self.scene.add_object("point", [(0.0, 0.0)])
        self.scene.translate_world(1.5, -0.5, dragging=True)
        self.assertAlmostEqual(obj.tx, 1.5, places=6)
        self.assertAlmostEqual(obj.ty, -0.5, places=6)
        self.assertEqual(len(obj.history), 0)

    def test_hit_test_polygon(self):
        obj = self.scene.add_object("rectangle", [(-1, -1), (1, -1), (1, 1), (-1, 1)])
        self.assertEqual(self.scene.hit_test(0.0, 0.0), obj.id)
        self.assertIsNone(self.scene.hit_test(5.0, 5.0))

    def test_clipping_line_uses_cohen_sutherland(self):
        obj = self.scene.add_object("line", [(-6.0, 0.0), (6.0, 0.0)])
        self.scene.set_clip_enabled(True)
        self.scene.set_clip_rect(-3.0, -2.0, 3.0, 2.0)
        clipped = self.scene.clipped_geometry(obj)
        expected = clip.cohen_sutherland_clip(-6, 0, 6, 0, -3, -2, 3, 2)
        self.assertIsNotNone(clipped)
        self.assertAlmostEqual(clipped[0][0], expected[0][0], places=6)
        self.assertAlmostEqual(clipped[1][0], expected[1][0], places=6)

    def test_clipping_polygon_uses_sutherland_hodgman(self):
        verts = [(-4.0, -1.0), (4.0, -1.0), (0.0, 3.0)]
        obj = self.scene.add_object("triangle", verts)
        self.scene.set_clip_enabled(True)
        self.scene.set_clip_rect(-2.0, -2.0, 2.0, 2.0)
        clipped = self.scene.clipped_geometry(obj)
        expected = clip.sutherland_hodgman_polygon_clip(verts, -2, -2, 2, 2)
        self.assertEqual(len(clipped), len(expected))
        for a, b in zip(clipped, expected):
            self.assertAlmostEqual(a[0], b[0], places=5)
            self.assertAlmostEqual(a[1], b[1], places=5)

    def test_invalid_clip_rect_raises(self):
        with self.assertRaises(ValueError):
            self.scene.set_clip_rect(3.0, 0.0, -1.0, 1.0)

    def test_rotation_challenge_matches_matrix(self):
        obj = self.scene.add_object("triangle")
        challenge = make_rotation_challenge_2d(obj, 90.0)
        expected = t2d.apply_transform(t2d.rotation_matrix(90.0), obj.world_vertices())
        self.assertAlmostEqual(challenge["target"][0], expected[0][0], places=6)
        self.assertAlmostEqual(challenge["target"][1], expected[0][1], places=6)

    def test_format_matrix_shape(self):
        text = format_matrix(np.eye(3))
        self.assertIn("1.00", text)
        self.assertEqual(text.count("\n"), 2)


if __name__ == "__main__":
    unittest.main()
