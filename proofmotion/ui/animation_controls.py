"""
ui/animation_controls.py
--------------------------
Cohesive animation transport toolbar:
- Interactive Step Timeline: visual progression, active step marker, click-to-seek
- Grouped Transport Toolbar: matching button heights, Play as primary action
- Speed multiplier control

Signals:
    previousClicked()
    playPauseClicked()      -- toggle; controller inspects `is_playing()`
    nextClicked()
    replayClicked()
    speedChanged(float)     -- multiplier, e.g. 0.5, 1.0, 2.0
    stepSelected(int)       -- 0-based step index selected via timeline click
"""

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QSlider, QFrame,
)
from PyQt5.QtCore import Qt, pyqtSignal, QPointF, QRectF
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont

from resources.theme import COLORS, get_mono_font


SPEED_STEPS = [0.25, 0.5, 1.0, 1.5, 2.0, 3.0]


class TimelineWidget(QWidget):
    """Interactive visual timeline indicating current step and allowing seek."""
    stepClicked = pyqtSignal(int)  # 0-based step index

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TimelineContainer")
        self.setFixedHeight(38)
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)

        self._current_step = 1  # 1-based
        self._total_steps = 1
        self._hover_step = -1

    def set_step(self, current_step_1based: int, total_steps: int):
        self._current_step = max(1, current_step_1based)
        self._total_steps = max(1, total_steps)
        self.update()

    def setValue(self, val: int):
        self._current_step = max(1, val)
        self.update()

    def value(self) -> int:
        return self._current_step

    def setMaximum(self, max_val: int):
        self._total_steps = max(1, max_val)
        self.update()

    def maximum(self) -> int:
        return self._total_steps

    def setTextVisible(self, visible: bool):
        pass  # compatibility with QProgressBar API

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._total_steps > 1:
            idx = self._pos_to_step(event.pos().x())
            if idx is not None:
                self.stepClicked.emit(idx)

    def mouseMoveEvent(self, event):
        if self._total_steps > 1:
            self._hover_step = self._pos_to_step(event.pos().x())
            self.update()

    def leaveEvent(self, event):
        self._hover_step = -1
        self.update()

    def _pos_to_step(self, px: float) -> int:
        w = self.width()
        margin_x = 90
        track_w = w - margin_x - 30
        if track_w <= 0 or self._total_steps <= 1:
            return 0
        clamped_x = max(margin_x, min(w - 30, px))
        ratio = (clamped_x - margin_x) / track_w
        step_0based = int(round(ratio * (self._total_steps - 1)))
        return max(0, min(self._total_steps - 1, step_0based))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        w = self.width()
        h = self.height()
        cy = h / 2.0

        # Background track card
        bg_rect = QRectF(0, 0, w, h)
        painter.setBrush(QBrush(QColor(COLORS["bg_panel_alt"])))
        painter.setPen(QPen(QColor(COLORS["border_soft"]), 1))
        painter.drawRoundedRect(bg_rect, 6, 6)

        # Label: STEP X OF Y
        painter.setFont(get_mono_font(12, weight=600))
        painter.setPen(QPen(QColor(COLORS["accent_gold"])))
        badge_text = f"STEP {self._current_step}/{self._total_steps}"
        painter.drawText(QRectF(12, 0, 85, h), Qt.AlignLeft | Qt.AlignVCenter, badge_text)

        margin_x = 104
        track_w = w - margin_x - 18
        if track_w <= 10:
            return

        total = max(1, self._total_steps)
        curr = max(1, min(total, self._current_step))

        # Base track
        track_pen = QPen(QColor(COLORS["border"]), 3, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(track_pen)
        painter.drawLine(QPointF(margin_x, cy), QPointF(margin_x + track_w, cy))

        # Progress filled track
        prog_ratio = (curr - 1) / max(1, total - 1) if total > 1 else 1.0
        active_x = margin_x + prog_ratio * track_w

        fill_pen = QPen(QColor(COLORS["accent_teal"]), 3, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(fill_pen)
        painter.drawLine(QPointF(margin_x, cy), QPointF(active_x, cy))

        # Step Markers (nodes)
        if total <= 24:
            for i in range(total):
                step_ratio = i / (total - 1) if total > 1 else 0.5
                nx = margin_x + step_ratio * track_w

                if i + 1 < curr:
                    # Completed
                    painter.setBrush(QBrush(QColor(COLORS["accent_teal"])))
                    painter.setPen(QPen(QColor(COLORS["bg_panel_alt"]), 1.5))
                    painter.drawEllipse(QPointF(nx, cy), 4.5, 4.5)
                elif i + 1 == curr:
                    # Current active step (gold halo & dot)
                    halo_color = QColor(COLORS["accent_gold"])
                    halo_color.setAlpha(45)
                    painter.setBrush(QBrush(halo_color))
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(QPointF(nx, cy), 10, 10)

                    painter.setBrush(QBrush(QColor(COLORS["accent_gold"])))
                    painter.setPen(QPen(QColor("#FFFFFF"), 1.5))
                    painter.drawEllipse(QPointF(nx, cy), 6, 6)
                else:
                    # Upcoming
                    painter.setBrush(QBrush(QColor(COLORS["border_soft"])))
                    painter.setPen(QPen(QColor(COLORS["border"]), 1.5))
                    painter.drawEllipse(QPointF(nx, cy), 3.5, 3.5)
        else:
            # High step counts: sleek cursor handle
            painter.setBrush(QBrush(QColor(COLORS["accent_gold"])))
            painter.setPen(QPen(QColor("#FFFFFF"), 1.5))
            painter.drawEllipse(QPointF(active_x, cy), 6, 6)


class AnimationControls(QWidget):
    previousClicked = pyqtSignal()
    playPauseClicked = pyqtSignal()
    nextClicked = pyqtSignal()
    replayClicked = pyqtSignal()
    speedChanged = pyqtSignal(float)
    stepSelected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TransportBar")
        self._is_playing = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 10, 14, 10)
        outer.setSpacing(8)

        # 1. Timeline Widget (replaces bulky progress bar with interactive step scrubber)
        self._timeline = TimelineWidget(self)
        self._timeline.stepClicked.connect(self.stepSelected.emit)
        outer.addWidget(self._timeline)

        # Compatibility reference
        self._progress = self._timeline

        # 2. Cohesive Transport Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(6)
        toolbar.setContentsMargins(0, 0, 0, 0)

        self._prev_btn = self._make_button("⏮  Prev")
        self._prev_btn.setToolTip("Step backward")
        self._prev_btn.clicked.connect(self.previousClicked.emit)
        toolbar.addWidget(self._prev_btn)

        # Play is the prominent primary action
        self._play_btn = self._make_button("▶  Play", primary=True)
        self._play_btn.setToolTip("Play / Pause animation")
        self._play_btn.clicked.connect(self._on_play_pause_clicked)
        toolbar.addWidget(self._play_btn)

        self._next_btn = self._make_button("Next  ⏭")
        self._next_btn.setToolTip("Step forward")
        self._next_btn.clicked.connect(self.nextClicked.emit)
        toolbar.addWidget(self._next_btn)

        self._replay_btn = self._make_button("↺  Replay")
        self._replay_btn.setToolTip("Restart animation from step 1")
        self._replay_btn.clicked.connect(self.replayClicked.emit)
        toolbar.addWidget(self._replay_btn)

        # Subtle vertical separator
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet(f"color: {COLORS['border']}; margin: 4px 6px;")
        toolbar.addWidget(sep)

        toolbar.addStretch(1)

        speed_label = QLabel("SPEED")
        speed_label.setObjectName("SpeedLabel")
        toolbar.addWidget(speed_label)

        self._speed_slider = QSlider(Qt.Horizontal)
        self._speed_slider.setMinimum(0)
        self._speed_slider.setMaximum(len(SPEED_STEPS) - 1)
        self._speed_slider.setValue(SPEED_STEPS.index(1.0))
        self._speed_slider.setFixedWidth(110)
        self._speed_slider.setPageStep(1)
        self._speed_slider.setCursor(Qt.PointingHandCursor)
        self._speed_slider.valueChanged.connect(self._on_speed_slider_changed)
        toolbar.addWidget(self._speed_slider)

        self._speed_value_label = QLabel("1.0×")
        self._speed_value_label.setObjectName("SpeedBadge")
        self._speed_value_label.setFixedWidth(46)
        self._speed_value_label.setAlignment(Qt.AlignCenter)
        toolbar.addWidget(self._speed_value_label)

        outer.addLayout(toolbar)
        self.set_enabled_all(False)

    def _make_button(self, text: str, primary: bool = False) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("TransportButton")
        if primary:
            btn.setProperty("primary", "true")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(36)
        return btn

    def _on_play_pause_clicked(self):
        self.playPauseClicked.emit()

    def _on_speed_slider_changed(self, index: int):
        speed = SPEED_STEPS[index]
        self._speed_value_label.setText(f"{speed:g}×")
        self.speedChanged.emit(speed)

    # ------------------------------------------------------------------
    # Public API (called by controller)
    # ------------------------------------------------------------------
    def set_playing(self, is_playing: bool):
        self._is_playing = is_playing
        self._play_btn.setText("⏸  Pause" if is_playing else "▶  Play")

    def is_playing(self) -> bool:
        return self._is_playing

    def set_progress(self, current_step_1based: int, total_steps: int):
        self._timeline.set_step(current_step_1based, total_steps)

    def set_enabled_all(self, enabled: bool):
        for w in (self._prev_btn, self._play_btn, self._next_btn,
                  self._replay_btn, self._speed_slider):
            w.setEnabled(enabled)

    def set_step_buttons_enabled(self, prev_enabled: bool, next_enabled: bool):
        self._prev_btn.setEnabled(prev_enabled)
        self._next_btn.setEnabled(next_enabled)
