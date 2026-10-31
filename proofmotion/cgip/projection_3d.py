"""
cgip/projection_3d.py
---------------------
3D Computer Graphics Transformations and 3D-to-2D Projections Studio.

Implements 4×4 homogeneous coordinates (column-vector convention P' = M · P):
- 3D Translation T(dx, dy, dz)
- 3D Scaling S(sx, sy, sz)
- 3D Euler Rotations: Rx(θ), Ry(θ), Rz(θ)
- Composite 3D Transformations
- Orthographic Projection
- Perspective Projection with perspective division
- 3D Wireframe models (Cube, Triangular Pyramid)
- Projecting calculated 3D coordinates to 2D view space for rendering
"""

import math
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from core.step_model import VisualizationStep, RenderData, Point2D, Line2D, Text2D
from resources.theme import COLORS


# --------------------------------------------------------------------------
# 4x4 Homogeneous Transformation Matrices
# --------------------------------------------------------------------------

def translation_matrix_3d(dx: float, dy: float, dz: float) -> np.ndarray:
    """4x4 translation matrix for column vectors."""
    return np.array([
        [1.0, 0.0, 0.0, float(dx)],
        [0.0, 1.0, 0.0, float(dy)],
        [0.0, 0.0, 1.0, float(dz)],
        [0.0, 0.0, 0.0, 1.0]
    ], dtype=np.float64)


def scaling_matrix_3d(sx: float, sy: float, sz: float) -> np.ndarray:
    """4x4 scaling matrix for column vectors."""
    return np.array([
        [float(sx), 0.0, 0.0, 0.0],
        [0.0, float(sy), 0.0, 0.0],
        [0.0, 0.0, float(sz), 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ], dtype=np.float64)


def rotation_x_matrix_3d(theta_deg: float) -> np.ndarray:
    """4x4 rotation matrix around X-axis."""
    rad = math.radians(theta_deg)
    c = math.cos(rad)
    s = math.sin(rad)
    return np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, c,   -s,  0.0],
        [0.0, s,    c,  0.0],
        [0.0, 0.0, 0.0, 1.0]
    ], dtype=np.float64)


def rotation_y_matrix_3d(theta_deg: float) -> np.ndarray:
    """4x4 rotation matrix around Y-axis."""
    rad = math.radians(theta_deg)
    c = math.cos(rad)
    s = math.sin(rad)
    return np.array([
        [c,   0.0, s,   0.0],
        [0.0, 1.0, 0.0, 0.0],
        [-s,  0.0, c,   0.0],
        [0.0, 0.0, 0.0, 1.0]
    ], dtype=np.float64)


