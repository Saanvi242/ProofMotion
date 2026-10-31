"""
playground/models.py
--------------------
Scene object models for the Interactive Graphics Playground.

2D pose uses the same column-vector convention as cgip.transformations:
    P' = M · P
    pose = T(tx, ty) · R(θ) · S(sx, sy)
    composed = extra_n · … · extra_1 · pose

3D pose reuses cgip.projection_3d.model_matrix_3d:
    M = T · Rz · Ry · Rx · S
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import uuid

import numpy as np

import cgip.transformations as t2d
import cgip.projection_3d as t3d


OBJECT_COLORS_2D = ["#6C5CE7", "#526CCB", "#2F9E78", "#D65362", "#C07800"]
OBJECT_COLORS_3D = [
    (0.42, 0.36, 0.90),
    (0.32, 0.42, 0.80),
    (0.18, 0.62, 0.47),
    (0.84, 0.33, 0.38),
    (0.85, 0.66, 0.31),
]


def new_id() -> str:
    return uuid.uuid4().hex[:10]


def default_shape_2d(kind: str) -> List[Tuple[float, float]]:
    kind = kind.lower()
    if kind == "point":
        return [(0.0, 0.0)]
    if kind == "line":
        return [(-2.0, 0.0), (2.0, 0.0)]
    if kind == "triangle":
        return [(-1.5, -1.0), (1.5, -1.0), (0.0, 1.6)]
    if kind in ("rectangle", "rect"):
        return [(-2.0, -1.2), (2.0, -1.2), (2.0, 1.2), (-2.0, 1.2)]
    if kind == "polygon":
        return [(0.0, 1.8), (1.7, 0.6), (1.1, -1.5), (-1.1, -1.5), (-1.7, 0.6)]
    raise ValueError(f"Unknown 2D shape: {kind}")


@dataclass
class TransformOp:
    """One sequential transform that has been applied on top of the object pose."""
    kind: str
    params: Dict[str, Any]
    matrix: np.ndarray
    label: str = ""

    def copy(self) -> "TransformOp":
        return TransformOp(
            kind=self.kind,
            params=dict(self.params),
            matrix=np.array(self.matrix, dtype=float, copy=True),
            label=self.label,
        )


@dataclass
class SceneObject2D:
    kind: str
    local_vertices: List[Tuple[float, float]]
    name: str = ""
    color: str = "#6C5CE7"
    id: str = field(default_factory=new_id)
    tx: float = 0.0
    ty: float = 0.0
    rotation: float = 0.0
    sx: float = 1.0
    sy: float = 1.0
    history: List[TransformOp] = field(default_factory=list)

    def pose_matrix(self) -> np.ndarray:
        s = t2d.scaling_matrix(self.sx, self.sy)
        r = t2d.rotation_matrix(self.rotation)
        t = t2d.translation_matrix(self.tx, self.ty)
        return t @ r @ s

    def extra_matrix(self) -> np.ndarray:
        if not self.history:
            return np.eye(3, dtype=float)
        return t2d.compose_transformations(*[op.matrix for op in self.history])

    def composed_matrix(self) -> np.ndarray:
        return self.extra_matrix() @ self.pose_matrix()

    def matrix_without_last(self) -> np.ndarray:
        if not self.history:
            return self.pose_matrix()
        prior = t2d.compose_transformations(*[op.matrix for op in self.history[:-1]]) if len(self.history) > 1 else np.eye(3, dtype=float)
        return prior @ self.pose_matrix()

    def world_vertices(self) -> List[Tuple[float, float]]:
        return t2d.apply_transform(self.composed_matrix(), self.local_vertices)

    def previous_world_vertices(self) -> List[Tuple[float, float]]:
        return t2d.apply_transform(self.matrix_without_last(), self.local_vertices)

    def apply_op(self, op: TransformOp) -> None:
        self.history.append(op)

    def reset_transforms(self) -> None:
        self.tx = 0.0
        self.ty = 0.0
        self.rotation = 0.0
        self.sx = 1.0
        self.sy = 1.0
        self.history.clear()


@dataclass
class SceneObject3D:
    kind: str
    name: str = ""
    color: Tuple[float, float, float] = (0.42, 0.36, 0.90)
    id: str = field(default_factory=new_id)
    tx: float = 0.0
    ty: float = 0.0
    tz: float = 0.0
    rx: float = 0.0
    ry: float = 0.0
    rz: float = 0.0
    sx: float = 1.0
    sy: float = 1.0
    sz: float = 1.0
    history: List[TransformOp] = field(default_factory=list)

    def pose_matrix(self) -> np.ndarray:
        return t3d.model_matrix_3d(
            tx=self.tx, ty=self.ty, tz=self.tz,
            sx=self.sx, sy=self.sy, sz=self.sz,
            rx_deg=self.rx, ry_deg=self.ry, rz_deg=self.rz,
        )

    def extra_matrix(self) -> np.ndarray:
        if not self.history:
            return np.eye(4, dtype=np.float64)
        return t3d.compose_transformations_3d(*[op.matrix for op in self.history])

    def composed_matrix(self) -> np.ndarray:
        return self.extra_matrix() @ self.pose_matrix()

    def matrix_without_last(self) -> np.ndarray:
        if not self.history:
            return self.pose_matrix()
        prior = (
            t3d.compose_transformations_3d(*[op.matrix for op in self.history[:-1]])
            if len(self.history) > 1
            else np.eye(4, dtype=np.float64)
        )
        return prior @ self.pose_matrix()

    def local_vertices(self) -> List[Tuple[float, float, float]]:
        return geometry_vertices_3d(self.kind)

    def world_vertices(self) -> List[Tuple[float, float, float]]:
        return t3d.apply_transform_3d(self.composed_matrix(), self.local_vertices())

    def previous_world_vertices(self) -> List[Tuple[float, float, float]]:
        return t3d.apply_transform_3d(self.matrix_without_last(), self.local_vertices())

    def apply_op(self, op: TransformOp) -> None:
        self.history.append(op)

    def reset_transforms(self) -> None:
        self.tx = self.ty = self.tz = 0.0
        self.rx = self.ry = self.rz = 0.0
        self.sx = self.sy = self.sz = 1.0
        self.history.clear()

    def centroid(self) -> Tuple[float, float, float]:
        verts = self.world_vertices()
        if not verts:
            return (0.0, 0.0, 0.0)
        xs, ys, zs = zip(*verts)
        n = float(len(verts))
        return (sum(xs) / n, sum(ys) / n, sum(zs) / n)


def geometry_vertices_3d(kind: str) -> List[Tuple[float, float, float]]:
    kind = kind.lower()
    if kind == "pyramid":
        verts, _ = t3d.get_wireframe_pyramid()
        return verts
    if kind == "sphere":
        verts, _, _ = t3d.get_wireframe_sphere()
        return verts
    if kind == "cylinder":
        verts, _, _ = t3d.get_wireframe_cylinder()
        return verts
    verts, _ = t3d.get_wireframe_cube()
    return verts


def make_translate_op_2d(dx: float, dy: float) -> TransformOp:
    m = t2d.translation_matrix(dx, dy)
    return TransformOp("translate", {"dx": dx, "dy": dy}, m, f"T({dx:g}, {dy:g})")


def make_rotate_op_2d(angle: float, cx: float = 0.0, cy: float = 0.0) -> TransformOp:
    m = t2d.rotation_matrix(angle, cx=cx, cy=cy)
    if cx or cy:
        label = f"R({angle:g}° @ {cx:g},{cy:g})"
    else:
        label = f"R({angle:g}°)"
    return TransformOp("rotate", {"angle": angle, "cx": cx, "cy": cy}, m, label)


def make_scale_op_2d(sx: float, sy: float, cx: float = 0.0, cy: float = 0.0) -> TransformOp:
    m = t2d.scaling_matrix(sx, sy, cx=cx, cy=cy)
    return TransformOp("scale", {"sx": sx, "sy": sy, "cx": cx, "cy": cy}, m, f"S({sx:g}, {sy:g})")


def make_reflect_op_2d(axis: str) -> TransformOp:
    m = t2d.reflection_matrix(axis)
    return TransformOp("reflect", {"axis": axis}, m, f"Reflect {axis}")


def make_translate_op_3d(dx: float, dy: float, dz: float) -> TransformOp:
    m = t3d.translation_matrix_3d(dx, dy, dz)
    return TransformOp("translate", {"dx": dx, "dy": dy, "dz": dz}, m, f"T({dx:g}, {dy:g}, {dz:g})")


def make_rotate_op_3d(axis: str, angle: float) -> TransformOp:
    axis = axis.lower()
    if axis == "x":
        m = t3d.rotation_x_matrix_3d(angle)
    elif axis == "y":
        m = t3d.rotation_y_matrix_3d(angle)
    else:
        m = t3d.rotation_z_matrix_3d(angle)
        axis = "z"
    return TransformOp("rotate", {"axis": axis, "angle": angle}, m, f"R{axis.upper()}({angle:g}°)")


def make_scale_op_3d(sx: float, sy: float, sz: float) -> TransformOp:
    m = t3d.scaling_matrix_3d(sx, sy, sz)
    return TransformOp("scale", {"sx": sx, "sy": sy, "sz": sz}, m, f"S({sx:g}, {sy:g}, {sz:g})")


def interpolate_op_matrix(op: TransformOp, t: float, dim: int = 2) -> np.ndarray:
    """Interpolate a sequential op from identity (t=0) to the full transform (t=1)."""
    t = max(0.0, min(1.0, float(t)))
    p = op.params
    if op.kind == "translate":
        if dim == 2:
            return t2d.translation_matrix(p.get("dx", 0.0) * t, p.get("dy", 0.0) * t)
        return t3d.translation_matrix_3d(p.get("dx", 0.0) * t, p.get("dy", 0.0) * t, p.get("dz", 0.0) * t)
    if op.kind == "rotate":
        if dim == 2:
            return t2d.rotation_matrix(p.get("angle", 0.0) * t, cx=p.get("cx", 0.0), cy=p.get("cy", 0.0))
        return make_rotate_op_3d(p.get("axis", "z"), p.get("angle", 0.0) * t).matrix
    if op.kind == "scale":
        if dim == 2:
            sx = 1.0 + (p.get("sx", 1.0) - 1.0) * t
            sy = 1.0 + (p.get("sy", 1.0) - 1.0) * t
            return t2d.scaling_matrix(sx, sy, cx=p.get("cx", 0.0), cy=p.get("cy", 0.0))
        sx = 1.0 + (p.get("sx", 1.0) - 1.0) * t
        sy = 1.0 + (p.get("sy", 1.0) - 1.0) * t
        sz = 1.0 + (p.get("sz", 1.0) - 1.0) * t
        return t3d.scaling_matrix_3d(sx, sy, sz)
    if op.kind == "reflect":
        if t < 1.0:
            return np.eye(3 if dim == 2 else 4, dtype=float)
        return np.array(op.matrix, dtype=float, copy=True)
    return np.array(op.matrix, dtype=float, copy=True)


def composed_matrix_through(obj, op_index: int, t: float = 1.0, dim: int = 2) -> np.ndarray:
    """Pose plus history[0..op_index], with that last included op interpolated at t.

    op_index < 0 → pose only. op_index past the end is clamped to the last op.
    """
    pose = obj.pose_matrix()
    hist = getattr(obj, "history", None) or []
    if int(op_index) < 0 or not hist:
        return pose
    k = min(int(op_index), len(hist) - 1)
    extras = [op.matrix for op in hist[:k]]
    extras.append(interpolate_op_matrix(hist[k], t, dim=dim))
    if dim == 2:
        extra = t2d.compose_transformations(*extras)
        return extra @ pose
    extra = t3d.compose_transformations_3d(*extras)
    return extra @ pose


def animated_composed_matrix(obj, t: float, dim: int = 2) -> np.ndarray:
    """Composed matrix while the last history op is interpolating at time t."""
    if not obj.history:
        return obj.pose_matrix()
    return composed_matrix_through(obj, len(obj.history) - 1, t, dim=dim)
