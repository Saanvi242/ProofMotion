"""
cgip/clipping.py
----------------
Cohen–Sutherland line clipping and Sutherland–Hodgman polygon clipping.

Line clipping uses 4-bit region codes (TBRL), trivial accept/reject tests,
and parametric boundary intersections. Polygon clipping walks every edge
against LEFT, RIGHT, BOTTOM, then TOP, using the four inside/outside cases.
"""

from typing import List, Tuple, Dict, Any, Optional
from core.step_model import VisualizationStep, RenderData
from resources.theme import COLORS

INSIDE = 0  # 0000
LEFT = 1    # 0001
RIGHT = 2   # 0010
BOTTOM = 4  # 0100
TOP = 8     # 1000

EPSILON = 1e-7

BIT_ORDER = ("TOP", "BOTTOM", "RIGHT", "LEFT")
BIT_MASKS = {"TOP": TOP, "BOTTOM": BOTTOM, "RIGHT": RIGHT, "LEFT": LEFT}
BIT_LETTERS = {"TOP": "T", "BOTTOM": "B", "RIGHT": "R", "LEFT": "L"}

REGION_NAMES: Dict[int, str] = {
    0: "Inside",
    1: "Left",
    2: "Right",
    4: "Bottom",
    5: "Bottom-Left",
    6: "Bottom-Right",
    8: "Top",
    9: "Top-Left",
    10: "Top-Right",
}

REGION_EXPLORE_ORDER = [0, 8, 4, 2, 1, 9, 10, 5, 6]


def compute_outcode(x: float, y: float, xmin: float, ymin: float, xmax: float, ymax: float) -> int:
    """Compute standard 4-bit region code [TOP, BOTTOM, RIGHT, LEFT]."""
    code = INSIDE
    if x < xmin - EPSILON:
        code |= LEFT
    elif x > xmax + EPSILON:
        code |= RIGHT
    if y < ymin - EPSILON:
        code |= BOTTOM
    elif y > ymax + EPSILON:
        code |= TOP
    return code


def outcode_to_str(code: int) -> str:
    """Format 4-bit OutCode as binary string [T B R L]."""
    t = "1" if (code & TOP) else "0"
    b = "1" if (code & BOTTOM) else "0"
    r = "1" if (code & RIGHT) else "0"
    l = "1" if (code & LEFT) else "0"
    return f"{t}{b}{r}{l}"


def outcode_breakdown(x: float, y: float, xmin: float, ymin: float, xmax: float, ymax: float) -> Dict[str, Any]:
    """Provide detailed breakdown of conditions causing each bit in the OutCode."""
    code = compute_outcode(x, y, xmin, ymin, xmax, ymax)
    t = bool(code & TOP)
    b = bool(code & BOTTOM)
    r = bool(code & RIGHT)
    l = bool(code & LEFT)
    reasons = []
    if t:
        reasons.append(f"y > ymax ({y:.2f} > {ymax:.2f})")
    if b:
        reasons.append(f"y < ymin ({y:.2f} < {ymin:.2f})")
    if r:
        reasons.append(f"x > xmax ({x:.2f} > {xmax:.2f})")
    if l:
        reasons.append(f"x < xmin ({x:.2f} < {xmin:.2f})")
    if not reasons:
        reasons.append(f"Inside window [{xmin:.1f} ≤ {x:.1f} ≤ {xmax:.1f}, {ymin:.1f} ≤ {y:.1f} ≤ {ymax:.1f}]")
    return {
        "code": code,
        "code_str": outcode_to_str(code),
        "region_name": REGION_NAMES.get(code, "Outside"),
        "bits": {"TOP": t, "BOTTOM": b, "RIGHT": r, "LEFT": l},
        "reasons": reasons,
    }


def _bit_tests(x: float, y: float, xmin: float, ymin: float, xmax: float, ymax: float) -> List[Dict[str, Any]]:
    """Classroom-friendly yes/no tests for each TBRL bit."""
    return [
        {
            "name": "TOP", "letter": "T", "question": "Above the window?",
            "condition": f"y > {ymax:.1f}", "lhs": y, "rhs": ymax,
            "set": y > ymax + EPSILON, "compare": f"{y:.2f} > {ymax:.1f}",
        },
        {
            "name": "BOTTOM", "letter": "B", "question": "Below the window?",
            "condition": f"y < {ymin:.1f}", "lhs": y, "rhs": ymin,
            "set": y < ymin - EPSILON, "compare": f"{y:.2f} < {ymin:.1f}",
        },
        {
            "name": "RIGHT", "letter": "R", "question": "To the right?",
            "condition": f"x > {xmax:.1f}", "lhs": x, "rhs": xmax,
            "set": x > xmax + EPSILON, "compare": f"{x:.2f} > {xmax:.1f}",
        },
        {
            "name": "LEFT", "letter": "L", "question": "To the left?",
            "condition": f"x < {xmin:.1f}", "lhs": x, "rhs": xmin,
            "set": x < xmin - EPSILON, "compare": f"{x:.2f} < {xmin:.1f}",
        },
    ]


def _code_equation(label: str, x: float, y: float, xmin: float, ymin: float, xmax: float, ymax: float) -> str:
    tests = _bit_tests(x, y, xmin, ymin, xmax, ymax)
    code = compute_outcode(x, y, xmin, ymin, xmax, ymax)
    lines = [f"{label} = ({x:.2f}, {y:.2f})", ""]
    for t in tests:
        bit = "1" if t["set"] else "0"
        lines.append(f"{t['letter']}  {t['question']:18}  {t['compare']:18}  →  {bit}")
    lines.append("")
    lines.append(f"Region code  TBRL = {outcode_to_str(code)}   ({REGION_NAMES.get(code, 'Outside')})")
    return "\n".join(lines)


def _shared_sides(and_val: int) -> List[str]:
    sides = []
    if and_val & TOP:
        sides.append("TOP")
    if and_val & BOTTOM:
        sides.append("BOTTOM")
    if and_val & RIGHT:
        sides.append("RIGHT")
    if and_val & LEFT:
        sides.append("LEFT")
    return sides


