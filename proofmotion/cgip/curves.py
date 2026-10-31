"""
cgip/curves.py
--------------
Parametric curve engines for the Curves & Geometric Modelling lessons.

Three distinct algorithms live here — they are not interchangeable:

  1. Bézier / De Casteljau
     A polynomial blend of every control point.  C(t) is obtained by
     repeated linear interpolation (De Casteljau) which is equivalent
     to the Bernstein basis.  Moving any handle affects the whole curve.

  2. B-spline / Cox–de Boor
     A piecewise polynomial whose basis functions have local support
     controlled by a knot vector and a degree.  Moving a control point
     changes only a neighbourhood of the curve.

  3. Cubic Hermite
     Interpolates two endpoints and two tangent vectors using the four
     Hermite blending functions.  Tangent direction and magnitude are
     first-class inputs, unlike Bézier's off-curve handles.

Pure math lives in this module.  The UI never reimplements interpolation.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

from core.step_model import RenderData, VisualizationStep

Point = Tuple[float, float]
EPSILON = 1e-12

BEZIER_TABS = [
    ("stage1", "1  What is Bézier?", "Control points & shapes"),
    ("stage2", "2  Linear Interpolation", "Lerp: P(t) = (1-t)A + tB"),
    ("stage3", "3  De Casteljau Levels", "Level 1 → Level 2 → Level 3"),
    ("stage4", "4  Interactive Studio", "Drag points & sweep t"),
    ("stage5", "5  Knowledge Quiz", "Test your understanding"),
]

BSPLINE_TABS = [
    ("intro", "1  The Idea", "Local control vs Bézier"),
    ("math", "2  Knots & Basis", "Cox–de Boor recursion"),
    ("experiment", "3  Experiment", "Degree, knots, points"),
]

HERMITE_TABS = [
    ("intro", "1  The Idea", "Positions and tangents"),
    ("math", "2  The Math", "Cubic Hermite basis"),
    ("experiment", "3  Experiment", "Pull on the handles"),
]

LEVEL_COLORS = ["#64748B", "#0D9488", "#D97706", "#6C5CE7", "#DB2777"]
CTRL_COLOR = "#334155"
CURVE_COLOR = "#6C5CE7"
TRACE_COLOR = "#4C1D95"
POINT_COLORS = ["#6C5CE7", "#0D9488", "#D97706", "#DB2777", "#2563EB", "#CA8A04"]

DEFAULT_BEZIER: List[Point] = [(-5.0, -2.0), (-1.5, 4.0), (1.5, -4.0), (5.0, 2.0)]
DEFAULT_LERP_A: Point = (-4.0, -1.0)
DEFAULT_LERP_B: Point = (4.0, 2.0)
DEFAULT_BSPLINE: List[Point] = [(-5.0, -1.0), (-2.5, 3.0), (0.0, -2.5), (2.5, 3.0), (5.0, -1.0)]
DEFAULT_HERMITE_P0: Point = (-4.5, -1.5)
DEFAULT_HERMITE_P1: Point = (4.5, 1.5)
DEFAULT_HERMITE_T0: Point = (3.5, 5.0)
DEFAULT_HERMITE_T1: Point = (3.5, -5.0)

SAMPLE_COUNT = 96
SWEEP_FRAMES = 21


# ---------------------------------------------------------------------------
# Vector helpers
# ---------------------------------------------------------------------------

def _pt(x: float, y: float) -> Point:
    return (float(x), float(y))


def add(a: Point, b: Point) -> Point:
    return (a[0] + b[0], a[1] + b[1])


def sub(a: Point, b: Point) -> Point:
    return (a[0] - b[0], a[1] - b[1])


def scale(a: Point, s: float) -> Point:
    return (a[0] * s, a[1] * s)


def lerp(a: Point, b: Point, t: float) -> Point:
    """Linear interpolation: (1-t)·A + t·B.  Defined for any real t."""
    return ((1.0 - t) * a[0] + t * b[0], (1.0 - t) * a[1] + t * b[1])


def dist(a: Point, b: Point) -> float:
    dx, dy = a[0] - b[0], a[1] - b[1]
    return (dx * dx + dy * dy) ** 0.5


def clamp(value: float, lo: float, hi: float) -> float:
    return lo if value < lo else hi if value > hi else value


def linspace(a: float, b: float, n: int) -> List[float]:
    if n <= 1:
        return [float(a)]
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def _fmt(p: Point, digits: int = 2) -> str:
    return f"({p[0]:.{digits}f}, {p[1]:.{digits}f})"


def binomial(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result


# ===========================================================================
# Bézier — Bernstein form and De Casteljau
# ===========================================================================

def bernstein(n: int, i: int, t: float) -> float:
    """Bernstein basis polynomial B_i^n(t) = C(n,i) t^i (1-t)^{n-i}.

    Convention: 0^0 = 1, so the endpoints evaluate correctly.
    """
    if i < 0 or i > n:
        return 0.0
    t = float(t)
    one_minus = 1.0 - t
    # pow(0, 0) is 1.0 in IEEE / Python, which is the needed convention.
    return binomial(n, i) * (t ** i) * (one_minus ** (n - i))


def bernstein_all(n: int, t: float) -> List[float]:
    return [bernstein(n, i, t) for i in range(n + 1)]


def bezier_bernstein(points: Sequence[Point], t: float) -> Point:
    """Evaluate a degree-(n) Bézier curve via the Bernstein basis."""
    if not points:
        raise ValueError("Bézier curve needs at least one control point.")
    n = len(points) - 1
    x = y = 0.0
    for i, p in enumerate(points):
        w = bernstein(n, i, t)
        x += w * p[0]
        y += w * p[1]
    return (x, y)


def de_casteljau_pyramid(points: Sequence[Point], t: float) -> List[List[Point]]:
    """Return every interpolation level of De Casteljau's algorithm.

    Level 0 is the control polygon.  Level r has n-r points, each the
    linear interpolation at parameter t of two neighbours on level r-1.
    The single point on the last level is C(t).

    Recurrence:
        P_i^{(0)}     = P_i
        P_i^{(r)}(t)  = (1-t) P_i^{(r-1)}(t) + t P_{i+1}^{(r-1)}(t)
        C(t)          = P_0^{(n)}(t)
    """
    if not points:
        raise ValueError("De Casteljau needs at least one control point.")
    levels: List[List[Point]] = [list(points)]
    current = list(points)
    while len(current) > 1:
        nxt = [lerp(current[i], current[i + 1], t) for i in range(len(current) - 1)]
        levels.append(nxt)
        current = nxt
    return levels


def de_casteljau(points: Sequence[Point], t: float) -> Point:
    """Evaluate C(t) by De Casteljau; equivalent to the Bernstein form."""
    return de_casteljau_pyramid(points, t)[-1][0]


def sample_bezier(points: Sequence[Point], count: int = SAMPLE_COUNT) -> List[Point]:
    return [de_casteljau(points, t) for t in linspace(0.0, 1.0, count)]


def bezier_derivative(points: Sequence[Point], t: float) -> Point:
    """C'(t) = n Σ B_i^{n-1}(t) (P_{i+1} - P_i)."""
    n = len(points) - 1
    if n <= 0:
        return (0.0, 0.0)
    diffs = [scale(sub(points[i + 1], points[i]), float(n)) for i in range(n)]
    return bezier_bernstein(diffs, t)


# ===========================================================================
# B-spline — knot vectors, Cox–de Boor, de Boor evaluation
# ===========================================================================

def clamped_uniform_knots(n_ctrl: int, degree: int) -> List[float]:
    """Open-uniform (clamped) knot vector in [0, 1].

    p+1 zeros, then (n-p) interior knots, then p+1 ones.
    Number of knots = n + p + 2, where n = n_ctrl - 1.
    Clamping makes C(u_min) = P_0 and C(u_max) = P_n.
    """
    if n_ctrl < 2:
        raise ValueError("A B-spline needs at least two control points.")
    if degree < 1:
        raise ValueError("B-spline degree must be at least 1.")
    if degree >= n_ctrl:
        raise ValueError(
            f"Degree {degree} requires at least {degree + 1} control points, got {n_ctrl}."
        )
    n = n_ctrl - 1
    p = degree
    interior = n - p
    knots = [0.0] * (p + 1)
    for j in range(1, interior + 1):
        knots.append(j / (interior + 1))
    knots.extend([1.0] * (p + 1))
    return knots


def uniform_knots(n_ctrl: int, degree: int) -> List[float]:
    """Periodic-style uniform knots equally spaced in [0, 1].

    Endpoints are not interpolated.  The valid parameter domain is
    [u_p, u_{n+1}].
    """
    if n_ctrl < 2:
        raise ValueError("A B-spline needs at least two control points.")
    if degree < 1:
        raise ValueError("B-spline degree must be at least 1.")
    if degree >= n_ctrl:
        raise ValueError(
            f"Degree {degree} requires at least {degree + 1} control points, got {n_ctrl}."
        )
    count = n_ctrl + degree + 1
    return [i / (count - 1) for i in range(count)]


def make_knot_vector(n_ctrl: int, degree: int, style: str = "Clamped uniform") -> List[float]:
    style_l = str(style).strip().lower()
    if style_l.startswith("uniform") and "clamp" not in style_l:
        return uniform_knots(n_ctrl, degree)
    return clamped_uniform_knots(n_ctrl, degree)


def validate_knots(n_ctrl: int, degree: int, knots: Sequence[float]) -> None:
    expected = n_ctrl + degree + 1
    if len(knots) != expected:
        raise ValueError(
            f"Knot vector length must be n+p+2 = {expected} "
            f"(n_ctrl={n_ctrl}, degree={degree}), got {len(knots)}."
        )
    for a, b in zip(knots, knots[1:]):
        if b + EPSILON < a:
            raise ValueError("Knot vector must be non-decreasing.")


def find_span(n: int, p: int, u: float, knots: Sequence[float]) -> int:
    """Piegl/Tiller A2.1: knot span index of u.  n = n_ctrl - 1."""
    if u >= knots[n + 1] - EPSILON:
        return n
    if u <= knots[p] + EPSILON:
        return p
    low, high = p, n + 1
    mid = (low + high) // 2
    while u < knots[mid] or u >= knots[mid + 1]:
        if u < knots[mid]:
            high = mid
        else:
            low = mid
        mid = (low + high) // 2
    return mid


def basis_funs(span: int, u: float, p: int, knots: Sequence[float]) -> List[float]:
    """Piegl/Tiller A2.2: the p+1 non-zero basis functions at `span`."""
    nvals = [0.0] * (p + 1)
    left = [0.0] * (p + 1)
    right = [0.0] * (p + 1)
    nvals[0] = 1.0
    for j in range(1, p + 1):
        left[j] = u - knots[span + 1 - j]
        right[j] = knots[span + j] - u
        saved = 0.0
        for r in range(j):
            denom = right[r + 1] + left[j - r]
            temp = 0.0 if abs(denom) < EPSILON else nvals[r] / denom
            nvals[r] = saved + right[r + 1] * temp
            saved = left[j - r] * temp
        nvals[j] = saved
    return nvals


