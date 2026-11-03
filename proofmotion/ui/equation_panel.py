"""
ui/equation_panel.py
----------------------
Bottom panel: step counter badge, mathematical equation / pseudocode,
intermediate metrics, and pedagogical explanation narrative.
"""

import re
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame
from PyQt5.QtCore import Qt


def clean_math_text(text: str) -> str:
    """Converts raw LaTeX formulas to crisp, readable human-friendly text."""
    if not text:
        return ""
    s = text
    # Fix potential Python tab character from '\text'
    s = s.replace('\text', 'text').replace('\t', ' ')
    s = re.sub(r'\\?text\{([^}]+)\}', r'\1', s)
    # Common mathematical symbol conversions
    replacements = [
        (r'\implies', '⟹'),
        (r'\iff', '⟺'),
        (r'\rightarrow', '→'),
        (r'\mapsto', '↦'),
        (r'\cdot', '·'),
        (r'\times', '×'),
        (r'\in', '∈'),
        (r'\notin', '∉'),
        (r'\leq', '≤'),
        (r'\geq', '≥'),
        (r'\neq', '≠'),
        (r'\approx', '≈'),
        (r'\pm', '±'),
        (r'\infty', '∞'),
        (r'\min', 'min'),
        (r'\max', 'max'),
        (r'\sum', 'Σ'),
        (r'\quad', '   '),
        (r'\qquad', '      '),
        (r'\,', ' '),
        (r'\{', '{'),
        (r'\}', '}'),
        (r'\_', '_'),
        (r'\vert', '|'),
        (r'\mid', '|'),
        (r'\cup', '∪'),
        (r'\cap', '∩'),
        (r'\subset', '⊂'),
        (r'\subseteq', '⊆'),
    ]
    for pattern, rep in replacements:
        s = s.replace(pattern, rep)
    # Clean subscripts like \min_{e \in Cut} -> min[e ∈ Cut]
    s = re.sub(r'_\{([^}]+)\}', r'[\1]', s)
    # Strip any residual single backslashes before words
    s = re.sub(r'\\([a-zA-Z]+)', r'\1', s)
    return s.strip()


class EquationPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 10, 18, 10)
        outer.setSpacing(6)

        # Header row: StepBadge on left, StepTitle, MetricBadge on right
        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(10)

        self._badge = QLabel("READY")
        self._badge.setObjectName("StepBadge")
        header_row.addWidget(self._badge)

        self._step_title_label = QLabel("")
        self._step_title_label.setObjectName("StepTitle")
        self._step_title_label.setWordWrap(False)
        self._step_title_label.hide()
        header_row.addWidget(self._step_title_label, stretch=1)

        self._metrics_label = QLabel("")
        self._metrics_label.setObjectName("ParamHint")
        self._metrics_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        header_row.addWidget(self._metrics_label)
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
        content_layout.setSpacing(4)

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
        self._result_label.setWordWrap(True)
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
        clean_eq = clean_math_text(equation)
        clean_title = clean_math_text(title)

        if ":" in clean_title and re.match(r'^Step\s+\d+[A-Z]?\s*:', clean_title, re.IGNORECASE):
            clean_title = clean_title.split(":", 1)[1].strip()

        self._step_title_label.setText(clean_title)
        self._step_title_label.setVisible(bool(clean_title))

        show_eq = bool(clean_eq) and (clean_eq.lower() not in clean_title.lower())
        if clean_eq.startswith(("Available Edges:", "MST Vertices:", "Global Sorted Edges:", "Edge ")):
            show_eq = False
        self._equation_label.setText(clean_eq)
        self._equation_label.setVisible(show_eq)

        formatted_exp = self._format_explanation_html(explanation)
        self._explanation_label.setTextFormat(Qt.RichText)
        self._explanation_label.setText(formatted_exp)

        if metrics:
            metric_strs = [f"{k}: {v}" for k, v in metrics.items() if not isinstance(v, (dict, list))]
            self._metrics_label.setText("  •  ".join(metric_strs))
        else:
            self._metrics_label.setText("")
        self._result_label.hide()

    def _format_explanation_html(self, text: str) -> str:
        if not text:
            return ""
        clean_t = clean_math_text(text)
        lines = [l.strip() for l in clean_t.split('\n') if l.strip()]
        if not lines:
            return ""

        html_blocks = []
        has_numbered = any(re.match(r'^[1-5]\.\s*', l) for l in lines)
        if has_numbered:
            for l in lines:
                m = re.match(r'^[1-5]\.\s*([^:?]+)[:?]\s*(.*)', l)
                if m:
                    q_text = m.group(1).strip()
                    ans_text = m.group(2).strip()
                    q_lower = q_text.lower()
                    if "what are we" in q_lower or "what do we" in q_lower or "goal" in q_lower:
                        tag, tag_c, bg_c = "Goal", "#6C5CE7", "#F0EDFF"
                    elif "why" in q_lower or "reason" in q_lower:
                        tag, tag_c, bg_c = "Why", "#047857", "#ECFDF5"
                    elif "calculation" in q_lower or "evaluat" in q_lower or "compar" in q_lower or "looking" in q_lower:
                        tag, tag_c, bg_c = "Operation", "#B45309", "#FEF3C7"
                    elif "result" in q_lower or "mean" in q_lower or "decision" in q_lower or "state" in q_lower:
                        tag, tag_c, bg_c = "Decision", "#0369A1", "#E0F2FE"
                    elif "next" in q_lower:
                        tag, tag_c, bg_c = "Next", "#4338CA", "#EEF2FF"
                    elif "cycle" in q_lower:
                        tag, tag_c, bg_c = "Cycle", "#DC2626", "#FEE2E2"
                    else:
                        tag, tag_c, bg_c = q_text[:10], "#475569", "#F1F5F9"

                    ans_text = re.sub(r'(Edge\s+[A-Za-z]-[A-Za-z]|\([A-Za-z],\s*[A-Za-z]\))', r'<b>\1</b>', ans_text)
                    ans_text = re.sub(r'(\bweight\s+\d+|\bweight:\s*\d+)', r'<span style="color:#6C5CE7; font-weight:700;">\1</span>', ans_text)
                    html_blocks.append(
                        f'<div style="margin-bottom: 5px; line-height: 1.5;">'
                        f'<span style="background-color: {bg_c}; color: {tag_c}; font-weight: 700; font-size: 10.5px; padding: 2px 7px; border-radius: 4px;">{tag.upper()}</span>&nbsp;&nbsp;'
                        f'<span style="color: #1E293B; font-size: 13px;">{ans_text}</span>'
                        f'</div>'
                    )
                else:
                    clean_l = l.lstrip('•-* ').strip()
                    clean_l = re.sub(r'(Edge\s+[A-Za-z]-[A-Za-z]|\([A-Za-z],\s*[A-Za-z]\))', r'<b>\1</b>', clean_l)
                    clean_l = re.sub(r'(\bweight\s+\d+|\bweight:\s*\d+)', r'<span style="color:#6C5CE7; font-weight:700;">\1</span>', clean_l)
                    html_blocks.append(f'<div style="color: #334155; font-size: 13px; margin-bottom: 3px; line-height: 1.45;">• {clean_l}</div>')
            return "".join(html_blocks)
        else:
            for l in lines:
                clean_l = l.lstrip('•-* ').strip()
                clean_l = re.sub(r'(Edge\s+[A-Za-z]-[A-Za-z]|\([A-Za-z],\s*[A-Za-z]\))', r'<b>\1</b>', clean_l)
                clean_l = re.sub(r'(\bweight\s+\d+|\bweight:\s*\d+)', r'<span style="color:#6C5CE7; font-weight:700;">\1</span>', clean_l)
                if clean_l.startswith("Core Idea:") or clean_l.startswith("How Prim") or clean_l.startswith("How Kruskal"):
                    html_blocks.append(f'<div style="color: #0F172A; font-weight: 700; font-size: 13px; margin-bottom: 4px;">{clean_l}</div>')
                else:
                    html_blocks.append(f'<div style="color: #334155; font-size: 13px; margin-bottom: 3px; line-height: 1.45;">{clean_l}</div>')
            return "".join(html_blocks)

    def display_result(self, result_text: str):
        clean_res = clean_math_text(result_text)
        self._result_label.setText(f"✓ {clean_res}")
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