def cohen_sutherland_trace(
    x1: float, y1: float, x2: float, y2: float,
    xmin: float = -4.0, ymin: float = -3.0,
    xmax: float = 4.0, ymax: float = 3.0
) -> List[VisualizationStep]:
    """
    Classroom walkthrough of Cohen-Sutherland line clipping.

    The mathematical loop is unchanged: 4-bit TBRL codes, bitwise OR/AND
    trivial tests, TOP→BOTTOM→RIGHT→LEFT boundary selection, and parametric
    intersection. Each emitted step reveals one idea and carries the real
    algorithm state for the canvas.
    """
    orig_p1 = (float(x1), float(y1))
    orig_p2 = (float(x2), float(y2))
    cur_x1, cur_y1 = orig_p1
    cur_x2, cur_y2 = orig_p2

    code1 = compute_outcode(cur_x1, cur_y1, xmin, ymin, xmax, ymax)
    code2 = compute_outcode(cur_x2, cur_y2, xmin, ymin, xmax, ymax)

    steps: List[VisualizationStep] = []
    step_num = 1
    intersections: List[Dict[str, Any]] = []
    discarded_segs: List[Tuple[float, float, float, float]] = []

    def make_clipping_payload(
        current_coords: Tuple[float, float, float, float],
        c1: int, c2: int,
        status: str = "evaluating",
        active_boundary: Optional[str] = None,
        shared_region: Optional[str] = None,
        selected_pt: Optional[str] = None,
        active_bit: Optional[str] = None,
        decision: str = "",
        formula_info: Optional[Dict[str, Any]] = None,
        anim: Optional[Dict[str, Any]] = None,
        is_final: bool = False,
        focus: str = "meet",
        caption: str = "",
        show_p1_code: bool = False,
        show_p2_code: bool = False,
        show_or: bool = False,
        show_and: bool = False,
    ) -> Dict[str, Any]:
        segs = []
        if current_coords != (orig_p1[0], orig_p1[1], orig_p2[0], orig_p2[1]):
            segs.append({
                "coords": (orig_p1[0], orig_p1[1], orig_p2[0], orig_p2[1]),
                "color": COLORS["text_muted"],
                "dashed": True,
                "width": 1.5,
                "p1_label": "",
                "p2_label": "",
            })
        for dseg in discarded_segs:
            segs.append({
                "coords": dseg,
                "color": COLORS["danger"],
                "dashed": True,
                "width": 1.8,
                "p1_label": "",
                "p2_label": "",
            })
        active_color = COLORS["success"] if (is_final and status == "accepted") else (
            COLORS["danger"] if status == "rejected" else COLORS["accent_gold"]
        )
        segs.append({
            "coords": current_coords,
            "color": active_color,
            "dashed": (status == "rejected"),
            "width": 3.6 if (is_final and status == "accepted") else 2.6,
            "p1_label": f"P1({current_coords[0]:.2f},{current_coords[1]:.2f})",
            "p2_label": f"P2({current_coords[2]:.2f},{current_coords[3]:.2f})",
        })
        return {
            "view_tab": "clip_line",
            "xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax,
            "orig_p1": orig_p1, "orig_p2": orig_p2,
            "current_p1": (current_coords[0], current_coords[1]),
            "current_p2": (current_coords[2], current_coords[3]),
            "current_seg": current_coords,
            "segments": segs,
            "intersections": list(intersections),
            "discarded_segs": list(discarded_segs),
            "code1": c1, "code2": c2,
            "code1_str": outcode_to_str(c1),
            "code2_str": outcode_to_str(c2),
            "or_result": c1 | c2,
            "or_str": outcode_to_str(c1 | c2),
            "and_result": c1 & c2,
            "and_str": outcode_to_str(c1 & c2),
            "active_boundary": active_boundary,
            "shared_region": shared_region,
            "selected_pt": selected_pt,
            "active_bit": active_bit,
            "decision": decision,
            "formula_info": formula_info,
            "anim": anim,
            "status": status,
            "is_final": is_final,
            "focus": focus,
            "caption": caption,
            "show_p1_code": show_p1_code,
            "show_p2_code": show_p2_code,
            "show_or": show_or,
            "show_and": show_and,
        }

    def add_step(title: str, equation: str, explanation: str, values: Dict[str, Any],
                 metrics: Dict[str, Any], payload: Dict[str, Any]) -> None:
        nonlocal step_num
        values = dict(values)
        values.setdefault("code1_str", payload["code1_str"])
        values.setdefault("code2_str", payload["code2_str"])
        values.setdefault("or_str", payload["or_str"])
        values.setdefault("and_str", payload["and_str"])
        values.setdefault("caption", payload.get("caption", ""))
        values.setdefault("focus", payload.get("focus", ""))
        steps.append(VisualizationStep(
            index=step_num,
            title=title,
            equation=equation,
            explanation=explanation,
            values=values,
            metrics=metrics,
            render_data=RenderData(mode="clipping", clipping_data=payload),
        ))
        step_num += 1

    bd1 = outcode_breakdown(cur_x1, cur_y1, xmin, ymin, xmax, ymax)
    bd2 = outcode_breakdown(cur_x2, cur_y2, xmin, ymin, xmax, ymax)
    p1_inside = code1 == INSIDE
    p2_inside = code2 == INSIDE
    p1_desc = "inside the window" if p1_inside else f"in the {bd1['region_name']} region"
    p2_desc = "inside the window" if p2_inside else f"in the {bd2['region_name']} region"

    add_step(
        "A line and a window",
        (
            f"Window  [{xmin:.1f}, {ymin:.1f}]  to  [{xmax:.1f}, {ymax:.1f}]\n"
            f"Line    P1({cur_x1:.2f}, {cur_y1:.2f})  →  P2({cur_x2:.2f}, {cur_y2:.2f})"
        ),
        (
            "Only the part of a line that sits inside the window should be drawn. "
            f"P1 is {p1_desc}; P2 is {p2_desc}. "
            "Next we give each endpoint a 4-bit region code so we can decide quickly."
        ),
        {
            "stage": "input_overview",
            "P1": (cur_x1, cur_y1), "P1_location": p1_desc,
            "P2": (cur_x2, cur_y2), "P2_location": p2_desc,
            "xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax,
        },
        {"Stage": "Meet the line", "P1": p1_desc, "P2": p2_desc},
        make_clipping_payload(
            (cur_x1, cur_y1, cur_x2, cur_y2), code1, code2,
            status="init", decision="Look at the line",
            focus="meet",
            caption="The teal rectangle is the visible window. We will keep only the piece of the line that lies inside it.",
            anim={"type": "scene_enter"},
        ),
    )

    add_step(
        "P1's region code",
        _code_equation("P1", cur_x1, cur_y1, xmin, ymin, xmax, ymax),
        (
            "Each bit answers one question: is this point outside on that side? "
            "A 1 means yes — the point is outside that edge. "
            f"P1's code is {outcode_to_str(code1)} ({bd1['region_name']})."
        ),
        {
            "stage": "code_p1",
            "P1": (cur_x1, cur_y1), "P1_code": outcode_to_str(code1),
            "region": bd1["region_name"], "reasons": bd1["reasons"],
        },
        {"Stage": "Code P1", "P1 code": outcode_to_str(code1), "Region": bd1["region_name"]},
        make_clipping_payload(
            (cur_x1, cur_y1, cur_x2, cur_y2), code1, code2,
            status="evaluating", selected_pt="P1",
            decision=f"P1 = {outcode_to_str(code1)}",
            focus="code_p1",
            caption=f"P1 is {p1_desc}. Its bits light up one question at a time: Top, Bottom, Right, Left.",
            show_p1_code=True,
            anim={"type": "bit_reveal", "target": "P1"},
        ),
    )

    add_step(
        "P2's region code",
        _code_equation("P2", cur_x2, cur_y2, xmin, ymin, xmax, ymax),
        (
            f"Same four questions for P2. Its code is {outcode_to_str(code2)} ({bd2['region_name']}). "
            "With both codes in hand, two bitwise tests will tell us whether to keep, discard, or clip the line."
        ),
        {
            "stage": "code_p2",
            "P2": (cur_x2, cur_y2), "P2_code": outcode_to_str(code2),
            "region": bd2["region_name"], "reasons": bd2["reasons"],
        },
        {"Stage": "Code P2", "P2 code": outcode_to_str(code2), "Region": bd2["region_name"]},
        make_clipping_payload(
            (cur_x1, cur_y1, cur_x2, cur_y2), code1, code2,
            status="evaluating", selected_pt="P2",
            decision=f"P2 = {outcode_to_str(code2)}",
            focus="code_p2",
            caption=f"P2 is {p2_desc}. Now both endpoints have a compact 4-bit address.",
            show_p1_code=True, show_p2_code=True,
            anim={"type": "bit_reveal", "target": "P2"},
        ),
    )

    or_val = code1 | code2
    and_val = code1 & code2
    trivial_accept = or_val == 0
    trivial_reject = and_val != 0
    shared_sides = _shared_sides(and_val)
    shared_str = " & ".join(shared_sides) if shared_sides else "None"

    or_caption = (
        "OR is 0000 — every bit is off. Both points are inside, so the whole line is visible."
        if trivial_accept else
        "OR is not 0000 — at least one point is outside. The line is not entirely inside."
    )
    add_step(
        "Is the whole line inside?",
        (
            f"P1  {outcode_to_str(code1)}\n"
            f"P2  {outcode_to_str(code2)}\n"
            f"OR  {outcode_to_str(or_val)}   "
            + ("= 0000  →  keep the whole line" if trivial_accept else "≠ 0000  →  not entirely inside")
        ),
        (
            "Bitwise OR turns a bit on if it is on in either code. "
            "If the result is 0000, neither point is outside — accept the line immediately. "
            + ("That is the case here, so we are done." if trivial_accept else "Here OR is not zero, so we ask one more question.")
        ),
        {
            "stage": "or_test",
            "P1_code": outcode_to_str(code1), "P2_code": outcode_to_str(code2),
            "OR_result": outcode_to_str(or_val),
            "decision": "ACCEPT" if trivial_accept else "NOT INSIDE",
        },
        {"Stage": "OR test", "OR": outcode_to_str(or_val), "Decision": "ACCEPT" if trivial_accept else "continue"},
        make_clipping_payload(
            (cur_x1, cur_y1, cur_x2, cur_y2), code1, code2,
            status="accepted" if trivial_accept else "evaluating",
            decision="Accept" if trivial_accept else "Not entirely inside",
            focus="or_test",
            caption=or_caption,
            show_p1_code=True, show_p2_code=True, show_or=True,
            anim={"type": "or_combine"},
        ),
    )

    iteration = 0
    final_status = "unknown"

    if trivial_accept:
        final_status = "accepted"
    else:
        and_caption = (
            f"AND is {outcode_to_str(and_val)} — both points share the {shared_str} side. The line never enters the window."
            if trivial_reject else
            "AND is 0000 — the points do not share an outside side. The line must cross the window, so we clip."
        )
        add_step(
            "Is the whole line outside?",
            (
                f"P1  {outcode_to_str(code1)}\n"
                f"P2  {outcode_to_str(code2)}\n"
                f"AND {outcode_to_str(and_val)}   "
                + (f"≠ 0000  →  discard  (shared {shared_str})" if trivial_reject else "= 0000  →  the line crosses the window")
            ),
            (
                "Bitwise AND keeps a bit only if it is on in both codes. "
                "A shared 1 means both points lie on the same outside side, so the segment cannot enter the window. "
                + ("We reject the line with no intersection math." if trivial_reject
                   else "No shared outside bit, so the line is partially visible — we must find where it hits the window.")
            ),
            {
                "stage": "and_test",
                "P1_code": outcode_to_str(code1), "P2_code": outcode_to_str(code2),
                "AND_result": outcode_to_str(and_val),
                "decision": "REJECT" if trivial_reject else "CLIP",
            },
            {"Stage": "AND test", "AND": outcode_to_str(and_val), "Decision": "REJECT" if trivial_reject else "CLIP"},
            make_clipping_payload(
                (cur_x1, cur_y1, cur_x2, cur_y2), code1, code2,
                status="rejected" if trivial_reject else "clipping",
                shared_region=shared_sides[0] if shared_sides else None,
                decision="Reject" if trivial_reject else "Clip the line",
                focus="and_test",
                caption=and_caption,
                show_p1_code=True, show_p2_code=True, show_or=True, show_and=True,
                anim={"type": "and_combine" if trivial_reject else "eval_bitwise"},
            ),
        )

        if trivial_reject:
            final_status = "rejected"
        else:
            while True:
                if (code1 | code2) == 0:
                    final_status = "accepted"
                    if iteration > 0:
                        add_step(
                            "Check the shortened line",
                            (
                                f"P1  {outcode_to_str(code1)}\n"
                                f"P2  {outcode_to_str(code2)}\n"
                                f"OR  {outcode_to_str(code1 | code2)}  = 0000"
                            ),
                            "Both endpoints now sit on or inside the window. The leftover segment is the visible piece.",
                            {"stage": "recheck", "decision": "ACCEPT"},
                            {"Stage": "Recheck", "Decision": "ACCEPT"},
                            make_clipping_payload(
                                (cur_x1, cur_y1, cur_x2, cur_y2), code1, code2,
                                status="accepted", decision="Accept",
                                focus="or_test",
                                caption="OR is 0000 again. Nothing outside remains — this is the clipped line.",
                                show_p1_code=True, show_p2_code=True, show_or=True,
                                anim={"type": "accept_glow"},
                            ),
                        )
                    break

                if (code1 & code2) != 0:
                    final_status = "rejected"
                    sides = _shared_sides(code1 & code2)
                    add_step(
                        "Check the shortened line",
                        (
                            f"P1  {outcode_to_str(code1)}\n"
                            f"P2  {outcode_to_str(code2)}\n"
                            f"AND {outcode_to_str(code1 & code2)}  ≠ 0000"
                        ),
                        f"After clipping, both points still share the {' & '.join(sides)} side. The line never enters the window, so we discard it.",
                        {"stage": "recheck", "decision": "REJECT"},
                        {"Stage": "Recheck", "Decision": "REJECT"},
                        make_clipping_payload(
                            (cur_x1, cur_y1, cur_x2, cur_y2), code1, code2,
                            status="rejected",
                            shared_region=sides[0] if sides else None,
                            decision="Reject",
                            focus="and_test",
                            caption="AND is no longer zero. The remaining piece is still fully outside.",
                            show_p1_code=True, show_p2_code=True, show_or=True, show_and=True,
                            anim={"type": "reject_flash"},
                        ),
                    )
                    break

                iteration += 1
                code_out = code1 if code1 != 0 else code2
                pt_label = "P1" if code1 != 0 else "P2"
                out_x = cur_x1 if code1 != 0 else cur_x2
                out_y = cur_y1 if code1 != 0 else cur_y2

                clip_edge = ""
                active_bit = ""
                boundary_eq = ""
                formula_latex = ""
                formula_sub = ""
                arithmetic_steps: List[str] = []
                x_int, y_int = 0.0, 0.0

                dx = cur_x2 - cur_x1
                dy = cur_y2 - cur_y1

                if code_out & TOP:
                    clip_edge = "TOP"
                    active_bit = "TOP (1000)"
                    boundary_eq = f"y = {ymax:.2f}"
                    formula_latex = "x = x₁ + (x₂ − x₁) · (ymax − y₁) / (y₂ − y₁),   y = ymax"
                    if abs(dy) > 1e-12:
                        t = (ymax - cur_y1) / dy
                        x_int = cur_x1 + dx * t
                        y_int = ymax
                        formula_sub = f"x = {cur_x1:.2f} + ({dx:.2f}) · ({ymax:.2f} − {cur_y1:.2f}) / ({dy:.2f})"
                        arithmetic_steps = [
                            f"Δx = {dx:.2f},  Δy = {dy:.2f}",
                            f"t = ({ymax:.2f} − {cur_y1:.2f}) / {dy:.2f} ≈ {t:.4f}",
                            f"x = {cur_x1:.2f} + {dx:.2f} × {t:.4f} = {x_int:.2f}",
                            f"y = ymax = {ymax:.2f}",
                        ]
                    else:
                        x_int = cur_x1
                        y_int = ymax
                elif code_out & BOTTOM:
                    clip_edge = "BOTTOM"
                    active_bit = "BOTTOM (0100)"
                    boundary_eq = f"y = {ymin:.2f}"
                    formula_latex = "x = x₁ + (x₂ − x₁) · (ymin − y₁) / (y₂ − y₁),   y = ymin"
                    if abs(dy) > 1e-12:
                        t = (ymin - cur_y1) / dy
                        x_int = cur_x1 + dx * t
                        y_int = ymin
                        formula_sub = f"x = {cur_x1:.2f} + ({dx:.2f}) · ({ymin:.2f} − {cur_y1:.2f}) / ({dy:.2f})"
                        arithmetic_steps = [
                            f"Δx = {dx:.2f},  Δy = {dy:.2f}",
                            f"t = ({ymin:.2f} − {cur_y1:.2f}) / {dy:.2f} ≈ {t:.4f}",
                            f"x = {cur_x1:.2f} + {dx:.2f} × {t:.4f} = {x_int:.2f}",
                            f"y = ymin = {ymin:.2f}",
                        ]
                    else:
                        x_int = cur_x1
                        y_int = ymin
                elif code_out & RIGHT:
                    clip_edge = "RIGHT"
                    active_bit = "RIGHT (0010)"
                    boundary_eq = f"x = {xmax:.2f}"
                    formula_latex = "y = y₁ + (y₂ − y₁) · (xmax − x₁) / (x₂ − x₁),   x = xmax"
                    if abs(dx) > 1e-12:
                        t = (xmax - cur_x1) / dx
                        y_int = cur_y1 + dy * t
                        x_int = xmax
                        formula_sub = f"y = {cur_y1:.2f} + ({dy:.2f}) · ({xmax:.2f} − {cur_x1:.2f}) / ({dx:.2f})"
                        arithmetic_steps = [
                            f"Δx = {dx:.2f},  Δy = {dy:.2f}",
                            f"t = ({xmax:.2f} − {cur_x1:.2f}) / {dx:.2f} ≈ {t:.4f}",
                            f"y = {cur_y1:.2f} + {dy:.2f} × {t:.4f} = {y_int:.2f}",
                            f"x = xmax = {xmax:.2f}",
                        ]
                    else:
                        x_int = xmax
                        y_int = cur_y1
                elif code_out & LEFT:
                    clip_edge = "LEFT"
                    active_bit = "LEFT (0001)"
                    boundary_eq = f"x = {xmin:.2f}"
                    formula_latex = "y = y₁ + (y₂ − y₁) · (xmin − x₁) / (x₂ − x₁),   x = xmin"
                    if abs(dx) > 1e-12:
                        t = (xmin - cur_x1) / dx
                        y_int = cur_y1 + dy * t
                        x_int = xmin
                        formula_sub = f"y = {cur_y1:.2f} + ({dy:.2f}) · ({xmin:.2f} − {cur_x1:.2f}) / ({dx:.2f})"
                        arithmetic_steps = [
                            f"Δx = {dx:.2f},  Δy = {dy:.2f}",
                            f"t = ({xmin:.2f} − {cur_x1:.2f}) / {dx:.2f} ≈ {t:.4f}",
                            f"y = {cur_y1:.2f} + {dy:.2f} × {t:.4f} = {y_int:.2f}",
                            f"x = xmin = {xmin:.2f}",
                        ]
                    else:
                        x_int = xmin
                        y_int = cur_y1

                if abs(x_int - xmin) < EPSILON:
                    x_int = xmin
                elif abs(x_int - xmax) < EPSILON:
                    x_int = xmax
                if abs(y_int - ymin) < EPSILON:
                    y_int = ymin
                elif abs(y_int - ymax) < EPSILON:
                    y_int = ymax

                is_corner = (abs(x_int - xmin) < 1e-4 or abs(x_int - xmax) < 1e-4) and \
                            (abs(y_int - ymin) < 1e-4 or abs(y_int - ymax) < 1e-4)
                corner_tag = " — a window corner" if is_corner else ""

                add_step(
                    f"Choose the outside endpoint" + (f"  ·  clip {iteration}" if iteration > 1 else ""),
                    (
                        f"{pt_label}({out_x:.2f}, {out_y:.2f})  code {outcode_to_str(code_out)}\n"
                        f"First set bit: {clip_edge}   →   clip against  {boundary_eq}"
                    ),
                    (
                        f"{pt_label} is still outside, so we clip it. "
                        "The algorithm tests bits in a fixed order — Top, then Bottom, then Right, then Left — "
                        f"and the first 1 it finds is {clip_edge}."
                    ),
                    {
                        "stage": "select_boundary",
                        "iteration": iteration,
                        "selected_endpoint": pt_label,
                        "boundary": clip_edge,
                        "boundary_equation": boundary_eq,
                    },
                    {"Clip": iteration, "Endpoint": pt_label, "Edge": clip_edge},
                    make_clipping_payload(
                        (cur_x1, cur_y1, cur_x2, cur_y2), code1, code2,
                        status="clipping",
                        active_boundary=clip_edge,
                        selected_pt=pt_label,
                        active_bit=clip_edge,
                        decision=f"Clip {pt_label} on {clip_edge}",
                        formula_info={
                            "type": "select",
                            "target": pt_label,
                            "boundary": clip_edge,
                            "equation": boundary_eq,
                            "bit": active_bit,
                        },
                        anim={"type": "boundary_focus", "boundary": clip_edge},
                        focus="select",
                        caption=f"{pt_label} is outside. We clip against the {clip_edge.lower()} edge first.",
                        show_p1_code=True, show_p2_code=True,
                    ),
                )

                intersections.append({"x": x_int, "y": y_int, "edge": clip_edge, "is_corner": is_corner})

                arith_block = "\n".join(arithmetic_steps) if arithmetic_steps else formula_sub
                add_step(
                    f"Where the line meets the window{corner_tag}",
                    (
                        f"{formula_latex}\n"
                        f"{arith_block}\n"
                        f"Intersection  I({x_int:.2f}, {y_int:.2f})"
                    ),
                    (
                        f"This is the point where the line crosses the {clip_edge.lower()} edge ({boundary_eq}). "
                        f"Everything of {pt_label} beyond I is outside and will be thrown away."
                    ),
                    {
                        "stage": "calculate_intersection",
                        "iteration": iteration,
                        "intersection": (round(x_int, 2), round(y_int, 2)),
                        "edge": clip_edge,
                        "is_corner": is_corner,
                        "arithmetic": arithmetic_steps,
                    },
                    {"I.x": f"{x_int:.2f}", "I.y": f"{y_int:.2f}", "Edge": clip_edge},
                    make_clipping_payload(
                        (cur_x1, cur_y1, cur_x2, cur_y2), code1, code2,
                        status="clipping",
                        active_boundary=clip_edge,
                        selected_pt=pt_label,
                        active_bit=clip_edge,
                        decision=f"I({x_int:.2f}, {y_int:.2f})",
                        formula_info={
                            "type": "calculate",
                            "formula_latex": formula_latex,
                            "formula_sub": formula_sub,
                            "arithmetic": arithmetic_steps,
                            "intersection": (x_int, y_int),
                            "is_corner": is_corner,
                        },
                        anim={"type": "intersection_marker", "pt": (x_int, y_int)},
                        focus="intersect",
                        caption=f"The line meets the {clip_edge.lower()} edge at I({x_int:.2f}, {y_int:.2f}).",
                        show_p1_code=True, show_p2_code=True,
                    ),
                )

                old_x, old_y = (cur_x1, cur_y1) if code_out == code1 else (cur_x2, cur_y2)
                discarded_segs.append((old_x, old_y, x_int, y_int))

                if code_out == code1:
                    cur_x1, cur_y1 = x_int, y_int
                    code1 = compute_outcode(cur_x1, cur_y1, xmin, ymin, xmax, ymax)
                    new_code = code1
                else:
                    cur_x2, cur_y2 = x_int, y_int
                    code2 = compute_outcode(cur_x2, cur_y2, xmin, ymin, xmax, ymax)
                    new_code = code2

                add_step(
                    f"Move {pt_label} onto the window",
                    (
                        f"{pt_label}  ({old_x:.2f}, {old_y:.2f})  →  ({x_int:.2f}, {y_int:.2f})\n"
                        f"New code for {pt_label}  =  {outcode_to_str(new_code)}"
                    ),
                    (
                        f"The outside stub is gone. {pt_label} now sits on the window edge, "
                        f"so its {clip_edge.lower()} bit turns off. We repeat the OR / AND tests with the shorter line."
                    ),
                    {
                        "stage": "update_endpoint",
                        "iteration": iteration,
                        "updated_point": pt_label,
                        "new_coords": (round(x_int, 2), round(y_int, 2)),
                        "new_code": outcode_to_str(new_code),
                    },
                    {"Moved": pt_label, "New code": outcode_to_str(new_code)},
                    make_clipping_payload(
                        (cur_x1, cur_y1, cur_x2, cur_y2), code1, code2,
                        status="clipping",
                        active_boundary=clip_edge,
                        selected_pt=pt_label,
                        decision=f"{pt_label} → {outcode_to_str(new_code)}",
                        formula_info={
                            "type": "update",
                            "updated_pt": pt_label,
                            "old_coords": (old_x, old_y),
                            "new_coords": (x_int, y_int),
                            "new_code": outcode_to_str(new_code),
                        },
                        anim={
                            "type": "endpoint_move",
                            "target": pt_label,
                            "from": (old_x, old_y),
                            "to": (x_int, y_int),
                        },
                        focus="update",
                        caption=f"{pt_label} slides to the edge. Its new code is {outcode_to_str(new_code)}.",
                        show_p1_code=True, show_p2_code=True,
                    ),
                )

    if final_status == "accepted":
        summary_eq = (
            f"Visible line  ({cur_x1:.2f}, {cur_y1:.2f})  →  ({cur_x2:.2f}, {cur_y2:.2f})\n"
            f"Original      ({orig_p1[0]:.2f}, {orig_p1[1]:.2f})  →  ({orig_p2[0]:.2f}, {orig_p2[1]:.2f})"
        )
        if iteration == 0:
            summary_expl = "Both endpoints were already inside. The original line is drawn unchanged."
            caption = "Nothing to clip. The whole line is visible."
        else:
            summary_expl = (
                f"After {iteration} clip{'s' if iteration != 1 else ''}, both codes are 0000. "
                "The green segment is what the rasterizer will actually draw."
            )
            caption = "The green segment is the visible piece. The dashed red stubs were discarded."
        result_title = "Clipping complete"
    else:
        summary_eq = (
            f"Visible line  none\n"
            f"Original      ({orig_p1[0]:.2f}, {orig_p1[1]:.2f})  →  ({orig_p2[0]:.2f}, {orig_p2[1]:.2f})"
        )
        summary_expl = (
            "The line never enters the window, so nothing is drawn. "
            "Cohen–Sutherland can prove that with a single AND — no intersection math required."
        )
        caption = "The line is fully outside. Nothing is sent on to drawing."
        result_title = "Clipping complete"

    add_step(
        result_title,
        summary_eq,
        summary_expl,
        {
            "stage": "final_result",
            "status": final_status,
            "accepted_segment": ((cur_x1, cur_y1), (cur_x2, cur_y2)) if final_status == "accepted" else None,
            "original_segment": (orig_p1, orig_p2),
            "iterations": iteration,
            "intersections_count": len(intersections),
        },
        {
            "accepted": (final_status == "accepted"),
            "rejected": (final_status == "rejected"),
            "clipped": (len(intersections) > 0),
            "iterations": iteration,
            "intersections": len(intersections),
            "final_status": final_status,
        },
        make_clipping_payload(
            (cur_x1, cur_y1, cur_x2, cur_y2), code1, code2,
            status=final_status,
            decision="Visible" if final_status == "accepted" else "Discarded",
            is_final=True,
            anim={"type": "final_summary"},
            focus="result",
            caption=caption,
            show_p1_code=True, show_p2_code=True,
        ),
    )

    return steps