def cox_de_boor(i: int, p: int, u: float, knots: Sequence[float]) -> float:
    """Scalar Cox–de Boor recurrence for a single basis function N_{i,p}(u).

    N_{i,0}(u) = 1  if u_i ≤ u < u_{i+1}  (last span closed on the right)
    N_{i,p}(u) = ω_{i,p} N_{i,p-1}(u) + (1 - ω_{i+1,p}) N_{i+1,p-1}(u)
    ω_{i,p}    = (u - u_i) / (u_{i+p} - u_i)   (0 if the denominator is 0)
    """
    if p == 0:
        left, right = knots[i], knots[i + 1]
        if right <= left + EPSILON:
            return 0.0
        last_knot = knots[-1]
        if abs(u - last_knot) <= EPSILON and abs(right - last_knot) <= EPSILON:
            return 1.0
        return 1.0 if (left <= u < right) else 0.0
    denom1 = knots[i + p] - knots[i]
    denom2 = knots[i + p + 1] - knots[i + 1]
    c1 = 0.0 if abs(denom1) < EPSILON else (u - knots[i]) / denom1 * cox_de_boor(i, p - 1, u, knots)
    c2 = 0.0 if abs(denom2) < EPSILON else (knots[i + p + 1] - u) / denom2 * cox_de_boor(i + 1, p - 1, u, knots)
    return c1 + c2


def all_basis(n_ctrl: int, degree: int, knots: Sequence[float], u: float) -> List[float]:
    """Every N_{i,p}(u), i = 0 .. n.  Most are zero (local support)."""
    n = n_ctrl - 1
    p = degree
    umin, umax = knots[p], knots[n + 1]
    u = clamp(float(u), umin, umax)
    values = [0.0] * n_ctrl
    span = find_span(n, p, u, knots)
    nvals = basis_funs(span, u, p, knots)
    for j in range(p + 1):
        idx = span - p + j
        if 0 <= idx < n_ctrl:
            values[idx] = nvals[j]
    return values


def bspline_point(points: Sequence[Point], degree: int, knots: Sequence[float], u: float) -> Point:
    """Evaluate C(u) = Σ N_{i,p}(u) P_i using the de Boor / A3.1 table."""
    n_ctrl = len(points)
    validate_knots(n_ctrl, degree, knots)
    n = n_ctrl - 1
    p = degree
    u = clamp(float(u), knots[p], knots[n + 1])
    span = find_span(n, p, u, knots)
    nvals = basis_funs(span, u, p, knots)
    x = y = 0.0
    for j in range(p + 1):
        px, py = points[span - p + j]
        x += nvals[j] * px
        y += nvals[j] * py
    return (x, y)


def parameter_domain(degree: int, n_ctrl: int, knots: Sequence[float]) -> Tuple[float, float]:
    n = n_ctrl - 1
    return float(knots[degree]), float(knots[n + 1])


def sample_bspline(
    points: Sequence[Point],
    degree: int,
    knots: Sequence[float],
    count: int = SAMPLE_COUNT,
) -> List[Point]:
    umin, umax = parameter_domain(degree, len(points), knots)
    return [bspline_point(points, degree, knots, u) for u in linspace(umin, umax, count)]


def basis_samples(
    n_ctrl: int, degree: int, knots: Sequence[float], count: int = 80
) -> Tuple[List[float], List[List[float]]]:
    umin, umax = parameter_domain(degree, n_ctrl, knots)
    xs = linspace(umin, umax, count)
    series = [[] for _ in range(n_ctrl)]
    for u in xs:
        vals = all_basis(n_ctrl, degree, knots, u)
        for i, v in enumerate(vals):
            series[i].append(v)
    return xs, series


def local_support_interval(i: int, degree: int, knots: Sequence[float]) -> Tuple[float, float]:
    """N_{i,p} is identically zero outside [u_i, u_{i+p+1}]."""
    return float(knots[i]), float(knots[i + degree + 1])


# ===========================================================================
# Cubic Hermite
# ===========================================================================

def hermite_basis(t: float) -> Tuple[float, float, float, float]:
    """Cubic Hermite blending functions on t ∈ [0, 1].

        H0(t) =  2t³ − 3t² + 1     blends P0  (H0(0)=1, H0(1)=0)
        H1(t) = −2t³ + 3t²         blends P1  (H1(0)=0, H1(1)=1)
        H2(t) =   t³ − 2t² + t     blends T0  (H2'(0)=1, H2'(1)=0)
        H3(t) =   t³ −  t²         blends T1  (H3'(0)=0, H3'(1)=1)
    """
    t2 = t * t
    t3 = t2 * t
    h0 = 2.0 * t3 - 3.0 * t2 + 1.0
    h1 = -2.0 * t3 + 3.0 * t2
    h2 = t3 - 2.0 * t2 + t
    h3 = t3 - t2
    return h0, h1, h2, h3


def hermite_basis_derivative(t: float) -> Tuple[float, float, float, float]:
    t2 = t * t
    d0 = 6.0 * t2 - 6.0 * t
    d1 = -6.0 * t2 + 6.0 * t
    d2 = 3.0 * t2 - 4.0 * t + 1.0
    d3 = 3.0 * t2 - 2.0 * t
    return d0, d1, d2, d3


def hermite_point(p0: Point, p1: Point, t0: Point, t1: Point, t: float) -> Point:
    """C(t) = H0(t) P0 + H1(t) P1 + H2(t) T0 + H3(t) T1."""
    h0, h1, h2, h3 = hermite_basis(t)
    return (
        h0 * p0[0] + h1 * p1[0] + h2 * t0[0] + h3 * t1[0],
        h0 * p0[1] + h1 * p1[1] + h2 * t0[1] + h3 * t1[1],
    )


def hermite_derivative(p0: Point, p1: Point, t0: Point, t1: Point, t: float) -> Point:
    d0, d1, d2, d3 = hermite_basis_derivative(t)
    return (
        d0 * p0[0] + d1 * p1[0] + d2 * t0[0] + d3 * t1[0],
        d0 * p0[1] + d1 * p1[1] + d2 * t0[1] + d3 * t1[1],
    )


def sample_hermite(p0: Point, p1: Point, t0: Point, t1: Point, count: int = SAMPLE_COUNT) -> List[Point]:
    return [hermite_point(p0, p1, t0, t1, t) for t in linspace(0.0, 1.0, count)]


def hermite_to_bezier(p0: Point, p1: Point, t0: Point, t1: Point) -> List[Point]:
    """Cubic Hermite is the cubic Bézier with handles P0 + T0/3 and P1 − T1/3."""
    return [p0, add(p0, scale(t0, 1.0 / 3.0)), sub(p1, scale(t1, 1.0 / 3.0)), p1]


# ===========================================================================
# Parameter parsing
# ===========================================================================

def control_points_from_values(values: Dict, count: int, defaults: Sequence[Point]) -> List[Point]:
    pts: List[Point] = []
    for i in range(count):
        dx, dy = defaults[i] if i < len(defaults) else (0.0, 0.0)
        x = float(values.get(f"p{i}x", dx))
        y = float(values.get(f"p{i}y", dy))
        pts.append((x, y))
    return pts


def parse_degree(raw) -> int:
    digits = []
    for ch in str(raw).strip():
        if ch.isdigit():
            digits.append(ch)
        elif digits:
            break
    if not digits:
        return 3
    return int("".join(digits))


def parse_knot_style(raw) -> str:
    text = str(raw).strip()
    if text.lower().startswith("uniform") and "clamp" not in text.lower():
        return "Uniform"
    return "Clamped uniform"


def _param_t(values: Dict, key: str = "t", default: float = 0.35) -> float:
    try:
        return clamp(float(values.get(key, default)), 0.0, 1.0)
    except (TypeError, ValueError):
        return default


# ===========================================================================
# Render-data builders
# ===========================================================================

def _bounds_from_points(points: Sequence[Point], pad: float = 1.6) -> Tuple[float, float, float, float]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    if xmax - xmin < 8.0:
        mid = 0.5 * (xmin + xmax)
        xmin, xmax = mid - 4.0, mid + 4.0
    if ymax - ymin < 6.0:
        mid = 0.5 * (ymin + ymax)
        ymin, ymax = mid - 3.0, mid + 3.0
    return (xmin - pad, ymin - pad, xmax + pad, ymax + pad)


def _basis_plot(
    title: str,
    xs: Sequence[float],
    series: Sequence[Sequence[float]],
    marker: float,
    labels: Sequence[str],
    highlight: Optional[int] = None,
) -> Dict:
    return {
        "title": title,
        "xs": list(xs),
        "series": [list(s) for s in series],
        "colors": [POINT_COLORS[i % len(POINT_COLORS)] for i in range(len(series))],
        "labels": list(labels),
        "marker": float(marker),
        "highlight": highlight,
    }


def _curve_render(
    kind: str,
    view_tab: str,
    control_points: Sequence[Point],
    labels: Sequence[str],
    curve: Sequence[Point],
    t: float,
    extra: Optional[Dict] = None,
) -> RenderData:
    extras = dict(extra or {})
    frame_pts = list(control_points)
    for key in ("t0_tip", "t1_tip"):
        if key in extras:
            frame_pts.append(extras[key])
    bounds = extras.pop("view_bounds", None) or _bounds_from_points(frame_pts)
    data = {
        "kind": kind,
        "view_tab": view_tab,
        "control_points": [tuple(p) for p in control_points],
        "labels": list(labels),
        "curve_samples": [tuple(p) for p in curve],
        "t": float(t),
        "caption": extras.pop("caption", ""),
        "draggable": extras.pop("draggable", True),
        "show_polygon": extras.pop("show_polygon", True),
        "show_curve": extras.pop("show_curve", True),
        **extras,
    }
    return RenderData(mode="curves", curve_data=data, view_bounds=bounds)


def _step(
    index: int,
    title: str,
    equation: str,
    explanation: str,
    values: Dict,
    render: RenderData,
    metrics: Optional[Dict] = None,
) -> VisualizationStep:
    return VisualizationStep(
        index=index,
        title=title,
        equation=equation,
        explanation=explanation,
        values=values,
        render_data=render,
        metrics=metrics or {},
    )


# ===========================================================================
# Bézier lesson
# ===========================================================================

def _bezier_values(points: Sequence[Point], t: float, extra: Optional[Dict] = None) -> Dict:
    ct = de_casteljau(points, t)
    pyramid = de_casteljau_pyramid(points, t)
    payload = {
        "t": t,
        "curve_point": ct,
        "control_points": [tuple(p) for p in points],
        "pyramid": [[tuple(p) for p in level] for level in pyramid],
        "kind": "bezier",
    }
    if extra:
        payload.update(extra)
    return payload


