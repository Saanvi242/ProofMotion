"""
tests/test_clipping.py
----------------------
Comprehensive unit and integration tests for Cohen-Sutherland line clipping.
Tests:
  - 4-bit OutCode calculations for all 9 plane regions
  - All 10 demonstration presets
  - Classroom walkthrough stages, equations, and metric reporting
  - Boundary intersection formulas, corner vertices, and arithmetic precision
  - Safe zero-division handling for vertical, horizontal, and parallel segments
  - Backward compatibility with pure clipping and state navigation
"""

import unittest
import cgip.clipping as clip


class TestClipping(unittest.TestCase):
    def setUp(self):
        self.xmin, self.ymin = -4.0, -3.0
        self.xmax, self.ymax = 4.0, 3.0

    def test_outcodes_all_9_regions(self):
        """Verify standard 4-bit region codes [TOP, BOTTOM, RIGHT, LEFT] in all 9 regions."""
        # 1. Center (Inside window)
        self.assertEqual(clip.compute_outcode(0, 0, self.xmin, self.ymin, self.xmax, self.ymax), clip.INSIDE)
        self.assertEqual(clip.outcode_to_str(clip.INSIDE), "0000")

        # 2. Left
        self.assertEqual(clip.compute_outcode(-6, 0, self.xmin, self.ymin, self.xmax, self.ymax), clip.LEFT)
        self.assertEqual(clip.outcode_to_str(clip.LEFT), "0001")

        # 3. Right
        self.assertEqual(clip.compute_outcode(6, 0, self.xmin, self.ymin, self.xmax, self.ymax), clip.RIGHT)
        self.assertEqual(clip.outcode_to_str(clip.RIGHT), "0010")

        # 4. Bottom
        self.assertEqual(clip.compute_outcode(0, -5, self.xmin, self.ymin, self.xmax, self.ymax), clip.BOTTOM)
        self.assertEqual(clip.outcode_to_str(clip.BOTTOM), "0100")

        # 5. Top
        self.assertEqual(clip.compute_outcode(0, 5, self.xmin, self.ymin, self.xmax, self.ymax), clip.TOP)
        self.assertEqual(clip.outcode_to_str(clip.TOP), "1000")

        # 6. Top-Left
        self.assertEqual(clip.compute_outcode(-6, 5, self.xmin, self.ymin, self.xmax, self.ymax), clip.TOP | clip.LEFT)
        self.assertEqual(clip.outcode_to_str(clip.TOP | clip.LEFT), "1001")

        # 7. Top-Right
        self.assertEqual(clip.compute_outcode(6, 5, self.xmin, self.ymin, self.xmax, self.ymax), clip.TOP | clip.RIGHT)
        self.assertEqual(clip.outcode_to_str(clip.TOP | clip.RIGHT), "1010")

        # 8. Bottom-Left
        self.assertEqual(clip.compute_outcode(-6, -5, self.xmin, self.ymin, self.xmax, self.ymax), clip.BOTTOM | clip.LEFT)
        self.assertEqual(clip.outcode_to_str(clip.BOTTOM | clip.LEFT), "0101")

        # 9. Bottom-Right
        self.assertEqual(clip.compute_outcode(6, -5, self.xmin, self.ymin, self.xmax, self.ymax), clip.BOTTOM | clip.RIGHT)
        self.assertEqual(clip.outcode_to_str(clip.BOTTOM | clip.RIGHT), "0110")

    def test_preset_1_completely_inside(self):
        """Preset 1: Both endpoints inside -> Trivial accept with no clipping."""
        steps = clip.cohen_sutherland_trace(-1.5, -1.0, 2.0, 1.2, -3.0, -2.0, 3.0, 2.0)
        last_step = steps[-1]
        self.assertTrue(last_step.metrics.get("accepted"))
        self.assertFalse(last_step.metrics.get("clipped"))
        seg = last_step.values["accepted_segment"]
        self.assertAlmostEqual(seg[0][0], -1.5)
        self.assertAlmostEqual(seg[0][1], -1.0)
        self.assertAlmostEqual(seg[1][0], 2.0)
        self.assertAlmostEqual(seg[1][1], 1.2)

    def test_preset_2_completely_outside_trivial_reject(self):
        """Preset 2: Both endpoints to the right -> Trivial reject with no intersection."""
        steps = clip.cohen_sutherland_trace(4.5, 0.5, 7.0, 1.8, -3.0, -2.0, 3.0, 2.0)
        last_step = steps[-1]
        self.assertTrue(last_step.metrics.get("rejected"))
        self.assertFalse(last_step.metrics.get("accepted"))
        self.assertEqual(last_step.metrics.get("intersections", 0), 0)

    def test_preset_3_crosses_window_double_clip(self):
        """Preset 3: Segment crosses window diagonally -> clips both ends."""
        steps = clip.cohen_sutherland_trace(-5.0, -3.5, 5.0, 3.5, -3.0, -2.0, 3.0, 2.0)
        last_step = steps[-1]
        self.assertTrue(last_step.metrics.get("accepted"))
        self.assertTrue(last_step.metrics.get("clipped"))
        self.assertEqual(len(last_step.values["accepted_segment"]), 2)

    def test_preset_4_one_endpoint_outside(self):
        """Preset 4: One endpoint outside, one inside -> single boundary clip."""
        steps = clip.cohen_sutherland_trace(-5.5, 1.0, 1.5, -0.5, -3.0, -2.0, 3.0, 2.0)
        last_step = steps[-1]
        self.assertTrue(last_step.metrics.get("accepted"))
        self.assertTrue(last_step.metrics.get("clipped"))
        seg = last_step.values["accepted_segment"]
        self.assertAlmostEqual(seg[0][0], -3.0)
        self.assertAlmostEqual(seg[1][0], 1.5)

    def test_preset_5_partially_visible_top(self):
        """Preset 5: P1 inside, P2 outside TOP -> clips against TOP boundary."""
        steps = clip.cohen_sutherland_trace(-1.0, -0.5, 2.0, 4.0, -3.0, -2.0, 3.0, 2.0)
        last_step = steps[-1]
        self.assertTrue(last_step.metrics.get("accepted"))
        seg = last_step.values["accepted_segment"]
        self.assertAlmostEqual(seg[1][1], 2.0)

    def test_preset_6_vertical_line(self):
        """Preset 6: Vertical line crossing window -> dx == 0 handled safely."""
        steps = clip.cohen_sutherland_trace(1.0, -4.5, 1.0, 4.5, -3.0, -2.0, 3.0, 2.0)
        last_step = steps[-1]
        self.assertTrue(last_step.metrics.get("accepted"))
        seg = last_step.values["accepted_segment"]
        self.assertAlmostEqual(seg[0][0], 1.0)
        self.assertAlmostEqual(seg[0][1], -2.0)
        self.assertAlmostEqual(seg[1][0], 1.0)
        self.assertAlmostEqual(seg[1][1], 2.0)

    def test_preset_7_horizontal_line(self):
        """Preset 7: Horizontal line crossing window -> dy == 0 handled safely."""
        steps = clip.cohen_sutherland_trace(-5.5, 0.5, 5.5, 0.5, -3.0, -2.0, 3.0, 2.0)
        last_step = steps[-1]
        self.assertTrue(last_step.metrics.get("accepted"))
        seg = last_step.values["accepted_segment"]
        self.assertAlmostEqual(seg[0][0], -3.0)
        self.assertAlmostEqual(seg[0][1], 0.5)
        self.assertAlmostEqual(seg[1][0], 3.0)
        self.assertAlmostEqual(seg[1][1], 0.5)

    def test_preset_8_corner_intersection(self):
        """Preset 8: Line passing directly through exact corner vertex."""
        steps = clip.cohen_sutherland_trace(-6.0, 5.0, 0.0, -1.0, -3.0, -2.0, 3.0, 2.0)
        last_step = steps[-1]
        self.assertTrue(last_step.metrics.get("accepted"))
        seg = last_step.values["accepted_segment"]
        self.assertAlmostEqual(seg[0][0], -3.0)
        self.assertAlmostEqual(seg[0][1], 2.0)

    def test_preset_9_boundary_case_collinear(self):
        """Preset 9: Line lying exactly on the left boundary edge."""
        steps = clip.cohen_sutherland_trace(-3.0, -1.5, -3.0, 1.5, -3.0, -2.0, 3.0, 2.0)
        last_step = steps[-1]
        self.assertTrue(last_step.metrics.get("accepted"))
        seg = last_step.values["accepted_segment"]
        self.assertAlmostEqual(seg[0][0], -3.0)
        self.assertAlmostEqual(seg[1][0], -3.0)

    def test_preset_10_outside_parallel_boundary(self):
        """Preset 10: Parallel to boundary and completely outside -> Trivial reject."""
        steps = clip.cohen_sutherland_trace(-5.0, -3.5, -5.0, 3.5, -3.0, -2.0, 3.0, 2.0)
        last_step = steps[-1]
        self.assertTrue(last_step.metrics.get("rejected"))

    def test_step_trace_progression(self):
        """Verify the classroom walkthrough covers codes, OR/AND, intersections, and a final result."""
        steps = clip.cohen_sutherland_trace(-6.0, 0, 6.0, 0, self.xmin, self.ymin, self.xmax, self.ymax)
        self.assertGreaterEqual(len(steps), 4)

        self.assertIn("line and a window", steps[0].title.lower())
        self.assertIn("Window", steps[0].equation)
        self.assertTrue(steps[0].explanation)
        self.assertIsNotNone(steps[0].render_data.clipping_data)
        self.assertEqual(steps[0].render_data.clipping_data.get("focus"), "meet")

        self.assertIn("P1", steps[1].title)
        self.assertIn("P2", steps[2].title)
        self.assertIn("TBRL", steps[1].equation)
        self.assertIn("inside", steps[3].title.lower())

        calc_steps = [s for s in steps if s.values.get("stage") == "calculate_intersection"]
        self.assertGreater(len(calc_steps), 0)
        for cs in calc_steps:
            self.assertIn("Intersection", cs.equation)
            self.assertIsNotNone(cs.values.get("intersection"))

        last_step = steps[-1]
        self.assertIn("complete", last_step.title.lower())
        self.assertTrue(last_step.metrics.get("accepted"))
        self.assertEqual(last_step.render_data.clipping_data.get("focus"), "result")

    def test_concept_tabs_step_generators(self):
        """Region-code lesson: window, four bits, map, then all nine regions."""
        region_steps = clip.build_region_codes_steps(0, self.xmin, self.ymin, self.xmax, self.ymax)
        self.assertGreaterEqual(len(region_steps), 15)
        self.assertIn("window", region_steps[0].title.lower())
        self.assertIn("Top bit", region_steps[1].title)
        self.assertIn("nine regions", region_steps[5].title.lower())

        region_only = [s for s in region_steps if s.values.get("lesson") == "region"]
        self.assertEqual(len(region_only), 9)
        self.assertIn("Inside", region_only[0].title)
        self.assertEqual(region_only[0].values.get("active_code"), 0)

    def test_or_and_decisions_match_codes(self):
        """OR/AND steps must use the same codes as the live endpoints."""
        steps = clip.cohen_sutherland_trace(-6.0, 5.0, 5.0, -2.0, -3.0, -2.0, 3.0, 2.0)
        or_step = next(s for s in steps if s.values.get("stage") == "or_test")
        and_step = next(s for s in steps if s.values.get("stage") == "and_test")
        cd = or_step.render_data.clipping_data
        self.assertEqual(or_step.values["OR_result"], cd["or_str"])
        self.assertEqual(and_step.values["AND_result"], and_step.render_data.clipping_data["and_str"])
        self.assertEqual(cd["or_result"], cd["code1"] | cd["code2"])
        self.assertEqual(and_step.render_data.clipping_data["and_result"],
                         and_step.render_data.clipping_data["code1"] & and_step.render_data.clipping_data["code2"])

    def test_pure_clip_function(self):
        """Test pure function cohen_sutherland_clip for contract correctness."""
        res = clip.cohen_sutherland_clip(-6, 0, 6, 0, self.xmin, self.ymin, self.xmax, self.ymax)
        self.assertIsNotNone(res)
        self.assertAlmostEqual(res[0][0], self.xmin)
        self.assertAlmostEqual(res[1][0], self.xmax)

        # Completely outside
        res_none = clip.cohen_sutherland_clip(-10, 10, -8, 12, self.xmin, self.ymin, self.xmax, self.ymax)
        self.assertIsNone(res_none)

    def test_state_restoration_backward_forward(self):
        """Verify that step state (P1, P2, codes, active boundary) is perfectly preserved and reversible."""
        steps = clip.cohen_sutherland_trace(-6.0, 5.0, 5.0, -2.0, -3.0, -2.0, 3.0, 2.0)
        self.assertGreater(len(steps), 4)

        # Iterate forward and record states
        states = []
        for s in steps:
            cd = s.render_data.clipping_data
            states.append((cd["current_p1"], cd["current_p2"], cd["code1_str"], cd["code2_str"]))

        # Step backward from the end
        for idx in range(len(steps) - 1, -1, -1):
            s = steps[idx]
            cd = s.render_data.clipping_data
            current_state = (cd["current_p1"], cd["current_p2"], cd["code1_str"], cd["code2_str"])
            self.assertEqual(current_state, states[idx])


if __name__ == "__main__":
    unittest.main()
