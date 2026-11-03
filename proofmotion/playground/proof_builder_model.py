"""
playground/proof_builder_model.py
---------------------------------
Data models for the Proof Builder studio feature in ProofMotion.
Enables users to author custom geometric theorem proofs with multiple steps,
mathematical shapes (points, lines, polygons, angles, circles, text labels),
equations, and pedagogical explanations.
"""

from __future__ import annotations

import json
import math
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from core.step_model import Arc2D, Line2D, Point2D, Polygon2D, RenderData, Text2D
from models.theorem_state import ProofStep


class ShapeType(str, Enum):
    POINT = "point"
    LINE = "line"
    POLYGON = "polygon"
    ANGLE = "angle"
    CIRCLE = "circle"
    TEXT = "text"
    CURVE = "curve"
    SECTOR = "sector"


def make_id() -> str:
    return uuid.uuid4().hex[:8]


@dataclass
class BuilderShape:
    """A single mathematical or geometric primitive within a proof step."""
    shape_type: str = ShapeType.POINT.value
    id: str = field(default_factory=make_id)
    name: str = ""
    color: str = "#6C5CE7"
    fill_color: str = "rgba(108, 92, 231, 0.22)"
    stroke_width: float = 2.0
    dashed: bool = False
    coords: List[float] = field(default_factory=list)
    polygon_points: List[Tuple[float, float]] = field(default_factory=list)
    text: str = ""
    font_size: int = 12
    bold: bool = False
    is_right_angle: bool = False

    def translate(self, dx: float, dy: float):
        """Translates all vertices and coordinates of this shape by (dx, dy)."""
        st = self.shape_type
        if st == ShapeType.POINT.value and len(self.coords) >= 2:
            self.coords[0] = round(self.coords[0] + dx, 3)
            self.coords[1] = round(self.coords[1] + dy, 3)
        elif st == ShapeType.LINE.value and len(self.coords) >= 4:
            self.coords[0] = round(self.coords[0] + dx, 3)
            self.coords[1] = round(self.coords[1] + dy, 3)
            self.coords[2] = round(self.coords[2] + dx, 3)
            self.coords[3] = round(self.coords[3] + dy, 3)
        elif st == ShapeType.POLYGON.value:
            self.polygon_points = [
                (round(px + dx, 3), round(py + dy, 3)) for px, py in self.polygon_points
            ]
            if len(self.coords) >= 2:
                self.coords[0] = round(self.coords[0] + dx, 3)
                self.coords[1] = round(self.coords[1] + dy, 3)
        elif st in (ShapeType.ANGLE.value, ShapeType.CIRCLE.value, ShapeType.TEXT.value, ShapeType.SECTOR.value):
            if len(self.coords) >= 2:
                self.coords[0] = round(self.coords[0] + dx, 3)
                self.coords[1] = round(self.coords[1] + dy, 3)
        elif st == ShapeType.CURVE.value and len(self.coords) >= 6:
            self.coords[0] = round(self.coords[0] + dx, 3)
            self.coords[1] = round(self.coords[1] + dy, 3)
            self.coords[2] = round(self.coords[2] + dx, 3)
            self.coords[3] = round(self.coords[3] + dy, 3)
            self.coords[4] = round(self.coords[4] + dx, 3)
            self.coords[5] = round(self.coords[5] + dy, 3)

    def center(self) -> Tuple[float, float]:
        """Returns the approximate geometric center (cx, cy) of the shape."""
        st = self.shape_type
        if st == ShapeType.POINT.value and len(self.coords) >= 2:
            return self.coords[0], self.coords[1]
        elif st == ShapeType.LINE.value and len(self.coords) >= 4:
            return (self.coords[0] + self.coords[2]) / 2.0, (self.coords[1] + self.coords[3]) / 2.0
        elif st == ShapeType.POLYGON.value and self.polygon_points:
            cx = sum(p[0] for p in self.polygon_points) / len(self.polygon_points)
            cy = sum(p[1] for p in self.polygon_points) / len(self.polygon_points)
            return round(cx, 3), round(cy, 3)
        elif st == ShapeType.CURVE.value and len(self.coords) >= 6:
            cx = (self.coords[0] + self.coords[2] + self.coords[4]) / 3.0
            cy = (self.coords[1] + self.coords[3] + self.coords[5]) / 3.0
            return round(cx, 3), round(cy, 3)
        elif st == ShapeType.SECTOR.value and len(self.coords) >= 5:
            cx, cy, r, s_deg, sp_deg = self.coords[0], self.coords[1], self.coords[2], self.coords[3], self.coords[4]
            mid_rad = math.radians(s_deg + sp_deg / 2.0)
            return round(cx + (2.0 / 3.0) * r * math.cos(mid_rad), 3), round(cy + (2.0 / 3.0) * r * math.sin(mid_rad), 3)
        elif len(self.coords) >= 2:
            return self.coords[0], self.coords[1]
        return 0.0, 0.0

    def copy(self) -> BuilderShape:
        return BuilderShape(
            shape_type=self.shape_type,
            id=make_id(),
            name=self.name,
            color=self.color,
            fill_color=self.fill_color,
            stroke_width=self.stroke_width,
            dashed=self.dashed,
            coords=list(self.coords),
            polygon_points=[(float(x), float(y)) for x, y in self.polygon_points],
            text=self.text,
            font_size=self.font_size,
            bold=self.bold,
            is_right_angle=self.is_right_angle,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "shape_type": self.shape_type,
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "fill_color": self.fill_color,
            "stroke_width": self.stroke_width,
            "dashed": self.dashed,
            "coords": self.coords,
            "polygon_points": self.polygon_points,
            "text": self.text,
            "font_size": self.font_size,
            "bold": self.bold,
            "is_right_angle": self.is_right_angle,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BuilderShape:
        poly_pts = [
            (float(p[0]), float(p[1])) for p in data.get("polygon_points", []) if len(p) >= 2
        ]
        return cls(
            shape_type=data.get("shape_type", ShapeType.POINT.value),
            id=data.get("id", make_id()),
            name=data.get("name", ""),
            color=data.get("color", "#6C5CE7"),
            fill_color=data.get("fill_color", "rgba(108, 92, 231, 0.22)"),
            stroke_width=float(data.get("stroke_width", 2.0)),
            dashed=bool(data.get("dashed", False)),
            coords=[float(c) for c in data.get("coords", [])],
            polygon_points=poly_pts,
            text=data.get("text", ""),
            font_size=int(data.get("font_size", 12)),
            bold=bool(data.get("bold", False)),
            is_right_angle=bool(data.get("is_right_angle", False)),
        )


@dataclass
class BuilderProofStep:
    """One step of a multi-stage geometric proof."""
    index: int = 1
    title: str = "Step 1: Initial Construction"
    equation: str = ""
    explanation: str = ""
    shapes: List[BuilderShape] = field(default_factory=list)
    view_bounds: Optional[Tuple[float, float, float, float]] = None

    def copy(self, new_index: Optional[int] = None) -> BuilderProofStep:
        return BuilderProofStep(
            index=new_index if new_index is not None else self.index,
            title=self.title,
            equation=self.equation,
            explanation=self.explanation,
            shapes=[s.copy() for s in self.shapes],
            view_bounds=self.view_bounds,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "title": self.title,
            "equation": self.equation,
            "explanation": self.explanation,
            "shapes": [s.to_dict() for s in self.shapes],
            "view_bounds": list(self.view_bounds) if self.view_bounds else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BuilderProofStep:
        bounds = data.get("view_bounds")
        tuple_bounds = tuple(bounds) if bounds and len(bounds) == 4 else None
        return cls(
            index=int(data.get("index", 1)),
            title=data.get("title", ""),
            equation=data.get("equation", ""),
            explanation=data.get("explanation", ""),
            shapes=[BuilderShape.from_dict(s) for s in data.get("shapes", [])],
            view_bounds=tuple_bounds,
        )

    def to_render_data(self) -> RenderData:
        """Converts this step into the exact RenderData format used by VisualizationWidget."""
        rd = RenderData(mode="geometry")
        all_x: List[float] = []
        all_y: List[float] = []

        for s in self.shapes:
            st = s.shape_type

            if st == ShapeType.POINT.value:
                if len(s.coords) >= 2:
                    x, y = s.coords[0], s.coords[1]
                    all_x.append(x)
                    all_y.append(y)
                    rad = s.coords[2] if len(s.coords) > 2 else 4.5
                    rd.points.append(
                        Point2D(x=x, y=y, label=s.name, color=s.color, radius=rad)
                    )

            elif st == ShapeType.LINE.value:
                if len(s.coords) >= 4:
                    x1, y1, x2, y2 = s.coords[0], s.coords[1], s.coords[2], s.coords[3]
                    all_x.extend([x1, x2])
                    all_y.extend([y1, y2])
                    rd.lines.append(
                        Line2D(
                            x1=x1, y1=y1, x2=x2, y2=y2,
                            color=s.color, width=s.stroke_width,
                            dashed=s.dashed, label=s.name
                        )
                    )

            elif st == ShapeType.POLYGON.value:
                pts = list(s.polygon_points)
                if not pts and len(s.coords) >= 6:
                    for i in range(0, len(s.coords) - 1, 2):
                        pts.append((s.coords[i], s.coords[i + 1]))
                if pts:
                    for px, py in pts:
                        all_x.append(px)
                        all_y.append(py)
                    rd.polygons.append(
                        Polygon2D(
                            points=pts,
                            fill_color=s.fill_color,
                            stroke_color=s.color,
                            stroke_width=s.stroke_width,
                            label=s.name
                        )
                    )

            elif st == ShapeType.ANGLE.value:
                # coords: [cx, cy, radius, start_angle, span_angle]
                if len(s.coords) >= 3:
                    cx = s.coords[0]
                    cy = s.coords[1]
                    r = s.coords[2] if s.coords[2] > 0 else 0.8
                    start_deg = s.coords[3] if len(s.coords) > 3 else 0.0
                    span_deg = s.coords[4] if len(s.coords) > 4 else 90.0

                    all_x.extend([cx - r, cx + r])
                    all_y.extend([cy - r, cy + r])

                    if s.is_right_angle:
                        # Draw perpendicular right-angle indicator box
                        sq_sz = r * 0.75
                        ang_rad1 = math.radians(start_deg)
                        ang_rad2 = math.radians(start_deg + span_deg)
                        u1 = (math.cos(ang_rad1) * sq_sz, math.sin(ang_rad1) * sq_sz)
                        u2 = (math.cos(ang_rad2) * sq_sz, math.sin(ang_rad2) * sq_sz)
                        corner = (cx + u1[0] + u2[0], cy + u1[1] + u2[1])

                        rd.lines.append(
                            Line2D(cx + u1[0], cy + u1[1], corner[0], corner[1], color=s.color, width=1.6)
                        )
                        rd.lines.append(
                            Line2D(cx + u2[0], cy + u2[1], corner[0], corner[1], color=s.color, width=1.6)
                        )
                        if s.name:
                            rd.texts.append(
                                Text2D(corner[0] + 0.1, corner[1] + 0.1, s.name, color=s.color, font_size=10)
                            )
                    else:
                        rd.arcs.append(
                            Arc2D(
                                cx=cx, cy=cy, radius=r,
                                start_angle_deg=start_deg,
                                span_angle_deg=span_deg,
                                color=s.color,
                                label=s.name
                            )
                        )

            elif st == ShapeType.CIRCLE.value:
                # coords: [cx, cy, radius]
                if len(s.coords) >= 3:
                    cx, cy, r = s.coords[0], s.coords[1], s.coords[2]
                    all_x.extend([cx - r, cx + r])
                    all_y.extend([cy - r, cy + r])

                    # Render filled circle approximation if fill_color is visible
                    if s.fill_color and s.fill_color != "transparent" and "rgba" in s.fill_color:
                        circle_pts = []
                        for k in range(36):
                            theta = 2.0 * math.pi * k / 36.0
                            circle_pts.append((cx + r * math.cos(theta), cy + r * math.sin(theta)))
                        rd.polygons.append(
                            Polygon2D(
                                points=circle_pts,
                                fill_color=s.fill_color,
                                stroke_color=s.color,
                                stroke_width=s.stroke_width,
                                label=s.name
                            )
                        )
                    else:
                        rd.arcs.append(
                            Arc2D(cx=cx, cy=cy, radius=r, start_angle_deg=0.0, span_angle_deg=360.0, color=s.color, label=s.name)
                        )

            elif st == ShapeType.TEXT.value:
                if len(s.coords) >= 2:
                    tx, ty = s.coords[0], s.coords[1]
                    all_x.append(tx)
                    all_y.append(ty)
                    rd.texts.append(
                        Text2D(x=tx, y=ty, text=s.text or s.name, color=s.color, font_size=s.font_size, bold=s.bold)
                    )

            elif st == ShapeType.CURVE.value:
                # coords: [x0, y0, cx, cy, x1, y1]
                if len(s.coords) >= 6:
                    x0, y0, cx, cy, x1, y1 = s.coords[:6]
                    all_x.extend([x0, cx, x1])
                    all_y.extend([y0, cy, y1])
                    num_samples = 24
                    curve_pts = []
                    for step_i in range(num_samples + 1):
                        t = step_i / float(num_samples)
                        bx = (1 - t)**2 * x0 + 2 * (1 - t) * t * cx + t**2 * x1
                        by = (1 - t)**2 * y0 + 2 * (1 - t) * t * cy + t**2 * y1
                        curve_pts.append((bx, by))
                    for k in range(len(curve_pts) - 1):
                        rd.lines.append(
                            Line2D(
                                x1=curve_pts[k][0], y1=curve_pts[k][1],
                                x2=curve_pts[k + 1][0], y2=curve_pts[k + 1][1],
                                color=s.color, width=s.stroke_width,
                                dashed=s.dashed, label=s.name if k == 12 else ""
                            )
                        )

            elif st == ShapeType.SECTOR.value:
                # coords: [cx, cy, radius, start_angle, span_angle]
                if len(s.coords) >= 5:
                    cx, cy, r, s_deg, sp_deg = s.coords[:5]
                    all_x.extend([cx - r, cx + r])
                    all_y.extend([cy - r, cy + r])
                    num_arc_pts = max(8, int(abs(sp_deg) / 8.0))
                    sector_pts = [(cx, cy)]
                    for k in range(num_arc_pts + 1):
                        ang = math.radians(s_deg + (k / float(num_arc_pts)) * sp_deg)
                        sector_pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
                    rd.polygons.append(
                        Polygon2D(
                            points=sector_pts,
                            fill_color=s.fill_color,
                            stroke_color=s.color,
                            stroke_width=s.stroke_width,
                            label=s.name
                        )
                    )

        if self.view_bounds:
            rd.view_bounds = self.view_bounds
        elif all_x and all_y:
            min_x, max_x = min(all_x), max(all_x)
            min_y, max_y = min(all_y), max(all_y)
            pad_x = max(1.2, (max_x - min_x) * 0.28)
            pad_y = max(1.2, (max_y - min_y) * 0.28)
            rd.view_bounds = (min_x - pad_x, min_y - pad_y, max_x + pad_x, max_y + pad_y)
        else:
            rd.view_bounds = (-5.0, -5.0, 5.0, 5.0)

        return rd

    def to_proof_step(self) -> ProofStep:
        """Converts into a runtime ProofStep object compatible with the theorem visualizer."""
        return ProofStep(
            index=self.index,
            equation=self.equation,
            explanation=self.explanation,
            render_data=self.to_render_data(),
            values={"step_title": self.title, "index": self.index},
        )


@dataclass
class BuilderProof:
    """Complete user-authored theorem proof containing title, description, and steps."""
    title: str = "My Custom Theorem"
    description: str = "A custom theorem proof created in Proof Builder."
    id: str = field(default_factory=make_id)
    steps: List[BuilderProofStep] = field(default_factory=list)

    def add_step(self, step: Optional[BuilderProofStep] = None) -> BuilderProofStep:
        idx = len(self.steps) + 1
        if step is None:
            step = BuilderProofStep(index=idx, title=f"Step {idx}: New Proof Step")
        else:
            step.index = idx
        self.steps.append(step)
        return step

    def duplicate_step(self, step_idx_0based: int) -> Optional[BuilderProofStep]:
        if 0 <= step_idx_0based < len(self.steps):
            source = self.steps[step_idx_0based]
            new_step = source.copy(new_index=step_idx_0based + 2)
            new_step.title = f"{source.title} (Copy)"
            self.steps.insert(step_idx_0based + 1, new_step)
            self._reindex_steps()
            return new_step
        return None

    def delete_step(self, step_idx_0based: int) -> bool:
        if 0 <= step_idx_0based < len(self.steps) and len(self.steps) > 1:
            self.steps.pop(step_idx_0based)
            self._reindex_steps()
            return True
        return False

    def move_step(self, from_idx: int, to_idx: int) -> bool:
        if 0 <= from_idx < len(self.steps) and 0 <= to_idx < len(self.steps):
            step = self.steps.pop(from_idx)
            self.steps.insert(to_idx, step)
            self._reindex_steps()
            return True
        return False

    def _reindex_steps(self):
        for i, step in enumerate(self.steps):
            step.index = i + 1

    def to_proof_steps(self) -> List[ProofStep]:
        return [step.to_proof_step() for step in self.steps]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "id": self.id,
            "steps": [s.to_dict() for s in self.steps],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BuilderProof:
        proof = cls(
            title=data.get("title", "Untitled Theorem"),
            description=data.get("description", ""),
            id=data.get("id", make_id()),
            steps=[BuilderProofStep.from_dict(s) for s in data.get("steps", [])],
        )
        if not proof.steps:
            proof.add_step()
        proof._reindex_steps()
        return proof

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> BuilderProof:
        data = json.loads(json_str)
        return cls.from_dict(data)

