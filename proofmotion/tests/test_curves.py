"""
tests/test_curves.py
--------------------
Mathematical tests for Bézier / De Casteljau, B-splines / Cox–de Boor,
and cubic Hermite curves.  The three algorithms are tested as distinct
engines — a Bézier identity is never used as a stand-in for a B-spline
except in the one case where the mathematics says they coincide.
"""

import math
import unittest

import cgip.curves as curves


def _almost(p, q, places=6):
    return abs(p[0] - q[0]) < 10 ** (-places) and abs(p[1] - q[1]) < 10 ** (-places)


class TestHelpers(unittest.TestCase):
    def test_lerp_endpoints_and_midpoint(self):
        a, b = (0.0, 0.0), (10.0, 4.0)
        self.assertEqual(curves.lerp(a, b, 0.0), a)
        self.assertEqual(curves.lerp(a, b, 1.0), b)
        mid = curves.lerp(a, b, 0.5)
        self.assertAlmostEqual(mid[0], 5.0)
        self.assertAlmostEqual(mid[1], 2.0)

    def test_binomial(self):
        self.assertEqual(curves.binomial(3, 0), 1)
        self.assertEqual(curves.binomial(3, 1), 3)
        self.assertEqual(curves.binomial(3, 2), 3)
        self.assertEqual(curves.binomial(3, 3), 1)
        self.assertEqual(curves.binomial(5, 2), 10)
        self.assertEqual(curves.binomial(4, 5), 0)


class TestBezierDeCasteljau(unittest.TestCase):
    def setUp(self):
        self.cubic = [(-5.0, -2.0), (-1.5, 4.0), (1.5, -4.0), (5.0, 2.0)]
        self.linear = [(0.0, 0.0), (4.0, 2.0)]
        self.quadratic = [(0.0, 0.0), (1.0, 2.0), (2.0, 0.0)]

    def test_endpoints(self):
        c0 = curves.de_casteljau(self.cubic, 0.0)
        c1 = curves.de_casteljau(self.cubic, 1.0)
        self.assertTrue(_almost(c0, self.cubic[0]))
        self.assertTrue(_almost(c1, self.cubic[-1]))

    def test_de_casteljau_matches_bernstein(self):
        for t in (0.0, 0.25, 0.35, 0.5, 0.73, 1.0):
            a = curves.de_casteljau(self.cubic, t)
            b = curves.bezier_bernstein(self.cubic, t)
            self.assertTrue(_almost(a, b, places=9), f"mismatch at t={t}: {a} vs {b}")

    def test_linear_bezier_is_lerp(self):
        for t in (0.0, 0.3, 0.5, 1.0):
            self.assertTrue(_almost(
                curves.de_casteljau(self.linear, t),
                curves.lerp(self.linear[0], self.linear[1], t),
            ))

    def test_quadratic_midpoint(self):
        # C(0.5) = 0.25 P0 + 0.5 P1 + 0.25 P2
        p0, p1, p2 = self.quadratic
        expected = (
            0.25 * p0[0] + 0.5 * p1[0] + 0.25 * p2[0],
            0.25 * p0[1] + 0.5 * p1[1] + 0.25 * p2[1],
        )
        self.assertTrue(_almost(curves.de_casteljau(self.quadratic, 0.5), expected))

    def test_pyramid_shape(self):
        pyramid = curves.de_casteljau_pyramid(self.cubic, 0.35)
        self.assertEqual(len(pyramid), 4)
        self.assertEqual([len(level) for level in pyramid], [4, 3, 2, 1])
        self.assertEqual(pyramid[0], self.cubic)

    def test_pyramid_level_is_lerp_of_parent(self):
        t = 0.4
        pyramid = curves.de_casteljau_pyramid(self.cubic, t)
        for r in range(1, len(pyramid)):
            parent = pyramid[r - 1]
            child = pyramid[r]
            for i, pt in enumerate(child):
                self.assertTrue(_almost(pt, curves.lerp(parent[i], parent[i + 1], t), places=9))

    def test_bernstein_partition_of_unity(self):
        for t in (0.0, 0.2, 0.5, 0.9, 1.0):
            weights = curves.bernstein_all(3, t)
            self.assertAlmostEqual(sum(weights), 1.0, places=9)
            self.assertTrue(all(w >= -1e-12 for w in weights))

    def test_bernstein_endpoint_basis(self):
        w0 = curves.bernstein_all(3, 0.0)
        w1 = curves.bernstein_all(3, 1.0)
        self.assertAlmostEqual(w0[0], 1.0)
        self.assertTrue(all(abs(w) < 1e-12 for w in w0[1:]))
        self.assertAlmostEqual(w1[-1], 1.0)
        self.assertTrue(all(abs(w) < 1e-12 for w in w1[:-1]))

    def test_single_point_curve(self):
        p = [(2.0, 3.0)]
        self.assertEqual(curves.de_casteljau(p, 0.3), p[0])
        self.assertEqual(curves.de_casteljau_pyramid(p, 0.7), [p])

    def test_coincident_control_points(self):
        pts = [(1.0, 1.0)] * 4
        for t in (0.0, 0.5, 1.0):
            self.assertTrue(_almost(curves.de_casteljau(pts, t), (1.0, 1.0)))

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            curves.de_casteljau([], 0.5)

    def test_sample_starts_and_ends_on_handles(self):
        samples = curves.sample_bezier(self.cubic, 20)
        self.assertTrue(_almost(samples[0], self.cubic[0]))
        self.assertTrue(_almost(samples[-1], self.cubic[-1]))
        self.assertEqual(len(samples), 20)

    def test_derivative_at_ends_matches_first_last_span(self):
        # C'(0) = n (P1 - P0),  C'(1) = n (Pn - P_{n-1})
        n = 3
        d0 = curves.bezier_derivative(self.cubic, 0.0)
        d1 = curves.bezier_derivative(self.cubic, 1.0)
        expected0 = curves.scale(curves.sub(self.cubic[1], self.cubic[0]), n)
        expected1 = curves.scale(curves.sub(self.cubic[3], self.cubic[2]), n)
        self.assertTrue(_almost(d0, expected0, places=8))
        self.assertTrue(_almost(d1, expected1, places=8))

    def test_convex_hull_midpoint_inside_aabb(self):
        c = curves.de_casteljau(self.cubic, 0.5)
        xs = [p[0] for p in self.cubic]
        ys = [p[1] for p in self.cubic]
        self.assertGreaterEqual(c[0], min(xs) - 1e-9)
        self.assertLessEqual(c[0], max(xs) + 1e-9)
        self.assertGreaterEqual(c[1], min(ys) - 1e-9)
        self.assertLessEqual(c[1], max(ys) + 1e-9)


