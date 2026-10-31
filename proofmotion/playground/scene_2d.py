"""
playground/scene_2d.py
----------------------
Pure-Python 2D playground scene: object CRUD, selection, hit testing,
clipping, and sequential transforms. No Qt dependency.
"""

from __future__ import annotations

from typing import Callable, List, Optional, Sequence, Tuple

import numpy as np

from playground.models import (
    OBJECT_COLORS_2D,
    SceneObject2D,
    TransformOp,
    default_shape_2d,
    make_reflect_op_2d,
    make_rotate_op_2d,
    make_scale_op_2d,
    make_translate_op_2d,
)
import cgip.clipping as clip
import cgip.transformations as t2d


Listener = Callable[[], None]


class Scene2D:
    def __init__(self):
        self.objects: List[SceneObject2D] = []
        self.selected_id: Optional[str] = None
        self.clip_enabled: bool = False
        self.clip_rect: Tuple[float, float, float, float] = (-3.0, -2.0, 3.0, 2.0)
        self.show_ghost: bool = True
        self.wireframe: bool = False
        self.show_coords: bool = True
        self._counters = {"point": 0, "line": 0, "triangle": 0, "rectangle": 0, "polygon": 0}
        self._listeners: List[Listener] = []
        self._dragging_translate: bool = False

        triangle = self.add_object("triangle", vertices=default_shape_2d("triangle"))
        self.selected_id = triangle.id

    def subscribe(self, fn: Listener) -> None:
        self._listeners.append(fn)

    def _notify(self) -> None:
        for fn in list(self._listeners):
            fn()

    def selected(self) -> Optional[SceneObject2D]:
        if not self.selected_id:
            return None
        return next((o for o in self.objects if o.id == self.selected_id), None)

    def select(self, object_id: Optional[str]) -> None:
        self.selected_id = object_id
        self._notify()

    def add_object(
        self,
        kind: str,
        vertices: Optional[Sequence[Tuple[float, float]]] = None,
        select: bool = True,
    ) -> SceneObject2D:
        kind = "rectangle" if kind == "rect" else kind.lower()
        verts = list(vertices) if vertices is not None else default_shape_2d(kind)
        self._counters[kind] = self._counters.get(kind, 0) + 1
        idx = self._counters[kind]
        color = OBJECT_COLORS_2D[(len(self.objects)) % len(OBJECT_COLORS_2D)]
        obj = SceneObject2D(
            kind=kind,
            local_vertices=[(float(x), float(y)) for x, y in verts],
            name=f"{kind.title()} {idx}",
            color=color,
        )
        self.objects.append(obj)
        if select:
            self.selected_id = obj.id
        self._notify()
        return obj

    def delete_selected(self) -> None:
        if not self.selected_id:
            return
        self.objects = [o for o in self.objects if o.id != self.selected_id]
        self.selected_id = self.objects[-1].id if self.objects else None
        self._notify()

    def clear(self) -> None:
        self.objects.clear()
        self.selected_id = None
        self._notify()

    def set_pose(self, **kwargs) -> None:
        obj = self.selected()
        if obj is None:
            return
        for key in ("tx", "ty", "rotation", "sx", "sy"):
            if key in kwargs:
                setattr(obj, key, float(kwargs[key]))
        self._notify()

    def apply_op(self, op: TransformOp) -> None:
        obj = self.selected()
        if obj is None:
            return
        obj.apply_op(op)
        self._dragging_translate = False
        self._notify()

    def apply_translate(self, dx: float, dy: float) -> None:
        self.apply_op(make_translate_op_2d(dx, dy))

    def apply_rotate(self, angle: float, cx: float = 0.0, cy: float = 0.0) -> None:
        self.apply_op(make_rotate_op_2d(angle, cx, cy))

    def apply_scale(self, sx: float, sy: float, cx: float = 0.0, cy: float = 0.0) -> None:
        self.apply_op(make_scale_op_2d(sx, sy, cx, cy))

    def apply_reflect(self, axis: str) -> None:
        self.apply_op(make_reflect_op_2d(axis))

    def reset_selected(self) -> None:
        obj = self.selected()
        if obj is None:
            return
        obj.reset_transforms()
        self._notify()

    def set_show_ghost(self, enabled: bool) -> None:
        self.show_ghost = bool(enabled)
        self._notify()

    def set_wireframe(self, enabled: bool) -> None:
        self.wireframe = bool(enabled)
        self._notify()

    def set_clip_enabled(self, enabled: bool) -> None:
        self.clip_enabled = bool(enabled)
        self._notify()

    def set_clip_rect(self, xmin: float, ymin: float, xmax: float, ymax: float) -> None:
        if xmax <= xmin or ymax <= ymin:
            raise ValueError("Clip window requires xmax > xmin and ymax > ymin.")
        self.clip_rect = (float(xmin), float(ymin), float(xmax), float(ymax))
        self._notify()

    def begin_world_drag(self) -> None:
        self._dragging_translate = False

    def translate_world(self, dx: float, dy: float, dragging: bool = False) -> None:
        obj = self.selected()
        if obj is None:
            return
        if not obj.history:
            obj.tx += dx
            obj.ty += dy
            self._notify()
            return
        if dragging and self._dragging_translate and obj.history and obj.history[-1].kind == "translate":
            last = obj.history[-1]
            last.params["dx"] += dx
            last.params["dy"] += dy
            last.matrix = t2d.translation_matrix(last.params["dx"], last.params["dy"])
            last.label = f"T({last.params['dx']:g}, {last.params['dy']:g})"
        else:
            op = make_translate_op_2d(dx, dy)
            obj.apply_op(op)
            self._dragging_translate = bool(dragging)
        self._notify()

    def hit_test(self, x: float, y: float, threshold: float = 0.35) -> Optional[str]:
        """Return the topmost object id under world point (x, y)."""
        for obj in reversed(self.objects):
            verts = obj.world_vertices()
            if not verts:
                continue
            if obj.kind == "point" or len(verts) == 1:
                px, py = verts[0]
                if (px - x) ** 2 + (py - y) ** 2 <= threshold ** 2:
                    return obj.id
            elif obj.kind == "line" or len(verts) == 2:
                if _point_to_segment(x, y, verts[0], verts[1]) <= threshold:
                    return obj.id
            else:
                if _point_in_polygon(x, y, verts):
                    return obj.id
                # also allow grabbing near an edge / vertex
                for i, (vx, vy) in enumerate(verts):
                    if (vx - x) ** 2 + (vy - y) ** 2 <= threshold ** 2:
                        return obj.id
                    nxt = verts[(i + 1) % len(verts)]
                    if _point_to_segment(x, y, (vx, vy), nxt) <= threshold * 0.6:
                        return obj.id
        return None

    def clipped_geometry(self, obj: SceneObject2D) -> Optional[List[Tuple[float, float]]]:
        if not self.clip_enabled:
            return None
        xmin, ymin, xmax, ymax = self.clip_rect
        verts = obj.world_vertices()
        if len(verts) == 1:
            x, y = verts[0]
            if xmin <= x <= xmax and ymin <= y <= ymax:
                return verts
            return []
        if len(verts) == 2:
            seg = clip.cohen_sutherland_clip(
                verts[0][0], verts[0][1], verts[1][0], verts[1][1],
                xmin, ymin, xmax, ymax,
            )
            if seg is None:
                return []
            return [seg[0], seg[1]]
        return clip.sutherland_hodgman_polygon_clip(verts, xmin, ymin, xmax, ymax)


def _point_to_segment(
    x: float, y: float,
    a: Tuple[float, float],
    b: Tuple[float, float],
) -> float:
    ax, ay = a
    bx, by = b
    abx, aby = bx - ax, by - ay
    denom = abx * abx + aby * aby
    if denom < 1e-12:
        return float(np.hypot(x - ax, y - ay))
    t = max(0.0, min(1.0, ((x - ax) * abx + (y - ay) * aby) / denom))
    px, py = ax + t * abx, ay + t * aby
    return float(np.hypot(x - px, y - py))


def _point_in_polygon(x: float, y: float, verts: Sequence[Tuple[float, float]]) -> bool:
    n = len(verts)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = verts[i]
        xj, yj = verts[j]
        intersects = ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi)
        if intersects:
            inside = not inside
        j = i
    return inside
