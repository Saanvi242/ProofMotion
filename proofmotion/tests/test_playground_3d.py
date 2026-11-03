"""
tests/test_playground_3d.py
---------------------------
Unit tests for the 3D Interactive Graphics Playground scene, TRS matrices,
projections, and primitive topology.
"""

import unittest
import numpy as np

from playground.scene_3d import Scene3D
from playground.math_sync import inspector_payload_3d
from playground.models import animated_composed_matrix, interpolate_op_matrix
import cgip.projection_3d as p3d


class TestPlayground3D(unittest.TestCase):
    def setUp(self):
        self.scene = Scene3D()
        self.scene.objects.clear()
        self.scene.selected_id = None

    def test_add_primitives(self):
        cube = self.scene.add_object("cube")
        sphere = self.scene.add_object("sphere")
        pyr = self.scene.add_object("pyramid")
        cyl = self.scene.add_object("cylinder")
        self.assertEqual(len(self.scene.objects), 4)
        self.assertEqual(cube.kind, "cube")
        self.assertEqual(sphere.kind, "sphere")
        self.assertEqual(pyr.kind, "pyramid")
        self.assertEqual(cyl.kind, "cylinder")
        self.assertEqual(self.scene.selected_id, cyl.id)

    def test_pose_uses_model_matrix_3d(self):
        obj = self.scene.add_object("cube")
        self.scene.set_pose(tx=1.0, ty=2.0, tz=3.0, sx=2.0, sy=2.0, sz=2.0, rx=0, ry=0, rz=0)
        expected = p3d.model_matrix_3d(tx=1, ty=2, tz=3, sx=2, sy=2, sz=2)
        np.testing.assert_allclose(obj.pose_matrix(), expected, atol=1e-9)
        world = obj.world_vertices()
        local = obj.local_vertices()
        rebuilt = p3d.apply_transform_3d(expected, local)
        np.testing.assert_allclose(world, rebuilt, atol=1e-9)

    def test_sequential_translate_then_rotate_y(self):
        obj = self.scene.add_object("cube")
        # Use a single point via applying to origin-offset: cube vertex (1,0,0) after identity pose
        self.scene.apply_translate(0.0, 0.0, 0.0)
        obj.history.clear()
        from playground.models import make_translate_op_3d, make_rotate_op_3d
        obj.apply_op(make_translate_op_3d(2.0, 0.0, 0.0))
        obj.apply_op(make_rotate_op_3d("y", 90.0))
        # Point (1,0,0): T -> (3,0,0); Ry(90) -> (0,0,-3)
        pts = p3d.apply_transform_3d(obj.composed_matrix(), [(1.0, 0.0, 0.0)])
        self.assertAlmostEqual(pts[0][0], 0.0, places=6)
        self.assertAlmostEqual(pts[0][1], 0.0, places=6)
        self.assertAlmostEqual(pts[0][2], -3.0, places=6)

    def test_inspector_matrix_equals_composed(self):
        obj = self.scene.add_object("pyramid")
        self.scene.set_pose(rx=20.0, ry=35.0, tz=-1.0)
        self.scene.apply_scale(1.2, 1.0, 0.8)
        payload = inspector_payload_3d(obj, projection_mode="perspective", fov_deg=50.0)
        np.testing.assert_allclose(payload["matrix"], obj.composed_matrix(), atol=1e-9)
        np.testing.assert_allclose(
            payload["multiply"]["result_matrix"],
            payload["multiply"]["op_matrix"] @ payload["multiply"]["prev_matrix"],
            atol=1e-9,
        )
        self.assertEqual(payload["projection"]["mode"], "perspective")
        self.assertEqual(payload["projection"]["fov"], 50.0)

    def test_render_payload_contains_numpy_model(self):
        self.scene.add_object("cube")
        payload = self.scene.render_payload()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["model"].shape, (4, 4))
        self.assertTrue(payload[0]["selected"])

    def test_projection_and_fov_state(self):
        self.scene.set_projection_mode("orthographic")
        self.assertEqual(self.scene.projection_mode, "orthographic")
        self.scene.set_fov(70.0)
        self.assertEqual(self.scene.fov_deg, 70.0)
        p = p3d.perspective_projection_matrix(fov_deg=70.0, aspect=1.0, near=0.1, far=100.0)
        self.assertAlmostEqual(p[3, 2], -1.0)
        wide = p3d.perspective_projection_matrix(fov_deg=80.0, aspect=1.0, near=0.1, far=100.0)
        tight = p3d.perspective_projection_matrix(fov_deg=30.0, aspect=1.0, near=0.1, far=100.0)
        self.assertLess(abs(wide[1, 1]), abs(tight[1, 1]))

    def test_camera_reset(self):
        self.scene.set_camera(azimuth=10, elevation=5, distance=12, pan_x=1, pan_y=2)
        self.scene.reset_camera()
        self.assertEqual(self.scene.camera["azimuth"], 35.0)
        self.assertEqual(self.scene.camera["distance"], 7.0)

    def test_compare_mode_flag(self):
        self.scene.set_compare_mode(True)
        self.assertTrue(self.scene.compare_mode)

    def test_animation_interpolation_reaches_full_op(self):
        obj = self.scene.add_object("cube")
        self.scene.apply_translate(4.0, 0.0, 0.0)
        m0 = animated_composed_matrix(obj, 0.0, dim=3)
        m1 = animated_composed_matrix(obj, 1.0, dim=3)
        np.testing.assert_allclose(m0, obj.matrix_without_last(), atol=1e-9)
        np.testing.assert_allclose(m1, obj.composed_matrix(), atol=1e-9)
        mid = interpolate_op_matrix(obj.history[-1], 0.5, dim=3)
        expected_mid = p3d.translation_matrix_3d(2.0, 0.0, 0.0)
        np.testing.assert_allclose(mid, expected_mid, atol=1e-9)

    def test_sphere_and_cylinder_topology(self):
        sv, se, sf = p3d.get_wireframe_sphere(slices=16, stacks=12)
        self.assertEqual(len(sv), 16 * 13)
        self.assertGreater(len(se), 0)
        self.assertGreater(len(sf), 0)
        cv, ce, cf = p3d.get_wireframe_cylinder(slices=20)
        self.assertEqual(len(cv), 20 * 2 + 2)
        self.assertGreater(len(ce), 0)
        self.assertGreater(len(cf), 0)
        cube_v, cube_e, cube_f = p3d.get_mesh_3d("cube")
        self.assertEqual(len(cube_v), 8)
        self.assertEqual(len(cube_e), 12)
        self.assertEqual(len(cube_f), 12)


if __name__ == "__main__":
    unittest.main()
