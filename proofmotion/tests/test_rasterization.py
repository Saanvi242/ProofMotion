"""
tests/test_rasterization.py
---------------------------
Unit tests for DDA, Bresenham (all octants), and Midpoint Circle.
"""

import unittest
import cgip.rasterization as rast


class TestRasterization(unittest.TestCase):
    def test_dda_horizontal_and_vertical(self):
        # Horizontal: (2, 5) to (8, 5)
        steps_h = rast.dda_line_trace(2, 5, 8, 5)
        self.assertGreater(len(steps_h), 0)
        # Vertical: (4, 1) to (4, 9)
        steps_v = rast.dda_line_trace(4, 1, 4, 9)
        self.assertGreater(len(steps_v), 0)

    def test_dda_zero_length(self):
        steps = rast.dda_line_trace(5, 5, 5, 5)
        self.assertEqual(len(steps), 1)

    def test_bresenham_octants(self):
        # Shallow positive slope (|m| <= 1): (0, 0) to (8, 4)
        s1 = rast.bresenham_line_trace(0, 0, 8, 4)
        self.assertGreater(len(s1), 0)

        # Steep positive slope (|m| > 1): (0, 0) to (3, 8)
        s2 = rast.bresenham_line_trace(0, 0, 3, 8)
        self.assertGreater(len(s2), 0)

        # Negative slope: (0, 8) to (8, 2)
        s3 = rast.bresenham_line_trace(0, 8, 8, 2)
        self.assertGreater(len(s3), 0)

        # Reverse direction: (8, 8) to (0, 0)
        s4 = rast.bresenham_line_trace(8, 8, 0, 0)
        self.assertGreater(len(s4), 0)

    def test_midpoint_circle(self):
        r = 6
        steps = rast.midpoint_circle_trace(10, 10, r)
        self.assertGreater(len(steps), 0)
        last_step = steps[-1]
        self.assertGreater(last_step.values["total_pixels"], 0)

    def test_dda_vs_bresenham_comparison(self):
        steps = rast.dda_vs_bresenham_comparison_trace(2, 3, 17, 11)
        self.assertEqual(len(steps), 4)
        self.assertIn("Comparison Setup", steps[0].title)
        self.assertIn("DDA Result", steps[1].title)
        self.assertIn("Bresenham Result", steps[2].title)
        self.assertIn("Comparison:", steps[3].title)
        self.assertTrue("matching_count" in steps[3].values)


    def test_rasterization_endpoint_to_line_progression(self):
        # DDA progression test
        dda_steps = rast.dda_line_trace(2, 3, 16, 11)
        self.assertGreater(len(dda_steps), 2)
        # Step 0 (Setup): Only endpoints, NO line drawn yet
        self.assertIsNone(dda_steps[0].render_data.pixel_grid.get("ideal_line"))
        self.assertEqual(dda_steps[0].render_data.pixel_grid.get("start_point"), (2, 3))
        self.assertEqual(dda_steps[0].render_data.pixel_grid.get("end_point"), (16, 11))
        # Intermediate steps: finding pixels, NO line drawn
        self.assertIsNone(dda_steps[1].render_data.pixel_grid.get("ideal_line"))
        # Final step: line drawn using plotted pixels
        self.assertEqual(dda_steps[-1].render_data.pixel_grid.get("ideal_line"), (2, 3, 16, 11))

        # Bresenham progression test
        bres_steps = rast.bresenham_line_trace(2, 3, 16, 11)
        self.assertGreater(len(bres_steps), 2)
        self.assertIsNone(bres_steps[0].render_data.pixel_grid.get("ideal_line"))
        self.assertIsNone(bres_steps[1].render_data.pixel_grid.get("ideal_line"))
        self.assertEqual(bres_steps[-1].render_data.pixel_grid.get("ideal_line"), (2, 3, 16, 11))

        # Circle progression test
        circ_steps = rast.midpoint_circle_trace(10, 10, 7)
        self.assertGreater(len(circ_steps), 2)
        self.assertIsNone(circ_steps[0].render_data.pixel_grid.get("ideal_circle"))
        self.assertEqual(circ_steps[-1].render_data.pixel_grid.get("ideal_circle"), (10, 10, 7))


if __name__ == "__main__":
    unittest.main()