def cohen_sutherland_clip(
    x1: float, y1: float, x2: float, y2: float,
    xmin: float, ymin: float, xmax: float, ymax: float
) -> Optional[Tuple[Tuple[float, float], Tuple[float, float]]]:
    """
    Pure Cohen-Sutherland line clipping computation.
    Returns:
        ((clipped_x1, clipped_y1), (clipped_x2, clipped_y2)) if line segment is visible.
        None if line segment is completely outside (trivially rejected).
    """
    code1 = compute_outcode(x1, y1, xmin, ymin, xmax, ymax)
    code2 = compute_outcode(x2, y2, xmin, ymin, xmax, ymax)

    while True:
        if (code1 | code2) == 0:
            return ((float(x1), float(y1)), (float(x2), float(y2)))
        elif (code1 & code2) != 0:
            return None
        else:
            code_out = code1 if code1 != 0 else code2

            if code_out & TOP:
                x_int = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1) if abs(y2 - y1) > 1e-12 else x1
                y_int = ymax
            elif code_out & BOTTOM:
                x_int = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1) if abs(y2 - y1) > 1e-12 else x1
                y_int = ymin
            elif code_out & RIGHT:
                y_int = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1) if abs(x2 - x1) > 1e-12 else y1
                x_int = xmax
            elif code_out & LEFT:
                y_int = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1) if abs(x2 - x1) > 1e-12 else y1
                x_int = xmin
            else:
                return None

            if code_out == code1:
                x1, y1 = x_int, y_int
                code1 = compute_outcode(x1, y1, xmin, ymin, xmax, ymax)
            else:
                x2, y2 = x_int, y_int
                code2 = compute_outcode(x2, y2, xmin, ymin, xmax, ymax)