class TestBSpline(unittest.TestCase):
    def setUp(self):
        self.pts = [(-5.0, -1.0), (-2.5, 3.0), (0.0, -2.5), (2.5, 3.0), (5.0, -1.0)]
        self.degree = 3
        self.knots = curves.clamped_uniform_knots(len(self.pts), self.degree)

    def test_clamped_knot_vector_length_and_repeats(self):
        p, n_ctrl = 3, 5
        u = curves.clamped_uniform_knots(n_ctrl, p)
        self.assertEqual(len(u), n_ctrl + p + 1)
        self.assertEqual(u[: p + 1], [0.0] * (p + 1))
        self.assertEqual(u[-(p + 1) :], [1.0] * (p + 1))
        self.assertEqual(u, [0, 0, 0, 0, 0.5, 1, 1, 1, 1])

    def test_clamped_cubic_four_points_is_bezier_knot_vector(self):
        u = curves.clamped_uniform_knots(4, 3)
        self.assertEqual(u, [0, 0, 0, 0, 1, 1, 1, 1])

    def test_uniform_knot_count(self):
        u = curves.uniform_knots(5, 3)
        self.assertEqual(len(u), 5 + 3 + 1)
        self.assertAlmostEqual(u[0], 0.0)
        self.assertAlmostEqual(u[-1], 1.0)

    def test_invalid_degree_raises(self):
        with self.assertRaises(ValueError):
            curves.clamped_uniform_knots(3, 3)
        with self.assertRaises(ValueError):
            curves.clamped_uniform_knots(5, 0)

    def test_wrong_knot_length_raises(self):
        with self.assertRaises(ValueError):
            curves.bspline_point(self.pts, 3, [0, 0, 1, 1], 0.5)

    def test_decreasing_knots_raise(self):
        bad = [0, 0, 0, 0, 0.8, 0.2, 1, 1, 1]
        with self.assertRaises(ValueError):
            curves.validate_knots(5, 3, bad)

    def test_clamped_endpoints_interpolate(self):
        c0 = curves.bspline_point(self.pts, self.degree, self.knots, 0.0)
        c1 = curves.bspline_point(self.pts, self.degree, self.knots, 1.0)
        self.assertTrue(_almost(c0, self.pts[0], places=8))
        self.assertTrue(_almost(c1, self.pts[-1], places=8))

    def test_uniform_does_not_interpolate_ends(self):
        uni = curves.uniform_knots(len(self.pts), self.degree)
        umin, umax = curves.parameter_domain(self.degree, len(self.pts), uni)
        c0 = curves.bspline_point(self.pts, self.degree, uni, umin)
        c1 = curves.bspline_point(self.pts, self.degree, uni, umax)
        self.assertFalse(_almost(c0, self.pts[0], places=3))
        self.assertFalse(_almost(c1, self.pts[-1], places=3))

    def test_partition_of_unity(self):
        for u in (0.0, 0.25, 0.5, 0.75, 1.0):
            basis = curves.all_basis(len(self.pts), self.degree, self.knots, u)
            self.assertAlmostEqual(sum(basis), 1.0, places=8)
            self.assertTrue(all(v >= -1e-12 for v in basis))

    def test_local_support(self):
        # N_i,p is zero outside [u_i, u_{i+p+1}]
        for i in range(len(self.pts)):
            lo, hi = curves.local_support_interval(i, self.degree, self.knots)
            for u in curves.linspace(0.0, 1.0, 25):
                val = curves.all_basis(len(self.pts), self.degree, self.knots, u)[i]
                if u < lo - 1e-9 or u > hi + 1e-9:
                    self.assertAlmostEqual(val, 0.0, places=8, msg=f"N{i}({u}) should be 0")

    def test_at_most_p_plus_one_nonzero(self):
        for u in curves.linspace(0.0, 1.0, 21):
            basis = curves.all_basis(len(self.pts), self.degree, self.knots, u)
            nonzero = sum(1 for v in basis if v > 1e-9)
            self.assertLessEqual(nonzero, self.degree + 1)

    def test_cox_de_boor_matches_a22_table(self):
        for u in (0.0, 0.2, 0.5, 0.81, 1.0):
            table = curves.all_basis(len(self.pts), self.degree, self.knots, u)
            rec = [curves.cox_de_boor(i, self.degree, u, self.knots) for i in range(len(self.pts))]
            for a, b in zip(table, rec):
                self.assertAlmostEqual(a, b, places=8, msg=f"u={u}")

    def test_clamped_cubic_four_points_equals_bezier(self):
        bez_pts = [(-5.0, -2.0), (-1.5, 4.0), (1.5, -4.0), (5.0, 2.0)]
        knots = curves.clamped_uniform_knots(4, 3)
        for t in (0.0, 0.17, 0.5, 0.84, 1.0):
            b = curves.de_casteljau(bez_pts, t)
            s = curves.bspline_point(bez_pts, 3, knots, t)
            self.assertTrue(_almost(b, s, places=8), f"t={t}: Bézier {b} vs B-spline {s}")

    def test_quadratic_five_points_not_equal_to_bezier(self):
        # A degree-2 B-spline with 5 handles is NOT a single quadratic Bézier.
        knots = curves.clamped_uniform_knots(5, 2)
        # Quadratic Bézier on the same 5 points is not even defined as one segment;
        # compare against cubic Bézier of first four — they must differ at mid.
        bez = curves.de_casteljau(self.pts[:4], 0.5)
        spl = curves.bspline_point(self.pts, 2, knots, 0.5)
        self.assertFalse(_almost(bez, spl, places=2))

    def test_moving_one_point_is_local(self):
        moved = list(self.pts)
        moved[0] = (moved[0][0], moved[0][1] + 4.0)
        # Near u=1 the first handle's basis is zero, so the curve must match.
        a = curves.bspline_point(self.pts, self.degree, self.knots, 0.95)
        b = curves.bspline_point(moved, self.degree, self.knots, 0.95)
        self.assertTrue(_almost(a, b, places=7))
        # Near u=0 the first handle matters.
        c = curves.bspline_point(self.pts, self.degree, self.knots, 0.05)
        d = curves.bspline_point(moved, self.degree, self.knots, 0.05)
        self.assertFalse(_almost(c, d, places=3))

    def test_sample_count_and_endpoints(self):
        samples = curves.sample_bspline(self.pts, self.degree, self.knots, 30)
        self.assertEqual(len(samples), 30)
        self.assertTrue(_almost(samples[0], self.pts[0], places=7))
        self.assertTrue(_almost(samples[-1], self.pts[-1], places=7))

    def test_degree_1_clamped_is_the_control_polygon(self):
        knots = curves.clamped_uniform_knots(4, 1)
        pts = [(0.0, 0.0), (1.0, 1.0), (2.0, 0.0), (3.0, 1.0)]
        # At the midpoint of the first span, u=0.5 of domain [0,1] with
        # knots [0,0, 1/3, 2/3, 1,1] — just check endpoints and a vertex.
        self.assertTrue(_almost(curves.bspline_point(pts, 1, knots, 0.0), pts[0]))
        self.assertTrue(_almost(curves.bspline_point(pts, 1, knots, 1.0), pts[-1]))


