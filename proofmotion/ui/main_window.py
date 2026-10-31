"""
ui/main_window.py
-------------------
Top-level QMainWindow: Learn/Studio gateway, topic catalog, lesson
workspace, and Studio playground.
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
from playground.ui.playground_host import PlaygroundHost
from ui.home_screens import HomeHost, LEARNING_TOPICS


def create_proofmotion_logo(size: int = 44) -> QPixmap:
    """
    Generate or load the vibrant, dimensional geometric mark for ProofMotion.
    Loads high-res mark from resources/logo.png, falling back to programmatic
    vector rendering if not found.
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
    p.setRenderHint(QPainter.SmoothPixmapTransform, True)

    scale = size / 44.0

    # Rich brand gradient background
    grad = QLinearGradient(0, 0, size, size)
    grad.setColorAt(0.0, QColor("#7760ED"))
    grad.setColorAt(0.5, QColor("#6E57DD"))
    grad.setColorAt(1.0, QColor("#5741C8"))

    # Outer subtle stroke & rich gradient body
    p.setPen(QPen(QColor(255, 255, 255, 40), 1.2 * scale))
    p.setBrush(QBrush(grad))
    p.drawRoundedRect(QRectF(1.0 * scale, 1.0 * scale, (size - 2.0) * scale, (size - 2.0) * scale), 10.5 * scale, 10.5 * scale)

    # Translucent geometric facet (triangle)
    poly = QPolygonF([
        QPointF(10.0 * scale, 33.5 * scale),
        QPointF(33.5 * scale, 33.5 * scale),
        QPointF(10.0 * scale, 10.0 * scale)
    ])
    p.setPen(Qt.NoPen)
    p.setBrush(QBrush(QColor(255, 255, 255, 28)))
    p.drawPolygon(poly)

    # Subtle vector hypotenuse guide line
    guide_pen = QPen(QColor(255, 255, 255, 120), 1.0 * scale, Qt.DashLine)
    p.setPen(guide_pen)
    p.drawLine(QPointF(10.0 * scale, 10.0 * scale), QPointF(33.5 * scale, 33.5 * scale))

    # Coordinate Axes in crisp white with round caps
    axis_pen = QPen(QColor("#FFFFFF"), 2.2 * scale, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    p.setPen(axis_pen)
    p.drawLine(QPointF(10.0 * scale, 33.5 * scale), QPointF(34.0 * scale, 33.5 * scale))
    p.drawLine(QPointF(10.0 * scale, 33.5 * scale), QPointF(10.0 * scale, 9.5 * scale))

    # Stepping pixel blocks (Rasterization / Computation steps)
    p.setPen(QPen(QColor(255, 255, 255, 180), 0.8 * scale))
    p.setBrush(QBrush(QColor("#FFFFFF")))
    px_size = 3.6 * scale
    for gx, gy in [(15.0, 27.5), (20.5, 22.0), (26.5, 16.0)]:
        p.drawRoundedRect(QRectF((gx - 0.5) * scale, (gy - 0.5) * scale, px_size, px_size), 0.8 * scale, 0.8 * scale)

    # Origin node (Bright glowing warm yellow anchor point with white ring)
    p.setPen(QPen(QColor("#FFFFFF"), 1.8 * scale))
    p.setBrush(QBrush(QColor("#FFE57B")))
    p.drawEllipse(QPointF(10.0 * scale, 33.5 * scale), 2.8 * scale, 2.8 * scale)

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
    elif module_key == "curves":
        # Cubic curve with control polygon
        p.setPen(QPen(color, 1.2, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawPolyline(QPolygonF([QPointF(3.0, 15.5), QPointF(7.0, 4.0), QPointF(13.5, 16.5), QPointF(17.5, 5.5)]))
        p.setPen(QPen(color, 1.9, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        p.drawArc(QRectF(2.2, 4.0, 16.0, 13.0), 200 * 16, 150 * 16)
        p.setBrush(QBrush(color))
        p.setPen(Qt.NoPen)
        for gx, gy in [(3.0, 15.5), (7.0, 4.0), (13.5, 16.5), (17.5, 5.5)]:
            p.drawEllipse(QPointF(gx, gy), 1.7, 1.7)
    elif module_key == "projections_3d":
        # Isometric / perspective wireframe cube
        p.setPen(QPen(color, 1.4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        # Front face
        p.drawPolygon(QPolygonF([QPointF(10.0, 2.5), QPointF(16.5, 6.0), QPointF(10.0, 9.5), QPointF(3.5, 6.0)])) # top diamond
        p.drawPolyline(QPolygonF([QPointF(3.5, 6.0), QPointF(3.5, 13.5), QPointF(10.0, 17.5), QPointF(10.0, 9.5)])) # left face
        p.drawPolyline(QPolygonF([QPointF(16.5, 6.0), QPointF(16.5, 13.5), QPointF(10.0, 17.5)])) # right face
    elif module_key == "playground":
        p.setPen(QPen(color, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        p.drawRect(QRectF(3.0, 3.0, 14.0, 14.0))
        p.drawPolygon(QPolygonF([QPointF(6.0, 14.0), QPointF(11.5, 14.0), QPointF(8.8, 8.5)]))
        p.drawEllipse(QRectF(11.2, 4.5, 4.6, 4.6))

    p.end()
    return QIcon(pix)


def create_studio_icon(color_hex: str = "#FFFFFF") -> QIcon:
    """Four-point spark used only for the Studio launch control."""
    pix = QPixmap(18, 18)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing, True)
    color = QColor(color_hex)
    p.setPen(QPen(color, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(QBrush(color))
    spark = QPolygonF([
        QPointF(9.0, 1.5), QPointF(10.6, 7.4), QPointF(16.5, 9.0),
        QPointF(10.6, 10.6), QPointF(9.0, 16.5), QPointF(7.4, 10.6),
        QPointF(1.5, 9.0), QPointF(7.4, 7.4),
    ])
    p.drawPolygon(spark)
    p.end()
    return QIcon(pix)


MODULE_TITLES = {key: title for key, title, _caption, _meta in LEARNING_TOPICS}


class MainWindow(QMainWindow):
    moduleSelected = pyqtSignal(str)
    homeRequested = pyqtSignal()

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

        self.playground_host = PlaygroundHost()
        self.playground_host.statusMessage.connect(self.set_status)
        self.playground_host.fullscreenToggled.connect(self.toggle_canvas_fullscreen)
        self.playground_host.modeChanged.connect(self._set_studio_mode_chips)

        self.home_host = HomeHost()
        self.home_host.learnChosen.connect(self.show_catalog)
        self.home_host.studioChosen.connect(self._on_studio_open_from_home)
        self.home_host.topicChosen.connect(self._on_module_clicked)
        self._module_buttons = self.home_host._module_buttons

        self._workspace_stack = QStackedWidget()
        self._workspace_stack.addWidget(self.home_host)         # 0: Learn / Studio home
        self._workspace_stack.addWidget(self._body_widget)      # 1: lesson workspace
        self._workspace_stack.addWidget(self.playground_host)   # 2: Studio
        root.addWidget(self._workspace_stack, stretch=1)
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
        self.show_home()

    # ------------------------------------------------------------------
    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("AppHeader")
        header.setFixedHeight(74)

        header_row = QHBoxLayout(header)
        header_row.setContentsMargins(24, 10, 24, 10)
        header_row.setSpacing(16)

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

        self._title_label = QLabel()
        self._title_label.setObjectName("AppTitle")
        self._title_label.setTextFormat(Qt.RichText)
        self._title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._set_wordmark(studio=False)

        self._subtitle_label = QLabel("FROM THEORY TO MOTION")
        self._subtitle_label.setObjectName("AppSubtitle")
        self._subtitle_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        title_col.addWidget(self._title_label)
        title_col.addWidget(self._subtitle_label)
        brand_row.addWidget(title_widget, alignment=Qt.AlignVCenter)
        header_row.addWidget(brand, alignment=Qt.AlignVCenter)

        self._home_back_btn = QPushButton("←  Learn")
        self._home_back_btn.setObjectName("HomeBackButton")
        self._home_back_btn.setCursor(Qt.PointingHandCursor)
        self._home_back_btn.clicked.connect(self._on_home_back)
        self._home_back_btn.hide()
        header_row.addWidget(self._home_back_btn, alignment=Qt.AlignVCenter)

        self._module_chip = QPushButton("Algorithms")
        self._module_chip.setObjectName("LessonModuleChip")
        self._module_chip.setCheckable(False)
        self._module_chip.setEnabled(False)
        self._module_chip.hide()
        header_row.addWidget(self._module_chip, alignment=Qt.AlignVCenter)

        header_row.addStretch(1)

        self._nav_pill_bar = QWidget()
        self._nav_pill_bar.setObjectName("NavPillBar")
        self._nav_pill_bar.hide()
        self._module_buttons = {}
        header_row.addWidget(self._nav_pill_bar)

        self._studio_mode_bar = QWidget()
        self._studio_mode_bar.setObjectName("StudioModeBar")
        mode_row = QHBoxLayout(self._studio_mode_bar)
        mode_row.setContentsMargins(4, 4, 4, 4)
        mode_row.setSpacing(2)
        self._studio_mode_buttons = {}
        for key, label in (("2d", "2D"), ("3d", "3D"), ("basis", "Basis"), ("lift", "Lift"), ("run", "Run")):
            chip = QPushButton(label)
            chip.setObjectName("StudioModeChip")
            chip.setCheckable(True)
            chip.setCursor(Qt.PointingHandCursor)
            chip.clicked.connect(lambda _=False, k=key: self._on_studio_mode_clicked(k))
            mode_row.addWidget(chip)
            self._studio_mode_buttons[key] = chip
        self._studio_mode_bar.hide()
        header_row.addWidget(self._studio_mode_bar, alignment=Qt.AlignVCenter)

        self._studio_leave_btn = QPushButton("  Leave Studio")
        self._studio_leave_btn.setObjectName("StudioLeaveButton")
        self._studio_leave_btn.setCursor(Qt.PointingHandCursor)
        self._studio_leave_btn.setToolTip("Leave Studio and go back")
        self._studio_leave_btn.clicked.connect(self._on_studio_leave)
        self._studio_leave_btn.hide()
        header_row.addWidget(self._studio_leave_btn, alignment=Qt.AlignVCenter)

        self._studio_open_btn = QPushButton("  Studio")
        self._studio_open_btn.setObjectName("StudioLaunchButton")
        self._studio_open_btn.setCursor(Qt.PointingHandCursor)
        self._studio_open_btn.setIcon(create_studio_icon("#FFFFFF"))
        self._studio_open_btn.setIconSize(QSize(16, 16))
        self._studio_open_btn.setToolTip("Leave the lessons and make something yourself")
        self._studio_open_btn.clicked.connect(self._on_studio_open)
        header_row.addWidget(self._studio_open_btn, alignment=Qt.AlignVCenter)

        self._last_lesson_module = "algorithms"
        self._studio_return = "home"
        self._surface = "gateway"
        return header

    def _on_module_clicked(self, module_key: str):
        self.select_module(module_key)
        self.moduleSelected.emit(module_key)

    def _on_studio_open(self):
        if self.lessons_active():
            self._studio_return = "lesson"
        elif self.home_active() and self.home_host.on_catalog():
            self._studio_return = "catalog"
        else:
            self._studio_return = "home"
        self._on_module_clicked("playground")

    def _on_studio_open_from_home(self):
        self._studio_return = "home"
        self._on_module_clicked("playground")

    def _on_studio_leave(self):
        if self._studio_return == "lesson" and self._last_lesson_module:
            self._on_module_clicked(self._last_lesson_module)
        elif self._studio_return == "catalog":
            self.show_catalog()
            self.homeRequested.emit()
        else:
            self.show_home()
            self.homeRequested.emit()

    def _on_home_back(self):
        if self.lessons_active():
            self.show_catalog()
            self.homeRequested.emit()
        else:
            self.show_home()
            self.homeRequested.emit()

    def _on_studio_mode_clicked(self, kind: str):
        if hasattr(self, "playground_host"):
            self.playground_host.open_mode(kind)
        self._set_studio_mode_chips(kind)

    def _set_wordmark(self, studio: bool):
        if studio:
            self._title_label.setText(
                '<span style="color: #F8FAFC; font-weight: 800; letter-spacing: -0.5px;">Proof</span>'
                '<span style="color: #6F5BEF; font-weight: 800; letter-spacing: -0.5px;">Motion</span>'
            )
        else:
            self._title_label.setText(
                '<span style="color: #0D172C; font-weight: 800; letter-spacing: -0.5px;">Proof</span>'
                '<span style="color: #6F5BEF; font-weight: 800; letter-spacing: -0.5px;">Motion</span>'
            )

    def _set_studio_mode_chips(self, kind: str):
        for key, chip in self._studio_mode_buttons.items():
            on = key == kind
            chip.setChecked(on)
            chip.setProperty("selected", "true" if on else "false")
            chip.style().unpolish(chip)
            chip.style().polish(chip)

    def _apply_widget_flag(self, widget, name: str, on: bool):
        widget.setProperty(name, "true" if on else "false")
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    def set_studio_chrome(self, on: bool, mode: str = "2d"):
        if on:
            self.set_surface_chrome("studio", studio_mode=mode)
        else:
            self.set_surface_chrome("lesson")

    def set_surface_chrome(self, surface: str, studio_mode: str = "2d"):
        self._surface = surface
        studio = surface == "studio"
        self._apply_widget_flag(self._header_widget, "studio", studio)
        self._apply_widget_flag(self._status_bar, "studio", studio)
        self._set_wordmark(studio)
        self._subtitle_label.setText("FROM THEORY TO MOTION • STUDIO" if studio else "FROM THEORY TO MOTION")
        self._nav_pill_bar.hide()
        self._studio_mode_bar.setVisible(studio)
        self._studio_leave_btn.setVisible(studio)
        self._studio_open_btn.setVisible(surface in ("catalog", "lesson"))
        self._home_back_btn.setVisible(surface in ("catalog", "lesson"))
        if surface == "catalog":
            self._home_back_btn.setText("←  Home")
        else:
            self._home_back_btn.setText("←  Learn")
        self._module_chip.setVisible(surface == "lesson")
        if studio:
            self._set_studio_mode_chips(studio_mode)

    def select_module(self, module_key: str):
        if module_key != "playground":
            self._last_lesson_module = module_key
            self._module_chip.setText(MODULE_TITLES.get(module_key, module_key.replace("_", " ").title()))
        if hasattr(self, "home_host"):
            self.home_host.set_selected_topic(module_key)

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
        from ui.bezier_quiz_widget import BezierQuizWidget
        self.quiz_widget = BezierQuizWidget()
        self.canvas_stack.addWidget(self.visualization_widget) # Index 0: 2D QPainter canvas
        self.canvas_stack.addWidget(self.opengl_widget)        # Index 1: 3D Hardware OpenGL canvas
        self.canvas_stack.addWidget(self.quiz_widget)          # Index 2: Interactive Quiz widget

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

    def show_home(self):
        self.home_host.show_gateway()
        self._workspace_stack.setCurrentIndex(0)
        self.set_surface_chrome("gateway")
        self.set_status("Welcome — Learn a topic, or open Studio.")

    def show_catalog(self):
        self.home_host.show_catalog()
        self._workspace_stack.setCurrentIndex(0)
        self.set_surface_chrome("catalog")
        self.set_status("Choose a topic to open its lesson workspace.")

    def show_playground(self):
        self._workspace_stack.setCurrentIndex(2)
        self.playground_host.enter()
        self.set_studio_chrome(True, self.playground_host.current_mode())

    def show_lessons(self):
        self._workspace_stack.setCurrentIndex(1)
        self.set_surface_chrome("lesson")

    def home_active(self) -> bool:
        return self._workspace_stack.currentIndex() == 0

    def lessons_active(self) -> bool:
        return self._workspace_stack.currentIndex() == 1

    def playground_active(self) -> bool:
        return self._workspace_stack.currentIndex() == 2

    def set_active_renderer(self, mode: str):
        """Switch active canvas between '2d' (QPainter), 'opengl' (QOpenGLWidget), and 'quiz' (BezierQuizWidget)."""
        if mode == "opengl":
            self.canvas_stack.setCurrentIndex(1)
            self.opengl_widget.update()
        elif mode == "quiz":
            self.canvas_stack.setCurrentIndex(2)
        else:
            self.canvas_stack.setCurrentIndex(0)
            self.visualization_widget.update()

    def get_active_renderer(self) -> str:
        """Return 'opengl' if OpenGL canvas is active, 'quiz' if Quiz widget is active, else '2d'."""
        if self.canvas_stack.currentIndex() == 1:
            return "opengl"
        elif self.canvas_stack.currentIndex() == 2:
            return "quiz"
        return "2d"

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
        playground_on = self.playground_active()
        if is_fullscreen:
            self._saved_splitter_sizes = self._main_splitter.sizes()
            self._header_widget.hide()
            self._status_bar.hide()
            if playground_on:
                self.playground_host.set_focus_mode(True)
                self.set_status("Focus Mode: studio canvas (Press Esc to restore)")
            else:
                self.theorem_panel.hide()
                self.parameter_panel.hide()
                self.equation_panel.hide()
                self.view_controls.set_fullscreen_state(True)
                self.set_status("Focus Mode: canvas, steps, and playback (Press Esc to restore)")
        else:
            self._header_widget.show()
            self._status_bar.show()
            if playground_on:
                self.playground_host.set_focus_mode(False)
            else:
                self.theorem_panel.show()
                self.parameter_panel.show()
                self.equation_panel.show()
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