def _region_payload(
    lesson: str,
    xmin: float, ymin: float, xmax: float, ymax: float,
    selected_code: Optional[int] = None,
    bit_focus: Optional[str] = None,
    caption: str = "",
    show_all_labels: bool = False,
) -> Dict[str, Any]:
    return {
        "view_tab": "region_codes",
        "lesson": lesson,
        "xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax,
        "selected_code": selected_code if selected_code is not None else -1,
        "active_region_code": selected_code,
        "bit_focus": bit_focus,
        "caption": caption,
        "show_all_labels": show_all_labels,
        "anim": {"type": "region_pulse"},
    }


def build_region_codes_steps(
    active_code: int = 0,
    xmin: float = -4.0, ymin: float = -3.0,
    xmax: float = 4.0, ymax: float = 3.0,
    selected_code: Optional[int] = None,
) -> List[VisualizationStep]:
    """
    First lesson: what the four bits mean, then the nine regions.

    `active_code` / `selected_code` are accepted so a canvas click can rebuild
    the lesson and jump to the matching region.
    """
    _ = selected_code  # accepted for compatibility; click handling jumps by values
    steps: List[VisualizationStep] = []

    bit_lessons = [
        ("TOP", "Top", f"y > {ymax:.1f}", "Is the point above the window?", "1000"),
        ("BOTTOM", "Bottom", f"y < {ymin:.1f}", "Is the point below the window?", "0100"),
        ("RIGHT", "Right", f"x > {xmax:.1f}", "Is the point to the right of the window?", "0010"),
        ("LEFT", "Left", f"x < {xmin:.1f}", "Is the point to the left of the window?", "0001"),
    ]

    intro = [
        VisualizationStep(
            index=1,
            title="The clipping window",
            equation=(
                f"Left    x = {xmin:.1f}\n"
                f"Right   x = {xmax:.1f}\n"
                f"Bottom  y = {ymin:.1f}\n"
                f"Top     y = {ymax:.1f}"
            ),
            explanation=(
                "Four axis-aligned edges make a rectangle — the visible screen. "
                "Extend those four lines across the plane and they cut space into nine regions: "
                "the window, four sides, and four corners."
            ),
            values={"tab": "region_codes", "lesson": "window", "caption": "Four edges, one window."},
            metrics={"Lesson": "The window"},
            render_data=RenderData(mode="clipping", clipping_data=_region_payload(
                "window", xmin, ymin, xmax, ymax,
                caption="This teal rectangle is the clipping window. Only what sits inside it will be drawn.",
            )),
        ),
    ]
    steps.extend(intro)

    for i, (bit, name, cond, question, mask) in enumerate(bit_lessons, start=2):
        steps.append(VisualizationStep(
            index=i,
            title=f"The {name} bit",
            equation=f"{name} bit  =  1  when  {cond}\nMask  {mask}     Question: {question}",
            explanation=(
                f"{question} If yes, that bit is 1. "
                "Region codes are just four of these yes/no answers packed into TBRL order: Top, Bottom, Right, Left."
            ),
            values={"tab": "region_codes", "lesson": "bits", "bit_focus": bit, "caption": question},
            metrics={"Bit": name, "When": cond},
            render_data=RenderData(mode="clipping", clipping_data=_region_payload(
                "bits", xmin, ymin, xmax, ymax,
                bit_focus=bit,
                caption=f"{question}  The shaded half-plane is where this bit is 1.",
            )),
        ))

    steps.append(VisualizationStep(
        index=6,
        title="Nine regions, nine codes",
        equation="TBRL  =  Top  Bottom  Right  Left\nInside the window  =  0000",
        explanation=(
            "Every point in the plane belongs to exactly one region and inherits that region's code. "
            "Click any region — or step forward — to see why its bits are on or off."
        ),
        values={"tab": "region_codes", "lesson": "map", "caption": "Click a region to inspect its code."},
        metrics={"Lesson": "Nine regions"},
        render_data=RenderData(mode="clipping", clipping_data=_region_payload(
            "map", xmin, ymin, xmax, ymax,
            show_all_labels=True,
            caption="The window is 0000. Side regions have one bit on. Corners have two.",
        )),
    ))

    for idx, code in enumerate(REGION_EXPLORE_ORDER, start=7):
        name = REGION_NAMES.get(code, "Unknown")
        code_s = outcode_to_str(code)
        tests = []
        if code & TOP:
            tests.append(f"T = 1   because y > {ymax:.1f}")
        else:
            tests.append(f"T = 0   not above the window")
        if code & BOTTOM:
            tests.append(f"B = 1   because y < {ymin:.1f}")
        else:
            tests.append(f"B = 0   not below the window")
        if code & RIGHT:
            tests.append(f"R = 1   because x > {xmax:.1f}")
        else:
            tests.append(f"R = 0   not to the right")
        if code & LEFT:
            tests.append(f"L = 1   because x < {xmin:.1f}")
        else:
            tests.append(f"L = 0   not to the left")

        why = "No bits are set — the point is inside every edge." if code == 0 else \
            "Each 1 is an outside side. Corners turn two bits on at once."
        steps.append(VisualizationStep(
            index=idx,
            title=f"{name}  ·  {code_s}",
            equation=f"Region code  TBRL = {code_s}\n" + "\n".join(tests),
            explanation=why + " Any endpoint that lands here gets this exact code.",
            values={
                "tab": "region_codes",
                "lesson": "region",
                "active_code": code,
                "region_name": name,
                "caption": f"{name} is {code_s}.",
            },
            metrics={"Region": name, "Code": code_s},
            render_data=RenderData(mode="clipping", clipping_data=_region_payload(
                "region", xmin, ymin, xmax, ymax,
                selected_code=code,
                caption=f"{name}: bits {code_s}. Click another region to compare.",
            )),
        ))

    return steps


