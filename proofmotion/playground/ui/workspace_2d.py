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
        self.canvas.setObjectName("StudioViewport")
        self.canvas.setAttribute(Qt.WA_StyledBackground, True)
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
        self._anim_all = False
        self._anim_op_index = 0

        self.scene.subscribe(self._refresh)
        self._wire()
        self._refresh()

    def _wire(self):
        self.rail.toolChosen.connect(self.canvas.set_tool)
        self.rail.deleteRequested.connect(self.scene.delete_selected)
        self.rail.clipToggled.connect(self.scene.set_clip_enabled)
        self.bar.rotateClicked.connect(lambda: self._nudge("rotate"))
        self.bar.scaleClicked.connect(lambda: self._nudge("scale"))
        self.bar.animateRequested.connect(self._animate_all)
        if hasattr(self.bar, "animateLastRequested"):
            self.bar.animateLastRequested.connect(self._animate_last)
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
            self.statusMessage.emit("Applied rotate.")
        else:
            from PyQt5.QtWidgets import QApplication
            about_origin = bool(QApplication.keyboardModifiers() & Qt.ShiftModifier)
            self.scene.apply_scale(1.4, 1.4, about_origin=about_origin)
            if about_origin:
                self.statusMessage.emit("Applied scale around origin (0, 0).")
            else:
                self.statusMessage.emit("Applied scale around shape centre.")
        self._animate_last()

    def _animate_all(self):
        """Play all transformations done to the selected shape from the beginning."""
        obj = self.scene.selected()
        if obj is None:
            self.statusMessage.emit("Select a shape first.")
            return
        if not obj.history:
            self.scene.apply_rotate(45.0)
        self._anim_all = True
        self._anim_op_index = 0
        self._anim_t = 0.0
        self.canvas.film_index = 0
        self.canvas.film_t = 0.0
        self.canvas.anim_t = 0.0
        self.filmstrip.set_playhead(0, 0.0)
        op_label = getattr(obj.history[0], "label", None) or getattr(obj.history[0], "kind", "op 1")
        self.statusMessage.emit(f"Playing all transformations (1 of {len(obj.history)}: {op_label})...")
        self._anim.start()
        self.canvas.update()

    def _animate_last(self):
        """Replay only the last transformation."""
        obj = self.scene.selected()
        if obj is None:
            self.statusMessage.emit("Select a shape first.")
            return
        if not obj.history:
            self.scene.apply_rotate(45.0)
        self._anim_all = False
        self._anim_op_index = len(obj.history) - 1
        self._anim_t = 0.0
        self.canvas.film_index = self._anim_op_index
        self.canvas.film_t = 0.0
        self.canvas.anim_t = 0.0
        self.filmstrip.set_playhead(self._anim_op_index, 0.0)
        self._anim.start()
        self.canvas.update()

    def _tick_anim(self):
        self._anim_t += 0.035
        obj = self.scene.selected()
        if obj is None or not obj.history:
            self._anim.stop()
            self._anim_all = False
            self.canvas.anim_t = None
            self.canvas.film_index = None
            self.canvas.update()
            return

        if self._anim_t >= 1.0:
            if getattr(self, "_anim_all", False) and (self._anim_op_index + 1 < len(obj.history)):
                self._anim_op_index += 1
                self._anim_t = 0.0
                self.canvas.film_index = self._anim_op_index
                self.canvas.film_t = 0.0
                self.canvas.anim_t = 0.0
                self.filmstrip.set_playhead(self._anim_op_index, 0.0)
                op = obj.history[self._anim_op_index]
                op_label = getattr(op, "label", None) or getattr(op, "kind", f"op {self._anim_op_index + 1}")
                self.statusMessage.emit(f"Playing transformation {self._anim_op_index + 1} of {len(obj.history)}: {op_label}")
                self.canvas.update()
                return
            else:
                self._anim.stop()
                self._anim_all = False
                self.canvas.anim_t = None
                self.canvas.film_index = None
                self.filmstrip.set_playhead(len(obj.history) - 1, 1.0)
                self.statusMessage.emit(f"Completed playing all {len(obj.history)} transformation(s).")
                self.canvas.update()
                return

        self.canvas.film_index = self._anim_op_index
        self.canvas.film_t = self._anim_t
        self.canvas.anim_t = self._anim_t
        self.filmstrip.set_playhead(self._anim_op_index, self._anim_t)
        self.canvas.update()

    def _on_film(self, op_index: int, t: float):
        self._anim.stop()
        self._anim_all = False
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
            self._animate_all()
            self.statusMessage.emit("Stacked T then R.")
