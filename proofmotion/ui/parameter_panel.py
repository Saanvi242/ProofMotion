from typing import Dict, List, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFrame, QScrollArea, QSizePolicy, QLayout, QSlider,
    QStackedWidget,
)
from PyQt5.QtGui import QRegExpValidator, QIntValidator
from PyQt5.QtCore import Qt, pyqtSignal, QRegExp, QPoint, QRect, QSize

from models.theorem_state import ParameterSpec, ParameterType
from ui.practical_learning_widget import PracticalLearningWidget


class FlowLayout(QLayout):
    
    def __init__(self, parent=None, margin=0, h_spacing=6, v_spacing=6):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self._h_spacing = h_spacing
        self._v_spacing = v_spacing
        self._item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._item_list.append(item)

    def horizontalSpacing(self):
        return self._h_spacing

    def verticalSpacing(self):
        return self._v_spacing

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0

        for item in self._item_list:
            space_x = self.horizontalSpacing()
            space_y = self.verticalSpacing()
            item_w = item.sizeHint().width()
            item_h = item.sizeHint().height()
            next_x = x + item_w + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item_w + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item_h)

        return y + line_height - rect.y()


PAIRS = {
    ("dx", "dy"), ("dy", "dx"),
    ("tx", "ty"), ("ty", "tx"),
    ("sx", "sy"), ("sy", "sx"),
    ("a", "b"), ("b", "a"),
    ("side_a", "side_b"), ("side_b", "side_a"),
    ("x0", "y0"), ("y0", "x0"),
    ("x1", "y1"), ("y1", "x1"),
    ("x2", "y2"), ("y2", "x2"),
    ("xmin", "ymin"), ("ymin", "xmin"),
    ("xmax", "ymax"), ("ymax", "xmax"),
    ("xw_min", "yw_min"), ("yw_min", "xw_min"),
    ("xw_max", "yw_max"), ("yw_max", "xw_max"),
    ("center_x", "center_y"), ("center_y", "center_x"),
    ("cx", "cy"), ("cy", "cx"),
    ("rx", "ry"), ("ry", "rx"),
    ("low_threshold", "high_threshold"),
    ("p0x", "p0y"), ("p0y", "p0x"),
    ("p1x", "p1y"), ("p1y", "p1x"),
    ("p2x", "p2y"), ("p2y", "p2x"),
    ("p3x", "p3y"), ("p3y", "p3x"),
    ("p4x", "p4y"), ("p4y", "p4x"),
    ("t0x", "t0y"), ("t0y", "t0x"),
    ("t1x", "t1y"), ("t1y", "t1x"),
}

