"""
playground/ui/playground_host.py
--------------------------------
Studio host: 2D / 3D / Living Basis / Homogeneous Lift / Pipeline Runway.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QLabel
from PyQt5.QtCore import Qt, pyqtSignal

from playground.ui.workspace_2d import Playground2DWorkspace

STUDIO_MODES = ("2d", "3d", "basis", "lift", "run")

_STATUS = {
    "2d": "Studio 2D — drag to move, scrub the filmstrip, Rotate / Scale to transform.",
    "3d": "Studio 3D — drag to orbit, scrub the filmstrip, Rotate / Scale to transform.",
    "basis": "Living Basis — drag î or ĵ. The grid is the matrix.",
    "lift": "Homogeneous Lift — 2D points rise onto the plane w = 1. Drag to orbit.",
    "run": "Pipeline Runway — Transform, clip, then rasterize one shape.",
}


class PlaygroundHost(QWidget):
    statusMessage = pyqtSignal(str)
    fullscreenToggled = pyqtSignal(bool)
    modeChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StudioHost")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._ws3d = None
        self._ws_basis = None
        self._ws_lift = None
        self._ws_run = None
        self._focus = False
        self._mode = "2d"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._hint = QLabel("Studio")
        self._hint.setObjectName("StudioHint")
        self._hint.hide()

        self.stack = QStackedWidget()
        self.ws2d = Playground2DWorkspace()
        self.stack.addWidget(self.ws2d)
        layout.addWidget(self.stack, stretch=1)

        self.ws2d.statusMessage.connect(self.statusMessage.emit)
        self.ws2d.fullscreenToggled.connect(self.fullscreenToggled.emit)
        self.ws2d.runwayRequested.connect(self._send_to_runway)

    def current_mode(self) -> str:
        return self._mode

    def open_mode(self, kind: str):
        kind = kind if kind in STUDIO_MODES else "2d"
        self._mode = kind
        widget = self._workspace(kind)
        self.stack.setCurrentWidget(widget)
        if self._focus:
            self.set_focus_mode(True)
        self.statusMessage.emit(_STATUS[kind])
        self.modeChanged.emit(kind)

    def apply_starter(self, kind: str):
        if self._mode == "2d":
            self.ws2d.apply_starter(kind)
        elif self._mode == "3d" and self._ws3d is not None:
            self._ws3d.apply_starter(kind)

    def _workspace(self, kind: str):
        if kind == "3d":
            self._ensure_3d()
            return self._ws3d
        if kind == "basis":
            self._ensure_basis()
            return self._ws_basis
        if kind == "lift":
            self._ensure_lift()
            return self._ws_lift
        if kind == "run":
            self._ensure_runway()
            return self._ws_run
        return self.ws2d

    def _ensure_3d(self):
        if self._ws3d is not None:
            return
        from playground.ui.workspace_3d import Playground3DWorkspace
        self._ws3d = Playground3DWorkspace()
        self.stack.addWidget(self._ws3d)
        self._ws3d.statusMessage.connect(self.statusMessage.emit)
        self._ws3d.fullscreenToggled.connect(self.fullscreenToggled.emit)

    def _ensure_basis(self):
        if self._ws_basis is not None:
            return
        from playground.ui.workspace_basis import LivingBasisWorkspace
        self._ws_basis = LivingBasisWorkspace()
        self.stack.addWidget(self._ws_basis)
        self._ws_basis.statusMessage.connect(self.statusMessage.emit)
        self._ws_basis.fullscreenToggled.connect(self.fullscreenToggled.emit)

    def _ensure_lift(self):
        if self._ws_lift is not None:
            return
        from playground.ui.workspace_lift import HomogeneousLiftWorkspace
        self._ws_lift = HomogeneousLiftWorkspace()
        self.stack.addWidget(self._ws_lift)
        self._ws_lift.statusMessage.connect(self.statusMessage.emit)
        self._ws_lift.fullscreenToggled.connect(self.fullscreenToggled.emit)

    def _ensure_runway(self):
        if self._ws_run is not None:
            return
        from playground.ui.workspace_runway import PipelineRunwayWorkspace
        self._ws_run = PipelineRunwayWorkspace()
        self.stack.addWidget(self._ws_run)
        self._ws_run.statusMessage.connect(self.statusMessage.emit)
        self._ws_run.fullscreenToggled.connect(self.fullscreenToggled.emit)

    def _send_to_runway(self, obj):
        self._ensure_runway()
        verts = obj.world_vertices() if hasattr(obj, "world_vertices") else []
        color = getattr(obj, "color", "#5EEAD4")
        self._ws_run.ingest(verts, color)
        self.open_mode("run")

    def show_chooser(self):
        self.open_mode("2d")

    def enter(self):
        self.open_mode(self._mode or "2d")

    def set_focus_mode(self, on: bool):
        self._focus = bool(on)
        current = self.stack.currentWidget()
        if hasattr(current, "set_focus_mode"):
            current.set_focus_mode(on)
        if hasattr(current, "set_fullscreen_button"):
            current.set_fullscreen_button(on)

    def is_3d_open(self) -> bool:
        return self._ws3d is not None and self.stack.currentWidget() is self._ws3d
