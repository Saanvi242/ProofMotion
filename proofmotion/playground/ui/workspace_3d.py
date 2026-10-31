"""3D Studio workspace: full-bleed viewport with floating chrome."""

from PyQt5.QtWidgets import QWidget, QStackedWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

from graphics.opengl_widget import OpenGL3DWidget
from playground.scene_3d import Scene3D
from playground.math_sync import inspector_payload_3d
from playground.models import composed_matrix_through
from playground.ui.compare_view import CompareView
from playground.ui.studio_chrome import (
    StudioToolRail, StudioMatrixHud, StudioActionBar, build_studio_layout,
)
from playground.ui.filmstrip import StudioFilmstrip


class Playground3DWorkspace(QWidget):
    statusMessage = pyqtSignal(str)
    fullscreenToggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StudioStage")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.scene = Scene3D()
        self._focus = False
        self._ignore_camera = False

        self.view_stack = QStackedWidget()
        self.view_stack.setObjectName("StudioViewport")
        self.gl = OpenGL3DWidget()
        self.compare = CompareView()
        self.view_stack.addWidget(self.gl)
        self.view_stack.addWidget(self.compare)

        self.rail = StudioToolRail("3d")
        self.hud = StudioMatrixHud()
        self.bar = StudioActionBar("3d")
        self.filmstrip = StudioFilmstrip()
        self.toolbar = self.bar
        self.compare_btn = self.bar.compare_btn
        build_studio_layout(self, self.view_stack, self.rail, self.hud, self.bar, self.filmstrip)
        self._film_index = None
        self._film_t = 1.0

        self._anim = QTimer(self)
        self._anim.setInterval(16)
        self._anim.timeout.connect(self._tick_anim)
        self._anim_t = 0.0

        self.scene.subscribe(self._refresh)
        self._wire()
        self._refresh()

    def _wire(self):
        self.rail.create3dRequested.connect(self.scene.add_object)
        self.rail.deleteRequested.connect(self.scene.delete_selected)
        self.bar.rotateClicked.connect(lambda: self._nudge("rotate"))
        self.bar.scaleClicked.connect(lambda: self._nudge("scale"))
        self.bar.animateRequested.connect(self._animate_last)
        self.bar.resetObject.connect(self.scene.reset_selected)
        self.bar.orthoToggled.connect(self._set_ortho)
        self.bar.compareToggled.connect(self._set_compare)
        self.bar.fullscreenToggled.connect(self.fullscreenToggled.emit)
        self.bar.ghostToggled.connect(self.scene.set_show_ghost)
        self.bar.wireToggled.connect(self.scene.set_wireframe)
        self.filmstrip.frameChanged.connect(self._on_film)
        self.gl.objectPicked.connect(self.scene.select)
        self.compare.persp.objectPicked.connect(self.scene.select)
        self.compare.ortho.objectPicked.connect(self.scene.select)
        self.gl.cameraChanged.connect(self._capture_camera)

    def _nudge(self, kind: str):
        if self.scene.selected() is None:
            self.statusMessage.emit("Select an object first.")
            return
        if kind == "rotate":
            self.scene.apply_rotate("Y", 40.0)
        else:
            self.scene.apply_scale(1.35, 1.35, 1.35)
        self.statusMessage.emit(f"Applied 3D {kind}.")
        self._animate_last()

    def _capture_camera(self):
        if self._ignore_camera:
            return
        self.scene.camera.update(self.gl.get_camera_state())

    def _reset_camera(self):
        self.scene.reset_camera()
        self._push_camera()

    def _push_camera(self):
        self._ignore_camera = True
        self.gl.set_camera_state(self.scene.camera, emit=False)
        self.compare.sync_camera_from(self.scene.camera)
        self._ignore_camera = False

    def _set_ortho(self, on: bool):
        self.scene.set_projection_mode("orthographic" if on else "perspective")

    def _set_compare(self, on: bool):
        self.scene.set_compare_mode(on)
        self.view_stack.setCurrentIndex(1 if on else 0)
        self._refresh()
        self.statusMessage.emit(
            "Perspective and orthographic, side by side." if on else "Single 3D viewport."
        )

    def _animate_last(self):
        obj = self.scene.selected()
        if obj is None:
            self.statusMessage.emit("Select an object first.")
            return
        if not obj.history:
            self.scene.apply_rotate("Y", 40.0)
        self._anim_t = 0.0
        self._film_index = len(obj.history) - 1
        self._film_t = 0.0
        self.filmstrip.set_playhead(self._film_index, 0.0)
        self._anim.start()

    def _tick_anim(self):
        self._anim_t += 0.04
        obj = self.scene.selected()
        if obj is None or not obj.history or self._anim_t >= 1.0:
            self._anim.stop()
            self._film_index = None
            if obj is not None and obj.history:
                self.filmstrip.set_playhead(len(obj.history) - 1, 1.0)
            self._refresh()
            return
        self._film_t = self._anim_t
        self.filmstrip.set_playhead(len(obj.history) - 1, self._anim_t)
        self._push_payload(self._filmed_payload())

    def _on_film(self, op_index: int, t: float):
        self._anim.stop()
        self._film_index = op_index
        self._film_t = t
        self._push_payload(self._filmed_payload())

    def _filmed_payload(self):
        payload = self.scene.render_payload()
        obj = self.scene.selected()
        if obj is None or self._film_index is None:
            return payload
        t = self._anim_t if self._anim.isActive() else self._film_t
        for item in payload:
            if item["id"] == obj.id:
                item["model"] = composed_matrix_through(obj, self._film_index, t, dim=3)
        return payload

    def _push_payload(self, payload):
        faces = not self.scene.wireframe
        self.gl.set_fov(self.scene.fov_deg)
        self.gl.set_show_faces(faces)
        self.gl.set_show_grid(self.scene.show_grid)
        self.gl.set_projection_mode(self.scene.projection_mode)
        self.gl.set_scene_objects(payload)
        self.compare.bind_scene(payload, self.scene.fov_deg, faces, self.scene.show_grid)

    def _refresh(self):
        obj = self.scene.selected()
        self.hud.bind(inspector_payload_3d(
            obj,
            projection_mode=self.scene.projection_mode,
            fov_deg=self.scene.fov_deg,
        ))
        self.filmstrip.bind(obj)
        if obj is None or (self._film_index is not None and self._film_index >= len(obj.history)):
            self._film_index = None
        if self._anim.isActive() or self._film_index is not None:
            self._push_payload(self._filmed_payload())
        else:
            self._push_payload(self.scene.render_payload())
        self._push_camera()

    def set_focus_mode(self, on: bool):
        self._focus = bool(on)
        self.rail.setVisible(not on)
        self.hud.setVisible(not on)
        self.bar.setVisible(not on)
        self.filmstrip.setVisible(not on)

    def set_fullscreen_button(self, on: bool):
        self.bar.fullscreen_btn.blockSignals(True)
        self.bar.fullscreen_btn.setChecked(on)
        self.bar.fullscreen_btn.blockSignals(False)

    def apply_starter(self, kind: str):
        obj = self.scene.selected()
        if obj is None and self.scene.objects:
            self.scene.select(self.scene.objects[0].id)
            obj = self.scene.selected()
        if kind == "spin":
            if obj is None:
                self.statusMessage.emit("Add a primitive first, then spin it.")
                return
            self.scene.reset_selected()
            self.scene.apply_rotate("Y", 55.0)
            self._animate_last()
            self.statusMessage.emit("Spinning around Y.")
        elif kind == "clip":
            if self.compare_btn is not None and not self.compare_btn.isChecked():
                self.compare_btn.setChecked(True)
            else:
                self._set_compare(True)
            self.statusMessage.emit("Perspective and orthographic, side by side.")
        elif kind == "stack":
            if obj is None:
                self.statusMessage.emit("Add a primitive first, then stack transforms.")
                return
            self.scene.reset_selected()
            self.scene.apply_translate(1.2, 0.4, 0.0)
            self.scene.apply_rotate("Z", 35.0)
            self._animate_last()
            self.statusMessage.emit("Stacked T then R.")
