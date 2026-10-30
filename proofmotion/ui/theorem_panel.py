"""
ui/theorem_panel.py
--------------------
Left sidebar: Topic and Algorithm selection.

Emits `theoremSelected(str)` with the topic's `key` when the user picks
an item. Can dynamically update its list of items when switching modules.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QButtonGroup,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal


class TheoremPanel(QWidget):
    theoremSelected = pyqtSignal(str)  # item key

    def __init__(self, theorems, parent=None):
        super().__init__(parent)
        self.setObjectName("SidebarPanel")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._buttons = {}

        self._outer = QVBoxLayout(self)
        self._outer.setContentsMargins(16, 16, 16, 16)
        self._outer.setSpacing(10)

        self._title_label = QLabel("Theorems")
        self._title_label.setObjectName("PanelTitle")
        self._outer.addWidget(self._title_label)

        self._divider = QWidget()
        self._divider.setObjectName("PanelDivider")
        self._outer.addWidget(self._divider)
        self._outer.addSpacing(4)

        self._btn_container = QWidget()
        self._btn_layout = QVBoxLayout(self._btn_container)
        self._btn_layout.setContentsMargins(0, 0, 0, 0)
        self._btn_layout.setSpacing(8)
        self._outer.addWidget(self._btn_container)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)

        self._outer.addStretch(1)

        self.set_items(theorems, title="THEOREMS")

    def set_items(self, items, title="TOPICS"):
        """Rebuild sidebar buttons for any list of items having .key and .display_name."""
        self._title_label.setText(title.title())

        # Clear existing buttons
        for btn in list(self._buttons.values()):
            self._group.removeButton(btn)
            self._btn_layout.removeWidget(btn)
            btn.deleteLater()
        self._buttons.clear()

        for i, item in enumerate(items, start=1):
            key = getattr(item, "key", str(item))
            display_name = getattr(item, "display_name", key)
            btn = self._make_button(i, display_name, key)
            self._btn_layout.addWidget(btn)
            self._buttons[key] = btn
            self._group.addButton(btn)

    def _make_button(self, index: int, label: str, key: str) -> QPushButton:
        btn = QPushButton()
        btn.setObjectName("TheoremButton")
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumHeight(46)
        btn.setToolTip(label)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        content = QHBoxLayout(btn)
        content.setContentsMargins(14, 7, 12, 7)
        content.setSpacing(12)

        index_label = QLabel(f"{index:02d}")
        index_label.setObjectName("TheoremIndex")
        index_label.setFixedSize(28, 24)
        index_label.setAlignment(Qt.AlignCenter)
        index_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        content.addWidget(index_label)

        name_label = QLabel(label)
        name_label.setObjectName("TheoremName")
        name_label.setWordWrap(True)
        name_label.setMinimumWidth(0)
        name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        name_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        content.addWidget(name_label, stretch=1)

        btn.clicked.connect(lambda checked, k=key: self._on_clicked(k))
        return btn

    def _on_clicked(self, key: str):
        self._apply_selected_style(key)
        self.theoremSelected.emit(key)

    def _apply_selected_style(self, key: str):
        for k, btn in self._buttons.items():
            selected = (k == key)
            btn.setChecked(selected)
            btn.setProperty("selected", "true" if selected else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            for label in btn.findChildren(QLabel):
                label.setProperty("selected", "true" if selected else "false")
                label.style().unpolish(label)
                label.style().polish(label)

    def select_theorem(self, key: str):
        """Programmatically select an item (e.g. to set initial default)."""
        if key in self._buttons:
            self._apply_selected_style(key)
            self.theoremSelected.emit(key)
