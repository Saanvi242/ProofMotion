"""
cgip/rasterization.py
--------------------
Classic Computer Graphics Rasterization Algorithms:
- Digital Differential Analyzer (DDA) Line Drawing
- Bresenham's Line Drawing Algorithm (Handles all 8 octants)
- Midpoint Circle Drawing Algorithm (8-way symmetry)

Generates step-by-step educational traces on a discrete pixel grid.
"""

import math
from typing import List, Tuple, Dict, Any
from core.step_model import VisualizationStep, RenderData
from resources.theme import COLORS


def dda_line(x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int]]:
    """
    Pure Digital Differential Analyzer (DDA) rasterization calculation.
    Returns the ordered list of integer pixel coordinates (x, y) along the line.
    Handles horizontal, vertical, diagonal, steep, shallow, positive and negative slopes,
    and degenerate zero-length lines.
    """
    dx = x1 - x0
    dy = y1 - y0
    steps_count = max(abs(dx), abs(dy))
    if steps_count == 0:
        return [(int(x0), int(y0))]

    x_inc = dx / steps_count
    y_inc = dy / steps_count

    curr_x = float(x0)
    curr_y = float(y0)
    pixels = []

    for _ in range(steps_count + 1):
        pixels.append((int(round(curr_x)), int(round(curr_y))))
        curr_x += x_inc
        curr_y += y_inc

    return pixels


def bresenham_line(x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int]]:
    """
    Pure Bresenham integer-only line drawing across all 8 octants.
    Returns the ordered list of integer pixel coordinates (x, y).
    """
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    x, y = int(x0), int(y0)
    pixels = []

    while True:
        pixels.append((x, y))
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy

    return pixels


def midpoint_circle(cx: int, cy: int, r: int, deduplicate: bool = True) -> List[Tuple[int, int]]:
    """
    Pure Midpoint Circle Algorithm calculating pixel coordinates with 8-way symmetry.
    Initial decision parameter p0 = 1 - r (integer formulation).
    deduplicate: if True, duplicate points on axes and diagonals are removed.
    """
    if r < 0:
        raise ValueError(f"Radius must be non-negative, got {r}")
    if r == 0:
        return [(int(cx), int(cy))]

    cx, cy, r = int(cx), int(cy), int(r)
    p = 1 - r
    x = 0
    y = r

    pixels = []
    seen = set()

    def add_sym(x_off, y_off):
        pts = [
            (cx + x_off, cy + y_off),
            (cx - x_off, cy + y_off),
            (cx + x_off, cy - y_off),
            (cx - x_off, cy - y_off),
            (cx + y_off, cy + x_off),
            (cx - y_off, cy + x_off),
            (cx + y_off, cy - x_off),
            (cx - y_off, cy - x_off),
        ]
        for pt in pts:
            if not deduplicate:
                pixels.append(pt)
            elif pt not in seen:
                seen.add(pt)
                pixels.append(pt)

    add_sym(x, y)

    while x < y:
        x += 1
        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * x + 1 - 2 * y
        add_sym(x, y)

    return pixels