def rotation_z_matrix_3d(theta_deg: float) -> np.ndarray:
    """4x4 rotation matrix around Z-axis."""
    rad = math.radians(theta_deg)
    c = math.cos(rad)
    s = math.sin(rad)
    return np.array([
        [c,   -s,  0.0, 0.0],
        [s,    c,  0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ], dtype=np.float64)


def compose_transformations_3d(*matrices: np.ndarray) -> np.ndarray:
    """
    Composes 4x4 transformation matrices in sequential application order:
    compose(M1, M2, M3) = M3 @ M2 @ M1 for column vectors.
    """
    res = np.eye(4, dtype=np.float64)
    for m in matrices:
        res = np.asarray(m, dtype=np.float64) @ res
    return res


def model_matrix_3d(
    tx: float = 0.0, ty: float = 0.0, tz: float = 0.0,
    sx: float = 1.0, sy: float = 1.0, sz: float = 1.0,
    rx_deg: float = 0.0, ry_deg: float = 0.0, rz_deg: float = 0.0
) -> np.ndarray:
    """
    Computes standard 4x4 Model Transformation Matrix M = T · Rz · Ry · Rx · S.
    Transformation order: Scale first, then Rotations (X -> Y -> Z), then Translation.
    """
    t_mat = translation_matrix_3d(tx, ty, tz)
    s_mat = scaling_matrix_3d(sx, sy, sz)
    rx_mat = rotation_x_matrix_3d(rx_deg)
    ry_mat = rotation_y_matrix_3d(ry_deg)
    rz_mat = rotation_z_matrix_3d(rz_deg)
    # Order: Scale -> Rx -> Ry -> Rz -> Translate
    return t_mat @ rz_mat @ ry_mat @ rx_mat @ s_mat


def perspective_projection_matrix(
    fov_deg: float = 45.0,
    aspect: float = 1.333,
    near: float = 0.1,
    far: float = 100.0
) -> np.ndarray:
    """
    Computes standard OpenGL 4x4 Perspective Projection Matrix:
    P = [[ f/aspect,   0,             0,                         0 ],
         [    0,       f,             0,                         0 ],
         [    0,       0,   -(far+near)/(far-near),  -2*far*near/(far-near) ],
         [    0,       0,            -1,                         0 ]]
    where f = 1 / tan(fov_rad / 2).
    """
    if aspect <= 0 or near <= 0 or far <= near:
        raise ValueError("Invalid perspective parameters: aspect > 0, 0 < near < far.")

    fov_rad = math.radians(fov_deg)
    f = 1.0 / math.tan(fov_rad / 2.0)
    nf = 1.0 / (near - far)

    return np.array([
        [f / aspect, 0.0,  0.0,                      0.0],
        [0.0,        f,    0.0,                      0.0],
        [0.0,        0.0,  (far + near) * nf,        2.0 * far * near * nf],
        [0.0,        0.0,  -1.0,                     0.0]
    ], dtype=np.float64)


def orthographic_projection_matrix(
    left: float = -3.0,
    right: float = 3.0,
    bottom: float = -3.0,
    top: float = 3.0,
    near: float = 0.1,
    far: float = 100.0
) -> np.ndarray:
    """
    Computes standard OpenGL 4x4 Orthographic Projection Matrix:
    Maps viewing cuboid [left..right, bottom..top, -far..-near] to NDC [-1..1, -1..1, -1..1].
    """
    if right <= left or top <= bottom or far <= near:
        raise ValueError("Invalid orthographic bounds: right > left, top > bottom, far > near.")

    dx = right - left
    dy = top - bottom
    dz = far - near

    return np.array([
        [2.0 / dx, 0.0,      0.0,       -(right + left) / dx],
        [0.0,      2.0 / dy, 0.0,       -(top + bottom) / dy],
        [0.0,      0.0,     -2.0 / dz,  -(far + near) / dz],
        [0.0,      0.0,      0.0,        1.0]
    ], dtype=np.float64)


def look_at_matrix(
    eye: Tuple[float, float, float],
    target: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    up: Tuple[float, float, float] = (0.0, 1.0, 0.0)
) -> np.ndarray:
    """
    Computes standard OpenGL 4x4 Camera View Matrix (gluLookAt):
    Transforms world coordinates into camera view space.
    """
    eye_vec = np.array(eye, dtype=np.float64)
    target_vec = np.array(target, dtype=np.float64)
    up_vec = np.array(up, dtype=np.float64)

    # Forward direction (from target to eye for right-handed camera space, looking along -Z)
    forward = eye_vec - target_vec
    forward_norm = np.linalg.norm(forward)
    if forward_norm < 1e-9:
        forward = np.array([0.0, 0.0, 1.0])
    else:
        forward = forward / forward_norm

    # Right vector = normalize(up x forward)
    right = np.cross(up_vec, forward)
    right_norm = np.linalg.norm(right)
    if right_norm < 1e-9:
        right = np.array([1.0, 0.0, 0.0])
    else:
        right = right / right_norm

    # True up vector = forward x right
    true_up = np.cross(forward, right)

    # View matrix rotation and translation
    v = np.eye(4, dtype=np.float64)
    v[0, 0:3] = right
    v[1, 0:3] = true_up
    v[2, 0:3] = forward
    v[0, 3] = -np.dot(right, eye_vec)
    v[1, 3] = -np.dot(true_up, eye_vec)
    v[2, 3] = -np.dot(forward, eye_vec)
    return v


def apply_transform_3d(matrix: np.ndarray, points: List[Tuple[float, float, float]]) -> List[Tuple[float, float, float]]:
    """Transform list of 3D (x, y, z) vertices using 4x4 matrix."""
    transformed = []
    for x, y, z in points:
        v = np.array([float(x), float(y), float(z), 1.0], dtype=np.float64)
        v_prime = matrix @ v
        # Homogeneous normalization if w != 1.0
        w = v_prime[3]
        if abs(w) > 1e-9 and w != 1.0:
            transformed.append((float(v_prime[0] / w), float(v_prime[1] / w), float(v_prime[2] / w)))
        else:
            transformed.append((float(v_prime[0]), float(v_prime[1]), float(v_prime[2])))
    return transformed


# --------------------------------------------------------------------------
# 3D to 2D Projections
# --------------------------------------------------------------------------

def project_orthographic(points_3d: List[Tuple[float, float, float]], scale: float = 1.0) -> List[Tuple[float, float]]:
    """
    Orthographic parallel projection onto the XY plane:
    (x, y, z) -> (scale * x, scale * y)
    Z-coordinate is ignored for depth projection.
    """
    return [(float(x * scale), float(y * scale)) for x, y, z in points_3d]


def project_perspective(
    points_3d: List[Tuple[float, float, float]],
    focal_distance: float = 4.0,
    camera_z: float = 6.0
) -> List[Tuple[float, float]]:
    """
    Perspective projection with center of projection at (0, 0, camera_z).
    Formula:
        x_proj = (x * focal_distance) / (camera_z - z)
        y_proj = (y * focal_distance) / (camera_z - z)
    """
    projected = []
    for x, y, z in points_3d:
        denom = camera_z - z
        if abs(denom) < 0.1:
            denom = 0.1 if denom >= 0 else -0.1
        factor = focal_distance / denom
        projected.append((float(x * factor), float(y * factor)))
    return projected


# --------------------------------------------------------------------------
# 3D Geometry Models
# --------------------------------------------------------------------------

def get_wireframe_cube(side: float = 2.0) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int]]]:
    """
    Returns 8 vertices and 12 connecting edges for a 3D cube centered at origin.
    """
    s = side / 2.0
    vertices = [
        (-s, -s, -s),  # 0: back bottom left
        ( s, -s, -s),  # 1: back bottom right
        ( s,  s, -s),  # 2: back top right
        (-s,  s, -s),  # 3: back top left
        (-s, -s,  s),  # 4: front bottom left
        ( s, -s,  s),  # 5: front bottom right
        ( s,  s,  s),  # 6: front top right
        (-s,  s,  s),  # 7: front top left
    ]
    edges = [
        # Back face
        (0, 1), (1, 2), (2, 3), (3, 0),
        # Front face
        (4, 5), (5, 6), (6, 7), (7, 4),
        # Connecting side edges
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]
    return vertices, edges


