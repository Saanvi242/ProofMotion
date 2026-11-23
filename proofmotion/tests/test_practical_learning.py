"""
tests/test_practical_learning.py
---------------------------------
Automated tests for Practical Learning & Real-World Applications:
1. Knowledge base content integrity across all categories (Theorems, Sorting,
   Searching, Graphs, Trees, Transformations, Rasterization, Clipping).
2. Separate Explore Applications interface (Practical Example & Applications only, zero MCQs).
3. Separate Test Your Understanding interface (Interactive MCQs with Check Answer & completion state, zero application cards).
4. Strict separation of button triggers:
   - Explore Applications opens ONLY applications_dialog.
   - Test Your Understanding opens ONLY quiz_dialog.
5. Absence of emojis across all labels and controls.
6. Playback continuity during dialog interactions.
"""

import os
import unittest
import re
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from core.practical_content import (
    PRACTICAL_KNOWLEDGE_BASE, get_practical_content, TopicPracticalData,
    QuizQuestion, RealWorldApplication, PracticalExample
)
from ui.practical_learning_widget import (
    ExploreApplicationsWidget, RealWorldApplicationsDialog,
    KnowledgeCheckWidget, KnowledgeCheckDialog,
    PracticalLearningWidget, PracticalLearningDialog
)
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
            # Verify knowledge check questions (3 to 5 questions per topic)
            self.assertTrue(3 <= len(data.knowledge_check) <= 5)
            for q in data.knowledge_check:
                self.assertTrue(len(q.question) > 10)
                self.assertEqual(len(q.options), 4)
                self.assertTrue(0 <= q.correct_index < 4)
                self.assertTrue(len(q.explanation) > 10)

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


class TestExploreApplicationsWidget(unittest.TestCase):
    """Verifies that ExploreApplicationsWidget contains ONLY practical applications and examples, no MCQs."""

    def setUp(self):
        self.widget = ExploreApplicationsWidget()

    def test_contains_only_applications_and_examples(self):
        self.widget.set_topic("bubble_sort")
        self.assertEqual(self.widget._topic_title_label.text(), "Bubble Sort")
        self.assertIn("student", self.widget._scenario_title.text().lower())
        self.assertGreater(self.widget._apps_list_layout.count(), 0)

        # Must NOT have quiz widgets or question layouts
        self.assertFalse(hasattr(self.widget, "_opt_buttons"))
        self.assertFalse(hasattr(self.widget, "_questions_layout"))
        self.assertFalse(hasattr(self.widget, "_action_btn"))


class TestKnowledgeCheckWidget(unittest.TestCase):
    """Verifies that KnowledgeCheckWidget contains ONLY interactive quiz questions, no application cards."""

    def setUp(self):
        self.widget = KnowledgeCheckWidget()

    def test_contains_only_quiz_elements(self):
        self.widget.set_topic("bubble_sort")
        self.assertEqual(self.widget._topic_title_label.text(), "Bubble Sort")
        self.assertTrue(len(self.widget._opt_buttons) == 4)
        self.assertFalse(self.widget._action_btn.isEnabled())  # Disabled before selection

        # Must NOT have practical example or application cards
        self.assertFalse(hasattr(self.widget, "_apps_list_layout"))
        self.assertFalse(hasattr(self.widget, "_scenario_title"))
        self.assertFalse(hasattr(self.widget, "_connection_box"))

    def test_quiz_interactive_flow(self):
        self.widget.set_topic("bubble_sort")
        q = self.widget._questions[0]
        correct_idx = q.correct_index

        # Select correct option
        self.widget._on_option_selected(correct_idx)
        self.assertTrue(self.widget._action_btn.isEnabled())
        self.assertEqual(self.widget._action_btn.text(), "Check Answer")

        # Click Check Answer
        self.widget._on_action_clicked()
        self.assertTrue(self.widget._question_graded)
        self.assertFalse(self.widget._feedback_box.isHidden())
        self.assertEqual(self.widget._result_header.text(), "Correct")
        self.assertEqual(self.widget._score, 1)


