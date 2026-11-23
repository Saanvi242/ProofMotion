"""
ui/lesson_completion_banner.py
------------------------------
A small, polished, dismissible banner displayed when the user reaches the
final step of a lesson for the first time in a lesson session.

Congratulates the user, directs them to Lesson Resources (Applications & Quiz),
and provides a quick action for PDF export. Does not block the interface,
interrupt playback, or reset the lesson.
"""

from PyQt5.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QWidget, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal


class LessonCompletionBanner(QFrame):
    openResourcesRequested = pyqtSignal()
    exportPdfRequested = pyqtSignal()
    dismissed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LessonCompletionBanner")
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.setStyleSheet("""
            QFrame#LessonCompletionBanner {
                background-color: #FAF5FF;
                border: 1.5px solid #E9D5FF;
                border-radius: 10px;
                padding: 4px 10px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(12)

        # Left Info Section
        info_col = QVBoxLayout()
        info_col.setContentsMargins(0, 0, 0, 0)
        info_col.setSpacing(3)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(8)

        badge = QLabel("LESSON COMPLETED")
        badge.setObjectName("LessonCompleteBadge")
        badge.setStyleSheet("""
            QLabel#LessonCompleteBadge {
                background-color: #EDE9FE;
                color: #6C5CE7;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 0.6px;
                padding: 2px 7px;
                border-radius: 4px;
            }
        """)
        top_row.addWidget(badge)

        headline = QLabel("Congratulations! You have completed all steps of this lesson.")
        headline.setObjectName("LessonCompleteHeadline")
        headline.setStyleSheet("""
            QLabel#LessonCompleteHeadline {
                color: #1E293B;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
                font-size: 12.5px;
                font-weight: 600;
            }
        """)
        top_row.addWidget(headline)
        top_row.addStretch(1)
        info_col.addLayout(top_row)

        desc = QLabel(
            "Visit the Lesson Resources tab to explore real-world applications or test your understanding. "
            "You can also export this lesson as a PDF study guide."
        )
        desc.setObjectName("LessonCompleteDesc")
        desc.setWordWrap(True)
        desc.setStyleSheet("""
            QLabel#LessonCompleteDesc {
                color: #64748B;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
                font-size: 11.5px;
                line-height: 1.35;
            }
        """)
        info_col.addWidget(desc)
        layout.addLayout(info_col, stretch=1)

        # Right Action Buttons
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setSpacing(8)

        self._resources_btn = QPushButton("Lesson Resources →")
        self._resources_btn.setObjectName("BannerResourcesBtn")
        self._resources_btn.setCursor(Qt.PointingHandCursor)
        self._resources_btn.setFixedHeight(30)
        self._resources_btn.setStyleSheet("""
            QPushButton#BannerResourcesBtn {
                background-color: #6C5CE7;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 0 12px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
                font-size: 11.5px;
                font-weight: 600;
            }
            QPushButton#BannerResourcesBtn:hover {
                background-color: #5B4BD5;
            }
        """)
        self._resources_btn.clicked.connect(self._on_resources_clicked)
        btn_row.addWidget(self._resources_btn)

        self._pdf_btn = QPushButton("Export PDF")
        self._pdf_btn.setObjectName("BannerPdfBtn")
        self._pdf_btn.setCursor(Qt.PointingHandCursor)
        self._pdf_btn.setFixedHeight(30)
        self._pdf_btn.setStyleSheet("""
            QPushButton#BannerPdfBtn {
                background-color: #FFFFFF;
                color: #6C5CE7;
                border: 1.5px solid #D8D1FF;
                border-radius: 6px;
                padding: 0 10px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
                font-size: 11.5px;
                font-weight: 600;
            }
            QPushButton#BannerPdfBtn:hover {
                background-color: #F5F3FF;
                border-color: #6C5CE7;
            }
        """)
        self._pdf_btn.clicked.connect(self._on_pdf_clicked)
        btn_row.addWidget(self._pdf_btn)

        self._dismiss_btn = QPushButton("✕")
        self._dismiss_btn.setObjectName("BannerDismissBtn")
        self._dismiss_btn.setCursor(Qt.PointingHandCursor)
        self._dismiss_btn.setToolTip("Dismiss notification")
        self._dismiss_btn.setFixedSize(26, 26)
        self._dismiss_btn.setStyleSheet("""
            QPushButton#BannerDismissBtn {
                background: transparent;
                color: #94A3B8;
                border: none;
                border-radius: 13px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton#BannerDismissBtn:hover {
                background-color: #EDE9FE;
                color: #6C5CE7;
            }
        """)
        self._dismiss_btn.clicked.connect(self._on_dismiss_clicked)
        btn_row.addWidget(self._dismiss_btn)

        layout.addLayout(btn_row)

    def _on_resources_clicked(self):
        self.openResourcesRequested.emit()

    def _on_pdf_clicked(self):
        self.exportPdfRequested.emit()

    def _on_dismiss_clicked(self):
        self.hide()
        self.dismissed.emit()