def get_wireframe_pyramid(base_side: float = 2.4, height: float = 2.5) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int]]]:
    """
    Returns 5 vertices and 8 edges for a square-based 3D pyramid.
    """
    s = base_side / 2.0
    vertices = [
        (-s, -height/2, -s),  # 0: base
        ( s, -height/2, -s),  # 1: base
        ( s, -height/2,  s),  # 2: base
        (-s, -height/2,  s),  # 3: base
        (0.0, height/2, 0.0), # 4: apex
    ]
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # base square
        (0, 4), (1, 4), (2, 4), (3, 4),  # sides to apex
    ]
    return vertices, edges


def get_wireframe_sphere(
    radius: float = 1.2,
    slices: int = 16,
    stacks: int = 12,
) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int]], List[Tuple[int, int, int]]]:
    """
    UV sphere centered at the origin.
    Returns (vertices, wireframe edges, triangle faces).
    """
    slices = max(3, int(slices))
    stacks = max(2, int(stacks))
    vertices: List[Tuple[float, float, float]] = []
    for i in range(stacks + 1):
        phi = math.pi * i / stacks
        y = radius * math.cos(phi)
        ring_r = radius * math.sin(phi)
        for j in range(slices):
            theta = 2.0 * math.pi * j / slices
            x = ring_r * math.cos(theta)
            z = ring_r * math.sin(theta)
            vertices.append((float(x), float(y), float(z)))

    edges: List[Tuple[int, int]] = []
    faces: List[Tuple[int, int, int]] = []
    for i in range(stacks + 1):
        for j in range(slices):
            a = i * slices + j
            b = i * slices + (j + 1) % slices
            if i < stacks:
                edges.append((a, b))
            if i < stacks:
                c = (i + 1) * slices + j
                edges.append((a, c))
                d = (i + 1) * slices + (j + 1) % slices
                if i == 0:
                    faces.append((a, c, d))
                elif i == stacks - 1:
                    faces.append((a, c, b))
                else:
                    faces.append((a, c, d))
                    faces.append((a, d, b))
    return vertices, edges, faces