class TestMainWindowIndependentTriggers(unittest.TestCase):
    """Verifies that Explore Applications and Test Your Understanding open two completely separate dialogs."""

    def setUp(self):
        self.engine = TheoremEngine()
        self.window = MainWindow(theorems=self.engine.get_theorems_list())
        self.controller = ApplicationController(self.window, engine=self.engine)

    def test_explore_applications_opens_only_applications_dialog(self):
        panel = self.window.parameter_panel
        self.assertFalse(self.window.applications_dialog.isVisible())
        self.assertFalse(self.window.quiz_dialog.isVisible())

        # Click Explore Applications
        panel._explore_apps_btn.click()

        self.assertTrue(self.window.applications_dialog.isVisible())
        self.assertFalse(self.window.quiz_dialog.isVisible())

        self.window.applications_dialog.close()
        self.assertFalse(self.window.applications_dialog.isVisible())

    def test_test_understanding_opens_only_quiz_dialog(self):
        panel = self.window.parameter_panel
        self.assertFalse(self.window.applications_dialog.isVisible())
        self.assertFalse(self.window.quiz_dialog.isVisible())

        # Click Test Your Understanding
        panel._quiz_link_btn.click()

        self.assertTrue(self.window.quiz_dialog.isVisible())
        self.assertFalse(self.window.applications_dialog.isVisible())

        self.window.quiz_dialog.close()
        self.assertFalse(self.window.quiz_dialog.isVisible())

    def test_independent_dialog_instances(self):
        # Verify that applications_dialog and quiz_dialog are distinct classes and instances
        self.assertNotEqual(self.window.applications_dialog, self.window.quiz_dialog)
        self.assertIsInstance(self.window.applications_dialog, RealWorldApplicationsDialog)
        self.assertIsInstance(self.window.quiz_dialog, KnowledgeCheckDialog)

    def test_equation_panel_hud_triggers(self):
        self.controller.on_module_selected("sorting")
        self.controller.on_topic_selected("bubble_sort")

        # Not final step: should open applications dialog
        self.window.equation_panel._is_final_step = False
        self.window.equation_panel._apps_btn.click()
        self.assertTrue(self.window.applications_dialog.isVisible())
        self.assertFalse(self.window.quiz_dialog.isVisible())
        self.window.applications_dialog.close()

        # Final step: should open quiz dialog
        self.window.equation_panel._is_final_step = True
        self.window.equation_panel._apps_btn.click()
        self.assertTrue(self.window.quiz_dialog.isVisible())
        self.assertFalse(self.window.applications_dialog.isVisible())
        self.window.quiz_dialog.close()

    def test_no_emojis_in_feature_interfaces(self):
        # Helper regex to detect emoji unicode characters
        emoji_pattern = re.compile(r'[\U00010000-\U0010ffff\u2600-\u27bf\u2300-\u23ff\u2b50-\u2b55\u203c-\u2049]')

        # 1. Parameter Panel controls
        self.assertFalse(bool(emoji_pattern.search(self.window.parameter_panel._explore_apps_btn.text())))
        self.assertFalse(bool(emoji_pattern.search(self.window.parameter_panel._quiz_link_btn.text())))

        # 2. Equation Panel HUD button
        self.assertFalse(bool(emoji_pattern.search(self.window.equation_panel._apps_btn.text())))

        # 3. Dialog Window Titles and Header Labels
        self.assertFalse(bool(emoji_pattern.search(self.window.applications_dialog.windowTitle())))
        self.assertFalse(bool(emoji_pattern.search(self.window.quiz_dialog.windowTitle())))

    def test_dialog_does_not_reset_playback(self):
        self.controller.on_module_selected("sorting")
        self.controller.on_topic_selected("bubble_sort")
        self.controller.on_step_selected(3)
        self.assertEqual(self.controller.current_step_index, 3)

        # Open applications dialog
        self.window._open_applications_dialog("bubble_sort")
        self.assertTrue(self.window.applications_dialog.isVisible())
        self.assertEqual(self.controller.current_step_index, 3)
        self.window.applications_dialog.close()

        # Open quiz dialog
        self.window._open_quiz_dialog("bubble_sort")
        self.assertTrue(self.window.quiz_dialog.isVisible())
        self.assertEqual(self.controller.current_step_index, 3)
        self.window.quiz_dialog.close()


if __name__ == "__main__":
    unittest.main()