TOPIC_PRESETS = {
    "pythagorean": [
        ("3, 4, 5 (Classic)", {"side_a": 3.0, "side_b": 4.0}),
        ("5, 12, 13 (Triple)", {"side_a": 5.0, "side_b": 12.0}),
        ("6, 8, 10 (Double)", {"side_a": 6.0, "side_b": 8.0}),
        ("7, 7 (Isosceles)", {"side_a": 7.0, "side_b": 7.0}),
        ("8, 15, 17 (Large)", {"side_a": 8.0, "side_b": 15.0}),
    ],
    "circle_area": [
        ("r = 3.0 cm (Small)", {"radius": 3.0}),
        ("r = 5.0 cm (Standard)", {"radius": 5.0}),
        ("r = 7.5 cm (Medium)", {"radius": 7.5}),
        ("r = 10.0 cm (Large)", {"radius": 10.0}),
    ],
    "circle_geometry": [
        ("r = 3.0 cm (Small)", {"radius": 3.0}),
        ("r = 5.0 cm (Standard)", {"radius": 5.0}),
        ("r = 7.5 cm (Medium)", {"radius": 7.5}),
        ("r = 10.0 cm (Large)", {"radius": 10.0}),
    ],
    "similar_triangles": [
        ("k = 0.5× (Half)", {"side_a": 6.0, "side_b": 8.0, "ratio": 0.5}),
        ("k = 1.5× (Standard)", {"side_a": 6.0, "side_b": 8.0, "ratio": 1.5}),
        ("k = 2.0× (Area ×4)", {"side_a": 6.0, "side_b": 8.0, "ratio": 2.0}),
        ("k = 3.0× (Area ×9)", {"side_a": 4.0, "side_b": 5.0, "ratio": 3.0}),
    ],
    "law_of_cosines": [
        ("Acute (60°)", {"side_a": 7.0, "side_b": 5.0, "angle_c": 60.0}),
        ("Right (90°)", {"side_a": 6.0, "side_b": 8.0, "angle_c": 90.0}),
        ("Obtuse (120°)", {"side_a": 5.0, "side_b": 6.0, "angle_c": 120.0}),
        ("Equilateral", {"side_a": 6.0, "side_b": 6.0, "angle_c": 60.0}),
    ],
    "trans_translation": [
        ("Shift (3, 2)", {"dx": 3.0, "dy": 2.0}),
        ("Shift (5, 0)", {"dx": 5.0, "dy": 0.0}),
        ("Shift (0, -4)", {"dx": 0.0, "dy": -4.0}),
        ("Shift (-4, 3)", {"dx": -4.0, "dy": 3.0}),
    ],
    "trans_scaling": [
        ("0.5× (Shrink)", {"sx": 0.5, "sy": 0.5}),
        ("1.5× (Enlarge)", {"sx": 1.5, "sy": 1.5}),
        ("2.0× (Double)", {"sx": 2.0, "sy": 2.0}),
        ("Stretch X (2.0, 0.8)", {"sx": 2.0, "sy": 0.8}),
    ],
    "trans_rotation": [
        ("45° Diagonal", {"angle": 45.0}),
        ("90° Quarter Turn", {"angle": 90.0}),
        ("180° Half Turn", {"angle": 180.0}),
        ("-45° Clockwise", {"angle": -45.0}),
    ],
    "trans_reflection": [
        ("X-Axis", {"axis": "X-axis"}),
        ("Y-Axis", {"axis": "Y-axis"}),
        ("Origin", {"axis": "Origin"}),
        ("Line y = x", {"axis": "y = x"}),
    ],
    "trans_composite": [
        ("Scale → Rotate → Shift", {"sx": 1.3, "angle": 30.0, "dx": 3.0, "dy": 2.0}),
        ("Rotate 45° + Shift (4, 4)", {"sx": 1.0, "angle": 45.0, "dx": 4.0, "dy": 4.0}),
        ("Double + 90° Turn", {"sx": 2.0, "angle": 90.0, "dx": 2.0, "dy": 1.0}),
    ],
    "rast_dda": [
        ("Gentle Slope (m < 1)", {"x0": 2, "y0": 3, "x1": 18, "y1": 9}),
        ("Steep Slope (m > 1)", {"x0": 3, "y0": 2, "x1": 8, "y1": 18}),
        ("Diagonal (m = 1)", {"x0": 2, "y0": 2, "x1": 16, "y1": 16}),
        ("Horizontal (m = 0)", {"x0": 2, "y0": 10, "x1": 18, "y1": 10}),
    ],
    "rast_bresenham": [
        ("Octant 1 (0 < m < 1)", {"x0": 2, "y0": 2, "x1": 18, "y1": 8}),
        ("Octant 2 (m > 1)", {"x0": 2, "y0": 2, "x1": 8, "y1": 18}),
        ("Negative Slope", {"x0": 2, "y0": 18, "x1": 18, "y1": 4}),
        ("Steep Negative", {"x0": 2, "y0": 18, "x1": 6, "y1": 2}),
    ],
    "rast_circle": [
        ("Small Circle (r=5)", {"center_x": 10, "center_y": 10, "radius": 5}),
        ("Medium Circle (r=8)", {"center_x": 10, "center_y": 10, "radius": 8}),
        ("Large Circle (r=11)", {"center_x": 10, "center_y": 10, "radius": 11}),
    ],
    "rast_midpoint_circle": [
        ("Small Circle (r=5)", {"center_x": 10, "center_y": 10, "radius": 5}),
        ("Medium Circle (r=8)", {"center_x": 10, "center_y": 10, "radius": 8}),
        ("Large Circle (r=11)", {"center_x": 10, "center_y": 10, "radius": 11}),
    ],
    "clip_cohen_sutherland": [
        ("Fully inside", {"x1": -1.5, "y1": -1.0, "x2": 2.0, "y2": 1.2, "xmin": -3.0, "ymin": -2.0, "xmax": 3.0, "ymax": 2.0}),
        ("Fully outside", {"x1": 4.5, "y1": 0.5, "x2": 7.0, "y2": 1.8, "xmin": -3.0, "ymin": -2.0, "xmax": 3.0, "ymax": 2.0}),
        ("Crosses the window", {"x1": -5.0, "y1": -3.5, "x2": 5.0, "y2": 3.5, "xmin": -3.0, "ymin": -2.0, "xmax": 3.0, "ymax": 2.0}),
        ("One end outside", {"x1": -5.5, "y1": 1.0, "x2": 1.5, "y2": -0.5, "xmin": -3.0, "ymin": -2.0, "xmax": 3.0, "ymax": 2.0}),
        ("Clips the top", {"x1": -1.0, "y1": -0.5, "x2": 2.0, "y2": 4.0, "xmin": -3.0, "ymin": -2.0, "xmax": 3.0, "ymax": 2.0}),
        ("Vertical line", {"x1": 1.0, "y1": -4.5, "x2": 1.0, "y2": 4.5, "xmin": -3.0, "ymin": -2.0, "xmax": 3.0, "ymax": 2.0}),
        ("Horizontal line", {"x1": -5.5, "y1": 0.5, "x2": 5.5, "y2": 0.5, "xmin": -3.0, "ymin": -2.0, "xmax": 3.0, "ymax": 2.0}),
        ("Hits a corner", {"x1": -6.0, "y1": 5.0, "x2": 0.0, "y2": -1.0, "xmin": -3.0, "ymin": -2.0, "xmax": 3.0, "ymax": 2.0}),
        ("On the left edge", {"x1": -3.0, "y1": -1.5, "x2": -3.0, "y2": 1.5, "xmin": -3.0, "ymin": -2.0, "xmax": 3.0, "ymax": 2.0}),
        ("Outside, parallel", {"x1": -5.0, "y1": -3.5, "x2": -5.0, "y2": 3.5, "xmin": -3.0, "ymin": -2.0, "xmax": 3.0, "ymax": 2.0}),
    ],
    "clip_sutherland_hodgman": [
        ("Crossing triangle", {"polygon_shape": "Crossing triangle", "xmin": -3.0, "ymin": -2.0, "xmax": 3.0, "ymax": 2.0}),
        ("Diamond", {"polygon_shape": "Diamond", "xmin": -3.0, "ymin": -2.0, "xmax": 3.0, "ymax": 2.0}),
        ("Hexagon", {"polygon_shape": "Hexagon", "xmin": -3.0, "ymin": -2.0, "xmax": 3.0, "ymax": 2.0}),
        ("Star", {"polygon_shape": "Star", "xmin": -3.0, "ymin": -2.0, "xmax": 3.0, "ymax": 2.0}),
        ("Fully inside", {"polygon_shape": "Fully inside", "xmin": -3.0, "ymin": -2.0, "xmax": 3.0, "ymax": 2.0}),
        ("Fully outside", {"polygon_shape": "Fully outside", "xmin": -3.0, "ymin": -2.0, "xmax": 3.0, "ymax": 2.0}),
    ],
    "linear_search": [
        ("Target in Middle (42)", {"array_input": "15, 23, 8, 42, 16, 4, 30, 19", "target": 42}),
        ("Target at Start (15)", {"array_input": "15, 23, 8, 42, 16, 4, 30, 19", "target": 15}),
        ("Target at End (19)", {"array_input": "15, 23, 8, 42, 16, 4, 30, 19", "target": 19}),
        ("Target Not Found (99)", {"array_input": "15, 23, 8, 42, 16, 4, 30, 19", "target": 99}),
    ],
    "binary_search": [
        ("Target in Mid (23)", {"array_input": "4, 8, 15, 16, 23, 30, 42, 55, 68", "target": 23}),
        ("Target Low Half (8)", {"array_input": "4, 8, 15, 16, 23, 30, 42, 55, 68", "target": 8}),
        ("Target High Half (55)", {"array_input": "4, 8, 15, 16, 23, 30, 42, 55, 68", "target": 55}),
        ("Target Absent (50)", {"array_input": "4, 8, 15, 16, 23, 30, 42, 55, 68", "target": 50}),
    ],
    "bubble_sort": [
        ("Random Array", {"array_input": "24, 13, 9, 45, 18, 32, 5, 29"}),
        ("Reverse Sorted", {"array_input": "50, 40, 30, 20, 10, 5"}),
        ("Nearly Sorted", {"array_input": "5, 10, 15, 25, 20, 30, 35"}),
    ],
    "selection_sort": [
        ("Random Array", {"array_input": "29, 10, 14, 37, 13, 2, 40, 25"}),
        ("Reverse Sorted", {"array_input": "45, 38, 29, 21, 15, 8"}),
        ("Nearly Sorted", {"array_input": "8, 12, 15, 22, 20, 29, 35"}),
    ],
    "insertion_sort": [
        ("Random Array", {"array_input": "31, 41, 59, 26, 41, 58, 12, 35"}),
        ("Reverse Sorted", {"array_input": "50, 42, 35, 26, 18, 12"}),
        ("Nearly Sorted", {"array_input": "10, 12, 18, 15, 22, 28"}),
    ],
    "merge_sort": [
        ("Random Array", {"array_input": "38, 27, 43, 3, 9, 82, 10, 19"}),
        ("Reverse Sorted", {"array_input": "64, 52, 41, 33, 25, 14"}),
        ("Nearly Sorted", {"array_input": "5, 9, 14, 25, 20, 31, 40"}),
    ],
    "quick_sort": [
        ("Random Array", {"array_input": "10, 80, 30, 90, 40, 50, 70, 20"}),
        ("Reverse Sorted", {"array_input": "70, 60, 50, 40, 30, 20, 10"}),
        ("Nearly Sorted", {"array_input": "10, 20, 35, 30, 45, 50, 60"}),
    ],
    "compare_sorting": [
        ("Quick vs Bubble", {"algo_1": "Bubble Sort", "algo_2": "Quick Sort", "array_input": "34, 12, 89, 5, 23, 77, 45, 18, 62, 9"}),
        ("Merge vs Quick", {"algo_1": "Merge Sort", "algo_2": "Quick Sort", "array_input": "45, 12, 85, 32, 89, 39, 69, 44, 42, 1, 68, 53"}),
        ("Insertion vs Bubble", {"algo_1": "Bubble Sort", "algo_2": "Insertion Sort", "array_input": "28, 14, 9, 42, 18, 35, 6, 21"}),
        ("Reversed Array", {"algo_1": "Bubble Sort", "algo_2": "Quick Sort", "array_input": "60, 50, 40, 30, 20, 10"}),
        ("Nearly Sorted", {"algo_1": "Insertion Sort", "algo_2": "Selection Sort", "array_input": "5, 10, 15, 25, 20, 30, 35, 40"}),
    ],
    "compare_searching": [
        ("Middle Target (23)", {"array_input": "4, 8, 15, 16, 23, 30, 42, 55, 68", "target": 23}),
        ("End Target (68)", {"array_input": "4, 8, 15, 16, 23, 30, 42, 55, 68", "target": 68}),
        ("First Item (4)", {"array_input": "4, 8, 15, 16, 23, 30, 42, 55, 68", "target": 4}),
        ("Not in Array (99)", {"array_input": "4, 8, 15, 16, 23, 30, 42, 55, 68", "target": 99}),
    ],
    "proj_cube_persp": [
        ("Default Perspective", {"rx": 25.0, "ry": 35.0, "rz": 0.0, "tx": 0.0, "ty": 0.0, "tz": 0.0, "sx": 1.0, "sy": 1.0, "sz": 1.0, "camera_dist": 7.0, "focal_dist": 4.5}),
        ("Top-Down View", {"rx": 65.0, "ry": 20.0, "rz": 0.0, "tx": 0.0, "ty": 0.0, "tz": 0.0, "sx": 1.0, "sy": 1.0, "sz": 1.0, "camera_dist": 8.0, "focal_dist": 4.5}),
        ("Translated & Scaled", {"rx": 15.0, "ry": 30.0, "rz": 10.0, "tx": 1.5, "ty": 0.5, "tz": -0.5, "sx": 1.4, "sy": 0.8, "sz": 1.2, "camera_dist": 7.5, "focal_dist": 4.5}),
        ("Close Dramatic Zoom", {"rx": 20.0, "ry": 45.0, "rz": 0.0, "tx": 0.0, "ty": 0.0, "tz": 0.0, "sx": 1.0, "sy": 1.0, "sz": 1.0, "camera_dist": 4.5, "focal_dist": 5.0}),
    ],
    "proj_cube_ortho": [
        ("Standard Isometric", {"rx": 30.0, "ry": 45.0, "rz": 0.0, "tx": 0.0, "ty": 0.0, "tz": 0.0, "sx": 1.0, "sy": 1.0, "sz": 1.0}),
        ("Front View (XZ)", {"rx": 0.0, "ry": 0.0, "rz": 0.0, "tx": 0.0, "ty": 0.0, "tz": 0.0, "sx": 1.0, "sy": 1.0, "sz": 1.0}),
        ("Top Elevation", {"rx": 90.0, "ry": 0.0, "rz": 0.0, "tx": 0.0, "ty": 0.0, "tz": 0.0, "sx": 1.0, "sy": 1.0, "sz": 1.0}),
        ("Side Elevation", {"rx": 0.0, "ry": 90.0, "rz": 0.0, "tx": 0.0, "ty": 0.0, "tz": 0.0, "sx": 1.0, "sy": 1.0, "sz": 1.0}),
    ],
    "proj_pyramid": [
        ("Standard Pyramid", {"rx": 20.0, "ry": 40.0, "rz": 0.0, "tx": 0.0, "ty": 0.0, "tz": 0.0, "sx": 1.0, "sy": 1.0, "sz": 1.0, "camera_dist": 7.0, "focal_dist": 4.5}),
        ("Bird's Eye Apex", {"rx": 70.0, "ry": 45.0, "rz": 0.0, "tx": 0.0, "ty": 0.0, "tz": 0.0, "sx": 1.0, "sy": 1.0, "sz": 1.0, "camera_dist": 8.0, "focal_dist": 4.5}),
        ("Elongated Spire", {"rx": 20.0, "ry": 35.0, "rz": 0.0, "tx": 0.0, "ty": -0.5, "tz": 0.0, "sx": 1.0, "sy": 2.0, "sz": 1.0, "camera_dist": 8.5, "focal_dist": 4.5}),
    ],
    "curve_bezier": [
        ("Classic S-curve (Bresenham)", {"p0x": -5.0, "p0y": -2.0, "p1x": -1.5, "p1y": 4.0, "p2x": 1.5, "p2y": -4.0, "p3x": 5.0, "p3y": 2.0, "subdivisions": 2, "raster_algorithm": "Bresenham"}),
        ("Classic S-curve (DDA)", {"p0x": -5.0, "p0y": -2.0, "p1x": -1.5, "p1y": 4.0, "p2x": 1.5, "p2y": -4.0, "p3x": 5.0, "p3y": 2.0, "subdivisions": 2, "raster_algorithm": "DDA"}),
        ("Symmetric Arch (Depth 3)", {"p0x": -5.0, "p0y": -2.0, "p1x": -2.0, "p1y": 4.5, "p2x": 2.0, "p2y": 4.5, "p3x": 5.0, "p3y": -2.0, "subdivisions": 3, "raster_algorithm": "Bresenham"}),
        ("Almost Linear (DDA)", {"p0x": -5.0, "p0y": -1.0, "p1x": -1.5, "p1y": -0.2, "p2x": 1.5, "p2y": 0.2, "p3x": 5.0, "p3y": 1.0, "subdivisions": 2, "raster_algorithm": "DDA"}),
        ("Loop (Depth 3)", {"p0x": -4.0, "p0y": 0.0, "p1x": 5.0, "p1y": 5.0, "p2x": 5.0, "p2y": -5.0, "p3x": -4.0, "p3y": 0.5, "subdivisions": 3, "raster_algorithm": "Bresenham"}),
    ],
}


