"""
ui/view_controls.py
---------------------
Small toolbar of Zoom In / Zoom Out / Reset View / Pan controls that sits
above the visualization area. These are reserved integration points: the
buttons emit signals now, and once the OpenGL widget exists the
controller wires them straight into VisualizationWidget's
set_zoom/set_pan/reset_view methods.

Signals:
    zoomInClicked()
    zoomOutClicked()
    resetViewClicked()
    panRequested(float dx, float dy)
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox
from PyQt5.QtCore import Qt, pyqtSignal


class ViewControls(QWidget):
    zoomInClicked = pyqtSignal()
    zoomOutClicked = pyqtSignal()
    resetViewClicked = pyqtSignal()
    panRequested = pyqtSignal(float, float)
    gridToggled = pyqtSignal(bool)
    fullscreenToggled = pyqtSignal(bool)
    sortingStyleChanged = pyqtSignal(str)
    reducedMotionToggled = pyqtSignal(bool)

    PAN_STEP = 20.0

    def __init__(self, parent=None):
        super().__init__(parent)

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)

        # -------------------------------------------------------------
        # Sorting Accessibility Controls (visible for sorting topics)
        # -------------------------------------------------------------
        self._style_container = QWidget()
        style_layout = QHBoxLayout(self._style_container)
        style_layout.setContentsMargins(0, 0, 10, 0)
        style_layout.setSpacing(6)

        self._reduced_motion_btn = QPushButton("Reduced Motion")
        self._reduced_motion_btn.setObjectName("MotionToggle")
        self._reduced_motion_btn.setCheckable(True)
        self._reduced_motion_btn.setChecked(False)
        self._reduced_motion_btn.setMinimumWidth(110)
        self._reduced_motion_btn.setToolTip("Disable curved motion transitions for accessibility")
        self._reduced_motion_btn.setCursor(Qt.PointingHandCursor)
        self._reduced_motion_btn.toggled.connect(self.reducedMotionToggled.emit)
        style_layout.addWidget(self._reduced_motion_btn)

        row.addWidget(self._style_container)
        self._style_container.setVisible(False)

        label = QLabel("VIEW")
        label.setObjectName("SpeedLabel")
        row.addWidget(label)

        self._zoom_out_btn = self._make_btn("\u2212")
        self._zoom_out_btn.setToolTip("Zoom Out")
        self._zoom_out_btn.clicked.connect(self.zoomOutClicked.emit)
        row.addWidget(self._zoom_out_btn)

        self._zoom_in_btn = self._make_btn("+")
        self._zoom_in_btn.setToolTip("Zoom In")
        self._zoom_in_btn.clicked.connect(self.zoomInClicked.emit)
        row.addWidget(self._zoom_in_btn)

        self._pan_left_btn = self._make_btn("\u2190")
        self._pan_left_btn.setToolTip("Pan Left")
        self._pan_left_btn.clicked.connect(lambda: self.panRequested.emit(-self.PAN_STEP, 0))
        row.addWidget(self._pan_left_btn)

        self._pan_right_btn = self._make_btn("\u2192")
        self._pan_right_btn.setToolTip("Pan Right")
        self._pan_right_btn.clicked.connect(lambda: self.panRequested.emit(self.PAN_STEP, 0))
        row.addWidget(self._pan_right_btn)

        self._pan_up_btn = self._make_btn("\u2191")
        self._pan_up_btn.setToolTip("Pan Up")
        self._pan_up_btn.clicked.connect(lambda: self.panRequested.emit(0, -self.PAN_STEP))
        row.addWidget(self._pan_up_btn)

        self._pan_down_btn = self._make_btn("\u2193")
        self._pan_down_btn.setToolTip("Pan Down")
        self._pan_down_btn.clicked.connect(lambda: self.panRequested.emit(0, self.PAN_STEP))
        row.addWidget(self._pan_down_btn)

        self._grid_btn = QPushButton("⊞ Grid")
        self._grid_btn.setObjectName("GridButton")
        self._grid_btn.setCheckable(True)
        self._grid_btn.setChecked(True)
        self._grid_btn.setToolTip("Toggle Coordinate Grid")
        self._grid_btn.setCursor(Qt.PointingHandCursor)
        self._grid_btn.toggled.connect(self.gridToggled.emit)
        row.addWidget(self._grid_btn)

        self._reset_btn = self._make_btn("Reset")
        self._reset_btn.setMinimumWidth(58)
        self._reset_btn.setToolTip("Reset Camera View")
        self._reset_btn.clicked.connect(self.resetViewClicked.emit)
        row.addWidget(self._reset_btn)

        self._fullscreen_btn = QPushButton("⛶ Fullscreen")
        self._fullscreen_btn.setObjectName("FullscreenButton")
        self._fullscreen_btn.setCheckable(True)
        self._fullscreen_btn.setChecked(False)
        self._fullscreen_btn.setToolTip("Toggle Fullscreen / Focus Canvas (Esc to exit)")
        self._fullscreen_btn.setCursor(Qt.PointingHandCursor)
        self._fullscreen_btn.toggled.connect(self._on_fullscreen_toggled)
        row.addWidget(self._fullscreen_btn)

        row.addStretch(1)

    def _on_style_changed(self, index: int):
        pass

    def set_sorting_style(self, style: str):
        pass

    def set_zoom_controls_visible(self, visible: bool):
        self._zoom_out_btn.setVisible(visible)
        self._zoom_in_btn.setVisible(visible)

    def set_sorting_controls_visible(self, visible: bool):
        self._style_container.setVisible(visible)
        # In sorting mode, hide 2D pan arrows to give style selector generous breathing room
        for btn in (self._pan_left_btn, self._pan_right_btn, self._pan_up_btn, self._pan_down_btn):
            btn.setVisible(not visible)

    def _on_fullscreen_toggled(self, checked: bool):
        self._fullscreen_btn.setText("🗗 Exit Fullscreen" if checked else "⛶ Fullscreen")
        self.fullscreenToggled.emit(checked)

    def set_fullscreen_state(self, is_fullscreen: bool):
        self._fullscreen_btn.blockSignals(True)
        self._fullscreen_btn.setChecked(is_fullscreen)
        self._fullscreen_btn.setText("🗗 Exit Fullscreen" if is_fullscreen else "⛶ Fullscreen")
        self._fullscreen_btn.blockSignals(False)

    def _make_btn(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("ZoomButton")
        btn.setCursor(Qt.PointingHandCursor)
        return btn
