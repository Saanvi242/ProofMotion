"""
theorems/similar_triangles.py
-----------------------------
Mathematical and geometric demonstration of Similar Triangles:
ΔABC ~ ΔA'B'C'

Demonstrates proportional side lengths (a'/a = b'/b = c'/c = k)
and equality of corresponding angles, plus the quadratic area scaling Area' = k² · Area.
"""

import math
import numpy as np
import sympy as sp
from typing import List, Tuple, Dict, Any

from models.theorem_state import Theorem, ParameterSpec, ParameterType, ProofStep
from core.step_model import RenderData, Point2D, Line2D, Polygon2D, Text2D, Arc2D
from cgip.transformations import scaling_matrix, translation_matrix, compose_transformations, apply_transform


def get_theorem_spec() -> Theorem:
    return Theorem(
        key="similar_triangles",
        display_name="Similar Triangles",
        short_description="Two triangles are similar if their corresponding angles are congruent and corresponding sides are proportional.",
        parameters=[
            ParameterSpec("side_a", "Side A (base)", ParameterType.LENGTH, default=6.0, min_value=1.0, max_value=30.0, suffix="cm"),
            ParameterSpec("side_b", "Side B", ParameterType.LENGTH, default=8.0, min_value=1.0, max_value=30.0, suffix="cm"),
            ParameterSpec("ratio", "Scale Ratio (k)", ParameterType.RATIO, default=1.5, min_value=0.2, max_value=5.0, suffix="×"),
        ],
        steps=[],
        final_result_template="Similarity verified: a'/a = b'/b = c'/c = {k:.2f}, Area ratio = {k_sq:.2f} (k²)",
    )


def validate_parameters(values: Dict[str, float]) -> Tuple[bool, str]:
    a = values.get("side_a", 0)
    b = values.get("side_b", 0)
    k = values.get("ratio", 0)
    if a <= 0:
        return False, "Side A must be greater than 0."
    if b <= 0:
        return False, "Side B must be greater than 0."
    if k <= 0:
        return False, "Scale ratio k must be greater than 0."
    return True, ""


def compute_final_result(values: Dict[str, float]) -> str:
    k = float(values.get("ratio", 1.5))
    return f"Similarity verified: a'/a = b'/b = c'/c = {k:.2f}, Area ratio = {k*k:.2f} (k²)"


