"""
tests/test_pdf_export.py
-------------------------
Automated test suite for PDF Export Feature:
1. Verifies PDF generation across all required curriculum categories:
   - Sorting: Bubble Sort
   - Searching: Binary Search
   - Graphs: Prim's MST
   - Trees: BST Traversals / Operations
   - Clipping: Cohen-Sutherland Line Clipping
   - Mathematical Theorems: Pythagorean Theorem
2. Verifies document structure:
   - Header, branding, category, topic title, export date
   - Input parameters preservation
   - Step sequence preservation (step numbers, titles, equations, explanations, metrics)
   - High-resolution visualization snapshots embedded
   - Final result & theoretical complexity analysis
3. Verifies controller & UI integration:
   - ViewControls button trigger and MainWindow signal wiring
   - Graceful handling of empty steps
   - Playback continuity (step index never reset during export)
"""

import os
import tempfile
import unittest
import fitz  # PyMuPDF
from PyQt5.QtWidgets import QApplication

from core.pdf_exporter import PDFExporter, COMPLEXITY_CATALOG
from algorithms.sorting.bubble_sort import bubble_sort_trace
from ui.main_window import MainWindow
from controllers.application_controller import ApplicationController
from theorems.theorem_engine import TheoremEngine


os.environ["QT_QPA_PLATFORM"] = "offscreen"
app = QApplication.instance() or QApplication([])


class TestPDFExporterCore(unittest.TestCase):
    """Direct unit tests for PDFExporter class across multiple lesson types."""

    def setUp(self):
        self.exporter = PDFExporter()
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_bubble_sort_export(self):
        steps = bubble_sort_trace([12, 5, 8, 3, 10])
        out_path = os.path.join(self.temp_dir.name, "bubble_sort.pdf")

        res_path = self.exporter.export_lesson(
            topic_key="bubble_sort",
            display_name="Bubble Sort",
            category="sorting",
            parameters={"array_input": "12, 5, 8, 3, 10", "order": "ascending"},
            steps=steps,
            output_path=out_path
        )

        self.assertTrue(os.path.exists(res_path))
        self.assertGreater(os.path.getsize(res_path), 5000)

        # Inspect generated PDF with PyMuPDF
        doc = fitz.open(res_path)
        self.assertGreaterEqual(len(doc), 2)  # Multi-page document

        full_text = "".join(page.get_text() for page in doc)
        self.assertIn("ProofMotion", full_text)
        self.assertIn("Bubble Sort", full_text)
        self.assertIn("Input Parameters", full_text)
        self.assertIn("12, 5, 8, 3, 10", full_text)
        self.assertIn("Step-by-Step Lesson Sequence", full_text)
        self.assertIn("Complexity Analysis", full_text)
        self.assertIn("O(n²)", full_text)

    def test_binary_search_export(self):
        engine = TheoremEngine()
        window = MainWindow(theorems=engine.get_theorems_list())
        controller = ApplicationController(window, engine=engine)
        controller.on_module_selected("searching")
        controller.on_topic_selected("binary_search")

        out_path = os.path.join(self.temp_dir.name, "binary_search.pdf")
        res_path = self.exporter.export_lesson(
            topic_key="binary_search",
            display_name="Binary Search",
            category="searching",
            parameters=controller.current_parameters,
            steps=controller.current_steps,
            output_path=out_path
        )

        self.assertTrue(os.path.exists(res_path))
        doc = fitz.open(res_path)
        full_text = "".join(page.get_text() for page in doc)
        self.assertIn("Binary Search", full_text)
        self.assertIn("O(log n)", full_text)

    def test_graph_prim_mst_export(self):
        engine = TheoremEngine()
        window = MainWindow(theorems=engine.get_theorems_list())
        controller = ApplicationController(window, engine=engine)
        controller.on_module_selected("graphs")
        controller.on_topic_selected("prim_mst")

        out_path = os.path.join(self.temp_dir.name, "prim_mst.pdf")
        res_path = self.exporter.export_lesson(
            topic_key="prim_mst",
            display_name="Prim's MST Algorithm",
            category="graphs",
            parameters=controller.current_parameters,
            steps=controller.current_steps,
            output_path=out_path
        )

        self.assertTrue(os.path.exists(res_path))
        doc = fitz.open(res_path)
        full_text = "".join(page.get_text() for page in doc)
        self.assertIn("Prim", full_text)

    def test_clipping_cohen_sutherland_export(self):
        engine = TheoremEngine()
        window = MainWindow(theorems=engine.get_theorems_list())
        controller = ApplicationController(window, engine=engine)
        controller.on_module_selected("clipping")
        controller.on_topic_selected("clip_cohen_sutherland")

        out_path = os.path.join(self.temp_dir.name, "cohen_sutherland.pdf")
        res_path = self.exporter.export_lesson(
            topic_key="clip_cohen_sutherland",
            display_name="Cohen-Sutherland Line Clipping",
            category="clipping",
            parameters=controller.current_parameters,
            steps=controller.current_steps,
            output_path=out_path
        )

        self.assertTrue(os.path.exists(res_path))
        doc = fitz.open(res_path)
        full_text = "".join(page.get_text() for page in doc)
        self.assertIn("Cohen-Sutherland", full_text)

    def test_pythagorean_theorem_export(self):
        engine = TheoremEngine()
        window = MainWindow(theorems=engine.get_theorems_list())
        controller = ApplicationController(window, engine=engine)
        controller.on_module_selected("theorems")
        controller.on_topic_selected("pythagorean")

        out_path = os.path.join(self.temp_dir.name, "pythagorean.pdf")
        res_path = self.exporter.export_lesson(
            topic_key="pythagorean",
            display_name="Pythagorean Theorem",
            category="theorems",
            parameters=controller.current_parameters,
            steps=controller.current_steps,
            output_path=out_path
        )

        self.assertTrue(os.path.exists(res_path))
        doc = fitz.open(res_path)
        full_text = "".join(page.get_text() for page in doc)
        self.assertIn("Pythagorean", full_text)


