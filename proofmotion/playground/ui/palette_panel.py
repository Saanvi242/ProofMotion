"""Left palette: create tools, object list, clip window (2D)."""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QButtonGroup,
    QScrollArea, QFrame, QCheckBox, QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal

from playground.ui.widgets import section_label, make_spin, quiet_button


class PalettePanel(QWidget):
    toolChosen = pyqtSignal(str)
    create3dRequested = pyqtSignal(str)
    deleteRequested = pyqtSignal()
    objectChosen = pyqtSignal(str)
    clipToggled = pyqtSignal(bool)
    clipRectChanged = pyqtSignal(float, float, float, float)

    def __init__(self, mode: str = "2d", parent=None):
        super().__init__(parent)
        self.mode = mode
        self.setObjectName("StudioPanel")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumWidth(205)
        self.setMaximumWidth(280)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(10)

        title = QLabel("Objects" if mode == "2d" else "Primitives")
        title.setObjectName("PanelTitle")
        outer.addWidget(title)

        divider = QWidget()
        divider.setObjectName("PanelDivider")
        outer.addWidget(divider)

        if mode == "2d":
            self._build_2d_tools(outer)
        else:
            self._build_3d_tools(outer)

        outer.addWidget(section_label("Scene"))
        self._list_host = QWidget()
        self._list_layout = QVBoxLayout(self._list_host)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(6)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(self._list_host)
        outer.addWidget(scroll, stretch=1)

        self._item_buttons = {}
        self._item_group = QButtonGroup(self)
        self._item_group.setExclusive(True)

        self._delete_btn = quiet_button("Delete selected")
        self._delete_btn.clicked.connect(self.deleteRequested.emit)
        outer.addWidget(self._delete_btn)

        if mode == "2d":
            self._build_clip_controls(outer)

    def _build_2d_tools(self, outer):
        outer.addWidget(section_label("Tools"))
        tools = [
            ("select", "Select"),
            ("point", "Point"),
            ("line", "Line"),
            ("triangle", "Triangle"),
            ("rectangle", "Rectangle"),
            ("polygon", "Polygon"),
        ]
        self._tool_group = QButtonGroup(self)
        self._tool_group.setExclusive(True)
        wrap = QWidget()
        grid = QVBoxLayout(wrap)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(6)
        row = None
        for i, (key, label) in enumerate(tools):
            if i % 2 == 0:
                row = QHBoxLayout()
                row.setSpacing(6)
                grid.addLayout(row)
            btn = QPushButton(label)
            btn.setObjectName("PresetChip")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(30)
            btn.clicked.connect(lambda _=False, k=key: self.toolChosen.emit(k))
            self._tool_group.addButton(btn)
            row.addWidget(btn)
            if key == "select":
                btn.setChecked(True)
        outer.addWidget(wrap)

        hint = QLabel("Select to move objects. Other tools draw on the canvas.")
        hint.setObjectName("ParamHint")
        hint.setWordWrap(True)
        outer.addWidget(hint)

    def _build_3d_tools(self, outer):
        outer.addWidget(section_label("Add"))
        for key, label in (("cube", "Cube"), ("sphere", "Sphere"), ("pyramid", "Pyramid"), ("cylinder", "Cylinder")):
            btn = QPushButton(f"  {label}")
            btn.setObjectName("TheoremButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda _=False, k=key: self.create3dRequested.emit(k))
            outer.addWidget(btn)
        hint = QLabel("Click a primitive to add it. Click objects in the viewport to select them.")
        hint.setObjectName("ParamHint")
        hint.setWordWrap(True)
        outer.addWidget(hint)

    def _build_clip_controls(self, outer):
        outer.addWidget(section_label("Clipping"))
        self.clip_check = QCheckBox("Show clip window")
        self.clip_check.setCursor(Qt.PointingHandCursor)
        self.clip_check.toggled.connect(self.clipToggled.emit)
        outer.addWidget(self.clip_check)

        self._clip_spins = {}
        for key, label, val in (("xmin", "X min", -3.0), ("ymin", "Y min", -2.0),
                                ("xmax", "X max", 3.0), ("ymax", "Y max", 2.0)):
            row = QHBoxLayout()
            lab = QLabel(label)
            lab.setObjectName("ParamLabel")
            spin = make_spin(-20, 20, val, 0.5)
            spin.valueChanged.connect(self._emit_clip_rect)
            row.addWidget(lab)
            row.addWidget(spin)
            outer.addLayout(row)
            self._clip_spins[key] = spin

    def _emit_clip_rect(self, *_):
        xmin = self._clip_spins["xmin"].value()
        ymin = self._clip_spins["ymin"].value()
        xmax = self._clip_spins["xmax"].value()
        ymax = self._clip_spins["ymax"].value()
        if xmax > xmin and ymax > ymin:
            self.clipRectChanged.emit(xmin, ymin, xmax, ymax)

    def set_objects(self, items, selected_id=None):
        """items: list of (id, name)."""
        for btn in list(self._item_buttons.values()):
            self._item_group.removeButton(btn)
            self._list_layout.removeWidget(btn)
            btn.deleteLater()
        self._item_buttons.clear()
        for obj_id, name in items:
            btn = QPushButton(name)
            btn.setObjectName("TheoremButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(36)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.clicked.connect(lambda _=False, k=obj_id: self.objectChosen.emit(k))
            self._list_layout.addWidget(btn)
            self._item_buttons[obj_id] = btn
            self._item_group.addButton(btn)
            if obj_id == selected_id:
                btn.setChecked(True)
                btn.setProperty("selected", "true")
                btn.style().unpolish(btn)
                btn.style().polish(btn)

    def set_selected(self, object_id):
        for k, btn in self._item_buttons.items():
            on = k == object_id
            btn.setChecked(on)
            btn.setProperty("selected", "true" if on else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