POLYGON_SHAPES: Dict[str, List[Tuple[float, float]]] = {
    "triangle": [(-4.5, -3.0), (4.5, -3.0), (0.0, 4.5)],
    "diamond": [(0.0, -4.5), (4.5, 0.0), (0.0, 4.5), (-4.5, 0.0)],
    "hexagon": [(-4.0, 0.0), (-2.0, 3.5), (2.0, 3.5), (4.0, 0.0), (2.0, -3.5), (-2.0, -3.5)],
    "star": [
        (-4.5, -3.5), (-1.5, -1.0), (0.0, -4.0), (1.5, -1.0), (4.5, -3.5),
        (3.0, 0.5), (4.8, 3.5), (1.5, 2.5), (0.0, 5.0), (-1.5, 2.5), (-4.8, 3.5), (-3.0, 0.5),
    ],
    "inside": [(-1.6, -1.0), (1.6, -1.0), (0.0, 1.3)],
    "outside": [(4.4, -1.2), (7.2, -0.4), (6.4, 2.2), (4.6, 1.4)],
}

POLYGON_BOUNDARIES = ("LEFT", "RIGHT", "BOTTOM", "TOP")

CASE_COPY = {
    "in_in": {
        "title": "Inside → Inside",
        "short": "Keep P",
        "why": "Both ends already sit on the visible side of this boundary, so the destination vertex stays.",
    },
    "in_out": {
        "title": "Inside → Outside",
        "short": "Keep the crossing, drop P",
        "why": "The edge leaves the window. Save the intersection and throw the outside vertex away.",
    },
    "out_in": {
        "title": "Outside → Inside",
        "short": "Add the crossing, then keep P",
        "why": "The edge re-enters. Insert the intersection, then keep the inside destination.",
    },
    "out_out": {
        "title": "Outside → Outside",
        "short": "Emit nothing",
        "why": "The whole edge is on the hidden side of this boundary, so it contributes no vertices.",
    },
}


