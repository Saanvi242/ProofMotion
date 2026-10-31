"""
controllers/application_controller.py
----------------------------------------
Central mediator between MainWindow (GUI) and the mathematical,
algorithmic, and CGIP engines in ProofMotion.

Coordinates:
  - Module selection: Theorems, Algorithms, Transformations, Rasterization, Clipping, Image Processing
  - Dynamic parameter panels and validation
  - Step-by-step state advancement, playback timers, and speed multipliers
  - View controls (Zoom, Pan, Reset)
  - Synchronized equations, pseudocode, metrics, and explanations
"""

import random
from typing import Dict, List, Any, Optional
from PyQt5.QtCore import QObject, QTimer, pyqtSignal

from models.theorem_state import Theorem, ParameterSpec, ParameterType, ProofStep
from core.step_model import VisualizationStep
from theorems.theorem_engine import TheoremEngine
from algorithms.algorithm_engine import AlgorithmEngine
import cgip.transformations as cgip_trans
import cgip.rasterization as cgip_rast
import cgip.clipping as cgip_clip
import cgip.projection_3d as cgip_3d
import cgip.curves as cgip_curves


class ApplicationController(QObject):
    theoremChanged = pyqtSignal(str)              # topic key
    stepChanged = pyqtSignal(int, int)             # (0-based index, total)
    playbackStateChanged = pyqtSignal(bool)        # is_playing

    BASE_TICK_MS = 1400

    def __init__(self, main_window, engine=None, parent=None):
        super().__init__(parent)
        self.window = main_window
        self.theorem_engine = engine or TheoremEngine()

        self.current_module = "algorithms"
        self.current_topic_key = ""
        self.current_parameters: Dict[str, Any] = {}
        self.current_steps: List[Any] = []
        self.current_step_index = 0
        self.is_playing = False
        self.speed_multiplier = 1.0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._advance_step_from_timer)

        self._init_module_catalog()
        self._wire_signals()

        # First paint is the Learn / Studio gateway, not a packed lesson
        if hasattr(self.window, "show_home"):
            self.window.show_home()
        else:
            self.window.select_module("algorithms")
            self.on_module_selected("algorithms")

    # ------------------------------------------------------------------
    # Module & Topic Catalog
    # ------------------------------------------------------------------
    def _init_module_catalog(self):
        """Define topics and parameter specs for each module."""
        self._catalog = {
            "theorems": {
                "title": "THEOREMS",
                "items": self.theorem_engine.get_theorems_list(),
            },
            "algorithms": {
                "title": "ALGORITHMS",
                "items": [
                    Theorem(
                        key="bubble_sort",
                        display_name="Bubble Sort",
                        short_description="Repeatedly compares and swaps adjacent elements.",
                        parameters=[
                            ParameterSpec("array_input", "Array (comma-separated)", ParameterType.TEXT, default="24, 13, 9, 45, 18, 32, 5, 29"),
                        ]
                    ),
                    Theorem(
                        key="selection_sort",
                        display_name="Selection Sort",
                        short_description="Repeatedly selects minimum from unsorted portion.",
                        parameters=[
                            ParameterSpec("array_input", "Array (comma-separated)", ParameterType.TEXT, default="29, 10, 14, 37, 13, 2, 40, 25"),
                        ]
                    ),
                    Theorem(
                        key="insertion_sort",
                        display_name="Insertion Sort",
                        short_description="Inserts each element into its sorted place in the prefix.",
                        parameters=[
                            ParameterSpec("array_input", "Array (comma-separated)", ParameterType.TEXT, default="31, 41, 59, 26, 41, 58, 12, 35"),
                        ]
                    ),
                    Theorem(
                        key="merge_sort",
                        display_name="Merge Sort",
                        short_description="Divide-and-conquer: divides array into halves and merges.",
                        parameters=[
                            ParameterSpec("array_input", "Array (comma-separated)", ParameterType.TEXT, default="38, 27, 43, 3, 9, 82, 10, 19"),
                        ]
                    ),
                    Theorem(
                        key="quick_sort",
                        display_name="Quick Sort",
                        short_description="Partitions array around a pivot element.",
                        parameters=[
                            ParameterSpec("array_input", "Array (comma-separated)", ParameterType.TEXT, default="10, 80, 30, 90, 40, 50, 70, 20"),
                        ]
                    ),
                    Theorem(
                        key="linear_search",
                        display_name="Linear Search",
                        short_description="Sequentially scans array until target is found.",
                        parameters=[
                            ParameterSpec("array_input", "Array (comma-separated)", ParameterType.TEXT, default="15, 23, 8, 42, 16, 4, 30, 19"),
                            ParameterSpec("target", "Target Value", ParameterType.INTEGER, default=42, min_value=-9999, max_value=9999),
                        ]
                    ),
                    Theorem(
                        key="binary_search",
                        display_name="Binary Search",
                        short_description="Halves search space on sorted collection.",
                        parameters=[
                            ParameterSpec("array_input", "Array (comma-separated)", ParameterType.TEXT, default="4, 8, 15, 16, 23, 30, 42, 55, 68"),
                            ParameterSpec("target", "Target Value", ParameterType.INTEGER, default=23, min_value=-9999, max_value=9999),
                        ]
                    ),
                ]
            },
            "transformations": {
                "title": "TRANSFORMATIONS",
                "items": [
                    Theorem(
                        key="trans_translation",
                        display_name="Translation T(dx, dy)",
                        short_description="Translates 2D shape along X and Y axes using homogeneous coordinates.",
                        parameters=[
                            ParameterSpec("dx", "Translate dx", ParameterType.LENGTH, default=3.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("dy", "Translate dy", ParameterType.LENGTH, default=2.0, min_value=-20.0, max_value=20.0),
                        ]
                    ),
                    Theorem(
                        key="trans_scaling",
                        display_name="Scaling S(sx, sy)",
                        short_description="Scales 2D shape horizontally and vertically.",
                        parameters=[
                            ParameterSpec("sx", "Scale X (sx)", ParameterType.RATIO, default=1.5, min_value=0.1, max_value=5.0),
                            ParameterSpec("sy", "Scale Y (sy)", ParameterType.RATIO, default=1.5, min_value=0.1, max_value=5.0),
                        ]
                    ),
                    Theorem(
                        key="trans_rotation",
                        display_name="Rotation R(θ)",
                        short_description="Rotates 2D shape by angle θ about the origin.",
                        parameters=[
                            ParameterSpec("angle", "Rotation Angle (θ)", ParameterType.ANGLE, default=45.0, min_value=-360.0, max_value=360.0, suffix="°"),
                        ]
                    ),
                    Theorem(
                        key="trans_pivot_rotation",
                        display_name="Rotation About Arbitrary Pivot",
                        short_description="Rotates 2D shape about an arbitrary user-chosen center (cx, cy): T(cx,cy) · R(θ) · T(-cx,-cy).",
                        parameters=[
                            ParameterSpec("angle", "Rotation Angle (θ)", ParameterType.ANGLE, default=45.0, min_value=-360.0, max_value=360.0, suffix="°"),
                            ParameterSpec("cx", "Pivot X (cx)", ParameterType.LENGTH, default=2.5, min_value=-20.0, max_value=20.0),
                            ParameterSpec("cy", "Pivot Y (cy)", ParameterType.LENGTH, default=2.0, min_value=-20.0, max_value=20.0),
                        ]
                    ),
                    Theorem(
                        key="trans_reflection",
                        display_name="Reflection",
                        short_description="Reflects shape across coordinate axes or line y = x.",
                        parameters=[
                            ParameterSpec("axis", "Reflection Axis", ParameterType.CHOICE, default="X-axis", choices=["X-axis", "Y-axis", "Origin", "y = x"]),
                        ]
                    ),
                    Theorem(
                        key="trans_composite",
                        display_name="Composite (T · R · S)",
                        short_description="Multiple sequential transformations demonstrating column-vector composition order.",
                        parameters=[
                            ParameterSpec("sx", "Scale (s)", ParameterType.RATIO, default=1.3, min_value=0.2, max_value=4.0),
                            ParameterSpec("angle", "Rotate Angle", ParameterType.ANGLE, default=30.0, min_value=-360.0, max_value=360.0, suffix="°"),
                            ParameterSpec("dx", "Translate dx", ParameterType.LENGTH, default=3.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("dy", "Translate dy", ParameterType.LENGTH, default=2.0, min_value=-20.0, max_value=20.0),
                        ]
                    ),
                ]
            },
            "rasterization": {
                "title": "RASTERIZATION",
                "items": [
                    Theorem(
                        key="rast_dda",
                        display_name="DDA Line Algorithm",
                        short_description="Draws lines using floating-point increments and rounding.",
                        parameters=[
                            ParameterSpec("x0", "Start X₀", ParameterType.INTEGER, default=2, min_value=0, max_value=30),
                            ParameterSpec("y0", "Start Y₀", ParameterType.INTEGER, default=3, min_value=0, max_value=30),
                            ParameterSpec("x1", "End X₁", ParameterType.INTEGER, default=16, min_value=0, max_value=30),
                            ParameterSpec("y1", "End Y₁", ParameterType.INTEGER, default=11, min_value=0, max_value=30),
                            ParameterSpec("grid_size", "Grid Size", ParameterType.INTEGER, default=20, min_value=10, max_value=40),
                        ]
                    ),
                    Theorem(
                        key="rast_bresenham",
                        display_name="Bresenham Line Algorithm",
                        short_description="Integer-only line drawing across all 8 octants.",
                        parameters=[
                            ParameterSpec("x0", "Start X₀", ParameterType.INTEGER, default=1, min_value=0, max_value=30),
                            ParameterSpec("y0", "Start Y₀", ParameterType.INTEGER, default=2, min_value=0, max_value=30),
                            ParameterSpec("x1", "End X₁", ParameterType.INTEGER, default=18, min_value=0, max_value=30),
                            ParameterSpec("y1", "End Y₁", ParameterType.INTEGER, default=12, min_value=0, max_value=30),
                            ParameterSpec("grid_size", "Grid Size", ParameterType.INTEGER, default=20, min_value=10, max_value=40),
                        ]
                    ),
                    Theorem(
                        key="rast_midpoint_circle",
                        display_name="Midpoint Circle",
                        short_description="Rasterizes a circle with 8-way symmetry and decision parameter.",
                        parameters=[
                            ParameterSpec("center_x", "Center X", ParameterType.INTEGER, default=10, min_value=0, max_value=30),
                            ParameterSpec("center_y", "Center Y", ParameterType.INTEGER, default=10, min_value=0, max_value=30),
                            ParameterSpec("radius", "Radius (r)", ParameterType.INTEGER, default=8, min_value=1, max_value=20),
                            ParameterSpec("grid_size", "Grid Size", ParameterType.INTEGER, default=22, min_value=10, max_value=40),
                        ]
                    ),
                    Theorem(
                        key="rast_compare",
                        display_name="DDA vs Bresenham",
                        short_description="Same endpoints, two rasterizers — compare pixels and the decision pendulum.",
                        parameters=[
                            ParameterSpec("x0", "Start X₀", ParameterType.INTEGER, default=2, min_value=0, max_value=30),
                            ParameterSpec("y0", "Start Y₀", ParameterType.INTEGER, default=3, min_value=0, max_value=30),
                            ParameterSpec("x1", "End X₁", ParameterType.INTEGER, default=17, min_value=0, max_value=30),
                            ParameterSpec("y1", "End Y₁", ParameterType.INTEGER, default=11, min_value=0, max_value=30),
                            ParameterSpec("grid_size", "Grid Size", ParameterType.INTEGER, default=20, min_value=10, max_value=40),
                        ]
                    ),
                ]
            },
            "clipping": {
                "title": "CLIPPING",
                "items": [
                    Theorem(
                        key="clip_cohen_sutherland",
                        display_name="Cohen-Sutherland Line Clipping",
                        short_description="Learn the 4-bit region codes, then clip a line step by step.",
                        parameters=[
                            ParameterSpec("x1", "P1 X", ParameterType.LENGTH, default=-6.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("y1", "P1 Y", ParameterType.LENGTH, default=5.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("x2", "P2 X", ParameterType.LENGTH, default=5.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("y2", "P2 Y", ParameterType.LENGTH, default=-2.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("xmin", "Win Xmin", ParameterType.LENGTH, default=-3.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("ymin", "Win Ymin", ParameterType.LENGTH, default=-2.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("xmax", "Win Xmax", ParameterType.LENGTH, default=3.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("ymax", "Win Ymax", ParameterType.LENGTH, default=2.0, min_value=-20.0, max_value=20.0),
                        ]
                    ),
                    Theorem(
                        key="clip_sutherland_hodgman",
                        display_name="Sutherland-Hodgman Polygon Clipping",
                        short_description="Learn the four edge cases, then clip a polygon one window side at a time.",
                        parameters=[
                            ParameterSpec("polygon_shape", "Polygon Shape", ParameterType.CHOICE, default="Crossing triangle",
                                          choices=["Crossing triangle", "Diamond", "Hexagon", "Star", "Fully inside", "Fully outside"]),
                            ParameterSpec("xmin", "Win Xmin", ParameterType.LENGTH, default=-3.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("ymin", "Win Ymin", ParameterType.LENGTH, default=-2.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("xmax", "Win Xmax", ParameterType.LENGTH, default=3.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("ymax", "Win Ymax", ParameterType.LENGTH, default=2.0, min_value=-20.0, max_value=20.0),
                        ]
                    ),
                ]
            },
            "curves": {
                "title": "CURVES",
                "items": [
                    Theorem(
                        key="curve_bezier",
                        display_name="Bézier Curves — De Casteljau",
                        short_description="Repeated linear interpolation builds a point on the curve.",
                        parameters=[
                            ParameterSpec("p0x", "P0 X", ParameterType.LENGTH, default=-5.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("p0y", "P0 Y", ParameterType.LENGTH, default=-2.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("p1x", "P1 X", ParameterType.LENGTH, default=-1.5, min_value=-20.0, max_value=20.0),
                            ParameterSpec("p1y", "P1 Y", ParameterType.LENGTH, default=4.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("p2x", "P2 X", ParameterType.LENGTH, default=1.5, min_value=-20.0, max_value=20.0),
                            ParameterSpec("p2y", "P2 Y", ParameterType.LENGTH, default=-4.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("p3x", "P3 X", ParameterType.LENGTH, default=5.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("p3y", "P3 Y", ParameterType.LENGTH, default=2.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("t", "Parameter t", ParameterType.RATIO, default=0.35, min_value=0.0, max_value=1.0),
                        ]
                    ),
                    Theorem(
                        key="curve_bspline",
                        display_name="B-Spline Curves",
                        short_description="Local control through degree, knots, and Cox–de Boor bases.",
                        parameters=[
                            ParameterSpec("p0x", "P0 X", ParameterType.LENGTH, default=-5.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("p0y", "P0 Y", ParameterType.LENGTH, default=-1.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("p1x", "P1 X", ParameterType.LENGTH, default=-2.5, min_value=-20.0, max_value=20.0),
                            ParameterSpec("p1y", "P1 Y", ParameterType.LENGTH, default=3.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("p2x", "P2 X", ParameterType.LENGTH, default=0.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("p2y", "P2 Y", ParameterType.LENGTH, default=-2.5, min_value=-20.0, max_value=20.0),
                            ParameterSpec("p3x", "P3 X", ParameterType.LENGTH, default=2.5, min_value=-20.0, max_value=20.0),
                            ParameterSpec("p3y", "P3 Y", ParameterType.LENGTH, default=3.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("p4x", "P4 X", ParameterType.LENGTH, default=5.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("p4y", "P4 Y", ParameterType.LENGTH, default=-1.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("degree", "Degree", ParameterType.CHOICE, default="3 (cubic)",
                                          choices=["2 (quadratic)", "3 (cubic)"]),
                            ParameterSpec("knot_style", "Knot vector", ParameterType.CHOICE, default="Clamped uniform",
                                          choices=["Clamped uniform", "Uniform"]),
                            ParameterSpec("u", "Parameter u", ParameterType.RATIO, default=0.45, min_value=0.0, max_value=1.0),
                        ]
                    ),
                    Theorem(
                        key="curve_hermite",
                        display_name="Hermite Curves",
                        short_description="A cubic that matches two endpoints and two tangent vectors.",
                        parameters=[
                            ParameterSpec("p0x", "P0 X", ParameterType.LENGTH, default=-4.5, min_value=-20.0, max_value=20.0),
                            ParameterSpec("p0y", "P0 Y", ParameterType.LENGTH, default=-1.5, min_value=-20.0, max_value=20.0),
                            ParameterSpec("p1x", "P1 X", ParameterType.LENGTH, default=4.5, min_value=-20.0, max_value=20.0),
                            ParameterSpec("p1y", "P1 Y", ParameterType.LENGTH, default=1.5, min_value=-20.0, max_value=20.0),
                            ParameterSpec("t0x", "T0 X", ParameterType.LENGTH, default=3.5, min_value=-20.0, max_value=20.0),
                            ParameterSpec("t0y", "T0 Y", ParameterType.LENGTH, default=5.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("t1x", "T1 X", ParameterType.LENGTH, default=3.5, min_value=-20.0, max_value=20.0),
                            ParameterSpec("t1y", "T1 Y", ParameterType.LENGTH, default=-5.0, min_value=-20.0, max_value=20.0),
                            ParameterSpec("t", "Parameter t", ParameterType.RATIO, default=0.35, min_value=0.0, max_value=1.0),
                        ]
                    ),
                ]
            },
            "projections_3d": {
                "title": "3D PROJECTIONS",
                "items": [
                    Theorem(
                        key="proj_cube_persp",
                        display_name="3D Cube (Perspective)",
                        short_description="Perspective projection of a 3D wireframe cube with depth division.",
                        parameters=[
                            ParameterSpec("rx", "Rotate X", ParameterType.ANGLE, default=25.0, min_value=-360.0, max_value=360.0, suffix="°"),
                            ParameterSpec("ry", "Rotate Y", ParameterType.ANGLE, default=35.0, min_value=-360.0, max_value=360.0, suffix="°"),
                            ParameterSpec("rz", "Rotate Z", ParameterType.ANGLE, default=0.0, min_value=-360.0, max_value=360.0, suffix="°"),
                            ParameterSpec("tx", "Translate X", ParameterType.LENGTH, default=0.0, min_value=-10.0, max_value=10.0),
                            ParameterSpec("ty", "Translate Y", ParameterType.LENGTH, default=0.0, min_value=-10.0, max_value=10.0),
                            ParameterSpec("tz", "Translate Z", ParameterType.LENGTH, default=0.0, min_value=-10.0, max_value=10.0),
                            ParameterSpec("sx", "Scale X", ParameterType.RATIO, default=1.0, min_value=0.1, max_value=5.0),
                            ParameterSpec("sy", "Scale Y", ParameterType.RATIO, default=1.0, min_value=0.1, max_value=5.0),
                            ParameterSpec("sz", "Scale Z", ParameterType.RATIO, default=1.0, min_value=0.1, max_value=5.0),
                            ParameterSpec("camera_dist", "Camera Distance", ParameterType.LENGTH, default=7.0, min_value=3.0, max_value=25.0),
                            ParameterSpec("focal_dist", "Focal Distance", ParameterType.LENGTH, default=4.5, min_value=1.0, max_value=15.0),
                        ]
                    ),
                    Theorem(
                        key="proj_cube_ortho",
                        display_name="3D Cube (Orthographic)",
                        short_description="Parallel orthographic projection of a 3D wireframe cube.",
                        parameters=[
                            ParameterSpec("rx", "Rotate X", ParameterType.ANGLE, default=30.0, min_value=-360.0, max_value=360.0, suffix="°"),
                            ParameterSpec("ry", "Rotate Y", ParameterType.ANGLE, default=45.0, min_value=-360.0, max_value=360.0, suffix="°"),
                            ParameterSpec("rz", "Rotate Z", ParameterType.ANGLE, default=0.0, min_value=-360.0, max_value=360.0, suffix="°"),
                            ParameterSpec("tx", "Translate X", ParameterType.LENGTH, default=0.0, min_value=-10.0, max_value=10.0),
                            ParameterSpec("ty", "Translate Y", ParameterType.LENGTH, default=0.0, min_value=-10.0, max_value=10.0),
                            ParameterSpec("tz", "Translate Z", ParameterType.LENGTH, default=0.0, min_value=-10.0, max_value=10.0),
                            ParameterSpec("sx", "Scale X", ParameterType.RATIO, default=1.0, min_value=0.1, max_value=5.0),
                            ParameterSpec("sy", "Scale Y", ParameterType.RATIO, default=1.0, min_value=0.1, max_value=5.0),
                            ParameterSpec("sz", "Scale Z", ParameterType.RATIO, default=1.0, min_value=0.1, max_value=5.0),
                        ]
                    ),
                    Theorem(
                        key="proj_pyramid",
                        display_name="3D Pyramid (Perspective)",
                        short_description="Perspective projection of a 3D square-based pyramid.",
                        parameters=[
                            ParameterSpec("rx", "Rotate X", ParameterType.ANGLE, default=20.0, min_value=-360.0, max_value=360.0, suffix="°"),
                            ParameterSpec("ry", "Rotate Y", ParameterType.ANGLE, default=40.0, min_value=-360.0, max_value=360.0, suffix="°"),
                            ParameterSpec("rz", "Rotate Z", ParameterType.ANGLE, default=0.0, min_value=-360.0, max_value=360.0, suffix="°"),
                            ParameterSpec("tx", "Translate X", ParameterType.LENGTH, default=0.0, min_value=-10.0, max_value=10.0),
                            ParameterSpec("ty", "Translate Y", ParameterType.LENGTH, default=0.0, min_value=-10.0, max_value=10.0),
                            ParameterSpec("tz", "Translate Z", ParameterType.LENGTH, default=0.0, min_value=-10.0, max_value=10.0),
                            ParameterSpec("sx", "Scale X", ParameterType.RATIO, default=1.0, min_value=0.1, max_value=5.0),
                            ParameterSpec("sy", "Scale Y", ParameterType.RATIO, default=1.0, min_value=0.1, max_value=5.0),
                            ParameterSpec("sz", "Scale Z", ParameterType.RATIO, default=1.0, min_value=0.1, max_value=5.0),
                            ParameterSpec("camera_dist", "Camera Distance", ParameterType.LENGTH, default=7.0, min_value=3.0, max_value=25.0),
                            ParameterSpec("focal_dist", "Focal Distance", ParameterType.LENGTH, default=4.5, min_value=1.0, max_value=15.0),
                        ]
                    ),
                ]
            }
        }

    # ------------------------------------------------------------------
    # Signal Wiring
    # ------------------------------------------------------------------
    def _wire_signals(self):
        w = self.window
        w.moduleSelected.connect(self.on_module_selected)
        if hasattr(w, "homeRequested"):
            w.homeRequested.connect(self.on_home_requested)
        w.theorem_panel.theoremSelected.connect(self.on_topic_selected)
        w.parameter_panel.parametersApplied.connect(self.on_parameters_applied)

        w.animation_controls.previousClicked.connect(self.on_previous_step)
        w.animation_controls.playPauseClicked.connect(self.on_play_pause)
        w.animation_controls.nextClicked.connect(self.on_next_step)
        w.animation_controls.replayClicked.connect(self.on_replay)
        w.animation_controls.speedChanged.connect(self.on_speed_changed)
        w.animation_controls.stepSelected.connect(self.on_step_selected)

        w.view_controls.zoomInClicked.connect(self.on_zoom_in)
        w.view_controls.zoomOutClicked.connect(self.on_zoom_out)
        w.view_controls.resetViewClicked.connect(self.on_reset_view)
        w.view_controls.panRequested.connect(self.on_pan_requested)
        w.view_controls.gridToggled.connect(self.on_grid_toggled)

        w.visualization_widget.clippingEndpointDragged.connect(self.on_clipping_endpoint_dragged)
        w.visualization_widget.clippingRegionClicked.connect(self.on_clipping_region_clicked)
        w.visualization_widget.curveHandleDragged.connect(self.on_curve_handle_dragged)
        if hasattr(w, "clipping_tab_bar"):
            w.clipping_tab_bar.tabChanged.connect(self.on_clipping_tab_changed)
        if hasattr(w.parameter_panel, "curveTChanged"):
            w.parameter_panel.curveTChanged.connect(self.on_curve_t_changed)

    # ------------------------------------------------------------------
    # Module & Topic Selection
    # ------------------------------------------------------------------
    def on_home_requested(self):
        self._stop_playback()
        if self.current_module == "playground":
            self.current_module = self.window._last_lesson_module or "algorithms"

    def on_module_selected(self, module_key: str):
        self._stop_playback()
        self.current_module = module_key

        if module_key != "playground" and hasattr(self.window, "select_module"):
            self.window.select_module(module_key)

        if module_key == "playground":
            if hasattr(self.window, "show_playground"):
                self.window.show_playground()
            self.window.set_status("Studio — not a lesson. Draw, transform, and watch the matrix follow.")
            return

        if hasattr(self.window, "show_lessons"):
            self.window.show_lessons()

        mod_info = self._catalog.get(module_key)
        if not mod_info:
            return

        # Dual renderer selection: 3D Projections uses OpenGL, others use QPainter
        if module_key == "projections_3d":
            self.window.set_active_renderer("opengl")
        else:
            self.window.set_active_renderer("2d")

        # Toggle Zoom controls: hidden in algorithms section, visible in all others
        is_algorithms = (module_key == "algorithms")
        if hasattr(self.window, "set_zoom_controls_visible"):
            self.window.set_zoom_controls_visible(not is_algorithms)
        elif hasattr(self.window, "view_controls") and hasattr(self.window.view_controls, "set_zoom_controls_visible"):
            self.window.view_controls.set_zoom_controls_visible(not is_algorithms)

        if is_algorithms and hasattr(self.window, "visualization_widget"):
            self.window.visualization_widget.reset_view()

        items = mod_info["items"]
        self.window.theorem_panel.set_items(items, title=mod_info["title"])
        if items:
            first_key = items[0].key
            self.window.theorem_panel.select_theorem(first_key)

    def on_topic_selected(self, topic_key: str):
        self._stop_playback()
        self.current_topic_key = topic_key
        mod_info = self._catalog[self.current_module]
        item = next((it for it in mod_info["items"] if it.key == topic_key), None)
        if not item:
            return

        if self.current_module == "projections_3d":
            if topic_key == "proj_cube_persp":
                self.window.opengl_widget.set_object_type("cube")
                self.window.opengl_widget.set_projection_mode("perspective")
            elif topic_key == "proj_cube_ortho":
                self.window.opengl_widget.set_object_type("cube")
                self.window.opengl_widget.set_projection_mode("orthographic")
            elif topic_key == "proj_pyramid":
                self.window.opengl_widget.set_object_type("pyramid")
                self.window.opengl_widget.set_projection_mode("perspective")

        self.window.parameter_panel.set_theorem(item)
        self.window.visualization_widget.set_theorem(topic_key, item.display_name)
        self.window.animation_controls.set_enabled_all(True)
        self.window.equation_panel.clear()

        self.window.set_status(f"Loaded: {item.display_name} — {item.short_description}")
        self.theoremChanged.emit(topic_key)

        # Toggle Zoom controls: hidden in algorithms section
        is_algorithms = (self.current_module == "algorithms")
        if hasattr(self.window, "set_zoom_controls_visible"):
            self.window.set_zoom_controls_visible(not is_algorithms)
        elif hasattr(self.window, "view_controls") and hasattr(self.window.view_controls, "set_zoom_controls_visible"):
            self.window.view_controls.set_zoom_controls_visible(not is_algorithms)

        # Toggle Animated Sorting Playground Style Controls
        is_sorting = (self.current_module == "algorithms" and topic_key in (
            "bubble_sort", "selection_sort", "insertion_sort", "merge_sort", "quick_sort"
        ))
        if hasattr(self.window, "set_sorting_controls_visible"):
            self.window.set_sorting_controls_visible(is_sorting)

        # Toggle lesson tabs for clipping and curves
        is_cohen = (topic_key == "clip_cohen_sutherland")
        is_hodgman = (topic_key == "clip_sutherland_hodgman")
        is_curve = topic_key in ("curve_bezier", "curve_bspline", "curve_hermite")
        if hasattr(self.window, "set_clipping_tabs_visible"):
            self.window.set_clipping_tabs_visible(is_cohen or is_hodgman or is_curve)
            if hasattr(self.window, "clipping_tab_bar"):
                from ui.clipping_tabs import COHEN_TABS, HODGMAN_TABS
                if is_cohen:
                    self.window.clipping_tab_bar.set_tabs(COHEN_TABS, "region_codes")
                elif is_hodgman:
                    self.window.clipping_tab_bar.set_tabs(HODGMAN_TABS, "four_cases")
                elif is_curve:
                    self.window.clipping_tab_bar.set_tabs(
                        cgip_curves.tabs_for_topic(topic_key),
                        cgip_curves.default_tab(topic_key),
                    )
            if hasattr(self.window.parameter_panel, "set_clipping_lesson_tab"):
                if is_cohen:
                    self.window.parameter_panel.set_clipping_lesson_tab("region_codes")
                elif is_hodgman:
                    self.window.parameter_panel.set_clipping_lesson_tab("four_cases")
                else:
                    self.window.parameter_panel.set_clipping_lesson_tab("")
            if hasattr(self.window.parameter_panel, "set_curve_lesson_tab"):
                if is_curve:
                    self.window.parameter_panel.set_curve_lesson_tab(
                        topic_key, cgip_curves.default_tab(topic_key)
                    )
                else:
                    self.window.parameter_panel.set_curve_lesson_tab("", "")

        # Apply default parameters
        defaults = {p.key: p.default for p in item.parameters}
        self.on_parameters_applied(defaults)

    # ------------------------------------------------------------------
    # Parameters Application & Trace Generation
    # ------------------------------------------------------------------
    def on_parameters_applied(self, values: dict):
        self._stop_playback()
        self.current_parameters = values

        # Synchronize parameters with OpenGL 3D renderer when active
        if self.current_module == "projections_3d" and hasattr(self.window, "opengl_widget"):
            self.window.opengl_widget.update_from_parameters(values)

        try:
            steps = self._generate_steps_for_topic(self.current_topic_key, values)
            self.current_steps = steps
            self.current_step_index = 0
            self.window.parameter_panel.clear_validation_error()
            self._render_current_step()
            self.window.set_status(f"Generated {len(steps)} steps for {self.current_topic_key}")
        except Exception as e:
            err_msg = str(e)
            self.window.parameter_panel.show_validation_error(err_msg)
            self.window.set_status(f"Validation Error: {err_msg}")

    def _generate_steps_for_topic(self, key: str, values: dict) -> List[Any]:
        # 1. Theorems
        if self.current_module == "theorems":
            ok, msg = self.theorem_engine.validate_parameters(key, values)
            if not ok:
                raise ValueError(msg)
            return self.theorem_engine.generate_steps(key, values)

        # 2. Algorithms
        elif self.current_module == "algorithms":
            # Parse array
            raw_arr = values.get("array_input", "10, 5, 20, 8")
            try:
                arr = [int(x.strip()) for x in str(raw_arr).split(",") if x.strip()]
            except ValueError:
                raise ValueError("Array must be comma-separated integers (e.g. 15, 8, 42, 23).")
            if not arr:
                raise ValueError("Array cannot be empty.")

            if key in ("bubble_sort", "selection_sort", "insertion_sort", "merge_sort", "quick_sort"):
                return AlgorithmEngine.run_sorting(key, arr)
            elif key in ("linear_search", "binary_search"):
                target = int(values.get("target", 23))
                return AlgorithmEngine.run_searching(key, arr, target)

        # 3. Transformations
        elif self.current_module == "transformations":
            if key == "trans_translation":
                dx = float(values.get("dx", 3.0))
                dy = float(values.get("dy", 2.0))
                return cgip_trans.generate_transformation_demo("triangle", [{"type": "translate", "dx": dx, "dy": dy}])
            elif key == "trans_scaling":
                sx = float(values.get("sx", 1.5))
                sy = float(values.get("sy", 1.5))
                return cgip_trans.generate_transformation_demo("rectangle", [{"type": "scale", "sx": sx, "sy": sy}])
            elif key == "trans_rotation":
                ang = float(values.get("angle", 45.0))
                return cgip_trans.generate_transformation_demo("triangle", [{"type": "rotate", "angle": ang}])
            elif key == "trans_pivot_rotation":
                ang = float(values.get("angle", 45.0))
                cx = float(values.get("cx", 2.5))
                cy = float(values.get("cy", 2.0))
                return cgip_trans.generate_transformation_demo("triangle", [{"type": "rotate", "angle": ang, "cx": cx, "cy": cy}])
            elif key == "trans_reflection":
                axis = str(values.get("axis", "X-axis"))
                return cgip_trans.generate_transformation_demo("triangle", [{"type": "reflect", "axis": axis}])
            elif key == "trans_composite":
                sx = float(values.get("sx", 1.3))
                ang = float(values.get("angle", 30.0))
                dx = float(values.get("dx", 3.0))
                dy = float(values.get("dy", 2.0))
                return cgip_trans.generate_transformation_demo("triangle", [
                    {"type": "scale", "sx": sx, "sy": sx},
                    {"type": "rotate", "angle": ang},
                    {"type": "translate", "dx": dx, "dy": dy},
                ])
            elif key == "trans_w2v":
                xw_min = float(values.get("xw_min", -5.0))
                xw_max = float(values.get("xw_max", 5.0))
                yw_min = float(values.get("yw_min", -5.0))
                yw_max = float(values.get("yw_max", 5.0))
                if xw_max <= xw_min or yw_max <= yw_min:
                    raise ValueError("World Window Max values must be greater than Min values.")
                return cgip_trans.window_to_viewport_trace((xw_min, yw_min), (xw_max, yw_max))

        # 4. Rasterization
        elif self.current_module == "rasterization":
            if key == "rast_dda":
                x0 = int(values.get("x0", 2))
                y0 = int(values.get("y0", 3))
                x1 = int(values.get("x1", 16))
                y1 = int(values.get("y1", 11))
                gs = int(values.get("grid_size", 20))
                return cgip_rast.dda_line_trace(x0, y0, x1, y1, grid_size=gs)
            elif key == "rast_bresenham":
                x0 = int(values.get("x0", 1))
                y0 = int(values.get("y0", 2))
                x1 = int(values.get("x1", 18))
                y1 = int(values.get("y1", 12))
                gs = int(values.get("grid_size", 20))
                return cgip_rast.bresenham_line_trace(x0, y0, x1, y1, grid_size=gs)
            elif key == "rast_midpoint_circle":
                cx = int(values.get("center_x", 10))
                cy = int(values.get("center_y", 10))
                r = int(values.get("radius", 8))
                gs = int(values.get("grid_size", 22))
                if r <= 0:
                    raise ValueError("Radius must be greater than 0.")
                return cgip_rast.midpoint_circle_trace(cx, cy, r, grid_size=gs)
            elif key == "rast_compare":
                x0 = int(values.get("x0", 2))
                y0 = int(values.get("y0", 3))
                x1 = int(values.get("x1", 17))
                y1 = int(values.get("y1", 11))
                gs = int(values.get("grid_size", 20))
                return cgip_rast.dda_vs_bresenham_comparison_trace(x0, y0, x1, y1, grid_size=gs)

        # 5. Clipping
        elif self.current_module == "clipping":
            xmin = float(values.get("xmin", -3.0))
            ymin = float(values.get("ymin", -2.0))
            xmax = float(values.get("xmax", 3.0))
            ymax = float(values.get("ymax", 2.0))
            if xmax <= xmin or ymax <= ymin:
                raise ValueError("Clipping window coordinates must have xmax > xmin and ymax > ymin.")

            if key == "clip_sutherland_hodgman":
                tab = "clip_polygon"
                if hasattr(self.window, "clipping_tab_bar"):
                    tab = self.window.clipping_tab_bar.current_tab()
                if tab == "four_cases":
                    return cgip_clip.build_polygon_cases_steps(xmin, ymin, xmax, ymax)
                shape = str(values.get("polygon_shape", "triangle"))
                poly = cgip_clip.get_polygon_shape(shape)
                return cgip_clip.sutherland_hodgman_trace(poly, xmin, ymin, xmax, ymax)
            else:
                tab = "clip_line"
                if hasattr(self.window, "clipping_tab_bar"):
                    tab = self.window.clipping_tab_bar.current_tab()
                if tab == "region_codes":
                    return cgip_clip.build_region_codes_steps(
                        xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax
                    )
                x1 = float(values.get("x1", -6.0))
                y1 = float(values.get("y1", 5.0))
                x2 = float(values.get("x2", 5.0))
                y2 = float(values.get("y2", -2.0))
                return cgip_clip.cohen_sutherland_trace(x1, y1, x2, y2, xmin, ymin, xmax, ymax)

        # 6. Curves & Geometric Modelling
        elif self.current_module == "curves":
            tab = ""
            if hasattr(self.window, "clipping_tab_bar"):
                tab = self.window.clipping_tab_bar.current_tab()
            return cgip_curves.generate_curve_steps(key, values, tab)

        # 7. 3D Projections
        elif self.current_module == "projections_3d":
            rx = float(values.get("rx", 25.0))
            ry = float(values.get("ry", 35.0))
            rz = float(values.get("rz", 0.0))
            tx = float(values.get("tx", 0.0))
            ty = float(values.get("ty", 0.0))
            tz = float(values.get("tz", 0.0))
            sx = float(values.get("sx", 1.0))
            sy = float(values.get("sy", 1.0))
            sz = float(values.get("sz", 1.0))
            cam_dist = float(values.get("camera_dist", 7.0))
            focal_dist = float(values.get("focal_dist", 4.5))

            if key == "proj_cube_persp":
                return cgip_3d.generate_3d_demo("cube", "perspective", rx, ry, rz, focal_dist, cam_dist, tx=tx, ty=ty, tz=tz, sx=sx, sy=sy, sz=sz)
            elif key == "proj_cube_ortho":
                return cgip_3d.generate_3d_demo("cube", "orthographic", rx, ry, rz, tx=tx, ty=ty, tz=tz, sx=sx, sy=sy, sz=sz)
            elif key == "proj_pyramid":
                return cgip_3d.generate_3d_demo("pyramid", "perspective", rx, ry, rz, focal_dist, cam_dist, tx=tx, ty=ty, tz=tz, sx=sx, sy=sy, sz=sz)

        return []

    # ------------------------------------------------------------------
    # Step Rendering & Transport
    # ------------------------------------------------------------------
    def _render_current_step(self):
        total = len(self.current_steps)
        if total == 0:
            self.window.equation_panel.clear()
            self.window.visualization_widget.clear()
            self.window.animation_controls.set_progress(0, 1)
            self.window.animation_controls.set_step_buttons_enabled(False, False)
            return

        idx = max(0, min(self.current_step_index, total - 1))
        step = self.current_steps[idx]

        step_idx_1based = getattr(step, "index", idx + 1)
        title = getattr(step, "title", "")
        eq = getattr(step, "equation", "")
        expl = getattr(step, "explanation", "")
        vals = getattr(step, "values", {})
        rd = getattr(step, "render_data", None)
        metrics = getattr(step, "metrics", {})

        self.window.equation_panel.display_step(
            step_idx_1based, total, eq, expl, metrics=metrics, title=title
        )
        self.window.visualization_widget.update_step(idx, vals, render_data=rd)
        self.window.animation_controls.set_progress(idx + 1, total)
        self.window.animation_controls.set_step_buttons_enabled(
            prev_enabled=idx > 0, next_enabled=idx < total - 1
        )
        self.stepChanged.emit(idx, total)

        # Update live lesson card for clipping and curve topics
        if self.current_topic_key in ("clip_cohen_sutherland", "clip_sutherland_hodgman"):
            tab = ""
            if hasattr(self.window, "clipping_tab_bar"):
                tab = self.window.clipping_tab_bar.current_tab()
            if hasattr(self.window.parameter_panel, "set_clipping_lesson_tab"):
                self.window.parameter_panel.set_clipping_lesson_tab(tab)
            self.window.parameter_panel.update_clipping_walkthrough(vals)
        elif self.current_topic_key in ("curve_bezier", "curve_bspline", "curve_hermite"):
            tab = ""
            if hasattr(self.window, "clipping_tab_bar"):
                tab = self.window.clipping_tab_bar.current_tab()
            if hasattr(self.window.parameter_panel, "set_curve_lesson_tab"):
                self.window.parameter_panel.set_curve_lesson_tab(self.current_topic_key, tab)
            if hasattr(self.window.parameter_panel, "update_curve_walkthrough"):
                self.window.parameter_panel.update_curve_walkthrough(vals)

        # If on the last step of a theorem or clipping, show verified result
        if idx == total - 1 and self.current_module == "theorems":
            res = self.theorem_engine.compute_final_result(self.current_topic_key, self.current_parameters)
            self.window.equation_panel.display_result(res)
        elif idx == total - 1 and self.current_topic_key == "clip_cohen_sutherland":
            seg = vals.get("accepted_segment")
            if seg:
                self.window.equation_panel.display_result(
                    f"Accepted: Line clipped to ({seg[0][0]:.2f}, {seg[0][1]:.2f}) → ({seg[1][0]:.2f}, {seg[1][1]:.2f})"
                )
            else:
                self.window.equation_panel.display_result("Rejected: Line segment lies entirely outside clipping window")
        elif idx == total - 1 and self.current_topic_key == "clip_sutherland_hodgman":
            verts = vals.get("accepted_polygon") or vals.get("final_vertices")
            if vals.get("status") == "accepted" and verts:
                self.window.equation_panel.display_result(
                    f"Accepted: clipped polygon with {len(verts)} vertices"
                )
            elif vals.get("status") == "rejected":
                self.window.equation_panel.display_result("Rejected: polygon lies entirely outside the clipping window")
        elif self.current_topic_key in ("curve_bezier", "curve_bspline", "curve_hermite"):
            pt = vals.get("curve_point")
            param = vals.get("t", vals.get("u"))
            if pt and (idx >= 1 or idx == total - 1):
                self.window.equation_panel.display_result(
                    f"C({float(param):.2f}) = ({pt[0]:.2f}, {pt[1]:.2f})"
                )

    def on_clipping_endpoint_dragged(self, target: str, x: float, y: float):
        """Handle real-time endpoint dragging on the canvas."""
        if self.current_topic_key != "clip_cohen_sutherland":
            return
        if hasattr(self.window, "clipping_tab_bar") and self.window.clipping_tab_bar.current_tab() != "clip_line":
            return
        if target == "P1":
            self.current_parameters["x1"] = x
            self.current_parameters["y1"] = y
            self.window.parameter_panel.set_input_value("x1", x)
            self.window.parameter_panel.set_input_value("y1", y)
        elif target == "P2":
            self.current_parameters["x2"] = x
            self.current_parameters["y2"] = y
            self.window.parameter_panel.set_input_value("x2", x)
            self.window.parameter_panel.set_input_value("y2", y)

        self._stop_playback()
        self.current_steps = self._generate_steps_for_topic(self.current_topic_key, self.current_parameters)
        self.current_step_index = min(self.current_step_index, max(0, len(self.current_steps) - 1))
        self._render_current_step()

    def on_clipping_tab_changed(self, tab_key: str):
        """Switch lesson tabs for clipping or curve topics."""
        if self.current_topic_key in ("curve_bezier", "curve_bspline", "curve_hermite"):
            if hasattr(self.window, "clipping_tab_bar"):
                self.window.clipping_tab_bar.set_current_tab(tab_key, emit_signal=False)
            self._stop_playback()
            try:
                self.current_steps = cgip_curves.generate_curve_steps(
                    self.current_topic_key, self.current_parameters, tab_key
                )
                self.window.parameter_panel.clear_validation_error()
            except Exception as e:
                self.window.parameter_panel.show_validation_error(str(e))
                return
            if hasattr(self.window.parameter_panel, "set_curve_lesson_tab"):
                self.window.parameter_panel.set_curve_lesson_tab(self.current_topic_key, tab_key)
            self.current_step_index = 0
            self._render_current_step()
            return
        if self.current_topic_key not in ("clip_cohen_sutherland", "clip_sutherland_hodgman"):
            return
        if hasattr(self.window, "clipping_tab_bar"):
            self.window.clipping_tab_bar.set_current_tab(tab_key, emit_signal=False)
        self._stop_playback()
        p = self.current_parameters
        xmin = float(p.get("xmin", -3.0))
        ymin = float(p.get("ymin", -2.0))
        xmax = float(p.get("xmax", 3.0))
        ymax = float(p.get("ymax", 2.0))
        if self.current_topic_key == "clip_cohen_sutherland":
            if tab_key == "region_codes":
                self.current_steps = cgip_clip.build_region_codes_steps(
                    xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax
                )
            else:
                self.current_steps = cgip_clip.cohen_sutherland_trace(
                    float(p.get("x1", -6.0)), float(p.get("y1", 5.0)),
                    float(p.get("x2", 5.0)), float(p.get("y2", -2.0)),
                    xmin, ymin, xmax, ymax,
                )
        else:
            if tab_key == "four_cases":
                self.current_steps = cgip_clip.build_polygon_cases_steps(xmin, ymin, xmax, ymax)
            else:
                poly = cgip_clip.get_polygon_shape(str(p.get("polygon_shape", "triangle")))
                self.current_steps = cgip_clip.sutherland_hodgman_trace(poly, xmin, ymin, xmax, ymax)
        if hasattr(self.window.parameter_panel, "set_clipping_lesson_tab"):
            self.window.parameter_panel.set_clipping_lesson_tab(tab_key)
        self.current_step_index = 0
        self._render_current_step()

    def on_clipping_region_clicked(self, code: int, name: str):
        """Jump to the matching region-code lesson step when the canvas is clicked."""
        if self.current_topic_key != "clip_cohen_sutherland":
            return
        if not hasattr(self.window, "clipping_tab_bar"):
            return
        if self.window.clipping_tab_bar.current_tab() != "region_codes":
            return
        p = self.current_parameters
        self.current_steps = cgip_clip.build_region_codes_steps(
            xmin=float(p.get("xmin", -3.0)),
            ymin=float(p.get("ymin", -2.0)),
            xmax=float(p.get("xmax", 3.0)),
            ymax=float(p.get("ymax", 2.0)),
        )
        for idx, s in enumerate(self.current_steps):
            if s.values.get("lesson") == "region" and s.values.get("active_code") == code:
                self.current_step_index = idx
                break
        self._render_current_step()

    def on_curve_handle_dragged(self, handle: str, x: float, y: float):
        """Live-update a control point or Hermite tangent from canvas dragging."""
        if self.current_topic_key not in ("curve_bezier", "curve_bspline", "curve_hermite"):
            return
        p = self.current_parameters
        if handle in ("T0", "T1"):
            origin_key = "p0" if handle == "T0" else "p1"
            p[f"{handle.lower()}x"] = x - float(p.get(f"{origin_key}x", 0.0))
            p[f"{handle.lower()}y"] = y - float(p.get(f"{origin_key}y", 0.0))
            self.window.parameter_panel.set_input_value(f"{handle.lower()}x", p[f"{handle.lower()}x"])
            self.window.parameter_panel.set_input_value(f"{handle.lower()}y", p[f"{handle.lower()}y"])
        elif handle.startswith("P") and handle[1:].isdigit():
            idx = handle[1:]
            p[f"p{idx}x"] = x
            p[f"p{idx}y"] = y
            self.window.parameter_panel.set_input_value(f"p{idx}x", x)
            self.window.parameter_panel.set_input_value(f"p{idx}y", y)
        else:
            return

        self._stop_playback()
        tab = ""
        if hasattr(self.window, "clipping_tab_bar"):
            tab = self.window.clipping_tab_bar.current_tab()
        self.current_steps = cgip_curves.generate_curve_steps(self.current_topic_key, p, tab)
        self.current_step_index = min(self.current_step_index, max(0, len(self.current_steps) - 1))
        self._render_current_step()

    def on_curve_t_changed(self, value: float):
        """Seek the parameter slider without resetting the lesson."""
        if self.current_topic_key not in ("curve_bezier", "curve_bspline", "curve_hermite"):
            return
        key = "u" if self.current_topic_key == "curve_bspline" else "t"
        self.current_parameters[key] = float(value)
        self.window.parameter_panel.set_input_value(key, float(value))
        tab = ""
        if hasattr(self.window, "clipping_tab_bar"):
            tab = self.window.clipping_tab_bar.current_tab()

        if tab == "experiment" and self.current_steps:
            best = min(
                range(len(self.current_steps)),
                key=lambda i: abs(float(self.current_steps[i].values.get(key, self.current_steps[i].values.get("t", 0.0))) - value),
            )
            self.current_step_index = best
            self._render_current_step()
            return

        self._stop_playback()
        self.current_steps = cgip_curves.generate_curve_steps(
            self.current_topic_key, self.current_parameters, tab
        )
        self.current_step_index = min(self.current_step_index, max(0, len(self.current_steps) - 1))
        self._render_current_step()

    def on_step_selected(self, step_index: int):
        self._stop_playback()
        if 0 <= step_index < len(self.current_steps):
            self.current_step_index = step_index
            self._render_current_step()

    def on_previous_step(self):
        self._stop_playback()
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self._render_current_step()

    def on_next_step(self):
        self._stop_playback()
        self._go_to_next_step_or_finish()

    def on_play_pause(self):
        if self.is_playing:
            self._stop_playback()
        else:
            self._start_playback()

    def on_replay(self):
        self._stop_playback()
        self.current_step_index = 0
        self._render_current_step()
        self._start_playback()

    def on_speed_changed(self, multiplier: float):
        self.speed_multiplier = multiplier
        if self._timer.isActive():
            self._timer.setInterval(self._playback_interval_ms())
        if hasattr(self.window.visualization_widget, "set_sorting_duration"):
            self.window.visualization_widget.set_sorting_duration(int(450 / max(0.2, multiplier)))

    def _playback_interval_ms(self) -> int:
        viz = getattr(self.window, "visualization_widget", None)
        if viz and hasattr(viz, "playback_interval_ms"):
            return max(350, viz.playback_interval_ms(self.speed_multiplier))
        return int(self.BASE_TICK_MS / max(0.25, self.speed_multiplier))

    def _start_playback(self):
        total = len(self.current_steps)
        if total <= 1:
            return
        if self.current_step_index >= total - 1:
            self.current_step_index = 0
            self._render_current_step()

        self.is_playing = True
        self.window.animation_controls.set_playing(True)
        self._timer.start(self._playback_interval_ms())
        self.playbackStateChanged.emit(True)

    def _stop_playback(self):
        self._timer.stop()
        self.is_playing = False
        self.window.animation_controls.set_playing(False)
        self.playbackStateChanged.emit(False)

    def _advance_step_from_timer(self):
        self._go_to_next_step_or_finish(auto=True)

    def _go_to_next_step_or_finish(self, auto: bool = False):
        total = len(self.current_steps)
        if self.current_step_index < total - 1:
            self.current_step_index += 1
            self._render_current_step()
            if auto and self.is_playing:
                self._timer.start(self._playback_interval_ms())
        else:
            if auto:
                self._stop_playback()

    # ------------------------------------------------------------------
    # View Navigation (Zoom, Pan, Reset)
    # ------------------------------------------------------------------
    def on_zoom_in(self):
        if self.current_module == "algorithms":
            return
        if self.current_module == "projections_3d" and hasattr(self.window, "opengl_widget"):
            self.window.opengl_widget.zoom_in()
        else:
            self.window.visualization_widget.set_zoom(
                self.window.visualization_widget._zoom * 1.2
            )

    def on_zoom_out(self):
        if self.current_module == "algorithms":
            return
        if self.current_module == "projections_3d" and hasattr(self.window, "opengl_widget"):
            self.window.opengl_widget.zoom_out()
        else:
            self.window.visualization_widget.set_zoom(
                self.window.visualization_widget._zoom / 1.2
            )

    def on_reset_view(self):
        if self.current_module == "projections_3d" and hasattr(self.window, "opengl_widget"):
            self.window.opengl_widget.reset_view()
        else:
            self.window.visualization_widget.reset_view()

    def on_pan_requested(self, dx: float, dy: float):
        if self.current_module == "projections_3d" and hasattr(self.window, "opengl_widget"):
            self.window.opengl_widget.pan(dx, dy)
        else:
            self.window.visualization_widget.set_pan(dx, dy)

    def on_grid_toggled(self, checked: bool):
        if hasattr(self.window, "opengl_widget"):
            self.window.opengl_widget.set_show_grid(checked)
