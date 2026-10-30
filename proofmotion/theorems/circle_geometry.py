"""
theorems/circle_geometry.py
---------------------------
Mathematical and geometric derivation of Circle Area and Circumference:
A = πr²,  C = 2πr

Derives the area formula by dividing the circle into congruent triangular
wedges and rearranging them into an approximating rectangle of base πr
and height r.
"""

import math
import numpy as np
import sympy as sp
from typing import List, Tuple, Dict, Any

from models.theorem_state import Theorem, ParameterSpec, ParameterType, ProofStep
from core.step_model import RenderData, Point2D, Line2D, Polygon2D, Text2D, Arc2D


def get_theorem_spec() -> Theorem:
    return Theorem(
        key="circle_area",
        display_name="Circle Geometry",
        short_description="Derivation of a circle's area (A = πr²) and circumference (C = 2πr) via polygon wedge rearrangement.",
        parameters=[
            ParameterSpec("radius", "Radius (r)", ParameterType.LENGTH, default=5.0, min_value=0.5, max_value=50.0, suffix="cm"),
        ],
        steps=[],
        final_result_template="Area = {area:.2f} cm²,  Circumference = {circ:.2f} cm",
    )


def validate_parameters(values: Dict[str, float]) -> Tuple[bool, str]:
    r = values.get("radius", 0)
    if r <= 0:
        return False, "Radius must be a positive number greater than 0."
    return True, ""


def compute_final_result(values: Dict[str, float]) -> str:
    r = float(values.get("radius", 5.0))
    area = math.pi * r * r
    circ = 2.0 * math.pi * r
    return f"Area = {area:.2f} cm²,  Circumference = {circ:.2f} cm (Verified: π · {r:.2f}² = {area:.2f})"