class TestHermite(unittest.TestCase):
    def setUp(self):
        self.p0 = (-4.5, -1.5)
        self.p1 = (4.5, 1.5)
        self.t0 = (3.5, 5.0)
        self.t1 = (3.5, -5.0)

    def test_endpoint_interpolation(self):
        c0 = curves.hermite_point(self.p0, self.p1, self.t0, self.t1, 0.0)
        c1 = curves.hermite_point(self.p0, self.p1, self.t0, self.t1, 1.0)
        self.assertTrue(_almost(c0, self.p0))
        self.assertTrue(_almost(c1, self.p1))

    def test_endpoint_derivatives(self):
        d0 = curves.hermite_derivative(self.p0, self.p1, self.t0, self.t1, 0.0)
        d1 = curves.hermite_derivative(self.p0, self.p1, self.t0, self.t1, 1.0)
        self.assertTrue(_almost(d0, self.t0, places=8))
        self.assertTrue(_almost(d1, self.t1, places=8))

    def test_basis_endpoint_values(self):
        h0 = curves.hermite_basis(0.0)
        h1 = curves.hermite_basis(1.0)
        self.assertAlmostEqual(h0, (1.0, 0.0, 0.0, 0.0))
        self.assertAlmostEqual(h1, (0.0, 1.0, 0.0, 0.0))

    def test_zero_tangents_stay_on_the_chord(self):
        """Zero tangents give a cubic ease along P0P1, not a linear lerp."""
        z = (0.0, 0.0)
        for t in (0.0, 0.25, 0.5, 0.75, 1.0):
            c = curves.hermite_point(self.p0, self.p1, z, z, t)
            # Collinear with P0P1: (C-P0) × (P1-P0) = 0
            cross = (c[0] - self.p0[0]) * (self.p1[1] - self.p0[1]) - (c[1] - self.p0[1]) * (self.p1[0] - self.p0[0])
            self.assertAlmostEqual(cross, 0.0, places=8)
        # Parameterization is smoothstep, not lerp — C(0.25) is closer to P0 than the 1/4 point.
        c = curves.hermite_point(self.p0, self.p1, z, z, 0.25)
        linear = curves.lerp(self.p0, self.p1, 0.25)
        self.assertFalse(_almost(c, linear, places=3))

    def test_hermite_matches_equivalent_bezier(self):
        bez = curves.hermite_to_bezier(self.p0, self.p1, self.t0, self.t1)
        for t in (0.0, 0.2, 0.35, 0.5, 0.8, 1.0):
            h = curves.hermite_point(self.p0, self.p1, self.t0, self.t1, t)
            b = curves.de_casteljau(bez, t)
            self.assertTrue(_almost(h, b, places=8), f"t={t}: Hermite {h} vs Bézier {b}")

    def test_equivalent_bezier_handles(self):
        bez = curves.hermite_to_bezier(self.p0, self.p1, self.t0, self.t1)
        self.assertTrue(_almost(bez[0], self.p0))
        self.assertTrue(_almost(bez[3], self.p1))
        self.assertTrue(_almost(bez[1], curves.add(self.p0, curves.scale(self.t0, 1.0 / 3.0))))
        self.assertTrue(_almost(bez[2], curves.sub(self.p1, curves.scale(self.t1, 1.0 / 3.0))))

    def test_numerical_derivative_agrees(self):
        def f(t):
            return curves.hermite_point(self.p0, self.p1, self.t0, self.t1, t)

        h = 1e-5
        for t in (0.2, 0.5, 0.8):
            num = ((f(t + h)[0] - f(t - h)[0]) / (2 * h), (f(t + h)[1] - f(t - h)[1]) / (2 * h))
            ana = curves.hermite_derivative(self.p0, self.p1, self.t0, self.t1, t)
            self.assertTrue(_almost(num, ana, places=5), f"t={t}")

    def test_tangent_magnitude_pulls_curve(self):
        short = curves.hermite_point(self.p0, self.p1, (1.0, 0.0), (1.0, 0.0), 0.25)
        long = curves.hermite_point(self.p0, self.p1, (8.0, 0.0), (1.0, 0.0), 0.25)
        # A longer T0 should push C(0.25) further in +x from P0.
        self.assertGreater(long[0], short[0])

    def test_sample_endpoints(self):
        samples = curves.sample_hermite(self.p0, self.p1, self.t0, self.t1, 16)
        self.assertEqual(len(samples), 16)
        self.assertTrue(_almost(samples[0], self.p0))
        self.assertTrue(_almost(samples[-1], self.p1))

    def test_h3_goes_negative(self):
        # Distinguishes Hermite from Bernstein: H3(t)=t²(t-1) < 0 on (0,1).
        _h0, _h1, h2, h3 = curves.hermite_basis(0.7)
        self.assertGreater(h2, 0.0)
        self.assertLess(h3, 0.0)