def _bezier_common_rd(points, t, view_tab, extra=None):
    extras = dict(extra or {})
    pyramid = de_casteljau_pyramid(points, t)
    ct = pyramid[-1][0]
    traced_n = max(2, int(round(t * (SAMPLE_COUNT - 1))) + 1)
    curve = sample_bezier(points)
    extras.setdefault("pyramid", [[tuple(p) for p in lv] for lv in pyramid])
    extras.setdefault("curve_point", ct)
    extras.setdefault("traced_samples", curve[:traced_n])
    extras.setdefault("reveal_level", len(pyramid) - 1)
    labels = [f"P{i}" for i in range(len(points))]
    return _curve_render("bezier", view_tab, points, labels, curve, t, extras)


def bezier_intro_steps(points: Sequence[Point], t: float) -> List[VisualizationStep]:
    n = len(points) - 1
    ct = de_casteljau(points, t)
    steps = []

    steps.append(_step(
        1, "A curve from a control polygon",
        "C(t) is not the polyline P0P1…Pn — it is a smooth blend of those points.",
        "Bézier curves solve a modelling problem: draw a smooth free-form shape "
        "that a designer can steer with a handful of handles.  The handles form "
        "the control polygon.  The curve starts at P0, ends at Pn, and is pulled "
        "toward the interior points without generally passing through them.",
        _bezier_values(points, t, {"stage": "polygon", "caption": "The control polygon is the designer's input."}),
        _bezier_common_rd(points, t, "intro", {
            "show_curve": False, "reveal_level": 0, "draggable": True,
            "caption": "Four handles.  The curve will start at P0 and end at P3.",
        }),
        {"degree": n, "handles": n + 1},
    ))

    steps.append(_step(
        2, "The curve is attracted, not interpolated",
        "C(0) = P0,   C(1) = Pn,   C(t) lies in the convex hull of {P_i}.",
        "Only the first and last control points are interpolated.  Interior "
        "handles act like magnets: they pull the curve toward themselves.  "
        "Because every Bernstein weight is non-negative and they sum to 1, the "
        "curve can never leave the convex hull of the control polygon — a "
        "safety property used in clipping and collision tests.",
        _bezier_values(points, t, {"stage": "curve", "caption": "The cubic Bézier of this control polygon."}),
        _bezier_common_rd(points, t, "intro", {
            "reveal_level": 0, "caption": "The curve hugs the polygon but only interpolates P0 and P3.",
        }),
        {"C(0)": _fmt(points[0]), "C(1)": _fmt(points[-1])},
    ))

    steps.append(_step(
        3, "One parameter t from 0 to 1",
        f"t = {t:.2f}   →   C(t) = {_fmt(ct)}",
        "t is a blending parameter, not arc length and not time unless you "
        "choose it to be.  t = 0 is P0, t = 1 is P3.  Every t in between "
        "picks exactly one point on the curve.  Font outlines, CAD surfaces, "
        "and animation paths are all built by evaluating C(t) densely enough "
        "to look smooth.",
        _bezier_values(points, t, {"stage": "parameter", "caption": f"The point C({t:.2f}) on the curve."}),
        _bezier_common_rd(points, t, "intro", {
            "caption": f"t = {t:.2f} selects this point.  Drag handles or change t in Experiment.",
        }),
        {"t": f"{t:.2f}", "C(t)": _fmt(ct)},
    ))

    steps.append(_step(
        4, "Why designers use Bézier curves",
        "Applications: type design, vector graphics, camera paths, CAD, CSS easing.",
        "A cubic has only four handles, so it is cheap to store and evaluate, "
        "yet expressive enough for most 2D shapes.  TrueType and PostScript "
        "fonts are Bézier outlines.  The same construction extends to Bézier "
        "surfaces in 3D.  The cost of that simplicity is global control: "
        "moving P1 reshapes the entire cubic — which is why B-splines exist.",
        _bezier_values(points, t, {"stage": "why", "caption": "Global control: every handle affects every t."}),
        _bezier_common_rd(points, t, "intro", {
            "highlight_index": 1,
            "caption": "Move P1 later and watch the whole cubic respond — not just a local piece.",
        }),
        {"property": "global control"},
    ))
    return steps


def bezier_math_steps(points: Sequence[Point], t: float) -> List[VisualizationStep]:
    n = len(points) - 1
    weights = bernstein_all(n, t)
    ct = bezier_bernstein(points, t)
    xs = linspace(0.0, 1.0, 80)
    series = [[bernstein(n, i, x) for x in xs] for i in range(n + 1)]
    labels = [f"B{i}" for i in range(n + 1)]
    plot = _basis_plot(f"Bernstein basis  Bᵢ^{n}(t)", xs, series, t, labels)

    p0, p1 = points[0], points[1]
    linear = lerp(p0, p1, t)

    steps = []
    steps.append(_step(
        1, "Linear Bézier is just lerp",
        f"C(t) = (1 − t) P0 + t P1\n"
        f"     = (1 − {t:.2f})·{_fmt(p0)} + {t:.2f}·{_fmt(p1)}\n"
        f"     = {_fmt(linear)}",
        "The degree-1 Bézier is ordinary linear interpolation.  De Casteljau "
        "is this formula, applied over and over to neighbouring points.  "
        "Everything that follows is repeated lerp — there is no other primitive.",
        _bezier_values(points[:2], t, {"stage": "linear"}),
        _curve_render("bezier", "math", points[:2], ["P0", "P1"], sample_bezier(points[:2]), t, {
            "reveal_level": 1, "caption": "Degree 1: the curve is the chord itself.",
            "pyramid": [[tuple(p0), tuple(p1)], [tuple(linear)]],
            "curve_point": linear,
        }),
        {"degree": 1},
    ))

    steps.append(_step(
        2, "Quadratic: lerp of two lerps",
        "C(t) = (1−t)² P0  +  2(1−t)t P1  +  t² P2",
        "A quadratic Bézier is the linear interpolation of two linear Béziers "
        "(P0P1 and P1P2) at the same t.  Expanding that nested lerp produces "
        "the three Bernstein polynomials of degree 2.  The middle weight "
        "2(1−t)t peaks at t = 1/2, so P1 has the most influence at the midpoint.",
        _bezier_values(points[:3], t, {"stage": "quadratic"}),
        _bezier_common_rd(points[:3], t, "math", {
            "caption": "Degree 2: three handles, a parabolic-looking arc.",
        }),
        {"degree": 2},
    ))

    wtxt = " + ".join(f"{weights[i]:.3f}·P{i}" for i in range(n + 1))
    steps.append(_step(
        3, "Cubic Bernstein form",
        f"Bᵢ³(t) = C(3,i) tⁱ (1−t)³⁻ⁱ\n\n"
        f"C(t) = B₀³(t) P0 + B₁³(t) P1 + B₂³(t) P2 + B₃³(t) P3\n"
        f"     = (1−t)³ P0 + 3(1−t)²t P1 + 3(1−t)t² P2 + t³ P3\n\n"
        f"At t = {t:.2f}:  C(t) = {wtxt}\n"
        f"              = {_fmt(ct)}",
        "The cubic is the workhorse of 2D design.  Each control point is "
        "multiplied by its Bernstein weight; the four weights always sum to 1 "
        "(partition of unity).  Read the plot: at the current t the tallest "
        "basis function tells you which handle dominates C(t).",
        _bezier_values(points, t, {"stage": "cubic", "weights": weights}),
        _bezier_common_rd(points, t, "math", {
            "basis_plot": plot,
            "caption": f"Bernstein weights at t = {t:.2f}  —  they sum to {sum(weights):.3f}.",
        }),
        {f"B{i}": f"{weights[i]:.3f}" for i in range(n + 1)},
    ))

    steps.append(_step(
        4, "Partition of unity and the convex hull",
        f"Σᵢ Bᵢⁿ(t) = 1,    Bᵢⁿ(t) ≥ 0 for t ∈ [0, 1]\n"
        f"At t = {t:.2f}:  sum = {sum(weights):.6f}",
        "Because the weights are a convex combination, C(t) is a weighted "
        "average of the control points.  That is the convex-hull property.  "
        "It also gives affine invariance: transforming every handle by the "
        "same matrix transforms the curve identically — so you can rotate a "
        "Bézier by rotating its polygon, not by resampling.",
        _bezier_values(points, t, {"stage": "hull", "weights": weights}),
        _bezier_common_rd(points, t, "math", {
            "basis_plot": plot,
            "caption": "Non-negative weights that sum to 1  ⇒  C(t) stays inside the hull.",
        }),
        {"sum": f"{sum(weights):.6f}"},
    ))

    steps.append(_step(
        5, "Endpoint interpolation and global control",
        "C(0) = P0,   C(1) = Pn\n"
        "Bᵢⁿ(t) > 0 for every i when t ∈ (0, 1)  →  every handle affects every interior point.",
        "Bézier curves interpolate only their endpoints.  Interior handles "
        "are off the curve.  And because every Bernstein polynomial of degree "
        "n is strictly positive on (0, 1), moving any single handle reshapes "
        "the entire curve.  That global coupling is the reason B-splines "
        "introduce a knot vector and local support.",
        _bezier_values(points, t, {"stage": "properties"}),
        _bezier_common_rd(points, t, "math", {
            "basis_plot": plot,
            "highlight_index": 1,
            "caption": "Every Bᵢ is positive on (0, 1) — there is no local control.",
        }),
        {"C(0)": _fmt(points[0]), "C(1)": _fmt(points[-1])},
    ))
    return steps


def _lerp_render(pt_a: Point, pt_b: Point, t: float, extra=None):
    extras = dict(extra or {})
    p_t = lerp(pt_a, pt_b, t)
    extras.setdefault("pt_a", tuple(pt_a))
    extras.setdefault("pt_b", tuple(pt_b))
    extras.setdefault("curve_point", p_t)
    extras.setdefault("kind", "lerp_1d")
    extras.setdefault("draggable", True)
    points = [pt_a, pt_b]
    labels = ["A", "B"]
    curve = [pt_a, pt_b]
    return _curve_render("bezier", "stage2", points, labels, curve, t, extras)


