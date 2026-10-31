"""
playground/experiences.py
-------------------------
Pure math for Studio experiences. No Qt.

Living Basis: columns of M are î and ĵ.
Homogeneous Lift: 2D (x, y) visualized as world (x, w, y) so w is height.
Pipeline Runway: one shape through T/R/S → clip → Bresenham pixels.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

import cgip.clipping as clip
import cgip.projection_3d as t3d
import cgip.rasterization as rast
import cgip.transformations as t2d


Point2 = Tuple[float, float]
Point3 = Tuple[float, float, float]


def living_basis_matrix(ix: float, iy: float, jx: float, jy: float) -> np.ndarray:
    """3×3 homogeneous matrix whose columns are î, ĵ, and the origin."""
    return np.array(
        [
            [float(ix), float(jx), 0.0],
            [float(iy), float(jy), 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )


def living_basis_det(ix: float, iy: float, jx: float, jy: float) -> float:
    return float(ix) * float(jy) - float(iy) * float(jx)


def deform_points(
    ix: float, iy: float, jx: float, jy: float,
    points: Sequence[Point2],
) -> List[Point2]:
    return t2d.apply_transform(living_basis_matrix(ix, iy, jx, jy), list(points))


def unit_grid_lines(n: int = 4, extent: float = 3.0) -> List[List[Point2]]:
    lines: List[List[Point2]] = []
    if n <= 0:
        return lines
    step = extent / float(n)
    i = -n
    while i <= n:
        t = i * step
        lines.append([(-extent, t), (extent, t)])
        lines.append([(t, -extent), (t, extent)])
        i += 1
    return lines


def sample_letter_f() -> List[Point2]:
    """A blocky F in the unit square, origin at the corner."""
    return [
        (0.0, 0.0), (0.35, 0.0), (0.35, 1.1), (1.15, 1.1),
        (1.15, 1.45), (0.35, 1.45), (0.35, 1.85), (1.45, 1.85),
        (1.45, 2.2), (0.0, 2.2),
    ]


def homogeneous_lift_point(x: float, y: float, w: float) -> Point3:
    """Visualize homogeneous (x, y, w) as world (x, w, y) so w is height."""
    return (float(x), float(w), float(y))


def apply_homogeneous(matrix: np.ndarray, x: float, y: float, w: float = 1.0) -> Tuple[float, float, float]:
    v = np.asarray(matrix, dtype=float) @ np.array([float(x), float(y), float(w)], dtype=float)
    return float(v[0]), float(v[1]), float(v[2])


def lift_vertices(
    points: Sequence[Point2],
    w: float,
    extra: Optional[np.ndarray] = None,
) -> List[Point3]:
    """Apply an optional 2D 3×3 extra, then lift each point to height w."""
    mat = np.eye(3, dtype=float) if extra is None else np.asarray(extra, dtype=float)
    w = float(w)
    out: List[Point3] = []
    for x, y in points:
        X, Y, W = apply_homogeneous(mat, x, y, 1.0)
        height = w * (W if abs(W) > 1e-9 else 1.0)
        out.append(homogeneous_lift_point(X, Y, height))
    return out


def ground_vertices(points: Sequence[Point2], extra: Optional[np.ndarray] = None) -> List[Point3]:
    return lift_vertices(points, 0.0, extra=extra)


def world_to_grid(
    x: float,
    y: float,
    grid_size: int = 18,
    span: float = 12.0,
) -> Tuple[int, int]:
    span = float(span) if span else 12.0
    s = span / 2.0
    gx = int(round((float(x) + s) / span * (grid_size - 1)))
    gy = int(round((float(y) + s) / span * (grid_size - 1)))
    return gx, gy


def pipeline_matrix(angle: float, sx: float, sy: float, t: float = 1.0) -> np.ndarray:
    """Interpolate S then R from identity (t=0) to the full transform (t=1)."""
    t = max(0.0, min(1.0, float(t)))
    sx_t = 1.0 + (float(sx) - 1.0) * t
    sy_t = 1.0 + (float(sy) - 1.0) * t
    S = t2d.scaling_matrix(sx_t, sy_t)
    R = t2d.rotation_matrix(float(angle) * t)
    return R @ S


def rasterize_polygon_edges(
    verts: Sequence[Point2],
    grid_size: int = 18,
    span: float = 12.0,
) -> List[Tuple[int, int]]:
    if len(verts) < 2:
        return []
    seen = set()
    pixels: List[Tuple[int, int]] = []
    n = len(verts)
    closed = n >= 3
    count = n if closed else n - 1
    for i in range(count):
        x0, y0 = verts[i]
        x1, y1 = verts[(i + 1) % n]
        g0 = world_to_grid(x0, y0, grid_size=grid_size, span=span)
        g1 = world_to_grid(x1, y1, grid_size=grid_size, span=span)
        for px in rast.bresenham_line(g0[0], g0[1], g1[0], g1[1]):
            if px not in seen:
                seen.add(px)
                pixels.append(px)
    return pixels


def pipeline_state(
    vertices: Sequence[Point2],
    angle: float = 35.0,
    sx: float = 1.35,
    sy: float = 1.35,
    clip_rect: Tuple[float, float, float, float] = (-3.0, -2.0, 3.0, 2.0),
    t: float = 1.0,
    grid_size: int = 18,
    span: float = 12.0,
) -> Dict[str, Any]:
    """One shape through Transform → Clip → Raster, parameterized by t in [0, 1]."""
    t = max(0.0, min(1.0, float(t)))
    verts = [(float(x), float(y)) for x, y in vertices]
    transform_t = min(1.0, t * 3.0)
    clip_t = min(1.0, max(0.0, (t - 1.0 / 3.0) * 3.0))
    rast_t = min(1.0, max(0.0, (t - 2.0 / 3.0) * 3.0))
    station = 0 if t < 1.0 / 3.0 else (1 if t < 2.0 / 3.0 else 2)

    M = pipeline_matrix(angle, sx, sy, transform_t)
    transformed = t2d.apply_transform(M, verts)
    xmin, ymin, xmax, ymax = clip_rect
    clipped = clip.sutherland_hodgman_polygon_clip(transformed, xmin, ymin, xmax, ymax) if clip_t > 0 else []
    source = clipped if clipped else transformed
    all_pixels = rasterize_polygon_edges(source, grid_size=grid_size, span=span) if rast_t > 0 else []
    count = int(round(len(all_pixels) * rast_t)) if all_pixels else 0
    pixels = all_pixels[: max(count, 1 if all_pixels and rast_t > 0 else 0)]

    return {
        "t": t,
        "station": station,
        "transform_t": transform_t,
        "clip_t": clip_t,
        "rast_t": rast_t,
        "matrix": M,
        "original": verts,
        "transformed": transformed,
        "clipped": clipped,
        "clip_rect": tuple(clip_rect),
        "pixels": pixels,
        "all_pixels": all_pixels,
        "grid_size": int(grid_size),
        "span": float(span),
    }
