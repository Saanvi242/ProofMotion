"""
tests/test_polygon_clipping.py
------------------------------
Unit tests for Sutherland-Hodgman Polygon Clipping:
  - Pure clip function on inside / outside / partial polygons
  - Four-case classroom lesson
  - Edge-by-edge trace whose final list matches the algorithm
  - All four boundaries visited with real intermediate vertex lists
"""

import unittest
import cgip.clipping as clip


def _round_poly(poly, ndigits=6):
    return [(round(float(x), ndigits), round(float(y), ndigits)) for x, y in poly]


class TestPolygonClipping(unittest.TestCase):
    def setUp(self):
        self.xmin, self.ymin = -2.0, -2.0
        self.xmax, self.ymax = 2.0, 2.0

    def test_polygon_fully_inside(self):
        tri = [(-1.0, -1.0), (1.0, -1.0), (0.0, 1.0)]
        clipped = clip.sutherland_hodgman_polygon_clip(tri, self.xmin, self.ymin, self.xmax, self.ymax)
        self.assertEqual(len(clipped), 3)
        for x, y in clipped:
            self.assertTrue(self.xmin <= x <= self.xmax)
            self.assertTrue(self.ymin <= y <= self.ymax)

    def test_polygon_fully_outside(self):
        poly = [(5.0, 0.0), (7.0, 0.0), (7.0, 2.0), (5.0, 2.0)]
        clipped = clip.sutherland_hodgman_polygon_clip(poly, self.xmin, self.ymin, self.xmax, self.ymax)
        self.assertEqual(len(clipped), 0)

    def test_polygon_partial_clipping(self):
        poly = [(-3.0, -3.0), (3.0, -3.0), (3.0, 3.0), (-3.0, 3.0)]
        clipped = clip.sutherland_hodgman_polygon_clip(poly, self.xmin, self.ymin, self.xmax, self.ymax)
        self.assertEqual(len(clipped), 4)
        for x, y in clipped:
            self.assertTrue(self.xmin - 1e-6 <= x <= self.xmax + 1e-6)
            self.assertTrue(self.ymin - 1e-6 <= y <= self.ymax + 1e-6)

    def test_classify_four_cases(self):
        self.assertEqual(clip.sh_classify(True, True), "in_in")
        self.assertEqual(clip.sh_classify(True, False), "in_out")
        self.assertEqual(clip.sh_classify(False, True), "out_in")
        self.assertEqual(clip.sh_classify(False, False), "out_out")

    def test_inside_and_intersect_all_boundaries(self):
        xmin, ymin, xmax, ymax = -3.0, -2.0, 3.0, 2.0
        self.assertTrue(clip.sh_inside((0.0, 0.0), "LEFT", xmin, ymin, xmax, ymax))
        self.assertFalse(clip.sh_inside((-4.0, 0.0), "LEFT", xmin, ymin, xmax, ymax))
        self.assertFalse(clip.sh_inside((4.0, 0.0), "RIGHT", xmin, ymin, xmax, ymax))
        self.assertFalse(clip.sh_inside((0.0, -3.0), "BOTTOM", xmin, ymin, xmax, ymax))
        self.assertFalse(clip.sh_inside((0.0, 3.0), "TOP", xmin, ymin, xmax, ymax))

        ix, iy = clip.sh_intersect((-5.0, 0.0), (1.0, 0.0), "LEFT", xmin, ymin, xmax, ymax)
        self.assertAlmostEqual(ix, xmin)
        self.assertAlmostEqual(iy, 0.0)
        ix, iy = clip.sh_intersect((0.0, -4.0), (0.0, 1.0), "BOTTOM", xmin, ymin, xmax, ymax)
        self.assertAlmostEqual(iy, ymin)
        self.assertAlmostEqual(ix, 0.0)

    def test_named_shapes_available(self):
        for name in ("triangle", "Crossing triangle", "diamond", "star", "Fully inside", "Fully outside"):
            poly = clip.get_polygon_shape(name)
            self.assertGreaterEqual(len(poly), 3)

    def test_four_cases_lesson(self):
        steps = clip.build_polygon_cases_steps(-3.0, -2.0, 3.0, 2.0)
        self.assertEqual(len(steps), 8)
        self.assertIn("clip a polygon", steps[0].title.lower())
        lessons = [s.values.get("lesson") for s in steps]
        self.assertEqual(lessons[0], "meet")
        self.assertEqual(lessons[1], "pipeline")
        self.assertEqual(lessons[2], "halfplane")
        cases = [s.values.get("case") for s in steps if s.values.get("lesson") == "case"]
        self.assertEqual(cases, ["in_in", "in_out", "out_in", "out_out"])
        self.assertEqual(steps[-1].values.get("lesson"), "wrap")
        for s in steps:
            cd = s.render_data.clipping_data
            self.assertEqual(cd.get("view_tab"), "four_cases")
            self.assertTrue(s.explanation)
            self.assertTrue(s.equation)

        in_out = next(s for s in steps if s.values.get("case") == "in_out")
        emitted = in_out.render_data.clipping_data.get("emitted") or []
        self.assertEqual(len(emitted), 1)
        self.assertEqual(emitted[0]["kind"], "new")

        out_in = next(s for s in steps if s.values.get("case") == "out_in")
        kinds = [item["kind"] for item in out_in.render_data.clipping_data.get("emitted") or []]
        self.assertEqual(kinds, ["new", "keep"])

        out_out = next(s for s in steps if s.values.get("case") == "out_out")
        self.assertEqual(out_out.render_data.clipping_data.get("emitted"), [])

    def test_sutherland_hodgman_trace_matches_clip(self):
        poly = clip.get_polygon_shape("triangle")
        xmin, ymin, xmax, ymax = -3.0, -2.0, 3.0, 2.0
        expected = clip.sutherland_hodgman_polygon_clip(poly, xmin, ymin, xmax, ymax)
        steps = clip.sutherland_hodgman_trace(poly, xmin, ymin, xmax, ymax)
        self.assertGreater(len(steps), 6)

        self.assertEqual(steps[0].render_data.clipping_data.get("focus"), "meet")
        self.assertEqual(steps[1].render_data.clipping_data.get("focus"), "pipeline")

        last = steps[-1]
        self.assertIn("complete", last.title.lower())
        cd = last.render_data.clipping_data
        self.assertEqual(cd.get("focus"), "result")
        got = cd["polygon"]["output"]
        self.assertEqual(_round_poly(got), _round_poly(expected))
        self.assertEqual(last.values.get("status"), "accepted" if len(expected) >= 3 else "rejected")
        self.assertEqual(last.metrics.get("final_vertex_count"), len(expected))

    def test_trace_visits_all_four_boundaries(self):
        poly = clip.get_polygon_shape("diamond")
        steps = clip.sutherland_hodgman_trace(poly, -3.0, -2.0, 3.0, 2.0)
        intro = [s.values.get("edge") for s in steps if s.values.get("stage") == "pass_intro"]
        self.assertEqual(intro, ["LEFT", "RIGHT", "BOTTOM", "TOP"])
        complete = [s.values.get("edge") for s in steps if s.values.get("stage") == "pass_complete"]
        self.assertEqual(complete, ["LEFT", "RIGHT", "BOTTOM", "TOP"])

    def test_trace_edge_steps_use_real_output_lists(self):
        poly = clip.get_polygon_shape("triangle")
        xmin, ymin, xmax, ymax = -3.0, -2.0, 3.0, 2.0
        steps = clip.sutherland_hodgman_trace(poly, xmin, ymin, xmax, ymax)
        edge_steps = [s for s in steps if s.values.get("stage") == "edge"]
        self.assertGreaterEqual(len(edge_steps), 3)
        for s in edge_steps:
            cd = s.render_data.clipping_data
            self.assertIn(cd.get("case"), ("in_in", "in_out", "out_in", "out_out"))
            self.assertIsNotNone(cd.get("edge_s"))
            self.assertIsNotNone(cd.get("edge_p"))
            self.assertEqual(cd.get("s_inside"), s.values.get("s_inside"))
            out = cd["polygon"]["output"]
            before = cd["polygon"]["output_before"]
            emitted = cd.get("emitted") or []
            self.assertEqual(len(out), len(before) + len(emitted))
            if cd["case"] == "out_out":
                self.assertEqual(emitted, [])
                self.assertIsNone(cd.get("intersection"))
            elif cd["case"] == "in_in":
                self.assertEqual(emitted[0]["kind"], "keep")
            else:
                self.assertIsNotNone(cd.get("intersection"))
                self.assertEqual(emitted[0]["kind"], "new")

    def test_outside_shape_rejected(self):
        poly = clip.get_polygon_shape("outside")
        expected = clip.sutherland_hodgman_polygon_clip(poly, -3.0, -2.0, 3.0, 2.0)
        steps = clip.sutherland_hodgman_trace(poly, -3.0, -2.0, 3.0, 2.0)
        self.assertEqual(len(expected), 0)
        self.assertEqual(steps[-1].values.get("status"), "rejected")
        self.assertTrue(steps[-1].metrics.get("rejected"))

    def test_inside_shape_keeps_all_vertices(self):
        poly = clip.get_polygon_shape("inside")
        expected = clip.sutherland_hodgman_polygon_clip(poly, -3.0, -2.0, 3.0, 2.0)
        steps = clip.sutherland_hodgman_trace(poly, -3.0, -2.0, 3.0, 2.0)
        self.assertEqual(len(expected), len(poly))
        self.assertEqual(steps[-1].values.get("status"), "accepted")
        self.assertEqual(_round_poly(steps[-1].render_data.clipping_data["polygon"]["output"]),
                         _round_poly(expected))

    def test_step_state_reversible(self):
        steps = clip.sutherland_hodgman_trace(clip.get_polygon_shape("triangle"), -3.0, -2.0, 3.0, 2.0)
        snapshots = []
        for s in steps:
            cd = s.render_data.clipping_data
            snapshots.append((
                cd.get("focus"),
                cd.get("case"),
                _round_poly(cd["polygon"]["output"]),
                _round_poly(cd["polygon"]["input"]),
            ))
        for idx in range(len(steps) - 1, -1, -1):
            cd = steps[idx].render_data.clipping_data
            current = (
                cd.get("focus"),
                cd.get("case"),
                _round_poly(cd["polygon"]["output"]),
                _round_poly(cd["polygon"]["input"]),
            )
            self.assertEqual(current, snapshots[idx])


if __name__ == "__main__":
    unittest.main()
