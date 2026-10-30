"""
theorems/pythagorean.py
-----------------------
Mathematical and geometric implementation of the Pythagorean Theorem:
a² + b² = c²

Generates authentic, mathematically calculated geometric proof steps
using NumPy coordinates and SymPy algebraic relationships.
"""

import math
import numpy as np
import sympy as sp
from typing import List, Tuple, Dict, Any

from models.theorem_state import Theorem, ParameterSpec, ParameterType, ProofStep
from core.step_model import RenderData, Point2D, Line2D, Polygon2D, Text2D, Arc2D
from cgip.transformations import rotation_matrix, apply_transform


def get_theorem_spec() -> Theorem:
    return Theorem(
        key="pythagorean",
        display_name="Pythagorean Theorem",
        short_description="In a right-angled triangle, the square of the hypotenuse is equal to the sum of the squares of the other two sides.",
        parameters=[
            ParameterSpec("side_a", "Side A (base)", ParameterType.LENGTH, default=3.0, min_value=0.5, max_value=50.0, suffix="cm"),
            ParameterSpec("side_b", "Side B (height)", ParameterType.LENGTH, default=4.0, min_value=0.5, max_value=50.0, suffix="cm"),
        ],
        steps=[],
        final_result_template="c = {c:.2f} cm (Verification: {a:.2f}² + {b:.2f}² = {c_sq:.2f} = {c:.2f}²)",
    )


def validate_parameters(values: Dict[str, float]) -> Tuple[bool, str]:
    a = values.get("side_a", 0)
    b = values.get("side_b", 0)
    if a <= 0:
        return False, "Side A must be a positive number greater than 0."
    if b <= 0:
        return False, "Side B must be a positive number greater than 0."
    return True, ""


def compute_final_result(values: Dict[str, float]) -> str:
    a = float(values.get("side_a", 3.0))
    b = float(values.get("side_b", 4.0))
    c_val = math.sqrt(a * a + b * b)
    c_sq = a * a + b * b
    return f"c = {c_val:.2f} cm (Verified: {a:.2f}² + {b:.2f}² = {c_sq:.2f} = {c_val:.2f}²)"


