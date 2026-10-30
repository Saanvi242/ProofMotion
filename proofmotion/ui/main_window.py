"""
ui/main_window.py
-------------------
Top-level QMainWindow that assembles the header with module navigation,
topic sidebar, parameter panel, visualization area, view controls,
animation controls, and equation panel into ProofMotion's layout.
"""

import os

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSplitter,
    QPushButton, QStatusBar, QShortcut, QStackedWidget, QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import Qt, pyqtSignal, QPointF, QRectF, QSize
from PyQt5.QtGui import (
    QResizeEvent, QIcon, QPixmap, QPainter, QPolygonF, QColor, QPen, QBrush,
    QKeySequence, QLinearGradient,
)

from resources.theme import build_stylesheet, COLORS
from resources.geo_background import GeoBackground

from ui.theorem_panel import TheoremPanel
from ui.parameter_panel import ParameterPanel
from ui.equation_panel import EquationPanel
from ui.animation_controls import AnimationControls
from ui.view_controls import ViewControls
from ui.clipping_tabs import ClippingTabBar

from graphics.visualization_widget import VisualizationWidget
from graphics.opengl_widget import OpenGL3DWidget


def create_proofmotion_logo(size: int = 44) -> QPixmap:
    """
    Generate or load the vibrant, dimensional geometric mark for ProofMotion.
    Loads high-res 3D icon with subtle lighting and glowing cyan vectors,
    falling back to programmatic vector rendering if not found.
    """
    logo_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "logo.png")
    if os.path.isfile(logo_file):
        pix = QPixmap(logo_file)
        if not pix.isNull():
            return pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing, True)

    scale = size / 42.0

    # Rich brand gradient background
    grad = QLinearGradient(0, 0, size, size)
    grad.setColorAt(0.0, QColor("#6C5CE7"))   # Electric purple
    grad.setColorAt(1.0, QColor("#4D3BB8"))   # Deep rich indigo

    # Outer subtle stroke & rich gradient body
    p.setPen(QPen(QColor(255, 255, 255, 50), 1.2 * scale))
    p.setBrush(QBrush(grad))
    p.drawRoundedRect(QRectF(1.0 * scale, 1.0 * scale, (size - 2.0) * scale, (size - 2.0) * scale), 11.0 * scale, 11.0 * scale)

    # Translucent geometric facet (triangle)
    poly = QPolygonF([
        QPointF(9.5 * scale, 32.0 * scale),
        QPointF(32.0 * scale, 32.0 * scale),
        QPointF(9.5 * scale, 9.5 * scale)
    ])
    p.setPen(Qt.NoPen)
    p.setBrush(QBrush(QColor(255, 255, 255, 26)))
    p.drawPolygon(poly)

    # Subtle vector hypotenuse guide line
    guide_pen = QPen(QColor(255, 255, 255, 80), 1.0 * scale, Qt.DashLine)
    p.setPen(guide_pen)
    p.drawLine(QPointF(9.5 * scale, 9.5 * scale), QPointF(32.0 * scale, 32.0 * scale))

    # Coordinate Axes in crisp white with round caps
    axis_pen = QPen(QColor("#FFFFFF"), 2.2 * scale, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    p.setPen(axis_pen)
    p.drawLine(QPointF(9.5 * scale, 32.0 * scale), QPointF(33.5 * scale, 32.0 * scale))
    p.drawLine(QPointF(9.5 * scale, 32.0 * scale), QPointF(9.5 * scale, 8.0 * scale))

    # Stepping pixel blocks (Rasterization / Computation steps)
    p.setPen(QPen(QColor(255, 255, 255, 140), 0.8 * scale))
    p.setBrush(QBrush(QColor("#FFFFFF")))
    px_size = 4.4 * scale
    for gx, gy in [(12.0, 12.0), (17.5, 17.5), (23.5, 23.5)]:
        p.drawRoundedRect(QRectF((gx - 0.5) * scale, (gy - 0.5) * scale, px_size, px_size), 1.2 * scale, 1.2 * scale)

    # Origin node (Bright glowing cyan anchor point)
    p.setBrush(QBrush(QColor("#00F5D4")))
    p.setPen(QPen(QColor("#FFFFFF"), 1.6 * scale))
    p.drawEllipse(QPointF(9.5 * scale, 32.0 * scale), 2.8 * scale, 2.8 * scale)

    p.end()
    return pix


def create_module_icon(module_key: str, color_hex: str = "#8FA3B8") -> QIcon:
    """Generate crisp, professional vector icons for modules without emojis."""
    pix = QPixmap(20, 20)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing, True)
    color = QColor(color_hex)
    pen = QPen(color, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    p.setPen(pen)

    if module_key == "theorems":
        # Geometric right-angle triangle
        p.setBrush(Qt.NoBrush)
        p.drawPolygon(QPolygonF([QPointF(3.5, 16.5), QPointF(16.5, 16.5), QPointF(3.5, 3.5)]))
        p.drawPolyline(QPolygonF([QPointF(3.5, 12.0), QPointF(8.0, 12.0), QPointF(8.0, 16.5)]))
    elif module_key == "algorithms":
        # Ascending algorithm bars
        p.setBrush(QBrush(color))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(QRectF(3.0, 11.0, 3.5, 6.0), 1, 1)
        p.drawRoundedRect(QRectF(8.2, 7.0, 3.5, 10.0), 1, 1)
        p.drawRoundedRect(QRectF(13.5, 3.0, 3.5, 14.0), 1, 1)
    elif module_key == "transformations":
        # Coordinate axes with rotation arrow arc
        p.drawLine(QPointF(10.0, 2.5), QPointF(10.0, 17.5))
        p.drawLine(QPointF(2.5, 10.0), QPointF(17.5, 10.0))
        p.drawArc(QRectF(4.0, 4.0, 12.0, 12.0), 30 * 16, 200 * 16)
        p.setBrush(QBrush(color))
        p.drawPolygon(QPolygonF([QPointF(10.0, 2.5), QPointF(7.0, 6.0), QPointF(13.0, 6.0)]))
    elif module_key == "rasterization":
        # 3x3 pixel raster grid
        p.setPen(QPen(color, 1.0))
        p.setBrush(Qt.NoBrush)
        for gx in range(3):
            for gy in range(3):
                rx = 2.5 + gx * 5.2
                ry = 2.5 + gy * 5.2
                if (gx == gy) or (gx == 1 and gy == 1):
                    p.fillRect(QRectF(rx, ry, 4.2, 4.2), QBrush(color))
                else:
                    p.drawRect(QRectF(rx, ry, 4.2, 4.2))
    elif module_key == "clipping":
        # Window box with clipped line
        p.setPen(QPen(color, 1.4))
        p.setBrush(Qt.NoBrush)
        p.drawRect(QRectF(4.0, 4.0, 12.0, 12.0))
        p.setPen(QPen(color, 1.8, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(QPointF(2.0, 17.5), QPointF(18.0, 2.5))
        p.setPen(QPen(QColor(COLORS["accent_gold"]), 2.2))
        p.drawPoint(QPointF(4.0, 15.5))
        p.drawPoint(QPointF(16.0, 4.5))
    elif module_key == "image_processing":
        # Photo frame with mountains and sun
        p.setPen(QPen(color, 1.5))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(QRectF(2.5, 3.5, 15.0, 13.0), 1.5, 1.5)
        # Small circle / sun
        p.setBrush(QBrush(color))
        p.drawEllipse(QPointF(6.0, 7.0), 1.5, 1.5)
        # Mountain peaks
        p.setBrush(Qt.NoBrush)
        p.drawPolyline(QPolygonF([QPointF(3.5, 14.5), QPointF(8.0, 9.5), QPointF(11.5, 13.0), QPointF(14.0, 10.5), QPointF(16.5, 14.5)]))
    elif module_key == "projections_3d":
        # Isometric / perspective wireframe cube
        p.setPen(QPen(color, 1.4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        # Front face
        p.drawPolygon(QPolygonF([QPointF(10.0, 2.5), QPointF(16.5, 6.0), QPointF(10.0, 9.5), QPointF(3.5, 6.0)])) # top diamond
        p.drawPolyline(QPolygonF([QPointF(3.5, 6.0), QPointF(3.5, 13.5), QPointF(10.0, 17.5), QPointF(10.0, 9.5)])) # left face
        p.drawPolyline(QPolygonF([QPointF(16.5, 6.0), QPointF(16.5, 13.5), QPointF(10.0, 17.5)])) # right face

    p.end()
    return QIcon(pix)


class MainWindow(QMainWindow):
    moduleSelected = pyqtSignal(str)

    def __init__(self, theorems, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ProofMotion — Interactive Mathematics, Algorithms & Computer Graphics")
        self.resize(1440, 900)
        self.setMinimumSize(1080, 680)
        self.setStyleSheet(build_stylesheet())

        # Simple direct background image path
        image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "backgroungimage.jpg")
        self._geo_background = GeoBackground(self, image_path=image_path)
        self._geo_background.lower()

        central = QWidget()
        central.setObjectName("CentralHost")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._header_widget = self._build_header()
        root.addWidget(self._header_widget)

        self._body_widget = QWidget()
        body_layout = QVBoxLayout(self._body_widget)
        body_layout.setContentsMargins(18, 16, 18, 16)
        body_layout.setSpacing(14)

        self._main_splitter = self._build_main_row(theorems)
        body_layout.addWidget(self._main_splitter, stretch=6)
        self.equation_panel = EquationPanel()
        self.equation_panel.setObjectName("EquationPanel")
        self.equation_panel.setAttribute(Qt.WA_StyledBackground, True)
        self.equation_panel.setMinimumHeight(172)
        self.equation_panel.setMaximumHeight(300)
        body_layout.addWidget(self.equation_panel, stretch=1)

        root.addWidget(self._body_widget, stretch=1)
        self._status_bar = self._build_status_bar()
        root.addWidget(self._status_bar)

        self._is_canvas_fullscreen = False
        self._saved_splitter_sizes = [230, 880, 250]

        # Shortcuts for fullscreen / focus mode
        esc_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        esc_shortcut.activated.connect(self._exit_fullscreen_if_active)
        f11_shortcut = QShortcut(QKeySequence(Qt.Key_F11), self)
        f11_shortcut.activated.connect(self._toggle_fullscreen_shortcut)

        self._geo_background.lower()

    # ------------------------------------------------------------------
    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("AppHeader")
        header.setFixedHeight(74)

        header_row = QHBoxLayout(header)
        header_row.setContentsMargins(36, 10, 36, 10)
        header_row.setSpacing(24)

        brand = QWidget()
        brand_row = QHBoxLayout(brand)
        brand_row.setContentsMargins(0, 0, 0, 0)
        brand_row.setSpacing(14)
        brand_row.setAlignment(Qt.AlignVCenter)

        logo = QLabel()
        logo.setPixmap(create_proofmotion_logo(44))
        logo.setFixedSize(44, 44)
        brand_row.addWidget(logo, alignment=Qt.AlignVCenter)

        title_widget = QWidget()
        title_col = QVBoxLayout(title_widget)
        title_col.setContentsMargins(0, 0, 0, 0)
        title_col.setSpacing(2)
        title_col.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        title = QLabel()
        title.setObjectName("AppTitle")
        title.setTextFormat(Qt.RichText)
        title.setText('<span style="color: #0F172A; font-weight: 700;">Proof</span><span style="color: #6C5CE7; font-weight: 700;">Motion</span>')
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        subtitle = QLabel("FROM THEORY TO VISUALIZATION.")
        subtitle.setObjectName("AppSubtitle")
        subtitle.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        brand_row.addWidget(title_widget, alignment=Qt.AlignVCenter)
        header_row.addWidget(brand, alignment=Qt.AlignVCenter)
        header_row.addStretch(1)

        pill_bar = QWidget()
        pill_bar.setObjectName("NavPillBar")
        nav_row = QHBoxLayout(pill_bar)
        nav_row.setContentsMargins(4, 4, 4, 4)
        nav_row.setSpacing(2)

        self._module_buttons = {}
        modules = [
            ("theorems", "Theorems"),
            ("algorithms", "Algorithms"),
            ("transformations", "Transformations"),
            ("rasterization", "Rasterization"),
            ("clipping", "Clipping"),
        ]

        for mod_key, mod_name in modules:
            btn = QPushButton(f"  {mod_name}")
            btn.setObjectName("NavTab")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setIcon(create_module_icon(mod_key, "#7B849A"))
            btn.setIconSize(QSize(16, 16))
            btn.clicked.connect(lambda ch, k=mod_key: self._on_module_clicked(k))
            nav_row.addWidget(btn)
            self._module_buttons[mod_key] = btn

        header_row.addWidget(pill_bar, alignment=Qt.AlignVCenter)
        return header

    def _on_module_clicked(self, module_key: str):
        self.select_module(module_key)
        self.moduleSelected.emit(module_key)

    def select_module(self, module_key: str):
        for k, btn in self._module_buttons.items():
            sel = (k == module_key)
            btn.setChecked(sel)
            btn.setProperty("selected", "true" if sel else "false")
            icon_color = COLORS["accent_gold_pressed"] if sel else "#7B849A"
            btn.setIcon(create_module_icon(k, icon_color))
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _build_main_row(self, theorems) -> QWidget:
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(12)
        splitter.setStyleSheet("QSplitter::handle { background: transparent; }")

        self.theorem_panel = TheoremPanel(theorems)
        self.theorem_panel.setMinimumWidth(205)
        self.theorem_panel.setMaximumWidth(280)

        viz_container = self._build_visualization_container()

        self.parameter_panel = ParameterPanel()
        self.parameter_panel.setMinimumWidth(280)
        self.parameter_panel.setMaximumWidth(360)

        # Wire sorting style synchronization between view controls and parameter panel
        self.parameter_panel.sortingStyleRequested.connect(self.view_controls.set_sorting_style)
        self.parameter_panel.sortingStyleRequested.connect(self.visualization_widget.set_sorting_style)
        self.view_controls.sortingStyleChanged.connect(self.parameter_panel.set_current_sort_style)

        splitter.addWidget(self.theorem_panel)
        splitter.addWidget(viz_container)
        splitter.addWidget(self.parameter_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([215, 850, 300])

        return splitter

    def _build_visualization_container(self) -> QWidget:
        container = QWidget()
        container.setObjectName("CentralWorkspace")
        container.setAttribute(Qt.WA_StyledBackground, True)

        shadow = QGraphicsDropShadowEffect(container)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(32, 48, 79, 12))  # ~0.045 subtle blue-navy tint
        shadow.setOffset(0, 2)
        container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        header_row = QHBoxLayout()
        title = QLabel("Visualization")
        title.setObjectName("PanelTitle")
        header_row.addWidget(title)
        header_row.addStretch(1)

        self.view_controls = ViewControls()
        header_row.addWidget(self.view_controls)
        layout.addLayout(header_row)

        self.clipping_tab_bar = ClippingTabBar()
        self.clipping_tab_bar.hide()
        layout.addWidget(self.clipping_tab_bar, stretch=0)

        self.canvas_stack = QStackedWidget()
        self.canvas_stack.setObjectName("CanvasStack")
        self.visualization_widget = VisualizationWidget()
        self.opengl_widget = OpenGL3DWidget()
        self.canvas_stack.addWidget(self.visualization_widget) # Index 0: 2D QPainter canvas
        self.canvas_stack.addWidget(self.opengl_widget)        # Index 1: 3D Hardware OpenGL canvas

        self.view_controls.gridToggled.connect(self.visualization_widget.set_show_grid)
        self.view_controls.gridToggled.connect(self.opengl_widget.set_show_grid)
        self.view_controls.fullscreenToggled.connect(self.toggle_canvas_fullscreen)
        self.view_controls.sortingStyleChanged.connect(self.visualization_widget.set_sorting_style)
        self.view_controls.reducedMotionToggled.connect(self.visualization_widget.set_sorting_reduced_motion)
        layout.addWidget(self.canvas_stack, stretch=1)

        self.animation_controls = AnimationControls()
        layout.addWidget(self.animation_controls, stretch=0)

        return container

    def set_zoom_controls_visible(self, visible: bool):
        self.view_controls.set_zoom_controls_visible(visible)

    def set_sorting_controls_visible(self, visible: bool):
        self.view_controls.set_sorting_controls_visible(visible)

    def set_clipping_tabs_visible(self, visible: bool):
        self.clipping_tab_bar.setVisible(visible)

    def set_active_renderer(self, mode: str):
        """Switch active canvas between '2d' (QPainter) and 'opengl' (QOpenGLWidget)."""
        if mode == "opengl":
            self.canvas_stack.setCurrentIndex(1)
            self.opengl_widget.update()
        else:
            self.canvas_stack.setCurrentIndex(0)
            self.visualization_widget.update()

    def get_active_renderer(self) -> str:
        """Return 'opengl' if OpenGL canvas is active, else '2d'."""
        return "opengl" if self.canvas_stack.currentIndex() == 1 else "2d"

    @property
    def vis_stack(self):
        return self.canvas_stack

    def _build_status_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("StatusBar")
        bar.setFixedHeight(28)
        row = QHBoxLayout(bar)
        row.setContentsMargins(16, 0, 16, 0)

        dot = QWidget()
        dot.setObjectName("StatusDot")
        row.addWidget(dot)

        self.status_label = QLabel("")
        row.addWidget(self.status_label)
        row.addStretch(1)

        return bar

    def set_status(self, text: str):
        self.status_label.setText(text)

    # ------------------------------------------------------------------
    # Fullscreen / Focus Mode
    # ------------------------------------------------------------------
    def toggle_canvas_fullscreen(self, is_fullscreen: bool):
        self._is_canvas_fullscreen = is_fullscreen
        if is_fullscreen:
            self._saved_splitter_sizes = self._main_splitter.sizes()
            self._header_widget.hide()
            self.theorem_panel.hide()
            self.parameter_panel.hide()
            self.equation_panel.hide()
            self._status_bar.hide()
            self.view_controls.set_fullscreen_state(True)
            self.set_status("Focus Mode: canvas, steps, and playback (Press Esc to restore)")
        else:
            self._header_widget.show()
            self.theorem_panel.show()
            self.parameter_panel.show()
            self.equation_panel.show()
            self._status_bar.show()
            if hasattr(self, "_saved_splitter_sizes") and self._saved_splitter_sizes:
                self._main_splitter.setSizes(self._saved_splitter_sizes)
            self.view_controls.set_fullscreen_state(False)

    def _exit_fullscreen_if_active(self):
        if getattr(self, "_is_canvas_fullscreen", False):
            self.toggle_canvas_fullscreen(False)

    def _toggle_fullscreen_shortcut(self):
        new_state = not getattr(self, "_is_canvas_fullscreen", False)
        self.toggle_canvas_fullscreen(new_state)

    # ------------------------------------------------------------------
    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self._geo_background.setGeometry(self.rect())