def dda_line_trace(x0: int, y0: int, x1: int, y1: int, grid_size: int = 20) -> List[VisualizationStep]:
    dx = x1 - x0
    dy = y1 - y0
    steps_count = max(abs(dx), abs(dy))

    steps = []
    step_num = 1

    if steps_count == 0:
        # Single point
        pixels = [(x0, y0, COLORS["accent_teal"])]
        steps.append(VisualizationStep(
            index=1,
            title="DDA: Single Point Line",
            equation=f"dx = 0, dy = 0 ⟹ Point ({x0}, {y0})",
            explanation="Start and end endpoints are identical. Plotted single pixel.",
            values={"pixel": (x0, y0)},
            metrics={"steps": 0},
            render_data=RenderData(
                mode="pixel_grid",
                pixel_grid={
                    "grid_w": grid_size, "grid_h": grid_size,
                    "pixels": pixels,
                    "current": (x0, y0),
                    "ideal_line": (x0, y0, x1, y1)
                }
            )
        ))
        return steps

    x_inc = dx / steps_count
    y_inc = dy / steps_count

    # Step 1: Initialization
    steps.append(VisualizationStep(
        index=step_num,
        title=f"DDA Setup: ({x0}, {y0}) to ({x1}, {y1})",
        equation=f"Δx = {dx},  Δy = {dy}\n"
                 f"steps = max(|Δx|, |Δy|) = {steps_count}\n"
                 f"x_inc = Δx / steps = {x_inc:.3f},  y_inc = Δy / steps = {y_inc:.3f}",
        explanation=f"Calculated coordinate increments. Total steps: {steps_count}. "
                    f"Along the dominant axis, step size is 1.0; along the non-dominant axis, increment is slope.",
        values={"x0": x0, "y0": y0, "x1": x1, "y1": y1, "dx": dx, "dy": dy, "steps": steps_count, "x_inc": x_inc, "y_inc": y_inc},
        metrics={"total_steps": steps_count, "algorithm": "DDA"},
        render_data=RenderData(
            mode="pixel_grid",
            pixel_grid={
                "grid_w": grid_size, "grid_h": grid_size,
                "pixels": [],
                "start_point": (x0, y0),
                "end_point": (x1, y1),
            }
        )
    ))

    curr_x = float(x0)
    curr_y = float(y0)
    plotted_pixels = []

    for k in range(steps_count + 1):
        step_num += 1
        px = int(round(curr_x))
        py = int(round(curr_y))
        plotted_pixels.append((px, py, COLORS["accent_teal"]))

        cand = []
        if k < steps_count:
            cand = [(int(round(curr_x + x_inc)), int(round(curr_y + y_inc)))]

        steps.append(VisualizationStep(
            index=step_num,
            title=f"DDA Step {k}: Plot Pixel ({px}, {py})",
            equation=f"Continuous: ({curr_x:.2f}, {curr_y:.2f}) ⟹ round() ⟹ Pixel ({px}, {py})\n"
                     f"Increment: x_inc = {x_inc:.3f}, y_inc = {y_inc:.3f}",
            explanation=f"At step {k}, continuous coordinates are ({curr_x:.2f}, {curr_y:.2f}). "
                        f"Rounding to the nearest integer grid cell selects pixel ({px}, {py})." +
                        (f" Next continuous coordinate will be ({curr_x + x_inc:.2f}, {curr_y + y_inc:.2f})." if k < steps_count else " Final endpoint reached."),
            values={"k": k, "x_float": round(curr_x, 3), "y_float": round(curr_y, 3), "plotted_pixel": (px, py), "candidates": cand},
            metrics={"plotted_count": len(plotted_pixels)},
            render_data=RenderData(
                mode="pixel_grid",
                pixel_grid={
                    "grid_w": grid_size, "grid_h": grid_size,
                    "pixels": list(plotted_pixels),
                    "current": (px, py),
                    "candidates": cand,
                    "start_point": (x0, y0),
                    "end_point": (x1, y1),
                }
            )
        ))

        curr_x += x_inc
        curr_y += y_inc

    # Final Step: Draw the line connecting start and end using the plotted pixels
    step_num += 1
    steps.append(VisualizationStep(
        index=step_num,
        title=f"DDA Complete: Line Drawn from ({x0}, {y0}) to ({x1}, {y1})",
        equation=f"Line rasterization complete. Plotted {len(plotted_pixels)} pixels.\n"
                 f"Continuous line drawn through the rasterized pixels.",
        explanation=f"All {len(plotted_pixels)} discrete pixels have been found and plotted. "
                    f"The continuous line is now drawn connecting start ({x0}, {y0}) to end ({x1}, {y1}) "
                    f"through the rasterized pixel path.",
        values={"x0": x0, "y0": y0, "x1": x1, "y1": y1, "total_pixels": len(plotted_pixels)},
        metrics={"plotted_count": len(plotted_pixels), "algorithm": "DDA"},
        render_data=RenderData(
            mode="pixel_grid",
            pixel_grid={
                "grid_w": grid_size, "grid_h": grid_size,
                "pixels": list(plotted_pixels),
                "start_point": (x0, y0),
                "end_point": (x1, y1),
                "ideal_line": (x0, y0, x1, y1),
            }
        )
    ))

    return steps