def bezier_stage1_steps(points: Sequence[Point], t: float) -> List[VisualizationStep]:
    """Stage 1 — What is a Bézier Curve? Explains vector paths, P0-P3 roles, and handle dragging."""
    n = len(points) - 1
    p0, p1, p2, p3 = points[0], points[1], points[2], points[3]
    steps = []

    # Step 1: Why Bézier curves?
    pts_summary = f"P0 = {_fmt(p0)}    P1 = {_fmt(p1)}\nP2 = {_fmt(p2)}    P3 = {_fmt(p3)}"
    steps.append(_step(
        1, "Why Bézier Curves? Pixels vs Vector Paths",
        f"Raster: Millions of discrete pixels → Blurs when scaled!\n"
        f"Bézier: Just 4 control points → Infinitely smooth at any scale!\n\n"
        f"Control Points:\n{pts_summary}",
        "In Computer Graphics, curves define typography (TrueType & OpenType fonts), "
        "vector artwork (SVG paths in web browsers), motion paths in animations, and 3D CAD design. "
        "Instead of storing heavy pixel grids, engineer Pierre Bézier (at Renault) pioneered using "
        "just four control points (P0, P1, P2, P3) to mathematically represent elegant, scalable curves.",
        _bezier_values(points, t, {"stage": "stage1_intro", "caption": "Four control points define an infinitely scalable curve."}),
        _bezier_common_rd(points, t, "stage1", {
            "show_curve": False, "reveal_level": 0, "draggable": True,
            "caption": "Level 0: Four control handles form the control polygon.",
        }),
        {"P0": _fmt(p0), "P3": _fmt(p3), "Model": "Cubic Bézier (4 points)"},
    ))

    # Step 2: Anchors P0 and P3
    steps.append(_step(
        2, "Anchor Points: Start (P0) and End (P3)",
        f"Curve Start Anchor:  B(0.0) = P0 = {_fmt(p0)}\n"
        f"Curve End Anchor:    B(1.0) = P3 = {_fmt(p3)}\n\n"
        f"Baseline Chord: P0 ──────── P3",
        "P0 and P3 are the 'Anchor Points'. The curve physically begins at P0 (at parameter t = 0) "
        "and ends at P3 (at parameter t = 1). The curve is mathematically pinned to these two points, "
        "like two fixed nails in a board. If there were no middle handles, the curve would simply be "
        "the straight dashed baseline connecting P0 to P3.",
        _bezier_values(points, t, {"stage": "stage1_anchors", "caption": "The curve always passes through anchors P0 and P3."}),
        _bezier_common_rd(points, t, "stage1", {
            "show_curve": True, "faint_curve": True, "show_baseline": True,
            "highlight_indices": [0, 3], "draggable": True,
            "caption": "P0 and P3 are anchors. The curve is guaranteed to begin at P0 and end at P3.",
        }),
        {"Start P0": _fmt(p0), "End P3": _fmt(p3), "Anchor Rule": "Curve MUST touch P0 & P3"},
    ))

    # Step 3: Off-curve handles P1 and P2
    steps.append(_step(
        3, "Shape Handles: P1 & P2 as Curve Attractors",
        f"P1 = {_fmt(p1)}  →  Steers initial tangent away from P0\n"
        f"P2 = {_fmt(p2)}  →  Steers arrival tangent into P3\n\n"
        f"Off-Curve Rule: The curve bends toward P1 and P2, but never touches them!",
        "P1 and P2 are off-curve control handles — the curve does NOT pass through them! "
        "Instead, think of them as powerful directional magnets: P1 pulls the curve upward as it leaves P0, "
        "while P2 pulls the curve downward before it arrives at P3. The line segment P0→P1 defines the start tangent, "
        "and P2→P3 defines the arrival tangent.",
        _bezier_values(points, t, {"stage": "stage1_tangents", "caption": "P1 and P2 act like magnetic handles steering the curve."}),
        _bezier_common_rd(points, t, "stage1", {
            "show_curve": True, "show_tangents": True,
            "highlight_indices": [1, 2], "draggable": True,
            "caption": "P1 and P2 pull the curve toward themselves without the curve touching them.",
        }),
        {"P1 Handle": _fmt(p1), "P2 Handle": _fmt(p2), "Role": "Direction & Curvature Attractors"},
    ))

    # Step 4: Hands-on dragging
    steps.append(_step(
        4, "Hands-on: Drag Handles to Steer the Curve",
        f"Interactive Steering:\n"
        f"• Drag P1 to alter departure angle and bend depth\n"
        f"• Drag P2 to alter arrival angle and curvature\n\n"
        f"Current: P0={_fmt(p0)}, P1={_fmt(p1)}, P2={_fmt(p2)}, P3={_fmt(p3)}",
        "Try it now! Click and drag P1 or P2 anywhere on the canvas above. "
        "Notice how moving P1 bends the start of the curve, while moving P2 bends the end. "
        "You can create an S-curve, an arch, an inflection point, or even a loop! "
        "In design tools like Figma or Adobe Illustrator, the Pen Tool works using these exact handles.",
        _bezier_values(points, t, {"stage": "stage1_interactive", "caption": "Drag P1 or P2 on canvas to see the curve reshape live!"}),
        _bezier_common_rd(points, t, "stage1", {
            "show_curve": True, "show_polygon": True, "draggable": True,
            "caption": "Interactive: Drag P1 or P2 on canvas to observe real-time curve reshaping!",
        }),
        {"Drag Target": "P1 & P2 handles", "Real-World": "Figma / SVG / TrueType Fonts"},
    ))
    return steps


def bezier_stage2_steps(pt_a: Point, pt_b: Point, t: float) -> List[VisualizationStep]:
    """Stage 2 — Understand Linear Interpolation (Lerp) from scratch with 2 points A and B."""
    steps = []
    p_t = lerp(pt_a, pt_b, t)
    mid = lerp(pt_a, pt_b, 0.5)

    # Step 1: Concept of interpolation
    steps.append(_step(
        1, "What Does 'Interpolation' Mean?",
        f"Endpoints on a line segment:\n"
        f"   A = {_fmt(pt_a)}     B = {_fmt(pt_b)}\n\n"
        f"Parameter t represents percentage of travel from 0% (t = 0.0) to 100% (t = 1.0).\n"
        f"Goal: Find the exact coordinate of point P(t) at any progress percentage t.",
        "Before learning De Casteljau's algorithm, we must understand the core operation: "
        "Linear Interpolation ('Lerp'). Imagine walking on a straight road from point A to point B. "
        "When t = 0, you haven't started (at A). When t = 1, you have arrived (at B). "
        "At any fraction t between 0 and 1, where are you? Interpolation computes that exact coordinate.",
        {"kind": "lerp_1d", "pt_a": pt_a, "pt_b": pt_b, "t": t, "curve_point": p_t, "caption": "Linear Interpolation: finding an intermediate point P(t) between A and B."},
        _lerp_render(pt_a, pt_b, t, {
            "caption": "Linear Interpolation: Finding an intermediate point P(t) between A and B.",
        }),
        {"Start A": _fmt(pt_a), "End B": _fmt(pt_b), "t": f"{t:.2f}"},
    ))

    # Step 2: The Lerp Formula
    w_a = 1.0 - t
    w_b = t
    px = w_a * pt_a[0] + w_b * pt_b[0]
    py = w_a * pt_a[1] + w_b * pt_b[1]
    steps.append(_step(
        2, "The Lerp Formula: P(t) = (1 − t)·A + t·B",
        f"P(t) = (1 − t)·A + t·B\n\n"
        f"Component-wise calculation at t = {t:.2f}:\n"
        f"   P_x = (1 − {t:.2f})·({pt_a[0]:.2f}) + {t:.2f}·({pt_b[0]:.2f}) = {w_a:.2f}·({pt_a[0]:.2f}) + {w_b:.2f}·({pt_b[0]:.2f}) = {px:.2f}\n"
        f"   P_y = (1 − {t:.2f})·({pt_a[1]:.2f}) + {t:.2f}·({pt_b[1]:.2f}) = {w_a:.2f}·({pt_a[1]:.2f}) + {w_b:.2f}·({pt_b[1]:.2f}) = {py:.2f}\n"
        f"   P({t:.2f}) = ({px:.2f}, {py:.2f})",
        "The formula is a weighted blend: the weights are (1 − t) and t. "
        "Notice that (1 − t) + t = 1 always! As t increases, the influence of start point A decreases, "
        "while destination B increases. At t = 0.35, point P has traveled 35% of the distance from A toward B.",
        {"kind": "lerp_1d", "pt_a": pt_a, "pt_b": pt_b, "t": t, "curve_point": p_t, "caption": f"P({t:.2f}) divides segment AB in ratio {int(t*100)}% : {int((1-t)*100)}%."},
        _lerp_render(pt_a, pt_b, t, {
            "show_weights": True,
            "caption": f"P({t:.2f}) divides segment AB into ratio {int(t*100)}% : {int((1-t)*100)}%.",
        }),
        {"P(t)": _fmt(p_t), "Weight A (1-t)": f"{w_a:.2f}", "Weight B (t)": f"{w_b:.2f}"},
    ))

    # Step 3: Three Milestones: t=0, t=0.5, t=1
    steps.append(_step(
        3, "Three Key Milestones: t = 0, t = 0.5, and t = 1",
        f"At t = 0.00:  P(0)   = 1·A + 0·B = A = {_fmt(pt_a)}           [Start Anchor]\n"
        f"At t = 0.50:  P(0.5) = 0.5·A + 0.5·B = (A + B)/2 = {_fmt(mid)}  [Exact Midpoint]\n"
        f"At t = 1.00:  P(1)   = 0·A + 1·B = B = {_fmt(pt_b)}            [End Destination]",
        "Notice how intuitive the math is at key milestones:\n"
        "• At t = 0: Weight of B is zero, leaving pure A.\n"
        "• At t = 0.5: Both points share equal 50/50 weight, giving the exact geometric midpoint (A + B)/2.\n"
        "• At t = 1: Weight of A is zero, leaving pure B.\n"
        "Every other point on the segment is simply an intermediate percentage.",
        {"kind": "lerp_1d", "pt_a": pt_a, "pt_b": pt_b, "t": t, "curve_point": p_t, "caption": "Milestones: t = 0 is A, t = 0.5 is Midpoint, t = 1 is B."},
        _lerp_render(pt_a, pt_b, t, {
            "show_milestones": True,
            "caption": "Milestones: t = 0 is A, t = 0.5 is Midpoint, t = 1 is B.",
        }),
        {"t": f"{t:.2f}", "Midpoint": _fmt(mid), "Rule": "(1-t) + t = 1"},
    ))

    # Step 4: Interactive Lerp
    steps.append(_step(
        4, "Interactive Lerp: Slide t & Drag A, B",
        f"Live Linear Interpolation at t = {t:.2f}:\n"
        f"   P({t:.2f}) = (1 − {t:.2f})·{_fmt(pt_a)} + {t:.2f}·{_fmt(pt_b)}\n"
        f"           = {w_a:.2f}·{_fmt(pt_a)} + {w_b:.2f}·{_fmt(pt_b)}\n"
        f"           = {_fmt(p_t)}",
        "Test it interactively! Move the 't' slider on the right panel from 0 to 1 to see point P "
        "glide smoothly along segment AB. You can also drag endpoints A and B anywhere on the canvas! "
        "Every calculation updates dynamically. Remember this single operation: De Casteljau's algorithm "
        "is built entirely by repeating this exact lerp across multiple points!",
        {"kind": "lerp_1d", "pt_a": pt_a, "pt_b": pt_b, "t": t, "curve_point": p_t, "caption": f"Drag A and B, or slide t ({t:.2f}) to watch P recalculate live!"},
        _lerp_render(pt_a, pt_b, t, {
            "caption": f"Drag endpoints A and B, or slide t ({t:.2f}) to see P move live!",
        }),
        {"P(t)": _fmt(p_t), "A": _fmt(pt_a), "B": _fmt(pt_b), "t": f"{t:.2f}"},
    ))
    return steps


