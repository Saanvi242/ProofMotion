"""
ui/bezier_quiz_widget.py
------------------------
Interactive 5-question assessment widget for Bézier Curves & De Casteljau's Algorithm.
Provides immediate feedback, detailed mathematical explanations, score tracking,
and celebration results.
"""

from typing import Dict, List, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy, QScrollArea, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QCursor, QFont

from resources.theme import get_ui_font, get_mono_font, COLORS

QUIZ_QUESTIONS = [
    {
        "id": 1,
        "topic": "Control Points & Anchors",
        "question": "In a cubic Bézier curve with control points P0, P1, P2, and P3, which points does the curve physically pass through?",
        "options": [
            ("A", "All four control points (P0, P1, P2, and P3)"),
            ("B", "Only the start point P0 and end point P3"),
            ("C", "Only the middle shape handles P1 and P2"),
            ("D", "None of them — the curve floats entirely free"),
        ],
        "correct": "B",
        "explanation": (
            "P0 is the start anchor (t = 0) and P3 is the end anchor (t = 1). The curve is mathematically "
            "guaranteed to touch both endpoints. The interior points P1 and P2 are off-curve control handles "
            "that act like magnets steering the bend without the curve passing through them."
        ),
    },
    {
        "id": 2,
        "topic": "Linear Interpolation (Lerp)",
        "question": "What is the linear interpolation formula to calculate point P(t) along a straight line segment from A to B?",
        "options": [
            ("A", "P(t) = (1 − t)·A + t·B"),
            ("B", "P(t) = t·A + (1 − t)·B"),
            ("C", "P(t) = (A + B) / t"),
            ("D", "P(t) = t²·A + (1 − t²)·B"),
        ],
        "correct": "A",
        "explanation": (
            "P(t) = (1 − t)·A + t·B is the fundamental Lerp formula. At t = 0, P(0) = 1·A + 0·B = A. "
            "At t = 1, P(1) = 0·A + 1·B = B. At t = 0.5, both points contribute equally: (A + B)/2. "
            "The blending weights (1 − t) and t always sum to 1."
        ),
    },
    {
        "id": 3,
        "topic": "Parameter t",
        "question": "What is the standard domain (range of values) for parameter t on a standard Bézier curve segment?",
        "options": [
            ("A", "t can be any real number from −∞ to +∞"),
            ("B", "t ranges from 0 to 100 percentage points"),
            ("C", "t ranges strictly from 0.0 to 1.0 (normalized unit interval)"),
            ("D", "t ranges from −1.0 to +1.0"),
        ],
        "correct": "C",
        "explanation": (
            "In Computer Graphics, curves are defined over the normalized parameter interval t ∈ [0, 1]. "
            "t = 0 represents the beginning of the curve at P0 (0% travel), while t = 1 represents the end "
            "of the curve at P3 (100% travel)."
        ),
    },
    {
        "id": 4,
        "topic": "De Casteljau Algorithm Levels",
        "question": "Starting with 4 control points (P0, P1, P2, P3), how many points are generated at Level 1, Level 2, and Level 3 respectively?",
        "options": [
            ("A", "Level 1: 4 points  →  Level 2: 3 points  →  Level 3: 2 points"),
            ("B", "Level 1: 3 points (Q)  →  Level 2: 2 points (R)  →  Level 3: 1 point (B(t))"),
            ("C", "Level 1: 2 points  →  Level 2: 2 points  →  Level 3: 1 point"),
            ("D", "Level 1: 3 points  →  Level 2: 1 point  →  Level 3: 0 points"),
        ],
        "correct": "B",
        "explanation": (
            "De Casteljau's algorithm forms a reduction pyramid! At each level, every neighbouring pair "
            "is linearly interpolated at the same t: 4 control points yield 3 points (Q0, Q1, Q2), "
            "which yield 2 points (R0, R1), which finally collapse to 1 single point: B(t)."
        ),
    },
    {
        "id": 5,
        "topic": "Why De Casteljau Works",
        "question": "Why does the final point B(t) calculated by De Casteljau lie exactly on the cubic Bézier curve?",
        "options": [
            ("A", "It is just a coarse visual approximation that looks close enough"),
            ("B", "Repeated affine linear interpolation is mathematically identical to the Bernstein polynomial expansion"),
            ("C", "Because computer screens round floating point numbers to integer pixels"),
            ("D", "Because the curve is precomputed and De Casteljau snaps to the nearest vertex"),
        ],
        "correct": "B",
        "explanation": (
            "Expanding the three nested lerps algebraically: B(t) = (1−t)R0 + tR1 = (1−t)³P0 + 3(1−t)²tP1 "
            "+ 3(1−t)t²P2 + t³P3. This exact polynomial expansion is the cubic Bernstein Bézier curve definition! "
            "De Casteljau is not a visual trick — it is an exact, numerically stable evaluation algorithm."
        ),
    },
]


