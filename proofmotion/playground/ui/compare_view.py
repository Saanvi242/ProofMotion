"""Synchronized perspective | orthographic OpenGL viewports."""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

from graphics.opengl_widget import OpenGL3DWidget


class CompareView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._syncing = False
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)

        self.persp = OpenGL3DWidget()
        self.ortho = OpenGL3DWidget()
        self.persp.set_projection_mode("perspective")
        self.ortho.set_projection_mode("orthographic")

        row.addWidget(self._wrap(self.persp, "Perspective"), stretch=1)
        row.addWidget(self._wrap(self.ortho, "Orthographic"), stretch=1)

        self.persp.cameraChanged.connect(lambda: self._mirror(self.persp, self.ortho))
        self.ortho.cameraChanged.connect(lambda: self._mirror(self.ortho, self.persp))

    def _wrap(self, widget: OpenGL3DWidget, title: str) -> QWidget:
        box = QWidget()
        col = QVBoxLayout(box)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(4)
        lab = QLabel(title)
        lab.setObjectName("SpeedLabel")
        lab.setAlignment(Qt.AlignCenter)
        col.addWidget(lab)
        col.addWidget(widget, stretch=1)
        return box

    def _mirror(self, src: OpenGL3DWidget, dst: OpenGL3DWidget):
        if self._syncing:
            return
        self._syncing = True
        dst.set_camera_state(src.get_camera_state(), emit=False)
        self._syncing = False

    def bind_scene(self, payload, fov: float, show_faces: bool, show_grid: bool):
        for w in (self.persp, self.ortho):
            w.set_fov(fov)
            w.set_show_faces(show_faces)
            w.set_show_grid(show_grid)
            w.set_scene_objects(payload)

    def sync_camera_from(self, state: dict):
        self._syncing = True
        self.persp.set_camera_state(state, emit=False)
        self.ortho.set_camera_state(state, emit=False)
        self._syncing = False