def bezier_stage3_steps(points: Sequence[Point], t: float) -> List[VisualizationStep]:
    """Stage 3 — De Casteljau's Algorithm taught in three separate progressive levels."""
    pyramid = de_casteljau_pyramid(points, t)
    n = len(points) - 1
    p0, p1, p2, p3 = points[0], points[1], points[2], points[3]
    q0, q1, q2 = pyramid[1][0], pyramid[1][1], pyramid[1][2]
    r0, r1 = pyramid[2][0], pyramid[2][1]
    b_t = pyramid[3][0]
    steps = []

    # Step 1: The Core Idea — Reduction Pyramid
    pts_lines = [f"P{i}⁽⁰⁾ = P{i} = {_fmt(p)}" for i, p in enumerate(points)]
    steps.append(_step(
        1, "The Core Idea: A Pyramid of Lerps",
        f"Level 0 (Control Polygon):  4 points  {{P0, P1, P2, P3}}\n"
        f"Level 1 (First lerps):      3 points  {{Q0, Q1, Q2}}\n"
        f"Level 2 (Second lerps):     2 points  {{R0, R1}}\n"
        f"Level 3 (Final lerp):       1 point   {{B(t)}} → Exactly on the curve!\n\n"
        f"Input Control Points:\n" + "\n".join(pts_lines),
        "De Casteljau's algorithm never uses complex polynomial calculus. It only uses linear interpolation! "
        "We start with 4 control points. Interpolating each consecutive pair gives 3 points (Q). "
        "Interpolating those gives 2 points (R). Interpolating the last two gives 1 point: B(t). "
        "That single point is guaranteed to sit on the Bézier curve!",
        _bezier_values(points, t, {"stage": "level0", "caption": "Level 0 — the input control polygon."}),
        _bezier_common_rd(points, t, "stage3", {
            "reveal_level": 0, "show_curve": False,
            "caption": "Level 0: 4 input control points. We will now lerp neighbouring handles at t.",
            "anim": {"type": "reveal"},
        }),
        {"level": 0, "points": 4, "t": f"{t:.2f}", "P1": _fmt(p1)},
    ))

    # Step 2: Level 1 — Three lerps produce Q0, Q1, Q2
    eq_lv1 = (
        f"Level 1: Three Lerps at t = {t:.2f}\n\n"
        f"Q0 = (1 − {t:.2f})·P0 + {t:.2f}·P1 = (1 − {t:.2f})·{_fmt(p0)} + {t:.2f}·{_fmt(p1)} = {_fmt(q0)}\n"
        f"Q1 = (1 − {t:.2f})·P1 + {t:.2f}·P2 = (1 − {t:.2f})·{_fmt(p1)} + {t:.2f}·{_fmt(p2)} = {_fmt(q1)}\n"
        f"Q2 = (1 − {t:.2f})·P2 + {t:.2f}·P3 = (1 − {t:.2f})·{_fmt(p2)} + {t:.2f}·{_fmt(p3)} = {_fmt(q2)}"
    )
    steps.append(_step(
        2, "Level 1: Three Lerps Produce Q0, Q1, Q2",
        eq_lv1,
        "We apply linear interpolation at the same 't' to each edge of the control polygon:\n"
        "• Q0 splits segment P0-P1 at ratio t : (1−t)\n"
        "• Q1 splits segment P1-P2 at ratio t : (1−t)\n"
        "• Q2 splits segment P2-P3 at ratio t : (1−t)\n"
        "Notice how 4 input points have condensed to 3 intermediate points! We connect them with teal segments.",
        _bezier_values(points, t, {"stage": "level1", "caption": f"Level 1: Q0={_fmt(q0)}, Q1={_fmt(q1)}, Q2={_fmt(q2)}"}),
        _bezier_common_rd(points, t, "stage3", {
            "reveal_level": 1, "show_curve": False,
            "caption": f"Level 1: 3 intermediate points Q0, Q1, Q2 connected by teal segments.",
            "anim": {"type": "lerp_level", "level": 1},
        }),
        {"level": 1, "Q0": _fmt(q0), "Q1": _fmt(q1), "Q2": _fmt(q2), "t": f"{t:.2f}"},
    ))

    # Step 3: Level 2 — Two lerps produce R0, R1
    eq_lv2 = (
        f"Level 2: Two Lerps at t = {t:.2f}\n\n"
        f"R0 = (1 − {t:.2f})·Q0 + {t:.2f}·Q1 = (1 − {t:.2f})·{_fmt(q0)} + {t:.2f}·{_fmt(q1)} = {_fmt(r0)}\n"
        f"R1 = (1 − {t:.2f})·Q1 + {t:.2f}·Q2 = (1 − {t:.2f})·{_fmt(q1)} + {t:.2f}·{_fmt(q2)} = {_fmt(r1)}"
    )
    steps.append(_step(
        3, "Level 2: Two Lerps Produce R0 and R1",
        eq_lv2,
        "Now repeat the exact same linear interpolation on the teal segments Q0-Q1 and Q1-Q2:\n"
        "• R0 splits segment Q0-Q1 at ratio t : (1−t)\n"
        "• R1 splits segment Q1-Q2 at ratio t : (1−t)\n"
        "3 points have now condensed down to 2 points! We connect R0 and R1 with an orange segment.",
        _bezier_values(points, t, {"stage": "level2", "caption": f"Level 2: R0={_fmt(r0)}, R1={_fmt(r1)}"}),
        _bezier_common_rd(points, t, "stage3", {
            "reveal_level": 2, "show_curve": False,
            "caption": f"Level 2: 2 points R0 and R1 connected by an orange segment.",
            "anim": {"type": "lerp_level", "level": 2},
        }),
        {"level": 2, "R0": _fmt(r0), "R1": _fmt(r1), "t": f"{t:.2f}"},
    ))

    # Step 4: Level 3 — Final lerp produces B(t)
    eq_lv3 = (
        f"Level 3: The Final Lerp at t = {t:.2f}\n\n"
        f"B(t) = (1 − {t:.2f})·R0 + {t:.2f}·R1\n"
        f"     = (1 − {t:.2f})·{_fmt(r0)} + {t:.2f}·{_fmt(r1)}\n"
        f"     = {_fmt(b_t)}\n\n"
        f"Final Curve Point: B({t:.2f}) = {_fmt(b_t)}"
    )
    steps.append(_step(
        4, "Level 3: The Final Lerp Produces B(t)",
        eq_lv3,
        "Only one segment remains: R0-R1. We perform one final lerp along R0-R1 at t = 0.35. "
        "A single point remains: B(t). After 3 successive stages of linear interpolation, "
        "we have arrived at the exact point on the Bézier curve!",
        _bezier_values(points, t, {"stage": "level3", "caption": f"Level 3: Final curve point B({t:.2f}) = {_fmt(b_t)}"}),
        _bezier_common_rd(points, t, "stage3", {
            "reveal_level": 3, "show_curve": True,
            "caption": f"Level 3: B({t:.2f}) = {_fmt(b_t)}. This point sits on the Bézier curve!",
            "anim": {"type": "lerp_level", "level": 3},
        }),
        {"level": 3, "B(t)": _fmt(b_t), "t": f"{t:.2f}"},
    ))

    # Step 5: Complete construction
    steps.append(_step(
        5, "The Miracle: B(t) Lies Exactly on the Bézier Curve!",
        f"Repeating De Casteljau for every t ∈ [0, 1] traces the full curve:\n"
        f"   t = 0.00  →  B(0.0) = P0 = {_fmt(p0)}\n"
        f"   t = {t:.2f}  →  B({t:.2f}) = {_fmt(b_t)}\n"
        f"   t = 1.00  →  B(1.0) = P3 = {_fmt(p3)}\n\n"
        f"Bernstein Equivalence:\n"
        f"   B(t) = (1−t)³·P0 + 3(1−t)²t·P1 + 3(1−t)t²·P2 + t³·P3 = {_fmt(b_t)}",
        "De Casteljau evaluates one point for a given t. When t smoothly sweeps from 0 to 1, "
        "every intermediate point slides along its segment, and point B(t) traces out the entire "
        "cubic Bézier curve! In Stage 4, you can experiment freely by dragging handles and sliding t.",
        _bezier_values(points, t, {"stage": "stage3_complete", "caption": f"De Casteljau evaluation: t = {t:.2f} → B(t) = {_fmt(b_t)}"}),
        _bezier_common_rd(points, t, "stage3", {
            "reveal_level": 3, "show_curve": True,
            "caption": f"Complete: B({t:.2f}) = {_fmt(b_t)}. Sweeping t from 0 to 1 traces the curve!",
        }),
        {"C(t)": _fmt(b_t), "t": f"{t:.2f}", "Complexity": "O(n²) lerps", "Result": "Exact Bézier Curve"},
    ))
    return steps


def bezier_stage4_steps(points: Sequence[Point], t_focus: float) -> List[VisualizationStep]:
    """Stage 4 — Complete Interactive Visualization. Draggable points, t slider, all levels, play/sweep."""
    steps = []
    ts = linspace(0.0, 1.0, SWEEP_FRAMES)
    focus_idx = min(range(len(ts)), key=lambda i: abs(ts[i] - t_focus))
    n = len(points) - 1

    for i, t in enumerate(ts):
        pyramid = de_casteljau_pyramid(points, t)
        b_t = pyramid[-1][0]
        weights = bernstein_all(n, t)
        caption = f"t = {t:.2f}   B(t) = {_fmt(b_t)}"
        weight_str = "  ".join(f"B{k}={w:.3f}" for k, w in enumerate(weights))
        eq_text = (
            f"Interactive Visualizer at t = {t:.2f}:\n"
            f"   B({t:.2f}) = {_fmt(b_t)}\n\n"
            f"Bernstein Basis Weights:\n   {weight_str}\n\n"
            f"De Casteljau Points:\n"
            f"   Q0={_fmt(pyramid[1][0])}  Q1={_fmt(pyramid[1][1])}  Q2={_fmt(pyramid[1][2])}\n"
            f"   R0={_fmt(pyramid[2][0])}  R1={_fmt(pyramid[2][1])}"
        )
        steps.append(_step(
            i + 1, f"Interactive Studio: t = {t:.2f}",
            eq_text,
            "Complete Interactive Studio: Drag P0, P1, P2, P3 anywhere on the canvas. "
            "Move the 't' slider on the right to sweep t from 0 to 1, or press Play to watch "
            "the De Casteljau pyramid slide smoothly and deposit B(t) onto the curve. "
            "Every intermediate point (Q0..Q2, R0..R1) and calculation recomputes dynamically in real time!",
            _bezier_values(points, t, {"stage": "stage4_studio", "caption": caption}),
            _bezier_common_rd(points, t, "stage4", {
                "reveal_level": 3, "show_curve": True, "draggable": True,
                "caption": caption,
                "anim": {"type": "sweep"} if i != focus_idx else None,
            }),
            {"t": f"{t:.2f}", "B(t)": _fmt(b_t), "P0": _fmt(points[0]), "P3": _fmt(points[-1])},
        ))
    return steps


