"""2D Studio workspace: full-bleed canvas with floating chrome."""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

from playground.scene_2d import Scene2D
from playground.math_sync import inspector_payload_2d
from playground.ui.canvas_2d import PlaygroundCanvas2D
from playground.ui.studio_chrome import (
    StudioToolRail, StudioMatrixHud, StudioActionBar, build_studio_layout,
)
from playground.ui.filmstrip import StudioFilmstrip


class Playground2DWorkspace(QWidget):
    statusMessage = pyqtSignal(str)
    fullscreenToggled = pyqtSignal(bool)
    runwayRequested = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StudioStage")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.scene = Scene2D()
        self._focus = False

        self.canvas = PlaygroundCanvas2D(self.scene)
        self.rail = StudioToolRail("2d")
        self.hud = StudioMatrixHud()
        self.bar = StudioActionBar("2d")
        self.filmstrip = StudioFilmstrip()
        self.toolbar = self.bar
        self.clip_btn = self.rail.clip_btn
        build_studio_layout(self, self.canvas, self.rail, self.hud, self.bar, self.filmstrip)

        self._anim = QTimer(self)
        self._anim.setInterval(16)
        self._anim.timeout.connect(self._tick_anim)
        self._anim_t = 0.0

        self.scene.subscribe(self._refresh)
        self._wire()
        self._refresh()

    def _wire(self):
        self.rail.toolChosen.connect(self.canvas.set_tool)
        self.rail.deleteRequested.connect(self.scene.delete_selected)
        self.rail.clipToggled.connect(self.scene.set_clip_enabled)
        self.bar.rotateClicked.connect(lambda: self._nudge("rotate"))
        self.bar.scaleClicked.connect(lambda: self._nudge("scale"))
        self.bar.animateRequested.connect(self._animate_last)
        self.bar.resetObject.connect(self.scene.reset_selected)
        self.bar.fullscreenToggled.connect(self.fullscreenToggled.emit)
        self.bar.ghostToggled.connect(self.scene.set_show_ghost)
        self.bar.wireToggled.connect(self.scene.set_wireframe)
        self.bar.runwayClicked.connect(self._send_runway)
        self.filmstrip.frameChanged.connect(self._on_film)
        self.canvas.statusMessage.connect(self.statusMessage.emit)

    def _nudge(self, kind: str):
        if self.scene.selected() is None:
            self.statusMessage.emit("Select a shape first.")
            return
        if kind == "rotate":
            self.scene.apply_rotate(45.0)
        else:
            self.scene.apply_scale(1.4, 1.4)
        self.statusMessage.emit(f"Applied {kind}.")
        self._animate_last()

    def _animate_last(self):
        obj = self.scene.selected()
        if obj is None:
            self.statusMessage.emit("Select a shape first.")
            return
        if not obj.history:
            self.scene.apply_rotate(45.0)
        self._anim_t = 0.0
        self.canvas.film_index = len(obj.history) - 1
        self.canvas.film_t = 0.0
        self.canvas.anim_t = 0.0
        self.filmstrip.set_playhead(self.canvas.film_index, 0.0)
        self._anim.start()

    def _tick_anim(self):
        self._anim_t += 0.04
        obj = self.scene.selected()
        if obj is None or not obj.history or self._anim_t >= 1.0:
            self._anim.stop()
            self.canvas.anim_t = None
            if obj is not None and obj.history:
                self.canvas.film_index = None
                self.filmstrip.set_playhead(len(obj.history) - 1, 1.0)
            self.canvas.update()
            return
        self.canvas.anim_t = self._anim_t
        self.filmstrip.set_playhead(len(obj.history) - 1, self._anim_t)
        self.canvas.update()

    def _on_film(self, op_index: int, t: float):
        self._anim.stop()
        self.canvas.anim_t = None
        self.canvas.film_index = op_index
        self.canvas.film_t = t
        self.canvas.update()

    def _send_runway(self):
        obj = self.scene.selected()
        if obj is None:
            self.statusMessage.emit("Select a shape first.")
            return
        self.runwayRequested.emit(obj)

    def _refresh(self):
        obj = self.scene.selected()
        self.hud.bind(inspector_payload_2d(obj))
        self.filmstrip.bind(obj)
        if obj is None:
            self.canvas.film_index = None
        elif self.canvas.film_index is not None and self.canvas.film_index >= len(obj.history):
            self.canvas.film_index = None

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
                self.statusMessage.emit("Add a shape first, then spin it.")
                return
            self.scene.reset_selected()
            self.scene.apply_rotate(50.0)
            self._animate_last()
            self.statusMessage.emit("Spinning the selected shape.")
        elif kind == "clip":
            self.scene.set_clip_enabled(True)
            if self.clip_btn is not None:
                self.clip_btn.blockSignals(True)
                self.clip_btn.setChecked(True)
                self.clip_btn.blockSignals(False)
            self.canvas.update()
            self.statusMessage.emit("Clip window on.")
        elif kind == "stack":
            if obj is None:
                self.statusMessage.emit("Add a shape first, then stack transforms.")
                return
            self.scene.reset_selected()
            self.scene.apply_translate(2.0, 1.0)
            self.scene.apply_rotate(40.0)
            self._animate_last()
            self.statusMessage.emit("Stacked T then R.")
