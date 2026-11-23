"""
tests/test_practical_learning.py
---------------------------------
Automated tests for Practical Learning & Real-World Applications:
1. Knowledge base content integrity across all categories (Theorems, Sorting,
   Searching, Graphs, Trees, Transformations, Rasterization, Clipping).
2. UI rendering of Practical Example, Real-World Applications, and Knowledge Check.
3. Interactive quiz response validation and feedback logic.
4. Seamless integration with ParameterPanel tab switching and MainWindow.
"""

import os
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from core.practical_content import (
    PRACTICAL_KNOWLEDGE_BASE, get_practical_content, TopicPracticalData,
    QuizQuestion, RealWorldApplication, PracticalExample
)
from ui.practical_learning_widget import PracticalLearningWidget, QuizQuestionWidget
from ui.main_window import MainWindow
from controllers.application_controller import ApplicationController
from theorems.theorem_engine import TheoremEngine


os.environ["QT_QPA_PLATFORM"] = "offscreen"
app = QApplication.instance() or QApplication([])


class TestPracticalLearningContent(unittest.TestCase):
    """Verifies that all curriculum topics have rich, accurate practical content."""

    def test_coverage_of_all_eight_categories(self):
        categories_found = set()
        for key, data in PRACTICAL_KNOWLEDGE_BASE.items():
            self.assertIsInstance(data, TopicPracticalData)
            categories_found.add(data.category)
            # Verify practical example
            self.assertTrue(len(data.practical_example.scenario) > 5)
            self.assertTrue(len(data.practical_example.description) > 20)
            self.assertTrue(len(data.practical_example.visualization_connection) > 10)
            # Verify real-world applications
            self.assertGreaterEqual(len(data.real_world_applications), 1)
            for app_item in data.real_world_applications:
                self.assertTrue(len(app_item.title) > 3)
                self.assertTrue(len(app_item.description) > 15)
                self.assertGreaterEqual(len(app_item.contexts), 1)
            # Verify knowledge check questions
            self.assertGreaterEqual(len(data.knowledge_check), 1)
            for q in data.knowledge_check:
                self.assertTrue(len(q.question) > 10)
                self.assertEqual(len(q.options), 4)
                self.assertTrue(0 <= q.correct_index < 4)
                self.assertTrue(len(q.explanation) > 10)

        # Ensure major required curriculum categories exist
        cat_str = " ".join(categories_found).lower()
        self.assertIn("theorem", cat_str)
        self.assertIn("sorting", cat_str)
        self.assertIn("searching", cat_str)
        self.assertIn("graph", cat_str)
        self.assertIn("tree", cat_str)
        self.assertIn("transformation", cat_str)
        self.assertIn("rasterization", cat_str)
        self.assertIn("clipping", cat_str)

    def test_specific_faculty_topics(self):
        # Cohen-Sutherland line clipping
        cs = get_practical_content("clip_cohen_sutherland")
        self.assertEqual(cs.display_name, "Cohen-Sutherland Line Clipping")
        app_titles = [a.title.lower() for a in cs.real_world_applications]
        self.assertTrue(any("viewport" in t or "culling" in t for t in app_titles))

        # Bubble sort
        bs = get_practical_content("bubble_sort")
        self.assertIn("student", bs.practical_example.scenario.lower())

        # Prim MST
        prim = get_practical_content("prim_mst")
        self.assertIn("cable", prim.practical_example.scenario.lower())

        # 2D Translation
        trans = get_practical_content("trans_translation")
        self.assertIn("character", trans.practical_example.scenario.lower())

    def test_fallback_for_unknown_topic(self):
        data = get_practical_content("unknown_custom_algorithm")
        self.assertIsNotNone(data)
        self.assertIn("Unknown Custom Algorithm", data.display_name)
        self.assertGreaterEqual(len(data.real_world_applications), 1)
        self.assertGreaterEqual(len(data.knowledge_check), 1)