def bezier_stage5_steps() -> List[VisualizationStep]:
    """Stage 5 — Test Your Understanding. 5 interactive assessment questions."""
    from ui.bezier_quiz_widget import QUIZ_QUESTIONS
    steps = []
    dummy_pts = DEFAULT_BEZIER
    t = 0.5

    for i, q in enumerate(QUIZ_QUESTIONS):
        opts_formatted = "\n".join(f"[{opt_key}] {opt_text}" for opt_key, opt_text in q["options"])
        eq_text = (
            f"Question {i + 1} of {len(QUIZ_QUESTIONS)}:  {q['topic']}\n\n"
            f"{q['question']}\n\n"
            f"Options:\n{opts_formatted}"
        )
        expl_text = (
            f"Select your answer directly on the Quiz Card in the central workspace above! "
            f"You will get immediate visual feedback and a detailed explanation.\n\n"
            f"Hint / Takeaway: {q['explanation']}"
        )
        steps.append(_step(
            i + 1, f"Question {i + 1}: {q['topic']}",
            eq_text,
            expl_text,
            {"stage": "stage5_quiz", "q_index": i, "topic": q["topic"]},
            _bezier_common_rd(dummy_pts, t, "stage5", {
                "caption": f"Question {i + 1} of 5: {q['topic']}. Click an answer on the card!",
            }),
            {"Question": f"{i + 1} / {len(QUIZ_QUESTIONS)}", "Topic": q["topic"]},
        ))
    return steps


def bezier_casteljau_steps(points: Sequence[Point], t: float) -> List[VisualizationStep]:
    return bezier_stage3_steps(points, t)


def bezier_experiment_steps(points: Sequence[Point], t_focus: float) -> List[VisualizationStep]:
    steps = []
    ts = linspace(0.0, 1.0, SWEEP_FRAMES)
    # Snap the focus t onto the sweep so the slider and timeline agree.
    focus_idx = min(range(len(ts)), key=lambda i: abs(ts[i] - t_focus))
    for i, t in enumerate(ts):
        ct = de_casteljau(points, t)
        weights = bernstein_all(len(points) - 1, t)
        caption = f"t = {t:.2f}   C(t) = {_fmt(ct)}"
        steps.append(_step(
            i + 1, f"Sweep  t = {t:.2f}",
            f"C({t:.2f}) = {_fmt(ct)}\n"
            + "  ".join(f"B{k}={w:.3f}" for k, w in enumerate(weights)),
            "Drag P0–P3 on the canvas.  The control polygon, De Casteljau "
            "pyramid, and curve all recompute from the same interpolation.  "
            "Play sweeps t from 0 to 1 so you can see every intermediate "
            "point slide along its parent segment and deposit C(t) onto the curve.",
            _bezier_values(points, t, {"stage": "experiment", "caption": caption}),
            _bezier_common_rd(points, t, "experiment", {
                "caption": caption,
                "anim": {"type": "sweep"} if i != focus_idx else None,
            }),
            {"t": f"{t:.2f}", "C(t)": _fmt(ct)},
        ))
    return steps


# ===========================================================================
# B-spline lesson
# ===========================================================================

def _bspline_bundle(points, degree, style, u):
    knots = make_knot_vector(len(points), degree, style)
    umin, umax = parameter_domain(degree, len(points), knots)
    u_clamped = clamp(u, umin, umax)
    curve = sample_bspline(points, degree, knots)
    cu = bspline_point(points, degree, knots, u_clamped)
    basis = all_basis(len(points), degree, knots, u_clamped)
    span = find_span(len(points) - 1, degree, u_clamped, knots)
    return knots, umin, umax, u_clamped, curve, cu, basis, span


def _bspline_rd(points, degree, knots, u, view_tab, extra=None):
    extras = dict(extra or {})
    curve = extras.pop("curve", None) or sample_bspline(points, degree, knots)
    umin, umax = parameter_domain(degree, len(points), knots)
    u = clamp(u, umin, umax)
    cu = bspline_point(points, degree, knots, u)
    extras.setdefault("curve_point", cu)
    extras.setdefault("knots", list(knots))
    extras.setdefault("degree", degree)
    extras.setdefault("u_domain", (umin, umax))
    traced_n = max(2, int(round(((u - umin) / max(umax - umin, EPSILON)) * (len(curve) - 1))) + 1)
    extras.setdefault("traced_samples", curve[:traced_n])
    labels = [f"P{i}" for i in range(len(points))]
    return _curve_render("bspline", view_tab, points, labels, curve, u, extras)


def _knot_equation(knots: Sequence[float], degree: int, n_ctrl: int) -> str:
    body = ", ".join(f"{k:.2f}" for k in knots)
    n = n_ctrl - 1
    return (
        f"p = {degree},   n = {n}  ({n_ctrl} control points)\n"
        f"m = n + p + 1 = {n + degree + 1}   →  {len(knots)} knots\n"
        f"U = [{body}]\n"
        f"domain  [u_p, u_{{n+1}}] = [{knots[degree]:.2f}, {knots[n + 1]:.2f}]"
    )


def bspline_intro_steps(points, degree, style, u) -> List[VisualizationStep]:
    knots, umin, umax, u, curve, cu, basis, span = _bspline_bundle(points, degree, style, u)
    steps = []

    steps.append(_step(
        1, "Bézier's limitation: global control",
        "A degree-n Bézier with n+1 handles is one polynomial.  Moving any Pi changes C(t) for every t ∈ (0, 1).",
        "That is fine for a short font stem.  It is a problem for a long "
        "free-form path: editing the left end should not wiggle the right end.  "
        "B-splines fix this by covering the path with overlapping local "
        "polynomials whose influence is limited by a knot vector.",
        {"kind": "bspline", "stage": "why", "u": u, "caption": "Same handles, but the influence is about to become local."},
        _bspline_rd(points, degree, knots, u, "intro", {
            "show_curve": False, "caption": "The control polygon.  B-splines still use one, plus knots and a degree.",
        }),
        {"handles": len(points)},
    ))

    steps.append(_step(
        2, "A piecewise curve with local support",
        f"C(u) = Σᵢ Nᵢ,ₚ(u) Pᵢ\n"
        f"Nᵢ,ₚ(u) = 0 outside [uᵢ, uᵢ₊ₚ₊₁]\n\n"
        + _knot_equation(knots, degree, len(points)),
        "Each basis function Nᵢ,ₚ is a bump spanning only p+1 knot intervals.  "
        "At any parameter u, only p+1 of them are non-zero, so C(u) is a blend "
        "of only p+1 neighbouring control points.  Move P2 and only the piece "
        "of the curve whose bases include i = 2 will move.",
        {"kind": "bspline", "stage": "local", "u": u, "knots": list(knots),
         "caption": "Local support: only a few handles affect C(u)."},
        _bspline_rd(points, degree, knots, u, "intro", {
            "caption": "The B-spline of this polygon.  Compare with a single cubic Bézier.",
            "highlight_index": 2,
        }),
        {"degree": degree, "nonzero_at_u": sum(1 for v in basis if v > EPSILON)},
    ))

    xs, series = basis_samples(len(points), degree, knots)
    plot = _basis_plot(f"B-spline basis  Nᵢ,{degree}(u)", xs, series, u, [f"N{i}" for i in range(len(points))], highlight=2)
    lo, hi = local_support_interval(2, degree, knots)

    steps.append(_step(
        3, "Clamped knots interpolate the endpoints",
        "Clamped (open-uniform) knots repeat 0 and 1, p+1 times.\n"
        "That forces C(u_min) = P0 and C(u_max) = Pn — like a Bézier.\n"
        "Uniform (unclamped) knots do not interpolate the ends.",
        "A clamped B-spline of degree n with exactly n+1 control points is "
        "identical to a Bézier curve of degree n (the knot vector collapses "
        "to [0…0, 1…1]).  Extra control points, or a different knot vector, "
        "are what make B-splines a different algorithm — not a renamed Bézier.",
        {"kind": "bspline", "stage": "clamped", "u": u, "knots": list(knots),
         "caption": f"N2 is nonzero only on [{lo:.2f}, {hi:.2f}]."},
        _bspline_rd(points, degree, knots, u, "intro", {
            "basis_plot": plot,
            "highlight_index": 2,
            "caption": f"Support of P2:  [{lo:.2f}, {hi:.2f}].  Outside that interval P2 is ignored.",
        }),
        {"C(umin)": _fmt(bspline_point(points, degree, knots, umin)),
         "C(umax)": _fmt(bspline_point(points, degree, knots, umax))},
    ))

    steps.append(_step(
        4, "Degree, knots, and smoothness",
        f"Degree p = {degree}   →   C^{{{degree - 1}}} continuity at a simple knot.\n"
        "Raising multiplicity at a knot lowers continuity there (a corner if multiplicity = p).",
        "Degree is independent of the number of control points (unlike Bézier, "
        "where degree = n_ctrl − 1).  You can keep a cubic and add as many "
        "handles as the shape needs.  That is the modelling reason B-splines "
        "won in CAD.",
        {"kind": "bspline", "stage": "degree", "u": u, "caption": "Degree is a separate knob from the handle count."},
        _bspline_rd(points, degree, knots, u, "intro", {
            "basis_plot": plot,
            "caption": f"Degree {degree} with {len(points)} handles.  Try quadratic in Experiment.",
        }),
        {"p": degree, "continuity": f"C{degree - 1} at simple knots"},
    ))
    return steps


