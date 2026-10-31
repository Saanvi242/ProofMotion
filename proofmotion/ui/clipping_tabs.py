"""
ui/clipping_tabs.py
-------------------
Lesson navigator shared by Cohen–Sutherland and Sutherland–Hodgman.

Two-line chips keep the title and subtitle inside the tab so they never
hang into the canvas.
"""

from typing import Dict, List, Tuple
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QStyle, QStyleOption
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QCursor, QPainter

from resources.theme import get_ui_font

COHEN_TABS: List[Tuple[str, str, str]] = [
    ("region_codes", "1  Region Codes", "What each bit means"),
    ("clip_line", "2  Clip a Line", "Watch the algorithm"),
]

HODGMAN_TABS: List[Tuple[str, str, str]] = [
    ("four_cases", "1  Four Cases", "Keep, cut, or add a vertex"),
    ("clip_polygon", "2  Clip a Polygon", "One boundary at a time"),
]


class LessonTabChip(QFrame):
    """Self-contained two-line lesson tab chip with guaranteed background painting."""
    clicked = pyqtSignal(str)

    def __init__(self, key: str, title: str, hint: str, parent=None):
        super().__init__(parent)
        self.key = key
        self.setObjectName("ClippingTabChip")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.setFixedHeight(52)
        self._active = False

        col = QVBoxLayout(self)
        col.setContentsMargins(13, 5, 13, 5)
        col.setSpacing(2)

        self._title = QLabel(title)
        self._title.setObjectName("ClippingTabTitle")
        self._title.setFont(get_ui_font(12, weight=600))
        self._title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        col.addWidget(self._title)

        self._hint = QLabel(hint)
        self._hint.setObjectName("ClippingTabHint")
        self._hint.setFont(get_ui_font(10, weight=400))
        self._hint.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        col.addWidget(self._hint)

        self.set_active(False)

    def sizeHint(self) -> QSize:
        return QSize(max(130, super().sizeHint().width()), 52)

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)
        super().paintEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.key)
        super().mousePressEvent(event)

    def set_active(self, active: bool):
        self._active = active
        if active:
            self.setStyleSheet("""
                QFrame#ClippingTabChip {
                    background-color: #6C5CE7;
                    border: 1.5px solid #5B4BD4;
                    border-radius: 10px;
                }
                QLabel#ClippingTabTitle {
                    color: #FFFFFF;
                    font-weight: 600;
                    background: transparent;
                }
                QLabel#ClippingTabHint {
                    color: #EDE9FE;
                    font-weight: 400;
                    background: transparent;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame#ClippingTabChip {
                    background-color: #FFFFFF;
                    border: 1.5px solid #E2E8F0;
                    border-radius: 10px;
                }
                QFrame#ClippingTabChip:hover {
                    background-color: #F8FAFC;
                    border-color: #CBD5E1;
                }
                QLabel#ClippingTabTitle {
                    color: #1E293B;
                    font-weight: 600;
                    background: transparent;
                }
                QLabel#ClippingTabHint {
                    color: #64748B;
                    font-weight: 400;
                    background: transparent;
                }
            """)


class ClippingTabBar(QWidget):
    """Configurable two-stage lesson switcher for clipping topics."""
    tabChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ClippingTabBar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedHeight(58)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._active_tab = "region_codes"
        self._buttons: Dict[str, LessonTabChip] = {}
        self._tab_defs: List[Tuple[str, str, str]] = list(COHEN_TABS)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 2, 0, 4)
        self._layout.setSpacing(8)
        self._rebuild()

    def setVisible(self, visible: bool):
        super().setVisible(visible)
        if visible:
            for chip in self._buttons.values():
                chip.show()

    def current_tab(self) -> str:
        return self._active_tab

    def set_tabs(self, tabs: List[Tuple[str, str, str]], active_key: str = None, emit_signal: bool = False):
        self._tab_defs = list(tabs)
        preferred = active_key or (tabs[0][0] if tabs else "")
        self._active_tab = preferred if any(k == preferred for k, _, _ in tabs) else (tabs[0][0] if tabs else "")
        self._rebuild()
        if emit_signal and self._active_tab:
            self.tabChanged.emit(self._active_tab)

    def set_current_tab(self, key: str, emit_signal: bool = False):
        if key not in self._buttons:
            return
        changed = self._active_tab != key
        self._active_tab = key
        self._update_styles()
        if emit_signal and changed:
            self.tabChanged.emit(key)

    def _clear_layout(self):
        while self._layout.count():
            item = self._layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

    def _rebuild(self):
        self._clear_layout()
        self._buttons = {}
        for key, label, hint in self._tab_defs:
            chip = LessonTabChip(key, label, hint, parent=self)
            chip.clicked.connect(lambda _k, k=key: self.set_current_tab(k, emit_signal=True))
            self._layout.addWidget(chip, 0, Qt.AlignLeft | Qt.AlignVCenter)
            self._buttons[key] = chip
            chip.show()
        self._layout.addStretch(1)
        self._update_styles()

    def _update_styles(self):
        for k, chip in self._buttons.items():
            chip.set_active(k == self._active_tab)