def bresenham_line_trace(x0: int, y0: int, x1: int, y1: int, grid_size: int = 20) -> List[VisualizationStep]:
    """
    Bresenham's integer line algorithm supporting all 8 octants.
    """
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1

    is_steep = dy > dx

    steps = []
    step_num = 1

    steps.append(VisualizationStep(
        index=step_num,
        title=f"Bresenham Setup: ({x0}, {y0}) to ({x1}, {y1})",
        equation=f"dx = |x₁ - x₀| = {dx},  dy = |y₁ - y₀| = {dy}\n"
                 f"Step directions: sx = {sx}, sy = {sy}\n"
                 f"Dominant Axis: {'Y (Steep, |m| > 1)' if is_steep else 'X (Shallow, |m| ≤ 1)'}",
        explanation=f"Endpoints defined: Start P₀({x0}, {y0}) and End P₁({x1}, {y1}). "
                    f"Bresenham uses pure integer addition and subtraction to decide which pixel is closer to the true line.",
        values={"dx": dx, "dy": dy, "sx": sx, "sy": sy, "is_steep": is_steep},
        metrics={"algorithm": "Bresenham"},
        render_data=RenderData(
            mode="pixel_grid",
            pixel_grid={
                "grid_w": grid_size, "grid_h": grid_size,
                "pixels": [],
                "start_point": (x0, y0),
                "end_point": (x1, y1),
            }
        )
    ))

    # Generalized integer error accumulator:
    # err = dx - dy
    err = dx - dy
    x, y = x0, y0
    plotted = []

    while True:
        step_num += 1
        plotted.append((x, y, COLORS["accent_teal"]))

        if x == x1 and y == y1:
            steps.append(VisualizationStep(
                index=step_num,
                title=f"Bresenham Step: Final Endpoint ({x}, {y})",
                equation=f"Plotted final endpoint ({x1}, {y1}). Total pixels: {len(plotted)}.",
                explanation=f"Reached endpoint ({x1}, {y1}). All line pixels have been found.",
                values={"pixel": (x, y), "total_pixels": len(plotted)},
                metrics={"plotted_count": len(plotted)},
                render_data=RenderData(
                    mode="pixel_grid",
                    pixel_grid={
                        "grid_w": grid_size, "grid_h": grid_size,
                        "pixels": list(plotted),
                        "current": (x, y),
                        "start_point": (x0, y0),
                        "end_point": (x1, y1),
                    }
                )
            ))
            break

        # Candidates for next step
        cand = []
        if is_steep:
            cand = [(x, y + sy), (x + sx, y + sy)]
        else:
            cand = [(x + sx, y), (x + sx, y + sy)]

        err_before = err
        e2 = 2 * err
        decision_info = f"Current error term: err = {err_before},  2·err = {e2}"
        next_x, next_y = x, y
        step_x = e2 > -dy
        step_y = e2 < dx
        if step_x and step_y:
            lean, choice = 0, "diagonal"
        elif step_x:
            lean, choice = -1, "x"
        else:
            lean, choice = 1, "y"

        step_expl = f"Plotted ({x}, {y}). "
        if step_x:
            err -= dy
            next_x += sx
            step_expl += f"2·err > -dy ({e2} > {-dy}) ⟹ step X by {sx}. "
        if step_y:
            err += dx
            next_y += sy
            step_expl += f"2·err < dx ({e2} < {dx}) ⟹ step Y by {sy}."

        steps.append(VisualizationStep(
            index=step_num,
            title=f"Bresenham Step: Plot Pixel ({x}, {y})",
            equation=decision_info,
            explanation=step_expl,
            values={"pixel": (x, y), "error": err, "decision": err_before, "candidates": cand, "choice": choice},
            metrics={"plotted_count": len(plotted)},
            render_data=RenderData(
                mode="pixel_grid",
                pixel_grid={
                    "grid_w": grid_size, "grid_h": grid_size,
                    "pixels": list(plotted),
                    "candidates": cand,
                    "current": (x, y),
                    "start_point": (x0, y0),
                    "end_point": (x1, y1),
                    "decision": err_before,
                    "decision_kind": "err",
                    "e2": e2,
                    "lean": lean,
                    "choice": choice,
                }
            )
        ))

        x, y = next_x, next_y

    # Final Step: Draw the line connecting start and end through the plotted pixels
    step_num += 1
    steps.append(VisualizationStep(
        index=step_num,
        title=f"Bresenham Complete: Line Drawn from ({x0}, {y0}) to ({x1}, {y1})",
        equation=f"Rasterization complete. Plotted {len(plotted)} pixels.\n"
                 f"Continuous line drawn through the rasterized pixels.",
        explanation=f"All {len(plotted)} pixels have been determined. "
                    f"The continuous line connects start ({x0}, {y0}) to end ({x1}, {y1}) "
                    f"through the rasterized pixel path.",
        values={"x0": x0, "y0": y0, "x1": x1, "y1": y1, "total_pixels": len(plotted)},
        metrics={"plotted_count": len(plotted), "algorithm": "Bresenham"},
        render_data=RenderData(
            mode="pixel_grid",
            pixel_grid={
                "grid_w": grid_size, "grid_h": grid_size,
                "pixels": list(plotted),
                "start_point": (x0, y0),
                "end_point": (x1, y1),
                "ideal_line": (x0, y0, x1, y1),
            }
        )
    ))

    return steps