class OptionButton(QFrame):
    """Interactive choice card with hover, selection, and feedback states."""
    selected = pyqtSignal(str)

    def __init__(self, key: str, text: str, parent=None):
        super().__init__(parent)
        self.key = key
        self.text = text
        self.setObjectName("QuizOptionCard")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(56)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(14)

        self._badge = QLabel(key)
        self._badge.setObjectName("QuizOptionKey")
        self._badge.setFixedSize(30, 30)
        self._badge.setAlignment(Qt.AlignCenter)
        self._badge.setFont(get_ui_font(12, weight=700))
        layout.addWidget(self._badge)

        self._label = QLabel(text)
        self._label.setObjectName("QuizOptionText")
        self._label.setFont(get_ui_font(13, weight=500))
        self._label.setWordWrap(True)
        layout.addWidget(self._label, stretch=1)

        self._status_icon = QLabel("")
        self._status_icon.setFont(get_ui_font(14, weight=700))
        self._status_icon.hide()
        layout.addWidget(self._status_icon)

        self.reset_state()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected.emit(self.key)
        super().mousePressEvent(event)

    def reset_state(self):
        self.setEnabled(True)
        self._status_icon.hide()
        self.setStyleSheet("""
            QFrame#QuizOptionCard {
                background-color: #FFFFFF;
                border: 1.5px solid #E2E8F0;
                border-radius: 12px;
            }
            QFrame#QuizOptionCard:hover {
                background-color: #F8FAFC;
                border-color: #6C5CE7;
            }
            QLabel#QuizOptionKey {
                background-color: #F1F5F9;
                color: #475569;
                border-radius: 8px;
            }
            QLabel#QuizOptionText {
                color: #1E293B;
                background: transparent;
            }
        """)

    def set_feedback(self, is_selected: bool, is_correct_choice: bool, is_actual_correct: bool):
        self.setEnabled(False)
        self._status_icon.show()
        if is_actual_correct:
            # Correct answer (highlighted in emerald green)
            self._status_icon.setText("✓ Correct")
            self._status_icon.setStyleSheet("color: #16A34A; font-weight: 700;")
            self.setStyleSheet("""
                QFrame#QuizOptionCard {
                    background-color: #F0FDF4;
                    border: 2px solid #22C55E;
                    border-radius: 12px;
                }
                QLabel#QuizOptionKey {
                    background-color: #22C55E;
                    color: #FFFFFF;
                    border-radius: 8px;
                }
                QLabel#QuizOptionText {
                    color: #14532D;
                    font-weight: 600;
                    background: transparent;
                }
            """)
        elif is_selected and not is_correct_choice:
            # User selected wrong answer (highlighted in soft red)
            self._status_icon.setText("✗ Incorrect")
            self._status_icon.setStyleSheet("color: #DC2626; font-weight: 700;")
            self.setStyleSheet("""
                QFrame#QuizOptionCard {
                    background-color: #FEF2F2;
                    border: 2px solid #EF4444;
                    border-radius: 12px;
                }
                QLabel#QuizOptionKey {
                    background-color: #EF4444;
                    color: #FFFFFF;
                    border-radius: 8px;
                }
                QLabel#QuizOptionText {
                    color: #7F1D1D;
                    font-weight: 600;
                    background: transparent;
                }
            """)
        else:
            # Unselected neutral option
            self._status_icon.hide()
            self.setStyleSheet("""
                QFrame#QuizOptionCard {
                    background-color: #F8FAFC;
                    border: 1px solid #E2E8F0;
                    border-radius: 12px;
                    opacity: 0.6;
                }
                QLabel#QuizOptionKey {
                    background-color: #E2E8F0;
                    color: #94A3B8;
                    border-radius: 8px;
                }
                QLabel#QuizOptionText {
                    color: #94A3B8;
                    background: transparent;
                }
            """)


