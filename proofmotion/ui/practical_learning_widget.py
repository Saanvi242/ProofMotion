"""
ui/practical_learning_widget.py
--------------------------------
Separate, dedicated views and dialogs for:
1. Explore Applications: Real-World Applications & Practical Example (Reference/Reading interface).
2. Test Your Understanding: Interactive Knowledge Check (Quiz interface with Check Answer & completion state).

Both dialogs are independent, non-modal, completely emoji-free, and styled with ProofMotion's
clean purple, lavender, slate, and white design system.
"""

from typing import List, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QButtonGroup, QSizePolicy, QDialog, QStackedWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt5.QtGui import QFont, QColor

from core.practical_content import (
    TopicPracticalData, QuizQuestion, RealWorldApplication, PracticalExample,
    get_practical_content
)


# ==============================================================================
# FEATURE 1: EXPLORE APPLICATIONS (Practical Examples & Real-World Context)
# ==============================================================================

class ExploreApplicationsWidget(QWidget):
    """
    Dedicated reading and reference view containing ONLY:
    - Topic summary and domain category
    - Practical Example (intuitive scenario + connection to ProofMotion)
    - Real-World Applications ("Where Is It Used?") with industrial contexts
    Does NOT contain any MCQ questions or quiz elements.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ExploreApplicationsWidget")
        self._current_topic_key = ""
        self._current_data: Optional[TopicPracticalData] = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setObjectName("AppsScrollArea")
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("""
            QScrollArea#AppsScrollArea {
                background-color: #F8FAFC;
                border: none;
            }
            QScrollArea#AppsScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)

        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(24, 20, 24, 28)
        self._content_layout.setSpacing(20)

        # Build reading sections
        self._build_header_card()
        self._build_practical_example_section()
        self._build_real_world_apps_section()

        self._content_layout.addStretch(1)
        self._scroll.setWidget(self._content_widget)
        outer.addWidget(self._scroll)

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
        h_layout.setContentsMargins(20, 18, 20, 18)
        h_layout.setSpacing(8)

        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        self._category_badge = QLabel("LEARNING MODULE")
        self._category_badge.setStyleSheet("""
            background-color: #EDE9FE;
            color: #5B21B6;
            font-family: Inter;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.8px;
            padding: 4px 10px;
            border-radius: 6px;
        """)
        top_row.addWidget(self._category_badge)

        self._practical_badge = QLabel("REAL-WORLD APPLICATIONS")
        self._practical_badge.setStyleSheet("""
            background-color: #F1F5F9;
            color: #475569;
            font-family: Inter;
            font-size: 10.5px;
            font-weight: 600;
            letter-spacing: 0.5px;
            padding: 4px 10px;
            border-radius: 6px;
        """)
        top_row.addWidget(self._practical_badge)
        top_row.addStretch(1)
        h_layout.addLayout(top_row)

        self._topic_title_label = QLabel("Select a Topic")
        self._topic_title_label.setStyleSheet("""
            color: #0F172A;
            font-family: Inter;
            font-size: 18px;
            font-weight: 700;
        """)
        h_layout.addWidget(self._topic_title_label)

        self._summary_label = QLabel("Explore how this mathematical or algorithmic concept is used in industry software.")
        self._summary_label.setWordWrap(True)
        self._summary_label.setStyleSheet("""
            color: #475569;
            font-family: Inter;
            font-size: 13.5px;
            line-height: 1.5;
        """)
        h_layout.addWidget(self._summary_label)

        self._content_layout.addWidget(self._header_card)

    def _build_practical_example_section(self):
        """Practical Example Section connecting the concept to a familiar scenario."""
        self._example_container = QWidget()
        v_layout = QVBoxLayout(self._example_container)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(8)

        sec_header = QHBoxLayout()
        sec_header.setSpacing(8)
        pill = QLabel("PRACTICAL EXAMPLE")
        pill.setStyleSheet("""
            color: #0284C7;
            background-color: #E0F2FE;
            font-family: Inter;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.8px;
            padding: 3px 9px;
            border-radius: 6px;
        """)
        sec_header.addWidget(pill)
        lbl = QLabel("Familiar scenario connecting theory to everyday experience")
        lbl.setStyleSheet("color: #64748B; font-family: Inter; font-size: 12px; font-weight: 500;")
        sec_header.addWidget(lbl)
        sec_header.addStretch(1)
        v_layout.addLayout(sec_header)

        self._example_card = QFrame()
        self._example_card.setObjectName("ExampleCard")
        self._example_card.setStyleSheet("""
            QFrame#ExampleCard {
                background-color: #FFFFFF;
                border: 1px solid #BAE6FD;
                border-left: 4px solid #0284C7;
                border-radius: 12px;
            }
        """)
        c_layout = QVBoxLayout(self._example_card)
        c_layout.setContentsMargins(20, 16, 20, 16)
        c_layout.setSpacing(10)

        self._scenario_title = QLabel("Example Scenario")
        self._scenario_title.setStyleSheet("""
            color: #0369A1;
            font-family: Inter;
            font-size: 14.5px;
            font-weight: 700;
        """)
        c_layout.addWidget(self._scenario_title)

        self._scenario_desc = QLabel("")
        self._scenario_desc.setWordWrap(True)
        self._scenario_desc.setStyleSheet("""
            color: #1E293B;
            font-family: Inter;
            font-size: 13.5px;
            line-height: 1.5;
        """)
        c_layout.addWidget(self._scenario_desc)

        self._connection_box = QFrame()
        self._connection_box.setStyleSheet("""
            background-color: #F8FAFC;
            border: 1px dashed #CBD5E1;
            border-radius: 8px;
        """)
        conn_layout = QVBoxLayout(self._connection_box)
        conn_layout.setContentsMargins(14, 10, 14, 10)
        conn_layout.setSpacing(4)

        conn_badge = QLabel("HOW PROOFMOTION DEMONSTRATES THIS:")
        conn_badge.setStyleSheet("""
            color: #6C5CE7;
            font-family: Inter;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.7px;
        """)
        conn_layout.addWidget(conn_badge)

        self._connection_text = QLabel("")
        self._connection_text.setWordWrap(True)
        self._connection_text.setStyleSheet("""
            color: #334155;
            font-family: Inter;
            font-size: 12.5px;
            line-height: 1.45;
        """)
        conn_layout.addWidget(self._connection_text)
        c_layout.addWidget(self._connection_box)

        v_layout.addWidget(self._example_card)
        self._content_layout.addWidget(self._example_container)

    def _build_real_world_apps_section(self):
        """Real-World Applications ("Where Is It Used?")."""
        self._apps_container = QWidget()
        self._apps_layout = QVBoxLayout(self._apps_container)
        self._apps_layout.setContentsMargins(0, 0, 0, 0)
        self._apps_layout.setSpacing(10)

        sec_header = QHBoxLayout()
        sec_header.setSpacing(8)
        pill = QLabel("WHERE IS IT USED?")
        pill.setStyleSheet("""
            color: #7C3AED;
            background-color: #EDE9FE;
            font-family: Inter;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.8px;
            padding: 3px 9px;
            border-radius: 6px;
        """)
        sec_header.addWidget(pill)
        lbl = QLabel("Industrial software, hardware, and engineering systems")
        lbl.setStyleSheet("color: #64748B; font-family: Inter; font-size: 12px; font-weight: 500;")
        sec_header.addWidget(lbl)
        sec_header.addStretch(1)
        self._apps_layout.addLayout(sec_header)

        self._apps_list_widget = QWidget()
        self._apps_list_layout = QVBoxLayout(self._apps_list_widget)
        self._apps_list_layout.setContentsMargins(0, 0, 0, 0)
        self._apps_list_layout.setSpacing(12)
        self._apps_layout.addWidget(self._apps_list_widget)

        self._content_layout.addWidget(self._apps_container)

    def set_topic(self, topic_key: str):
        """Load and display practical learning data for the given topic."""
        if not topic_key:
            return
        self._current_topic_key = topic_key
        data = get_practical_content(topic_key)
        self._current_data = data

        self._category_badge.setText(data.category.upper())
        self._topic_title_label.setText(data.display_name)
        self._summary_label.setText(data.summary)

        self._scenario_title.setText(data.practical_example.scenario)
        self._scenario_desc.setText(data.practical_example.description)
        self._connection_text.setText(data.practical_example.visualization_connection)

        # Rebuild Application cards
        while self._apps_list_layout.count():
            item = self._apps_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for app in data.real_world_applications:
            card = self._create_app_card(app)
            self._apps_list_layout.addWidget(card)

        self.scroll_to_top()

    def scroll_to_top(self):
        if self._scroll:
            self._scroll.verticalScrollBar().setValue(0)

    def _create_app_card(self, app: RealWorldApplication) -> QFrame:
        card = QFrame()
        card.setObjectName("AppCard")
        card.setStyleSheet("""
            QFrame#AppCard {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        tag_badge = QLabel(app.tag.upper())
        tag_badge.setStyleSheet("""
            background-color: #F1F5F9;
            color: #475569;
            font-family: Inter;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.6px;
            padding: 3px 8px;
            border-radius: 5px;
        """)
        top_row.addWidget(tag_badge)

        title_lbl = QLabel(app.title)
        title_lbl.setStyleSheet("""
            color: #0F172A;
            font-family: Inter;
            font-size: 14px;
            font-weight: 700;
        """)
        top_row.addWidget(title_lbl, stretch=1)
        layout.addLayout(top_row)

        desc_lbl = QLabel(app.description)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("""
            color: #334155;
            font-family: Inter;
            font-size: 13px;
            line-height: 1.5;
        """)
        layout.addWidget(desc_lbl)

        if app.contexts:
            ctx_box = QFrame()
            ctx_box.setStyleSheet("background-color: #F8FAFC; border-radius: 8px; padding: 4px;")
            ctx_layout = QVBoxLayout(ctx_box)
            ctx_layout.setContentsMargins(12, 8, 12, 8)
            ctx_layout.setSpacing(4)

            for ctx in app.contexts:
                bullet = QLabel(f"•  {ctx}")
                bullet.setWordWrap(True)
                bullet.setStyleSheet("color: #475569; font-family: Inter; font-size: 12.5px; line-height: 1.4;")
                ctx_layout.addWidget(bullet)

            layout.addWidget(ctx_box)

        return card


class RealWorldApplicationsDialog(QDialog):
    """
    Dedicated, spacious overlay dialog displaying ONLY Practical Examples and Real-World Applications.
    Completely isolated from quiz/MCQ elements.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ProofMotion — Real-World Applications")
        self.setModal(False)
        self.resize(760, 680)
        self.setMinimumSize(620, 480)

        self.setStyleSheet("""
            QDialog {
                background-color: #F8FAFC;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header Bar
        header = QFrame()
        header.setFixedHeight(64)
        header.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-bottom: 1.5px solid #E2E8F0;
            }
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 0, 20, 0)
        h_layout.setSpacing(12)

        title_col = QVBoxLayout()
        title_col.setSpacing(1)
        title_col.setAlignment(Qt.AlignVCenter)

        title_lbl = QLabel("Practical Applications & Real-World Context")
        title_lbl.setStyleSheet("""
            color: #0F172A;
            font-family: Inter;
            font-size: 15px;
            font-weight: 700;
            background: transparent;
        """)
        sub_lbl = QLabel("Industrial software, hardware, and engineering systems")
        sub_lbl.setStyleSheet("""
            color: #64748B;
            font-family: Inter;
            font-size: 12px;
            background: transparent;
        """)
        title_col.addWidget(title_lbl)
        title_col.addWidget(sub_lbl)
        h_layout.addLayout(title_col, stretch=1)

        # Close button
        self._close_btn = QPushButton("Close")
        self._close_btn.setCursor(Qt.PointingHandCursor)
        self._close_btn.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 6px 14px;
                font-family: Inter;
                font-size: 12.5px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                color: #0F172A;
            }
        """)
        self._close_btn.clicked.connect(self.close)
        h_layout.addWidget(self._close_btn)

        layout.addWidget(header)

        # Embed reading widget
        self.practical_widget = ExploreApplicationsWidget(self)
        layout.addWidget(self.practical_widget, stretch=1)

    def open_topic(self, topic_key: str):
        self.practical_widget.set_topic(topic_key)
        self.show()
        self.raise_()
        self.activateWindow()

    def set_topic(self, topic_key: str):
        self.practical_widget.set_topic(topic_key)


# ==============================================================================
# FEATURE 2: TEST YOUR UNDERSTANDING (Dedicated Interactive Knowledge Check)
# ==============================================================================

class KnowledgeCheckWidget(QWidget):
    """
    Dedicated interactive quiz view containing ONLY:
    - Topic-specific multiple-choice questions
    - 4 selectable options with explicit selection state
    - "Check Answer" submit button
    - Correct/Incorrect result indication with explanation
    - "Next Question" progression
    - Clean quiz completion state with score summary
    Does NOT contain practical example or real-world application cards.
    """
    quizCompleted = pyqtSignal(int, int)  # correct_count, total_count

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("KnowledgeCheckWidget")
        self._current_topic_key = ""
        self._current_data: Optional[TopicPracticalData] = None
        self._questions: List[QuizQuestion] = []
        self._current_q_index = 0
        self._selected_opt_index = -1
        self._score = 0
        self._question_graded = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setObjectName("QuizScrollArea")
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("""
            QScrollArea#QuizScrollArea {
                background-color: #F8FAFC;
                border: none;
            }
            QScrollArea#QuizScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)

        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(24, 20, 24, 24)
        self._content_layout.setSpacing(16)

        # Header Card
        self._build_header_card()

        # Quiz View Stack (Page 0: Question View, Page 1: Completion View)
        self._view_stack = QStackedWidget()

        # Page 0: Question View
        self._q_page = QWidget()
        self._q_layout = QVBoxLayout(self._q_page)
        self._q_layout.setContentsMargins(0, 0, 0, 0)
        self._q_layout.setSpacing(14)
        self._build_question_view()
        self._view_stack.addWidget(self._q_page)

        # Page 1: Completion View
        self._completion_page = QWidget()
        self._comp_layout = QVBoxLayout(self._completion_page)
        self._comp_layout.setContentsMargins(0, 0, 0, 0)
        self._comp_layout.setSpacing(14)
        self._build_completion_view()
        self._view_stack.addWidget(self._completion_page)

        self._content_layout.addWidget(self._view_stack)
        self._content_layout.addStretch(1)

        self._scroll.setWidget(self._content_widget)
        outer.addWidget(self._scroll)

    def _build_header_card(self):
        self._header_card = QFrame()
        self._header_card.setObjectName("QuizHeaderCard")
        self._header_card.setStyleSheet("""
            QFrame#QuizHeaderCard {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        h_layout = QVBoxLayout(self._header_card)
        h_layout.setContentsMargins(18, 16, 18, 16)
        h_layout.setSpacing(8)

        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        self._category_badge = QLabel("KNOWLEDGE CHECK")
        self._category_badge.setStyleSheet("""
            background-color: #EDE9FE;
            color: #5B21B6;
            font-family: Inter;
            font-size: 10.5px;
            font-weight: 700;
            letter-spacing: 0.8px;
            padding: 3px 9px;
            border-radius: 6px;
        """)
        top_row.addWidget(self._category_badge)

        self._progress_badge = QLabel("Question 1 of 1")
        self._progress_badge.setStyleSheet("""
            background-color: #F1F5F9;
            color: #475569;
            font-family: Inter;
            font-size: 10.5px;
            font-weight: 600;
            padding: 3px 9px;
            border-radius: 6px;
        """)
        top_row.addWidget(self._progress_badge)
        top_row.addStretch(1)
        h_layout.addLayout(top_row)

        self._topic_title_label = QLabel("Select a Topic")
        self._topic_title_label.setStyleSheet("""
            color: #0F172A;
            font-family: Inter;
            font-size: 17px;
            font-weight: 700;
        """)
        h_layout.addWidget(self._topic_title_label)

        sub_desc = QLabel("Test your understanding of concept mechanics and practical utility.")
        sub_desc.setStyleSheet("color: #64748B; font-family: Inter; font-size: 12.5px;")
        h_layout.addWidget(sub_desc)

        self._content_layout.addWidget(self._header_card)

    def _build_question_view(self):
        # Card holding the active question
        self._question_card = QFrame()
        self._question_card.setObjectName("QuestionCard")
        self._question_card.setStyleSheet("""
            QFrame#QuestionCard {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        card_layout = QVBoxLayout(self._question_card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        # Question prompt
        self._prompt_label = QLabel("")
        self._prompt_label.setWordWrap(True)
        self._prompt_label.setStyleSheet("""
            color: #0F172A;
            font-family: Inter;
            font-size: 14px;
            font-weight: 600;
            line-height: 1.5;
        """)
        card_layout.addWidget(self._prompt_label)

        # 4 Options Buttons
        self._opt_buttons: List[QPushButton] = []
        for i in range(4):
            btn = QPushButton("")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            btn.clicked.connect(lambda checked, idx=i: self._on_option_selected(idx))
            self._opt_buttons.append(btn)
            card_layout.addWidget(btn)

        # Feedback box (hidden until Check Answer clicked)
        self._feedback_box = QFrame()
        self._feedback_box.setObjectName("QuizFeedback")
        self._feedback_box.hide()
        fb_layout = QVBoxLayout(self._feedback_box)
        fb_layout.setContentsMargins(14, 12, 14, 12)
        fb_layout.setSpacing(6)

        self._result_header = QLabel("")
        fb_layout.addWidget(self._result_header)

        self._explanation_label = QLabel("")
        self._explanation_label.setWordWrap(True)
        self._explanation_label.setStyleSheet("color: #334155; font-family: Inter; font-size: 12.5px; line-height: 1.5;")
        fb_layout.addWidget(self._explanation_label)

        card_layout.addWidget(self._feedback_box)

        # Action Button Row (Check Answer / Next Question)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch(1)

        self._action_btn = QPushButton("Check Answer")
        self._action_btn.setObjectName("QuizActionButton")
        self._action_btn.setCursor(Qt.PointingHandCursor)
        self._action_btn.setEnabled(False)
        self._action_btn.setFixedHeight(36)
        self._action_btn.setMinimumWidth(130)
        self._action_btn.setStyleSheet("""
            QPushButton#QuizActionButton {
                background-color: #6C5CE7;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-family: Inter;
                font-size: 12.5px;
                font-weight: 600;
                padding: 0px 16px;
            }
            QPushButton#QuizActionButton:hover {
                background-color: #5B4BC4;
            }
            QPushButton#QuizActionButton:disabled {
                background-color: #E2E8F0;
                color: #94A3B8;
            }
        """)
        self._action_btn.clicked.connect(self._on_action_clicked)
        btn_row.addWidget(self._action_btn)
        card_layout.addLayout(btn_row)

        self._q_layout.addWidget(self._question_card)

    def _build_completion_view(self):
        card = QFrame()
        card.setObjectName("CompletionCard")
        card.setStyleSheet("""
            QFrame#CompletionCard {
                background-color: #FFFFFF;
                border: 1px solid #BBF7D0;
                border-radius: 12px;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Quiz Completed")
        title.setStyleSheet("""
            color: #065F46;
            font-family: Inter;
            font-size: 18px;
            font-weight: 700;
        """)
        layout.addWidget(title, alignment=Qt.AlignCenter)

        self._score_label = QLabel("Score: 0 / 0")
        self._score_label.setStyleSheet("""
            color: #0F172A;
            font-family: Inter;
            font-size: 15px;
            font-weight: 600;
        """)
        layout.addWidget(self._score_label, alignment=Qt.AlignCenter)

        desc = QLabel("You have successfully verified your theoretical and practical understanding of this topic.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #475569; font-family: Inter; font-size: 13px; text-align: center;")
        layout.addWidget(desc, alignment=Qt.AlignCenter)

        self._retake_btn = QPushButton("Retake Quiz")
        self._retake_btn.setCursor(Qt.PointingHandCursor)
        self._retake_btn.setFixedHeight(34)
        self._retake_btn.setFixedWidth(120)
        self._retake_btn.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #334155;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                font-family: Inter;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                color: #0F172A;
            }
        """)
        self._retake_btn.clicked.connect(self._restart_quiz)
        layout.addWidget(self._retake_btn, alignment=Qt.AlignCenter)

        self._comp_layout.addWidget(card)

    def set_topic(self, topic_key: str):
        if not topic_key:
            return
        self._current_topic_key = topic_key
        data = get_practical_content(topic_key)
        self._current_data = data
        self._questions = list(data.knowledge_check)
        self._current_q_index = 0
        self._score = 0

        self._category_badge.setText(data.category.upper())
        self._topic_title_label.setText(data.display_name)

        self._load_question(0)
        self._view_stack.setCurrentIndex(0)

    def _load_question(self, index: int):
        if not self._questions or index < 0 or index >= len(self._questions):
            return
        self._current_q_index = index
        self._selected_opt_index = -1
        self._question_graded = False

        q = self._questions[index]
        self._progress_badge.setText(f"Question {index + 1} of {len(self._questions)}")
        self._prompt_label.setText(f"Q{index + 1}.  {q.question}")
        self._explanation_label.setText(q.explanation)

        prefix_letters = ["A", "B", "C", "D"]
        for i, btn in enumerate(self._opt_buttons):
            if i < len(q.options):
                btn.show()
                letter = prefix_letters[i]
                btn.setText(f"  {letter}.  {q.options[i]}")
                btn.setEnabled(True)
                self._apply_option_style(btn, "default")
            else:
                btn.hide()

        self._feedback_box.hide()
        self._action_btn.setEnabled(False)
        self._action_btn.setText("Check Answer")

    def _on_option_selected(self, index: int):
        if self._question_graded:
            return
        self._selected_opt_index = index
        for i, btn in enumerate(self._opt_buttons):
            if i == index:
                self._apply_option_style(btn, "selected")
            else:
                self._apply_option_style(btn, "default")
        self._action_btn.setEnabled(True)

    def _on_action_clicked(self):
        if not self._question_graded:
            # Step 1: Grade Answer
            self._grade_current_question()
        else:
            # Step 2: Next question or finish
            if self._current_q_index + 1 < len(self._questions):
                self._load_question(self._current_q_index + 1)
            else:
                # Show completion page
                self._score_label.setText(f"Score: {self._score} / {len(self._questions)}")
                self._view_stack.setCurrentIndex(1)
                self.quizCompleted.emit(self._score, len(self._questions))

    def _grade_current_question(self):
        self._question_graded = True
        q = self._questions[self._current_q_index]
        is_correct = (self._selected_opt_index == q.correct_index)

        if is_correct:
            self._score += 1

        for i, btn in enumerate(self._opt_buttons):
            btn.setEnabled(False)
            if i == q.correct_index:
                self._apply_option_style(btn, "correct")
            elif i == self._selected_opt_index and not is_correct:
                self._apply_option_style(btn, "incorrect")
            else:
                self._apply_option_style(btn, "disabled")

        if is_correct:
            self._feedback_box.setStyleSheet("""
                QFrame#QuizFeedback {
                    background-color: #F0FDF4;
                    border: 1px solid #BBF7D0;
                    border-radius: 8px;
                }
            """)
            self._result_header.setText("Correct")
            self._result_header.setStyleSheet("color: #15803D; font-family: Inter; font-size: 13px; font-weight: 700;")
        else:
            self._feedback_box.setStyleSheet("""
                QFrame#QuizFeedback {
                    background-color: #FFF1F2;
                    border: 1px solid #FECDD3;
                    border-radius: 8px;
                }
            """)
            self._result_header.setText("Incorrect")
            self._result_header.setStyleSheet("color: #B91C1C; font-family: Inter; font-size: 13px; font-weight: 700;")

        self._feedback_box.show()

        if self._current_q_index + 1 < len(self._questions):
            self._action_btn.setText("Next Question →")
        else:
            self._action_btn.setText("Finish Quiz")
        self._action_btn.setEnabled(True)

    def _restart_quiz(self):
        self._score = 0
        self._load_question(0)
        self._view_stack.setCurrentIndex(0)

    def _apply_option_style(self, btn: QPushButton, state: str):
        if state == "selected":
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F5F3FF;
                    color: #5B21B6;
                    border: 2px solid #6C5CE7;
                    border-radius: 8px;
                    padding: 10px 14px;
                    font-family: Inter;
                    font-size: 12.5px;
                    font-weight: 600;
                    text-align: left;
                }
            """)
        elif state == "correct":
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #ECFDF5;
                    color: #065F46;
                    border: 1.5px solid #10B981;
                    border-radius: 8px;
                    padding: 10px 14px;
                    font-family: Inter;
                    font-size: 12.5px;
                    font-weight: 600;
                    text-align: left;
                }
            """)
        elif state == "incorrect":
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #FEF2F2;
                    color: #991B1B;
                    border: 1.5px solid #EF4444;
                    border-radius: 8px;
                    padding: 10px 14px;
                    font-family: Inter;
                    font-size: 12.5px;
                    font-weight: 600;
                    text-align: left;
                }
            """)
        elif state == "disabled":
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F8FAFC;
                    color: #94A3B8;
                    border: 1px solid #E2E8F0;
                    border-radius: 8px;
                    padding: 10px 14px;
                    font-family: Inter;
                    font-size: 12.5px;
                    text-align: left;
                }
            """)
        else:  # default
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F8FAFC;
                    color: #334155;
                    border: 1px solid #CBD5E1;
                    border-radius: 8px;
                    padding: 10px 14px;
                    font-family: Inter;
                    font-size: 12.5px;
                    text-align: left;
                    line-height: 1.4;
                }
                QPushButton:hover {
                    background-color: #F1F5F9;
                    border-color: #6C5CE7;
                    color: #0F172A;
                }
            """)