def midpoint_circle_trace(cx: int, cy: int, r: int, grid_size: int = 24) -> List[VisualizationStep]:
    """
    Midpoint Circle Algorithm with 8-way symmetry.
    """
    steps = []
    step_num = 1

    p = 1 - r # Initial decision parameter p0 = 1 - r (integer formulation)
    x = 0
    y = r

    plotted = []

    def get_symmetric_points(x_offset, y_offset):
        return [
            (cx + x_offset, cy + y_offset),
            (cx - x_offset, cy + y_offset),
            (cx + x_offset, cy - y_offset),
            (cx - x_offset, cy - y_offset),
            (cx + y_offset, cy + x_offset),
            (cx - y_offset, cy + x_offset),
            (cx + y_offset, cy - x_offset),
            (cx - y_offset, cy - x_offset),
        ]

    steps.append(VisualizationStep(
        index=step_num,
        title=f"Midpoint Circle Setup: Center=({cx}, {cy}), Radius={r}",
        equation=f"p₀ = 1 - r = 1 - {r} = {p}\n"
                 f"Initial point on 1st octant: (x₀, y₀) = (0, {r})",
        explanation=f"Midpoint circle algorithm evaluates whether the midpoint between candidate pixels "
                    f"E(x+1, y) and SE(x+1, y-1) lies inside or outside the circle. "
                    f"By 8-way symmetry, each calculated point (x, y) yields 8 mirrored pixels.",
        values={"center": (cx, cy), "radius": r, "p0": p},
        metrics={"radius": r, "symmetry": "8-way"},
        render_data=RenderData(
            mode="pixel_grid",
            pixel_grid={
                "grid_w": grid_size, "grid_h": grid_size,
                "pixels": [],
                "center": (cx, cy),
            }
        )
    ))

    # Add initial points
    sym_pts = get_symmetric_points(x, y)
    for sp in sym_pts:
        plotted.append((sp[0], sp[1], COLORS["accent_teal"]))

    step_num += 1
    steps.append(VisualizationStep(
        index=step_num,
        title=f"Plot Initial 8-Symmetric Pixels for (0, {r})",
        equation=f"x = 0, y = {r},  p = {p}\n"
                 f"Points: ({cx}±0, {cy}±{r}) and ({cx}±{r}, {cy}±0)",
        explanation=f"Plotted initial 8 points at the compass extremes around center ({cx}, {cy}).",
        values={"x": x, "y": y, "p": p, "symmetric_points": sym_pts},
        metrics={"plotted_count": len(plotted)},
        render_data=RenderData(
            mode="pixel_grid",
            pixel_grid={
                "grid_w": grid_size, "grid_h": grid_size,
                "pixels": list(plotted),
                "current": (cx + x, cy + y),
                "center": (cx, cy),
            }
        )
    ))

    while x < y:
        x += 1
        cand_E = (cx + x, cy + y)
        cand_SE = (cx + x, cy + y - 1)

        p_before = p
        if p < 0:
            # Midpoint is inside circle, choose E (x+1, y)
            p_next = p + 2 * x + 1
            expl = f"p = {p} < 0: Midpoint is inside the circle boundary. Choose E: y remains {y}. p_next = p + 2x + 1 = {p_next}."
            lean, choice = -1, "E"
            p = p_next
        else:
            # Midpoint is outside circle, choose SE (x+1, y-1)
            y -= 1
            p_next = p + 2 * x + 1 - 2 * y
            expl = f"p = {p} ≥ 0: Midpoint is outside or on circle boundary. Choose SE: y decrements to {y}. p_next = p + 2x + 1 - 2y = {p_next}."
            lean, choice = 1, "SE"
            p = p_next

        sym_pts = get_symmetric_points(x, y)
        for sp in sym_pts:
            plotted.append((sp[0], sp[1], COLORS["accent_teal"]))

        step_num += 1
        steps.append(VisualizationStep(
            index=step_num,
            title=f"Step x={x}, y={y} (p={p})",
            equation=f"Decision p = {p_next},  Selected (x={x}, y={y})",
            explanation=expl + f" Symmetrically replicated across all 8 octants ({len(sym_pts)} points).",
            values={"x": x, "y": y, "decision_param": p_before, "octant_points": sym_pts, "choice": choice},
            metrics={"plotted_count": len(plotted)},
            render_data=RenderData(
                mode="pixel_grid",
                pixel_grid={
                    "grid_w": grid_size, "grid_h": grid_size,
                    "pixels": list(plotted),
                    "candidates": [cand_E, cand_SE],
                    "current": (cx + x, cy + y),
                    "center": (cx, cy),
                    "decision": p_before,
                    "decision_kind": "p",
                    "lean": lean,
                    "choice": choice,
                }
            )
        ))

    step_num += 1
    steps.append(VisualizationStep(
        index=step_num,
        title=f"Circle Complete: {len(plotted)} Pixels Rasterized",
        equation=f"x >= y ⟹ Octant 1 complete. Full 360° circle rasterized.",
        explanation=f"Reached boundary condition x ≥ y. The complete raster circle with radius {r} is plotted.",
        values={"total_pixels": len(plotted)},
        metrics={"plotted_count": len(plotted)},
        render_data=RenderData(
            mode="pixel_grid",
            pixel_grid={
                "grid_w": grid_size, "grid_h": grid_size,
                "pixels": list(plotted),
                "center": (cx, cy),
                "ideal_circle": (cx, cy, r)
            }
        )
    ))

    return steps