def get_wireframe_cylinder(
    radius: float = 0.85,
    height: float = 2.2,
    slices: int = 20,
) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int]], List[Tuple[int, int, int]]]:
    """
    Cylinder aligned with the Y axis, centered at the origin.
    Returns (vertices, wireframe edges, triangle faces).
    Vertex layout: bottom ring [0..slices), top ring [slices..2*slices),
    bottom center, top center.
    """
    slices = max(3, int(slices))
    y0 = -height / 2.0
    y1 = height / 2.0
    vertices: List[Tuple[float, float, float]] = []
    for y in (y0, y1):
        for j in range(slices):
            theta = 2.0 * math.pi * j / slices
            vertices.append((radius * math.cos(theta), y, radius * math.sin(theta)))
    vertices.append((0.0, y0, 0.0))
    vertices.append((0.0, y1, 0.0))
    bottom_center = 2 * slices
    top_center = 2 * slices + 1

    edges: List[Tuple[int, int]] = []
    faces: List[Tuple[int, int, int]] = []
    for j in range(slices):
        jn = (j + 1) % slices
        b0, b1 = j, jn
        t0, t1 = slices + j, slices + jn
        edges.append((b0, b1))
        edges.append((t0, t1))
        edges.append((b0, t0))
        faces.append((b0, b1, t1))
        faces.append((b0, t1, t0))
        faces.append((bottom_center, b1, b0))
        faces.append((top_center, t0, t1))
    return vertices, edges, faces


def get_mesh_3d(kind: str):
    """Return (vertices, edges, faces) for a named 3D primitive."""
    kind = (kind or "cube").lower()
    if kind == "pyramid":
        verts, edges = get_wireframe_pyramid()
        faces = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (0, 3, 2), (0, 2, 1)]
        return verts, edges, faces
    if kind == "sphere":
        return get_wireframe_sphere()
    if kind == "cylinder":
        return get_wireframe_cylinder()
    verts, edges = get_wireframe_cube()
    faces = [
        (4, 5, 6), (4, 6, 7),  # front
        (1, 0, 3), (1, 3, 2),  # back
        (7, 6, 2), (7, 2, 3),  # top
        (0, 1, 5), (0, 5, 4),  # bottom
        (5, 1, 2), (5, 2, 6),  # right
        (0, 4, 7), (0, 7, 3),  # left
    ]
    return verts, edges, faces


# --------------------------------------------------------------------------
# Demonstration & Trace Generator
# --------------------------------------------------------------------------