class KnowledgeCheckDialog(QDialog):
    """
    Dedicated overlay dialog displaying ONLY the interactive Knowledge Check.
    Completely isolated from practical example / real-world application content.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ProofMotion — Test Your Understanding")
        self.setModal(False)
        self.resize(620, 620)
        self.setMinimumSize(540, 480)

        self.setStyleSheet("""
            QDialog {
                background-color: #F8FAFC;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header Bar
        header = QFrame()
        header.setFixedHeight(64)
        header.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-bottom: 1.5px solid #E2E8F0;
            }
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 0, 20, 0)
        h_layout.setSpacing(12)

        title_col = QVBoxLayout()
        title_col.setSpacing(1)
        title_col.setAlignment(Qt.AlignVCenter)

        title_lbl = QLabel("Test Your Understanding")
        title_lbl.setStyleSheet("""
            color: #0F172A;
            font-family: Inter;
            font-size: 15px;
            font-weight: 700;
            background: transparent;
        """)
        sub_lbl = QLabel("Concept mechanics and practical utility check")
        sub_lbl.setStyleSheet("""
            color: #64748B;
            font-family: Inter;
            font-size: 12px;
            background: transparent;
        """)
        title_col.addWidget(title_lbl)
        title_col.addWidget(sub_lbl)
        h_layout.addLayout(title_col, stretch=1)

        # Close button
        self._close_btn = QPushButton("Close")
        self._close_btn.setCursor(Qt.PointingHandCursor)
        self._close_btn.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 6px 14px;
                font-family: Inter;
                font-size: 12.5px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                color: #0F172A;
            }
        """)
        self._close_btn.clicked.connect(self.close)
        h_layout.addWidget(self._close_btn)

        layout.addWidget(header)

        # Embed KnowledgeCheckWidget
        self.quiz_widget = KnowledgeCheckWidget(self)
        layout.addWidget(self.quiz_widget, stretch=1)

    def open_topic(self, topic_key: str):
        self.quiz_widget.set_topic(topic_key)
        self.show()
        self.raise_()
        self.activateWindow()

    def set_topic(self, topic_key: str):
        self.quiz_widget.set_topic(topic_key)


# ==============================================================================
# BACKWARD COMPATIBILITY ALIASES
# ==============================================================================
PracticalLearningDialog = RealWorldApplicationsDialog
PracticalLearningWidget = ExploreApplicationsWidget