def dda_vs_bresenham_comparison_trace(x0: int, y0: int, x1: int, y1: int, grid_size: int = 20) -> List[VisualizationStep]:
    """
    Direct pedagogical comparison of DDA and Bresenham algorithms on identical endpoints (x0, y0) to (x1, y1).
    Exposes:
      1. Baseline endpoints and slope m = dy / dx.
      2. DDA floating-point incremental evaluation.
      3. Bresenham integer error accumulation.
      4. Pixel-by-pixel match and arithmetic operation count comparison.
    """
    dda_pts = dda_line(x0, y0, x1, y1)
    bres_pts = bresenham_line(x0, y0, x1, y1)

    steps = []
    dx = x1 - x0
    dy = y1 - y0
    slope_str = f"{dy/dx:.3f}" if dx != 0 else "Undefined (Vertical)"

    # Step 1: Specification
    steps.append(VisualizationStep(
        index=1,
        title=f"Line Comparison Setup: ({x0}, {y0}) to ({x1}, {y1})",
        equation=f"Start: P₀({x0}, {y0}),  End: P₁({x1}, {y1})\n"
                 f"Δx = {dx},  Δy = {dy},  Slope m = {slope_str}",
        explanation=f"Comparing Digital Differential Analyzer (DDA) vs Bresenham's Integer Line Algorithm on identical endpoints. "
                    f"DDA uses continuous floating-point increments, while Bresenham uses pure integer decision arithmetic.",
        values={"x0": x0, "y0": y0, "x1": x1, "y1": y1, "dx": dx, "dy": dy},
        metrics={"dda_steps": len(dda_pts), "bresenham_steps": len(bres_pts)},
        render_data=RenderData(
            mode="pixel_grid",
            pixel_grid={
                "grid_w": grid_size, "grid_h": grid_size,
                "pixels": [],
                "start_point": (x0, y0),
                "end_point": (x1, y1),
            }
        )
    ))

    # Step 2: DDA Output
    dda_pixels = [(p[0], p[1], COLORS["accent_teal"]) for p in dda_pts]
    steps.append(VisualizationStep(
        index=2,
        title=f"DDA Result: {len(dda_pts)} Pixels Plotted",
        equation=f"DDA Arithmetic: {len(dda_pts)} floating-point additions + {len(dda_pts)} round() operations.\n"
                 f"Pixels: {dda_pts}",
        explanation="DDA advances along the dominant axis with step 1.0 and along the minor axis with increment m = dy/dx. "
                    "Each continuous value is rounded to the nearest integer grid coordinate.",
        values={"algorithm": "DDA", "pixels": dda_pts, "count": len(dda_pts)},
        metrics={"plotted": len(dda_pts), "flops": len(dda_pts) * 2},
        render_data=RenderData(
            mode="pixel_grid",
            pixel_grid={
                "grid_w": grid_size, "grid_h": grid_size,
                "pixels": dda_pixels,
                "start_point": (x0, y0),
                "end_point": (x1, y1),
            }
        )
    ))

    # Step 3: Bresenham Output
    bres_pixels = [(p[0], p[1], COLORS["accent_gold"]) for p in bres_pts]
    steps.append(VisualizationStep(
        index=3,
        title=f"Bresenham Result: {len(bres_pts)} Pixels Plotted",
        equation=f"Bresenham Arithmetic: {len(bres_pts)} integer additions/subtractions, 0 floating-point operations.\n"
                 f"Pixels: {bres_pts}",
        explanation="Bresenham maintains an integer error term tracking distance from candidate pixels to the ideal line. "
                    "Only integer addition, subtraction, and bit-shifts (2*err) are executed.",
        values={"algorithm": "Bresenham", "pixels": bres_pts, "count": len(bres_pts)},
        metrics={"plotted": len(bres_pts), "flops": 0},
        render_data=RenderData(
            mode="pixel_grid",
            pixel_grid={
                "grid_w": grid_size, "grid_h": grid_size,
                "pixels": bres_pixels,
                "start_point": (x0, y0),
                "end_point": (x1, y1),
            }
        )
    ))

    # Step 4: Comparison Analysis
    dda_set = set(dda_pts)
    bres_set = set(bres_pts)
    matches = dda_set & bres_set
    diffs = (dda_set ^ bres_set)
    is_identical = (dda_pts == bres_pts)

    comp_pixels = []
    for p in matches:
        comp_pixels.append((p[0], p[1], COLORS["accent_teal"]))  # Matching (teal)
    for p in (dda_set - bres_set):
        comp_pixels.append((p[0], p[1], "#E4685D"))  # DDA only (coral)
    for p in (bres_set - dda_set):
        comp_pixels.append((p[0], p[1], COLORS["accent_gold"]))  # Bresenham only (gold)

    match_pct = (len(matches) / max(len(dda_set), len(bres_set))) * 100.0 if dda_set else 100.0

    steps.append(VisualizationStep(
        index=4,
        title=f"Comparison: {'Exact Pixel Match (100%)' if is_identical else f'{match_pct:.1f}% Pixel Match'}",
        equation=f"Total Steps: DDA={len(dda_pts)}, Bresenham={len(bres_pts)}\n"
                 f"Matching Pixels: {len(matches)},  Differing Pixels: {len(diffs)}\n"
                 f"DDA: O(N) Float Adds + Rounding | Bresenham: O(N) Pure Integer Adds",
        explanation=f"{'Both algorithms generated an identical sequence of pixels. ' if is_identical else 'Subtle differences in tie-breaking midpoint rounding occurred. '} "
                    f"Bresenham is historically preferred in hardware and embedded renderers because it eliminates floating-point arithmetic entirely.",
        values={"matching_count": len(matches), "diff_count": len(diffs), "identical": is_identical},
        metrics={"match_rate": f"{match_pct:.1f}%", "dda_count": len(dda_pts), "bresenham_count": len(bres_pts)},
        render_data=RenderData(
            mode="pixel_grid",
            pixel_grid={
                "grid_w": grid_size, "grid_h": grid_size,
                "pixels": comp_pixels,
                "start_point": (x0, y0),
                "end_point": (x1, y1),
                "ideal_line": (x0, y0, x1, y1)
            }
        )
    ))

    return steps