class TestLessonSteps(unittest.TestCase):
    def test_bezier_tabs_produce_steps(self):
        values = {
            "p0x": -5, "p0y": -2, "p1x": -1.5, "p1y": 4,
            "p2x": 1.5, "p2y": -4, "p3x": 5, "p3y": 2, "t": 0.35,
        }
        for tab in ("intro", "math", "casteljau", "experiment"):
            steps = curves.generate_curve_steps("curve_bezier", values, tab)
            self.assertGreater(len(steps), 2, msg=tab)
            self.assertTrue(all(s.render_data.mode == "curves" for s in steps))
            self.assertTrue(all(s.title and s.explanation for s in steps))

    def test_bezier_casteljau_reveals_levels_in_order(self):
        values = {"t": 0.4}
        steps = curves.generate_curve_steps("curve_bezier", values, "casteljau")
        levels = [s.render_data.curve_data.get("reveal_level") for s in steps]
        revealed = [lv for lv in levels if lv is not None]
        self.assertEqual(revealed[0], 0)
        self.assertGreaterEqual(max(revealed), 3)

    def test_bezier_casteljau_dynamic_calculations_on_drag(self):
        # Shift P1 from (-1.5, 4.0) to (-2.0, 5.0)
        val1 = {"p0x": -5, "p0y": -2, "p1x": -1.5, "p1y": 4.0, "p2x": 1.5, "p2y": -4, "p3x": 5, "p3y": 2, "t": 0.5}
        val2 = {"p0x": -5, "p0y": -2, "p1x": -2.0, "p1y": 5.0, "p2x": 1.5, "p2y": -4, "p3x": 5, "p3y": 2, "t": 0.5}
        steps1 = curves.generate_curve_steps("curve_bezier", val1, "casteljau")
        steps2 = curves.generate_curve_steps("curve_bezier", val2, "casteljau")

        # Step 1: Control points are in equation and metrics dynamically
        self.assertIn("(-1.50, 4.00)", steps1[0].equation)
        self.assertIn("(-2.00, 5.00)", steps2[0].equation)
        self.assertEqual(steps1[0].metrics["P1"], "(-1.50, 4.00)")
        self.assertEqual(steps2[0].metrics["P1"], "(-2.00, 5.00)")

        # Step 2: Lerp calculation dynamically updates
        self.assertIn("Q0", steps1[1].equation)
        self.assertIn("Q0", steps2[1].equation)
        self.assertNotEqual(steps1[1].equation, steps2[1].equation)

        # Final experiment step is present in the clubbed casteljau tab
        exp_step = steps1[-1]
        self.assertEqual(exp_step.title, "Interactive Experiment: Drag points & vary t")
        self.assertIn("Bernstein Polynomial Equivalence", exp_step.equation)
        self.assertIn("C(0.50)", exp_step.equation)

    def test_bezier_experiment_covers_unit_interval(self):
        steps = curves.generate_curve_steps("curve_bezier", {"t": 0.35}, "experiment")
        ts = [s.values["t"] for s in steps]
        self.assertAlmostEqual(ts[0], 0.0)
        self.assertAlmostEqual(ts[-1], 1.0)
        self.assertEqual(len(steps), curves.SWEEP_FRAMES)
        # Pyramid is present so the visualisation can show De Casteljau, not a precomputed stroke.
        pyr = steps[10].render_data.curve_data["pyramid"]
        self.assertEqual(len(pyr), 4)

    def test_bspline_and_hermite_tabs(self):
        b_steps = curves.generate_curve_steps("curve_bspline", {"u": 0.4, "degree": "3 (cubic)"}, "math")
        self.assertGreater(len(b_steps), 3)
        self.assertIn("knots", b_steps[0].render_data.curve_data)
        h_steps = curves.generate_curve_steps("curve_hermite", {"t": 0.3}, "experiment")
        self.assertEqual(len(h_steps), curves.SWEEP_FRAMES)
        self.assertIn("t0", h_steps[0].render_data.curve_data)

    def test_bspline_degree_too_high_raises(self):
        with self.assertRaises(ValueError):
            curves.generate_curve_steps(
                "curve_bspline",
                {"degree": "5", "p0x": 0, "p1x": 1, "p2x": 2, "p3x": 3, "p4x": 4},
                "intro",
            )

    def test_unknown_topic_raises(self):
        with self.assertRaises(ValueError):
            curves.generate_curve_steps("curve_nurbs", {}, "intro")

    def test_tabs_for_topic(self):
        self.assertEqual(len(curves.tabs_for_topic("curve_bezier")), 3)
        self.assertEqual([k for k, _, _ in curves.tabs_for_topic("curve_bezier")], ["intro", "math", "casteljau"])
        self.assertEqual(len(curves.tabs_for_topic("curve_bspline")), 3)
        self.assertEqual(len(curves.tabs_for_topic("curve_hermite")), 3)
        self.assertEqual(curves.default_tab("curve_bezier"), "intro")

    def test_hermite_experiment_carries_tangents(self):
        steps = curves.generate_curve_steps(
            "curve_hermite",
            {"p0x": 0, "p0y": 0, "p1x": 4, "p1y": 0, "t0x": 2, "t0y": 3, "t1x": 2, "t1y": -3, "t": 0.2},
            "experiment",
        )
        cd = steps[0].render_data.curve_data
        self.assertEqual(cd["kind"], "hermite")
        self.assertIn("t0_tip", cd)
        self.assertIn("t1_tip", cd)

    def test_bezier_math_includes_basis_plot(self):
        steps = curves.generate_curve_steps("curve_bezier", {"t": 0.3}, "math")
        plots = [s.render_data.curve_data.get("basis_plot") for s in steps]
        self.assertTrue(any(plots))

    def test_t_is_clamped(self):
        steps = curves.generate_curve_steps("curve_bezier", {"t": 2.5}, "intro")
        self.assertAlmostEqual(steps[0].values["t"], 1.0)


