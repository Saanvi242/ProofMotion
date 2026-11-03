"""
playground/math_sync.py
-----------------------
Format matrices and coordinate tables that stay synchronized with the
matrices actually applied to playground objects.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from playground.models import SceneObject2D, SceneObject3D, TransformOp


def format_matrix(m: np.ndarray, decimals: int = 2) -> str:
    arr = np.asarray(m, dtype=float)
    rows = []
    for i in range(arr.shape[0]):
        cells = ", ".join(f"{arr[i, j]:.{decimals}f}" for j in range(arr.shape[1]))
        rows.append(f"[{cells}]")
    return "[" + "\n ".join(rows) + "]"


def format_vertices_2d(
    local: List[Tuple[float, float]],
    world: List[Tuple[float, float]],
    decimals: int = 2,
    limit: int = 8,
) -> str:
    lines = []
    count = min(len(local), len(world), limit)
    for i in range(count):
        label = chr(ord("A") + i) if i < 26 else f"P{i}"
        lx, ly = local[i]
        wx, wy = world[i]
        lines.append(
            f"{label}  ({lx:.{decimals}f}, {ly:.{decimals}f})  →  ({wx:.{decimals}f}, {wy:.{decimals}f})"
        )
    if len(local) > limit:
        lines.append(f"… {len(local) - limit} more vertices")
    return "\n".join(lines) if lines else "—"


def format_vertices_3d(
    local: List[Tuple[float, float, float]],
    world: List[Tuple[float, float, float]],
    decimals: int = 2,
    limit: int = 8,
) -> str:
    lines = []
    count = min(len(local), len(world), limit)
    for i in range(count):
        label = f"V{i}"
        lx, ly, lz = local[i]
        wx, wy, wz = world[i]
        lines.append(
            f"{label}  ({lx:.{decimals}f}, {ly:.{decimals}f}, {lz:.{decimals}f})"
            f"  →  ({wx:.{decimals}f}, {wy:.{decimals}f}, {wz:.{decimals}f})"
        )
    if len(local) > limit:
        lines.append(f"… {len(local) - limit} more vertices")
    return "\n".join(lines) if lines else "—"


def last_multiply_payload(obj, dim: int = 2) -> Optional[Dict[str, Any]]:
    if not obj.history:
        return None
    last: TransformOp = obj.history[-1]
    prev = obj.matrix_without_last()
    result = obj.composed_matrix()
    return {
        "label": last.label or last.kind,
        "op_matrix": np.array(last.matrix, dtype=float, copy=True),
        "prev_matrix": np.array(prev, dtype=float, copy=True),
        "result_matrix": np.array(result, dtype=float, copy=True),
        "equation": "M = M_op · M_prev",
    }


def inspector_payload_2d(obj: Optional[SceneObject2D]) -> Dict[str, Any]:
    if obj is None:
        return {"empty": True}
    local = list(obj.local_vertices)
    world = obj.world_vertices()
    M = obj.composed_matrix()
    return {
        "empty": False,
        "id": obj.id,
        "name": obj.name,
        "kind": obj.kind,
        "tx": obj.tx,
        "ty": obj.ty,
        "tz": 0.0,
        "rx": 0.0,
        "ry": 0.0,
        "rz": obj.rotation,
        "sx": obj.sx,
        "sy": obj.sy,
        "sz": 1.0,
        "rotation": obj.rotation,
        "matrix": M,
        "matrix_str": format_matrix(M),
        "pose_str": format_matrix(obj.pose_matrix()),
        "coords_str": format_vertices_2d(local, world),
        "local": local,
        "world": world,
        "history": [op.label for op in obj.history],
        "multiply": last_multiply_payload(obj, dim=2),
        "projection": None,
    }


def inspector_payload_3d(
    obj: Optional[SceneObject3D],
    projection_mode: str = "perspective",
    fov_deg: float = 45.0,
) -> Dict[str, Any]:
    if obj is None:
        return {"empty": True, "projection": {"mode": projection_mode, "fov": fov_deg}}
    local = obj.local_vertices()
    world = obj.world_vertices()
    M = obj.composed_matrix()
    return {
        "empty": False,
        "id": obj.id,
        "name": obj.name,
        "kind": obj.kind,
        "tx": obj.tx,
        "ty": obj.ty,
        "tz": obj.tz,
        "rx": obj.rx,
        "ry": obj.ry,
        "rz": obj.rz,
        "sx": obj.sx,
        "sy": obj.sy,
        "sz": obj.sz,
        "matrix": M,
        "matrix_str": format_matrix(M),
        "pose_str": format_matrix(obj.pose_matrix()),
        "coords_str": format_vertices_3d(local, world),
        "local": local,
        "world": world,
        "history": [op.label for op in obj.history],
        "multiply": last_multiply_payload(obj, dim=3),
        "projection": {
            "mode": projection_mode,
            "fov": fov_deg,
        },
    }


def make_rotation_challenge_2d(obj: SceneObject2D, angle: float = 90.0) -> Dict[str, Any]:
    """Freeze current world vertices and compute the result of an extra rotation."""
    import cgip.transformations as t2d

    before = obj.world_vertices()
    m = t2d.rotation_matrix(angle)
    after = t2d.apply_transform(m, before)
    target = after[0] if after else (0.0, 0.0)
    label = chr(ord("A"))
    return {
        "prompt": f"If this {obj.kind} is rotated {angle:g}° about the origin, where does {label} land?",
        "before": before,
        "after": after,
        "target": target,
        "angle": angle,
        "label": label,
        "start": before[0] if before else (0.0, 0.0),
    }
