"""
cgip/transformations.py
-----------------------
2D Computer Graphics Transformation Studio and Window-to-Viewport Mapping.

Implements 2D Homogeneous coordinates using column-vector convention:
P' = M · P

Supports:
- Translation T(dx, dy)
- Scaling S(sx, sy)
- Rotation R(theta)
- Reflection over X-axis, Y-axis, Origin, and line y = x
- Composite transformation sequences (e.g., T · R · S) demonstrating right-to-left order
- Window-to-Viewport mapping calculations and aspect ratio analysis
"""

import math
import numpy as np
from typing import List, Tuple, Dict, Any
from core.step_model import VisualizationStep, RenderData, Point2D, Line2D, Polygon2D, Text2D
from resources.theme import COLORS


def translation_matrix(dx: float, dy: float) -> np.ndarray:
    return np.array([
        [1.0, 0.0, float(dx)],
        [0.0, 1.0, float(dy)],
        [0.0, 0.0, 1.0]
    ], dtype=float)


def scaling_matrix(sx: float, sy: float, cx: float = 0.0, cy: float = 0.0) -> np.ndarray:
    if cx == 0.0 and cy == 0.0:
        return np.array([
            [float(sx), 0.0, 0.0],
            [0.0, float(sy), 0.0],
            [0.0, 0.0, 1.0]
        ], dtype=float)
    # Scale about fixed point (cx, cy): T(cx, cy) * S(sx, sy) * T(-cx, -cy)
    t_to_origin = translation_matrix(-cx, -cy)
    s = np.array([
        [float(sx), 0.0, 0.0],
        [0.0, float(sy), 0.0],
        [0.0, 0.0, 1.0]
    ], dtype=float)
    t_back = translation_matrix(cx, cy)
    return t_back @ s @ t_to_origin


def rotation_matrix(theta_deg: float, cx: float = 0.0, cy: float = 0.0) -> np.ndarray:
    rad = math.radians(theta_deg)
    cos_t = math.cos(rad)
    sin_t = math.sin(rad)
    r = np.array([
        [cos_t, -sin_t, 0.0],
        [sin_t, cos_t, 0.0],
        [0.0, 0.0, 1.0]
    ], dtype=float)
    if cx == 0.0 and cy == 0.0:
        return r
    # Rotate about arbitrary point: T(cx, cy) * R * T(-cx, -cy)
    t_to_origin = translation_matrix(-cx, -cy)
    t_back = translation_matrix(cx, cy)
    return t_back @ r @ t_to_origin


def reflection_matrix(axis: str) -> np.ndarray:
    axis = axis.lower()
    if axis in ("x", "x-axis"):
        return np.array([
            [1.0, 0.0, 0.0],
            [0.0, -1.0, 0.0],
            [0.0, 0.0, 1.0]
        ], dtype=float)
    elif axis in ("y", "y-axis"):
        return np.array([
            [-1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0]
        ], dtype=float)
    elif axis in ("origin", "(0,0)"):
        return np.array([
            [-1.0, 0.0, 0.0],
            [0.0, -1.0, 0.0],
            [0.0, 0.0, 1.0]
        ], dtype=float)
    elif axis in ("y=x", "y = x"):
        return np.array([
            [0.0, 1.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0]
        ], dtype=float)
    raise ValueError(f"Unknown reflection axis: {axis}")


def compose_transformations(*matrices: np.ndarray) -> np.ndarray:
    """
    Compose multiple 3x3 homogeneous transformation matrices in sequential application order.
    For column vectors (P' = M_n ... M_2 M_1 P):
    If M1 is applied first, then M2, then M3:
    compose_transformations(M1, M2, M3) returns M3 @ M2 @ M1.
    """
    if not matrices:
        return np.eye(3, dtype=float)
    result = np.eye(3, dtype=float)
    for m in matrices:
        result = np.asarray(m, dtype=float) @ result
    return result


def rotation_about_pivot_matrix(theta_deg: float, px: float, py: float) -> np.ndarray:
    """
    Calculates 2D homogeneous transformation matrix for rotation about arbitrary pivot (px, py):
    M = T(px, py) @ R(theta) @ T(-px, -py)
    """
    return rotation_matrix(theta_deg, cx=px, cy=py)


