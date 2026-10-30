"""
ui/equation_panel.py
----------------------
Bottom panel: step counter badge, mathematical equation / pseudocode,
intermediate metrics, and pedagogical explanation narrative.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame
from PyQt5.QtCore import Qt


class EquationPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 10, 18, 10)
        outer.setSpacing(6)

        # Header row: StepBadge on left, MetricBadge on right
        header_row = QHBoxLayout()
        self._badge = QLabel("READY")
        self._badge.setObjectName("StepBadge")
        header_row.addWidget(self._badge)

        self._metrics_label = QLabel("")
        self._metrics_label.setObjectName("ParamHint")
        self._metrics_label.setWordWrap(True)
        header_row.addSpacing(12)
        header_row.addWidget(self._metrics_label, stretch=1)
        outer.addLayout(header_row)

        divider = QWidget()
        divider.setObjectName("PanelDivider")
        outer.addWidget(divider)

        # Scrollable content area so long multi-step equations & explanations never clip
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setStyleSheet("background: transparent; border: none;")
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 2, 8, 2)
        content_layout.setSpacing(6)

        self._step_title_label = QLabel("")
        self._step_title_label.setObjectName("StepTitle")
        self._step_title_label.setWordWrap(True)
        self._step_title_label.hide()
        content_layout.addWidget(self._step_title_label)

        self._equation_label = QLabel("Select a topic to explore its interactive logic.")
        self._equation_label.setObjectName("EquationLabel")
        self._equation_label.setWordWrap(True)
        content_layout.addWidget(self._equation_label)

        self._explanation_label = QLabel("")
        self._explanation_label.setObjectName("ExplanationLabel")
        self._explanation_label.setWordWrap(True)
        content_layout.addWidget(self._explanation_label)

        self._result_label = QLabel("")
        self._result_label.setObjectName("ResultLabel")
        self._result_label.hide()
        content_layout.addWidget(self._result_label)

        self._scroll.setWidget(content_widget)
        outer.addWidget(self._scroll)

    # ------------------------------------------------------------------
    # Public API (called by the controller)
    # ------------------------------------------------------------------
    def display_step(self, step_index_1based: int, total_steps: int,
                     equation: str, explanation: str, metrics: dict = None,
                     title: str = ""):
        self._badge.setText(f"STEP {step_index_1based} OF {max(1, total_steps)}")
        self._equation_label.setText(equation)
        self._step_title_label.setText(title)
        self._step_title_label.setVisible(bool(title))
        self._equation_label.setVisible(bool(equation))
        self._explanation_label.setText(explanation)
        if metrics:
            metric_strs = [f"{k}: {v}" for k, v in metrics.items() if not isinstance(v, (dict, list))]
            self._metrics_label.setText("  •  ".join(metric_strs))
        else:
            self._metrics_label.setText("")
        self._result_label.hide()

    def display_result(self, result_text: str):
        self._result_label.setText(f"✓ {result_text}")
        self._result_label.show()

    def clear(self):
        self._badge.setText("READY")
        self._metrics_label.setText("")
        self._step_title_label.clear()
        self._step_title_label.hide()
        self._equation_label.setText("Select a topic to explore its interactive logic.")
        self._equation_label.show()
        self._explanation_label.setText("")
        self._result_label.hide()