def generate_3d_demo(
    object_type: str = "cube",
    projection_mode: str = "perspective",
    rx_deg: float = 25.0,
    ry_deg: float = 35.0,
    rz_deg: float = 0.0,
    focal_distance: float = 4.5,
    camera_distance: float = 7.0,
    tx: float = 0.0,
    ty: float = 0.0,
    tz: float = 0.0,
    sx: float = 1.0,
    sy: float = 1.0,
    sz: float = 1.0,
) -> List[VisualizationStep]:
    """
    Generates step-by-step 3D transformations and projection trace.
    Steps:
      1. Original 3D Object Definition (Vertices & Topology Edges)
      2. 3D Model Transformation Matrix (M = T · Rz · Ry · Rx · S)
      3. Projection from 3D World Space to 2D Screen Space
    """
    if object_type == "pyramid":
        verts_3d, edges = get_wireframe_pyramid()
        obj_name = "Square-Based Pyramid"
    else:
        verts_3d, edges = get_wireframe_cube()
        obj_name = "Unit 3D Cube"

    steps = []

    # Step 1: Base 3D Model
    m_model = model_matrix_3d(tx=tx, ty=ty, tz=tz, sx=sx, sy=sy, sz=sz, rx_deg=rx_deg, ry_deg=ry_deg, rz_deg=rz_deg)
    transformed_3d = apply_transform_3d(m_model, verts_3d)

    # Step 1: Unrotated initial projection
    pts_2d_orig = project_orthographic(verts_3d, scale=1.0)
    rd1 = RenderData(view_bounds=(-4, -4, 4, 4))
    for i1, i2 in edges:
        p1 = pts_2d_orig[i1]
        p2 = pts_2d_orig[i2]
        rd1.lines.append(Line2D(p1[0], p1[1], p2[0], p2[1], color="#5F7488", width=1.5, dashed=True))
    for i, (px, py) in enumerate(pts_2d_orig):
        rd1.points.append(Point2D(px, py, label=f"V{i}", color="#8FA3B8"))

    steps.append(VisualizationStep(
        index=1,
        title=f"3D Model Definition: {obj_name}",
        equation=f"Vertices: {len(verts_3d)},  Edges: {len(edges)}\nCoordinate Space: 3D Homogeneous [X, Y, Z, 1]ᵀ",
        explanation=f"Defined 3D geometric object '{obj_name}' with {len(verts_3d)} vertices and {len(edges)} wireframe edges. "
                    f"Each vertex is represented as a 4-element homogeneous column vector.",
        values={"vertices_3d": verts_3d, "edges": edges},
        metrics={"vertex_count": len(verts_3d), "edge_count": len(edges)},
        render_data=rd1
    ))

    # Step 2: 3D Model Matrix Transformation (M = T · Rz · Ry · Rx · S)
    rd2 = RenderData(view_bounds=(-4, -4, 4, 4))
    pts_2d_rotated = project_orthographic(transformed_3d, scale=1.0)
    for i1, i2 in edges:
        p1 = pts_2d_rotated[i1]
        p2 = pts_2d_rotated[i2]
        rd2.lines.append(Line2D(p1[0], p1[1], p2[0], p2[1], color=COLORS["accent_gold"], width=2.0))
    for i, (px, py) in enumerate(pts_2d_rotated):
        rd2.points.append(Point2D(px, py, label=f"V{i}'", color="#EAF0F6"))

    eq_model = (
        f"M = T({tx:.1f}, {ty:.1f}, {tz:.1f}) · Rz({rz_deg:.0f}°) · Ry({ry_deg:.0f}°) · Rx({rx_deg:.0f}°) · S({sx:.2f}, {sy:.2f}, {sz:.2f})\n"
        f"P' = M_model · P"
    )
    steps.append(VisualizationStep(
        index=2,
        title=f"3D Model Transformation (T · R · S)",
        equation=eq_model,
        explanation=f"Applied 4×4 affine model matrix: Translation T({tx:.1f}, {ty:.1f}, {tz:.1f}), "
                    f"Rotations Rx={rx_deg:.0f}°, Ry={ry_deg:.0f}°, Rz={rz_deg:.0f}°, and Scale S({sx:.2f}, {sy:.2f}, {sz:.2f}). "
                    f"NumPy calculates the composite 4×4 matrix and transforms all {len(verts_3d)} homogeneous vertices in 3D space.",
        values={
            "transformed_3d": [tuple(round(c, 2) for c in pt) for pt in transformed_3d],
            "translation": (tx, ty, tz),
            "rotation": (rx_deg, ry_deg, rz_deg),
            "scale": (sx, sy, sz),
        },
        metrics={"rx": rx_deg, "ry": ry_deg, "rz": rz_deg, "tx": tx, "ty": ty, "tz": tz},
        render_data=rd2
    ))

    # Step 3: Projection to 2D
    is_perspective = (projection_mode.lower() == "perspective")
    if is_perspective:
        final_2d = project_perspective(transformed_3d, focal_distance=focal_distance, camera_z=camera_distance)
        proj_eq = (f"Perspective Projection (Camera Z = {camera_distance:.1f}, Focal = {focal_distance:.1f}):\n"
                   f"x_proj = (x · f) / (Z_cam - z),   y_proj = (y · f) / (Z_cam - z)")
        proj_expl = ("Perspective projection simulates human vision and cameras: objects farther along Z "
                     "appear smaller due to perspective division by depth distance.")
    else:
        final_2d = project_orthographic(transformed_3d, scale=1.2)
        proj_eq = "Orthographic Projection: x_proj = x · scale,  y_proj = y · scale  (Z ignored)"
        proj_expl = "Orthographic parallel projection projects 3D vertices directly onto the viewing plane preserving parallel lines."

    rd3 = RenderData(view_bounds=(-4, -4, 4, 4))
    # Original in faint
    for i1, i2 in edges:
        p1 = pts_2d_orig[i1]
        p2 = pts_2d_orig[i2]
        rd3.lines.append(Line2D(p1[0], p1[1], p2[0], p2[1], color="#5F7488", width=1.0, dashed=True))

    # Projected wireframe
    for i1, i2 in edges:
        p1 = final_2d[i1]
        p2 = final_2d[i2]
        rd3.lines.append(Line2D(p1[0], p1[1], p2[0], p2[1], color=COLORS["accent_teal"], width=2.5))
    for i, (px, py) in enumerate(final_2d):
        rd3.points.append(Point2D(px, py, label=f"P{i}({px:.1f},{py:.1f})", color=COLORS["accent_gold"]))

    steps.append(VisualizationStep(
        index=3,
        title=f"3D to 2D Projection: {projection_mode.capitalize()} Mode",
        equation=proj_eq,
        explanation=proj_expl,
        values={"projected_2d": [tuple(round(c, 2) for c in pt) for pt in final_2d]},
        metrics={"projection": projection_mode, "points_projected": len(final_2d)},
        render_data=rd3
    ))

    return steps

