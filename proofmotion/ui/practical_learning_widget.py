"""
ui/practical_learning_widget.py
--------------------------------
Interactive Practical Learning & Real-World Applications widget.
Displays:
1. Feature B: Familiar Practical Example & connection to the ProofMotion visualization.
2. Feature A: Real-World Applications ("Where Is It Used?") with technical contexts.
3. Feature C: Lightweight Quick Knowledge Check with instant interactive feedback.
"""

from typing import List, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QButtonGroup, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from core.practical_content import (
    TopicPracticalData, QuizQuestion, RealWorldApplication,
    get_practical_content
)
from resources.theme import COLORS


class QuizQuestionWidget(QFrame):
    """
    Renders an interactive multiple-choice question card.
    Provides immediate feedback on selection with explanation.
    """
    answered = pyqtSignal(bool)

    def __init__(self, index: int, question_data: QuizQuestion, parent=None):
        super().__init__(parent)
        self.q_data = question_data
        self.q_index = index
        self._buttons: List[QPushButton] = []
        self._answered = False

        self.setObjectName("QuizCard")
        self.setStyleSheet("""
            QFrame#QuizCard {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(10)

        # Header: Q1 Badge + Question Prompt
        header_row = QHBoxLayout()
        header_row.setSpacing(8)

        q_badge = QLabel(f"Q{self.q_index + 1}")
        q_badge.setStyleSheet("""
            background-color: #F0EDFF;
            color: #6C5CE7;
            font-family: Inter;
            font-size: 11px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 6px;
        """)
        header_row.addWidget(q_badge)

        self._prompt_label = QLabel(self.q_data.question)
        self._prompt_label.setWordWrap(True)
        self._prompt_label.setStyleSheet("""
            color: #0F172A;
            font-family: Inter;
            font-size: 13px;
            font-weight: 600;
            line-height: 1.4;
        """)
        header_row.addWidget(self._prompt_label, stretch=1)
        layout.addLayout(header_row)

        # Options Container
        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)

        prefix_letters = ["A", "B", "C", "D"]
        for opt_idx, opt_text in enumerate(self.q_data.options):
            letter = prefix_letters[opt_idx] if opt_idx < len(prefix_letters) else f"{opt_idx+1}"
            btn = QPushButton(f"  {letter}.  {opt_text}")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(False)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F8FAFC;
                    color: #334155;
                    border: 1px solid #CBD5E1;
                    border-radius: 8px;
                    padding: 8px 10px;
                    font-family: Inter;
                    font-size: 12px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #F1F5F9;
                    border-color: #6C5CE7;
                    color: #0F172A;
                }
            """)
            btn.clicked.connect(lambda checked, idx=opt_idx: self._handle_selection(idx))
            self._buttons.append(btn)
            layout.addWidget(btn)

        # Feedback & Explanation Box (Initially Hidden)
        self._feedback_box = QFrame()
        self._feedback_box.setObjectName("FeedbackBox")
        self._feedback_box.hide()
        fb_layout = QVBoxLayout(self._feedback_box)
        fb_layout.setContentsMargins(10, 8, 10, 8)
        fb_layout.setSpacing(4)

        self._result_header = QLabel("")
        self._result_header.setStyleSheet("font-family: Inter; font-size: 12px; font-weight: 700;")
        fb_layout.addWidget(self._result_header)

        self._explanation_label = QLabel(self.q_data.explanation)
        self._explanation_label.setWordWrap(True)
        self._explanation_label.setStyleSheet("color: #334155; font-family: Inter; font-size: 12px; line-height: 1.4;")
        fb_layout.addWidget(self._explanation_label)

        # Subtle Reset Button
        self._reset_btn = QPushButton("Try Again")
        self._reset_btn.setCursor(Qt.PointingHandCursor)
        self._reset_btn.setFixedWidth(80)
        self._reset_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #6C5CE7;
                font-family: Inter;
                font-size: 11px;
                font-weight: 600;
                border: 1px solid #D5DDED;
                border-radius: 4px;
                padding: 3px 6px;
                margin-top: 4px;
            }
            QPushButton:hover {
                background: #F0EDFF;
                border-color: #6C5CE7;
            }
        """)
        self._reset_btn.clicked.connect(self.reset_question)
        fb_layout.addWidget(self._reset_btn, alignment=Qt.AlignRight)

        layout.addWidget(self._feedback_box)

    def _handle_selection(self, selected_idx: int):
        self._answered = True
        is_correct = (selected_idx == self.q_data.correct_index)

        # Disable further clicks until reset
        for i, btn in enumerate(self._buttons):
            btn.setEnabled(False)
            if i == self.q_data.correct_index:
                # Highlight correct in soft green
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ECFDF5;
                        color: #065F46;
                        border: 1.5px solid #10B981;
                        border-radius: 8px;
                        padding: 8px 10px;
                        font-family: Inter;
                        font-size: 12px;
                        font-weight: 600;
                        text-align: left;
                    }
                """)
            elif i == selected_idx and not is_correct:
                # Highlight wrong selection in soft red
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #FEF2F2;
                        color: #991B1B;
                        border: 1.5px solid #EF4444;
                        border-radius: 8px;
                        padding: 8px 10px;
                        font-family: Inter;
                        font-size: 12px;
                        font-weight: 600;
                        text-align: left;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #F8FAFC;
                        color: #94A3B8;
                        border: 1px solid #E2E8F0;
                        border-radius: 8px;
                        padding: 8px 10px;
                        font-family: Inter;
                        font-size: 12px;
                        text-align: left;
                    }
                """)

        # Show feedback
        if is_correct:
            self._feedback_box.setStyleSheet("""
                QFrame#FeedbackBox {
                    background-color: #F0FDF4;
                    border: 1px solid #BBF7D0;
                    border-radius: 8px;
                }
            """)
            self._result_header.setText("✓ Correct!")
            self._result_header.setStyleSheet("color: #15803D; font-family: Inter; font-size: 12px; font-weight: 700;")
        else:
            self._feedback_box.setStyleSheet("""
                QFrame#FeedbackBox {
                    background-color: #FFF1F2;
                    border: 1px solid #FECDD3;
                    border-radius: 8px;
                }
            """)
            self._result_header.setText("✕ Incorrect — Explanation:")
            self._result_header.setStyleSheet("color: #B91C1C; font-family: Inter; font-size: 12px; font-weight: 700;")

        self._feedback_box.show()
        self.answered.emit(is_correct)

    def reset_question(self):
        self._answered = False
        self._feedback_box.hide()
        for btn in self._buttons:
            btn.setEnabled(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F8FAFC;
                    color: #334155;
                    border: 1px solid #CBD5E1;
                    border-radius: 8px;
                    padding: 8px 10px;
                    font-family: Inter;
                    font-size: 12px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #F1F5F9;
                    border-color: #6C5CE7;
                    color: #0F172A;
                }
            """)


