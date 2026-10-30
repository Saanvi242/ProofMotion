"""
tests/test_theorems.py
----------------------
Unit tests for mathematical theorem verification and proof generation.
"""

import unittest
import math
from theorems.theorem_engine import TheoremEngine
import theorems.pythagorean as pyth
import theorems.circle_geometry as circ
import theorems.similar_triangles as sim
import theorems.law_of_cosines as loc


class TestTheorems(unittest.TestCase):
    def setUp(self):
        self.engine = TheoremEngine()

    def test_pythagorean_calculation(self):
        # 3-4-5 right triangle
        steps = pyth.generate_proof_steps({"side_a": 3.0, "side_b": 4.0})
        self.assertEqual(len(steps), 4)
        last_step = steps[-1]
        self.assertEqual(last_step.values["c"], 5.0)
        self.assertEqual(last_step.values["c²"], 25.0)

        # 5-12-13 right triangle
        steps_13 = pyth.generate_proof_steps({"side_a": 5.0, "side_b": 12.0})
        self.assertEqual(steps_13[-1].values["c"], 13.0)

    def test_pythagorean_validation(self):
        ok, msg = pyth.validate_parameters({"side_a": -3.0, "side_b": 4.0})
        self.assertFalse(ok)
        ok, msg = pyth.validate_parameters({"side_a": 3.0, "side_b": 4.0})
        self.assertTrue(ok)

    def test_circle_geometry(self):
        r = 7.0
        steps = circ.generate_proof_steps({"radius": r})
        self.assertEqual(len(steps), 4)
        last_step = steps[-1]
        expected_area = math.pi * r * r
        expected_circ = 2.0 * math.pi * r
        self.assertAlmostEqual(last_step.values["area"], expected_area, places=1)
        self.assertAlmostEqual(last_step.values["circumference"], expected_circ, places=1)

    def test_similar_triangles(self):
        steps = sim.generate_proof_steps({"side_a": 6.0, "side_b": 8.0, "ratio": 2.0})
        self.assertEqual(len(steps), 4)
        last_step = steps[-1]
        self.assertEqual(last_step.values["ratio_a"], 2.0)
        self.assertEqual(last_step.values["ratio_b"], 2.0)
        self.assertEqual(last_step.values["area_ratio"], 4.0)

    def test_law_of_cosines(self):
        # When C = 90 deg, c² should equal a² + b² (Pythagorean)
        steps_90 = loc.generate_proof_steps({"side_a": 6.0, "side_b": 8.0, "angle_c": 90.0})
        self.assertAlmostEqual(steps_90[-1].values["c"], 10.0, places=1)

        # When C = 60 deg, a=5, b=5: equilateral triangle c = 5
        steps_60 = loc.generate_proof_steps({"side_a": 5.0, "side_b": 5.0, "angle_c": 60.0})
        self.assertAlmostEqual(steps_60[-1].values["c"], 5.0, places=1)


if __name__ == "__main__":
    unittest.main()