_POLYGON_SHAPE_ALIASES = {
    "triangle": "triangle",
    "crossing triangle": "triangle",
    "diamond": "diamond",
    "hexagon": "hexagon",
    "star": "star",
    "inside": "inside",
    "fully inside": "inside",
    "outside": "outside",
    "fully outside": "outside",
}


def get_polygon_shape(name: str) -> List[Tuple[float, float]]:
    """Return a copy of a named demonstration polygon."""
    key = _POLYGON_SHAPE_ALIASES.get(str(name).strip().lower(), "triangle")
    return list(POLYGON_SHAPES.get(key, POLYGON_SHAPES["triangle"]))


def _pt(p: Tuple[float, float]) -> Tuple[float, float]:
    return (float(p[0]), float(p[1]))


def _fmt_pt(p: Tuple[float, float]) -> str:
    return f"({p[0]:.2f}, {p[1]:.2f})"


def sh_inside(p: Tuple[float, float], edge: str,
              xmin: float, ymin: float, xmax: float, ymax: float) -> bool:
    """True if point p is on the visible side of one infinite clip boundary."""
    x, y = p
    if edge == "LEFT":
        return x >= xmin - 1e-9
    if edge == "RIGHT":
        return x <= xmax + 1e-9
    if edge == "BOTTOM":
        return y >= ymin - 1e-9
    if edge == "TOP":
        return y <= ymax + 1e-9
    return True


def sh_intersect(p1: Tuple[float, float], p2: Tuple[float, float], edge: str,
                 xmin: float, ymin: float, xmax: float, ymax: float) -> Tuple[float, float]:
    """Parametric intersection of segment p1→p2 with one infinite clip boundary."""
    x1, y1 = p1
    x2, y2 = p2
    if edge == "LEFT":
        t = (xmin - x1) / (x2 - x1) if abs(x2 - x1) > 1e-12 else 0.0
        return (xmin, y1 + t * (y2 - y1))
    if edge == "RIGHT":
        t = (xmax - x1) / (x2 - x1) if abs(x2 - x1) > 1e-12 else 0.0
        return (xmax, y1 + t * (y2 - y1))
    if edge == "BOTTOM":
        t = (ymin - y1) / (y2 - y1) if abs(y2 - y1) > 1e-12 else 0.0
        return (x1 + t * (x2 - x1), ymin)
    if edge == "TOP":
        t = (ymax - y1) / (y2 - y1) if abs(y2 - y1) > 1e-12 else 0.0
        return (x1 + t * (x2 - x1), ymax)
    return p2


def sh_classify(s_in: bool, p_in: bool) -> str:
    if s_in and p_in:
        return "in_in"
    if s_in and not p_in:
        return "in_out"
    if (not s_in) and p_in:
        return "out_in"
    return "out_out"


def _boundary_equation(edge: str, xmin: float, ymin: float, xmax: float, ymax: float) -> str:
    return {
        "LEFT": f"x = {xmin:.1f}",
        "RIGHT": f"x = {xmax:.1f}",
        "BOTTOM": f"y = {ymin:.1f}",
        "TOP": f"y = {ymax:.1f}",
    }.get(edge, edge)


def _boundary_inside_rule(edge: str, xmin: float, ymin: float, xmax: float, ymax: float) -> str:
    return {
        "LEFT": f"visible when x ≥ {xmin:.1f}",
        "RIGHT": f"visible when x ≤ {xmax:.1f}",
        "BOTTOM": f"visible when y ≥ {ymin:.1f}",
        "TOP": f"visible when y ≤ {ymax:.1f}",
    }.get(edge, "")


def sutherland_hodgman_polygon_clip(
    polygon: List[Tuple[float, float]],
    xmin: float, ymin: float, xmax: float, ymax: float
) -> List[Tuple[float, float]]:
    """
    Sutherland-Hodgman Polygon Clipping algorithm.
    Clips arbitrary 2D polygon against a rectangular clipping window.
    Iteratively clips against 4 boundaries: LEFT, RIGHT, BOTTOM, TOP.
    Returns:
        List of (x, y) vertices of the clipped polygon.
    """
    if not polygon or len(polygon) < 3:
        return []

    output_list = [_pt(p) for p in polygon]

    for edge in POLYGON_BOUNDARIES:
        input_list = output_list
        output_list = []
        if not input_list:
            break

        s = input_list[-1]
        for p in input_list:
            p_in = sh_inside(p, edge, xmin, ymin, xmax, ymax)
            s_in = sh_inside(s, edge, xmin, ymin, xmax, ymax)
            if p_in:
                if s_in:
                    output_list.append(p)
                else:
                    output_list.append(sh_intersect(s, p, edge, xmin, ymin, xmax, ymax))
                    output_list.append(p)
            elif s_in:
                output_list.append(sh_intersect(s, p, edge, xmin, ymin, xmax, ymax))
            s = p

    return output_list


