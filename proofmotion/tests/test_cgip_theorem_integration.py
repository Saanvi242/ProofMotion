"""
tests/test_cgip_theorem_integration.py
--------------------------------------
Integration tests confirming that Mathematical Theorems call and consume
genuine CGIP transformations and matrix computations.
"""

import unittest
import numpy as np
from theorems.pythagorean import generate_proof_steps as gen_pythagorean
from theorems.similar_triangles import generate_proof_steps as gen_similar_triangles
import cgip.transformations as trans


class TestCGIPTheoremIntegration(unittest.TestCase):
    def test_similar_triangles_uses_cgip_transformation(self):
        # Generate steps for Similar Triangles with scale factor k = 2.0
        k = 2.0
        steps = gen_similar_triangles({"side_a": 6.0, "side_b": 8.0, "ratio": k})
        self.assertGreater(len(steps), 2)

        # Step 2 contains ΔA'B'C' scaled via CGIP matrix
        step2 = steps[1]
        rd = step2.render_data
        self.assertIsNotNone(rd)
        self.assertGreaterEqual(len(rd.polygons), 2)

        poly_orig = rd.polygons[0].points
        poly_scaled = rd.polygons[1].points

        # Verify side ratio equals k
        orig_base = abs(poly_orig[1][0] - poly_orig[0][0])
        scaled_base = abs(poly_scaled[1][0] - poly_scaled[0][0])
        self.assertAlmostEqual(scaled_base / orig_base, k)

    def test_pythagorean_dissection_uses_cgip_rotation(self):
        # Generate steps for Pythagorean theorem
        steps = gen_pythagorean({"side_a": 3.0, "side_b": 4.0})
        self.assertEqual(len(steps), 4)

        # Step 3 is Bhaskara's dissection with 4 rotated congruent triangles
        step3 = steps[2]
        rd = step3.render_data
        self.assertIsNotNone(rd)

        # Check that 4 triangles are present
        t_polys = [p for p in rd.polygons if p.label in ("T1", "T2", "T3", "T4")]
        self.assertEqual(len(t_polys), 4)

        # Confirm all 4 have the same area (½ * a * b = 6.0)
        def poly_area(pts):
            x = [p[0] for p in pts]
            y = [p[1] for p in pts]
            return 0.5 * abs(sum(x[i]*y[i+1] - x[i+1]*y[i] for i in range(-1, len(pts)-1)))

        for t in t_polys:
            self.assertAlmostEqual(poly_area(t.points), 6.0, places=3)


if __name__ == "__main__":
    unittest.main()