class BezierQuizWidget(QWidget):
    """Complete interactive assessment module for Bézier Curves."""
    questionChanged = pyqtSignal(int, int)  # current_index (0-based), total
    quizCompleted = pyqtSignal(int, int)    # score, total

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("BezierQuizWidget")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self._questions = list(QUIZ_QUESTIONS)
        self._current_index = 0
        self._user_answers: Dict[int, str] = {}
        self._option_buttons: List[OptionButton] = []

        self._init_ui()
        self.load_question(0)

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(28, 20, 28, 20)
        root_layout.setSpacing(16)

        # ---------------- Top Header Bar ----------------
        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        stage_chip = QLabel("STAGE 5: TEST YOUR UNDERSTANDING")
        stage_chip.setStyleSheet("""
            background-color: #EDE9FE;
            color: #6C5CE7;
            font-weight: 700;
            font-size: 11px;
            padding: 4px 12px;
            border-radius: 6px;
        """)
        top_bar.addWidget(stage_chip)

        self._progress_badge = QLabel("Question 1 of 5")
        self._progress_badge.setFont(get_ui_font(12, weight=600))
        self._progress_badge.setStyleSheet("color: #64748B;")
        top_bar.addWidget(self._progress_badge)

        top_bar.addStretch(1)

        self._score_badge = QLabel("Score: 0 / 5")
        self._score_badge.setStyleSheet("""
            background-color: #FEF3C7;
            color: #B45309;
            font-weight: 700;
            font-size: 12px;
            padding: 4px 14px;
            border-radius: 8px;
            border: 1px solid #FDE68A;
        """)
        top_bar.addWidget(self._score_badge)
        root_layout.addLayout(top_bar)

        # ---------------- Scroll Area for Content ----------------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        self._content_layout = QVBoxLayout(content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(14)

        # Question Card
        self._q_card = QFrame()
        self._q_card.setObjectName("QuizQuestionCard")
        self._q_card.setStyleSheet("""
            QFrame#QuizQuestionCard {
                background-color: #FFFFFF;
                border: 1.5px solid #E2E8F0;
                border-radius: 14px;
                padding: 16px;
            }
        """)
        q_vbox = QVBoxLayout(self._q_card)
        q_vbox.setContentsMargins(18, 14, 18, 14)
        q_vbox.setSpacing(8)

        self._topic_tag = QLabel("Topic: Control Points")
        self._topic_tag.setFont(get_ui_font(11, weight=600))
        self._topic_tag.setStyleSheet("color: #6C5CE7; text-transform: uppercase; letter-spacing: 0.5px;")
        q_vbox.addWidget(self._topic_tag)

        self._question_label = QLabel("")
        self._question_label.setFont(get_ui_font(15, weight=700))
        self._question_label.setStyleSheet("color: #0F172A; line-height: 1.4;")
        self._question_label.setWordWrap(True)
        q_vbox.addWidget(self._question_label)

        self._content_layout.addWidget(self._q_card)

        # Options Container
        self._options_container = QVBoxLayout()
        self._options_container.setSpacing(10)
        self._content_layout.addLayout(self._options_container)

        # Feedback & Explanation Box
        self._explanation_box = QFrame()
        self._explanation_box.setObjectName("QuizExplanationBox")
        self._explanation_box.setStyleSheet("""
            QFrame#QuizExplanationBox {
                background-color: #F8FAFC;
                border: 1.5px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        exp_vbox = QVBoxLayout(self._explanation_box)
        exp_vbox.setContentsMargins(18, 14, 18, 14)
        exp_vbox.setSpacing(6)

        self._exp_title = QLabel("💡 Explanation")
        self._exp_title.setFont(get_ui_font(13, weight=700))
        self._exp_title.setStyleSheet("color: #334155;")
        exp_vbox.addWidget(self._exp_title)

        self._exp_body = QLabel("")
        self._exp_body.setFont(get_ui_font(12, weight=400))
        self._exp_body.setStyleSheet("color: #475569; line-height: 1.45;")
        self._exp_body.setWordWrap(True)
        exp_vbox.addWidget(self._exp_body)

        self._explanation_box.hide()
        self._content_layout.addWidget(self._explanation_box)

        # Celebration Completion Banner (Hidden until finished)
        self._summary_box = QFrame()
        self._summary_box.setObjectName("QuizSummaryBox")
        self._summary_box.setStyleSheet("""
            QFrame#QuizSummaryBox {
                background-color: #F5F3FF;
                border: 2px solid #C4B5FD;
                border-radius: 16px;
            }
        """)
        sum_vbox = QVBoxLayout(self._summary_box)
        sum_vbox.setContentsMargins(24, 20, 24, 20)
        sum_vbox.setSpacing(10)

        sum_title = QLabel("🎉 Tutorial Assessment Completed!")
        sum_title.setFont(get_ui_font(18, weight=700))
        sum_title.setStyleSheet("color: #4C1D95;")
        sum_vbox.addWidget(sum_title)

        self._sum_body = QLabel("")
        self._sum_body.setFont(get_ui_font(13, weight=500))
        self._sum_body.setStyleSheet("color: #5B21B6; line-height: 1.5;")
        self._sum_body.setWordWrap(True)
        sum_vbox.addWidget(self._sum_body)

        sum_btns = QHBoxLayout()
        self._retake_btn = QPushButton("🔄 Retake Quiz")
        self._retake_btn.setFont(get_ui_font(12, weight=600))
        self._retake_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._retake_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C5CE7;
                color: #FFFFFF;
                border: none;
                padding: 8px 18px;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #5B4BD4; }
        """)
        self._retake_btn.clicked.connect(self.restart_quiz)
        sum_btns.addWidget(self._retake_btn)
        sum_btns.addStretch(1)
        sum_vbox.addLayout(sum_btns)

        self._summary_box.hide()
        self._content_layout.addWidget(self._summary_box)

        scroll.setWidget(content)
        root_layout.addWidget(scroll, stretch=1)

        # ---------------- Bottom Navigation Bar ----------------
        bottom_bar = QHBoxLayout()
        self._prev_btn = QPushButton("← Previous Question")
        self._prev_btn.setFont(get_ui_font(12, weight=600))
        self._prev_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1.5px solid #CBD5E1;
                color: #334155;
                padding: 8px 16px;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #F8FAFC; border-color: #94A3B8; }
            QPushButton:disabled { color: #CBD5E1; border-color: #E2E8F0; }
        """)
        self._prev_btn.clicked.connect(self.previous_question)
        bottom_bar.addWidget(self._prev_btn)

        bottom_bar.addStretch(1)

        self._next_btn = QPushButton("Next Question →")
        self._next_btn.setFont(get_ui_font(12, weight=600))
        self._next_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._next_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C5CE7;
                border: none;
                color: #FFFFFF;
                padding: 8px 18px;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #5B4BD4; }
            QPushButton:disabled { background-color: #CBD5E1; color: #94A3B8; }
        """)
        self._next_btn.clicked.connect(self.next_question)
        bottom_bar.addWidget(self._next_btn)

        root_layout.addLayout(bottom_bar)

    # ------------------------------------------------------------------
    # Quiz Logic
    # ------------------------------------------------------------------
    def load_question(self, index: int):
        if index < 0 or index >= len(self._questions):
            return
        self._current_index = index
        q = self._questions[index]

        self._progress_badge.setText(f"Question {index + 1} of {len(self._questions)}")
        self._topic_tag.setText(f"Topic: {q['topic']}")
        self._question_label.setText(f"Q{q['id']}. {q['question']}")

        # Clear old option buttons
        while self._options_container.count():
            item = self._options_container.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._option_buttons.clear()

        # Build options
        for key, text in q["options"]:
            btn = OptionButton(key, text, self)
            btn.selected.connect(lambda k=key: self.select_answer(k))
            self._options_container.addWidget(btn)
            self._option_buttons.append(btn)

        # Check if already answered
        answered_key = self._user_answers.get(index)
        if answered_key:
            self._show_answer_feedback(answered_key, q["correct"], q["explanation"])
        else:
            self._explanation_box.hide()

        self._prev_btn.setEnabled(index > 0)
        self._next_btn.setEnabled(index < len(self._questions) - 1 or len(self._user_answers) == len(self._questions))
        if index == len(self._questions) - 1 and len(self._user_answers) == len(self._questions):
            self._next_btn.setText("View Results 🎉")
        else:
            self._next_btn.setText("Next Question →")

        self.questionChanged.emit(self._current_index, len(self._questions))

    def select_answer(self, key: str):
        q = self._questions[self._current_index]
        is_new = self._current_index not in self._user_answers
        self._user_answers[self._current_index] = key

        self._show_answer_feedback(key, q["correct"], q["explanation"])
        self._update_score()

        if len(self._user_answers) == len(self._questions):
            self._show_summary()

    def _show_answer_feedback(self, selected_key: str, correct_key: str, explanation: str):
        is_correct = (selected_key == correct_key)
        for btn in self._option_buttons:
            btn.set_feedback(
                is_selected=(btn.key == selected_key),
                is_correct_choice=is_correct,
                is_actual_correct=(btn.key == correct_key)
            )

        if is_correct:
            self._exp_title.setText("✓ Correct! Nice work.")
            self._exp_title.setStyleSheet("color: #16A34A; font-weight: 700;")
            self._explanation_box.setStyleSheet("""
                QFrame#QuizExplanationBox {
                    background-color: #F0FDF4;
                    border: 1.5px solid #BBF7D0;
                    border-radius: 12px;
                }
            """)
        else:
            self._exp_title.setText(f"💡 Key Takeaway (Correct Answer: {correct_key})")
            self._exp_title.setStyleSheet("color: #B45309; font-weight: 700;")
            self._explanation_box.setStyleSheet("""
                QFrame#QuizExplanationBox {
                    background-color: #FFFBEB;
                    border: 1.5px solid #FDE68A;
                    border-radius: 12px;
                }
            """)

        self._exp_body.setText(explanation)
        self._explanation_box.show()

    def _update_score(self):
        score = sum(
            1 for idx, ans in self._user_answers.items()
            if ans == self._questions[idx]["correct"]
        )
        total = len(self._questions)
        self._score_badge.setText(f"Score: {score} / {total}")
        return score

    def _show_summary(self):
        score = self._update_score()
        total = len(self._questions)
        pct = int(round((score / total) * 100))
        if pct == 100:
            msg = f"Outstanding! You scored {score}/{total} ({pct}%). You have mastered the fundamentals of Bézier curves, linear interpolation, and De Casteljau's reduction pyramid!"
        elif pct >= 60:
            msg = f"Great job! You scored {score}/{total} ({pct}%). You understand how repeated linear interpolations build smooth curves in computer graphics."
        else:
            msg = f"You scored {score}/{total} ({pct}%). Review the previous stages to solidify how P0-P3, Lerp, and the three levels of De Casteljau interact."
        self._sum_body.setText(msg)
        self._summary_box.show()
        self.quizCompleted.emit(score, total)

    def next_question(self):
        if self._current_index < len(self._questions) - 1:
            self.load_question(self._current_index + 1)
        elif len(self._user_answers) == len(self._questions):
            self._summary_box.show()

    def previous_question(self):
        if self._current_index > 0:
            self.load_question(self._current_index - 1)

    def restart_quiz(self):
        self._user_answers.clear()
        self._summary_box.hide()
        self._score_badge.setText("Score: 0 / 5")
        self.load_question(0)