def sutherland_hodgman_trace(
    polygon: List[Tuple[float, float]],
    xmin: float = -3.0, ymin: float = -2.0,
    xmax: float = 3.0, ymax: float = 2.0
) -> List[VisualizationStep]:
    """
    Classroom walkthrough of Sutherland–Hodgman polygon clipping.

    The mathematical loop is unchanged: clip the current vertex list against
    LEFT, RIGHT, BOTTOM, then TOP. Each emitted step is one real edge
    classification, carrying the actual input/output lists for the canvas.
    """
    orig_poly = [_pt(p) for p in polygon]
    steps: List[VisualizationStep] = []
    step_num = 1

    def payload(
        *,
        focus: str,
        caption: str,
        input_pts: List[Tuple[float, float]],
        output_pts: List[Tuple[float, float]],
        current_pts: Optional[List[Tuple[float, float]]] = None,
        output_before: Optional[List[Tuple[float, float]]] = None,
        active_boundary: Optional[str] = None,
        case: Optional[str] = None,
        edge_s: Optional[Tuple[float, float]] = None,
        edge_p: Optional[Tuple[float, float]] = None,
        s_inside: Optional[bool] = None,
        p_inside: Optional[bool] = None,
        intersection: Optional[Tuple[float, float]] = None,
        emitted: Optional[List[Dict[str, Any]]] = None,
        anim: Optional[Dict[str, Any]] = None,
        is_final: bool = False,
        pass_index: int = 0,
        edge_index: int = 0,
        edge_count: int = 0,
    ) -> Dict[str, Any]:
        current = current_pts if current_pts is not None else input_pts
        return {
            "view_tab": "clip_polygon",
            "xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax,
            "focus": focus,
            "caption": caption,
            "active_boundary": active_boundary,
            "case": case,
            "edge_s": edge_s,
            "edge_p": edge_p,
            "s_inside": s_inside,
            "p_inside": p_inside,
            "intersection": intersection,
            "emitted": list(emitted or []),
            "anim": anim,
            "pass_index": pass_index,
            "edge_index": edge_index,
            "edge_count": edge_count,
            "polygon": {
                "original": list(orig_poly),
                "input": list(input_pts),
                "output": list(output_pts),
                "output_before": list(output_before if output_before is not None else output_pts),
                "current": list(current),
                "is_final": is_final,
            },
        }

    def add_step(title: str, equation: str, explanation: str, values: Dict[str, Any],
                 metrics: Dict[str, Any], cd: Dict[str, Any]) -> None:
        nonlocal step_num
        values = dict(values)
        values.setdefault("caption", cd.get("caption", ""))
        values.setdefault("focus", cd.get("focus", ""))
        values.setdefault("stage", values.get("stage") or cd.get("focus", ""))
        steps.append(VisualizationStep(
            index=step_num,
            title=title,
            equation=equation,
            explanation=explanation,
            values=values,
            metrics=metrics,
            render_data=RenderData(mode="clipping", clipping_data=cd),
        ))
        step_num += 1

    add_step(
        "A polygon and a window",
        (
            f"Window   [{xmin:.1f}, {ymin:.1f}]  to  [{xmax:.1f}, {ymax:.1f}]\n"
            f"Polygon  {len(orig_poly)} vertices"
        ),
        (
            "We only want the piece of this polygon that sits inside the teal window. "
            "Sutherland–Hodgman does that by walking every edge, then repeating for each of the four sides."
        ),
        {"stage": "meet", "vertices": list(orig_poly)},
        {"Vertices": len(orig_poly), "Boundaries": 4},
        payload(
            focus="meet",
            caption="The dashed shape is the original polygon. We will keep only what lies inside the window.",
            input_pts=orig_poly,
            output_pts=[],
            current_pts=orig_poly,
            anim={"type": "scene_enter"},
        ),
    )

    add_step(
        "One boundary at a time",
        "Pass order:  LEFT  →  RIGHT  →  BOTTOM  →  TOP\nEach pass’s output list is the next pass’s input.",
        (
            "A rectangle is four infinite half-planes. Clip against the left side first, take the surviving vertices, "
            "then the right, then bottom, then top. After four passes the leftover polygon is inside the window."
        ),
        {"stage": "pipeline"},
        {"Stage": "Pipeline"},
        payload(
            focus="pipeline",
            caption="Four passes, always in the same order. Output of one pass becomes input of the next.",
            input_pts=orig_poly,
            output_pts=[],
            current_pts=orig_poly,
            anim={"type": "pipeline"},
        ),
    )

    current_poly = list(orig_poly)

    for pass_i, edge_name in enumerate(POLYGON_BOUNDARIES, start=1):
        boundary_eq = _boundary_equation(edge_name, xmin, ymin, xmax, ymax)
        inside_rule = _boundary_inside_rule(edge_name, xmin, ymin, xmax, ymax)
        input_list = list(current_poly)
        nice = edge_name.title()

        add_step(
            f"Clip against {nice.lower()}",
            f"{nice} boundary  {boundary_eq}\nInside  {inside_rule}\nInput vertices  {len(input_list)}",
            (
                f"Every vertex is now tested against the {nice.lower()} side only. "
                f"A point is visible here when {inside_rule.split('when ')[-1]}. "
                "We walk the polygon in order, classifying each edge as we go."
            ),
            {
                "stage": "pass_intro",
                "edge": edge_name,
                "boundary": edge_name,
                "pass_index": pass_i,
            },
            {"Pass": f"{pass_i} of 4", "Boundary": nice, "Input": len(input_list)},
            payload(
                focus="pass",
                caption=f"Pass {pass_i} of 4: clip against {nice.lower()}  ({boundary_eq}).",
                input_pts=input_list,
                output_pts=[],
                current_pts=input_list,
                active_boundary=edge_name,
                anim={"type": "boundary_focus", "boundary": edge_name},
                pass_index=pass_i,
            ),
        )

        output_list: List[Tuple[float, float]] = []
        if not input_list:
            add_step(
                f"{nice} pass — nothing to clip",
                "Input list is empty, so this pass emits no vertices.",
                "A previous boundary already removed the whole polygon. Later passes stay empty.",
                {"stage": "pass_complete", "edge": edge_name, "vertices": []},
                {"Pass": pass_i, "Output": 0},
                payload(
                    focus="pass_complete",
                    caption="No vertices remain. The polygon is already gone.",
                    input_pts=[],
                    output_pts=[],
                    active_boundary=edge_name,
                    anim={"type": "pass_morph"},
                    pass_index=pass_i,
                    is_final=False,
                ),
            )
            current_poly = []
            continue

        s = input_list[-1]
        edge_count = len(input_list)
        for edge_i, p in enumerate(input_list, start=1):
            s_in = sh_inside(s, edge_name, xmin, ymin, xmax, ymax)
            p_in = sh_inside(p, edge_name, xmin, ymin, xmax, ymax)
            case = sh_classify(s_in, p_in)
            info = CASE_COPY[case]
            before = list(output_list)
            inter = None
            emitted: List[Dict[str, Any]] = []

            if p_in:
                if s_in:
                    output_list.append(p)
                    emitted.append({"kind": "keep", "pt": _pt(p), "label": "P"})
                else:
                    inter = sh_intersect(s, p, edge_name, xmin, ymin, xmax, ymax)
                    output_list.append(inter)
                    output_list.append(p)
                    emitted.append({"kind": "new", "pt": _pt(inter), "label": "I"})
                    emitted.append({"kind": "keep", "pt": _pt(p), "label": "P"})
            elif s_in:
                inter = sh_intersect(s, p, edge_name, xmin, ymin, xmax, ymax)
                output_list.append(inter)
                emitted.append({"kind": "new", "pt": _pt(inter), "label": "I"})

            s_tag = "inside" if s_in else "outside"
            p_tag = "inside" if p_in else "outside"
            emit_txt = ", ".join(item["label"] for item in emitted) if emitted else "nothing"
            add_step(
                f"{nice}: {info['title']}",
                (
                    f"S {_fmt_pt(s)}  {s_tag}\n"
                    f"P {_fmt_pt(p)}  {p_tag}\n"
                    f"{info['short']}   →   output {emit_txt}"
                ),
                info["why"] + f" Output list now has {len(output_list)} vertex{'es' if len(output_list) != 1 else ''}.",
                {
                    "stage": "edge",
                    "edge": edge_name,
                    "boundary": edge_name,
                    "case": case,
                    "s_inside": s_in,
                    "p_inside": p_in,
                    "output_count": len(output_list),
                    "pass_index": pass_i,
                    "edge_index": edge_i,
                },
                {
                    "Pass": f"{pass_i} of 4",
                    "Edge": f"{edge_i} of {edge_count}",
                    "Case": info["title"],
                    "Output": len(output_list),
                },
                payload(
                    focus="edge",
                    caption=f"S is {s_tag}, P is {p_tag}. {info['short']}.",
                    input_pts=input_list,
                    output_pts=list(output_list),
                    output_before=before,
                    current_pts=input_list,
                    active_boundary=edge_name,
                    case=case,
                    edge_s=_pt(s),
                    edge_p=_pt(p),
                    s_inside=s_in,
                    p_inside=p_in,
                    intersection=_pt(inter) if inter is not None else None,
                    emitted=emitted,
                    anim={"type": "edge_travel", "from": _pt(s), "to": _pt(p)},
                    pass_index=pass_i,
                    edge_index=edge_i,
                    edge_count=edge_count,
                ),
            )
            s = p

        current_poly = list(output_list)
        survived = len(current_poly) >= 3
        add_step(
            f"{nice} pass complete",
            (
                f"Input  {len(input_list)} vertices   →   output  {len(current_poly)} vertices\n"
                + ("This list becomes the input of the next boundary." if survived
                   else "Fewer than 3 vertices remain — the polygon is gone.")
            ),
            (
                f"Every edge has been classified against {nice.lower()}. "
                + ("The surviving polygon is handed to the next pass." if survived
                   else "Nothing is left to clip against the remaining sides.")
            ),
            {
                "stage": "pass_complete",
                "edge": edge_name,
                "vertices": [tuple(round(c, 2) for c in pt) for pt in current_poly],
                "pass_index": pass_i,
            },
            {"Pass": f"{pass_i} of 4", "Output": len(current_poly)},
            payload(
                focus="pass_complete",
                caption=(
                    f"After {nice.lower()}, {len(current_poly)} vertices remain."
                    if survived else f"After {nice.lower()}, the polygon has been fully clipped away."
                ),
                input_pts=input_list,
                output_pts=list(current_poly),
                current_pts=list(current_poly) if survived else input_list,
                active_boundary=edge_name,
                anim={"type": "pass_morph"},
                pass_index=pass_i,
            ),
        )

    visible = len(current_poly) >= 3
    add_step(
        "Clipping complete",
        (
            f"Visible polygon  {len(current_poly)} vertices\n"
            f"Original         {len(orig_poly)} vertices"
            if visible else
            f"Visible polygon  none\nOriginal         {len(orig_poly)} vertices"
        ),
        (
            "All four boundaries have been applied. The green shape is what will be filled on screen."
            if visible else
            "After four half-plane tests the polygon never entered the window, so nothing is drawn."
        ),
        {
            "stage": "final_result",
            "status": "accepted" if visible else "rejected",
            "final_vertices": [tuple(round(c, 2) for c in pt) for pt in current_poly],
            "accepted_polygon": list(current_poly) if visible else None,
        },
        {
            "final_vertex_count": len(current_poly),
            "accepted": visible,
            "rejected": not visible,
        },
        payload(
            focus="result",
            caption=(
                "The green polygon is the clipped result. The dashed outline is what we started with."
                if visible else
                "Nothing survived. The original dashed outline never entered the window."
            ),
            input_pts=orig_poly,
            output_pts=list(current_poly),
            current_pts=list(current_poly) if visible else orig_poly,
            anim={"type": "final_summary"},
            is_final=True,
        ),
    )
    return steps


