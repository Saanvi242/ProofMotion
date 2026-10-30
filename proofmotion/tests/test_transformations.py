"""
tests/test_transformations.py
-----------------------------
Unit tests for 2D Transformation matrices and Window-to-Viewport mapping.
"""

import unittest
import math
import numpy as np
import cgip.transformations as trans


class TestTransformations(unittest.TestCase):
    def test_translation(self):
        m = trans.translation_matrix(5.0, -3.0)
        pts = [(1.0, 2.0)]
        res = trans.apply_transform(m, pts)
        self.assertAlmostEqual(res[0][0], 6.0)
        self.assertAlmostEqual(res[0][1], -1.0)

    def test_scaling(self):
        m = trans.scaling_matrix(2.0, 3.0)
        pts = [(2.0, 4.0)]
        res = trans.apply_transform(m, pts)
        self.assertAlmostEqual(res[0][0], 4.0)
        self.assertAlmostEqual(res[0][1], 12.0)

    def test_rotation_90(self):
        m = trans.rotation_matrix(90.0)
        pts = [(1.0, 0.0)]
        res = trans.apply_transform(m, pts)
        self.assertAlmostEqual(res[0][0], 0.0)
        self.assertAlmostEqual(res[0][1], 1.0)

    def test_reflection(self):
        m_x = trans.reflection_matrix("X-axis")
        pts = [(3.0, 4.0)]
        res_x = trans.apply_transform(m_x, pts)
        self.assertAlmostEqual(res_x[0][0], 3.0)
        self.assertAlmostEqual(res_x[0][1], -4.0)

        m_y = trans.reflection_matrix("Y-axis")
        res_y = trans.apply_transform(m_y, pts)
        self.assertAlmostEqual(res_y[0][0], -3.0)
        self.assertAlmostEqual(res_y[0][1], 4.0)

    def test_composite_order(self):
        # Translate then Rotate vs Rotate then Translate:
        t = trans.translation_matrix(2.0, 0.0)
        r = trans.rotation_matrix(90.0)

        # In column-vector convention P' = M * P:
        # Applying T then R: P' = R * (T * P) = (R @ T) * P
        p = [(0.0, 0.0)]
        res_TR = trans.apply_transform(r @ t, p) # translate (0,0) -> (2,0), then rotate 90 -> (0,2)
        self.assertAlmostEqual(res_TR[0][0], 0.0)
        self.assertAlmostEqual(res_TR[0][1], 2.0)

        # Applying R then T: P' = T * (R * P) = (T @ R) * P
        res_RT = trans.apply_transform(t @ r, p) # rotate (0,0) -> (0,0), then translate -> (2,0)
        self.assertAlmostEqual(res_RT[0][0], 2.0)
        self.assertAlmostEqual(res_RT[0][1], 0.0)

    def test_window_to_viewport(self):
        steps = trans.window_to_viewport_trace(
            w_min=(-10.0, -10.0), w_max=(10.0, 10.0),
            v_min=(0.0, 0.0), v_max=(200.0, 200.0),
            sample_points=[(0.0, 0.0)]
        )
        self.assertGreater(len(steps), 0)
        # World origin (0, 0) should map to viewport center (100, 100)
        last_step = steps[-1]
        self.assertEqual(last_step.values["screen_pt"], (100.0, 100.0))

    def test_invalid_window_raises(self):
        with self.assertRaises(ValueError):
            trans.window_to_viewport_trace(w_min=(10.0, 10.0), w_max=(-10.0, -10.0))


if __name__ == "__main__":
    unittest.main()
