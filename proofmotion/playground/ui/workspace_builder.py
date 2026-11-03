"""
playground/ui/workspace_builder.py
----------------------------------
Studio Proof Builder Workspace:
Enables users to author, customize, and present step-by-step mathematical proofs
of any theorem.

Features:
  - Multi-step proof management (Add, Duplicate, Delete, Reorder, Copy from Previous)
  - Geometric & mathematical shape tools (Points, Lines, Polygons, Angles, Circles, Math Labels)
  - Interactive canvas with vertex dragging, snap-to-grid, and coordinate inspection
  - Pedagogical step editor (Title, Equation with math symbol picker, Caption/Explanation)
  - Instant prebuilt starter templates (Pythagorean Theorem, Triangle Angle Sum,
    Thales's Theorem, Exterior Angle Theorem, Triangle Area, Blank Canvas)
  - JSON save & load
  - Built-in Learn Presentation View: Renders the custom proof IDENTICALLY to the prebuilt
    proofs in the Learn section using VisualizationWidget, EquationPanel, and AnimationControls.
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget,
    QListWidget, QListWidgetItem, QLineEdit, QTextEdit, QComboBox, QCheckBox,
    QDoubleSpinBox, QSpinBox, QSplitter, QFrame, QMenu, QAction, QFileDialog,
    QMessageBox, QTabWidget, QGraphicsDropShadowEffect, QSizePolicy, QToolButton
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QIcon, QColor, QFont

from playground.proof_builder_model import (
    BuilderProof, BuilderProofStep, BuilderShape, ShapeType
)
from playground.proof_templates import get_template_catalog
from playground.ui.builder_canvas import BuilderCanvas
from graphics.visualization_widget import VisualizationWidget
from ui.equation_panel import EquationPanel
from ui.animation_controls import AnimationControls
from resources.theme import COLORS, get_mono_font, get_ui_font


MATH_SYMBOLS = ["²", "³", "√", "∠", "°", "⊥", "∥", "Δ", "π", "θ", "α", "β", "⟹", "≅", "±", "½", "·", "×"]

COLOR_PALETTE = [
    ("#6C5CE7", "Purple"),
    ("#5EEAD4", "Teal"),
    ("#5B8DEF", "Blue"),
    ("#2F9E78", "Green"),
    ("#F59E0B", "Gold"),
    ("#EC4899", "Pink"),
    ("#EAF0F6", "White"),
    ("#D65362", "Coral"),
]


class WorkspaceBuilder(QWidget):
    statusMessage = pyqtSignal(str)
    fullscreenToggled = pyqtSignal(bool)

    BASE_TICK_MS = 1500

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StudioStage")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self._templates = get_template_catalog()
        # Default starting proof: Pythagorean Theorem
        self._proof: BuilderProof = self._templates["pythagorean"]
        self._active_step_idx = 0
        self._is_presenting = False

        # Playback timer for Learn Presentation Mode
        self._play_timer = QTimer(self)
        self._play_timer.timeout.connect(self._on_play_tick)
        self._speed_multiplier = 1.0
        self._updating_inspector = False

        self._init_ui()
        self._load_proof_into_editor(self._proof)

    # ------------------------------------------------------------------
    # UI Layout Construction
    # ------------------------------------------------------------------
    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(10)

        # 1. Top Control Bar: Title, Templates, Save/Open, Mode Switch
        top_bar = self._build_top_bar()
        root.addWidget(top_bar)

        # 2. Main Stack: Mode 0 = Design & Edit, Mode 1 = Learn Presentation View
        self._mode_stack = QStackedWidget()

        # Mode 0: Editor View
        self._editor_view = self._build_editor_view()
        self._mode_stack.addWidget(self._editor_view)

        # Mode 1: Presentation View (Identical to Learn section)
        self._presentation_view = self._build_presentation_view()
        self._mode_stack.addWidget(self._presentation_view)

        root.addWidget(self._mode_stack, stretch=1)

    def _build_top_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("StudioPanel")
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(16, 8, 16, 8)
        bar_layout.setSpacing(12)

        # Theorem Title Badge & Input
        lbl = QLabel("THEOREM:")
        lbl.setStyleSheet("color: #5EEAD4; font-weight: 700; font-size: 11.5px; letter-spacing: 0.5px;")
        bar_layout.addWidget(lbl)

        self._title_edit = QLineEdit(self._proof.title)
        self._title_edit.setStyleSheet(
            "background: rgba(16, 21, 32, 0.85); border: 1px solid rgba(94, 234, 212, 0.35); "
            "border-radius: 8px; color: #F8FAFC; font-weight: 700; font-size: 14px; padding: 5px 10px;"
        )
        self._title_edit.setMinimumWidth(220)
        self._title_edit.textChanged.connect(self._on_title_changed)
        bar_layout.addWidget(self._title_edit)

        # Templates Button
        tmpl_btn = QPushButton("📐  Templates ▼")
        tmpl_btn.setObjectName("StudioActionBtn")
        tmpl_btn.setCursor(Qt.PointingHandCursor)
        tmpl_btn.setToolTip("Choose a prebuilt starter theorem proof")
        tmpl_menu = QMenu(self)
        tmpl_menu.setStyleSheet("background: #101520; color: #F8FAFC; border: 1px solid #1F2A38;")

        for k, name in [
            ("pythagorean", "Pythagorean Theorem (a² + b² = c²)"),
            ("triangle_angle_sum", "Triangle Angle Sum (∠A + ∠B + ∠C = 180°)"),
            ("thales", "Thales's Theorem (Angle in Semicircle = 90°)"),
            ("exterior_angle", "Exterior Angle Theorem (∠ext = ∠A + ∠B)"),
            ("triangle_area", "Area of a Triangle (Area = ½ · b · h)"),
            ("blank", "Blank Custom Canvas"),
        ]:
            act = QAction(name, self)
            act.triggered.connect(lambda _, key=k: self._on_template_selected(key))
            tmpl_menu.addAction(act)

        tmpl_btn.setMenu(tmpl_menu)
        bar_layout.addWidget(tmpl_btn)

        # New Proof Button
        new_btn = QPushButton("+ New")
        new_btn.setObjectName("StudioActionBtn")
        new_btn.setCursor(Qt.PointingHandCursor)
        new_btn.setToolTip("Start a clean new proof")
        new_btn.clicked.connect(self._on_new_proof)
        bar_layout.addWidget(new_btn)

        # Save & Open JSON
        open_btn = QPushButton("📂 Open")
        open_btn.setObjectName("StudioActionBtn")
        open_btn.setCursor(Qt.PointingHandCursor)
        open_btn.setToolTip("Open a saved proof (.json)")
        open_btn.clicked.connect(self._on_open_json)
        bar_layout.addWidget(open_btn)

        save_btn = QPushButton("💾 Save")
        save_btn.setObjectName("StudioActionBtn")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setToolTip("Save proof to a JSON file")
        save_btn.clicked.connect(self._on_save_json)
        bar_layout.addWidget(save_btn)

        bar_layout.addStretch(1)

        # Mode Switcher: "Design & Edit" vs "Learn Presentation View"
        self._mode_btn_edit = QPushButton("✎  Graphics Grid Mode")
        self._mode_btn_edit.setObjectName("StudioModeChip")
        self._mode_btn_edit.setCheckable(True)
        self._mode_btn_edit.setChecked(True)
        self._mode_btn_edit.setCursor(Qt.PointingHandCursor)
        self._mode_btn_edit.clicked.connect(lambda: self.switch_mode(False))
        bar_layout.addWidget(self._mode_btn_edit)

        self._mode_btn_present = QPushButton("▶  Learn Presentation View")
        self._mode_btn_present.setObjectName("StudioModeChip")
        self._mode_btn_present.setCheckable(True)
        self._mode_btn_present.setChecked(False)
        self._mode_btn_present.setCursor(Qt.PointingHandCursor)
        self._mode_btn_present.setStyleSheet("color: #5EEAD4; font-weight: 700;")
        self._mode_btn_present.setToolTip("Present and animate this proof just like prebuilt proofs in Learn")
        self._mode_btn_present.clicked.connect(lambda: self.switch_mode(True))
        bar_layout.addWidget(self._mode_btn_present)

        return bar

    # ------------------------------------------------------------------
    # Mode 0: Design & Edit View
    # ------------------------------------------------------------------
    def _build_editor_view(self) -> QWidget:
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(8)

        # Left Column: Steps Timeline & Actions
        left_col = self._build_steps_panel()
        splitter.addWidget(left_col)

        # Center Column: Canvas & Geometry Tools
        center_col = self._build_canvas_panel()
        splitter.addWidget(center_col)

        # Right Column: Step Equations & Shape Inspector
        right_col = self._build_inspector_panel()
        splitter.addWidget(right_col)

        splitter.setSizes([220, 680, 340])
        return splitter

    def _build_steps_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("StudioPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        hdr = QLabel("PROOF STEPS")
        hdr.setObjectName("PanelTitle")
        hdr.setStyleSheet("color: #5EEAD4; font-weight: 700; font-size: 12px; letter-spacing: 0.6px;")
        layout.addWidget(hdr)

        self._steps_list = QListWidget()
        self._steps_list.setStyleSheet(
            "QListWidget { background: rgba(16, 21, 32, 0.7); border: 1px solid rgba(94, 234, 212, 0.2); "
            "border-radius: 8px; color: #F8FAFC; font-size: 12.5px; } "
            "QListWidget::item { padding: 8px 10px; border-bottom: 1px solid rgba(255,255,255,0.05); } "
            "QListWidget::item:selected { background: rgba(94, 234, 212, 0.22); color: #5EEAD4; font-weight: 600; border-left: 3px solid #5EEAD4; }"
        )
        self._steps_list.currentRowChanged.connect(self._on_step_list_selected)
        layout.addWidget(self._steps_list, stretch=1)

        # Step Actions: Add, Duplicate, Delete, Move Up/Down
        btn_grid_1 = QHBoxLayout()
        btn_grid_1.setSpacing(6)

        add_step_btn = QPushButton("+ Step")
        add_step_btn.setObjectName("StudioActionBtn")
        add_step_btn.setCursor(Qt.PointingHandCursor)
        add_step_btn.clicked.connect(self._on_add_step)
        btn_grid_1.addWidget(add_step_btn)

        dup_step_btn = QPushButton("Duplicate")
        dup_step_btn.setObjectName("StudioActionBtn")
        dup_step_btn.setCursor(Qt.PointingHandCursor)
        dup_step_btn.setToolTip("Duplicate active step and all its shapes")
        dup_step_btn.clicked.connect(self._on_duplicate_step)
        btn_grid_1.addWidget(dup_step_btn)
        layout.addLayout(btn_grid_1)

        btn_grid_2 = QHBoxLayout()
        btn_grid_2.setSpacing(6)

        del_step_btn = QPushButton("Delete Step")
        del_step_btn.setObjectName("StudioActionBtn")
        del_step_btn.setCursor(Qt.PointingHandCursor)
        del_step_btn.setStyleSheet("color: #F87171;")
        del_step_btn.setToolTip("Delete current step")
        del_step_btn.clicked.connect(self._on_delete_step)
        btn_grid_2.addWidget(del_step_btn)
        layout.addLayout(btn_grid_2)

        reorder_row = QHBoxLayout()
        reorder_row.setSpacing(6)
        up_btn = QPushButton("▲ Up")
        up_btn.setObjectName("StudioActionBtn")
        up_btn.setCursor(Qt.PointingHandCursor)
        up_btn.clicked.connect(lambda: self._on_move_step(-1))
        reorder_row.addWidget(up_btn)

        down_btn = QPushButton("▼ Down")
        down_btn.setObjectName("StudioActionBtn")
        down_btn.setCursor(Qt.PointingHandCursor)
        down_btn.clicked.connect(lambda: self._on_move_step(1))
        reorder_row.addWidget(down_btn)
        layout.addLayout(reorder_row)

        return panel

    def _build_canvas_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        def _make_separator():
            sep = QFrame()
            sep.setFrameShape(QFrame.VLine)
            sep.setFrameShadow(QFrame.Sunken)
            sep.setStyleSheet("color: rgba(255, 255, 255, 0.15); margin: 2px 4px;")
            return sep

        # -------------------------------------------------------------
        # Canvas Top Toolbar: 2 Neat Rows (Tools & Shapes)
        # -------------------------------------------------------------
        tools_bar = QWidget()
        tools_bar.setObjectName("StudioPanel")
        tools_bar.setStyleSheet("""
            QWidget#StudioPanel {
                background: rgba(14, 19, 30, 0.96);
                border: 1px solid rgba(94, 234, 212, 0.22);
                border-radius: 10px;
                padding: 4px;
            }
        """)
        tb_layout = QVBoxLayout(tools_bar)
        tb_layout.setContentsMargins(8, 6, 8, 6)
        tb_layout.setSpacing(6)

        self._tool_buttons: Dict[str, QPushButton] = {}

        tool_btn_css = """
            QPushButton#CanvasToolBtn {
                background-color: rgba(20, 27, 42, 0.9);
                border: 1px solid rgba(94, 234, 212, 0.22);
                border-radius: 6px;
                color: #E2E8F0;
                font-size: 11.5px;
                font-weight: 600;
                padding: 4px 10px;
                min-height: 26px;
            }
            QPushButton#CanvasToolBtn:hover {
                background-color: rgba(94, 234, 212, 0.16);
                border-color: rgba(94, 234, 212, 0.5);
                color: #5EEAD4;
            }
            QPushButton#CanvasToolBtn:checked {
                background-color: #5EEAD4;
                border-color: #5EEAD4;
                color: #07080D;
                font-weight: 700;
            }
        """

        # Row 1: Canvas tools (navigation, selection, and annotations)
        row1 = QHBoxLayout()
        row1.setContentsMargins(0, 0, 0, 0)
        row1.setSpacing(6)

        lbl_tools = QLabel("TOOLS:")
        lbl_tools.setStyleSheet("color: #5EEAD4; font-weight: 800; font-size: 11px; letter-spacing: 0.5px;")
        row1.addWidget(lbl_tools)

        row1_specs = [
            ("select", "↖ Select"),
            ("pan", "✣ Pan"),
            ("slice", "◔ Slice"),
            ("text", "T Text"),
            ("angle", "∠ Angle"),
            ("right_angle", "⊾ Right ∠"),
        ]

        for key, label in row1_specs:
            if label is None:
                row1.addWidget(_make_separator())
                continue
            btn = QPushButton(label)
            btn.setObjectName("CanvasToolBtn")
            btn.setStyleSheet(tool_btn_css)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _=False, k=key: self._on_tool_chosen(k))
            row1.addWidget(btn)
            self._tool_buttons[key] = btn

        row1.addStretch(1)
        tb_layout.addLayout(row1)

        # Row 2: Shapes created on the canvas
        row2 = QHBoxLayout()
        row2.setContentsMargins(0, 0, 0, 0)
        row2.setSpacing(6)

        lbl_shapes = QLabel("SHAPES:")
        lbl_shapes.setStyleSheet("color: #94A3B8; font-weight: 800; font-size: 11px; letter-spacing: 0.5px;")
        row2.addWidget(lbl_shapes)

        row2_specs = [
            ("point", "● Point"),
            ("line", "╱ Line"),
            ("curve", "⌒ Curve"),
            ("triangle", "▲ Triangle"),
            ("rectangle", "■ Rectangle"),
            ("circle", "○ Circle"),
            ("polygon", "⬡ Polygon"),
        ]

        for key, label in row2_specs:
            if label is None:
                row2.addWidget(_make_separator())
                continue
            btn = QPushButton(label)
            btn.setObjectName("CanvasToolBtn")
            btn.setStyleSheet(tool_btn_css)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _=False, k=key: self._on_tool_chosen(k))
            row2.addWidget(btn)
            self._tool_buttons[key] = btn

        row2.addStretch(1)
        tb_layout.addLayout(row2)

        self._tool_buttons["select"].setChecked(True)
        layout.addWidget(tools_bar)

        # -------------------------------------------------------------
        # Interactive Canvas (Middle)
        # -------------------------------------------------------------
        self._canvas = BuilderCanvas()
        layout.addWidget(self._canvas, stretch=1)

        # -------------------------------------------------------------
        # Canvas Bottom Bar: Status, Coordinates, Snap & Viewport HUD
        # -------------------------------------------------------------
        bottom_bar = QWidget()
        bottom_bar.setObjectName("StudioPanel")
        bottom_bar.setStyleSheet("""
            QWidget#StudioPanel {
                background: rgba(14, 19, 30, 0.96);
                border: 1px solid rgba(94, 234, 212, 0.22);
                border-radius: 8px;
            }
        """)
        b_layout = QHBoxLayout(bottom_bar)
        b_layout.setContentsMargins(10, 4, 10, 4)
        b_layout.setSpacing(8)

        # Snap to Grid toggle
        snap_box = QCheckBox("Snap Grid")
        snap_box.setChecked(True)
        snap_box.setStyleSheet(
            "QCheckBox { color: #94A3B8; font-size: 11px; font-weight: 600; } "
            "QCheckBox:hover { color: #5EEAD4; }"
        )
        snap_box.toggled.connect(self._on_snap_toggled)
        b_layout.addWidget(snap_box)

        b_layout.addWidget(_make_separator())

        # Live Coordinate Indicator
        self._coord_label = QLabel("⌖ (0.0, 0.0)")
        self._coord_label.setStyleSheet("color: #5EEAD4; font-family: monospace; font-size: 11px; font-weight: 700;")
        self._coord_label.setToolTip("Current cursor coordinates")
        b_layout.addWidget(self._coord_label)

        b_layout.addWidget(_make_separator())

        # Live Helper Hint Message
        self._hint_label = QLabel("Select / Drag: Click to select shapes, drag vertices to reshape, or drag background to pan.")
        self._hint_label.setStyleSheet("color: #64748B; font-size: 11px;")
        b_layout.addWidget(self._hint_label, stretch=1)

        # Navigation & Viewport Controls Group
        nav_btn_css = """
            QPushButton {
                background-color: rgba(20, 27, 42, 0.9);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 4px;
                color: #CBD5E1;
                font-size: 11px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: rgba(94, 234, 212, 0.2);
                border-color: #5EEAD4;
                color: #5EEAD4;
            }
            QPushButton:pressed {
                background-color: rgba(94, 234, 212, 0.35);
            }
        """

        # Pan D-Pad Buttons
        pan_left_btn = QPushButton("◀")
        pan_left_btn.setFixedSize(24, 24)
        pan_left_btn.setStyleSheet(nav_btn_css)
        pan_left_btn.setToolTip("Pan Left (Left Arrow)")
        pan_left_btn.clicked.connect(lambda: self._canvas.pan_by(60.0, 0.0))
        b_layout.addWidget(pan_left_btn)

        pan_up_btn = QPushButton("▲")
        pan_up_btn.setFixedSize(24, 24)
        pan_up_btn.setStyleSheet(nav_btn_css)
        pan_up_btn.setToolTip("Pan Up (Up Arrow)")
        pan_up_btn.clicked.connect(lambda: self._canvas.pan_by(0.0, 60.0))
        b_layout.addWidget(pan_up_btn)

        pan_down_btn = QPushButton("▼")
        pan_down_btn.setFixedSize(24, 24)
        pan_down_btn.setStyleSheet(nav_btn_css)
        pan_down_btn.setToolTip("Pan Down (Down Arrow)")
        pan_down_btn.clicked.connect(lambda: self._canvas.pan_by(0.0, -60.0))
        b_layout.addWidget(pan_down_btn)

        pan_right_btn = QPushButton("▶")
        pan_right_btn.setFixedSize(24, 24)
        pan_right_btn.setStyleSheet(nav_btn_css)
        pan_right_btn.setToolTip("Pan Right (Right Arrow)")
        pan_right_btn.clicked.connect(lambda: self._canvas.pan_by(-60.0, 0.0))
        b_layout.addWidget(pan_right_btn)

        b_layout.addWidget(_make_separator())

        # Zoom Controls
        zoom_out_btn = QPushButton("−")
        zoom_out_btn.setFixedSize(24, 24)
        zoom_out_btn.setStyleSheet(nav_btn_css)
        zoom_out_btn.setToolTip("Zoom Out (- / Wheel)")
        zoom_out_btn.clicked.connect(lambda: self._canvas.zoom_by(1.0 / 1.2))
        b_layout.addWidget(zoom_out_btn)

        self._zoom_label = QLabel("100%")
        self._zoom_label.setStyleSheet("color: #5EEAD4; font-family: monospace; font-size: 11px; font-weight: 700; padding: 0 4px;")
        self._zoom_label.setToolTip("Current Zoom Level")
        b_layout.addWidget(self._zoom_label)

        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedSize(24, 24)
        zoom_in_btn.setStyleSheet(nav_btn_css)
        zoom_in_btn.setToolTip("Zoom In (+ / Wheel)")
        zoom_in_btn.clicked.connect(lambda: self._canvas.zoom_by(1.2))
        b_layout.addWidget(zoom_in_btn)

        reset_btn = QPushButton("⟲")
        reset_btn.setFixedSize(24, 24)
        reset_btn.setStyleSheet(nav_btn_css)
        reset_btn.setToolTip("Reset Canvas View (Home / 0)")
        reset_btn.clicked.connect(lambda: self._canvas.reset_view())
        b_layout.addWidget(reset_btn)

        fit_btn = QPushButton("⛶ Fit")
        fit_btn.setFixedHeight(24)
        fit_btn.setStyleSheet(nav_btn_css + "QPushButton { padding: 0 8px; }")
        fit_btn.setToolTip("Fit View to All Shapes (F)")
        fit_btn.clicked.connect(lambda: self._canvas.fit_to_content())
        b_layout.addWidget(fit_btn)

        layout.addWidget(bottom_bar)

        # Hook Canvas Events
        self._canvas.statusMessage.connect(
            lambda msg: (self._hint_label.setText(msg), self.statusMessage.emit(msg))
        )
        self._canvas.stepModified.connect(self._on_step_modified)
        self._canvas.shapeSelected.connect(self._on_shape_selected)
        self._canvas.toolChanged.connect(self._on_canvas_tool_changed)
        self._canvas.cursorCoordChanged.connect(
            lambda x, y: self._coord_label.setText(f"⌖ ({x:.1f}, {y:.1f})")
        )
        self._canvas.zoomChanged.connect(
            lambda z: self._zoom_label.setText(f"{int(round(z * 100))}%")
        )

        return panel

    def _build_inspector_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("StudioPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        tabs = QTabWidget()
        tabs.setStyleSheet(
            "QTabWidget::pane { border: 1px solid rgba(94, 234, 212, 0.2); background: rgba(16, 21, 32, 0.6); border-radius: 8px; } "
            "QTabBar::tab { background: #101520; color: #94A3B8; padding: 7px 14px; font-weight: 600; font-size: 12px; } "
            "QTabBar::tab:selected { color: #5EEAD4; border-bottom: 2px solid #5EEAD4; }"
        )

        # Tab 1: Step Details (Title, Equation, Caption/Explanation)
        tab_step = self._build_step_details_tab()
        tabs.addTab(tab_step, "Step Details")

        # Tab 2: Shapes & Elements
        tab_shapes = self._build_shapes_tab()
        tabs.addTab(tab_shapes, "Shapes & Objects")

        layout.addWidget(tabs, stretch=1)
        return panel

    def _build_step_details_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Step Title
        layout.addWidget(QLabel("Step Title:"))
        self._step_title_edit = QLineEdit()
        self._step_title_edit.setStyleSheet(
            "background: rgba(10, 13, 20, 0.9); border: 1px solid #1F2A38; border-radius: 6px; color: #F8FAFC; padding: 6px;"
        )
        self._step_title_edit.textChanged.connect(self._on_step_title_changed)
        layout.addWidget(self._step_title_edit)

        # Equation / Formula
        layout.addWidget(QLabel("Mathematical Formula / Equation:"))
        self._equation_edit = QLineEdit()
        self._equation_edit.setStyleSheet(
            "background: rgba(10, 13, 20, 0.9); border: 1px solid #1F2A38; border-radius: 6px; color: #5EEAD4; "
            "font-family: monospace; font-size: 13px; padding: 6px;"
        )
        self._equation_edit.textChanged.connect(self._on_equation_changed)
        layout.addWidget(self._equation_edit)

        # Math Symbols Quick Insert Toolbar
        sym_box = QWidget()
        sym_layout = QHBoxLayout(sym_box)
        sym_layout.setContentsMargins(0, 0, 0, 0)
        sym_layout.setSpacing(3)
        for sym in MATH_SYMBOLS:
            s_btn = QPushButton(sym)
            s_btn.setFixedSize(24, 24)
            s_btn.setCursor(Qt.PointingHandCursor)
            s_btn.setStyleSheet(
                "background: rgba(94, 234, 212, 0.12); color: #5EEAD4; border: 1px solid rgba(94, 234, 212, 0.25); "
                "border-radius: 4px; font-weight: 700; font-size: 11px;"
            )
            s_btn.clicked.connect(lambda _=False, s=sym: self._insert_math_symbol(s))
            sym_layout.addWidget(s_btn)
        sym_layout.addStretch(1)
        layout.addWidget(sym_box)

        # Caption / Pedagogical Explanation
        layout.addWidget(QLabel("Caption & Pedagogical Explanation:"))

        # Helper buttons to structure explanation
        helper_row = QHBoxLayout()
        helper_row.setSpacing(4)
        for tag in ["+ Goal", "+ Why", "+ Calculation", "+ Result"]:
            h_btn = QPushButton(tag)
            h_btn.setCursor(Qt.PointingHandCursor)
            h_btn.setStyleSheet(
                "background: rgba(108, 92, 231, 0.15); color: #A78BFA; border: 1px solid rgba(108, 92, 231, 0.3); "
                "border-radius: 4px; font-size: 10.5px; padding: 3px 6px;"
            )
            h_btn.clicked.connect(lambda _=False, t=tag: self._insert_explanation_tag(t))
            helper_row.addWidget(h_btn)
        helper_row.addStretch(1)
        layout.addLayout(helper_row)

        self._explanation_edit = QTextEdit()
        self._explanation_edit.setStyleSheet(
            "background: rgba(10, 13, 20, 0.9); border: 1px solid #1F2A38; border-radius: 6px; color: #CBD5E1; "
            "font-size: 12px; padding: 6px;"
        )
        self._explanation_edit.textChanged.connect(self._on_explanation_changed)
        layout.addWidget(self._explanation_edit, stretch=1)

        return widget

    def _build_shapes_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        layout.addWidget(QLabel("Shapes in Current Step:"))

        self._shapes_list = QListWidget()
        self._shapes_list.setStyleSheet(
            "QListWidget { background: rgba(10, 13, 20, 0.9); border: 1px solid #1F2A38; border-radius: 6px; color: #F8FAFC; } "
            "QListWidget::item { padding: 5px 8px; } "
            "QListWidget::item:selected { background: rgba(94, 234, 212, 0.2); color: #5EEAD4; }"
        )
        self._shapes_list.currentRowChanged.connect(self._on_shape_list_selected)
        layout.addWidget(self._shapes_list, stretch=1)

        # Selected Shape Properties
        props_hdr = QLabel("SHAPE PROPERTIES")
        props_hdr.setStyleSheet("color: #5EEAD4; font-weight: 700; font-size: 11px; margin-top: 4px;")
        layout.addWidget(props_hdr)

        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Label:"))
        self._shape_name_edit = QLineEdit()
        self._shape_name_edit.setStyleSheet("background: rgba(10, 13, 20, 0.9); color: #F8FAFC; border: 1px solid #1F2A38; border-radius: 4px; padding: 4px;")
        self._shape_name_edit.textChanged.connect(self._on_shape_property_changed)
        name_row.addWidget(self._shape_name_edit)
        layout.addLayout(name_row)

        # Palette colors
        color_row = QHBoxLayout()
        color_row.addWidget(QLabel("Color:"))
        for hex_code, tip in COLOR_PALETTE:
            c_btn = QPushButton()
            c_btn.setFixedSize(22, 22)
            c_btn.setToolTip(tip)
            c_btn.setCursor(Qt.PointingHandCursor)
            c_btn.setStyleSheet(f"background: {hex_code}; border: 1.5px solid rgba(255,255,255,0.4); border-radius: 11px;")
            c_btn.clicked.connect(lambda _=False, col=hex_code: self._set_selected_shape_color(col))
            color_row.addWidget(c_btn)
        color_row.addStretch(1)
        layout.addLayout(color_row)

        # Stroke Width & Dashed
        stroke_row = QHBoxLayout()
        stroke_row.addWidget(QLabel("Width:"))
        self._stroke_spin = QDoubleSpinBox()
        self._stroke_spin.setRange(0.5, 10.0)
        self._stroke_spin.setSingleStep(0.5)
        self._stroke_spin.setValue(2.0)
        self._stroke_spin.setStyleSheet("background: rgba(10, 13, 20, 0.9); color: #F8FAFC; border: 1px solid #1F2A38; border-radius: 4px;")
        self._stroke_spin.valueChanged.connect(self._on_shape_property_changed)
        stroke_row.addWidget(self._stroke_spin)

        self._dashed_check = QCheckBox("Dashed")
        self._dashed_check.setStyleSheet("color: #94A3B8; font-size: 11px;")
        self._dashed_check.toggled.connect(self._on_shape_property_changed)
        stroke_row.addWidget(self._dashed_check)
        stroke_row.addStretch(1)
        layout.addLayout(stroke_row)

        # Position & Placement controls
        pos_hdr = QLabel("POSITION & PLACEMENT")
        pos_hdr.setStyleSheet("color: #5EEAD4; font-weight: 700; font-size: 11px; margin-top: 6px;")
        layout.addWidget(pos_hdr)

        pos_row = QHBoxLayout()
        pos_row.setSpacing(6)
        pos_row.addWidget(QLabel("X:"))
        self._pos_x_spin = QDoubleSpinBox()
        self._pos_x_spin.setRange(-50.0, 50.0)
        self._pos_x_spin.setSingleStep(0.5)
        self._pos_x_spin.setStyleSheet("background: rgba(10, 13, 20, 0.9); color: #5EEAD4; border: 1px solid #1F2A38; border-radius: 4px;")
        self._pos_x_spin.valueChanged.connect(self._on_pos_changed)
        pos_row.addWidget(self._pos_x_spin)

        pos_row.addWidget(QLabel("Y:"))
        self._pos_y_spin = QDoubleSpinBox()
        self._pos_y_spin.setRange(-50.0, 50.0)
        self._pos_y_spin.setSingleStep(0.5)
        self._pos_y_spin.setStyleSheet("background: rgba(10, 13, 20, 0.9); color: #5EEAD4; border: 1px solid #1F2A38; border-radius: 4px;")
        self._pos_y_spin.valueChanged.connect(self._on_pos_changed)
        pos_row.addWidget(self._pos_y_spin)
        layout.addLayout(pos_row)

        # Nudge D-pad buttons: ◀, ▲, ▼, ▶ and Center button
        nudge_row = QHBoxLayout()
        nudge_row.setSpacing(4)
        for label, tip, ndx, ndy in [
            ("◀", "Nudge Left (or Left Arrow key)", -0.5, 0.0),
            ("▲", "Nudge Up (or Up Arrow key)", 0.0, 0.5),
            ("▼", "Nudge Down (or Down Arrow key)", 0.0, -0.5),
            ("▶", "Nudge Right (or Right Arrow key)", 0.5, 0.0),
        ]:
            n_btn = QPushButton(label)
            n_btn.setObjectName("StudioActionBtn")
            n_btn.setFixedSize(28, 26)
            n_btn.setToolTip(tip)
            n_btn.setCursor(Qt.PointingHandCursor)
            n_btn.clicked.connect(lambda _=False, dx=ndx, dy=ndy: self._nudge_selected_shape(dx, dy))
            nudge_row.addWidget(n_btn)

        center_btn = QPushButton("✛ Center")
        center_btn.setObjectName("StudioActionBtn")
        center_btn.setToolTip("Move shape to center of canvas (0, 0)")
        center_btn.setCursor(Qt.PointingHandCursor)
        center_btn.clicked.connect(self._center_selected_shape)
        nudge_row.addWidget(center_btn)
        nudge_row.addStretch(1)
        layout.addLayout(nudge_row)

        # Angle settings group (visible when an angle is selected)
        self._angle_group = QWidget()
        ang_layout = QVBoxLayout(self._angle_group)
        ang_layout.setContentsMargins(0, 0, 0, 0)
        ang_layout.setSpacing(6)

        ang_hdr = QLabel("ANGLE SPECIFICATIONS")
        ang_hdr.setStyleSheet("color: #D8A94E; font-weight: 700; font-size: 11px; margin-top: 6px;")
        ang_layout.addWidget(ang_hdr)

        ang_deg_row = QHBoxLayout()
        ang_deg_row.addWidget(QLabel("Span (°):"))
        self._angle_span_spin = QDoubleSpinBox()
        self._angle_span_spin.setRange(1.0, 360.0)
        self._angle_span_spin.setSingleStep(5.0)
        self._angle_span_spin.setValue(60.0)
        self._angle_span_spin.setStyleSheet("background: rgba(10, 13, 20, 0.9); color: #F59E0B; border: 1px solid #1F2A38; border-radius: 4px;")
        self._angle_span_spin.valueChanged.connect(self._on_angle_property_changed)
        ang_deg_row.addWidget(self._angle_span_spin)

        self._angle_right_check = QCheckBox("⊾ 90° Box")
        self._angle_right_check.setStyleSheet("color: #D8A94E; font-size: 11px;")
        self._angle_right_check.toggled.connect(self._on_angle_property_changed)
        ang_deg_row.addWidget(self._angle_right_check)
        ang_layout.addLayout(ang_deg_row)

        preset_row = QHBoxLayout()
        preset_row.setSpacing(4)
        for deg in [30, 45, 60, 90, 120]:
            p_btn = QPushButton(f"{deg}°")
            p_btn.setObjectName("StudioActionBtn")
            p_btn.setFixedSize(36, 22)
            p_btn.setCursor(Qt.PointingHandCursor)
            p_btn.clicked.connect(lambda _=False, d=deg: self._set_selected_angle_span(d))
            preset_row.addWidget(p_btn)
        preset_row.addStretch(1)
        ang_layout.addLayout(preset_row)

        layout.addWidget(self._angle_group)
        self._angle_group.setVisible(False)

        # Text/Formula Editor group (visible when a text label is selected)
        self._text_group = QWidget()
        t_layout = QVBoxLayout(self._text_group)
        t_layout.setContentsMargins(0, 0, 0, 0)
        t_layout.setSpacing(6)

        t_hdr = QLabel("TEXT & FORMULA EDITOR")
        t_hdr.setStyleSheet("color: #5EEAD4; font-weight: 700; font-size: 11px; margin-top: 6px;")
        t_layout.addWidget(t_hdr)

        t_layout.addWidget(QLabel("Content / Math Equation:"))
        self._shape_text_edit = QLineEdit()
        self._shape_text_edit.setPlaceholderText("Enter formula or text (e.g. a² + b² = c²)...")
        self._shape_text_edit.setStyleSheet(
            "background: rgba(10, 13, 20, 0.9); color: #5EEAD4; border: 1px solid #1F2A38; "
            "border-radius: 4px; padding: 6px; font-family: monospace; font-size: 13px;"
        )
        self._shape_text_edit.textChanged.connect(self._on_shape_text_changed)
        t_layout.addWidget(self._shape_text_edit)

        t_sym_box = QWidget()
        t_sym_layout = QHBoxLayout(t_sym_box)
        t_sym_layout.setContentsMargins(0, 0, 0, 0)
        t_sym_layout.setSpacing(3)
        for sym in ["²", "³", "√", "∠", "°", "⊥", "∥", "Δ", "π", "θ", "α", "β", "⟹", "≅"]:
            s_btn = QPushButton(sym)
            s_btn.setFixedSize(22, 22)
            s_btn.setCursor(Qt.PointingHandCursor)
            s_btn.setStyleSheet(
                "background: rgba(94, 234, 212, 0.12); color: #5EEAD4; border: 1px solid rgba(94, 234, 212, 0.25); "
                "border-radius: 4px; font-weight: 700; font-size: 10.5px;"
            )
            s_btn.clicked.connect(lambda _=False, s=sym: self._insert_shape_text_symbol(s))
            t_sym_layout.addWidget(s_btn)
        t_sym_layout.addStretch(1)
        t_layout.addWidget(t_sym_box)

        font_row = QHBoxLayout()
        font_row.addWidget(QLabel("Font Size:"))
        self._text_font_size_spin = QSpinBox()
        self._text_font_size_spin.setRange(8, 48)
        self._text_font_size_spin.setValue(13)
        self._text_font_size_spin.setStyleSheet("background: rgba(10, 13, 20, 0.9); color: #F8FAFC; border: 1px solid #1F2A38; border-radius: 4px;")
        self._text_font_size_spin.valueChanged.connect(self._on_shape_text_changed)
        font_row.addWidget(self._text_font_size_spin)

        self._text_bold_check = QCheckBox("Bold")
        self._text_bold_check.setChecked(True)
        self._text_bold_check.setStyleSheet("color: #94A3B8; font-size: 11px;")
        self._text_bold_check.toggled.connect(self._on_shape_text_changed)
        font_row.addWidget(self._text_bold_check)
        font_row.addStretch(1)
        t_layout.addLayout(font_row)

        layout.addWidget(self._text_group)
        self._text_group.setVisible(False)

        del_shape_btn = QPushButton("Delete Selected Shape")
        del_shape_btn.setObjectName("StudioActionBtn")
        del_shape_btn.setStyleSheet("color: #F87171; border-color: rgba(248, 113, 113, 0.4);")
        del_shape_btn.setCursor(Qt.PointingHandCursor)
        del_shape_btn.clicked.connect(self._on_delete_selected_shape)
        layout.addWidget(del_shape_btn)

        return widget

    # ------------------------------------------------------------------
    # Mode 1: Built-in Learn Presentation View
    # (Identical look, feel, and playback to prebuilt proofs in Learn!)
    # ------------------------------------------------------------------
    def _build_presentation_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # Header bar for Presentation mode
        top_row = QHBoxLayout()
        self._pres_title = QLabel("Proof Presentation")
        self._pres_title.setStyleSheet("color: #F8FAFC; font-weight: 800; font-size: 17px; letter-spacing: -0.3px;")
        top_row.addWidget(self._pres_title)

        top_row.addStretch(1)

        back_to_edit_btn = QPushButton("✎  Return to Editor")
        back_to_edit_btn.setObjectName("StudioActionBtn")
        back_to_edit_btn.setCursor(Qt.PointingHandCursor)
        back_to_edit_btn.clicked.connect(lambda: self.switch_mode(False))
        top_row.addWidget(back_to_edit_btn)
        layout.addLayout(top_row)

        # Center Canvas: Exact VisualizationWidget from Learn section!
        self._pres_canvas = VisualizationWidget()
        layout.addWidget(self._pres_canvas, stretch=6)

        # Transport Controls: Exact AnimationControls from Learn section!
        self._pres_controls = AnimationControls()
        self._pres_controls.previousClicked.connect(self._pres_step_prev)
        self._pres_controls.nextClicked.connect(self._pres_step_next)
        self._pres_controls.playPauseClicked.connect(self._pres_toggle_play)
        self._pres_controls.replayClicked.connect(self._pres_replay)
        self._pres_controls.stepSelected.connect(self._pres_seek_step)
        self._pres_controls.speedChanged.connect(self._pres_set_speed)
        self._pres_controls.set_enabled_all(True)
        layout.addWidget(self._pres_controls)

        # Bottom Panel: Exact EquationPanel from Learn section!
        self._pres_equation = EquationPanel()
        self._pres_equation.setObjectName("EquationPanel")
        self._pres_equation.setAttribute(Qt.WA_StyledBackground, True)
        self._pres_equation.setMinimumHeight(135)
        self._pres_equation.setMaximumHeight(200)
        layout.addWidget(self._pres_equation, stretch=1)

        return widget

    # ------------------------------------------------------------------
    # State Synchronization & Loading
    # ------------------------------------------------------------------
    def _load_proof_into_editor(self, proof: BuilderProof):
        self._proof = proof
        self._title_edit.setText(proof.title)
        self._refresh_steps_list()
        self.select_step(0)

    def _refresh_steps_list(self):
        self._steps_list.blockSignals(True)
        self._steps_list.clear()
        for i, step in enumerate(self._proof.steps):
            item = QListWidgetItem(f"Step {step.index}: {step.title or 'Untitled'}")
            self._steps_list.addItem(item)
        self._steps_list.blockSignals(False)

        if self._active_step_idx < len(self._proof.steps):
            self._steps_list.setCurrentRow(self._active_step_idx)

    def select_step(self, step_idx: int):
        if not self._proof.steps:
            return
        self._active_step_idx = max(0, min(step_idx, len(self._proof.steps) - 1))
        step = self._proof.steps[self._active_step_idx]

        # Bind to canvas
        self._canvas.set_step(step)

        # Update Step Details tab
        self._step_title_edit.blockSignals(True)
        self._step_title_edit.setText(step.title)
        self._step_title_edit.blockSignals(False)

        self._equation_edit.blockSignals(True)
        self._equation_edit.setText(step.equation)
        self._equation_edit.blockSignals(False)

        self._explanation_edit.blockSignals(True)
        self._explanation_edit.setPlainText(step.explanation)
        self._explanation_edit.blockSignals(False)

        self._refresh_shapes_list()

    def _refresh_shapes_list(self):
        self._shapes_list.blockSignals(True)
        self._shapes_list.clear()
        step = self.current_step()
        if step:
            for s in step.shapes:
                label_txt = f"{s.shape_type.upper()}: {s.name or 'Shape'}"
                item = QListWidgetItem(label_txt)
                item.setData(Qt.UserRole, s.id)
                self._shapes_list.addItem(item)
        self._shapes_list.blockSignals(False)

    def current_step(self) -> Optional[BuilderProofStep]:
        if 0 <= self._active_step_idx < len(self._proof.steps):
            return self._proof.steps[self._active_step_idx]
        return None

    # ------------------------------------------------------------------
    # Step & Shape Modifications
    # ------------------------------------------------------------------
    def _on_step_list_selected(self, row: int):
        if row >= 0:
            self.select_step(row)

    def _on_add_step(self):
        new_step = self._proof.add_step()
        self._active_step_idx = len(self._proof.steps) - 1
        self._refresh_steps_list()
        self.select_step(self._active_step_idx)
        self.statusMessage.emit(f"Added Step {new_step.index}.")

    def _on_duplicate_step(self):
        new_step = self._proof.duplicate_step(self._active_step_idx)
        if new_step:
            self._active_step_idx += 1
            self._refresh_steps_list()
            self.select_step(self._active_step_idx)
            self.statusMessage.emit(f"Duplicated Step {new_step.index}.")

    def _on_copy_from_previous_step(self):
        if self._active_step_idx > 0:
            prev_step = self._proof.steps[self._active_step_idx - 1]
            curr_step = self._proof.steps[self._active_step_idx]
            curr_step.shapes = [s.copy() for s in prev_step.shapes]
            if prev_step.view_bounds:
                curr_step.view_bounds = prev_step.view_bounds
            self.select_step(self._active_step_idx)
            self.statusMessage.emit(f"Copied {len(curr_step.shapes)} shapes from Step {prev_step.index}.")
        else:
            self.statusMessage.emit("This is the first step — no previous step to copy from.")

    def _on_delete_step(self):
        if len(self._proof.steps) <= 1:
            QMessageBox.information(self, "Proof Builder", "Cannot delete the only step in the proof.")
            return
        self._proof.delete_step(self._active_step_idx)
        self._active_step_idx = max(0, self._active_step_idx - 1)
        self._refresh_steps_list()
        self.select_step(self._active_step_idx)
        self.statusMessage.emit("Step deleted.")

    def _on_move_step(self, offset: int):
        new_idx = self._active_step_idx + offset
        if self._proof.move_step(self._active_step_idx, new_idx):
            self._active_step_idx = new_idx
            self._refresh_steps_list()
            self.select_step(self._active_step_idx)

    def _on_title_changed(self, text: str):
        self._proof.title = text

    def _on_step_title_changed(self, text: str):
        step = self.current_step()
        if step:
            step.title = text
            # Update list widget title
            item = self._steps_list.item(self._active_step_idx)
            if item:
                item.setText(f"Step {step.index}: {step.title}")

    def _on_equation_changed(self, text: str):
        step = self.current_step()
        if step:
            step.equation = text

    def _on_explanation_changed(self):
        step = self.current_step()
        if step:
            step.explanation = self._explanation_edit.toPlainText()

    def _insert_math_symbol(self, sym: str):
        self._equation_edit.insert(sym)
        self._equation_edit.setFocus()

    def _insert_explanation_tag(self, tag: str):
        mapping = {
            "+ Goal": "\n1. Goal: ",
            "+ Why": "\n2. Why: ",
            "+ Calculation": "\n3. Calculation: ",
            "+ Result": "\n4. Result: ",
        }
        to_insert = mapping.get(tag, f"\n{tag}: ")
        self._explanation_edit.insertPlainText(to_insert)
        self._explanation_edit.setFocus()

    def _on_tool_chosen(self, tool_name: str):
        for k, btn in self._tool_buttons.items():
            btn.setChecked(k == tool_name)
        self._canvas.set_tool(tool_name)

    def _on_canvas_tool_changed(self, tool_name: str):
        for k, btn in self._tool_buttons.items():
            btn.setChecked(k == tool_name)

    def _on_snap_toggled(self, checked: bool):
        self._canvas.set_snap_to_grid(bool(checked))
        msg = f"Snap to Grid: ON ({self._canvas.grid_size} units)" if checked else "Snap to Grid: OFF (Freeform movement)"
        self.statusMessage.emit(msg)

    def _on_step_modified(self):
        self._refresh_shapes_list()
        self._update_shape_inspector()

    def _on_shape_selected(self, shape_id: str):
        if not shape_id:
            return
        # Find item in shapes list and select it
        for i in range(self._shapes_list.count()):
            item = self._shapes_list.item(i)
            if item.data(Qt.UserRole) == shape_id:
                self._shapes_list.setCurrentRow(i)
                break
        self._update_shape_inspector()

    def _on_shape_list_selected(self, row: int):
        if row >= 0:
            item = self._shapes_list.item(row)
            shape_id = item.data(Qt.UserRole)
            self._canvas.set_selected_shape_id(shape_id)
            self._update_shape_inspector()

    def _update_shape_inspector(self):
        shape = self._canvas.selected_shape()
        if not shape:
            return
        self._updating_inspector = True
        try:
            self._shape_name_edit.blockSignals(True)
            self._shape_name_edit.setText(shape.name)
            self._shape_name_edit.blockSignals(False)

            self._stroke_spin.blockSignals(True)
            self._stroke_spin.setValue(shape.stroke_width)
            self._stroke_spin.blockSignals(False)

            self._dashed_check.blockSignals(True)
            self._dashed_check.setChecked(shape.dashed)
            self._dashed_check.blockSignals(False)

            if hasattr(self, "_pos_x_spin") and hasattr(self, "_pos_y_spin"):
                cx, cy = shape.center()
                self._pos_x_spin.blockSignals(True)
                self._pos_x_spin.setValue(cx)
                self._pos_x_spin.blockSignals(False)

                self._pos_y_spin.blockSignals(True)
                self._pos_y_spin.setValue(cy)
                self._pos_y_spin.blockSignals(False)

            if hasattr(self, "_angle_group"):
                is_angle = (shape.shape_type == ShapeType.ANGLE.value)
                self._angle_group.setVisible(is_angle)
                if is_angle and len(shape.coords) >= 5:
                    self._angle_span_spin.blockSignals(True)
                    self._angle_span_spin.setValue(shape.coords[4])
                    self._angle_span_spin.blockSignals(False)

                    self._angle_right_check.blockSignals(True)
                    self._angle_right_check.setChecked(shape.is_right_angle)
                    self._angle_right_check.blockSignals(False)

            if hasattr(self, "_text_group"):
                is_text = (shape.shape_type == ShapeType.TEXT.value)
                self._text_group.setVisible(is_text)
                if is_text:
                    self._shape_text_edit.blockSignals(True)
                    self._shape_text_edit.setText(shape.text or shape.name)
                    self._shape_text_edit.blockSignals(False)

                    self._text_font_size_spin.blockSignals(True)
                    self._text_font_size_spin.setValue(shape.font_size)
                    self._text_font_size_spin.blockSignals(False)

                    self._text_bold_check.blockSignals(True)
                    self._text_bold_check.setChecked(shape.bold)
                    self._text_bold_check.blockSignals(False)
        finally:
            self._updating_inspector = False

    def _on_shape_text_changed(self):
        shape = self._canvas.selected_shape()
        if shape and shape.shape_type == ShapeType.TEXT.value and not self._updating_inspector:
            shape.text = self._shape_text_edit.text()
            shape.name = shape.text
            shape.font_size = int(self._text_font_size_spin.value())
            shape.bold = bool(self._text_bold_check.isChecked())
            self._shape_name_edit.blockSignals(True)
            self._shape_name_edit.setText(shape.name)
            self._shape_name_edit.blockSignals(False)
            self._canvas.update()
            row = self._shapes_list.currentRow()
            if row >= 0:
                item = self._shapes_list.item(row)
                if item:
                    item.setText(f"TEXT: {shape.text or 'Label'}")
            self._on_step_modified()

    def _insert_shape_text_symbol(self, sym: str):
        if hasattr(self, "_shape_text_edit"):
            self._shape_text_edit.insert(sym)
            self._shape_text_edit.setFocus()

    def _on_angle_property_changed(self):
        shape = self._canvas.selected_shape()
        if shape and shape.shape_type == ShapeType.ANGLE.value and not self._updating_inspector:
            span = float(self._angle_span_spin.value())
            is_rt = bool(self._angle_right_check.isChecked())
            if len(shape.coords) >= 5:
                shape.coords[4] = span
            shape.is_right_angle = is_rt
            shape.name = "90°" if is_rt else f"{round(span)}°"
            self._shape_name_edit.setText(shape.name)
            self._canvas.update()
            self._on_step_modified()

    def _set_selected_angle_span(self, span: float):
        shape = self._canvas.selected_shape()
        if shape and shape.shape_type == ShapeType.ANGLE.value:
            if len(shape.coords) >= 5:
                shape.coords[4] = float(span)
            shape.is_right_angle = (span == 90.0)
            shape.name = f"{round(span)}°"
            self._canvas.update()
            self._update_shape_inspector()
            self._on_step_modified()

    def _nudge_selected_shape(self, dx: float, dy: float):
        shape = self._canvas.selected_shape()
        if shape:
            shape.translate(dx, dy)
            self._canvas.update()
            self._on_step_modified()

    def _center_selected_shape(self):
        shape = self._canvas.selected_shape()
        if shape:
            cx, cy = shape.center()
            shape.translate(-cx, -cy)
            self._canvas.update()
            self._on_step_modified()

    def _on_pos_changed(self):
        shape = self._canvas.selected_shape()
        if shape and not self._updating_inspector and hasattr(self, "_pos_x_spin") and hasattr(self, "_pos_y_spin"):
            cx, cy = shape.center()
            target_x = float(self._pos_x_spin.value())
            target_y = float(self._pos_y_spin.value())
            dx = round(target_x - cx, 3)
            dy = round(target_y - cy, 3)
            if abs(dx) > 1e-4 or abs(dy) > 1e-4:
                shape.translate(dx, dy)
                self._canvas.update()
                self._refresh_shapes_list()

    def _on_shape_property_changed(self):
        shape = self._canvas.selected_shape()
        if shape:
            shape.name = self._shape_name_edit.text()
            if shape.shape_type == ShapeType.TEXT.value and hasattr(self, "_shape_text_edit"):
                shape.text = shape.name
                self._shape_text_edit.blockSignals(True)
                self._shape_text_edit.setText(shape.text)
                self._shape_text_edit.blockSignals(False)
            shape.stroke_width = float(self._stroke_spin.value())
            shape.dashed = bool(self._dashed_check.isChecked())
            self._canvas.update()
            # Update shapes list text
            row = self._shapes_list.currentRow()
            if row >= 0:
                item = self._shapes_list.item(row)
                item.setText(f"{shape.shape_type.upper()}: {shape.name or 'Shape'}")

    def _set_selected_shape_color(self, hex_color: str):
        shape = self._canvas.selected_shape()
        if shape:
            shape.color = hex_color
            if shape.shape_type in (ShapeType.POLYGON.value, ShapeType.SECTOR.value):
                # Set matching translucent fill
                qc = QColor(hex_color)
                shape.fill_color = f"rgba({qc.red()}, {qc.green()}, {qc.blue()}, 0.25)"
            self._canvas.update()

    def _on_delete_selected_shape(self):
        shape = self._canvas.selected_shape()
        step = self.current_step()
        if shape and step:
            step.shapes = [s for s in step.shapes if s.id != shape.id]
            self._canvas.set_selected_shape_id(None)
            self._refresh_shapes_list()
            self._canvas.update()
            self.statusMessage.emit("Shape deleted.")

    # ------------------------------------------------------------------
    # Templates, New, Save, Open
    # ------------------------------------------------------------------
    def _on_template_selected(self, key: str):
        from playground.proof_templates import get_template_catalog
        catalogs = get_template_catalog()
        if key in catalogs:
            self._proof = catalogs[key]
            self._active_step_idx = 0
            self._load_proof_into_editor(self._proof)
            self.statusMessage.emit(f"Loaded template: {self._proof.title}")

    def _on_new_proof(self):
        from playground.proof_templates import create_blank_template
        self._proof = create_blank_template()
        self._active_step_idx = 0
        self._load_proof_into_editor(self._proof)
        self.statusMessage.emit("Started new custom theorem proof.")

    def _on_save_json(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Proof to JSON", f"{self._proof.title.replace(' ', '_')}.json", "JSON Files (*.json)"
        )
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(self._proof.to_json())
                self.statusMessage.emit(f"Proof saved to {os.path.basename(filepath)}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Could not save proof: {e}")

    def _on_open_json(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Proof JSON", "", "JSON Files (*.json)"
        )
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = f.read()
                self._proof = BuilderProof.from_json(data)
                self._active_step_idx = 0
                self._load_proof_into_editor(self._proof)
                self.statusMessage.emit(f"Opened proof: {self._proof.title}")
            except Exception as e:
                QMessageBox.critical(self, "Open Error", f"Could not open proof: {e}")

    # ------------------------------------------------------------------
    # Mode Switching & Learn Presentation View
    # ------------------------------------------------------------------
    def switch_mode(self, present: bool):
        self._is_presenting = bool(present)
        self._mode_btn_edit.setChecked(not present)
        self._mode_btn_present.setChecked(present)

        if present:
            self._mode_stack.setCurrentIndex(1)
            self._init_presentation()
            self.statusMessage.emit("Learn Presentation View: Scrub or Play your custom proof.")
        else:
            self._play_timer.stop()
            self._pres_controls.set_playing(False)
            self._mode_stack.setCurrentIndex(0)
            self.select_step(self._active_step_idx)
            self.statusMessage.emit("Editor Mode: Modify steps, shapes, and formulas.")

    def _init_presentation(self):
        self._pres_title.setText(self._proof.title)
        self._pres_step_idx = self._active_step_idx
        self._render_presentation_step(self._pres_step_idx)

    def _render_presentation_step(self, step_idx_0based: int):
        total = len(self._proof.steps)
        if total == 0:
            return

        idx = max(0, min(step_idx_0based, total - 1))
        self._pres_step_idx = idx
        step = self._proof.steps[idx]

        # 1. Update EquationPanel (identical to Learn section!)
        self._pres_equation.display_step(
            step_index_1based=step.index,
            total_steps=total,
            equation=step.equation,
            explanation=step.explanation,
            title=step.title
        )

        # 2. Update VisualizationWidget (vector geometry with lerp transition!)
        rd = step.to_render_data()
        self._pres_canvas.update_step(idx, {"step": step.index}, render_data=rd)

        # 3. Update AnimationControls (timeline progress & step buttons)
        self._pres_controls.set_progress(step.index, total)
        self._pres_controls.set_step_buttons_enabled(idx > 0, idx < total - 1)

    def _pres_step_prev(self):
        if self._pres_step_idx > 0:
            self._render_presentation_step(self._pres_step_idx - 1)

    def _pres_step_next(self):
        total = len(self._proof.steps)
        if self._pres_step_idx < total - 1:
            self._render_presentation_step(self._pres_step_idx + 1)
        else:
            self._play_timer.stop()
            self._pres_controls.set_playing(False)

    def _pres_seek_step(self, target_idx: int):
        self._render_presentation_step(target_idx)

    def _pres_replay(self):
        self._render_presentation_step(0)
        self._pres_controls.set_playing(True)
        interval = int(self.BASE_TICK_MS / max(0.25, self._speed_multiplier))
        self._play_timer.start(interval)

    def _pres_toggle_play(self):
        if self._play_timer.isActive():
            self._play_timer.stop()
            self._pres_controls.set_playing(False)
        else:
            total = len(self._proof.steps)
            if self._pres_step_idx >= total - 1:
                self._pres_step_idx = 0
                self._render_presentation_step(0)
            self._pres_controls.set_playing(True)
            interval = int(self.BASE_TICK_MS / max(0.25, self._speed_multiplier))
            self._play_timer.start(interval)

    def _pres_set_speed(self, speed: float):
        self._speed_multiplier = speed
        if self._play_timer.isActive():
            interval = int(self.BASE_TICK_MS / max(0.25, self._speed_multiplier))
            self._play_timer.start(interval)

    def _on_play_tick(self):
        total = len(self._proof.steps)
        if self._pres_step_idx < total - 1:
            self._render_presentation_step(self._pres_step_idx + 1)
        else:
            self._play_timer.stop()
            self._pres_controls.set_playing(False)

    # ------------------------------------------------------------------
    # PlaygroundHost Integration
    # ------------------------------------------------------------------
    def set_focus_mode(self, on: bool):
        pass

    def set_fullscreen_button(self, on: bool):
        pass