def generate_proof_steps(values: Dict[str, float]) -> List[ProofStep]:
    a = float(values.get("side_a", 6.0))
    b = float(values.get("side_b", 8.0))
    k = float(values.get("ratio", 1.5))

    # Construct triangle ABC with vertices:
    # C at (0, 0)
    # B at (a, 0)
    # A at (b * cos(gamma), b * sin(gamma)) with angle gamma = 60 degrees (pi/3)
    gamma_deg = 50.0
    gamma_rad = math.radians(gamma_deg)

    Ax = b * math.cos(gamma_rad)
    Ay = b * math.sin(gamma_rad)
    Bx = a
    By = 0.0
    Cx = 0.0
    Cy = 0.0

    # Side c (opposite to vertex C, between A and B)
    c = math.hypot(Ax - Bx, Ay - By)

    # Angles using law of cosines:
    alpha_rad = math.acos(np.clip((b**2 + c**2 - a**2) / (2 * b * c), -1.0, 1.0))
    beta_rad = math.acos(np.clip((a**2 + c**2 - b**2) / (2 * a * c), -1.0, 1.0))
    alpha_deg = math.degrees(alpha_rad)
    beta_deg = math.degrees(beta_rad)

    # Scaled triangle A'B'C'
    a_prime = a * k
    b_prime = b * k
    c_prime = c * k

    area_orig = 0.5 * a * b * math.sin(gamma_rad)
    area_scaled = area_orig * k * k

    steps = []

    # -------------------------------------------------------------
    # Step 1: Base Triangle ΔABC
    # -------------------------------------------------------------
    rd1 = RenderData(view_bounds=(-1, -1, max(a, b) + 2, max(a, b) + 2))
    rd1.polygons.append(Polygon2D(
        points=[(Cx, Cy), (Bx, By), (Ax, Ay)],
        fill_color="rgba(91, 141, 239, 0.28)",
        stroke_color="#5B8DEF",
        stroke_width=2.5,
        label="ΔABC"
    ))
    rd1.points.extend([
        Point2D(Cx, Cy, label="C", color="#EAF0F6"),
        Point2D(Bx, By, label="B", color="#EAF0F6"),
        Point2D(Ax, Ay, label="A", color="#EAF0F6"),
    ])
    rd1.texts.extend([
        Text2D(a / 2.0, -0.4, f"a = {a:.1f}", color="#5B8DEF", font_size=10, bold=True),
        Text2D(Ax / 2.0 - 0.4, Ay / 2.0 + 0.2, f"b = {b:.1f}", color="#5B8DEF", font_size=10, bold=True),
        Text2D((Ax + Bx) / 2.0 + 0.4, (Ay + By) / 2.0, f"c = {c:.2f}", color="#5B8DEF", font_size=10, bold=True),
    ])

    steps.append(ProofStep(
        index=1,
        equation=f"ΔABC: a = {a:.1f} cm, b = {b:.1f} cm, c = {c:.2f} cm,  Area = {area_orig:.2f} cm²",
        explanation=f"Construct reference triangle ΔABC with side lengths a = {a:.1f} cm, b = {b:.1f} cm, and c = {c:.2f} cm. "
                    f"Angles: ∠A = {alpha_deg:.1f}°, ∠B = {beta_deg:.1f}°, ∠C = {gamma_deg:.1f}°.",
        values={"a": a, "b": b, "c": round(c, 2), "∠A": round(alpha_deg, 1), "∠B": round(beta_deg, 1), "∠C": round(gamma_deg, 1)},
        render_data=rd1
    ))

    # -------------------------------------------------------------
    # Step 2: Scaled Triangle ΔA'B'C' (Side-by-Side via CGIP Transform Engine)
    # -------------------------------------------------------------
    # Offset scaled triangle to the right
    offset_x = a + 2.0

    # Genuine CGIP 2D Homogeneous Transformation: S(k, k) then T(offset_x, 0)
    s_mat = scaling_matrix(k, k)
    t_mat = translation_matrix(offset_x, 0.0)
    m_composite = compose_transformations(s_mat, t_mat) # T @ S

    scaled_transformed_pts = apply_transform(m_composite, [(Cx, Cy), (Bx, By), (Ax, Ay)])
    (C_px, C_py), (B_px, B_py), (A_px, A_py) = scaled_transformed_pts

    max_w = offset_x + a_prime + 2.0
    max_h = max(Ay, A_py) + 2.0
    rd2 = RenderData(view_bounds=(-1, -1, max_w, max_h))

    # ΔABC (Original)
    rd2.polygons.append(Polygon2D(
        points=[(Cx, Cy), (Bx, By), (Ax, Ay)],
        fill_color="rgba(91, 141, 239, 0.25)",
        stroke_color="#5B8DEF",
        stroke_width=2.0,
        label="ΔABC (1×)"
    ))
    # ΔA'B'C' (Scaled via CGIP matrix)
    rd2.polygons.append(Polygon2D(
        points=[(C_px, C_py), (B_px, B_py), (A_px, A_py)],
        fill_color="rgba(78, 199, 176, 0.35)",
        stroke_color="#4EC7B0",
        stroke_width=2.5,
        label=f"ΔA'B'C' ({k:.2f}×)"
    ))

    rd2.points.extend([
        Point2D(C_px, C_py, label="C'", color="#4EC7B0"),
        Point2D(B_px, B_py, label="B'", color="#4EC7B0"),
        Point2D(A_px, A_py, label="A'", color="#4EC7B0"),
    ])

    rd2.texts.extend([
        Text2D(offset_x + a_prime / 2.0, -0.4, f"a' = {a_prime:.1f}", color="#4EC7B0", font_size=10, bold=True),
        Text2D(offset_x + (Ax * k) / 2.0 - 0.5, (Ay * k) / 2.0 + 0.2, f"b' = {b_prime:.1f}", color="#4EC7B0", font_size=10, bold=True),
        Text2D(offset_x + (Ax * k + Bx * k) / 2.0 + 0.5, (Ay * k + By * k) / 2.0, f"c' = {c_prime:.2f}", color="#4EC7B0", font_size=10, bold=True),
    ])

    steps.append(ProofStep(
        index=2,
        equation=f"Scaling with k = {k:.2f}: a' = {a_prime:.2f}, b' = {b_prime:.2f}, c' = {c_prime:.2f}",
        explanation=f"Construct second triangle ΔA'B'C' by multiplying each side of ΔABC by uniform scale factor k = {k:.2f}. "
                    f"a' = k·a = {a_prime:.2f} cm, b' = k·b = {b_prime:.2f} cm, c' = k·c = {c_prime:.2f} cm.",
        values={"k": k, "a'": round(a_prime, 2), "b'": round(b_prime, 2), "c'": round(c_prime, 2)},
        render_data=rd2
    ))

    # -------------------------------------------------------------
    # Step 3: Congruence of Corresponding Angles
    # -------------------------------------------------------------
    # Draw them overlaid sharing vertex C at origin
    max_coord = max(a_prime, b_prime, a, b) + 2.0
    rd3 = RenderData(view_bounds=(-1, -1, max_coord, max_coord))

    # Scaled larger/smaller in background via CGIP scaling matrix
    overlaid_scaled_pts = apply_transform(s_mat, [(0.0, 0.0), (Bx, By), (Ax, Ay)])
    rd3.polygons.append(Polygon2D(
        points=overlaid_scaled_pts,
        fill_color="rgba(78, 199, 176, 0.22)",
        stroke_color="#4EC7B0",
        stroke_width=2.0,
        label="ΔA'B'C'"
    ))
    # Original overlaid
    rd3.polygons.append(Polygon2D(
        points=[(0, 0), (Bx, By), (Ax, Ay)],
        fill_color="rgba(216, 169, 78, 0.35)",
        stroke_color="#D8A94E",
        stroke_width=2.5,
        label="ΔABC"
    ))

    # Shared angle C arc at origin
    arc_r = min(a, b) * 0.25
    rd3.arcs.append(Arc2D(0, 0, arc_r, 0, gamma_deg, color="#D8A94E", label=f"∠C = {gamma_deg:.1f}°"))

    rd3.texts.append(
        Text2D(max_coord / 2.0, max_coord - 0.8, f"Corresponding Angles: ∠A = ∠A' = {alpha_deg:.1f}°, ∠B = ∠B' = {beta_deg:.1f}°, ∠C = ∠C' = {gamma_deg:.1f}°", color="#EAF0F6", font_size=10, bold=True)
    )

    steps.append(ProofStep(
        index=3,
        equation=f"Angle Invariance: ∠A = ∠A' = {alpha_deg:.1f}°,  ∠B = ∠B' = {beta_deg:.1f}°,  ∠C = ∠C' = {gamma_deg:.1f}°",
        explanation="When overlaid, corresponding angles match exactly. Uniform geometric dilation preserves angle measures, "
                    "satisfying the AAA (Angle-Angle-Angle) similarity criterion.",
        values={"∠A": round(alpha_deg, 1), "∠B": round(beta_deg, 1), "∠C": round(gamma_deg, 1)},
        render_data=rd3
    ))

    # -------------------------------------------------------------
    # Step 4: Proportional Ratios and Area Verification
    # -------------------------------------------------------------
    rd4 = RenderData(view_bounds=(-1, -1, max_coord, max_coord))
    rd4.polygons.append(Polygon2D(
        points=[(0, 0), (Bx * k, By * k), (Ax * k, Ay * k)],
        fill_color="rgba(89, 196, 138, 0.28)",
        stroke_color="#59C48A",
        stroke_width=2.5,
        label=f"Area' = {area_scaled:.2f} cm²"
    ))
    rd4.polygons.append(Polygon2D(
        points=[(0, 0), (Bx, By), (Ax, Ay)],
        fill_color="rgba(216, 169, 78, 0.4)",
        stroke_color="#D8A94E",
        stroke_width=2.0,
        label=f"Area = {area_orig:.2f} cm²"
    ))

    rd4.texts.extend([
        Text2D(max_coord / 2.0, max_coord - 0.5, f"a'/a = {a_prime:.1f}/{a:.1f} = {k:.2f} | b'/b = {b_prime:.1f}/{b:.1f} = {k:.2f} | c'/c = {c_prime:.2f}/{c:.2f} = {k:.2f}", color="#59C48A", font_size=11, bold=True),
        Text2D(max_coord / 2.0, max_coord - 1.2, f"Area' / Area = {area_scaled:.2f} / {area_orig:.2f} = {k*k:.2f} = k²", color="#D8A94E", font_size=10, bold=True),
    ])

    steps.append(ProofStep(
        index=4,
        equation=f"a'/a = b'/b = c'/c = {k:.2f},   Area(ΔA'B'C') / Area(ΔABC) = k² = {k*k:.2f}",
        explanation=f"All corresponding side ratios are strictly equal to the scale factor k = {k:.2f}. "
                    f"Furthermore, the area scales quadratically by k² = {k*k:.2f} (Area = {area_orig:.2f} cm² ⟹ Area' = {area_scaled:.2f} cm²).",
        values={"ratio_a": round(a_prime / a, 4), "ratio_b": round(b_prime / b, 4), "ratio_c": round(c_prime / c, 4), "area_ratio": round(k * k, 4)},
        render_data=rd4
    ))

    return steps
