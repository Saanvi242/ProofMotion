"""
ui/comparison_bar.py
--------------------
Interactive canvas-top comparison bar for selecting and swapping
algorithms in side-by-side comparison mode.
"""

from typing import List
from PyQt5.QtWidgets import (
    QFrame, QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QCursor, QFont

from resources.theme import COLORS, get_ui_font, get_mono_font

SORT_OPTIONS = [
    "Bubble Sort",
    "Selection Sort",
    "Insertion Sort",
    "Merge Sort",
    "Quick Sort",
]


class ComparisonBar(QFrame):
    """
    Toolbar placed directly above the visualization canvas in comparison mode.
    Allows changing Algorithm 1, Algorithm 2, swapping, and applying quick presets.
    """
    algorithmsChanged = pyqtSignal(str, str)  # (algo_1, algo_2)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ComparisonBar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(48)

        self.setStyleSheet("""
            QFrame#ComparisonBar {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 4px 12px;
            }
            QLabel#CompBarLabel {
                color: #0F172A;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
                font-size: 12px;
                font-weight: 700;
            }
            QLabel#CompBarVs {
                background-color: #EDE9FE;
                color: #6C5CE7;
                border: 1px solid #DDD6FE;
                border-radius: 10px;
                padding: 2px 7px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
                font-size: 10.5px;
                font-weight: 800;
            }
            QComboBox#CompBarCombo {
                background-color: #F8FAFC;
                color: #0F172A;
                border: 1.5px solid #CBD5E1;
                border-radius: 6px;
                padding: 3px 10px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
                font-size: 12px;
                font-weight: 600;
                min-width: 130px;
                height: 28px;
            }
            QComboBox#CompBarCombo:hover {
                border-color: #6C5CE7;
                background-color: #FFFFFF;
            }
            QComboBox#CompBarCombo::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: none;
            }
            QPushButton#CompBarSwapBtn {
                background-color: #F1F5F9;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 4px 9px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
                font-size: 11.5px;
                font-weight: 600;
                height: 28px;
            }
            QPushButton#CompBarSwapBtn:hover {
                background-color: #EDE9FE;
                color: #6C5CE7;
                border-color: #A78BFA;
            }
            QPushButton#CompBarChip {
                background-color: #F8FAFC;
                color: #64748B;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                padding: 3px 9px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
                font-size: 10.5px;
                font-weight: 600;
                height: 24px;
            }
            QPushButton#CompBarChip:hover {
                background-color: #F5F3FF;
                color: #6C5CE7;
                border-color: #C4B5FD;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignVCenter)

        # Title
        title_lbl = QLabel("⚔  Compare:")
        title_lbl.setObjectName("CompBarLabel")
        layout.addWidget(title_lbl)

        # Algo 1 Dropdown
        self.algo1_combo = QComboBox()
        self.algo1_combo.setObjectName("CompBarCombo")
        self.algo1_combo.addItems(SORT_OPTIONS)
        self.algo1_combo.setCurrentText("Bubble Sort")
        self.algo1_combo.activated.connect(self._on_combo_changed)
        layout.addWidget(self.algo1_combo)

        # VS Badge
        vs_lbl = QLabel("VS")
        vs_lbl.setObjectName("CompBarVs")
        layout.addWidget(vs_lbl)

        # Algo 2 Dropdown
        self.algo2_combo = QComboBox()
        self.algo2_combo.setObjectName("CompBarCombo")
        self.algo2_combo.addItems(SORT_OPTIONS)
        self.algo2_combo.setCurrentText("Quick Sort")
        self.algo2_combo.activated.connect(self._on_combo_changed)
        layout.addWidget(self.algo2_combo)

        # Swap button
        self.swap_btn = QPushButton("⇄ Swap")
        self.swap_btn.setObjectName("CompBarSwapBtn")
        self.swap_btn.setToolTip("Swap Left and Right algorithms")
        self.swap_btn.setCursor(Qt.PointingHandCursor)
        self.swap_btn.clicked.connect(self._on_swap_clicked)
        layout.addWidget(self.swap_btn)

        layout.addSpacing(6)
        sep = QLabel("|")
        sep.setStyleSheet("color: #CBD5E1; font-weight: 300;")
        layout.addWidget(sep)
        layout.addSpacing(6)

        # Quick preset chips
        preset_lbl = QLabel("Matchups:")
        preset_lbl.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 600;")
        layout.addWidget(preset_lbl)

        presets = [
            ("Quick vs Bubble", "Bubble Sort", "Quick Sort"),
            ("Merge vs Quick", "Merge Sort", "Quick Sort"),
            ("Insertion vs Bubble", "Bubble Sort", "Insertion Sort"),
            ("Selection vs Insertion", "Selection Sort", "Insertion Sort"),
        ]

        for label, a1, a2 in presets:
            chip = QPushButton(label)
            chip.setObjectName("CompBarChip")
            chip.setCursor(Qt.PointingHandCursor)
            chip.clicked.connect(lambda _, x=a1, y=a2: self.set_algorithms(x, y, emit=True))
            layout.addWidget(chip)

        layout.addStretch(1)

    def set_algorithms(self, algo_1: str, algo_2: str, emit: bool = False):
        """Update dropdown displays, optionally emitting change signal."""
        self.algo1_combo.blockSignals(True)
        self.algo2_combo.blockSignals(True)

        if algo_1 in SORT_OPTIONS:
            self.algo1_combo.setCurrentText(algo_1)
        if algo_2 in SORT_OPTIONS:
            self.algo2_combo.setCurrentText(algo_2)

        self.algo1_combo.blockSignals(False)
        self.algo2_combo.blockSignals(False)

        if emit:
            self.algorithmsChanged.emit(self.algo1_combo.currentText(), self.algo2_combo.currentText())

    def get_algorithms(self) -> (str, str):
        return self.algo1_combo.currentText(), self.algo2_combo.currentText()

    def _on_combo_changed(self):
        self.algorithmsChanged.emit(self.algo1_combo.currentText(), self.algo2_combo.currentText())

    def _on_swap_clicked(self):
        a1 = self.algo1_combo.currentText()
        a2 = self.algo2_combo.currentText()
        self.set_algorithms(a2, a1, emit=True)
