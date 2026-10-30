"""
tests/test_projection_3d.py
---------------------------
Unit tests for 3D geometric transformations and projections.
"""

import unittest
import math
import numpy as np
import cgip.projection_3d as p3d


class TestProjection3D(unittest.TestCase):
    def test_translation_3d(self):
        m = p3d.translation_matrix_3d(2.0, 3.0, -4.0)
        pts = [(1.0, 1.0, 1.0)]
        res = p3d.apply_transform_3d(m, pts)
        self.assertAlmostEqual(res[0][0], 3.0)
        self.assertAlmostEqual(res[0][1], 4.0)
        self.assertAlmostEqual(res[0][2], -3.0)

    def test_scaling_3d(self):
        m = p3d.scaling_matrix_3d(2.0, 0.5, 3.0)
        pts = [(3.0, 4.0, 2.0)]
        res = p3d.apply_transform_3d(m, pts)
        self.assertAlmostEqual(res[0][0], 6.0)
        self.assertAlmostEqual(res[0][1], 2.0)
        self.assertAlmostEqual(res[0][2], 6.0)

    def test_rotations_3d(self):
        # 90 degree rotation around X-axis: (0, 1, 0) -> (0, 0, 1)
        rx = p3d.rotation_x_matrix_3d(90.0)
        res_x = p3d.apply_transform_3d(rx, [(0.0, 1.0, 0.0)])
        self.assertAlmostEqual(res_x[0][0], 0.0)
        self.assertAlmostEqual(res_x[0][1], 0.0)
        self.assertAlmostEqual(res_x[0][2], 1.0)

        # 90 degree rotation around Y-axis: (0, 0, 1) -> (1, 0, 0)
        ry = p3d.rotation_y_matrix_3d(90.0)
        res_y = p3d.apply_transform_3d(ry, [(0.0, 0.0, 1.0)])
        self.assertAlmostEqual(res_y[0][0], 1.0)
        self.assertAlmostEqual(res_y[0][1], 0.0)
        self.assertAlmostEqual(res_y[0][2], 0.0)

        # 90 degree rotation around Z-axis: (1, 0, 0) -> (0, 1, 0)
        rz = p3d.rotation_z_matrix_3d(90.0)
        res_z = p3d.apply_transform_3d(rz, [(1.0, 0.0, 0.0)])
        self.assertAlmostEqual(res_z[0][0], 0.0)
        self.assertAlmostEqual(res_z[0][1], 1.0)
        self.assertAlmostEqual(res_z[0][2], 0.0)

    def test_orthographic_projection(self):
        pts_3d = [(2.0, 3.0, 10.0), (-4.0, 5.0, -20.0)]
        res_2d = p3d.project_orthographic(pts_3d, scale=1.5)
        self.assertAlmostEqual(res_2d[0][0], 3.0)
        self.assertAlmostEqual(res_2d[0][1], 4.5)
        self.assertAlmostEqual(res_2d[1][0], -6.0)
        self.assertAlmostEqual(res_2d[1][1], 7.5)

    def test_perspective_projection(self):
        # Point on optical axis (0, 0, 0)
        pts_3d = [(0.0, 0.0, 0.0), (2.0, 4.0, 2.0)]
        # camera_z = 6.0, focal_dist = 4.0
        # for (2, 4, 2): denom = 6 - 2 = 4; factor = 4 / 4 = 1.0 -> (2.0, 4.0)
        res_2d = p3d.project_perspective(pts_3d, focal_distance=4.0, camera_z=6.0)
        self.assertEqual(res_2d[0], (0.0, 0.0))
        self.assertAlmostEqual(res_2d[1][0], 2.0)
        self.assertAlmostEqual(res_2d[1][1], 4.0)

    def test_model_matrix_3d(self):
        m = p3d.model_matrix_3d(tx=1.0, ty=2.0, tz=3.0, sx=2.0, sy=2.0, sz=2.0, rx_deg=0.0, ry_deg=0.0, rz_deg=0.0)
        res = p3d.apply_transform_3d(m, [(1.0, 1.0, 1.0)])
        self.assertAlmostEqual(res[0][0], 3.0)
        self.assertAlmostEqual(res[0][1], 4.0)
        self.assertAlmostEqual(res[0][2], 5.0)

    def test_projection_matrices_4x4(self):
        p_persp = p3d.perspective_projection_matrix(fov_deg=45.0, aspect=1.0, near=0.1, far=100.0)
        self.assertEqual(p_persp.shape, (4, 4))
        self.assertAlmostEqual(p_persp[3, 2], -1.0)
        self.assertEqual(p_persp[3, 3], 0.0)

        p_ortho = p3d.orthographic_projection_matrix(left=-4.0, right=4.0, bottom=-4.0, top=4.0, near=0.1, far=100.0)
        self.assertEqual(p_ortho.shape, (4, 4))
        self.assertAlmostEqual(p_ortho[0, 0], 2.0 / 8.0)
        self.assertAlmostEqual(p_ortho[1, 1], 2.0 / 8.0)

    def test_look_at_matrix(self):
        v = p3d.look_at_matrix(eye=(0.0, 0.0, 10.0), target=(0.0, 0.0, 0.0), up=(0.0, 1.0, 0.0))
        self.assertEqual(v.shape, (4, 4))
        origin_view = v @ np.array([0.0, 0.0, 0.0, 1.0])
        self.assertAlmostEqual(origin_view[0], 0.0)
        self.assertAlmostEqual(origin_view[1], 0.0)
        self.assertAlmostEqual(origin_view[2], -10.0)

    def test_generate_3d_demo_steps(self):
        steps = p3d.generate_3d_demo("cube", "perspective", rx_deg=20.0, ry_deg=30.0, tx=1.0, ty=2.0)
        self.assertEqual(len(steps), 3)
        self.assertIn("3D Model Definition", steps[0].title)
        self.assertIn("3D Model Transformation", steps[1].title)
        self.assertIn("3D to 2D Projection", steps[2].title)


if __name__ == "__main__":
    unittest.main()