def bspline_math_steps(points, degree, style, u) -> List[VisualizationStep]:
    knots, umin, umax, u, curve, cu, basis, span = _bspline_bundle(points, degree, style, u)
    xs, series = basis_samples(len(points), degree, knots)
    plot = _basis_plot(f"Nᵢ,{degree}(u)", xs, series, u, [f"N{i}" for i in range(len(points))])
    n = len(points) - 1
    steps = []

    steps.append(_step(
        1, "The knot vector",
        _knot_equation(knots, degree, len(points)),
        "Knots are not control points.  They are the parameter values where "
        "the piecewise polynomial changes which handles it is blending.  "
        "They must be non-decreasing.  Repeating a knot (multiplicity) "
        "squeezes the basis functions and can create a corner.  Clamped "
        "vectors repeat the first and last knot p+1 times.",
        {"kind": "bspline", "stage": "knots", "u": u, "knots": list(knots),
         "caption": "Knots live on the parameter axis, not in the plane of the curve."},
        _bspline_rd(points, degree, knots, u, "math", {
            "basis_plot": plot,
            "caption": f"U has {len(knots)} knots for {len(points)} points of degree {degree}.",
        }),
        {"knots": len(knots), "interior": n - degree},
    ))

    steps.append(_step(
        2, "Find the span containing u",
        f"u = {u:.2f} lives in span k = {span}\n"
        f"that is the unique k with  u_k ≤ u < u_{{k+1}}  (right-closed at u_max).\n"
        f"Only handles P_{{{span - degree}}} … P_{{{span}}} can contribute.",
        "This is why the algorithm is local.  The span index is a binary "
        "search on the knot vector (Piegl/Tiller A2.1).  From here we only "
        "ever look at p+1 control points.",
        {"kind": "bspline", "stage": "span", "u": u, "span": span, "knots": list(knots),
         "caption": f"Span {span}: blend P{span - degree}…P{span}."},
        _bspline_rd(points, degree, knots, u, "math", {
            "basis_plot": plot,
            "span": span,
            "highlight_range": (span - degree, span),
            "caption": f"u = {u:.2f} → span {span}.  Highlighted handles are the only ones in C(u).",
        }),
        {"span": span, "local_points": degree + 1},
    ))

    # Show Cox–de Boor recurrence with numeric N_i,0 then build up.
    i0 = span - degree
    rec_lines = [
        "Nᵢ,₀(u) = 1  if uᵢ ≤ u < uᵢ₊₁  else  0",
        f"Nᵢ,ₚ(u) = [(u − uᵢ)/(uᵢ₊ₚ − uᵢ)] Nᵢ,ₚ₋₁(u)",
        "         + [(uᵢ₊ₚ₊₁ − u)/(uᵢ₊ₚ₊₁ − uᵢ₊₁)] Nᵢ₊₁,ₚ₋₁(u)",
        "",
        f"At u = {u:.2f}:",
    ]
    for i, val in enumerate(basis):
        rec_lines.append(f"  N{i},{degree}(u) = {val:.4f}")
    rec_lines.append(f"  sum = {sum(basis):.6f}   (partition of unity)")

    steps.append(_step(
        3, "Cox–de Boor recurrence",
        "\n".join(rec_lines),
        "Degree 0 bases are box functions on a single knot interval.  Higher "
        "degree bases are the linear interpolation of two lower-degree bases "
        "— the same idea as De Casteljau, but on the parameter axis rather "
        "than on the control polygon.  A zero denominator (repeated knots) "
        "is defined to contribute 0.  The result is a numerically stable "
        "pyramid that yields exactly p+1 non-zero values.",
        {"kind": "bspline", "stage": "cox", "u": u, "basis": basis, "knots": list(knots),
         "caption": "Cox–de Boor builds the weights, then the curve is their blend of the Pi."},
        _bspline_rd(points, degree, knots, u, "math", {
            "basis_plot": plot,
            "highlight_range": (i0, span),
            "caption": "The bumps are the Nᵢ,ₚ.  Their heights at the marker are the blend weights.",
        }),
        {f"N{i}": f"{basis[i]:.3f}" for i in range(len(points))},
    ))

    blend = " + ".join(f"{basis[i]:.3f}·P{i}" for i, v in enumerate(basis) if v > 1e-6)
    steps.append(_step(
        4, "The curve point is a local weighted average",
        f"C(u) = Σᵢ Nᵢ,{degree}(u) Pᵢ\n"
        f"     = {blend}\n"
        f"     = {_fmt(cu)}",
        "This is the same convex-combination idea as Bézier, restricted to "
        "the local handles.  Partition of unity still holds, so the piece "
        "stays in the convex hull of those p+1 points — a tighter hull than "
        "the whole polygon.",
        {"kind": "bspline", "stage": "eval", "u": u, "curve_point": cu, "caption": f"C({u:.2f}) = {_fmt(cu)}"},
        _bspline_rd(points, degree, knots, u, "math", {
            "basis_plot": plot,
            "caption": f"C({u:.2f}) = {_fmt(cu)}",
        }),
        {"C(u)": _fmt(cu), "sum N": f"{sum(basis):.6f}"},
    ))

    steps.append(_step(
        5, "Pseudocode (de Boor evaluation)",
        "k ← FindSpan(n, p, u, U)          # A2.1\n"
        "N ← BasisFuns(k, u, p, U)          # A2.2, p+1 values\n"
        "C ← (0, 0)\n"
        "for j ← 0 to p:\n"
        "    C ← C + N[j] · P[k − p + j]\n"
        "return C",
        "The triangle of Cox–de Boor can also be run on the points themselves "
        "(the de Boor algorithm), analogous to De Casteljau.  The two are "
        "equivalent; we show the basis form because the plot of Nᵢ,ₚ is the "
        "clearest picture of local control.",
        {"kind": "bspline", "stage": "code", "u": u, "caption": "de Boor / A3.1 evaluation."},
        _bspline_rd(points, degree, knots, u, "math", {
            "basis_plot": plot,
            "caption": "Play Experiment to sweep u and watch the active bump travel.",
        }),
        {"span": span},
    ))
    return steps


def bspline_experiment_steps(points, degree, style, u_focus) -> List[VisualizationStep]:
    knots, umin, umax, _, curve, _, _, _ = _bspline_bundle(points, degree, style, u_focus)
    xs, series = basis_samples(len(points), degree, knots)
    steps = []
    us = linspace(umin, umax, SWEEP_FRAMES)
    for i, u in enumerate(us):
        cu = bspline_point(points, degree, knots, u)
        basis = all_basis(len(points), degree, knots, u)
        span = find_span(len(points) - 1, degree, u, knots)
        plot = _basis_plot(
            f"Nᵢ,{degree}(u)", xs, series, u,
            [f"N{k}" for k in range(len(points))],
        )
        active = [k for k, v in enumerate(basis) if v > 1e-6]
        caption = f"u = {u:.2f}   C(u) = {_fmt(cu)}   span {span}  (P{active[0]}…P{active[-1]})"
        steps.append(_step(
            i + 1, f"Sweep  u = {u:.2f}",
            f"C({u:.2f}) = {_fmt(cu)}\n"
            + "  ".join(f"N{k}={basis[k]:.3f}" for k in range(len(points))),
            "Drag any handle: only the arc whose bases include that index "
            "will move.  Change the degree or the knot style and the basis "
            "plot tells you immediately whether endpoints are interpolated "
            "and how wide each bump is.",
            {"kind": "bspline", "stage": "experiment", "u": u, "t": u, "curve_point": cu,
             "knots": list(knots), "basis": basis, "span": span, "caption": caption},
            _bspline_rd(points, degree, knots, u, "experiment", {
                "basis_plot": plot,
                "span": span,
                "highlight_range": (span - degree, span),
                "caption": caption,
            }),
            {"u": f"{u:.2f}", "C(u)": _fmt(cu), "span": span},
        ))
    return steps


# ===========================================================================
# Hermite lesson
# ===========================================================================

def _hermite_rd(p0, p1, t0, t1, t, view_tab, extra=None):
    extras = dict(extra or {})
    curve = sample_hermite(p0, p1, t0, t1)
    ct = hermite_point(p0, p1, t0, t1, t)
    tip0, tip1 = add(p0, t0), add(p1, t1)
    extras.setdefault("curve_point", ct)
    extras.setdefault("p0", tuple(p0))
    extras.setdefault("p1", tuple(p1))
    extras.setdefault("t0", tuple(t0))
    extras.setdefault("t1", tuple(t1))
    extras.setdefault("t0_tip", tuple(tip0))
    extras.setdefault("t1_tip", tuple(tip1))
    traced_n = max(2, int(round(t * (len(curve) - 1))) + 1)
    extras.setdefault("traced_samples", curve[:traced_n])
    bezier = hermite_to_bezier(p0, p1, t0, t1)
    extras.setdefault("equiv_bezier", [tuple(p) for p in bezier])
    return _curve_render(
        "hermite", view_tab, [p0, p1], ["P0", "P1"], curve, t, extras,
    )


def hermite_intro_steps(p0, p1, t0, t1, t) -> List[VisualizationStep]:
    ct = hermite_point(p0, p1, t0, t1, t)
    d0 = hermite_derivative(p0, p1, t0, t1, 0.0)
    d1 = hermite_derivative(p0, p1, t0, t1, 1.0)
    steps = []

    steps.append(_step(
        1, "Interpolate position and velocity",
        "Given P0, P1 and tangents T0, T1, find a cubic C such that\n"
        "C(0) = P0,  C(1) = P1,  C'(0) = T0,  C'(1) = T1.",
        "Animation, camera paths, and physical trajectories often specify "
        "where something is and which way it is going.  Cubic Hermite "
        "interpolation is the unique cubic that matches two positions and "
        "two velocities.  The tangents are on-curve data, not off-curve "
        "Bézier handles.",
        {"kind": "hermite", "stage": "goal", "t": t, "caption": "Two points, two arrows."},
        _hermite_rd(p0, p1, t0, t1, t, "intro", {
            "show_curve": False, "show_polygon": False,
            "caption": "P0, P1 and their tangent vectors T0, T1.  The curve must match all four.",
        }),
        {"inputs": 4},
    ))

    steps.append(_step(
        2, "The unique cubic that matches all four",
        f"C(0) = {_fmt(p0)}   C(1) = {_fmt(p1)}\n"
        f"C'(0) = {_fmt(d0)}   C'(1) = {_fmt(d1)}",
        "The arrows you see are the actual tangent vectors: direction is "
        "the heading of the curve at the endpoint, magnitude is how "
        "aggressively the cubic leaves (or arrives).  A long T0 makes the "
        "curve shoot far in that direction before it has to meet P1; a zero "
        "tangent makes the cubic leave slowly, almost like a straight fade.",
        {"kind": "hermite", "stage": "match", "t": t, "caption": "The cubic matching those four conditions."},
        _hermite_rd(p0, p1, t0, t1, t, "intro", {
            "caption": "Lengthen a tangent and the curve overshoots; shorten it and the curve flattens.",
        }),
        {"C(0)": _fmt(p0), "C(1)": _fmt(p1)},
    ))

    steps.append(_step(
        3, "Not a Bézier — but equivalent to one",
        "Hermite inputs:      P0, P1, T0, T1\n"
        "Equivalent Bézier:   P0,  P0 + T0/3,  P1 − T1/3,  P1",
        "The two cubics are the same polynomial written in different bases.  "
        "Bézier hides the derivatives inside off-curve handles; Hermite "
        "exposes them.  Use Hermite when the derivatives are the thing you "
        "want to edit (motion, a joining G¹ spline).  Use Bézier when the "
        "shape of a control polygon is the thing you want to edit.",
        {"kind": "hermite", "stage": "equiv", "t": t, "caption": "Ghosted Bézier handles P0+T0/3 and P1−T1/3."},
        _hermite_rd(p0, p1, t0, t1, t, "intro", {
            "show_equiv_bezier": True,
            "caption": "Dashed: the equivalent Bézier polygon.  Same curve, different knobs.",
        }),
        {"C(t)": _fmt(ct)},
    ))
    return steps


