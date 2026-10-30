"""
theorems/law_of_cosines.py
--------------------------
Mathematical and geometric derivation of the Law of Cosines:
c² = a² + b² - 2ab·cos(C)

Constructs the triangle, drops an altitude h = a·sin(C), expresses
the sub-segments, and applies the Pythagorean theorem to derive the general formula.
"""

import math
import numpy as np
import sympy as sp
from typing import List, Tuple, Dict, Any

from models.theorem_state import Theorem, ParameterSpec, ParameterType, ProofStep
from core.step_model import RenderData, Point2D, Line2D, Polygon2D, Text2D, Arc2D


def get_theorem_spec() -> Theorem:
    return Theorem(
        key="law_of_cosines",
        display_name="Law of Cosines",
        short_description="Generalized Pythagorean theorem for any triangle: c² = a² + b² - 2ab·cos(C).",
        parameters=[
            ParameterSpec("side_a", "Side a", ParameterType.LENGTH, default=7.0, min_value=1.0, max_value=40.0, suffix="cm"),
            ParameterSpec("side_b", "Side b", ParameterType.LENGTH, default=5.0, min_value=1.0, max_value=40.0, suffix="cm"),
            ParameterSpec("angle_c", "Angle C", ParameterType.ANGLE, default=60.0, min_value=1.0, max_value=179.0, suffix="°"),
        ],
        steps=[],
        final_result_template="c = {c:.2f} cm (Verified: c² = {c_sq:.2f} = {a:.2f}² + {b:.2f}² - 2·{a:.2f}·{b:.2f}·cos({C:.1f}°))",
    )


def validate_parameters(values: Dict[str, float]) -> Tuple[bool, str]:
    a = values.get("side_a", 0)
    b = values.get("side_b", 0)
    C_deg = values.get("angle_c", 0)
    if a <= 0:
        return False, "Side a must be greater than 0."
    if b <= 0:
        return False, "Side b must be greater than 0."
    if not (0 < C_deg < 180):
        return False, "Angle C must be between 0° and 180°."
    return True, ""


def compute_final_result(values: Dict[str, float]) -> str:
    a = float(values.get("side_a", 7.0))
    b = float(values.get("side_b", 5.0))
    C_deg = float(values.get("angle_c", 60.0))
    C_rad = math.radians(C_deg)
    c_sq = a * a + b * b - 2.0 * a * b * math.cos(C_rad)
    c_val = math.sqrt(max(0.0001, c_sq))
    return f"c = {c_val:.2f} cm (Verified: {a:.1f}² + {b:.1f}² - 2·{a:.1f}·{b:.1f}·cos({C_deg:.0f}°) = {c_sq:.2f})"