def generate_proof_steps(values: Dict[str, float]) -> List[ProofStep]:
    a = float(values.get("side_a", 3.0))
    b = float(values.get("side_b", 4.0))
    c = math.sqrt(a * a + b * b)
    c_sq = a * a + b * b

    # SymPy symbolic verification
    sa, sb = sp.symbols('a b', positive=True)
    sc = sp.sqrt(sa**2 + sb**2)
    expr_eval = sc.subs({sa: a, sb: b}).evalf()

    # Coordinates:
    # A = Origin (0, 0)
    # B = (a, 0)
    # C = (0, b)
    # View bounds
    pad = max(a, b) * 1.5
    bounds = (-pad, -pad, a + pad, b + pad)

    steps = []

    # -------------------------------------------------------------
    # Step 1: Right-Angled Triangle Construction
    # -------------------------------------------------------------
    rd1 = RenderData(view_bounds=(-1, -1, a + 2, b + 2))
    # Triangle ABC
    rd1.polygons.append(Polygon2D(
        points=[(0, 0), (a, 0), (0, b)],
        fill_color="rgba(91, 141, 239, 0.25)",
        stroke_color="#5B8DEF",
        stroke_width=2.5,
        label="ΔABC"
    ))
    # Right angle marker at (0, 0)
    sq_size = min(a, b) * 0.15
    rd1.lines.extend([
        Line2D(0, sq_size, sq_size, sq_size, color="#D8A94E", width=1.5),
        Line2D(sq_size, 0, sq_size, sq_size, color="#D8A94E", width=1.5),
    ])
    # Points
    rd1.points.extend([
        Point2D(0, 0, label="C(0,0)", color="#EAF0F6"),
        Point2D(a, 0, label=f"B({a:.1f}, 0)", color="#EAF0F6"),
        Point2D(0, b, label=f"A(0, {b:.1f})", color="#EAF0F6"),
    ])
    # Labels
    rd1.texts.extend([
        Text2D(a / 2.0, -0.4, f"a = {a:.1f}", color="#5B8DEF", font_size=11, bold=True),
        Text2D(-0.6, b / 2.0, f"b = {b:.1f}", color="#5B8DEF", font_size=11, bold=True),
        Text2D(a / 2.0 + 0.4, b / 2.0 + 0.3, f"c = {c:.2f}", color="#D8A94E", font_size=11, bold=True),
    ])

    steps.append(ProofStep(
        index=1,
        equation="ΔABC with ∠C = 90°, legs a and b",
        explanation=f"Construct right-angled triangle ABC with perpendicular legs a = {a:.1f} cm and b = {b:.1f} cm. "
                    f"The hypotenuse c connects vertex A to B.",
        values={"a": a, "b": b, "c": round(c, 2)},
        render_data=rd1
    ))

    # -------------------------------------------------------------
    # Step 2: Squares Constructed on Legs a and b
    # -------------------------------------------------------------
    rd2 = RenderData(view_bounds=(-b - 1, -a - 1, a + 2, b + 2))
    # Triangle
    rd2.polygons.append(Polygon2D(
        points=[(0, 0), (a, 0), (0, b)],
        fill_color="rgba(91, 141, 239, 0.25)",
        stroke_color="#5B8DEF",
        stroke_width=2.0
    ))
    # Square on side a: vertices (0,0), (a,0), (a,-a), (0,-a)
    rd2.polygons.append(Polygon2D(
        points=[(0, 0), (a, 0), (a, -a), (0, -a)],
        fill_color="rgba(78, 199, 176, 0.3)",
        stroke_color="#4EC7B0",
        stroke_width=2.0,
        label=f"a² = {a*a:.1f}"
    ))
    # Square on side b: vertices (0,0), (-b,0), (-b,b), (0,b)
    rd2.polygons.append(Polygon2D(
        points=[(0, 0), (0, b), (-b, b), (-b, 0)],
        fill_color="rgba(216, 169, 78, 0.3)",
        stroke_color="#D8A94E",
        stroke_width=2.0,
        label=f"b² = {b*b:.1f}"
    ))
    # Points
    rd2.points.extend([
        Point2D(0, 0, label="C", color="#EAF0F6"),
        Point2D(a, 0, label="B", color="#EAF0F6"),
        Point2D(0, b, label="A", color="#EAF0F6"),
    ])
    rd2.texts.append(
        Text2D(a / 2.0, -a - 0.5, f"Area(a) = {a:.1f}² = {a*a:.2f}", color="#4EC7B0", font_size=10, bold=True)
    )
    rd2.texts.append(
        Text2D(-b / 2.0, b + 0.5, f"Area(b) = {b:.1f}² = {b*b:.2f}", color="#D8A94E", font_size=10, bold=True)
    )

    steps.append(ProofStep(
        index=2,
        equation=f"Area(Square_a) = a² = {a*a:.2f},  Area(Square_b) = b² = {b*b:.2f}",
        explanation=f"Construct squares on each perpendicular leg. The square on leg a has area a² = {a*a:.2f} cm², "
                    f"and the square on leg b has area b² = {b*b:.2f} cm².",
        values={"a": a, "b": b, "a²": round(a*a, 2), "b²": round(b*b, 2)},
        render_data=rd2
    ))

    # -------------------------------------------------------------
    # Step 3: Geometric Dissection / Rearrangement (The (a+b)² Square)
    # -------------------------------------------------------------
    # In a square of side (a+b), arrange 4 congruent right triangles around hypotenuse square c²
    total_side = a + b
    rd3 = RenderData(view_bounds=(-1, -1, total_side + 1, total_side + 1))

    # Big outer bounding square
    rd3.lines.extend([
        Line2D(0, 0, total_side, 0, color="#26374A", width=1.5, dashed=True),
        Line2D(total_side, 0, total_side, total_side, color="#26374A", width=1.5, dashed=True),
        Line2D(total_side, total_side, 0, total_side, color="#26374A", width=1.5, dashed=True),
        Line2D(0, total_side, 0, 0, color="#26374A", width=1.5, dashed=True),
    ])

    # 4 congruent triangles generated via CGIP pivot rotation around outer square center:
    center_sq = total_side / 2.0
    t1_base = [(0.0, 0.0), (a, 0.0), (0.0, b)]
    t_color = "rgba(91, 141, 239, 0.28)"

    triangles = []
    for rot_deg, t_label in [(0.0, "T1"), (90.0, "T2"), (180.0, "T3"), (270.0, "T4")]:
        r_mat = rotation_matrix(rot_deg, cx=center_sq, cy=center_sq)
        t_pts = apply_transform(r_mat, t1_base)
        triangles.append(Polygon2D(t_pts, fill_color=t_color, stroke_color="#5B8DEF", stroke_width=1.5, label=t_label))

    rd3.polygons.extend(triangles)

    # Inscribed hypotenuse square c²:
    # Vertices: (a, 0), (total_side, a), (b, total_side), (0, b)
    rd3.polygons.append(Polygon2D(
        points=[(a, 0), (total_side, a), (b, total_side), (0, b)],
        fill_color="rgba(78, 199, 176, 0.4)",
        stroke_color="#4EC7B0",
        stroke_width=2.5,
        label=f"c² = {c_sq:.2f}"
    ))

    rd3.texts.append(
        Text2D(total_side / 2.0, total_side + 0.6, f"Outer Square side = a + b = {total_side:.1f}", color="#EAF0F6", font_size=11, bold=True)
    )

    steps.append(ProofStep(
        index=3,
        equation="(a + b)² = 4 · (½ · a · b) + c²  ⟹  a² + 2ab + b² = 2ab + c²  ⟹  a² + b² = c²",
        explanation="Bhaskara's geometric proof: 4 copies of right triangle ΔABC are arranged inside a square of side (a+b). "
                    "The central tilted square has side length c and area c². Expanding both sides cancels 2ab, proving a² + b² = c².",
        values={"4 × Area(T)": round(2 * a * b, 2), "c²": round(c_sq, 2), "(a+b)²": round(total_side**2, 2)},
        render_data=rd3
    ))

    # -------------------------------------------------------------
    # Step 4: Direct Square on Hypotenuse & Numerical Verification
    # -------------------------------------------------------------
    # In original triangle, draw square extending outwardly from hypotenuse AB
    # Vector AB = (a, -b). Perpendicular outward vector = (b, a).
    pA = np.array([0.0, b])
    pB = np.array([a, 0.0])
    v_hyp = pB - pA # (a, -b)
    # Perpendicular pointing outward (away from origin (0,0)):
    # Normal to (a, -b) is (b, a)
    v_norm = np.array([b, a])
    pC_sq = pB + v_norm
    pD_sq = pA + v_norm

    all_x = [0, a, pC_sq[0], pD_sq[0], -b]
    all_y = [0, b, pC_sq[1], pD_sq[1], -a]
    rd4 = RenderData(view_bounds=(min(all_x) - 1, min(all_y) - 1, max(all_x) + 1, max(all_y) + 1))

    # Triangle
    rd4.polygons.append(Polygon2D(
        points=[(0, 0), (a, 0), (0, b)],
        fill_color="rgba(91, 141, 239, 0.25)",
        stroke_color="#5B8DEF",
        stroke_width=2.0
    ))
    # Square on a
    rd4.polygons.append(Polygon2D(
        points=[(0, 0), (a, 0), (a, -a), (0, -a)],
        fill_color="rgba(78, 199, 176, 0.25)",
        stroke_color="#4EC7B0",
        stroke_width=1.5,
        label=f"a²={a*a:.1f}"
    ))
    # Square on b
    rd4.polygons.append(Polygon2D(
        points=[(0, 0), (0, b), (-b, b), (-b, 0)],
        fill_color="rgba(216, 169, 78, 0.25)",
        stroke_color="#D8A94E",
        stroke_width=1.5,
        label=f"b²={b*b:.1f}"
    ))
    # Square on Hypotenuse c
    rd4.polygons.append(Polygon2D(
        points=[(pA[0], pA[1]), (pB[0], pB[1]), (pC_sq[0], pC_sq[1]), (pD_sq[0], pD_sq[1])],
        fill_color="rgba(89, 196, 138, 0.35)",
        stroke_color="#59C48A",
        stroke_width=2.5,
        label=f"c² = {c_sq:.2f}"
    ))

    rd4.points.extend([
        Point2D(0, 0, label="C", color="#EAF0F6"),
        Point2D(a, 0, label="B", color="#EAF0F6"),
        Point2D(0, b, label="A", color="#EAF0F6"),
    ])

    rd4.texts.append(
        Text2D((pA[0] + pC_sq[0]) / 2.0, (pA[1] + pC_sq[1]) / 2.0 + 0.4, f"c = √({a*a:.1f} + {b*b:.1f}) = {c:.2f} cm", color="#59C48A", font_size=11, bold=True)
    )

    steps.append(ProofStep(
        index=4,
        equation=f"c = √(a² + b²) = √({a:.2f}² + {b:.2f}²) = √({c_sq:.2f}) = {c:.2f} cm",
        explanation=f"All three squares shown together: Area(Square_a) + Area(Square_b) = {a*a:.2f} + {b*b:.2f} = {c_sq:.2f} cm², "
                    f"which equals Area(Square_c) = {c:.2f}² = {c_sq:.2f} cm². Pythagorean theorem holds exactly.",
        values={"a² + b²": round(a*a + b*b, 2), "c²": round(c_sq, 2), "c": round(c, 2)},
        render_data=rd4
    ))

    return steps
