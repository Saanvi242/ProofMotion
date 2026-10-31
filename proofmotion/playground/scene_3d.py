"""
playground/scene_3d.py
----------------------
Pure-Python 3D playground scene: primitives, TRS pose, sequential
transforms, camera, and projection settings. No Qt dependency.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Tuple

from playground.models import (
    OBJECT_COLORS_3D,
    SceneObject3D,
    TransformOp,
    make_rotate_op_3d,
    make_scale_op_3d,
    make_translate_op_3d,
)


Listener = Callable[[], None]


class Scene3D:
    def __init__(self):
        self.objects: List[SceneObject3D] = []
        self.selected_id: Optional[str] = None
        self.projection_mode: str = "perspective"
        self.fov_deg: float = 45.0
        self.compare_mode: bool = False
        self.wireframe: bool = False
        self.show_grid: bool = True
        self.show_ghost: bool = True
        self.camera: Dict[str, float] = {
            "azimuth": 35.0,
            "elevation": 22.0,
            "distance": 7.0,
            "pan_x": 0.0,
            "pan_y": 0.0,
            "target_z": 0.0,
        }
        self._counters = {"cube": 0, "sphere": 0, "pyramid": 0, "cylinder": 0}
        self._listeners: List[Listener] = []

        cube = self.add_object("cube")
        self.selected_id = cube.id

    def subscribe(self, fn: Listener) -> None:
        self._listeners.append(fn)

    def _notify(self) -> None:
        for fn in list(self._listeners):
            fn()

    def selected(self) -> Optional[SceneObject3D]:
        if not self.selected_id:
            return None
        return next((o for o in self.objects if o.id == self.selected_id), None)

    def select(self, object_id: Optional[str]) -> None:
        self.selected_id = object_id
        self._notify()

    def add_object(self, kind: str, select: bool = True) -> SceneObject3D:
        kind = kind.lower()
        if kind not in self._counters:
            kind = "cube"
        self._counters[kind] += 1
        color = OBJECT_COLORS_3D[len(self.objects) % len(OBJECT_COLORS_3D)]
        obj = SceneObject3D(
            kind=kind,
            name=f"{kind.title()} {self._counters[kind]}",
            color=color,
        )
        # Offset later objects so they don't fully overlap
        n = len(self.objects)
        if n:
            obj.tx = 2.4 * ((n % 3) - 1)
            obj.tz = 2.4 * ((n // 3) % 3 - 1)
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

    def set_pose(self, **kwargs) -> None:
        obj = self.selected()
        if obj is None:
            return
        for key in ("tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"):
            if key in kwargs:
                setattr(obj, key, float(kwargs[key]))
        self._notify()

    def apply_op(self, op: TransformOp) -> None:
        obj = self.selected()
        if obj is None:
            return
        obj.apply_op(op)
        self._notify()

    def apply_translate(self, dx: float, dy: float, dz: float) -> None:
        self.apply_op(make_translate_op_3d(dx, dy, dz))

    def apply_rotate(self, axis: str, angle: float) -> None:
        self.apply_op(make_rotate_op_3d(axis, angle))

    def apply_scale(self, sx: float, sy: float, sz: float) -> None:
        self.apply_op(make_scale_op_3d(sx, sy, sz))

    def reset_selected(self) -> None:
        obj = self.selected()
        if obj is None:
            return
        obj.reset_transforms()
        self._notify()

    def reset_camera(self) -> None:
        self.camera = {
            "azimuth": 35.0,
            "elevation": 22.0,
            "distance": 7.0,
            "pan_x": 0.0,
            "pan_y": 0.0,
            "target_z": 0.0,
        }
        self._notify()

    def set_projection_mode(self, mode: str) -> None:
        self.projection_mode = "orthographic" if str(mode).lower().startswith("ortho") else "perspective"
        self._notify()

    def set_fov(self, fov_deg: float) -> None:
        self.fov_deg = max(15.0, min(90.0, float(fov_deg)))
        self._notify()

    def set_compare_mode(self, enabled: bool) -> None:
        self.compare_mode = bool(enabled)
        self._notify()

    def set_show_ghost(self, enabled: bool) -> None:
        self.show_ghost = bool(enabled)
        self._notify()

    def set_wireframe(self, enabled: bool) -> None:
        self.wireframe = bool(enabled)
        self._notify()

    def set_camera(self, **kwargs) -> None:
        for key in ("azimuth", "elevation", "distance", "pan_x", "pan_y"):
            if key in kwargs:
                self.camera[key] = float(kwargs[key])
        self._notify()

    def render_payload(self, projection_override: Optional[str] = None) -> List[dict]:
        """Serializable object list consumed by OpenGL3DWidget.set_scene_objects."""
        items = []
        for obj in self.objects:
            items.append({
                "id": obj.id,
                "kind": obj.kind,
                "model": obj.composed_matrix(),
                "selected": obj.id == self.selected_id,
                "color": obj.color,
                "ghost_model": obj.matrix_without_last() if self.show_ghost and obj.history else None,
            })
        return items