def window_to_viewport_map(
    x: float, y: float,
    w_min: Tuple[float, float],
    w_max: Tuple[float, float],
    v_min: Tuple[float, float],
    v_max: Tuple[float, float]
) -> Tuple[float, float]:
    """
    Direct mathematical Window-to-Viewport coordinate mapping.
    Maps world Cartesian point (x, y) into physical screen pixel (xv, yv).
    """
    xw_min, yw_min = w_min
    xw_max, yw_max = w_max
    xv_min, yv_min = v_min
    xv_max, yv_max = v_max

    w_width = xw_max - xw_min
    w_height = yw_max - yw_min
    v_width = xv_max - xv_min
    v_height = yv_max - yv_min

    if w_width <= 0 or w_height <= 0:
        raise ValueError(f"Invalid world window dimensions: width={w_width}, height={w_height}. Max must exceed Min.")
    if v_width <= 0 or v_height <= 0:
        raise ValueError(f"Invalid viewport dimensions: width={v_width}, height={v_height}. Max must exceed Min.")

    sx = v_width / w_width
    sy = v_height / w_height

    xv = xv_min + (x - xw_min) * sx
    yv = yv_min + (y - yw_min) * sy
    return float(xv), float(yv)


def apply_transform(matrix: np.ndarray, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """Transform list of 2D (x, y) coordinates using 3x3 homogeneous matrix."""
    transformed = []
    for x, y in points:
        v = np.array([x, y, 1.0], dtype=float)
        v_prime = matrix @ v
        transformed.append((float(v_prime[0]), float(v_prime[1])))
    return transformed


def format_matrix_str(m: np.ndarray) -> str:
    return (
        f"[[{m[0,0]:.2f}, {m[0,1]:.2f}, {m[0,2]:.2f}],\n"
        f" [{m[1,0]:.2f}, {m[1,1]:.2f}, {m[1,2]:.2f}],\n"
        f" [{m[2,0]:.2f}, {m[2,1]:.2f}, {m[2,2]:.2f}]]"
    )


def generate_transformation_demo(
    shape_type: str = "triangle",
    transformations: List[Dict[str, Any]] = None
) -> List[VisualizationStep]:
    """
    Generates step-by-step visual transformations of a 2D shape.
    transformations: list of dicts, e.g.
      [{"type": "scale", "sx": 1.5, "sy": 1.5},
       {"type": "rotate", "angle": 45},
       {"type": "translate", "dx": 3, "dy": 2}]
    """
    if shape_type == "triangle":
        base_points = [(1.0, 1.0), (4.0, 1.0), (2.5, 3.5)]
        shape_name = "Triangle ΔABC"
    elif shape_type == "rectangle":
        base_points = [(1.0, 1.0), (4.0, 1.0), (4.0, 3.0), (1.0, 3.0)]
        shape_name = "Rectangle ABCD"
    else:
        # Default polygon
        base_points = [(1.0, 1.0), (3.0, 1.0), (4.0, 2.5), (2.0, 3.5), (0.5, 2.0)]
        shape_name = "Polygon"

    if not transformations:
        transformations = [
            {"type": "scale", "sx": 1.5, "sy": 1.5},
            {"type": "rotate", "angle": 45.0},
            {"type": "translate", "dx": 3.0, "dy": 2.0},
        ]

    steps = []
    current_pts = list(base_points)
    current_matrix = np.eye(3, dtype=float)

    # Initial Step
    rd0 = RenderData(view_bounds=(-6, -6, 10, 10))
    rd0.polygons.append(Polygon2D(
        points=list(base_points),
        fill_color="rgba(91, 141, 239, 0.35)",
        stroke_color="#5B8DEF",
        stroke_width=2.5,
        label=shape_name
    ))
    for i, (px, py) in enumerate(base_points):
        label = chr(ord('A') + i)
        rd0.points.append(Point2D(px, py, label=f"{label}({px:.1f},{py:.1f})", color="#EAF0F6"))

    steps.append(VisualizationStep(
        index=1,
        title=f"Original Object: {shape_name}",
        equation="P = [x, y, 1]ᵀ,  M₀ = Identity Matrix I₃",
        explanation=f"Initial 2D coordinates for {shape_name}. Homogeneous representation assigns each vertex (x, y, 1)ᵀ.",
        values={"points": base_points},
        metrics={"total_transforms": len(transformations)},
        render_data=rd0
    ))

    step_idx = 1
    composed_m = np.eye(3, dtype=float)

    for t_spec in transformations:
        step_idx += 1
        t_type = t_spec.get("type", "translate")

        if t_type == "translate":
            dx, dy = t_spec.get("dx", 0.0), t_spec.get("dy", 0.0)
            m_step = translation_matrix(dx, dy)
            t_name = f"Translation T({dx:.1f}, {dy:.1f})"
            eq = f"T(dx={dx:.1f}, dy={dy:.1f}): P' = T · P"
            expl = f"Translate shape by dx={dx:.1f} along X-axis and dy={dy:.1f} along Y-axis."
        elif t_type == "scale":
            sx, sy = t_spec.get("sx", 1.0), t_spec.get("sy", 1.0)
            m_step = scaling_matrix(sx, sy)
            t_name = f"Scaling S({sx:.1f}, {sy:.1f})"
            eq = f"S(sx={sx:.1f}, sy={sy:.1f}): P' = S · P"
            expl = f"Scale shape by factor sx={sx:.1f} horizontally and sy={sy:.1f} vertically."
        elif t_type == "rotate":
            deg = float(t_spec.get("angle", 45.0))
            cx = float(t_spec.get("cx", 0.0))
            cy = float(t_spec.get("cy", 0.0))
            m_step = rotation_matrix(deg, cx=cx, cy=cy)
            if cx != 0.0 or cy != 0.0:
                t_name = f"Rotation R({deg:.1f}°) about Pivot ({cx:.1f}, {cy:.1f})"
                eq = f"R(θ={deg:.1f}°, P_pivot=({cx:.1f}, {cy:.1f})): P' = T(p) · R(θ) · T(-p) · P"
                expl = f"Rotate shape counter-clockwise by {deg:.1f}° about arbitrary fixed pivot ({cx:.1f}, {cy:.1f})."
            else:
                t_name = f"Rotation R({deg:.1f}°)"
                eq = f"R(θ={deg:.1f}°): P' = R · P"
                expl = f"Rotate shape counter-clockwise by {deg:.1f}° around the origin (0, 0)."
        elif t_type == "reflect":
            axis = t_spec.get("axis", "X-axis")
            m_step = reflection_matrix(axis)
            t_name = f"Reflection over {axis}"
            eq = f"Reflect({axis}): P' = M_ref · P"
            expl = f"Reflect shape across {axis}."
        else:
            continue

        # Column-vector composition: next matrix multiplies on the LEFT: M_new = M_step @ composed_m
        composed_m = m_step @ composed_m
        next_pts = apply_transform(m_step, current_pts)

        # Dynamic bounds
        all_pts = base_points + next_pts
        min_x = min(p[0] for p in all_pts) - 3.0
        max_x = max(p[0] for p in all_pts) + 3.0
        min_y = min(p[1] for p in all_pts) - 3.0
        max_y = max(p[1] for p in all_pts) + 3.0

        rd = RenderData(view_bounds=(min_x, min_y, max_x, max_y))

        # Original shape (faint dashed)
        rd.polygons.append(Polygon2D(
            points=list(base_points),
            fill_color="rgba(95, 116, 136, 0.15)",
            stroke_color="#5F7488",
            stroke_width=1.5,
            label="Original"
        ))

        # Previous intermediate shape
        if current_pts != base_points:
            rd.polygons.append(Polygon2D(
                points=list(current_pts),
                fill_color="rgba(91, 141, 239, 0.15)",
                stroke_color="#5B8DEF",
                stroke_width=1.5,
                label="Prior Step"
            ))

        # New transformed shape (vibrant)
        rd.polygons.append(Polygon2D(
            points=list(next_pts),
            fill_color="rgba(78, 199, 176, 0.4)",
            stroke_color="#4EC7B0",
            stroke_width=2.5,
            label=t_name
        ))

        # Vertex markers
        for i, (px, py) in enumerate(next_pts):
            label = chr(ord('A') + i) + "'" * (step_idx - 1)
            rd.points.append(Point2D(px, py, label=f"{label}({px:.1f},{py:.1f})", color="#D8A94E"))

        # Highlight pivot point if arbitrary rotation
        if t_type == "rotate" and (t_spec.get("cx", 0.0) != 0.0 or t_spec.get("cy", 0.0) != 0.0):
            piv_x = float(t_spec.get("cx", 0.0))
            piv_y = float(t_spec.get("cy", 0.0))
            rd.points.append(Point2D(piv_x, piv_y, label=f"Pivot({piv_x:.1f},{piv_y:.1f})", color=COLORS["danger"], radius=6.0))

        # Transition lines connecting old vertices to new vertices
        for (ox, oy), (nx, ny) in zip(current_pts, next_pts):
            rd.lines.append(Line2D(ox, oy, nx, ny, color="#D8A94E", width=1.5, dashed=True))

        steps.append(VisualizationStep(
            index=step_idx,
            title=t_name,
            equation=eq + "\nMatrix:\n" + format_matrix_str(m_step),
            explanation=expl + f" In column vector convention, P' = M · P. Combined matrix: P_final = M_composite · P_orig.",
            values={"matrix": m_step.tolist(), "composite_matrix": composed_m.tolist(), "points": next_pts},
            metrics={"step": step_idx - 1, "operation": t_name},
            render_data=rd
        ))

        current_pts = next_pts

    return steps


def window_to_viewport_trace(
    w_min: Tuple[float, float] = (-5.0, -5.0),
    w_max: Tuple[float, float] = (5.0, 5.0),
    v_min: Tuple[float, float] = (0.0, 0.0),
    v_max: Tuple[float, float] = (400.0, 300.0),
    sample_points: List[Tuple[float, float]] = None
) -> List[VisualizationStep]:
    """
    Step-by-step Window-to-Viewport mapping demonstration.
    """
    xw_min, yw_min = w_min
    xw_max, yw_max = w_max
    xv_min, yv_min = v_min
    xv_max, yv_max = v_max

    w_width = xw_max - xw_min
    w_height = yw_max - yw_min
    v_width = xv_max - xv_min
    v_height = yv_max - yv_min

    if w_width <= 0 or w_height <= 0:
        raise ValueError("Invalid world window: max must be strictly greater than min.")

    sx = v_width / w_width
    sy = v_height / w_height

    sample_points = sample_points or [(-2.0, -1.0), (0.0, 0.0), (3.0, 2.0)]
    mapped_points = [
        window_to_viewport_map(x, y, w_min, w_max, v_min, v_max)
        for (x, y) in sample_points
    ]

    steps = []

    # Step 1: Definition of Window and Viewport
    steps.append(VisualizationStep(
        index=1,
        title="Window-to-Viewport Mapping Setup",
        equation=f"World Window: [{xw_min}, {yw_min}] to [{xw_max}, {yw_max}]\n"
                 f"Viewport: [{xv_min}, {yv_min}] to [{xv_max}, {yv_max}]",
        explanation="World coordinates define the user's mathematical Cartesian space. "
                    "The Viewport defines the physical display area on the screen in pixels.",
        values={"world_window": (w_min, w_max), "viewport": (v_min, v_max)},
        metrics={"Sx": round(sx, 4), "Sy": round(sy, 4), "aspect_ratio_match": sx == sy}
    ))

    # Step 2: Scale Factors
    aspect_note = "Aspect ratio preserved (Sx == Sy)." if math.isclose(sx, sy) else f"Aspect ratio distorted (Sx={sx:.2f} != Sy={sy:.2f})."
    steps.append(VisualizationStep(
        index=2,
        title="Compute Scaling Factors Sx and Sy",
        equation=f"Sx = (Xv_max - Xv_min) / (Xw_max - Xw_min) = {v_width} / {w_width} = {sx:.4f}\n"
                 f"Sy = (Yv_max - Yv_min) / (Yw_max - Yw_min) = {v_height} / {w_height} = {sy:.4f}",
        explanation=f"Calculated horizontal scale Sx = {sx:.4f} and vertical scale Sy = {sy:.4f}. {aspect_note}",
        values={"Sx": round(sx, 4), "Sy": round(sy, 4)},
        metrics={"Sx": round(sx, 4), "Sy": round(sy, 4)}
    ))

    # Step 3: Transformation Equations
    steps.append(VisualizationStep(
        index=3,
        title="Mapping Equations",
        equation="Xv = Xv_min + (Xw - Xw_min) · Sx\n"
                 "Yv = Yv_min + (Yw - Yw_min) · Sy",
        explanation="Linear transformation formula maps any world point (Xw, Yw) into viewport coordinates (Xv, Yv).",
        values={"formula_x": f"Xv = {xv_min} + (Xw - {xw_min}) · {sx:.4f}",
                "formula_y": f"Yv = {yv_min} + (Yw - {yw_min}) · {sy:.4f}"}
    ))

    # Step 4: Sample point mapping
    for i, ((wx, wy), (vx, vy)) in enumerate(zip(sample_points, mapped_points), 1):
        steps.append(VisualizationStep(
            index=3 + i,
            title=f"Map Point P{i}({wx:.1f}, {wy:.1f})",
            equation=f"P{i}_v = ({xv_min} + ({wx} - {xw_min})·{sx:.2f}, {yv_min} + ({wy} - {yw_min})·{sy:.2f}) = ({vx:.1f}, {vy:.1f})",
            explanation=f"World coordinate ({wx:.1f}, {wy:.1f}) maps to screen pixel ({vx:.1f}, {vy:.1f}).",
            values={"world_pt": (wx, wy), "screen_pt": (round(vx, 1), round(vy, 1))}
        ))

    return steps