class PracticalLearningWidget(QWidget):
    """
    Main Practical Learning & Real-World Applications container.
    Embedded as a dedicated tab/panel in the Learning Module.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PracticalLearningPanel")
        self._current_topic_key = ""
        self._current_data: Optional[TopicPracticalData] = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Scroll Area for comfortable viewing on all screen sizes
        self._scroll = QScrollArea()
        self._scroll.setObjectName("PracticalScrollArea")
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("""
            QScrollArea#PracticalScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea#PracticalScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)

        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(12, 10, 12, 16)
        self._content_layout.setSpacing(14)

        # Build dynamic sections
        self._build_header_card()
        self._build_practical_example_section()
        self._build_real_world_apps_section()
        self._build_knowledge_check_section()

        self._content_layout.addStretch(1)
        self._scroll.setWidget(self._content_widget)
        outer.addWidget(self._scroll)

    # ------------------------------------------------------------------
    # Section Builders
    # ------------------------------------------------------------------
    def _build_header_card(self):
        """Header card showing Category Pill, Title, and Concise Summary."""
        self._header_card = QFrame()
        self._header_card.setObjectName("HeaderCard")
        self._header_card.setStyleSheet("""
            QFrame#HeaderCard {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        h_layout = QVBoxLayout(self._header_card)
        h_layout.setContentsMargins(14, 12, 14, 12)
        h_layout.setSpacing(6)

        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        self._category_badge = QLabel("LEARNING MODULE")
        self._category_badge.setStyleSheet("""
            background-color: #EDE9FE;
            color: #5B21B6;
            font-family: Inter;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.8px;
            padding: 3px 8px;
            border-radius: 6px;
        """)
        top_row.addWidget(self._category_badge)

        self._practical_badge = QLabel("APPLICATIONS & PRACTICE")
        self._practical_badge.setStyleSheet("""
            background-color: #F1F5F9;
            color: #475569;
            font-family: Inter;
            font-size: 10px;
            font-weight: 600;
            letter-spacing: 0.5px;
            padding: 3px 8px;
            border-radius: 6px;
        """)
        top_row.addWidget(self._practical_badge)
        top_row.addStretch(1)
        h_layout.addLayout(top_row)

        self._topic_title_label = QLabel("Select a Topic")
        self._topic_title_label.setStyleSheet("""
            color: #0F172A;
            font-family: Inter;
            font-size: 16px;
            font-weight: 700;
        """)
        h_layout.addWidget(self._topic_title_label)

        self._summary_label = QLabel("Explore how this mathematical or algorithmic concept is used in industry software.")
        self._summary_label.setWordWrap(True)
        self._summary_label.setStyleSheet("""
            color: #475569;
            font-family: Inter;
            font-size: 12.5px;
            line-height: 1.4;
        """)
        h_layout.addWidget(self._summary_label)

        self._content_layout.addWidget(self._header_card)

    def _build_practical_example_section(self):
        """Feature B: Practical Example Section."""
        self._example_container = QWidget()
        v_layout = QVBoxLayout(self._example_container)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(6)

        # Section Heading
        sec_header = QHBoxLayout()
        sec_header.setSpacing(6)
        pill = QLabel("PRACTICAL EXAMPLE")
        pill.setStyleSheet("""
            color: #0284C7;
            background-color: #E0F2FE;
            font-family: Inter;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.8px;
            padding: 2px 7px;
            border-radius: 5px;
        """)
        sec_header.addWidget(pill)
        lbl = QLabel("Familiar Scenario")
        lbl.setStyleSheet("color: #64748B; font-family: Inter; font-size: 11.5px; font-weight: 500;")
        sec_header.addWidget(lbl)
        sec_header.addStretch(1)
        v_layout.addLayout(sec_header)

        # Card Content
        self._example_card = QFrame()
        self._example_card.setObjectName("ExampleCard")
        self._example_card.setStyleSheet("""
            QFrame#ExampleCard {
                background-color: #FFFFFF;
                border: 1px solid #BAE6FD;
                border-left: 3.5px solid #0284C7;
                border-radius: 10px;
            }
        """)
        c_layout = QVBoxLayout(self._example_card)
        c_layout.setContentsMargins(14, 12, 14, 12)
        c_layout.setSpacing(8)

        self._scenario_title = QLabel("Example Scenario")
        self._scenario_title.setStyleSheet("""
            color: #0369A1;
            font-family: Inter;
            font-size: 13.5px;
            font-weight: 700;
        """)
        c_layout.addWidget(self._scenario_title)

        self._scenario_desc = QLabel("")
        self._scenario_desc.setWordWrap(True)
        self._scenario_desc.setStyleSheet("""
            color: #1E293B;
            font-family: Inter;
            font-size: 12.5px;
            line-height: 1.45;
        """)
        c_layout.addWidget(self._scenario_desc)

        # Connection to ProofMotion visualization
        self._connection_box = QFrame()
        self._connection_box.setStyleSheet("""
            background-color: #F8FAFC;
            border: 1px dashed #CBD5E1;
            border-radius: 8px;
        """)
        conn_layout = QVBoxLayout(self._connection_box)
        conn_layout.setContentsMargins(10, 8, 10, 8)
        conn_layout.setSpacing(3)

        conn_badge = QLabel("HOW PROOFMOTION DEMONSTRATES THIS:")
        conn_badge.setStyleSheet("""
            color: #6C5CE7;
            font-family: Inter;
            font-size: 9.5px;
            font-weight: 700;
            letter-spacing: 0.6px;
        """)
        conn_layout.addWidget(conn_badge)

        self._connection_text = QLabel("")
        self._connection_text.setWordWrap(True)
        self._connection_text.setStyleSheet("""
            color: #334155;
            font-family: Inter;
            font-size: 12px;
            line-height: 1.4;
        """)
        conn_layout.addWidget(self._connection_text)
        c_layout.addWidget(self._connection_box)

        v_layout.addWidget(self._example_card)
        self._content_layout.addWidget(self._example_container)

    def _build_real_world_apps_section(self):
        """Feature A: Real-World Applications ("Where Is It Used?")."""
        self._apps_container = QWidget()
        self._apps_layout = QVBoxLayout(self._apps_container)
        self._apps_layout.setContentsMargins(0, 0, 0, 0)
        self._apps_layout.setSpacing(8)

        # Section Heading
        sec_header = QHBoxLayout()
        sec_header.setSpacing(6)
        pill = QLabel("WHERE IS IT USED?")
        pill.setStyleSheet("""
            color: #7C3AED;
            background-color: #EDE9FE;
            font-family: Inter;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.8px;
            padding: 2px 7px;
            border-radius: 5px;
        """)
        sec_header.addWidget(pill)
        lbl = QLabel("Real-World Software & Engineering Applications")
        lbl.setStyleSheet("color: #64748B; font-family: Inter; font-size: 11.5px; font-weight: 500;")
        sec_header.addWidget(lbl)
        sec_header.addStretch(1)
        self._apps_layout.addLayout(sec_header)

        # Applications List Area
        self._apps_list_widget = QWidget()
        self._apps_list_layout = QVBoxLayout(self._apps_list_widget)
        self._apps_list_layout.setContentsMargins(0, 0, 0, 0)
        self._apps_list_layout.setSpacing(8)
        self._apps_layout.addWidget(self._apps_list_widget)

        self._content_layout.addWidget(self._apps_container)

    def _build_knowledge_check_section(self):
        """Feature C: Quick Knowledge Check Section."""
        self._quiz_container = QWidget()
        self._quiz_layout = QVBoxLayout(self._quiz_container)
        self._quiz_layout.setContentsMargins(0, 0, 0, 0)
        self._quiz_layout.setSpacing(8)

        # Section Heading
        sec_header = QHBoxLayout()
        sec_header.setSpacing(6)
        pill = QLabel("QUICK KNOWLEDGE CHECK")
        pill.setStyleSheet("""
            color: #059669;
            background-color: #D1FAE5;
            font-family: Inter;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.8px;
            padding: 2px 7px;
            border-radius: 5px;
        """)
        sec_header.addWidget(pill)
        lbl = QLabel("Test your understanding of the concept & usage")
        lbl.setStyleSheet("color: #64748B; font-family: Inter; font-size: 11.5px; font-weight: 500;")
        sec_header.addWidget(lbl)
        sec_header.addStretch(1)
        self._quiz_layout.addLayout(sec_header)

        # Questions List Container
        self._questions_widget = QWidget()
        self._questions_layout = QVBoxLayout(self._questions_widget)
        self._questions_layout.setContentsMargins(0, 0, 0, 0)
        self._questions_layout.setSpacing(10)
        self._quiz_layout.addWidget(self._questions_widget)

        self._content_layout.addWidget(self._quiz_container)

    # ------------------------------------------------------------------
    # Public Controller API
    # ------------------------------------------------------------------
    def set_topic(self, topic_key: str):
        """Load and display practical learning data for the given topic."""
        if not topic_key:
            return
        self._current_topic_key = topic_key
        data = get_practical_content(topic_key)
        self._current_data = data

        # 1. Update Header
        self._category_badge.setText(data.category.upper())
        self._topic_title_label.setText(data.display_name)
        self._summary_label.setText(data.summary)

        # 2. Update Practical Example
        self._scenario_title.setText(data.practical_example.scenario)
        self._scenario_desc.setText(data.practical_example.description)
        self._connection_text.setText(data.practical_example.visualization_connection)

        # 3. Rebuild Real-World Applications Cards
        # Clear existing
        while self._apps_list_layout.count():
            item = self._apps_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for app in data.real_world_applications:
            card = self._create_app_card(app)
            self._apps_list_layout.addWidget(card)

        # 4. Rebuild Knowledge Check Questions
        while self._questions_layout.count():
            item = self._questions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for idx, q in enumerate(data.knowledge_check):
            q_widget = QuizQuestionWidget(idx, q, self)
            self._questions_layout.addWidget(q_widget)

        # Scroll to top smoothly
        if self._scroll:
            self._scroll.verticalScrollBar().setValue(0)

    def _create_app_card(self, app: RealWorldApplication) -> QFrame:
        card = QFrame()
        card.setObjectName("AppCard")
        card.setStyleSheet("""
            QFrame#AppCard {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        # Top row: Domain Tag + Title
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        tag_badge = QLabel(app.tag.upper())
        tag_badge.setStyleSheet("""
            background-color: #F1F5F9;
            color: #475569;
            font-family: Inter;
            font-size: 9.5px;
            font-weight: 700;
            letter-spacing: 0.5px;
            padding: 2px 6px;
            border-radius: 4px;
        """)
        top_row.addWidget(tag_badge)

        title_lbl = QLabel(app.title)
        title_lbl.setStyleSheet("""
            color: #0F172A;
            font-family: Inter;
            font-size: 13px;
            font-weight: 700;
        """)
        top_row.addWidget(title_lbl, stretch=1)
        layout.addLayout(top_row)

        desc_lbl = QLabel(app.description)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("""
            color: #334155;
            font-family: Inter;
            font-size: 12px;
            line-height: 1.4;
        """)
        layout.addWidget(desc_lbl)

        # Contexts / Software bullet points
        if app.contexts:
            ctx_box = QFrame()
            ctx_box.setStyleSheet("background-color: #F8FAFC; border-radius: 6px; padding: 2px;")
            ctx_layout = QVBoxLayout(ctx_box)
            ctx_layout.setContentsMargins(8, 6, 8, 6)
            ctx_layout.setSpacing(3)

            for ctx in app.contexts:
                bullet = QLabel(f"•  {ctx}")
                bullet.setWordWrap(True)
                bullet.setStyleSheet("color: #475569; font-family: Inter; font-size: 11.5px; line-height: 1.35;")
                ctx_layout.addWidget(bullet)

            layout.addWidget(ctx_box)

        return card