def generate_proof_steps(values: Dict[str, float]) -> List[ProofStep]:
    r = float(values.get("radius", 5.0))
    area = math.pi * r * r
    circ = 2.0 * math.pi * r

    steps = []

    # -------------------------------------------------------------
    # Step 1: Circle Definition and Circumference
    # -------------------------------------------------------------
    rd1 = RenderData(view_bounds=(-r - 3.0, -r - 3.2, r + 3.0, r + 2.5))
    # Draw circle using polygon of 72 points
    theta = np.linspace(0, 2 * np.pi, 72)
    circle_pts = [(float(r * np.cos(t)), float(r * np.sin(t))) for t in theta]
    rd1.polygons.append(Polygon2D(
        points=circle_pts,
        fill_color="rgba(78, 199, 176, 0.18)",
        stroke_color="#4EC7B0",
        stroke_width=2.5,
        label=""
    ))
    # Radius line from (0,0) to (r, 0)
    rd1.lines.append(Line2D(0, 0, r, 0, color="#D8A94E", width=2.5, label=f"r = {r:.1f} cm"))
    # Diameter dashed line
    rd1.lines.append(Line2D(-r, 0, 0, 0, color="#5B8DEF", width=1.5, dashed=True, label=f"d = {2*r:.1f} cm"))
    rd1.points.extend([
        Point2D(0, 0, label="O(0,0)", color="#EAF0F6"),
        Point2D(r, 0, label=f"P({r:.1f}, 0)", color="#D8A94E"),
    ])
    rd1.texts.append(
        Text2D(0, -r - 1.8, f"Circumference C = 2πr = 2 · π · {r:.1f} = {circ:.2f} cm", color="#4EC7B0", font_size=11, bold=True)
    )

    steps.append(ProofStep(
        index=1,
        equation=f"Circumference C = 2πr = 2 · π · {r:.2f} = {circ:.2f} cm",
        explanation=f"Consider a circle of radius r = {r:.1f} cm centered at origin O. "
                    f"The perimeter around the boundary is defined by C = 2πr = {circ:.2f} cm.",
        values={"radius": r, "diameter": 2 * r, "circumference": round(circ, 2)},
        render_data=rd1
    ))

    # -------------------------------------------------------------
    # Step 2: Slicing the Circle into Slices / Wedges
    # -------------------------------------------------------------
    n_slices = 16
    rd2 = RenderData(view_bounds=(-r - 3.0, -r - 3.2, r + 3.0, r + 2.5))
    # Draw alternating colored wedges
    d_phi = 2 * np.pi / n_slices
    for i in range(n_slices):
        phi1 = i * d_phi
        phi2 = (i + 1) * d_phi
        # Points along arc
        arc_thetas = np.linspace(phi1, phi2, 8)
        wedge_pts = [(0.0, 0.0)] + [(float(r * np.cos(t)), float(r * np.sin(t))) for t in arc_thetas]
        color = "rgba(78, 199, 176, 0.4)" if i % 2 == 0 else "rgba(216, 169, 78, 0.4)"
        stroke = "#4EC7B0" if i % 2 == 0 else "#D8A94E"
        rd2.polygons.append(Polygon2D(
            points=wedge_pts,
            fill_color=color,
            stroke_color=stroke,
            stroke_width=1.5
        ))

    rd2.points.append(Point2D(0, 0, label="O", color="#EAF0F6"))
    rd2.texts.append(
        Text2D(0, -r - 1.8, f"Divided into n = {n_slices} equal wedges of angle {360/n_slices:.1f}°", color="#D8A94E", font_size=11, bold=True)
    )

    steps.append(ProofStep(
        index=2,
        equation=f"Circle = Σ (n = {n_slices} triangular wedges),  Wedge angle = 360° / {n_slices} = {360/n_slices:.1f}°",
        explanation=f"Divide the circle into {n_slices} congruent circular sectors (wedges). "
                    f"Each sector behaves approximately like an isosceles triangle with base b ≈ 2πr / {n_slices} and height h = r.",
        values={"n_wedges": n_slices, "sector_angle_deg": 360 / n_slices, "radius": r},
        render_data=rd2
    ))

    # -------------------------------------------------------------
    # Step 3: Rearranging Wedges into an Alternating Strip
    # -------------------------------------------------------------
    # Unroll the 16 wedges: 8 point down, 8 point up, interlocking
    rd3 = RenderData(view_bounds=(-1, -1, math.pi * r + 2, r + 2))
    wedge_base = (2 * math.pi * r) / n_slices
    half_base = wedge_base / 2.0

    # Draw interlocking trapezoid-like triangles
    for i in range(n_slices):
        if i % 2 == 0:
            # Pointing UP: base along y = 0, apex at y = r
            bx = (i // 2) * wedge_base
            pts = [(bx, 0.0), (bx + wedge_base, 0.0), (bx + half_base, r)]
            rd3.polygons.append(Polygon2D(
                points=pts,
                fill_color="rgba(78, 199, 176, 0.45)",
                stroke_color="#4EC7B0",
                stroke_width=1.5
            ))
        else:
            # Pointing DOWN: base along y = r, apex at y = 0
            bx = (i // 2) * wedge_base + half_base
            pts = [(bx, r), (bx + wedge_base, r), (bx + half_base, 0.0)]
            rd3.polygons.append(Polygon2D(
                points=pts,
                fill_color="rgba(216, 169, 78, 0.45)",
                stroke_color="#D8A94E",
                stroke_width=1.5
            ))

    # Base dimension line along bottom
    base_len = (n_slices // 2) * wedge_base # ≈ pi * r
    rd3.lines.append(Line2D(0, -0.3, base_len, -0.3, color="#4EC7B0", width=2.0, label=f"Base ≈ πr = {math.pi * r:.2f} cm"))
    # Height dimension line along left
    rd3.lines.append(Line2D(-0.4, 0, -0.4, r, color="#D8A94E", width=2.0, label=f"h = r = {r:.1f} cm"))

    steps.append(ProofStep(
        index=3,
        equation=f"Interlocking Strip: Base = ½ · C = πr ≈ {math.pi * r:.2f} cm,  Height = r = {r:.1f} cm",
        explanation="Rearrange the wedges alternating alternately pointing up and down into an interlocking strip. "
                    "Half of the curved circumference forms the bottom base (length πr), and the other half forms the top. "
                    "The height of each wedge is the radius r.",
        values={"bottom_arc_sum": round(math.pi * r, 2), "wedge_height": r},
        render_data=rd3
    ))

    # -------------------------------------------------------------
    # Step 4: Limit as n -> ∞: Rectangle with Area A = πr²
    # -------------------------------------------------------------
    rd4 = RenderData(view_bounds=(-1, -1, math.pi * r + 2, r + 2))
    base_w = math.pi * r
    rd4.polygons.append(Polygon2D(
        points=[(0, 0), (base_w, 0), (base_w, r), (0, r)],
        fill_color="rgba(89, 196, 138, 0.35)",
        stroke_color="#59C48A",
        stroke_width=2.5,
        label=""
    ))
    rd4.lines.append(Line2D(0, -0.4, base_w, -0.4, color="#59C48A", width=2.5, label=f"Base = πr = {base_w:.2f} cm"))
    rd4.lines.append(Line2D(-0.5, 0, -0.5, r, color="#D8A94E", width=2.5, label=f"Height = r = {r:.1f} cm"))
    rd4.texts.append(
        Text2D(base_w / 2.0, r / 2.0, f"Area = Base × Height = (πr) · r = πr² = {area:.2f} cm²", color="#0F172A", font_size=12, bold=True)
    )

    steps.append(ProofStep(
        index=4,
        equation=f"Area = Base × Height = (πr) · r = πr² = π · {r:.2f}² = {area:.2f} cm²",
        explanation=f"As the number of wedges n approaches infinity, the scalloped edges straighten into vertical sides. "
                    f"The shape becomes a perfect rectangle with base πr and height r. Therefore: Area = (πr) · r = πr² = {area:.2f} cm².",
        values={"r": r, "r²": round(r * r, 2), "area": round(area, 2), "circumference": round(circ, 2)},
        render_data=rd4
    ))

    return steps