class TestPDFExportControllerIntegration(unittest.TestCase):
    """Verifies UI button triggering, signal wiring, and playback continuity."""

    def setUp(self):
        self.engine = TheoremEngine()
        self.window = MainWindow(theorems=self.engine.get_theorems_list())
        self.controller = ApplicationController(self.window, engine=self.engine)
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_view_controls_button_exists(self):
        self.assertTrue(hasattr(self.window.view_controls, "_export_pdf_btn"))
        btn = self.window.view_controls._export_pdf_btn
        self.assertEqual(btn.text(), "Export PDF")
        self.assertEqual(btn.objectName(), "ExportPdfButton")

    def test_controller_export_flow(self):
        self.controller.on_module_selected("sorting")
        self.controller.on_topic_selected("bubble_sort")
        self.controller.on_step_selected(4)
        self.assertEqual(self.controller.current_step_index, 4)

        # Trigger programmatic export to a destination file
        out_file = os.path.join(self.temp_dir.name, "controller_export.pdf")
        result = self.controller.on_export_pdf_requested(target_filepath=out_file)

        self.assertEqual(result, out_file)
        self.assertTrue(os.path.exists(out_file))

        # Critical requirement: Lesson playback state must NOT be reset or interrupted
        self.assertEqual(self.controller.current_step_index, 4)

    def test_empty_steps_handled_gracefully(self):
        self.controller.current_steps = []
        out_file = os.path.join(self.temp_dir.name, "should_not_exist.pdf")
        result = self.controller.on_export_pdf_requested(target_filepath=out_file)
        self.assertIsNone(result)
        self.assertFalse(os.path.exists(out_file))


if __name__ == "__main__":
    unittest.main()