def build_polygon_cases_steps(
    xmin: float = -3.0, ymin: float = -2.0,
    xmax: float = 3.0, ymax: float = 2.0
) -> List[VisualizationStep]:
    """First lesson: the four edge cases, before walking a real polygon."""
    mid_y = (ymin + ymax) / 2.0
    demo_poly = [
        (xmin + 1.4, ymin + 0.5),
        (xmax + 1.6, ymin + 0.4),
        (xmax + 0.4, ymax + 1.4),
        (xmin - 1.8, ymax + 0.6),
        (xmin - 1.6, ymin - 0.8),
    ]
    case_edges = {
        "in_in": ((xmin + 1.3, ymin + 0.7), (xmax - 1.1, ymax - 0.7)),
        "in_out": ((xmin + 1.6, mid_y + 0.85), (xmin - 2.3, mid_y + 0.85)),
        "out_in": ((xmin - 2.3, mid_y - 0.85), (xmin + 1.6, mid_y - 0.85)),
        "out_out": ((xmin - 2.5, ymax + 1.15), (xmin - 1.7, ymin - 1.15)),
    }

    def case_payload(focus: str, caption: str, case: Optional[str] = None,
                     anim: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        edge = case_edges.get(case or "", (None, None))
        s_pt, p_pt = edge
        inter = None
        s_in = p_in = None
        emitted: List[Dict[str, Any]] = []
        if s_pt and p_pt:
            s_in = sh_inside(s_pt, "LEFT", xmin, ymin, xmax, ymax)
            p_in = sh_inside(p_pt, "LEFT", xmin, ymin, xmax, ymax)
            if case == "in_in":
                emitted = [{"kind": "keep", "pt": p_pt, "label": "P"}]
            elif case == "in_out":
                inter = sh_intersect(s_pt, p_pt, "LEFT", xmin, ymin, xmax, ymax)
                emitted = [{"kind": "new", "pt": inter, "label": "I"}]
            elif case == "out_in":
                inter = sh_intersect(s_pt, p_pt, "LEFT", xmin, ymin, xmax, ymax)
                emitted = [
                    {"kind": "new", "pt": inter, "label": "I"},
                    {"kind": "keep", "pt": p_pt, "label": "P"},
                ]
        return {
            "view_tab": "four_cases",
            "lesson": focus,
            "xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax,
            "focus": focus,
            "caption": caption,
            "case": case,
            "active_boundary": "LEFT" if focus in ("halfplane", "case") else None,
            "edge_s": s_pt,
            "edge_p": p_pt,
            "s_inside": s_in,
            "p_inside": p_in,
            "intersection": inter,
            "emitted": emitted,
            "anim": anim or {"type": "region_pulse"},
            "polygon": {
                "original": list(demo_poly),
                "input": list(demo_poly),
                "output": [item["pt"] for item in emitted],
                "output_before": [],
                "current": list(demo_poly),
                "is_final": False,
            },
        }

    steps = [
        VisualizationStep(
            index=1,
            title="Why clip a polygon?",
            equation="Keep the part inside the window\nDiscard the part that sits outside",
            explanation=(
                "Filled shapes spill over the screen just like lines do. "
                "Clipping a polygon means rebuilding a new vertex list that only covers the visible region."
            ),
            values={"tab": "four_cases", "lesson": "meet", "caption": "Only the piece inside the window should be filled."},
            metrics={"Lesson": "The idea"},
            render_data=RenderData(mode="clipping", clipping_data=case_payload(
                "meet",
                "The teal rectangle is the window. Everything outside it should disappear.",
                anim={"type": "scene_enter"},
            )),
        ),
        VisualizationStep(
            index=2,
            title="Four sides, four passes",
            equation="LEFT  →  RIGHT  →  BOTTOM  →  TOP\nOutput of one pass = input of the next",
            explanation=(
                "Sutherland–Hodgman never clips against the whole rectangle at once. "
                "It treats the window as four infinite edges and peels the polygon against them, one after another."
            ),
            values={"tab": "four_cases", "lesson": "pipeline",
                    "caption": "Clip left, then right, then bottom, then top. Same idea every time — only the boundary changes."},
            metrics={"Lesson": "The pipeline"},
            render_data=RenderData(mode="clipping", clipping_data=case_payload(
                "pipeline",
                "Clip left, then right, then bottom, then top. Same idea every time — only the boundary changes.",
                anim={"type": "pipeline"},
            )),
        ),
        VisualizationStep(
            index=3,
            title="Inside or outside one line",
            equation=f"Left boundary  x = {xmin:.1f}\nA vertex is inside this pass when x ≥ {xmin:.1f}",
            explanation=(
                "For a single pass we only care about one question: which side of this infinite line is the vertex on? "
                "The four cases below are just the four combinations of answers for the two ends of an edge."
            ),
            values={"tab": "four_cases", "lesson": "halfplane",
                    "caption": "The shaded side is outside the left boundary. Inside means ‘keep for this pass’."},
            metrics={"Lesson": "Half-plane"},
            render_data=RenderData(mode="clipping", clipping_data=case_payload(
                "halfplane",
                "The shaded side is outside the left boundary. Inside means ‘keep for this pass’.",
                anim={"type": "boundary_focus", "boundary": "LEFT"},
            )),
        ),
    ]

    case_order = [
        ("in_in", "Both vertices stay inside"),
        ("in_out", "The edge leaves the window"),
        ("out_in", "The edge comes back in"),
        ("out_out", "The whole edge is hidden"),
    ]
    for idx, (case, title) in enumerate(case_order, start=4):
        info = CASE_COPY[case]
        s_pt, p_pt = case_edges[case]
        steps.append(VisualizationStep(
            index=idx,
            title=title,
            equation=(
                f"{info['title']}\n"
                f"S {_fmt_pt(s_pt)}   P {_fmt_pt(p_pt)}\n"
                f"Output  {info['short']}"
            ),
            explanation=info["why"] + " Remember this rule — the algorithm uses it on every edge of every pass.",
            values={"tab": "four_cases", "lesson": "case", "case": case, "caption": info["why"]},
            metrics={"Case": info["title"], "Output": info["short"]},
            render_data=RenderData(mode="clipping", clipping_data=case_payload(
                "case",
                f"{info['title']}. {info['short']}.",
                case=case,
                anim={"type": "edge_travel", "from": s_pt, "to": p_pt},
            )),
        ))

    steps.append(VisualizationStep(
        index=8,
        title="Then repeat for the other three sides",
        equation="After LEFT, do the same for RIGHT, BOTTOM, and TOP\nThe leftover vertices are the clipped polygon",
        explanation=(
            "That is the whole algorithm: four cases, four boundaries. "
            "Open Clip a Polygon to watch a real vertex list grow and shrink on each pass."
        ),
        values={"tab": "four_cases", "lesson": "wrap",
                "caption": "Same four cases, new boundary. Switch to Clip a Polygon to see them work on a real shape."},
        metrics={"Lesson": "Next"},
        render_data=RenderData(mode="clipping", clipping_data=case_payload(
            "wrap",
            "Same four cases, new boundary. Switch to Clip a Polygon to see them work on a real shape.",
            anim={"type": "scene_enter"},
        )),
    ))
    return steps