def generate_proof_steps(values: Dict[str, float]) -> List[ProofStep]:
    a = float(values.get("side_a", 7.0))
    b = float(values.get("side_b", 5.0))
    C_deg = float(values.get("angle_c", 60.0))
    C_rad = math.radians(C_deg)

    # Vertices:
    # C at origin (0, 0)
    # A at (b, 0) on the positive X-axis
    # B at (a * cos(C), a * sin(C))
    Cx, Cy = 0.0, 0.0
    Ax, Ay = b, 0.0
    Bx = a * math.cos(C_rad)
    By = a * math.sin(C_rad)

    # Foot of perpendicular dropped from B to line AC (X-axis)
    Dx = Bx
    Dy = 0.0

    # Segments
    h = By # altitude height
    CD = Bx # can be negative if C > 90°
    DA = b - Bx
    c_sq = a * a + b * b - 2.0 * a * b * math.cos(C_rad)
    c = math.sqrt(max(0.0001, c_sq))

    min_x = min(0.0, Bx, b) - 2.0
    max_x = max(0.0, Bx, b) + 2.0
    min_y = -2.0
    max_y = max(By, 2.0) + 2.0
    bounds = (min_x, min_y, max_x, max_y)

    steps = []

    # -------------------------------------------------------------
    # Step 1: Triangle Construction and Included Angle
    # -------------------------------------------------------------
    rd1 = RenderData(view_bounds=bounds)
    rd1.polygons.append(Polygon2D(
        points=[(Cx, Cy), (Ax, Ay), (Bx, By)],
        fill_color="rgba(91, 141, 239, 0.25)",
        stroke_color="#5B8DEF",
        stroke_width=2.5,
        label="ΔABC"
    ))
    rd1.points.extend([
        Point2D(Cx, Cy, label="C(0,0)", color="#EAF0F6"),
        Point2D(Ax, Ay, label=f"A({b:.1f}, 0)", color="#EAF0F6"),
        Point2D(Bx, By, label=f"B({Bx:.1f}, {By:.1f})", color="#EAF0F6"),
    ])
    # Angle C arc
    arc_rad = min(a, b) * 0.25
    rd1.arcs.append(Arc2D(0, 0, arc_rad, 0, C_deg, color="#D8A94E", label=f"C={C_deg:.1f}°"))
    # Side labels
    rd1.texts.extend([
        Text2D(b / 2.0, -0.4, f"b = {b:.1f}", color="#5B8DEF", font_size=10, bold=True),
        Text2D(Bx / 2.0 - 0.4, By / 2.0 + 0.2, f"a = {a:.1f}", color="#5B8DEF", font_size=10, bold=True),
        Text2D((Ax + Bx) / 2.0 + 0.4, (Ay + By) / 2.0, f"c = {c:.2f}", color="#D8A94E", font_size=10, bold=True),
    ])

    steps.append(ProofStep(
        index=1,
        equation=f"ΔABC: a = {a:.1f} cm,  b = {b:.1f} cm,  ∠C = {C_deg:.1f}°",
        explanation=f"Construct general triangle ABC with side a = {a:.1f} cm and side b = {b:.1f} cm "
                    f"enclosing angle ∠C = {C_deg:.1f}°. Side c is opposite to angle C.",
        values={"a": a, "b": b, "C": C_deg, "cos(C)": round(math.cos(C_rad), 4)},
        render_data=rd1
    ))

    # -------------------------------------------------------------
    # Step 2: Drop Altitude h from Vertex B
    # -------------------------------------------------------------
    rd2 = RenderData(view_bounds=bounds)
    rd2.polygons.append(Polygon2D(
        points=[(Cx, Cy), (Ax, Ay), (Bx, By)],
        fill_color="rgba(91, 141, 239, 0.2)",
        stroke_color="#5B8DEF",
        stroke_width=2.0
    ))
    # Dashed altitude line from B to D
    rd2.lines.append(Line2D(Bx, By, Dx, Dy, color="#D8A94E", width=2.5, dashed=True, label=f"h = a·sin(C) = {h:.2f}"))
    # If C > 90, extend line AC backwards
    if C_deg > 90:
        rd2.lines.append(Line2D(0, 0, Dx, Dy, color="#5F7488", width=1.5, dashed=True))

    rd2.points.extend([
        Point2D(Cx, Cy, label="C", color="#EAF0F6"),
        Point2D(Ax, Ay, label="A", color="#EAF0F6"),
        Point2D(Bx, By, label="B", color="#EAF0F6"),
        Point2D(Dx, Dy, label=f"D({Dx:.1f}, 0)", color="#D8A94E"),
    ])

    # Right angle marker at foot D
    sq_size = min(a, b) * 0.12
    rd2.lines.extend([
        Line2D(Dx, Dy + sq_size, Dx + sq_size, Dy + sq_size, color="#D8A94E", width=1.2),
        Line2D(Dx + sq_size, Dy, Dx + sq_size, Dy + sq_size, color="#D8A94E", width=1.2),
    ])

    steps.append(ProofStep(
        index=2,
        equation=f"Altitude h = a · sin(C) = {a:.1f} · sin({C_deg:.1f}°) = {h:.2f} cm",
        explanation=f"Drop perpendicular altitude from vertex B to the line containing side AC. "
                    f"In right triangle ΔCDB, the altitude is h = a · sin(C) = {h:.2f} cm.",
        values={"h": round(h, 2), "sin(C)": round(math.sin(C_rad), 4)},
        render_data=rd2
    ))

    # -------------------------------------------------------------
    # Step 3: Segment Decompositions (CD and DA)
    # -------------------------------------------------------------
    rd3 = RenderData(view_bounds=bounds)
    # Highlight right sub-triangle ΔBDA
    rd3.polygons.append(Polygon2D(
        points=[(Dx, Dy), (Ax, Ay), (Bx, By)],
        fill_color="rgba(78, 199, 176, 0.3)",
        stroke_color="#4EC7B0",
        stroke_width=2.5,
        label="Right ΔBDA"
    ))
    # Original ΔCDB in faint blue
    rd3.polygons.append(Polygon2D(
        points=[(Cx, Cy), (Dx, Dy), (Bx, By)],
        fill_color="rgba(91, 141, 239, 0.18)",
        stroke_color="#5B8DEF",
        stroke_width=1.5
    ))

    # Dimension lines along X-axis
    rd3.lines.append(Line2D(0, -0.4, Dx, -0.4, color="#D8A94E", width=2.0, label=f"CD = a·cos(C) = {CD:.2f}"))
    rd3.lines.append(Line2D(Dx, -0.4, Ax, -0.4, color="#4EC7B0", width=2.0, label=f"DA = b - a·cos(C) = {DA:.2f}"))

    rd3.points.extend([
        Point2D(Cx, Cy, label="C", color="#EAF0F6"),
        Point2D(Ax, Ay, label="A", color="#EAF0F6"),
        Point2D(Bx, By, label="B", color="#EAF0F6"),
        Point2D(Dx, Dy, label="D", color="#D8A94E"),
    ])

    steps.append(ProofStep(
        index=3,
        equation=f"CD = a · cos(C) = {CD:.2f} cm,   DA = b - a · cos(C) = {DA:.2f} cm",
        explanation=f"In right triangle ΔCDB, adjacent side CD = a · cos(C) = {CD:.2f} cm. "
                    f"Therefore, the adjacent leg of right triangle ΔBDA is DA = b - CD = {DA:.2f} cm.",
        values={"CD": round(CD, 2), "DA": round(DA, 2), "h": round(h, 2)},
        render_data=rd3
    ))

    # -------------------------------------------------------------
    # Step 4: Apply Pythagorean Theorem to Right Triangle ΔBDA
    # -------------------------------------------------------------
    rd4 = RenderData(view_bounds=bounds)
    rd4.polygons.append(Polygon2D(
        points=[(Dx, Dy), (Ax, Ay), (Bx, By)],
        fill_color="rgba(89, 196, 138, 0.35)",
        stroke_color="#59C48A",
        stroke_width=2.5,
        label=f"c² = {c_sq:.2f}"
    ))
    rd4.lines.append(Line2D(Bx, By, Dx, Dy, color="#D8A94E", width=2.5, dashed=True, label=f"h = {h:.2f}"))
    rd4.lines.append(Line2D(Dx, Dy, Ax, Ay, color="#4EC7B0", width=2.5, label=f"DA = {DA:.2f}"))
    rd4.lines.append(Line2D(Ax, Ay, Bx, By, color="#59C48A", width=3.0, label=f"c = {c:.2f}"))

    steps.append(ProofStep(
        index=4,
        equation="c² = h² + (b - a·cos(C))² = a²·sin²(C) + b² - 2ab·cos(C) + a²·cos²(C)",
        explanation="Applying the Pythagorean theorem to right triangle ΔBDA: "
                    "c² = h² + DA² = (a·sin C)² + (b - a·cos C)². "
                    "Expanding: c² = a²·sin²(C) + b² - 2ab·cos(C) + a²·cos²(C).",
        values={"h²": round(h*h, 2), "DA²": round(DA*DA, 2), "c²": round(c_sq, 2)},
        render_data=rd4
    ))

    # -------------------------------------------------------------
    # Step 5: Final Derivation and Verification
    # -------------------------------------------------------------
    rd5 = RenderData(view_bounds=bounds)
    rd5.polygons.append(Polygon2D(
        points=[(Cx, Cy), (Ax, Ay), (Bx, By)],
        fill_color="rgba(89, 196, 138, 0.3)",
        stroke_color="#59C48A",
        stroke_width=2.5,
        label=f"c = {c:.2f} cm"
    ))
    rd5.arcs.append(Arc2D(0, 0, arc_rad, 0, C_deg, color="#D8A94E", label=f"{C_deg:.1f}°"))
    rd5.texts.append(
        Text2D((min_x + max_x) / 2.0, max_y - 0.6, f"c² = {a*a:.1f} + {b*b:.1f} - 2·({a:.1f})·({b:.1f})·({math.cos(C_rad):.3f}) = {c_sq:.2f}", color="#59C48A", font_size=11, bold=True)
    )

    steps.append(ProofStep(
        index=5,
        equation=f"c² = a² + b² - 2ab·cos(C)  ⟹  c = √({c_sq:.2f}) = {c:.2f} cm",
        explanation=f"Using sin²(C) + cos²(C) = 1, terms factor into a²(sin²C + cos²C) = a². "
                    f"Thus: c² = a² + b² - 2ab·cos(C) = {a*a:.2f} + {b*b:.2f} - {2*a*b*math.cos(C_rad):.2f} = {c_sq:.2f}. "
                    f"Therefore c = {c:.2f} cm.",
        values={"a²": round(a*a, 2), "b²": round(b*b, 2), "2ab·cos(C)": round(2*a*b*math.cos(C_rad), 2), "c²": round(c_sq, 2), "c": round(c, 2)},
        render_data=rd5
    ))

    return steps
