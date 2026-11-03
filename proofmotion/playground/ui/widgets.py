"""Small shared controls for the playground inspector and toolbars."""

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QDoubleSpinBox, QSlider,
    QPushButton, QSizePolicy, QAbstractSpinBox,
)
from PyQt5.QtCore import Qt, pyqtSignal


def section_label(text: str) -> QLabel:
    lab = QLabel(text.upper())
    lab.setObjectName("PresetSectionTitle")
    return lab


def make_spin(minimum: float, maximum: float, value: float, step: float = 0.1,
              decimals: int = 2, suffix: str = "") -> QDoubleSpinBox:
    spin = QDoubleSpinBox()
    spin.setObjectName("ParamInput")
    spin.setRange(minimum, maximum)
    spin.setDecimals(decimals)
    spin.setSingleStep(step)
    spin.setValue(value)
    if suffix:
        spin.setSuffix(suffix)
    spin.setKeyboardTracking(False)
    spin.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
    spin.setMinimumHeight(30)
    spin.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    return spin


class AxisSliderRow(QWidget):
    """Label + slider + spinbox that stay in sync and emit a float."""
    valueChanged = pyqtSignal(float)

    def __init__(self, label: str, minimum: float, maximum: float, value: float,
                 step: float = 0.1, decimals: int = 2, suffix: str = "", parent=None):
        super().__init__(parent)
        self._scale = 10 ** decimals
        self._block = False

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        name = QLabel(label)
        name.setObjectName("ParamLabel")
        name.setFixedWidth(22)
        row.addWidget(name)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(int(minimum * self._scale), int(maximum * self._scale))
        self.slider.setValue(int(round(value * self._scale)))
        row.addWidget(self.slider, stretch=1)

        self.spin = make_spin(minimum, maximum, value, step, decimals, suffix)
        self.spin.setFixedWidth(92)
        row.addWidget(self.spin)

        self.slider.valueChanged.connect(self._from_slider)
        self.spin.valueChanged.connect(self._from_spin)

    def _from_slider(self, ival: int):
        if self._block:
            return
        self._block = True
        val = ival / self._scale
        self.spin.setValue(val)
        self._block = False
        self.valueChanged.emit(val)

    def _from_spin(self, val: float):
        if self._block:
            return
        self._block = True
        self.slider.setValue(int(round(val * self._scale)))
        self._block = False
        self.valueChanged.emit(val)

    def set_value(self, val: float):
        self._block = True
        self.spin.setValue(val)
        self.slider.setValue(int(round(val * self._scale)))
        self._block = False

    def value(self) -> float:
        return float(self.spin.value())


def tool_button(text: str, checkable: bool = False) -> QPushButton:
    btn = QPushButton(text)
    btn.setObjectName("ZoomButton")
    btn.setCursor(Qt.PointingHandCursor)
    btn.setCheckable(checkable)
    btn.setMinimumHeight(30)
    return btn


def primary_button(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setObjectName("ApplyButton")
    btn.setCursor(Qt.PointingHandCursor)
    return btn


def quiet_button(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setObjectName("ResetParamButton")
    btn.setCursor(Qt.PointingHandCursor)
    return btn