class TestPracticalLearningWidget(unittest.TestCase):
    """Verifies the UI rendering and interactive quiz logic."""

    def setUp(self):
        self.widget = PracticalLearningWidget()

    def test_topic_loading(self):
        self.widget.set_topic("bubble_sort")
        self.assertEqual(self.widget._topic_title_label.text(), "Bubble Sort")
        self.assertIn("student", self.widget._scenario_title.text().lower())
        self.assertGreater(self.widget._apps_list_layout.count(), 0)
        self.assertGreater(self.widget._questions_layout.count(), 0)

        # Switch to Cohen-Sutherland
        self.widget.set_topic("clip_cohen_sutherland")
        self.assertIn("Cohen-Sutherland", self.widget._topic_title_label.text())
        self.assertIn("map", self.widget._scenario_title.text().lower())

    def test_interactive_quiz_correct_answer(self):
        q = QuizQuestion(
            question="What is 2 + 2?",
            options=["3", "4", "5", "6"],
            correct_index=1,
            explanation="Basic arithmetic: 2 + 2 = 4."
        )
        card = QuizQuestionWidget(0, q)

        # Select correct option (index 1)
        card._buttons[1].click()
        self.assertTrue(card._answered)
        self.assertFalse(card._feedback_box.isHidden())
        self.assertIn("Correct", card._result_header.text())

    def test_interactive_quiz_incorrect_answer(self):
        q = QuizQuestion(
            question="What is the time complexity of binary search?",
            options=["O(n)", "O(n²)", "O(log n)", "O(1)"],
            correct_index=2,
            explanation="Binary search cuts the search space in half each step."
        )
        card = QuizQuestionWidget(0, q)

        # Select wrong option (index 0)
        card._buttons[0].click()
        self.assertTrue(card._answered)
        self.assertFalse(card._feedback_box.isHidden())
        self.assertIn("Incorrect", card._result_header.text())

        # Reset question
        card.reset_question()
        self.assertFalse(card._answered)
        self.assertTrue(card._feedback_box.isHidden())
        self.assertTrue(card._buttons[0].isEnabled())


class TestMainWindowIntegration(unittest.TestCase):
    """Verifies that MainWindow, ParameterPanel, and PracticalLearningDialog integrate cleanly."""

    def setUp(self):
        self.engine = TheoremEngine()
        self.window = MainWindow(theorems=self.engine.get_theorems_list())
        self.controller = ApplicationController(self.window, engine=self.engine)

    def test_parameter_panel_overlay_trigger(self):
        panel = self.window.parameter_panel
        dialog = self.window.practical_dialog
        self.assertFalse(dialog.isVisible())

        # Click Explore Applications button in parameter panel
        panel._explore_apps_btn.click()
        self.assertTrue(dialog.isVisible())
        self.assertEqual(dialog.practical_widget._current_topic_key, panel.practical_widget._current_topic_key)

        # Close dialog
        dialog.close()
        self.assertFalse(dialog.isVisible())

    def test_equation_panel_nav_button(self):
        self.controller.on_module_selected("sorting")
        self.controller.on_topic_selected("bubble_sort")

        # Click "Explore Applications ↗" in equation panel
        self.window.equation_panel._apps_btn.click()
        self.assertTrue(self.window.practical_dialog.isVisible())
        self.assertEqual(self.window.practical_dialog.practical_widget._current_topic_key, "bubble_sort")
        self.window.practical_dialog.close()

    def test_topic_switching_updates_practical_content(self):
        self.controller.on_module_selected("clipping")
        self.controller.on_topic_selected("clip_cohen_sutherland")
        self.assertEqual(
            self.window.practical_dialog.practical_widget._current_topic_key,
            "clip_cohen_sutherland"
        )
        self.assertIn(
            "Cohen-Sutherland",
            self.window.practical_dialog.practical_widget._topic_title_label.text()
        )

        # Switch to binary search
        self.controller.on_module_selected("searching")
        self.controller.on_topic_selected("binary_search")
        self.assertEqual(
            self.window.practical_dialog.practical_widget._current_topic_key,
            "binary_search"
        )
        self.assertIn(
            "Binary Search",
            self.window.practical_dialog.practical_widget._topic_title_label.text()
        )

    def test_dialog_does_not_reset_playback(self):
        self.controller.on_module_selected("sorting")
        self.controller.on_topic_selected("bubble_sort")
        self.controller.on_step_selected(3)
        self.assertEqual(self.controller.current_step_index, 3)

        # Open and close the dedicated applications dialog
        self.window._open_practical_dialog("bubble_sort", scroll_to_quiz=False)
        self.assertTrue(self.window.practical_dialog.isVisible())
        # Step index must remain exactly at 3
        self.assertEqual(self.controller.current_step_index, 3)

        self.window.practical_dialog.close()
        self.assertEqual(self.controller.current_step_index, 3)


if __name__ == "__main__":
    unittest.main()
