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
from typing import Tuple, Dict, Any, Optional

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
        self.object_type = "cube"          # 'cube', 'pyramid'
        self.projection_mode = "perspective" # 'perspective', 'orthographic'

        # Camera orbit controls
        self.camera_azimuth = 35.0         # degrees around Y axis
        self.camera_elevation = 22.0       # degrees above XZ plane
        self.camera_distance = 7.0         # distance from target
        self.camera_target = [0.0, 0.0, 0.0]
        self.camera_pan = [0.0, 0.0]

        # Display toggles
        self.show_axes = True
        self.show_grid = True
        self.show_faces = True

        # Mouse interaction tracking
        self._dragging = False
        self._drag_button = None
        self._last_mouse_pos = QPoint()

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
        """Set active 3D geometric primitive ('cube' or 'pyramid')."""
        self.object_type = obj_type.lower()
        self.update()

    def set_show_grid(self, show: bool):
        self.show_grid = bool(show)
        self.update()

    def reset_view(self):
        """Restore default camera orbit position."""
        self.camera_azimuth = 35.0
        self.camera_elevation = 22.0
        self.camera_distance = 7.0
        self.camera_pan = [0.0, 0.0]
        self.viewChanged.emit(self.camera_azimuth, self.camera_elevation, self.camera_distance)
        self.update()

    def zoom_in(self, factor: float = 0.85):
        """Decrease camera distance (zoom into 3D scene)."""
        self.camera_distance = max(2.0, min(35.0, self.camera_distance * factor))
        self.viewChanged.emit(self.camera_azimuth, self.camera_elevation, self.camera_distance)
        self.update()

    def zoom_out(self, factor: float = 1.18):
        """Increase camera distance (zoom out of 3D scene)."""
        self.camera_distance = max(2.0, min(35.0, self.camera_distance * factor))
        self.viewChanged.emit(self.camera_azimuth, self.camera_elevation, self.camera_distance)
        self.update()

    def pan(self, dx: float, dy: float):
        """Pan camera center across the viewing screen plane."""
        pan_speed = 0.015 * (self.camera_distance / 7.0)
        self.camera_pan[0] += dx * pan_speed
        self.camera_pan[1] += dy * pan_speed
        self.update()

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

        # 1. Compute Camera Eye Position in Spherical Coordinates
        az_rad = math.radians(self.camera_azimuth)
        el_rad = math.radians(self.camera_elevation)
        d = self.camera_distance

        eye_x = d * math.cos(el_rad) * math.sin(az_rad) + self.camera_pan[0]
        eye_y = d * math.sin(el_rad) + self.camera_pan[1]
        eye_z = d * math.cos(el_rad) * math.cos(az_rad)
        target = (self.camera_pan[0], self.camera_pan[1], 0.0)

        # 2. Compute 4x4 View Matrix (look_at)
        self.current_view_matrix = p3d.look_at_matrix(
            eye=(eye_x, eye_y, eye_z),
            target=target,
            up=(0.0, 1.0, 0.0)
        )

        # 3. Compute 4x4 Projection Matrix
        if self.projection_mode == "perspective":
            self.current_proj_matrix = p3d.perspective_projection_matrix(
                fov_deg=45.0, aspect=aspect, near=0.1, far=100.0
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

        # 6. Render Model Geometry Transformed by Model Matrix
        # Multiply ModelView = View @ Model
        model_view = self.current_view_matrix @ self.current_model_matrix
        mv_cm = np.ascontiguousarray(model_view.T, dtype=np.float64)
        gl.glLoadMatrixd(mv_cm)

        if self.object_type == "pyramid":
            self._render_pyramid()
        else:
            self._render_cube()

        # 7. 2D HUD Text Overlay via QPainter
        self._render_hud_overlay()

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
        status_text = (
            f"OpenGL 3D Hardware Accelerated | Mode: {mode_str} | "
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
        hint = "Left-drag: Orbit Camera | Right-drag: Pan | Scroll: Zoom | Reset View in controls"
        painter.drawText(16, self.height() - 12, hint)

        painter.end()

    # ----------------------------------------------------------------------
    # Mouse & Keyboard Interaction
    # ----------------------------------------------------------------------
    def mousePressEvent(self, event):
        self._dragging = True
        self._drag_button = event.button()
        self._last_mouse_pos = event.pos()
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)
        elif event.button() == Qt.RightButton:
            self.setCursor(Qt.SizeAllCursor)

    def mouseMoveEvent(self, event):
        if self._dragging:
            delta = event.pos() - self._last_mouse_pos
            self._last_mouse_pos = event.pos()

            if self._drag_button == Qt.LeftButton:
                # Orbit camera: horizontal movement changes azimuth, vertical changes elevation
                self.camera_azimuth = (self.camera_azimuth + delta.x() * 0.45) % 360.0
                self.camera_elevation = max(-89.0, min(89.0, self.camera_elevation + delta.y() * 0.45))
                self.viewChanged.emit(self.camera_azimuth, self.camera_elevation, self.camera_distance)
                self.update()

            elif self._drag_button == Qt.RightButton:
                # Pan camera
                pan_speed = 0.008 * (self.camera_distance / 7.0)
                self.camera_pan[0] -= delta.x() * pan_speed
                self.camera_pan[1] += delta.y() * pan_speed
                self.update()

    def mouseReleaseEvent(self, event):
        self._dragging = False
        self._drag_button = None
        self.setCursor(Qt.ArrowCursor)

    def wheelEvent(self, event):
        # Zoom camera in/out
        delta = event.angleDelta().y()
        factor = 0.90 if delta > 0 else 1.10
        self.camera_distance = max(2.0, min(35.0, self.camera_distance * factor))
        self.viewChanged.emit(self.camera_azimuth, self.camera_elevation, self.camera_distance)
        self.update()