class ParameterPanel(QWidget):
    parametersApplied = pyqtSignal(dict)  # key -> value (float, int, str)
    sortingStyleRequested = pyqtSignal(str) # "balls", "cubes", "marbles", "bars"
    curveTChanged = pyqtSignal(float)

    exploreApplicationsRequested = pyqtSignal(str)
    testUnderstandingRequested = pyqtSignal(str)
    exportPdfRequested = pyqtSignal()
    tabChanged = pyqtSignal(int)
    compareRequested = pyqtSignal(str)
    compareWithRequested = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ParamPanel")
        self.setMinimumWidth(300)
        self._specs: List[ParameterSpec] = []
        self._inputs: Dict[str, Any] = {}
        self._preset_chips: List[QPushButton] = []
        self._preset_section = None
        self._field_cols: Dict[str, QWidget] = {}
        self._active_theorem = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(10)

        # Header Segmented Tab Bar: [ Explore Parameters ]  [ Lesson Resources ]
        self._tab_bar_frame = QFrame()
        self._tab_bar_frame.setObjectName("ParamTabBar")
        self._tab_bar_frame.setStyleSheet("""
            QFrame#ParamTabBar {
                background-color: #F1F5F9;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 2px;
            }
        """)
        tab_layout = QHBoxLayout(self._tab_bar_frame)
        tab_layout.setContentsMargins(2, 2, 2, 2)
        tab_layout.setSpacing(4)

        self._tab_params_btn = QPushButton("Explore Parameters")
        self._tab_params_btn.setObjectName("TabParamsBtn")
        self._tab_params_btn.setCursor(Qt.PointingHandCursor)
        self._tab_params_btn.setFixedHeight(30)
        self._tab_params_btn.setToolTip("Explore Parameters")
        self._tab_params_btn.clicked.connect(lambda: self.set_tab(0))

        self._tab_resources_btn = QPushButton("Lesson Resources")
        self._tab_resources_btn.setObjectName("TabResourcesBtn")
        self._tab_resources_btn.setCursor(Qt.PointingHandCursor)
        self._tab_resources_btn.setFixedHeight(30)
        self._tab_resources_btn.setToolTip("Lesson Resources")
        self._tab_resources_btn.clicked.connect(lambda: self.set_tab(1))

        tab_layout.addWidget(self._tab_params_btn)
        tab_layout.addWidget(self._tab_resources_btn)
        outer.addWidget(self._tab_bar_frame)

        divider = QWidget()
        divider.setObjectName("PanelDivider")
        outer.addWidget(divider)

        # Main stacked container holding Explore Parameters (0) and Lesson Resources (1)
        self._tab_stack = QStackedWidget()

        # Page 0: Explore Parameters
        self._scroll = QScrollArea()
        self._scroll.setObjectName("ParamScrollArea")
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet(
            "QScrollArea#ParamScrollArea { background: transparent; border: none; } "
            "QScrollArea#ParamScrollArea > QWidget > QWidget { background: transparent; }"
        )

        self._fields_container = QWidget()
        self._fields_layout = QVBoxLayout(self._fields_container)
        self._fields_layout.setContentsMargins(0, 0, 0, 0)
        self._fields_layout.setSpacing(12)

        # 1. Parameter inputs and presets container
        self._params_widget = QWidget()
        self._params_layout = QVBoxLayout(self._params_widget)
        self._params_layout.setContentsMargins(0, 0, 0, 0)
        self._params_layout.setSpacing(12)
        self._fields_layout.addWidget(self._params_widget)

        # 2. Action area (Directly below controls with subtle divider and reasonable gap)
        self._action_widget = QWidget()
        action_layout = QVBoxLayout(self._action_widget)
        action_layout.setContentsMargins(0, 6, 0, 0)
        action_layout.setSpacing(8)

        self._action_divider = QFrame()
        self._action_divider.setFrameShape(QFrame.HLine)
        self._action_divider.setStyleSheet("background-color: #EDF2F7; max-height: 1px; border: none;")
        action_layout.addWidget(self._action_divider)

        # Validation error banner
        self._error_label = QLabel("")
        self._error_label.setObjectName("ParamError")
        self._error_label.setWordWrap(True)
        self._error_label.hide()
        action_layout.addWidget(self._error_label)

        # Action Buttons: Apply (Primary) & Reset (Secondary Outlined)
        self._apply_btn = QPushButton("Apply Parameters")
        self._apply_btn.setObjectName("ApplyButton")
        self._apply_btn.setCursor(Qt.PointingHandCursor)
        self._apply_btn.setFixedHeight(36)
        self._apply_btn.clicked.connect(self._on_apply_clicked)
        action_layout.addWidget(self._apply_btn)

        self._reset_btn = QPushButton("Reset Defaults")
        self._reset_btn.setObjectName("ResetParamButton")
        self._reset_btn.setCursor(Qt.PointingHandCursor)
        self._reset_btn.setFixedHeight(36)
        self._reset_btn.clicked.connect(self._on_reset_clicked)
        action_layout.addWidget(self._reset_btn)

        self._fields_layout.addWidget(self._action_widget)
        self._fields_layout.addStretch(1)
        self._scroll.setWidget(self._fields_container)

        self._params_page = QWidget()
        params_page_layout = QVBoxLayout(self._params_page)
        params_page_layout.setContentsMargins(0, 0, 0, 0)
        params_page_layout.addWidget(self._scroll)

        # Page 1: Lesson Resources (Real-World Applications & Test Your Understanding)
        self._resources_page = self._build_resources_page()

        self._tab_stack.addWidget(self._params_page)
        self._tab_stack.addWidget(self._resources_page)
        outer.addWidget(self._tab_stack, stretch=1)

        self.set_tab(0)

        # Retain practical_widget reference for backwards compatibility
        self.practical_widget = PracticalLearningWidget()

        self._set_empty_state()

    def _build_resources_page(self) -> QWidget:
        page = QWidget()
        pv = QVBoxLayout(page)
        pv.setContentsMargins(0, 0, 0, 0)
        pv.setSpacing(10)

        scroll = QScrollArea()
        scroll.setObjectName("ResourcesScrollArea")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        cv = QVBoxLayout(container)
        cv.setContentsMargins(2, 4, 2, 4)
        cv.setSpacing(12)

        # Card 1: Real-World Applications
        app_card = QFrame()
        app_card.setObjectName("ExploreAppsBanner")
        self._apps_banner = app_card  # Backwards compatibility
        app_card.setStyleSheet("""
            QFrame#ExploreAppsBanner {
                background-color: #FFFFFF;
                border: 1.5px solid #E8ECF5;
                border-radius: 12px;
            }
        """)
        av = QVBoxLayout(app_card)
        av.setContentsMargins(14, 14, 14, 14)
        av.setSpacing(8)

        b1 = QLabel("ENGINEERING & SYSTEMS")
        b1.setStyleSheet("""
            background-color: #EDE9FE;
            color: #6C5CE7;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
            font-size: 9.5px;
            font-weight: 700;
            letter-spacing: 0.6px;
            padding: 2px 6px;
            border-radius: 4px;
        """)
        av.addWidget(b1, alignment=Qt.AlignLeft)

        t1 = QLabel("Real-World Applications")
        t1.setStyleSheet("""
            color: #0F172A;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
            font-size: 13.5px;
            font-weight: 600;
        """)
        av.addWidget(t1)

        d1 = QLabel(
            "Explore production software architectures, graphics engines, and physical engineering systems "
            "where this algorithm or mathematical theorem is actively applied."
        )
        d1.setWordWrap(True)
        d1.setStyleSheet("""
            color: #64748B;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
            font-size: 11.5px;
            line-height: 1.4;
        """)
        av.addWidget(d1)

        self._explore_apps_btn = QPushButton("Explore Applications →")
        self._explore_apps_btn.setObjectName("ExploreAppsButton")
        self._explore_apps_btn.setCursor(Qt.PointingHandCursor)
        self._explore_apps_btn.setFixedHeight(34)
        self._explore_apps_btn.setStyleSheet("""
            QPushButton#ExploreAppsButton {
                background-color: #6C5CE7;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton#ExploreAppsButton:hover {
                background-color: #5B4BD5;
            }
        """)
        self._explore_apps_btn.clicked.connect(self._on_explore_apps_clicked)
        av.addWidget(self._explore_apps_btn)
        cv.addWidget(app_card)

        # Card 2: Test Your Understanding
        quiz_card = QFrame()
        quiz_card.setObjectName("QuizResourceCard")
        quiz_card.setStyleSheet("""
            QFrame#QuizResourceCard {
                background-color: #FFFFFF;
                border: 1.5px solid #E8ECF5;
                border-radius: 12px;
            }
        """)
        qv = QVBoxLayout(quiz_card)
        qv.setContentsMargins(14, 14, 14, 14)
        qv.setSpacing(8)

        b2 = QLabel("KNOWLEDGE CHECK")
        b2.setStyleSheet("""
            background-color: #DCFCE7;
            color: #15803D;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
            font-size: 9.5px;
            font-weight: 700;
            letter-spacing: 0.6px;
            padding: 2px 6px;
            border-radius: 4px;
        """)
        qv.addWidget(b2, alignment=Qt.AlignLeft)

        t2 = QLabel("Test Your Understanding")
        t2.setStyleSheet("""
            color: #0F172A;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
            font-size: 13.5px;
            font-weight: 600;
        """)
        qv.addWidget(t2)

        d2 = QLabel(
            "Challenge yourself with topic-specific multiple-choice questions, "
            "instant answer validation, and detailed explanations."
        )
        d2.setWordWrap(True)
        d2.setStyleSheet("""
            color: #64748B;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
            font-size: 11.5px;
            line-height: 1.4;
        """)
        qv.addWidget(d2)

        self._quiz_link_btn = QPushButton("Test Your Understanding →")
        self._quiz_link_btn.setObjectName("QuizLinkButton")
        self._quiz_link_btn.setCursor(Qt.PointingHandCursor)
        self._quiz_link_btn.setFixedHeight(34)
        self._quiz_link_btn.setStyleSheet("""
            QPushButton#QuizLinkButton {
                background-color: #FFFFFF;
                color: #059669;
                border: 1.5px solid #A7F3D0;
                border-radius: 6px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton#QuizLinkButton:hover {
                background-color: #ECFDF5;
                border-color: #059669;
            }
        """)
        self._quiz_link_btn.clicked.connect(self._on_quiz_link_clicked)
        qv.addWidget(self._quiz_link_btn)
        cv.addWidget(quiz_card)

        # Card 3: Study Notes & PDF Export
        pdf_card = QFrame()
        pdf_card.setObjectName("PdfResourceCard")
        pdf_card.setStyleSheet("""
            QFrame#PdfResourceCard {
                background-color: #FFFFFF;
                border: 1.5px solid #E8ECF5;
                border-radius: 12px;
            }
        """)
        pv_c = QVBoxLayout(pdf_card)
        pv_c.setContentsMargins(14, 14, 14, 14)
        pv_c.setSpacing(8)

        b3 = QLabel("OFFLINE STUDY GUIDE")
        b3.setStyleSheet("""
            background-color: #FEF3C7;
            color: #92400E;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
            font-size: 9.5px;
            font-weight: 700;
            letter-spacing: 0.6px;
            padding: 2px 6px;
            border-radius: 4px;
        """)
        pv_c.addWidget(b3, alignment=Qt.AlignLeft)

        t3 = QLabel("Export Lesson as PDF")
        t3.setStyleSheet("""
            color: #0F172A;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
            font-size: 13.5px;
            font-weight: 600;
        """)
        pv_c.addWidget(t3)

        d3 = QLabel(
            "Export this complete step-by-step lesson with mathematical formulas, "
            "active parameters, and visual snapshots into an offline PDF document."
        )
        d3.setWordWrap(True)
        d3.setStyleSheet("""
            color: #64748B;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
            font-size: 11.5px;
            line-height: 1.4;
        """)
        pv_c.addWidget(d3)

        self._export_pdf_btn = QPushButton("Export PDF Document")
        self._export_pdf_btn.setObjectName("ExportPdfResourceBtn")
        self._export_pdf_btn.setCursor(Qt.PointingHandCursor)
        self._export_pdf_btn.setFixedHeight(34)
        self._export_pdf_btn.setStyleSheet("""
            QPushButton#ExportPdfResourceBtn {
                background-color: #FFFFFF;
                color: #6C5CE7;
                border: 1.5px solid #D8D1FF;
                border-radius: 6px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton#ExportPdfResourceBtn:hover {
                background-color: #FAF5FF;
                border-color: #6C5CE7;
            }
        """)
        self._export_pdf_btn.clicked.connect(self.exportPdfRequested.emit)
        pv_c.addWidget(self._export_pdf_btn)
        cv.addWidget(pdf_card)

        cv.addStretch(1)
        scroll.setWidget(container)
        pv.addWidget(scroll)
        return page

    def set_tab(self, index: int):
        index = max(0, min(index, 1))
        self._tab_stack.setCurrentIndex(index)
        self._update_tab_button_styles()
        self.tabChanged.emit(index)

    def current_tab(self) -> int:
        return self._tab_stack.currentIndex()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_tab_labels()

    def showEvent(self, event):
        super().showEvent(event)
        self._update_tab_labels()

    def _update_tab_labels(self):
        available = self._tab_bar_frame.width()
        if available > 0 and available < 265:
            self._tab_params_btn.setText("Parameters")
            self._tab_resources_btn.setText("Resources")
        else:
            self._tab_params_btn.setText("Explore Parameters")
            self._tab_resources_btn.setText("Lesson Resources")

    def _update_tab_button_styles(self):
        active_idx = self._tab_stack.currentIndex()
        active_style = """
            QPushButton {
                background-color: #FFFFFF;
                color: #6C5CE7;
                border: 1px solid #D8D1FF;
                border-radius: 6px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
                font-size: 11px;
                font-weight: 600;
                padding: 3px 4px;
            }
        """
        inactive_style = """
            QPushButton {
                background: transparent;
                color: #64748B;
                border: 1px solid transparent;
                border-radius: 6px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
                font-size: 11px;
                font-weight: 500;
                padding: 3px 4px;
            }
            QPushButton:hover {
                background-color: #EDE9FE;
                color: #5B21B6;
            }
        """
        self._tab_params_btn.setStyleSheet(active_style if active_idx == 0 else inactive_style)
        self._tab_resources_btn.setStyleSheet(active_style if active_idx == 1 else inactive_style)

    def _on_explore_apps_clicked(self):
        topic_key = getattr(self._active_theorem, "key", "")
        self.exploreApplicationsRequested.emit(topic_key)

    def _on_quiz_link_clicked(self):
        topic_key = getattr(self._active_theorem, "key", "")
        self.testUnderstandingRequested.emit(topic_key)

    def show_applications(self):
        """Open the wide dedicated Real-World Applications view."""
        topic_key = getattr(self._active_theorem, "key", "")
        if hasattr(self, "practical_widget"):
            self.practical_widget.set_topic(topic_key)
        self.exploreApplicationsRequested.emit(topic_key)

    def show_quiz(self):
        """Open the dedicated Knowledge Check view."""
        topic_key = getattr(self._active_theorem, "key", "")
        self.testUnderstandingRequested.emit(topic_key)

    def show_parameters(self):
        """Switch to the Explore Parameters tab."""
        self.set_tab(0)

    def show_resources(self):
        """Switch to the Lesson Resources tab."""
        self.set_tab(1)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def set_theorem(self, theorem):
        """Rebuild input fields and presets for the given Theorem/Topic."""
        self._clear_fields()
        self._active_theorem = theorem
        self._specs = getattr(theorem, "parameters", [])
        self._inputs = {}
        self._preset_chips = []
        self._preset_section = None
        self._field_cols = {}

        if not self._specs:
            self._set_empty_state()
            return

        # 1. Parameter Inputs
        i = 0
        n = len(self._specs)
        while i < n:
            s1 = self._specs[i]
            if i + 1 < n and self._can_pair(s1, self._specs[i + 1]):
                pair_row = self._build_paired_row(s1, self._specs[i + 1])
                self._params_layout.addWidget(pair_row)
                i += 2
                continue

            row = self._build_single_row(s1)
            self._params_layout.addWidget(row)
            i += 1

        topic_key = getattr(theorem, "key", "")

        # Auto-apply and quick swap button for Compare Sorting
        if topic_key == "compare_sorting":
            for k in ("algo_1", "algo_2"):
                cb = self._inputs.get(k)
                if isinstance(cb, QComboBox):
                    cb.activated.connect(lambda *_: self._on_apply_clicked())

            swap_btn = QPushButton("⇄  Swap Left and Right Algorithms")
            swap_btn.setObjectName("CompareSwapParamBtn")
            swap_btn.setCursor(Qt.PointingHandCursor)
            swap_btn.setStyleSheet("""
                QPushButton#CompareSwapParamBtn {
                    background-color: #F8FAFC;
                    color: #6C5CE7;
                    border: 1px dashed #C4B5FD;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
                    font-size: 11.5px;
                    font-weight: 600;
                    margin-top: 4px;
                    margin-bottom: 4px;
                }
                QPushButton#CompareSwapParamBtn:hover {
                    background-color: #EDE9FE;
                    border-color: #8B5CF6;
                    color: #5B21B6;
                }
            """)
            def _swap_inputs():
                cb1 = self._inputs.get("algo_1")
                cb2 = self._inputs.get("algo_2")
                if isinstance(cb1, QComboBox) and isinstance(cb2, QComboBox):
                    t1, t2 = cb1.currentText(), cb2.currentText()
                    cb1.setCurrentText(t2)
                    cb2.setCurrentText(t1)
                    self._on_apply_clicked()
            swap_btn.clicked.connect(_swap_inputs)
            self._params_layout.addWidget(swap_btn)

        # 2. Quick Presets Section (if available for this topic)
        presets = TOPIC_PRESETS.get(topic_key, [])
        if presets:
            self._preset_section = self._build_preset_section(presets)
            self._params_layout.addWidget(self._preset_section)

        # 3. Sorting Visual Themes & Benchmark Comparison Section (if sorting topic)
        if topic_key in ("bubble_sort", "selection_sort", "insertion_sort", "merge_sort", "quick_sort"):
            theme_section = self._build_sorting_styles_section()
            self._params_layout.addWidget(theme_section)
            comp_card = self._build_sorting_comparison_launcher(topic_key)
            self._params_layout.addWidget(comp_card)
        elif topic_key in ("linear_search", "binary_search"):
            comp_btn = QPushButton("⚔  Compare Linear vs Binary Search →")
            comp_btn.setObjectName("CompareQuickBtn")
            comp_btn.setCursor(Qt.PointingHandCursor)
            comp_btn.setStyleSheet("""
                QPushButton#CompareQuickBtn {
                    background-color: #EFF6FF;
                    color: #2563EB;
                    border: 1px solid #BFDBFE;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
                    font-size: 11.5px;
                    font-weight: 600;
                    text-align: center;
                }
                QPushButton#CompareQuickBtn:hover {
                    background-color: #DBEAFE;
                    border-color: #3B82F6;
                    color: #1D4ED8;
                }
            """)
            comp_btn.clicked.connect(lambda: self.compareRequested.emit("compare_searching"))
            self._params_layout.addWidget(comp_btn)

        # 4. Clipping lesson controls
        if topic_key in ("clip_cohen_sutherland", "clip_sutherland_hodgman"):
            combo = self._inputs.get("polygon_shape")
            if isinstance(combo, QComboBox):
                combo.activated.connect(lambda *_: self._on_apply_clicked())

        # 5. Curve lesson now-card (Bézier Subdivision, B-spline, Hermite)
        if topic_key in ("curve_bezier", "curve_bspline", "curve_hermite"):
            curve_section = self._build_curve_walkthrough_section()
            self._params_layout.addWidget(curve_section)


        # Update Practical Learning Widget with the current topic
        if hasattr(self, "practical_widget") and topic_key:
            self.practical_widget.set_topic(topic_key)

        self._hide_error()
        self._action_widget.show()
        self._apply_btn.setEnabled(True)
        self._reset_btn.setEnabled(True)
        if hasattr(self, "_scroll") and self._scroll:
            self._scroll.verticalScrollBar().setValue(0)

    def get_values(self) -> dict:
        """Return the currently-entered values (unvalidated)."""
        res = {}
        specs_map = {s.key: s for s in self._specs} if hasattr(self, "_specs") else {}
        for k, widget in self._inputs.items():
            if isinstance(widget, QComboBox):
                res[k] = widget.currentText()
            else:
                raw = widget.text().strip()
                spec = specs_map.get(k)
                if spec and spec.param_type == ParameterType.TEXT:
                    res[k] = raw
                else:
                    res[k] = raw.replace(',', '.')
        return res

    def show_validation_error(self, message: str):
        self._error_label.setText(message)
        self._error_label.show()

    def clear_validation_error(self):
        self._hide_error()

    # ------------------------------------------------------------------
    # Internal Field & Stepper Builders
    # ------------------------------------------------------------------
    def _can_pair(self, s1: ParameterSpec, s2: ParameterSpec) -> bool:
        if (s1.key, s2.key) in PAIRS:
            return True
        if s1.param_type not in (ParameterType.TEXT, ParameterType.CHOICE) and \
           s2.param_type not in (ParameterType.TEXT, ParameterType.CHOICE):
            if len(s1.label) <= 14 and len(s2.label) <= 14:
                return True
        return False

    def _build_paired_row(self, s1: ParameterSpec, s2: ParameterSpec) -> QWidget:
        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)

        col1 = self._build_field_col(s1, is_paired=True)
        col2 = self._build_field_col(s2, is_paired=True)
        h.addWidget(col1, stretch=1)
        h.addWidget(col2, stretch=1)
        return row

    def _build_single_row(self, spec: ParameterSpec) -> QWidget:
        row = QWidget()
        v = QVBoxLayout(row)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)

        col = self._build_field_col(spec, is_paired=False)
        v.addWidget(col)
        return row

    def _build_field_col(self, spec: ParameterSpec, is_paired: bool = False) -> QWidget:
        col = QWidget()
        self._field_cols[spec.key] = col
        v = QVBoxLayout(col)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)

        # Text input (e.g. array string) enclosed in dedicated ArrayCard container
        if spec.param_type == ParameterType.TEXT:
            card = QFrame()
            card.setObjectName("ArrayCard")
            cv = QVBoxLayout(card)
            cv.setContentsMargins(12, 10, 12, 10)
            cv.setSpacing(6)

            header_row = QHBoxLayout()
            header_row.setContentsMargins(0, 0, 0, 0)
            lbl = QLabel(spec.label)
            lbl.setObjectName("ArrayCardLabel")
            header_row.addWidget(lbl)
            header_row.addStretch(1)

            count_badge = QLabel("")
            count_badge.setObjectName("ArrayCountBadge")
            header_row.addWidget(count_badge)
            cv.addLayout(header_row)

            edit = QLineEdit(self._format_default(spec.default))
            edit.setObjectName("ArrayCardInput")
            edit.setFixedHeight(38)
            if spec.key == "custom_edges":
                edit.setPlaceholderText("e.g. A-B:4, B-C:2, C-A:5")
                count_badge.setText("Optional")
                count_badge.setStyleSheet("color: #64748B; background: transparent; border: none; font-size: 11px;")
            cv.addWidget(edit)

            def _update_count(text: str):
                if spec.key == "custom_edges":
                    parts = [p.strip() for p in text.split(',') if p.strip()]
                    n = len(parts)
                    count_badge.setText(f"{n} edges" if n else "Optional")
                else:
                    parts = [p.strip() for p in text.split(',') if p.strip()]
                    n = len(parts)
                    count_badge.setText(f"{n} item" if n == 1 else f"{n} items")

            _update_count(edit.text())
            edit.textChanged.connect(_update_count)
            edit.textChanged.connect(lambda _=None, k=spec.key: self._validate_field(k))
            edit.returnPressed.connect(self._on_apply_clicked)

            self._inputs[spec.key] = edit
            v.addWidget(card)
            return col

        # Clear, prominent parameter label (not camouflaged)
        lbl = QLabel(spec.label)
        lbl.setObjectName("ParamLabel")
        v.addWidget(lbl)

        # Choice Dropdown
        if spec.param_type == ParameterType.CHOICE:
            combo = QComboBox()
            combo.setObjectName("ParamInput")
            combo.setFixedHeight(34)
            if spec.choices:
                combo.addItems(spec.choices)
            if str(spec.default) in spec.choices:
                combo.setCurrentText(str(spec.default))
            v.addWidget(combo)
            self._inputs[spec.key] = combo
            return col

        # Precision Stepper [ − ] [ Value ] [ + ]
        stepper_box = QWidget()
        sh = QHBoxLayout(stepper_box)
        sh.setContentsMargins(0, 0, 0, 0)
        sh.setSpacing(2 if is_paired else 4)

        minus_btn = QPushButton("−")
        minus_btn.setObjectName("StepperButton")
        minus_btn.setCursor(Qt.PointingHandCursor)
        minus_btn.setToolTip(f"Decrease {spec.label}")
        if is_paired:
            minus_btn.setFixedSize(26, 28)
        else:
            minus_btn.setFixedSize(30, 32)
        sh.addWidget(minus_btn)

        edit = QLineEdit(self._format_default(spec.default))
        edit.setObjectName("ParamInput")
        edit.setFixedHeight(30 if is_paired else 34)
        edit.setAlignment(Qt.AlignCenter)
        if is_paired:
            edit.setFixedWidth(50)
        else:
            edit.setFixedWidth(80)

        if spec.param_type == ParameterType.INTEGER:
            validator = QRegExpValidator(QRegExp(r"^-?\d*$"), edit)
            edit.setValidator(validator)
        else:
            # Allows decimal typing like "0.5", "3.", "3.14", ",5" without Qt blocking keystrokes
            validator = QRegExpValidator(QRegExp(r"^-?\d*[.,]?\d*$"), edit)
            edit.setValidator(validator)

        edit.textChanged.connect(lambda _=None, k=spec.key: self._validate_field(k))
        sh.addWidget(edit)

        plus_btn = QPushButton("+")
        plus_btn.setObjectName("StepperButton")
        plus_btn.setCursor(Qt.PointingHandCursor)
        plus_btn.setToolTip(f"Increase {spec.label}")
        if is_paired:
            plus_btn.setFixedSize(26, 28)
        else:
            plus_btn.setFixedSize(30, 32)
        sh.addWidget(plus_btn)

        # Unit badge
        unit_str = spec.suffix
        if not unit_str:
            if spec.param_type == ParameterType.ANGLE:
                unit_str = "°"
            elif spec.param_type == ParameterType.RATIO:
                unit_str = "×"
            elif spec.param_type == ParameterType.LENGTH and "X" not in spec.label and "Y" not in spec.label:
                unit_str = "cm"

        if unit_str:
            unit_lbl = QLabel(unit_str)
            unit_lbl.setObjectName("ParamUnitBadge")
            sh.addWidget(unit_lbl)

        sh.addStretch(1)

        minus_btn.clicked.connect(lambda: self._on_step_change(spec, edit, -1))
        plus_btn.clicked.connect(lambda: self._on_step_change(spec, edit, 1))
        edit.returnPressed.connect(self._on_apply_clicked)

        v.addWidget(stepper_box)
        self._inputs[spec.key] = edit
        return col

    def _get_step_size(self, spec: ParameterSpec) -> float:
        if spec.param_type == ParameterType.ANGLE:
            return 5.0
        elif spec.param_type == ParameterType.RATIO:
            return 0.1
        elif spec.param_type == ParameterType.INTEGER:
            return 1.0
        elif spec.param_type == ParameterType.LENGTH:
            return 0.5
        else:
            span = spec.max_value - spec.min_value
            if span <= 10.0:
                return 0.5
            elif span <= 30.0:
                return 1.0
            else:
                return 2.0

    def _on_step_change(self, spec: ParameterSpec, edit: QLineEdit, direction: int):
        step = self._get_step_size(spec) * direction
        raw_text = edit.text().strip().replace(',', '.')
        try:
            val = float(raw_text)
        except ValueError:
            val = float(spec.default)

        new_val = max(spec.min_value, min(spec.max_value, val + step))
        if spec.param_type == ParameterType.INTEGER:
            edit.setText(str(int(round(new_val))))
        else:
            if abs(new_val - round(new_val)) < 1e-6:
                edit.setText(str(int(round(new_val))))
            else:
                edit.setText(f"{new_val:.2f}".rstrip("0").rstrip("."))

        # Deactivate any active preset highlight since value manually changed
        for c in self._preset_chips:
            c.setProperty("active", "false")
            c.style().unpolish(c)
            c.style().polish(c)

    # ------------------------------------------------------------------
    # Quick Presets Section Builder
    # ------------------------------------------------------------------
    def _build_preset_section(self, presets: list) -> QWidget:
        container = QWidget()
        v = QVBoxLayout(container)
        v.setContentsMargins(0, 8, 0, 0)
        v.setSpacing(6)

        title = QLabel("QUICK PRESETS")
        title.setObjectName("PresetSectionTitle")
        v.addWidget(title)

        chips_widget = QWidget()
        flow = FlowLayout(chips_widget, margin=0, h_spacing=6, v_spacing=6)

        for name, preset_values in presets:
            chip = QPushButton(name)
            chip.setObjectName("PresetChip")
            chip.setCursor(Qt.PointingHandCursor)
            chip.clicked.connect(lambda ch, pv=preset_values, b=chip: self._on_preset_clicked(pv, b))
            flow.addWidget(chip)
            self._preset_chips.append(chip)

        v.addWidget(chips_widget)
        return container

    def _on_preset_clicked(self, preset_values: dict, chip_btn: QPushButton):
        """Immediately populate inputs, highlight chip, and apply parameters."""
        for c in self._preset_chips:
            c.setProperty("active", "true" if c == chip_btn else "false")
            c.style().unpolish(c)
            c.style().polish(c)

        for k, val in preset_values.items():
            widget = self._inputs.get(k)
            if not widget:
                continue
            if isinstance(widget, QComboBox):
                widget.setCurrentText(str(val))
            else:
                if isinstance(val, float) and val.is_integer():
                    widget.setText(str(int(val)))
                else:
                    widget.setText(str(val))

        self._hide_error()
        self._on_apply_clicked()

    def _build_sorting_styles_section(self) -> QWidget:
        container = QWidget()
        v = QVBoxLayout(container)
        v.setContentsMargins(0, 10, 0, 0)
        v.setSpacing(6)

        title = QLabel("VISUALIZATION STYLE")
        title.setObjectName("PresetSectionTitle")
        v.addWidget(title)

        chips_widget = QWidget()
        flow = FlowLayout(chips_widget, margin=0, h_spacing=6, v_spacing=6)

        styles = [
            ("balls", "Bouncing Balls"),
            ("cubes", "Floating Cubes"),
            ("marbles", "Marble Track"),
            ("cars", "Toy Cars"),
            ("bars", "Bars"),
        ]

        self._style_chips = []
        current = getattr(self, "_current_sort_style", "balls")
        for key, name in styles:
            chip = QPushButton(name)
            chip.setObjectName("PresetChip")
            chip.setCursor(Qt.PointingHandCursor)
            if key == current:
                chip.setProperty("active", "true")
            chip.clicked.connect(lambda ch, s=key, b=chip: self._on_style_chip_clicked(s, b))
            flow.addWidget(chip)
            self._style_chips.append((key, chip))

        v.addWidget(chips_widget)
        return container

    def _build_sorting_comparison_launcher(self, topic_key: str) -> QWidget:
        container = QFrame()
        container.setObjectName("SortingCompLauncherCard")
        container.setStyleSheet("""
            QFrame#SortingCompLauncherCard {
                background-color: #F8FAFC;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                padding: 10px;
                margin-top: 6px;
            }
            QLabel#LauncherTitle {
                color: #0F172A;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
                font-size: 11.5px;
                font-weight: 700;
            }
            QLabel#LauncherSubtitle {
                color: #64748B;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
                font-size: 10.5px;
            }
            QComboBox#LauncherCombo {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 4px 8px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
                font-size: 11px;
                font-weight: 600;
                height: 28px;
            }
            QPushButton#LauncherBtn {
                background-color: #6C5CE7;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
                font-size: 11px;
                font-weight: 700;
                height: 28px;
            }
            QPushButton#LauncherBtn:hover {
                background-color: #5B21B6;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        hdr = QLabel("⚔  Benchmark Comparison")
        hdr.setObjectName("LauncherTitle")
        layout.addWidget(hdr)

        names = {
            "bubble_sort": "Bubble Sort",
            "selection_sort": "Selection Sort",
            "insertion_sort": "Insertion Sort",
            "merge_sort": "Merge Sort",
            "quick_sort": "Quick Sort",
        }
        current_name = names.get(topic_key, "Bubble Sort")

        sub = QLabel(f"Run {current_name} side-by-side with a rival:")
        sub.setObjectName("LauncherSubtitle")
        layout.addWidget(sub)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)

        combo = QComboBox()
        combo.setObjectName("LauncherCombo")
        all_algos = ["Bubble Sort", "Selection Sort", "Insertion Sort", "Merge Sort", "Quick Sort"]
        rivals = [a for a in all_algos if a != current_name]
        combo.addItems(rivals)

        default_rival = "Quick Sort" if current_name != "Quick Sort" else "Merge Sort"
        if default_rival in rivals:
            combo.setCurrentText(default_rival)

        row.addWidget(combo, stretch=1)

        btn = QPushButton("Compare →")
        btn.setObjectName("LauncherBtn")
        btn.setCursor(Qt.PointingHandCursor)
        def _launch():
            rival = combo.currentText()
            self.compareWithRequested.emit(current_name, rival)
            self.compareRequested.emit("compare_sorting")
        btn.clicked.connect(_launch)
        row.addWidget(btn, stretch=0)

        layout.addLayout(row)
        return container

    def _on_style_chip_clicked(self, style_key: str, chip_btn: QPushButton):
        self._current_sort_style = style_key
        for k, c in getattr(self, "_style_chips", []):
            c.setProperty("active", "true" if c == chip_btn else "false")
            c.style().unpolish(c)
            c.style().polish(c)
        self.sortingStyleRequested.emit(style_key)

    def set_current_sort_style(self, style_key: str):
        self._current_sort_style = style_key
        for k, c in getattr(self, "_style_chips", []):
            is_active = (k == style_key)
            c.setProperty("active", "true" if is_active else "false")
            c.style().unpolish(c)
            c.style().polish(c)

    def set_input_value(self, key: str, value: Any):
        """Programmatically update a single input field (e.g., from canvas dragging)."""
        widget = self._inputs.get(key)
        if widget is None:
            return
        widget.blockSignals(True)
        if isinstance(widget, QComboBox):
            text = str(value)
            idx = widget.findText(text)
            if idx >= 0:
                widget.setCurrentIndex(idx)
            else:
                widget.setCurrentText(text)
        elif isinstance(value, float):
            if abs(value - round(value)) < 1e-6:
                widget.setText(str(int(round(value))))
            else:
                widget.setText(f"{value:.2f}".rstrip("0").rstrip("."))
        else:
            widget.setText(str(value))
        widget.blockSignals(False)

    def _build_clipping_walkthrough_section(self) -> QWidget:
        """Compact now-card for Cohen–Sutherland and Sutherland–Hodgman lessons."""
        container = QWidget()
        container.setObjectName("PresetContainer")
        self._clip_walkthrough = container
        v = QVBoxLayout(container)
        v.setContentsMargins(12, 10, 12, 12)
        v.setSpacing(8)

        header_row = QHBoxLayout()
        self._clip_card_title = QLabel("THIS STEP")
        self._clip_card_title.setObjectName("PresetSectionTitle")
        header_row.addWidget(self._clip_card_title)
        header_row.addStretch(1)
        self._clip_iter_badge = QLabel("Start")
        self._clip_iter_badge.setStyleSheet(
            "background: #EDE9FE; color: #5B21B6; "
            "font-weight: 600; font-size: 11px; padding: 2px 8px; border-radius: 8px;"
        )
        header_row.addWidget(self._clip_iter_badge)
        v.addLayout(header_row)

        self._clip_hint = QLabel("Click a region on the canvas. Each region has a 4-bit code.")
        self._clip_hint.setWordWrap(True)
        self._clip_hint.setStyleSheet("color: #64748B; font-size: 12.5px;")
        v.addWidget(self._clip_hint)

        self._clip_codes = QWidget()
        codes_l = QVBoxLayout(self._clip_codes)
        codes_l.setContentsMargins(0, 0, 0, 0)
        codes_l.setSpacing(3)
        self._clip_p1_lbl = QLabel("P1   ·   —")
        self._clip_p1_lbl.setStyleSheet("font-family: monospace; font-size: 12px; color: #1E293B;")
        codes_l.addWidget(self._clip_p1_lbl)
        self._clip_p2_lbl = QLabel("P2   ·   —")
        self._clip_p2_lbl.setStyleSheet("font-family: monospace; font-size: 12px; color: #1E293B;")
        codes_l.addWidget(self._clip_p2_lbl)
        v.addWidget(self._clip_codes)

        self._clip_dec_banner = QLabel("")
        self._clip_dec_banner.setWordWrap(True)
        self._clip_dec_banner.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._clip_dec_banner.setStyleSheet(
            "background: #F8FAFC; color: #334155; border: 1px solid #E2E8F0; "
            "font-size: 12.5px; padding: 8px 10px; border-radius: 8px;"
        )
        v.addWidget(self._clip_dec_banner)
        self._clip_lesson_tab = ""
        return container

    def _set_param_field_visible(self, key: str, visible: bool):
        col = getattr(self, "_field_cols", {}).get(key)
        if col is None:
            return
        col.setVisible(visible)
        parent = col.parent()
        if parent is not None and parent is not self._params_widget:
            parent.setVisible(visible)

    def set_clipping_lesson_tab(self, tab_key: str):
        self._clip_lesson_tab = tab_key or ""
        is_regions = tab_key == "region_codes"
        is_clip_line = tab_key == "clip_line"
        is_cases = tab_key == "four_cases"
        is_clip_poly = tab_key == "clip_polygon"

        topic = getattr(self._active_theorem, "key", "") if self._active_theorem else ""
        if getattr(self, "_preset_section", None) and topic == "clip_sutherland_hodgman":
            self._preset_section.setVisible(is_clip_poly)
        self._set_param_field_visible("polygon_shape", is_clip_poly)

        # The clipping walkthrough card is intentionally omitted from the UI.
        # Keep tab-specific parameter visibility working without that card.
        if not getattr(self, "_clip_walkthrough", None):
            return

        self._clip_walkthrough.setVisible(is_regions or is_clip_line or is_cases or is_clip_poly)

        if is_regions:
            self._clip_card_title.setText("REGION CODES")
            self._clip_iter_badge.setText("Explore")
            self._clip_hint.setText(
                "Click any region. T B R L means Top, Bottom, Right, Left — a 1 means outside on that side."
            )
            self._clip_codes.hide()
            self._clip_dec_banner.hide()
        elif is_clip_line:
            self._clip_card_title.setText("THIS STEP")
            self._clip_hint.setText("Drag P1 or P2 on the canvas, or pick a preset, then step through.")
            self._clip_codes.show()
            self._clip_dec_banner.show()
        elif is_cases:
            self._clip_card_title.setText("FOUR CASES")
            self._clip_iter_badge.setText("Learn")
            self._clip_hint.setText(
                "Each polygon edge is classified against one window side. Memorize these four transitions."
            )
            self._clip_codes.hide()
            self._clip_dec_banner.hide()
        elif is_clip_poly:
            self._clip_card_title.setText("THIS STEP")
            self._clip_hint.setText("Pick a shape, then walk every edge against LEFT, RIGHT, BOTTOM, and TOP.")
            self._clip_codes.show()
            self._clip_dec_banner.show()
            self._clip_p1_lbl.setText("S   ·   —")
            self._clip_p2_lbl.setText("P   ·   —")

    def update_clipping_walkthrough(self, step_values: dict):
        """Update the now-card from the current algorithm step."""
        if not hasattr(self, "_clip_iter_badge"):
            return
        tab = getattr(self, "_clip_lesson_tab", "")
        caption = step_values.get("caption") or step_values.get("region_name") or ""

        if tab == "region_codes":
            if caption:
                self._clip_hint.setText(str(caption))
            return

        if tab == "four_cases":
            lesson = step_values.get("lesson") or step_values.get("focus") or ""
            case = step_values.get("case")
            badges = {
                "meet": "Idea",
                "pipeline": "Pipeline",
                "halfplane": "Half-plane",
                "wrap": "Next",
            }
            case_badges = {
                "in_in": "IN → IN",
                "in_out": "IN → OUT",
                "out_in": "OUT → IN",
                "out_out": "OUT → OUT",
            }
            self._clip_iter_badge.setText(case_badges.get(case, badges.get(lesson, "Learn")))
            if caption:
                self._clip_hint.setText(str(caption))
            if lesson == "case" and caption:
                self._clip_dec_banner.setText(str(caption))
                self._clip_dec_banner.setStyleSheet(
                    "background: #F5F3FF; color: #5B21B6; border: 1px solid #DDD6FE; "
                    "font-size: 12.5px; padding: 8px 10px; border-radius: 8px;"
                )
                self._clip_dec_banner.show()
            else:
                self._clip_dec_banner.hide()
            return

        if tab == "clip_polygon":
            stage = step_values.get("stage", "")
            boundary = (step_values.get("boundary") or step_values.get("edge") or "").title()
            pass_i = step_values.get("pass_index")
            case = step_values.get("case")
            if pass_i and boundary:
                self._clip_iter_badge.setText(f"Pass {pass_i} · {boundary}")
            elif stage == "final_result":
                self._clip_iter_badge.setText("Done")
            else:
                self._clip_iter_badge.setText("Now")

            s_in = step_values.get("s_inside")
            p_in = step_values.get("p_inside")
            if s_in is None:
                self._clip_p1_lbl.setText("S   ·   —")
            else:
                self._clip_p1_lbl.setText("S   ·   inside" if s_in else "S   ·   outside")
            if p_in is None:
                self._clip_p2_lbl.setText("P   ·   —")
            else:
                self._clip_p2_lbl.setText("P   ·   inside" if p_in else "P   ·   outside")

            style = (
                "background: #F8FAFC; color: #334155; border: 1px solid #E2E8F0; "
                "font-size: 12.5px; padding: 8px 10px; border-radius: 8px;"
            )
            if case == "in_in" or (stage == "final_result" and step_values.get("status") == "accepted"):
                style = (
                    "background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; "
                    "font-size: 12.5px; padding: 8px 10px; border-radius: 8px;"
                )
            elif case == "out_out" or (stage == "final_result" and step_values.get("status") == "rejected"):
                style = (
                    "background: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; "
                    "font-size: 12.5px; padding: 8px 10px; border-radius: 8px;"
                )
            elif stage in ("edge", "pass_intro") or case in ("in_out", "out_in"):
                style = (
                    "background: #F5F3FF; color: #5B21B6; border: 1px solid #DDD6FE; "
                    "font-size: 12.5px; padding: 8px 10px; border-radius: 8px;"
                )
            if caption:
                self._clip_dec_banner.setText(caption)
                self._clip_dec_banner.setStyleSheet(style)
                self._clip_dec_banner.show()
            return

        stage = step_values.get("stage", "")
        iteration = step_values.get("iteration")
        self._clip_iter_badge.setText(f"Clip {iteration}" if iteration else "Now")

        p1_code = step_values.get("code1_str")
        p2_code = step_values.get("code2_str")
        if p1_code:
            self._clip_p1_lbl.setText(f"P1   ·   {p1_code}")
        if p2_code:
            self._clip_p2_lbl.setText(f"P2   ·   {p2_code}")

        style = (
            "background: #F8FAFC; color: #334155; border: 1px solid #E2E8F0; "
            "font-size: 12.5px; padding: 8px 10px; border-radius: 8px;"
        )
        if stage == "or_test" and step_values.get("decision") == "ACCEPT":
            style = (
                "background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; "
                "font-size: 12.5px; padding: 8px 10px; border-radius: 8px;"
            )
        elif stage == "and_test" and step_values.get("decision") == "REJECT":
            style = (
                "background: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; "
                "font-size: 12.5px; padding: 8px 10px; border-radius: 8px;"
            )
        elif stage in ("select_boundary", "calculate_intersection", "update_endpoint"):
            style = (
                "background: #F5F3FF; color: #5B21B6; border: 1px solid #DDD6FE; "
                "font-size: 12.5px; padding: 8px 10px; border-radius: 8px;"
            )
        elif stage == "final_result":
            accepted = step_values.get("status") == "accepted"
            style = (
                "background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; "
                "font-size: 12.5px; padding: 8px 10px; border-radius: 8px;"
            ) if accepted else (
                "background: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; "
                "font-size: 12.5px; padding: 8px 10px; border-radius: 8px;"
            )
            if caption:
                self._clip_dec_banner.setText(caption)
                self._clip_dec_banner.setStyleSheet(style)
                self._clip_dec_banner.show()

    def _build_curve_walkthrough_section(self) -> QWidget:
        """Now-card for Bézier, B-spline and Hermite lessons, with a live t/u slider."""
        container = QWidget()
        container.setObjectName("PresetContainer")
        self._curve_walkthrough = container
        v = QVBoxLayout(container)
        v.setContentsMargins(12, 10, 12, 12)
        v.setSpacing(8)

        header_row = QHBoxLayout()
        self._curve_card_title = QLabel("THIS STEP")
        self._curve_card_title.setObjectName("PresetSectionTitle")
        header_row.addWidget(self._curve_card_title)
        header_row.addStretch(1)
        self._curve_badge = QLabel("t")
        self._curve_badge.setStyleSheet(
            "background: #EDE9FE; color: #5B21B6; "
            "font-weight: 600; font-size: 11px; padding: 2px 8px; border-radius: 8px;"
        )
        header_row.addWidget(self._curve_badge)
        v.addLayout(header_row)

        self._curve_hint = QLabel("Drag control points on the canvas. Play sweeps the parameter.")
        self._curve_hint.setWordWrap(True)
        self._curve_hint.setStyleSheet("color: #64748B; font-size: 12.5px;")
        v.addWidget(self._curve_hint)

        slider_row = QHBoxLayout()
        self._curve_t_label = QLabel("t")
        self._curve_t_label.setStyleSheet("font-family: monospace; font-size: 12px; color: #1E293B;")
        self._curve_t_label.setFixedWidth(16)
        slider_row.addWidget(self._curve_t_label)
        self._curve_t_slider = QSlider(Qt.Horizontal)
        self._curve_t_slider.setRange(0, 20)
        self._curve_t_slider.setValue(7)
        self._curve_t_slider.setCursor(Qt.PointingHandCursor)
        self._curve_t_slider.valueChanged.connect(self._on_curve_t_slider)
        slider_row.addWidget(self._curve_t_slider, stretch=1)
        self._curve_t_value = QLabel("0.35")
        self._curve_t_value.setStyleSheet(
            "font-family: monospace; font-size: 12px; color: #5B21B6; min-width: 36px;"
        )
        slider_row.addWidget(self._curve_t_value)
        v.addLayout(slider_row)
        self._curve_slider_row = slider_row

        self._curve_banner = QLabel("")
        self._curve_banner.setWordWrap(True)
        self._curve_banner.setStyleSheet(
            "background: #F5F3FF; color: #5B21B6; border: 1px solid #DDD6FE; "
            "font-size: 12.5px; padding: 8px 10px; border-radius: 8px;"
        )
        v.addWidget(self._curve_banner)

        self._curve_knots = QLabel("")
        self._curve_knots.setWordWrap(True)
        self._curve_knots.setStyleSheet("font-family: monospace; font-size: 11px; color: #475569;")
        self._curve_knots.hide()
        v.addWidget(self._curve_knots)

        self._curve_topic = ""
        self._curve_lesson_tab = ""
        return container

    def _on_curve_t_slider(self, ticks: int):
        value = ticks / 20.0
        self._curve_t_value.setText(f"{value:.2f}")
        self.curveTChanged.emit(value)

    def set_curve_lesson_tab(self, topic_key: str, tab_key: str):
        self._curve_topic = topic_key or ""
        self._curve_lesson_tab = tab_key or ""
        if not getattr(self, "_curve_walkthrough", None):
            return
        is_curve = topic_key in ("curve_bezier", "curve_bspline", "curve_hermite")
        self._curve_walkthrough.setVisible(is_curve)
        if not is_curve:
            return

        param_name = "u" if topic_key == "curve_bspline" else "t"
        self._curve_t_label.setText(param_name)
        show_slider = tab_key in ("casteljau", "math", "experiment")
        if hasattr(self, "_curve_t_slider"):
            self._curve_t_slider.setVisible(show_slider)
            self._curve_t_label.setVisible(show_slider)
            self._curve_t_value.setVisible(show_slider)

        titles = {
            "intro": "THE IDEA",
            "math": "THE MATH",
            "casteljau": "DE CASTELJAU & EXPERIMENT",
            "experiment": "EXPERIMENT",
        }
        self._curve_card_title.setText(titles.get(tab_key, "THIS STEP"))

        if tab_key == "intro":
            self._curve_hint.setText("Read the construction, then open the next tab to manipulate it.")
        elif tab_key == "math":
            self._curve_hint.setText("The formula and the picture stay in lockstep. Drag handles anytime.")
        elif tab_key == "casteljau":
            self._curve_hint.setText("Drag handles on canvas or adjust t slider. Play steps through the lerp pyramid.")
        else:
            self._curve_hint.setText("Drag handles on the canvas. Play sweeps the parameter from 0 to 1.")

        self._set_param_field_visible("t", topic_key != "curve_bspline")
        self._set_param_field_visible("u", topic_key == "curve_bspline")
        for key in ("degree", "knot_style"):
            self._set_param_field_visible(key, topic_key == "curve_bspline")

    def update_curve_walkthrough(self, step_values: dict):
        if not getattr(self, "_curve_walkthrough", None):
            return
        t = step_values.get("t")
        if t is None:
            t = step_values.get("u")
        if t is not None and hasattr(self, "_curve_t_slider"):
            ticks = int(round(float(t) * 20))
            self._curve_t_slider.blockSignals(True)
            self._curve_t_slider.setValue(max(0, min(20, ticks)))
            self._curve_t_slider.blockSignals(False)
            self._curve_t_value.setText(f"{float(t):.2f}")

        caption = step_values.get("caption") or ""
        if caption:
            self._curve_hint.setText(str(caption))

        pt = step_values.get("curve_point")
        stage = step_values.get("stage", "")
        if pt:
            self._curve_banner.setText(f"C = ({pt[0]:.2f}, {pt[1]:.2f})")
            self._curve_banner.show()
        elif caption:
            self._curve_banner.setText(str(caption))
            self._curve_banner.show()
        else:
            self._curve_banner.hide()

        badge = "Now"
        if t is not None:
            badge = f"t = {float(t):.2f}" if self._curve_topic != "curve_bspline" else f"u = {float(t):.2f}"
        if stage.startswith("level"):
            badge = stage.replace("level", "L")
        elif stage == "experiment":
            badge = badge
        self._curve_badge.setText(badge)

        knots = step_values.get("knots")
        if knots:
            body = ", ".join(f"{k:.2f}" for k in knots)
            self._curve_knots.setText(f"U = [{body}]")
            self._curve_knots.show()
        else:
            self._curve_knots.hide()

    @staticmethod
    def _format_default(value) -> str:
        if isinstance(value, float):
            if abs(value - round(value)) < 1e-6:
                return str(int(round(value)))
            return f"{value:.2f}".rstrip("0").rstrip(".")
        return str(value)

    def _validate_field(self, key: str):
        widget = self._inputs.get(key)
        spec = next((s for s in self._specs if s.key == key), None)
        if not widget or not spec or isinstance(widget, QComboBox):
            return

        raw_text = widget.text().strip()
        if spec.param_type == ParameterType.TEXT:
            valid = True
            if spec.key == "custom_edges":
                if raw_text:
                    for part in raw_text.split(','):
                        part_str = part.strip()
                        if not part_str:
                            continue
                        if "-" not in part_str or ":" not in part_str:
                            valid = False
                            break
            else:
                if raw_text:
                    for part in raw_text.split(','):
                        part_str = part.strip()
                        if part_str and not (part_str.isdigit() or (part_str.startswith(('-', '+')) and part_str[1:].isdigit())):
                            valid = False
                            break
            widget.setProperty("invalid", "false" if valid else "true")
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            self._hide_error()
            return

        raw_text = raw_text.replace(',', '.')
        
        # Permit intermediate typing states (empty, minus sign, dot) without showing red error
        if raw_text in ("", "-", ".", "-."):
            widget.setProperty("invalid", "false")
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            return

        valid = True
        if spec.param_type in (ParameterType.LENGTH, ParameterType.ANGLE, ParameterType.RATIO):
            try:
                val = float(raw_text)
                if not (spec.min_value <= val <= spec.max_value):
                    valid = False
            except ValueError:
                valid = False
        elif spec.param_type == ParameterType.INTEGER:
            try:
                val = int(raw_text)
                if not (spec.min_value <= val <= spec.max_value):
                    valid = False
            except ValueError:
                valid = False

        widget.setProperty("invalid", "false" if valid else "true")
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        self._hide_error()

    def _on_apply_clicked(self):
        values = {}
        for spec in self._specs:
            widget = self._inputs[spec.key]
            if isinstance(widget, QComboBox):
                values[spec.key] = widget.currentText()
                continue

            raw_text = widget.text().strip()
            if spec.param_type == ParameterType.TEXT:
                values[spec.key] = raw_text
                continue

            text = raw_text.replace(',', '.')
            if spec.param_type == ParameterType.INTEGER:
                try:
                    val = int(text)
                    if not (spec.min_value <= val <= spec.max_value):
                        raise ValueError
                    values[spec.key] = val
                except ValueError:
                    self.show_validation_error(
                        f"'{spec.label}' must be an integer between {int(spec.min_value)} and {int(spec.max_value)}."
                    )
                    return
            else:
                try:
                    val = float(text)
                    if not (spec.min_value <= val <= spec.max_value):
                        raise ValueError
                    values[spec.key] = val
                except ValueError:
                    self.show_validation_error(
                        f"'{spec.label}' must be a number between {spec.min_value:g} and {spec.max_value:g}."
                    )
                    return

        self._hide_error()
        self.parametersApplied.emit(values)

    def _on_reset_clicked(self):
        """Restore all parameters to topic defaults."""
        if not self._specs:
            return

        defaults = {}
        for spec in self._specs:
            widget = self._inputs.get(spec.key)
            if not widget:
                continue

            defaults[spec.key] = spec.default
            if isinstance(widget, QComboBox):
                if str(spec.default) in spec.choices:
                    widget.setCurrentText(str(spec.default))
            else:
                widget.setText(self._format_default(spec.default))

        for c in self._preset_chips:
            c.setProperty("active", "false")
            c.style().unpolish(c)
            c.style().polish(c)

        self._hide_error()
        self.parametersApplied.emit(defaults)

    def _set_empty_state(self):
        self._clear_fields()
        placeholder = QLabel("Select an item to configure its parameters.")
        placeholder.setObjectName("ParamHint")
        placeholder.setWordWrap(True)
        self._params_layout.addWidget(placeholder)
        self._apply_btn.setEnabled(False)
        self._reset_btn.setEnabled(False)

    def _clear_fields(self):
        while self._params_layout.count():
            item = self._params_layout.takeAt(0)
            w = item.widget()
            if w:
                w.hide()
                w.setParent(None)
                w.deleteLater()
            elif item.layout():
                self._clear_layout_recursively(item.layout())
        self._preset_chips = []
        self._preset_section = None
        self._field_cols = {}
        self._clip_walkthrough = None
        self._curve_walkthrough = None
        self._hide_error()

    def _clear_layout_recursively(self, layout):
        if not layout:
            return
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.hide()
                w.setParent(None)
                w.deleteLater()
            elif item.layout():
                self._clear_layout_recursively(item.layout())

    def _hide_error(self):
        self._error_label.clear()
        self._error_label.hide()