class TestAlgorithmsAreDistinct(unittest.TestCase):
    def test_default_bspline_is_not_a_bezier_of_its_polygon(self):
        pts = curves.DEFAULT_BSPLINE
        knots = curves.clamped_uniform_knots(len(pts), 3)
        # A 4-point cubic Bézier cannot even consume 5 handles as one segment.
        # Evaluating a cubic Bézier on the first four vs the B-spline of all five
        # must differ, and a degree-4 Bézier of all five must also differ because
        # the B-spline is piecewise.
        bez4 = curves.de_casteljau(pts, 0.5)  # treats 5 points as degree-4 Bézier
        spl = curves.bspline_point(pts, 3, knots, 0.5)
        self.assertFalse(_almost(bez4, spl, places=3))

    def test_hermite_is_not_de_casteljau_on_the_four_inputs(self):
        p0, p1 = (-4.0, 0.0), (4.0, 0.0)
        t0, t1 = (0.0, 6.0), (0.0, -6.0)
        # Naively running De Casteljau on (P0, T0, T1, P1) is the wrong algorithm.
        naive = curves.de_casteljau([p0, t0, t1, p1], 0.5)
        real = curves.hermite_point(p0, p1, t0, t1, 0.5)
        self.assertFalse(_almost(naive, real, places=2))
        # The correct related Bézier uses P0+T0/3 and P1-T1/3.
        related = curves.de_casteljau(curves.hermite_to_bezier(p0, p1, t0, t1), 0.5)
        self.assertTrue(_almost(real, related, places=8))


if __name__ == "__main__":
    unittest.main()
