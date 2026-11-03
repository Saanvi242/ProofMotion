"""
graphics/label_layout.py
------------------------
Shared intelligent label placement for ProofMotion visualizations.

Keeps annotations near their anchors, off important geometry, and
clear of one another. Used by the 2D canvas, clipping, curves,
playground, and any other painter that needs collision-aware text.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Sequence, Tuple

Rect = Tuple[float, float, float, float]  # x, y, w, h
Point = Tuple[float, float]
Poly = Sequence[Point]


def rect_right(r: Rect) -> float:
    return r[0] + r[2]


def rect_bottom(r: Rect) -> float:
    return r[1] + r[3]


def rect_center(r: Rect) -> Point:
    return (r[0] + r[2] * 0.5, r[1] + r[3] * 0.5)


def inflate_rect(r: Rect, pad: float) -> Rect:
    return (r[0] - pad, r[1] - pad, r[2] + pad * 2.0, r[3] + pad * 2.0)


def rects_intersect(a: Rect, b: Rect, gap: float = 0.0) -> bool:
    return not (
        rect_right(a) + gap <= b[0]
        or rect_right(b) + gap <= a[0]
        or rect_bottom(a) + gap <= b[1]
        or rect_bottom(b) + gap <= a[1]
    )


def intersection_area(a: Rect, b: Rect) -> float:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(rect_right(a), rect_right(b))
    y1 = min(rect_bottom(a), rect_bottom(b))
    if x1 <= x0 or y1 <= y0:
        return 0.0
    return (x1 - x0) * (y1 - y0)


def clamp_rect(r: Rect, viewport: Rect, margin: float) -> Rect:
    x, y, w, h = r
    vx, vy, vw, vh = viewport
    max_w = max(1.0, vw - margin * 2.0)
    max_h = max(1.0, vh - margin * 2.0)
    w = min(w, max_w)
    h = min(h, max_h)
    x = min(max(vx + margin, x), vx + vw - margin - w)
    y = min(max(vy + margin, y), vy + vh - margin - h)
    return (x, y, w, h)


def point_in_rect(p: Point, r: Rect, pad: float = 0.0) -> bool:
    return (
        r[0] - pad <= p[0] <= rect_right(r) + pad
        and r[1] - pad <= p[1] <= rect_bottom(r) + pad
    )


def _point_in_poly(p: Point, poly: Poly) -> bool:
    if len(poly) < 3:
        return False
    x, y = p
    inside = False
    j = len(poly) - 1
    for i, (xi, yi) in enumerate(poly):
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi):
            inside = not inside
        j = i
    return inside


def _seg_intersect(a1: Point, a2: Point, b1: Point, b2: Point) -> bool:
    def orient(p, q, r):
        return (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])

    def on_seg(p, q, r):
        return (
            min(p[0], r[0]) - 1e-6 <= q[0] <= max(p[0], r[0]) + 1e-6
            and min(p[1], r[1]) - 1e-6 <= q[1] <= max(p[1], r[1]) + 1e-6
        )

    o1 = orient(a1, a2, b1)
    o2 = orient(a1, a2, b2)
    o3 = orient(b1, b2, a1)
    o4 = orient(b1, b2, a2)
    if (o1 > 0) != (o2 > 0) and (o3 > 0) != (o4 > 0):
        return True
    if abs(o1) < 1e-6 and on_seg(a1, b1, a2):
        return True
    if abs(o2) < 1e-6 and on_seg(a1, b2, a2):
        return True
    if abs(o3) < 1e-6 and on_seg(b1, a1, b2):
        return True
    if abs(o4) < 1e-6 and on_seg(b1, a2, b2):
        return True
    return False


def _rect_corners(r: Rect) -> List[Point]:
    x, y, w, h = r
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def _rect_edges(r: Rect) -> List[Tuple[Point, Point]]:
    c = _rect_corners(r)
    return [(c[i], c[(i + 1) % 4]) for i in range(4)]


def rect_hits_poly(r: Rect, poly: Poly) -> bool:
    if len(poly) < 2:
        return False
    if any(_point_in_poly(c, poly) for c in _rect_corners(r)):
        return True
    if any(point_in_rect(p, r) for p in poly):
        return True
    if _point_in_poly(rect_center(r), poly):
        return True
    for a, b in _rect_edges(r):
        for i in range(len(poly)):
            if _seg_intersect(a, b, poly[i], poly[(i + 1) % len(poly)]):
                return True
    return False


def rect_hits_segment(r: Rect, p1: Point, p2: Point, thickness: float = 2.0) -> bool:
    if point_in_rect(p1, r, thickness) or point_in_rect(p2, r, thickness):
        return True
    for a, b in _rect_edges(r):
        if _seg_intersect(a, b, p1, p2):
            return True
    # Distance from rect center to the segment
    cx, cy = rect_center(r)
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    length2 = dx * dx + dy * dy
    if length2 < 1e-9:
        return math.hypot(cx - p1[0], cy - p1[1]) < (min(r[2], r[3]) * 0.5 + thickness)
    t = max(0.0, min(1.0, ((cx - p1[0]) * dx + (cy - p1[1]) * dy) / length2))
    px, py = p1[0] + t * dx, p1[1] + t * dy
    return math.hypot(cx - px, cy - py) < (min(r[2], r[3]) * 0.35 + thickness)


def closest_point_on_rect(p: Point, r: Rect) -> Point:
    x = min(max(p[0], r[0]), rect_right(r))
    y = min(max(p[1], r[1]), rect_bottom(r))
    return (x, y)


def leader_needed(anchor: Point, r: Rect, threshold: float = 16.0) -> bool:
    q = closest_point_on_rect(anchor, r)
    return math.hypot(q[0] - anchor[0], q[1] - anchor[1]) > threshold


@dataclass
class Obstacle:
    kind: str  # "rect", "poly", "segment", "point"
    rect: Optional[Rect] = None
    poly: Optional[List[Point]] = None
    p1: Optional[Point] = None
    p2: Optional[Point] = None
    radius: float = 0.0

    def hits(self, r: Rect) -> bool:
        if self.kind == "rect" and self.rect is not None:
            return rects_intersect(r, self.rect, gap=2.0)
        if self.kind == "poly" and self.poly:
            return rect_hits_poly(inflate_rect(r, 2.0), self.poly)
        if self.kind == "segment" and self.p1 and self.p2:
            return rect_hits_segment(r, self.p1, self.p2, thickness=max(2.0, self.radius))
        if self.kind == "point" and self.p1:
            return math.hypot(rect_center(r)[0] - self.p1[0], rect_center(r)[1] - self.p1[1]) < (
                self.radius + min(r[2], r[3]) * 0.35
            ) or point_in_rect(self.p1, r, self.radius * 0.6)
        return False


@dataclass
class LabelSpec:
    text: str
    anchor: Point
    width: float
    height: float
    kind: str = "point"  # point | polygon | line | banner | free
    outward: Optional[Point] = None
    preferred: Optional[Point] = None  # preferred top-left
    priority: int = 0


@dataclass
class PlacedLabel:
    text: str
    rect: Rect
    anchor: Point
    leader: bool
    kind: str = "point"


class LabelPlacer:
    """
    Places a batch of labels so they stay associated with their anchors
    without covering geometry or each other.
    """

    def __init__(
        self,
        viewport: Rect,
        margin: float = 10.0,
        reserved: Optional[Iterable[Rect]] = None,
        gap: float = 12.0,
        max_distance: float = 92.0,
    ):
        self.viewport = viewport
        self.margin = margin
        self.gap = gap
        self.max_distance = max_distance
        self.obstacles: List[Obstacle] = []
        self.placed: List[PlacedLabel] = []
        for r in reserved or []:
            self.obstacles.append(Obstacle(kind="rect", rect=r))

    def add_polygon(self, points: Sequence[Point]):
        if len(points) >= 2:
            self.obstacles.append(Obstacle(kind="poly", poly=list(points)))

    def add_segment(self, p1: Point, p2: Point, thickness: float = 2.0):
        self.obstacles.append(Obstacle(kind="segment", p1=p1, p2=p2, radius=thickness))

    def add_point(self, p: Point, radius: float = 6.0):
        self.obstacles.append(Obstacle(kind="point", p1=p, radius=radius))

    def add_rect(self, r: Rect):
        self.obstacles.append(Obstacle(kind="rect", rect=r))

    def place(self, spec: LabelSpec) -> PlacedLabel:
        candidates = self._candidates(spec)
        best: Optional[Rect] = None
        best_score = -1e18
        for rect in candidates:
            score = self._score(spec, rect)
            if score > best_score:
                best_score = score
                best = rect
        if best is None:
            best = clamp_rect(
                (spec.anchor[0] + self.gap, spec.anchor[1] - spec.height - self.gap, spec.width, spec.height),
                self.viewport,
                self.margin,
            )
        placed = PlacedLabel(
            text=spec.text,
            rect=best,
            anchor=spec.anchor,
            leader=leader_needed(spec.anchor, best),
            kind=spec.kind,
        )
        self.placed.append(placed)
        self.obstacles.append(Obstacle(kind="rect", rect=inflate_rect(best, 3.0)))
        return placed

    def place_all(self, specs: Sequence[LabelSpec]) -> List[PlacedLabel]:
        ordered = sorted(specs, key=lambda s: s.priority)
        return [self.place(spec) for spec in ordered]

    def _candidates(self, spec: LabelSpec) -> List[Rect]:
        w, h = spec.width, spec.height
        ax, ay = spec.anchor
        dirs = [
            (1.0, -1.0), (0.0, -1.0), (-1.0, -1.0),
            (1.0, 0.0), (-1.0, 0.0),
            (1.0, 1.0), (0.0, 1.0), (-1.0, 1.0),
        ]
        if spec.outward:
            ox, oy = spec.outward
            dirs.sort(key=lambda d: -(d[0] * ox + d[1] * oy))
        if spec.kind == "polygon":
            dirs = [(0.0, -1.0), (0.0, 1.0), (1.0, 0.0), (-1.0, 0.0)] + dirs
        if spec.kind == "banner":
            dirs = [(0.0, -1.0), (0.0, 1.0)] + dirs

        rects: List[Rect] = []
        if spec.preferred is not None:
            rects.append(clamp_rect((spec.preferred[0], spec.preferred[1], w, h), self.viewport, self.margin))

        distances = (self.gap, self.gap + 8.0, self.gap + 18.0, self.gap + 30.0, self.gap + 46.0)
        if spec.kind == "polygon":
            distances = (self.gap + 6.0, self.gap + 16.0, self.gap + 28.0, self.gap + 44.0)
        for dist in distances:
            for ux, uy in dirs:
                rects.append(self._rect_in_direction(ax, ay, w, h, ux, uy, dist))

        # Keep a near-anchor fallback so meaning stays attached
        rects.append(clamp_rect((ax + 10, ay - h - 8, w, h), self.viewport, self.margin))
        return rects

    def _rect_in_direction(self, ax: float, ay: float, w: float, h: float,
                           ux: float, uy: float, dist: float) -> Rect:
        if ux > 0:
            x = ax + dist
        elif ux < 0:
            x = ax - dist - w
        else:
            x = ax - w * 0.5
        if uy > 0:
            y = ay + dist
        elif uy < 0:
            y = ay - dist - h
        else:
            y = ay - h * 0.5
        return clamp_rect((x, y, w, h), self.viewport, self.margin)

    def _score(self, spec: LabelSpec, rect: Rect) -> float:
        score = 200.0
        geom_hits = 0
        label_hits = 0
        for obs in self.obstacles:
            if obs.hits(rect):
                if obs.kind == "rect":
                    label_hits += 1
                    score -= 80.0 + intersection_area(rect, obs.rect or (0, 0, 0, 0)) * 0.15
                else:
                    geom_hits += 1
                    score -= 140.0
        if geom_hits == 0:
            score += 90.0
        if label_hits == 0:
            score += 70.0

        q = closest_point_on_rect(spec.anchor, rect)
        dist = math.hypot(q[0] - spec.anchor[0], q[1] - spec.anchor[1])
        score -= dist * 1.15
        if dist > self.max_distance:
            score -= (dist - self.max_distance) * 4.0

        # Prefer staying inside the viewport without clamping (already clamped)
        vx, vy, vw, vh = self.viewport
        if rect[0] <= vx + self.margin + 0.5 or rect[1] <= vy + self.margin + 0.5:
            score -= 8.0
        if rect_right(rect) >= vx + vw - self.margin - 0.5:
            score -= 8.0

        if spec.outward:
            cx, cy = rect_center(rect)
            vx_, vy_ = cx - spec.anchor[0], cy - spec.anchor[1]
            mag = math.hypot(vx_, vy_) or 1.0
            align = (vx_ / mag) * spec.outward[0] + (vy_ / mag) * spec.outward[1]
            score += align * 28.0

        if spec.kind == "polygon":
            # Extra penalty for sitting on the shape
            for obs in self.obstacles:
                if obs.kind == "poly" and obs.hits(rect):
                    score -= 60.0
        return score


def outward_from_centroid(anchor: Point, centroid: Point) -> Point:
    dx = anchor[0] - centroid[0]
    dy = anchor[1] - centroid[1]
    mag = math.hypot(dx, dy)
    if mag < 1e-6:
        return (0.0, -1.0)
    return (dx / mag, dy / mag)


def polygon_centroid(points: Sequence[Point]) -> Point:
    if not points:
        return (0.0, 0.0)
    return (
        sum(p[0] for p in points) / len(points),
        sum(p[1] for p in points) / len(points),
    )


def polygon_bbox_anchor(points: Sequence[Point]) -> Point:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return ((min(xs) + max(xs)) * 0.5, min(ys))