def hermite_math_steps(p0, p1, t0, t1, t) -> List[VisualizationStep]:
    h0, h1, h2, h3 = hermite_basis(t)
    ct = hermite_point(p0, p1, t0, t1, t)
    xs = linspace(0.0, 1.0, 80)
    series = list(zip(*[hermite_basis(x) for x in xs]))
    plot = _basis_plot("Hermite basis  H₀ H₁ H₂ H₃", xs, series, t, ["H0", "H1", "H2", "H3"])
    steps = []

    steps.append(_step(
        1, "Four blending functions",
        "H0(t) =  2t³ − 3t² + 1\n"
        "H1(t) = −2t³ + 3t²\n"
        "H2(t) =   t³ − 2t² + t\n"
        "H3(t) =   t³ −  t²\n\n"
        f"At t = {t:.2f}:  H0={h0:.3f}  H1={h1:.3f}  H2={h2:.3f}  H3={h3:.3f}",
        "H0 and H1 blend the two positions (they form a smooth step from 1 "
        "to 0 and 0 to 1).  H2 and H3 blend the two tangents; they are zero "
        "at both ends so they do not disturb the positions, but their "
        "derivatives are 1 and 0 (or 0 and 1) at the ends, which is how the "
        "tangents get copied onto C'.",
        {"kind": "hermite", "stage": "basis", "t": t, "H": (h0, h1, h2, h3),
         "caption": "H0, H1 mix positions; H2, H3 mix tangents."},
        _hermite_rd(p0, p1, t0, t1, t, "math", {
            "basis_plot": plot,
            "caption": "Read the plot: H0 starts at 1, H1 ends at 1, H2/H3 are the tangent bumps.",
        }),
        {"H0": f"{h0:.3f}", "H1": f"{h1:.3f}", "H2": f"{h2:.3f}", "H3": f"{h3:.3f}"},
    ))

    steps.append(_step(
        2, "The cubic",
        f"C(t) = H0(t) P0 + H1(t) P1 + H2(t) T0 + H3(t) T1\n\n"
        f"     = {h0:.3f}·{_fmt(p0)} + {h1:.3f}·{_fmt(p1)}\n"
        f"       + {h2:.3f}·{_fmt(t0)} + {h3:.3f}·{_fmt(t1)}\n"
        f"     = {_fmt(ct)}",
        "This is a linear combination, but not a convex combination of the "
        "four inputs: H3(t) = t²(t−1) is negative on (0, 1), so a tangent "
        "can push the curve off the segment P0P1.  Bernstein weights never "
        "go negative — that is a real difference between Hermite and Bézier.",
        {"kind": "hermite", "stage": "eval", "t": t, "curve_point": ct, "caption": f"C({t:.2f}) = {_fmt(ct)}"},
        _hermite_rd(p0, p1, t0, t1, t, "math", {
            "basis_plot": plot,
            "caption": f"C({t:.2f}) = {_fmt(ct)}",
        }),
        {"C(t)": _fmt(ct)},
    ))

    d0 = hermite_derivative(p0, p1, t0, t1, 0.0)
    d1 = hermite_derivative(p0, p1, t0, t1, 1.0)
    steps.append(_step(
        3, "Check the four Hermite conditions",
        f"C(0)  = {_fmt(p0)}    (required P0)\n"
        f"C(1)  = {_fmt(p1)}    (required P1)\n"
        f"C'(0) = {_fmt(d0)}    (required T0 = {_fmt(t0)})\n"
        f"C'(1) = {_fmt(d1)}    (required T1 = {_fmt(t1)})",
        "These four identities are why the basis looks the way it does.  "
        "They are also the test the engine uses: if you drag a tangent and "
        "C' at that end does not match, the visualisation would be lying.  "
        "It does match — the arrows on the canvas are C'(0) and C'(1).",
        {"kind": "hermite", "stage": "verify", "t": t, "caption": "The four interpolation conditions hold."},
        _hermite_rd(p0, p1, t0, t1, t, "math", {
            "basis_plot": plot,
            "caption": "Arrows are C'(0)=T0 and C'(1)=T1, not decorations.",
        }),
        {"match_T0": dist(d0, t0) < 1e-9, "match_T1": dist(d1, t1) < 1e-9},
    ))

    bez = hermite_to_bezier(p0, p1, t0, t1)
    steps.append(_step(
        4, "Change of basis to Bézier",
        "P0_bez = P0\n"
        "P1_bez = P0 + T0 / 3\n"
        "P2_bez = P1 − T1 / 3\n"
        "P3_bez = P1\n\n"
        f"equivalent polygon: {_fmt(bez[0])}, {_fmt(bez[1])}, {_fmt(bez[2])}, {_fmt(bez[3])}",
        "The factor 1/3 comes from C'(0) = 3 (P1_bez − P0) for a cubic "
        "Bézier, so T0 = 3 (P1_bez − P0)  ⇒  P1_bez = P0 + T0/3.  The two "
        "lessons are consistent: evaluating this Bézier with De Casteljau "
        "gives the same points as the Hermite formula.",
        {"kind": "hermite", "stage": "change_of_basis", "t": t, "caption": "Same cubic, Bézier handles shown dashed."},
        _hermite_rd(p0, p1, t0, t1, t, "math", {
            "show_equiv_bezier": True,
            "basis_plot": plot,
            "caption": "Dashed polygon is the equivalent cubic Bézier.",
        }),
        {"factor": "1/3"},
    ))
    return steps


def hermite_experiment_steps(p0, p1, t0, t1, t_focus) -> List[VisualizationStep]:
    xs = linspace(0.0, 1.0, 80)
    series = list(zip(*[hermite_basis(x) for x in xs]))
    steps = []
    ts = linspace(0.0, 1.0, SWEEP_FRAMES)
    for i, t in enumerate(ts):
        h0, h1, h2, h3 = hermite_basis(t)
        ct = hermite_point(p0, p1, t0, t1, t)
        plot = _basis_plot("H₀ H₁ H₂ H₃", xs, series, t, ["H0", "H1", "H2", "H3"])
        caption = f"t = {t:.2f}   C(t) = {_fmt(ct)}"
        steps.append(_step(
            i + 1, f"Sweep  t = {t:.2f}",
            f"C({t:.2f}) = {_fmt(ct)}\n"
            f"H0={h0:.3f}  H1={h1:.3f}  H2={h2:.3f}  H3={h3:.3f}",
            "Drag P0 or P1 to move an endpoint.  Drag an arrowhead to change "
            "that tangent's direction and length.  Magnitude is part of the "
            "mathematics: it is C' at the endpoint, not a cosmetic scale.",
            {"kind": "hermite", "stage": "experiment", "t": t, "curve_point": ct,
             "p0": p0, "p1": p1, "t0": t0, "t1": t1, "caption": caption},
            _hermite_rd(p0, p1, t0, t1, t, "experiment", {
                "basis_plot": plot,
                "caption": caption,
            }),
            {"t": f"{t:.2f}", "C(t)": _fmt(ct)},
        ))
    return steps


# ===========================================================================
# Public dispatcher
# ===========================================================================

def generate_curve_steps(topic_key: str, values: Dict, tab: str = "") -> List[VisualizationStep]:
    """Build the lesson steps for a Curves topic and the active lesson tab."""
    if topic_key == "curve_bezier":
        points = control_points_from_values(values, 4, DEFAULT_BEZIER)
        t = _param_t(values, "t", 0.35)
        tab = tab or "stage1"
        if tab in ("stage1", "intro"):
            return bezier_stage1_steps(points, t)
        if tab in ("stage2", "lerp"):
            pt_a = _pt(values.get("ax", values.get("p0x", DEFAULT_LERP_A[0])), values.get("ay", values.get("p0y", DEFAULT_LERP_A[1])))
            pt_b = _pt(values.get("bx", values.get("p3x", DEFAULT_LERP_B[0])), values.get("by", values.get("p3y", DEFAULT_LERP_B[1])))
            return bezier_stage2_steps(pt_a, pt_b, t)
        if tab in ("stage3", "casteljau"):
            return bezier_stage3_steps(points, t)
        if tab in ("stage4", "experiment"):
            return bezier_stage4_steps(points, t)
        if tab in ("stage5", "quiz"):
            return bezier_stage5_steps()
        if tab == "math":
            return bezier_math_steps(points, t)
        return bezier_stage1_steps(points, t)

    if topic_key == "curve_bspline":
        points = control_points_from_values(values, 5, DEFAULT_BSPLINE)
        degree = parse_degree(values.get("degree", 3))
        style = parse_knot_style(values.get("knot_style", "Clamped uniform"))
        u = _param_t(values, "u", 0.45)
        if degree >= len(points):
            raise ValueError(f"Degree {degree} needs at least {degree + 1} control points.")
        tab = tab or "intro"
        if tab == "math":
            return bspline_math_steps(points, degree, style, u)
        if tab == "experiment":
            return bspline_experiment_steps(points, degree, style, u)
        return bspline_intro_steps(points, degree, style, u)

    if topic_key == "curve_hermite":
        p0 = _pt(values.get("p0x", DEFAULT_HERMITE_P0[0]), values.get("p0y", DEFAULT_HERMITE_P0[1]))
        p1 = _pt(values.get("p1x", DEFAULT_HERMITE_P1[0]), values.get("p1y", DEFAULT_HERMITE_P1[1]))
        t0 = _pt(values.get("t0x", DEFAULT_HERMITE_T0[0]), values.get("t0y", DEFAULT_HERMITE_T0[1]))
        t1 = _pt(values.get("t1x", DEFAULT_HERMITE_T1[0]), values.get("t1y", DEFAULT_HERMITE_T1[1]))
        t = _param_t(values, "t", 0.35)
        tab = tab or "intro"
        if tab == "math":
            return hermite_math_steps(p0, p1, t0, t1, t)
        if tab == "experiment":
            return hermite_experiment_steps(p0, p1, t0, t1, t)
        return hermite_intro_steps(p0, p1, t0, t1, t)

    raise ValueError(f"Unknown curve topic '{topic_key}'.")


def tabs_for_topic(topic_key: str) -> List[Tuple[str, str, str]]:
    if topic_key == "curve_bezier":
        return BEZIER_TABS
    if topic_key == "curve_bspline":
        return BSPLINE_TABS
    if topic_key == "curve_hermite":
        return HERMITE_TABS
    return []


def default_tab(topic_key: str) -> str:
    tabs = tabs_for_topic(topic_key)
    return tabs[0][0] if tabs else ""
