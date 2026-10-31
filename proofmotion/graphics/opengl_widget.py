"""
graphics/opengl_widget.py
-------------------------
Dedicated Hardware-Accelerated 3D OpenGL Visualization Widget for ProofMotion.

Uses QOpenGLWidget and PyOpenGL with NumPy 4×4 homogeneous transformation matrices:
- Model Matrix (M = T · Rz · Ry · Rx · S)
- View Matrix (V = look_at(eye, target, up))
- Projection Matrix (P = perspective or orthographic)
- 3D Coordinate axes (X = Red, Y = Green, Z = Blue)
- Ground spatial reference grid (XZ plane)
- Interactive orbit camera with mouse drag, pan, zoom, and reset
- Wireframe and depth-buffered shaded 3D geometric primitives (Cube, Pyramid)
- Real-time HUD overlay showing camera coordinates, projection mode, and matrix values
"""

import math
import numpy as np
from typing import Tuple, Dict, Any, Optional, List

from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QPoint, QRectF, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QFont, QPen

import OpenGL.GL as gl
import cgip.projection_3d as p3d
from resources.theme import COLORS, get_mono_font


class OpenGL3DWidget(QOpenGLWidget):
    """
    Hardware-accelerated 3D OpenGL Canvas integrated into ProofMotion.
    Demonstrates GPU-accelerated 3D transformations, projections, and depth testing.
    """
    viewChanged = pyqtSignal(float, float, float) # azimuth, elevation, distance
    cameraChanged = pyqtSignal()
    objectPicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(360, 240)
        self.setMouseTracking(True)

        # 3D Model transformation parameters
        self.tx = 0.0
        self.ty = 0.0
        self.tz = 0.0
        self.sx = 1.0
        self.sy = 1.0
        self.sz = 1.0
        self.rx = 25.0
        self.ry = 35.0
        self.rz = 0.0

        # Object selection
        self.object_type = "cube"          # 'cube', 'pyramid', 'sphere', 'cylinder'
        self.projection_mode = "perspective" # 'perspective', 'orthographic'
        self.fov_deg = 45.0
        self.scene_objects: Optional[List[Dict[str, Any]]] = None
        self._overlay_lines: List[Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, ...]]] = []
        self._overlay_plane_y: Optional[float] = None

        # Camera orbit controls — eye rides a sphere around camera_target
        self.camera_azimuth = 35.0         # degrees around Y axis
        self.camera_elevation = 22.0       # degrees above XZ plane
        self.camera_distance = 7.0         # distance from target
        self.camera_target = [0.0, 0.0, 0.0]
        self.camera_pan = [0.0, 0.0]       # alias of target x/y for older callers

        # Display toggles
        self.show_axes = True
        self.show_grid = True
        self.show_faces = True

        # Mouse interaction tracking
        self._dragging = False
        self._drag_mode = None             # 'orbit' | 'pan' | 'dolly'
        self._drag_button = None
        self._last_mouse_pos = QPoint()
        self._press_pos = QPoint()
        self._syncing_camera = False
        self.setFocusPolicy(Qt.StrongFocus)
        self.setCursor(Qt.OpenHandCursor)

        # Matrices cache for inspection / HUD
        self.current_model_matrix = np.eye(4, dtype=np.float64)
        self.current_view_matrix = np.eye(4, dtype=np.float64)
        self.current_proj_matrix = np.eye(4, dtype=np.float64)

    # ----------------------------------------------------------------------
    # Public Control API
    # ----------------------------------------------------------------------
    def set_transformations(
        self,
        tx: float = 0.0, ty: float = 0.0, tz: float = 0.0,
        sx: float = 1.0, sy: float = 1.0, sz: float = 1.0,
        rx: float = 0.0, ry: float = 0.0, rz: float = 0.0
    ):
        """Update model 3D transformation parameters."""
        self.tx = float(tx)
        self.ty = float(ty)
        self.tz = float(tz)
        self.sx = float(sx)
        self.sy = float(sy)
        self.sz = float(sz)
        self.rx = float(rx)
        self.ry = float(ry)
        self.rz = float(rz)
        self.update()

    def set_projection_mode(self, mode: str):
        """Switch between 'perspective' and 'orthographic'."""
        self.projection_mode = mode.lower()
        self.update()

    def set_object_type(self, obj_type: str):
        """Set active 3D geometric primitive ('cube', 'pyramid', 'sphere', 'cylinder')."""
        self.object_type = obj_type.lower()
        self.update()

    def set_fov(self, fov_deg: float):
        self.fov_deg = max(15.0, min(90.0, float(fov_deg)))
        self.update()

    def set_show_faces(self, show: bool):
        self.show_faces = bool(show)
        self.update()

    def set_scene_objects(self, objects: Optional[List[Dict[str, Any]]]):
        """
        Playground multi-object mode. Pass None to restore the single-object
        lesson renderer used by the hidden 3D projections catalog.
        """
        self.scene_objects = objects
        self.update()

    def get_camera_state(self) -> Dict[str, float]:
        return {
            "azimuth": self.camera_azimuth,
            "elevation": self.camera_elevation,
            "distance": self.camera_distance,
            "pan_x": self.camera_target[0],
            "pan_y": self.camera_target[1],
            "target_z": self.camera_target[2],
        }

    def set_camera_state(self, state: Dict[str, Any], emit: bool = False):
        self._syncing_camera = True
        self.camera_azimuth = float(state.get("azimuth", self.camera_azimuth))
        self.camera_elevation = float(state.get("elevation", self.camera_elevation))
        self.camera_distance = float(state.get("distance", self.camera_distance))
        self.camera_target = [
            float(state.get("pan_x", state.get("target_x", self.camera_target[0]))),
            float(state.get("pan_y", state.get("target_y", self.camera_target[1]))),
            float(state.get("target_z", self.camera_target[2])),
        ]
        self.camera_pan = [self.camera_target[0], self.camera_target[1]]
        self._syncing_camera = False
        self.update()
        if emit:
            self.viewChanged.emit(self.camera_azimuth, self.camera_elevation, self.camera_distance)
            self.cameraChanged.emit()
        self.update()

    def set_show_grid(self, show: bool):
        self.show_grid = bool(show)
        self.update()

    def set_overlay_lines(self, lines=None):
        """World-space line segments: ((x0,y0,z0), (x1,y1,z1), (r,g,b[,a]))."""
        self._overlay_lines = list(lines or [])
        self.update()

    def set_overlay_plane_y(self, y: Optional[float]):
        self._overlay_plane_y = None if y is None else float(y)
        self.update()

    def reset_view(self):
        """Restore default camera orbit position."""
        self.camera_azimuth = 35.0
        self.camera_elevation = 22.0
        self.camera_distance = 7.0
        self.camera_target = [0.0, 0.0, 0.0]
        self.camera_pan = [0.0, 0.0]
        self.viewChanged.emit(self.camera_azimuth, self.camera_elevation, self.camera_distance)
        self.cameraChanged.emit()
        self.update()

    def zoom_in(self, factor: float = 0.85):
        """Decrease camera distance (zoom into 3D scene)."""
        self.camera_distance = max(2.0, min(35.0, self.camera_distance * factor))
        self.viewChanged.emit(self.camera_azimuth, self.camera_elevation, self.camera_distance)
        self.cameraChanged.emit()
        self.update()

    def zoom_out(self, factor: float = 1.18):
        """Increase camera distance (zoom out of 3D scene)."""
        self.camera_distance = max(2.0, min(35.0, self.camera_distance * factor))
        self.viewChanged.emit(self.camera_azimuth, self.camera_elevation, self.camera_distance)
        self.cameraChanged.emit()
        self.update()

    def pan(self, dx: float, dy: float):
        """Pan the look-at target across the camera's screen plane."""
        self._apply_pan(dx, -dy)
        self._emit_camera()

    def reset_transformations(self):
        """Restore default transformation state."""
        self.tx, self.ty, self.tz = 0.0, 0.0, 0.0
        self.sx, self.sy, self.sz = 1.0, 1.0, 1.0
        self.rx, self.ry, self.rz = 25.0, 35.0, 0.0
        self.update()

    def update_from_parameters(self, values: Dict[str, Any]):
        """Dynamically sync with ProofMotion parameter panel values."""
        if not values:
            return

        if "rx" in values:
            self.rx = float(values.get("rx", self.rx))
        if "ry" in values:
            self.ry = float(values.get("ry", self.ry))
        if "rz" in values:
            self.rz = float(values.get("rz", self.rz))

        if "tx" in values:
            self.tx = float(values.get("tx", self.tx))
        if "ty" in values:
            self.ty = float(values.get("ty", self.ty))
        if "tz" in values:
            self.tz = float(values.get("tz", self.tz))

        if "sx" in values:
            self.sx = float(values.get("sx", self.sx))
        if "sy" in values:
            self.sy = float(values.get("sy", self.sy))
        if "sz" in values:
            self.sz = float(values.get("sz", self.sz))

        if "camera_dist" in values:
            self.camera_distance = max(2.0, min(30.0, float(values["camera_dist"])))

        if "projection" in values:
            self.projection_mode = str(values["projection"]).lower()

        if "shape" in values:
            self.object_type = str(values["shape"]).lower()

        if "fov" in values:
            self.fov_deg = max(15.0, min(90.0, float(values["fov"])))

        self.update()

    # ----------------------------------------------------------------------
    # QOpenGLWidget Lifecycle
    # ----------------------------------------------------------------------
    def initializeGL(self):
        """Initialize OpenGL state, depth testing, blending, and line smoothing."""
        # Theme viewport background: #10151C (0.063, 0.082, 0.110)
        gl.glClearColor(0.063, 0.082, 0.110, 1.0)

        # Enable depth testing so front surfaces occlude back surfaces
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LEQUAL)

        # Enable alpha blending for translucent surfaces
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        # Anti-aliased line smoothing
        gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST)
        gl.glLineWidth(2.0)

    def resizeGL(self, width: int, height: int):
        """Handle widget resize event, updating the OpenGL viewport."""
        w = max(1, width)
        h = max(1, height)
        gl.glViewport(0, 0, w, h)

    def paintGL(self):
        """Core OpenGL rendering pass: computes NumPy MVP matrices and renders 3D scene."""
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        w = max(1, self.width())
        h = max(1, self.height())
        aspect = w / float(h)

        # 1. Compute Camera Eye Position in Spherical Coordinates around the look-at target
        ox, oy, oz = self._orbit_offset()
        tx, ty, tz = self.camera_target
        eye_x, eye_y, eye_z = tx + ox, ty + oy, tz + oz
        target = (tx, ty, tz)

        # 2. Compute 4x4 View Matrix (look_at)
        self.current_view_matrix = p3d.look_at_matrix(
            eye=(eye_x, eye_y, eye_z),
            target=target,
            up=(0.0, 1.0, 0.0)
        )

        # 3. Compute 4x4 Projection Matrix
        if self.projection_mode == "perspective":
            self.current_proj_matrix = p3d.perspective_projection_matrix(
                fov_deg=self.fov_deg, aspect=aspect, near=0.1, far=100.0
            )
        else:
            half_h = 3.2 * (self.camera_distance / 7.0)
            half_w = half_h * aspect
            self.current_proj_matrix = p3d.orthographic_projection_matrix(
                left=-half_w, right=half_w, bottom=-half_h, top=half_h, near=0.1, far=100.0
            )

        # 4. Compute 4x4 Model Matrix (T · Rz · Ry · Rx · S)
        self.current_model_matrix = p3d.model_matrix_3d(
            tx=self.tx, ty=self.ty, tz=self.tz,
            sx=self.sx, sy=self.sy, sz=self.sz,
            rx_deg=self.rx, ry_deg=self.ry, rz_deg=self.rz
        )

        # Load Projection Matrix into OpenGL
        gl.glMatrixMode(gl.GL_PROJECTION)
        proj_cm = np.ascontiguousarray(self.current_proj_matrix.T, dtype=np.float64)
        gl.glLoadMatrixd(proj_cm)

        # Load View Matrix into OpenGL
        gl.glMatrixMode(gl.GL_MODELVIEW)
        view_cm = np.ascontiguousarray(self.current_view_matrix.T, dtype=np.float64)
        gl.glLoadMatrixd(view_cm)

        # 5. Render Reference Elements in World Space
        if self.show_grid:
            self._render_grid()

        if self.show_axes:
            self._render_axes()
        self._render_overlay()

        # 6. Render Model Geometry Transformed by Model Matrix
        # Multiply ModelView = View @ Model
        model_view = self.current_view_matrix @ self.current_model_matrix
        mv_cm = np.ascontiguousarray(model_view.T, dtype=np.float64)
        gl.glLoadMatrixd(mv_cm)

        if self.scene_objects is not None:
            for item in self.scene_objects:
                ghost = item.get("ghost_model")
                if ghost is not None:
                    self._load_modelview(self.current_view_matrix @ np.asarray(ghost, dtype=np.float64))
                    self._render_kind(item.get("kind", "cube"), selected=False, color=(0.45, 0.50, 0.58), faces=False, ghost=True)
                self._load_modelview(self.current_view_matrix @ np.asarray(item["model"], dtype=np.float64))
                self._render_kind(
                    item.get("kind", "cube"),
                    selected=bool(item.get("selected")),
                    color=item.get("color", (0.31, 0.78, 0.69)),
                    faces=self.show_faces,
                )
        elif self.object_type == "pyramid":
            self._render_pyramid()
        elif self.object_type == "sphere":
            self._render_kind("sphere", selected=False, color=(0.31, 0.78, 0.69), faces=self.show_faces)
        elif self.object_type == "cylinder":
            self._render_kind("cylinder", selected=False, color=(0.31, 0.78, 0.69), faces=self.show_faces)
        else:
            self._render_cube()

        # 7. 2D HUD Text Overlay via QPainter
        self._render_hud_overlay()

    def _load_modelview(self, matrix: np.ndarray):
        mv_cm = np.ascontiguousarray(np.asarray(matrix, dtype=np.float64).T)
        gl.glLoadMatrixd(mv_cm)

    def _render_kind(self, kind: str, selected: bool, color, faces: bool, ghost: bool = False):
        kind = (kind or "cube").lower()
        verts, edges, tris = p3d.get_mesh_3d(kind)
        r, g, b = color
        if faces and not ghost and tris:
            gl.glBegin(gl.GL_TRIANGLES)
            gl.glColor4f(r, g, b, 0.22)
            for i0, i1, i2 in tris:
                gl.glVertex3f(*verts[i0])
                gl.glVertex3f(*verts[i1])
                gl.glVertex3f(*verts[i2])
            gl.glEnd()
        gl.glLineWidth(1.2 if ghost else (2.8 if selected else 2.2))
        if ghost:
            gl.glEnable(gl.GL_LINE_STIPPLE)
            gl.glLineStipple(1, 0x0F0F)
            gl.glColor4f(r, g, b, 0.55)
        else:
            gl.glColor4f(0.85, 0.72, 0.28, 0.98) if selected else gl.glColor4f(r, g, b, 0.95)
        gl.glBegin(gl.GL_LINES)
        for i0, i1 in edges:
            gl.glVertex3f(*verts[i0])
            gl.glVertex3f(*verts[i1])
        gl.glEnd()
        if ghost:
            gl.glDisable(gl.GL_LINE_STIPPLE)
        gl.glLineWidth(2.0)

    def project_world_to_screen(self, x: float, y: float, z: float) -> Optional[Tuple[float, float]]:
        v = np.array([float(x), float(y), float(z), 1.0], dtype=np.float64)
        clip = self.current_proj_matrix @ (self.current_view_matrix @ v)
        w = clip[3]
        if abs(w) < 1e-9:
            return None
        ndc = clip[:3] / w
        sx = (ndc[0] * 0.5 + 0.5) * self.width()
        sy = (1.0 - (ndc[1] * 0.5 + 0.5)) * self.height()
        return float(sx), float(sy)

    # ----------------------------------------------------------------------
    # 3D Scene Geometry Renderers
    # ----------------------------------------------------------------------
    def _render_axes(self):
        """Render 3D RGB Coordinate Axes with labels."""
        axis_len = 3.0
        gl.glLineWidth(2.5)
        gl.glBegin(gl.GL_LINES)

        # X Axis — Vibrant Red / Coral
        gl.glColor3f(0.89, 0.41, 0.36)
        gl.glVertex3f(0.0, 0.0, 0.0)
        gl.glVertex3f(axis_len, 0.0, 0.0)

        # Y Axis — Vibrant Teal / Mint
        gl.glColor3f(0.31, 0.78, 0.69)
        gl.glVertex3f(0.0, 0.0, 0.0)
        gl.glVertex3f(0.0, axis_len, 0.0)

        # Z Axis — Vibrant Blue / Indigo
        gl.glColor3f(0.36, 0.55, 0.94)
        gl.glVertex3f(0.0, 0.0, 0.0)
        gl.glVertex3f(0.0, 0.0, axis_len)

        gl.glEnd()
        gl.glLineWidth(2.0)

    def _render_overlay(self):
        if self._overlay_plane_y is not None:
            y = self._overlay_plane_y
            s = 3.4
            gl.glEnable(gl.GL_BLEND)
            gl.glBegin(gl.GL_QUADS)
            gl.glColor4f(0.96, 0.45, 0.71, 0.10)
            gl.glVertex3f(-s, y, -s)
            gl.glVertex3f(s, y, -s)
            gl.glVertex3f(s, y, s)
            gl.glVertex3f(-s, y, s)
            gl.glEnd()
            gl.glLineWidth(1.0)
            gl.glBegin(gl.GL_LINES)
            gl.glColor4f(0.96, 0.45, 0.71, 0.35)
            n = 4
            for i in range(-n, n + 1):
                gl.glVertex3f(float(i), y, -s)
                gl.glVertex3f(float(i), y, s)
                gl.glVertex3f(-s, y, float(i))
                gl.glVertex3f(s, y, float(i))
            gl.glEnd()
        if self._overlay_lines:
            gl.glLineWidth(2.2)
            gl.glBegin(gl.GL_LINES)
            for a, b, color in self._overlay_lines:
                r, g, bl = color[0], color[1], color[2]
                alpha = color[3] if len(color) > 3 else 0.92
                gl.glColor4f(float(r), float(g), float(bl), float(alpha))
                gl.glVertex3f(float(a[0]), float(a[1]), float(a[2]))
                gl.glVertex3f(float(b[0]), float(b[1]), float(b[2]))
            gl.glEnd()
            gl.glLineWidth(2.0)

    def _render_grid(self):
        """Render subtle spatial ground grid on XZ plane."""
        grid_size = 5.0
        step = 1.0
        gl.glLineWidth(1.0)
        gl.glBegin(gl.GL_LINES)
        gl.glColor4f(0.18, 0.24, 0.31, 0.45) # Dark muted grid lines

        n_lines = int(grid_size / step)
        for i in range(-n_lines, n_lines + 1):
            coord = i * step
            # Lines parallel to Z axis
            gl.glVertex3f(coord, 0.0, -grid_size)
            gl.glVertex3f(coord, 0.0, grid_size)
            # Lines parallel to X axis
            gl.glVertex3f(-grid_size, 0.0, coord)
            gl.glVertex3f(grid_size, 0.0, coord)

        gl.glEnd()
        gl.glLineWidth(2.0)

    def _render_cube(self):
        """Render 3D Cube with translucent shaded faces and crisp wireframe edges."""
        s = 1.0  # side length = 2.0 (from -1 to 1)

        # 1. Translucent solid faces for 3D depth cueing
        if self.show_faces:
            gl.glBegin(gl.GL_QUADS)
            # Front face (Z = +1)
            gl.glColor4f(0.31, 0.78, 0.69, 0.20) # Teal
            gl.glVertex3f(-s, -s,  s)
            gl.glVertex3f( s, -s,  s)
            gl.glVertex3f( s,  s,  s)
            gl.glVertex3f(-s,  s,  s)

            # Back face (Z = -1)
            gl.glColor4f(0.36, 0.55, 0.94, 0.16) # Blue
            gl.glVertex3f(-s, -s, -s)
            gl.glVertex3f(-s,  s, -s)
            gl.glVertex3f( s,  s, -s)
            gl.glVertex3f( s, -s, -s)

            # Top face (Y = +1)
            gl.glColor4f(0.85, 0.66, 0.31, 0.22) # Gold
            gl.glVertex3f(-s,  s, -s)
            gl.glVertex3f(-s,  s,  s)
            gl.glVertex3f( s,  s,  s)
            gl.glVertex3f( s,  s, -s)

            # Bottom face (Y = -1)
            gl.glColor4f(0.20, 0.28, 0.38, 0.25)
            gl.glVertex3f(-s, -s, -s)
            gl.glVertex3f( s, -s, -s)
            gl.glVertex3f( s, -s,  s)
            gl.glVertex3f(-s, -s,  s)

            # Right face (X = +1)
            gl.glColor4f(0.31, 0.78, 0.69, 0.18)
            gl.glVertex3f( s, -s, -s)
            gl.glVertex3f( s,  s, -s)
            gl.glVertex3f( s,  s,  s)
            gl.glVertex3f( s, -s,  s)

            # Left face (X = -1)
            gl.glColor4f(0.36, 0.55, 0.94, 0.18)
            gl.glVertex3f(-s, -s, -s)
            gl.glVertex3f(-s, -s,  s)
            gl.glVertex3f(-s,  s,  s)
            gl.glVertex3f(-s,  s, -s)
            gl.glEnd()

        # 2. Crisp Wireframe Edges
        gl.glLineWidth(2.5)
        gl.glColor4f(0.31, 0.78, 0.69, 0.95) # Vibrant teal outline
        gl.glBegin(gl.GL_LINES)

        # Back square
        gl.glVertex3f(-s, -s, -s); gl.glVertex3f( s, -s, -s)
        gl.glVertex3f( s, -s, -s); gl.glVertex3f( s,  s, -s)
        gl.glVertex3f( s,  s, -s); gl.glVertex3f(-s,  s, -s)
        gl.glVertex3f(-s,  s, -s); gl.glVertex3f(-s, -s, -s)

        # Front square
        gl.glVertex3f(-s, -s,  s); gl.glVertex3f( s, -s,  s)
        gl.glVertex3f( s, -s,  s); gl.glVertex3f( s,  s,  s)
        gl.glVertex3f( s,  s,  s); gl.glVertex3f(-s,  s,  s)
        gl.glVertex3f(-s,  s,  s); gl.glVertex3f(-s, -s,  s)

        # Connecting longitudinal edges
        gl.glVertex3f(-s, -s, -s); gl.glVertex3f(-s, -s,  s)
        gl.glVertex3f( s, -s, -s); gl.glVertex3f( s, -s,  s)
        gl.glVertex3f( s,  s, -s); gl.glVertex3f( s,  s,  s)
        gl.glVertex3f(-s,  s, -s); gl.glVertex3f(-s,  s,  s)

        gl.glEnd()

        # 3. Vertex Highlight Points
        gl.glPointSize(6.0)
        gl.glColor3f(0.85, 0.66, 0.31) # Gold points
        gl.glBegin(gl.GL_POINTS)
        for vx in (-s, s):
            for vy in (-s, s):
                for vz in (-s, s):
                    gl.glVertex3f(vx, vy, vz)
        gl.glEnd()
        gl.glPointSize(1.0)
        gl.glLineWidth(2.0)

    def _render_pyramid(self):
        """Render 3D Square Pyramid with wireframe and shaded sides."""
        s = 1.2
        h = 1.6

        # Translucent faces
        if self.show_faces:
            gl.glBegin(gl.GL_TRIANGLES)
            # Front side
            gl.glColor4f(0.31, 0.78, 0.69, 0.25)
            gl.glVertex3f(-s, -h/2,  s)
            gl.glVertex3f( s, -h/2,  s)
            gl.glVertex3f(0.0, h/2, 0.0)

            # Right side
            gl.glColor4f(0.85, 0.66, 0.31, 0.22)
            gl.glVertex3f( s, -h/2,  s)
            gl.glVertex3f( s, -h/2, -s)
            gl.glVertex3f(0.0, h/2, 0.0)

            # Back side
            gl.glColor4f(0.36, 0.55, 0.94, 0.20)
            gl.glVertex3f( s, -h/2, -s)
            gl.glVertex3f(-s, -h/2, -s)
            gl.glVertex3f(0.0, h/2, 0.0)

            # Left side
            gl.glColor4f(0.89, 0.41, 0.36, 0.22)
            gl.glVertex3f(-s, -h/2, -s)
            gl.glVertex3f(-s, -h/2,  s)
            gl.glVertex3f(0.0, h/2, 0.0)
            gl.glEnd()

        # Wireframe edges
        gl.glLineWidth(2.5)
        gl.glColor4f(0.31, 0.78, 0.69, 0.95)
        gl.glBegin(gl.GL_LINES)
        # Base
        gl.glVertex3f(-s, -h/2, -s); gl.glVertex3f( s, -h/2, -s)
        gl.glVertex3f( s, -h/2, -s); gl.glVertex3f( s, -h/2,  s)
        gl.glVertex3f( s, -h/2,  s); gl.glVertex3f(-s, -h/2,  s)
        gl.glVertex3f(-s, -h/2,  s); gl.glVertex3f(-s, -h/2, -s)
        # Apex connections
        gl.glVertex3f(-s, -h/2, -s); gl.glVertex3f(0.0, h/2, 0.0)
        gl.glVertex3f( s, -h/2, -s); gl.glVertex3f(0.0, h/2, 0.0)
        gl.glVertex3f( s, -h/2,  s); gl.glVertex3f(0.0, h/2, 0.0)
        gl.glVertex3f(-s, -h/2,  s); gl.glVertex3f(0.0, h/2, 0.0)
        gl.glEnd()

        # Vertex points
        gl.glPointSize(6.0)
        gl.glColor3f(0.85, 0.66, 0.31)
        gl.glBegin(gl.GL_POINTS)
        gl.glVertex3f(-s, -h/2, -s)
        gl.glVertex3f( s, -h/2, -s)
        gl.glVertex3f( s, -h/2,  s)
        gl.glVertex3f(-s, -h/2,  s)
        gl.glVertex3f(0.0, h/2, 0.0)
        gl.glEnd()
        gl.glPointSize(1.0)
        gl.glLineWidth(2.0)

    # ----------------------------------------------------------------------
    # 2D HUD Text Overlay via QPainter
    # ----------------------------------------------------------------------
    def _render_hud_overlay(self):
        """Draws non-intrusive HUD status and camera details over the OpenGL view."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        painter.setFont(get_mono_font(12, weight=400))

        # Top-right status badge
        mode_str = self.projection_mode.capitalize()
        fov_bit = f" FOV={self.fov_deg:.0f}° |" if self.projection_mode == "perspective" else " "
        status_text = (
            f"OpenGL 3D Hardware Accelerated | Mode: {mode_str} |{fov_bit}"
            f"Orbit: Az={self.camera_azimuth:.0f}° El={self.camera_elevation:.0f}° Dist={self.camera_distance:.1f}"
        )
        painter.setPen(QPen(QColor(COLORS["text_muted"])))
        painter.drawText(
            QRectF(12, 10, self.width() - 24, 20),
            Qt.AlignRight | Qt.AlignVCenter,
            status_text
        )

        # Top-left axes legend
        painter.setFont(get_mono_font(12, weight=600))
        legend_y = 12
        painter.setPen(QPen(QColor("#E4685D")))
        painter.drawText(16, legend_y + 12, "— X Axis (Pitch)")
        painter.setPen(QPen(QColor("#4EC7B0")))
        painter.drawText(16, legend_y + 28, "— Y Axis (Yaw / Height)")
        painter.setPen(QPen(QColor("#5B8DEF")))
        painter.drawText(16, legend_y + 44, "— Z Axis (Roll / Depth)")

        # Bottom-left interaction hint
        painter.setFont(get_mono_font(11, weight=400))
        painter.setPen(QPen(QColor(COLORS["text_muted"])))
        hint = "Drag to orbit  ·  Right-drag or Shift-drag to pan  ·  Scroll to zoom  ·  Double-click to frame"
        painter.drawText(16, self.height() - 12, hint)

        painter.end()

    # ----------------------------------------------------------------------
    # Camera basis (orbit around look-at target)
    # ----------------------------------------------------------------------
    def _orbit_offset(self) -> Tuple[float, float, float]:
        az = math.radians(self.camera_azimuth)
        el = math.radians(self.camera_elevation)
        d = self.camera_distance
        c_el, s_el = math.cos(el), math.sin(el)
        return (
            d * c_el * math.sin(az),
            d * s_el,
            d * c_el * math.cos(az),
        )

    def _camera_basis(self) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
        """Screen-right and screen-up unit vectors at the current orbit pose."""
        az = math.radians(self.camera_azimuth)
        el = math.radians(self.camera_elevation)
        s_az, c_az = math.sin(az), math.cos(az)
        s_el, c_el = math.sin(el), math.cos(el)
        right = (c_az, 0.0, -s_az)
        up = (-s_el * s_az, c_el, -s_el * c_az)
        return right, up

    def _sync_pan_alias(self):
        self.camera_pan = [self.camera_target[0], self.camera_target[1]]

    def _emit_camera(self):
        self._sync_pan_alias()
        if not self._syncing_camera:
            self.viewChanged.emit(self.camera_azimuth, self.camera_elevation, self.camera_distance)
            self.cameraChanged.emit()
        self.update()

    def _apply_orbit(self, dx: float, dy: float):
        # Grab-the-scene: the world follows the cursor.
        self.camera_azimuth = (self.camera_azimuth - dx * 0.42) % 360.0
        self.camera_elevation = max(-89.0, min(89.0, self.camera_elevation + dy * 0.38))

    def _apply_pan(self, dx: float, dy: float):
        right, up = self._camera_basis()
        scale = 0.012 * (self.camera_distance / 7.0)
        for i in range(3):
            self.camera_target[i] -= right[i] * dx * scale
            self.camera_target[i] += up[i] * dy * scale
        self._sync_pan_alias()

    def _apply_dolly(self, dy: float):
        factor = 1.0 + dy * 0.01
        self.camera_distance = max(1.2, min(40.0, self.camera_distance * factor))

    def _drag_mode_for(self, event) -> str:
        mods = event.modifiers()
        button = event.button()
        if button in (Qt.RightButton, Qt.MiddleButton) or (button == Qt.LeftButton and mods & Qt.ShiftModifier):
            return "pan"
        if button == Qt.LeftButton and mods & Qt.ControlModifier:
            return "dolly"
        return "orbit"

    # ----------------------------------------------------------------------
    # Mouse & Keyboard Interaction
    # ----------------------------------------------------------------------
    def enterEvent(self, event):
        if not self._dragging:
            self.setCursor(Qt.OpenHandCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self._dragging:
            self.setCursor(Qt.ArrowCursor)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self._dragging = True
        self._drag_button = event.button()
        self._drag_mode = self._drag_mode_for(event)
        self._last_mouse_pos = event.pos()
        self._press_pos = event.pos()
        self.setFocus(Qt.MouseFocusReason)
        if self._drag_mode == "pan":
            self.setCursor(Qt.SizeAllCursor)
        else:
            self.setCursor(Qt.ClosedHandCursor)
        event.accept()

    def mouseMoveEvent(self, event):
        if not self._dragging:
            return
        delta = event.pos() - self._last_mouse_pos
        self._last_mouse_pos = event.pos()
        dx, dy = float(delta.x()), float(delta.y())
        if abs(dx) < 0.1 and abs(dy) < 0.1:
            return
        if self._drag_mode == "pan":
            self._apply_pan(dx, dy)
        elif self._drag_mode == "dolly":
            self._apply_dolly(dy)
        else:
            self._apply_orbit(dx, dy)
        self._emit_camera()
        event.accept()

    def mouseReleaseEvent(self, event):
        moved = (event.pos() - self._press_pos).manhattanLength() if not self._press_pos.isNull() else 999
        mode = self._drag_mode
        self._dragging = False
        self._drag_button = None
        self._drag_mode = None
        self.setCursor(Qt.OpenHandCursor)
        if event.button() == Qt.LeftButton and mode == "orbit" and moved < 8 and self.scene_objects:
            picked = self._pick_object(event.pos())
            if picked:
                self.objectPicked.emit(picked)
        event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.reset_view()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta == 0:
            delta = event.pixelDelta().y()
        factor = 0.88 if delta > 0 else 1.14
        self.camera_distance = max(1.2, min(40.0, self.camera_distance * factor))
        self._emit_camera()
        event.accept()

    def keyPressEvent(self, event):
        key = event.key()
        step = 8.0
        if key == Qt.Key_Left:
            self._apply_orbit(-step, 0)
        elif key == Qt.Key_Right:
            self._apply_orbit(step, 0)
        elif key == Qt.Key_Up:
            self._apply_orbit(0, -step)
        elif key == Qt.Key_Down:
            self._apply_orbit(0, step)
        elif key in (Qt.Key_Plus, Qt.Key_Equal):
            self.zoom_in()
            return
        elif key == Qt.Key_Minus:
            self.zoom_out()
            return
        elif key == Qt.Key_F:
            self.reset_view()
            return
        else:
            super().keyPressEvent(event)
            return
        self._emit_camera()
        event.accept()

    def _pick_object(self, pos: QPoint) -> Optional[str]:
        best_id = None
        best_dist = 56.0
        px, py = float(pos.x()), float(pos.y())
        for item in self.scene_objects or []:
            model = np.asarray(item.get("model"), dtype=np.float64)
            origin = model @ np.array([0.0, 0.0, 0.0, 1.0])
            screen = self.project_world_to_screen(origin[0], origin[1], origin[2])
            if screen is None:
                continue
            dist = math.hypot(screen[0] - px, screen[1] - py)
            if dist < best_dist:
                best_dist = dist
                best_id = item.get("id")
        return best_id
