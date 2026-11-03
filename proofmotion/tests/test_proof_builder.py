"""
tests/test_proof_builder.py
---------------------------
Comprehensive unit and integration tests for Proof Builder:
  - Shape models, step models, and proof state models
  - Conversion to RenderData and runtime ProofStep
  - JSON serialization & round-tripping
  - All prebuilt proof templates
  - BuilderCanvas interactive tools & geometry handling
  - WorkspaceBuilder editor & Learn Presentation View
"""

import sys
import unittest
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWidgets import QApplication

from playground.proof_builder_model import (
    BuilderProof, BuilderProofStep, BuilderShape, ShapeType
)
from playground.proof_templates import (
    get_template_catalog,
    create_pythagorean_template,
    create_triangle_angle_sum_template,
    create_thales_template,
    create_exterior_angle_template,
    create_triangle_area_template,
    create_blank_template,
)
from core.step_model import RenderData
from models.theorem_state import ProofStep


class TestProofBuilderModel(unittest.TestCase):
    def test_shape_creation_and_copy(self):
        shape = BuilderShape(
            shape_type=ShapeType.POINT.value,
            name="A",
            color="#6C5CE7",
            coords=[1.0, 2.0, 4.5]
        )
        self.assertEqual(shape.name, "A")
        self.assertEqual(shape.coords, [1.0, 2.0, 4.5])

        copied = shape.copy()
        self.assertNotEqual(shape.id, copied.id)
        self.assertEqual(copied.name, "A")
        self.assertEqual(copied.coords, [1.0, 2.0, 4.5])

    def test_shape_serialization_roundtrip(self):
        shape = BuilderShape(
            shape_type=ShapeType.POLYGON.value,
            name="ΔABC",
            color="#5B8DEF",
            fill_color="rgba(91, 141, 239, 0.25)",
            stroke_width=2.5,
            polygon_points=[(0.0, 0.0), (3.0, 0.0), (0.0, 4.0)]
        )
        d = shape.to_dict()
        restored = BuilderShape.from_dict(d)
        self.assertEqual(restored.shape_type, ShapeType.POLYGON.value)
        self.assertEqual(restored.name, "ΔABC")
        self.assertEqual(len(restored.polygon_points), 3)
        self.assertEqual(restored.polygon_points[1], (3.0, 0.0))

    def test_step_to_render_data(self):
        step = BuilderProofStep(
            index=1,
            title="Right Triangle ΔABC",
            equation="a² + b² = c²",
            explanation="Goal: establish triangle.",
            shapes=[
                BuilderShape(shape_type=ShapeType.POINT.value, name="C", coords=[0.0, 0.0, 4.0]),
                BuilderShape(shape_type=ShapeType.LINE.value, name="Leg a", coords=[0.0, 0.0, 4.0, 0.0], stroke_width=2.0),
                BuilderShape(shape_type=ShapeType.POLYGON.value, name="Δ", polygon_points=[(0.0, 0.0), (4.0, 0.0), (0.0, 3.0)]),
                BuilderShape(shape_type=ShapeType.ANGLE.value, name="90°", is_right_angle=True, coords=[0.0, 0.0, 0.6, 0.0, 90.0]),
                BuilderShape(shape_type=ShapeType.CIRCLE.value, name="Circ", coords=[2.0, 2.0, 1.5]),
                BuilderShape(shape_type=ShapeType.TEXT.value, name="Note", text="Test Formula", coords=[1.0, 1.0]),
            ]
        )
        rd = step.to_render_data()
        self.assertIsInstance(rd, RenderData)
        self.assertEqual(len(rd.points), 1)
        self.assertEqual(len(rd.lines), 3)  # 1 base line + 2 right-angle indicator segments
        self.assertEqual(len(rd.polygons), 2)  # 1 triangle polygon + 1 circle fill polygon
        self.assertGreaterEqual(len(rd.texts), 1)

        # Check conversion to ProofStep
        ps = step.to_proof_step()
        self.assertIsInstance(ps, ProofStep)
        self.assertEqual(ps.index, 1)
        self.assertEqual(ps.equation, "a² + b² = c²")

    def test_proof_step_management(self):
        proof = BuilderProof(title="Pythagorean")
        s1 = proof.add_step()
        self.assertEqual(len(proof.steps), 1)
        self.assertEqual(s1.index, 1)

        s2 = proof.add_step()
        self.assertEqual(len(proof.steps), 2)
        self.assertEqual(s2.index, 2)

        dup = proof.duplicate_step(0)
        self.assertIsNotNone(dup)
        self.assertEqual(len(proof.steps), 3)
        self.assertEqual(proof.steps[0].index, 1)
        self.assertEqual(proof.steps[1].index, 2)
        self.assertEqual(proof.steps[2].index, 3)

        deleted = proof.delete_step(1)
        self.assertTrue(deleted)
        self.assertEqual(len(proof.steps), 2)
        self.assertEqual(proof.steps[0].index, 1)
        self.assertEqual(proof.steps[1].index, 2)

    def test_proof_json_roundtrip(self):
        tmpl = create_pythagorean_template()
        json_data = tmpl.to_json()
        restored = BuilderProof.from_json(json_data)
        self.assertEqual(restored.title, tmpl.title)
        self.assertEqual(len(restored.steps), len(tmpl.steps))
        for orig_step, rest_step in zip(tmpl.steps, restored.steps):
            self.assertEqual(orig_step.index, rest_step.index)
            self.assertEqual(orig_step.title, rest_step.title)
            self.assertEqual(len(orig_step.shapes), len(rest_step.shapes))


class TestProofTemplates(unittest.TestCase):
    def test_all_templates_exist_and_are_valid(self):
        catalogs = get_template_catalog()
        expected_keys = [
            "pythagorean", "triangle_angle_sum", "thales",
            "exterior_angle", "triangle_area", "blank"
        ]
        for key in expected_keys:
            self.assertIn(key, catalogs, f"Missing template {key}")
            proof = catalogs[key]
            self.assertIsInstance(proof, BuilderProof)
            self.assertTrue(bool(proof.title))
            self.assertGreaterEqual(len(proof.steps), 1)

            for step in proof.steps:
                self.assertGreaterEqual(step.index, 1)
                self.assertTrue(bool(step.title))
                rd = step.to_render_data()
                self.assertIsInstance(rd, RenderData)
                ps = step.to_proof_step()
                self.assertIsInstance(ps, ProofStep)

    def test_pythagorean_template_contents(self):
        proof = create_pythagorean_template()
        self.assertEqual(len(proof.steps), 4)
        self.assertIn("a² + b²", proof.steps[3].equation)
        self.assertIn("c²", proof.steps[3].equation)

    def test_triangle_angle_sum_template_contents(self):
        proof = create_triangle_angle_sum_template()
        self.assertEqual(len(proof.steps), 4)
        self.assertIn("180°", proof.steps[3].equation)


class TestProofBuilderUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_builder_canvas_tools_and_drawing(self):
        from playground.ui.builder_canvas import BuilderCanvas
        canvas = BuilderCanvas()
        step = BuilderProofStep(index=1, title="Test Step")
        canvas.set_step(step)

        canvas.set_tool("point")
        self.assertEqual(canvas.tool, "point")

        # Simulate adding a point
        pt = BuilderShape(shape_type=ShapeType.POINT.value, name="A", coords=[2.0, 3.0, 4.5])
        step.shapes.append(pt)
        canvas.update()

        # Hit test
        sx, sy = canvas.world_to_screen(2.0, 3.0)
        hit = canvas._hit_test_point(sx, sy)
        self.assertIsNotNone(hit)
        self.assertEqual(hit[0].name, "A")

        canvas.close()

    def test_workspace_builder_creation_and_mode_switching(self):
        from playground.ui.workspace_builder import WorkspaceBuilder
        ws = WorkspaceBuilder()
        ws.show()

        self.assertIsNotNone(ws.current_step())
        self.assertEqual(ws._mode_stack.currentIndex(), 0)

        # Switch to Learn Presentation View
        ws.switch_mode(True)
        self.assertEqual(ws._mode_stack.currentIndex(), 1)
        self.assertTrue(ws._is_presenting)

        # Presentation navigation
        ws._pres_step_next()
        self.assertEqual(ws._pres_step_idx, 1)

        ws._pres_step_prev()
        self.assertEqual(ws._pres_step_idx, 0)

        # Switch back to Design Mode
        ws.switch_mode(False)
        self.assertEqual(ws._mode_stack.currentIndex(), 0)
        self.assertFalse(ws._is_presenting)

        ws.close()

    def test_workspace_builder_template_loading(self):
        from playground.ui.workspace_builder import WorkspaceBuilder
        ws = WorkspaceBuilder()
        ws.show()

        ws._on_template_selected("thales")
        self.assertEqual(ws._proof.title, "Thales's Theorem")
        self.assertEqual(len(ws._proof.steps), 3)

        ws._on_template_selected("triangle_angle_sum")
        self.assertEqual(ws._proof.title, "Triangle Angle Sum Theorem")
        self.assertEqual(len(ws._proof.steps), 4)

        ws.close()

    def test_shape_translation_and_center(self):
        # Point
        pt = BuilderShape(shape_type=ShapeType.POINT.value, name="P", coords=[1.0, 2.0, 4.0])
        self.assertEqual(pt.center(), (1.0, 2.0))
        pt.translate(2.0, -1.0)
        self.assertEqual(pt.coords[:2], [3.0, 1.0])
        self.assertEqual(pt.center(), (3.0, 1.0))

        # Line
        line = BuilderShape(shape_type=ShapeType.LINE.value, coords=[0.0, 0.0, 4.0, 2.0])
        self.assertEqual(line.center(), (2.0, 1.0))
        line.translate(1.0, 1.0)
        self.assertEqual(line.coords, [1.0, 1.0, 5.0, 3.0])
        self.assertEqual(line.center(), (3.0, 2.0))

        # Polygon
        poly = BuilderShape(
            shape_type=ShapeType.POLYGON.value,
            polygon_points=[(0.0, 0.0), (3.0, 0.0), (0.0, 3.0)]
        )
        self.assertEqual(poly.center(), (1.0, 1.0))
        poly.translate(2.0, 3.0)
        self.assertEqual(poly.polygon_points, [(2.0, 3.0), (5.0, 3.0), (2.0, 6.0)])
        self.assertEqual(poly.center(), (3.0, 4.0))

        # Circle
        circ = BuilderShape(shape_type=ShapeType.CIRCLE.value, coords=[0.0, 0.0, 2.5])
        self.assertEqual(circ.center(), (0.0, 0.0))
        circ.translate(3.0, 4.0)
        self.assertEqual(circ.coords, [3.0, 4.0, 2.5])
        self.assertEqual(circ.center(), (3.0, 4.0))

    def test_canvas_shape_creation_and_auto_select(self):
        from playground.ui.builder_canvas import BuilderCanvas
        canvas = BuilderCanvas()
        step = BuilderProofStep(index=1, title="Test Step")
        canvas.set_step(step)

        # Set tool to triangle
        canvas.set_tool("triangle")
        self.assertEqual(canvas.tool, "triangle")

        emitted_tools = []
        canvas.toolChanged.connect(lambda t: emitted_tools.append(t))

        tri = BuilderShape(
            shape_type=ShapeType.POLYGON.value,
            name="Tri",
            polygon_points=[(0.0, 0.0), (2.0, 0.0), (1.0, 2.0)]
        )
        canvas._finish_shape_creation(tri)

        # Should auto-switch to "select" and select the shape
        self.assertEqual(canvas.tool, "select")
        self.assertIn("select", emitted_tools)
        self.assertEqual(canvas._selected_shape_id, tri.id)
        self.assertIsNotNone(canvas.selected_shape())
        self.assertEqual(canvas.selected_shape().name, "Tri")

        # Hit test anywhere inside body
        cx, cy = tri.center()
        sx, sy = canvas.world_to_screen(cx, cy)
        hit_shape = canvas._hit_test_any_shape(sx, sy)
        self.assertIsNotNone(hit_shape)
        self.assertEqual(hit_shape.id, tri.id)

        canvas.close()

    def test_workspace_builder_position_and_nudge_controls(self):
        from playground.ui.workspace_builder import WorkspaceBuilder
        ws = WorkspaceBuilder()
        ws.show()

        step = ws.current_step()
        self.assertIsNotNone(step)

        poly = BuilderShape(
            shape_type=ShapeType.POLYGON.value,
            name="TestPoly",
            polygon_points=[(2.0, 2.0), (4.0, 2.0), (3.0, 4.0)]
        )
        step.shapes.append(poly)
        ws._canvas.set_selected_shape_id(poly.id)
        ws._update_shape_inspector()

        # Nudge right by 1.0, up by 0.5
        ws._nudge_selected_shape(1.0, 0.5)
        self.assertEqual(poly.center(), (4.0, 3.167))

        # Center shape to (0, 0)
        ws._center_selected_shape()
        self.assertEqual(poly.center(), (0.0, 0.0))

        # Check tool sync signal
        ws._canvas.set_tool("line")
        ws._on_canvas_tool_changed("select")
        self.assertTrue(ws._tool_buttons["select"].isChecked())

        ws.close()

    def test_smart_two_point_angle_creation(self):
        from playground.ui.builder_canvas import BuilderCanvas
        canvas = BuilderCanvas()
        step = BuilderProofStep(index=1, title="Angle Test")
        canvas.set_step(step)

        # Add a right triangle with vertices (0,0), (4,0), (0,3)
        tri = BuilderShape(
            shape_type=ShapeType.POLYGON.value,
            name="RightTriangle",
            polygon_points=[(0.0, 0.0), (4.0, 0.0), (0.0, 3.0)]
        )
        step.shapes.append(tri)

        # Test Case 1: Click at corner (0, 0), and second click inside (1, 1)
        ang1 = canvas._create_angle_from_two_points((0.0, 0.0), (1.0, 1.0))
        self.assertEqual(ang1.shape_type, ShapeType.ANGLE.value)
        self.assertEqual(ang1.coords[0], 0.0)
        self.assertEqual(ang1.coords[1], 0.0)
        self.assertEqual(ang1.coords[4], 90.0)  # Exactly 90 degrees
        self.assertTrue(ang1.is_right_angle)
        self.assertEqual(ang1.name, "90°")

        # Test Case 2: Click two points inside the triangle near corner (0, 3)
        ang2 = canvas._create_angle_from_two_points((0.2, 2.5), (1.0, 1.0))
        self.assertEqual(ang2.shape_type, ShapeType.ANGLE.value)
        self.assertEqual(ang2.coords[0], 0.0)
        self.assertEqual(ang2.coords[1], 3.0)
        self.assertAlmostEqual(ang2.coords[4], 53.13, delta=1.5)

        # Test Case 3: Right angle tool on corner
        ang3 = canvas._create_angle_from_two_points((0.0, 0.0), (2.0, 0.0), is_right=True)
        self.assertTrue(ang3.is_right_angle)
        self.assertEqual(ang3.name, "90°")

        # Test Case 4: Freeform two points outside any polygon
        ang4 = canvas._create_angle_from_two_points((10.0, 10.0), (12.0, 10.0))
        self.assertEqual(ang4.coords[0], 10.0)
        self.assertEqual(ang4.coords[1], 10.0)
        self.assertEqual(ang4.coords[4], 60.0)

        # Test Case 5: Triangle edge and a passing line that crosses it
        line_cross = BuilderShape(
            shape_type=ShapeType.LINE.value,
            coords=[2.0, -2.0, 2.0, 4.0]
        )
        step.shapes.append(line_cross)
        # Click on triangle edge at (1.0, 0.0) and on crossing line at (2.0, 2.0)
        ang5 = canvas._create_angle_from_two_points((1.0, 0.0), (2.0, 2.0))
        self.assertEqual(ang5.coords[0], 2.0)  # Intersection X
        self.assertEqual(ang5.coords[1], 0.0)  # Intersection Y
        self.assertEqual(ang5.coords[4], 90.0) # Exactly 90° between horizontal base and vertical line
        self.assertTrue(ang5.is_right_angle)

        # Test Case 6: Triangle edge and exterior ray extending from vertex (Exterior Angle)
        line_ext = BuilderShape(
            shape_type=ShapeType.LINE.value,
            coords=[4.0, 0.0, 8.0, 0.0]
        )
        step.shapes.append(line_ext)
        # Click on hypotenuse and on exterior ray
        ang6 = canvas._create_angle_from_two_points((2.0, 1.5), (6.0, 0.0))
        self.assertEqual(ang6.coords[0], 4.0)  # Vertex C
        self.assertEqual(ang6.coords[1], 0.0)
        self.assertAlmostEqual(ang6.coords[4], 143.13, delta=2.0)

        # Test Case 7: Two standalone intersecting lines
        step.shapes.clear()
        line_a = BuilderShape(shape_type=ShapeType.LINE.value, coords=[0.0, 0.0, 4.0, 4.0])
        line_b = BuilderShape(shape_type=ShapeType.LINE.value, coords=[0.0, 4.0, 4.0, 0.0])
        step.shapes.extend([line_a, line_b])
        ang7 = canvas._create_angle_from_two_points((1.0, 1.0), (1.0, 3.0))
        self.assertEqual(ang7.coords[0], 2.0)
        self.assertEqual(ang7.coords[1], 2.0)
        self.assertEqual(ang7.coords[4], 90.0)

        canvas.close()

    def test_copy_previous_step_in_workspace(self):
        """Verifies 'Copy Prev' copies all shapes, updates canvas binding, and refreshes shapes list."""
        app = QApplication.instance() or QApplication(sys.argv)
        from playground.ui.workspace_builder import WorkspaceBuilder
        workspace = WorkspaceBuilder()
        proof = BuilderProof(title="Copy Test")
        s1 = proof.add_step()
        s1.shapes.append(BuilderShape(shape_type=ShapeType.POINT.value, name="A", coords=[1.0, 2.0]))
        s1.shapes.append(BuilderShape(shape_type=ShapeType.LINE.value, name="Edge", coords=[0.0, 0.0, 3.0, 4.0]))
        s2 = proof.add_step()  # Step 2 is empty

        workspace._load_proof_into_editor(proof)
        workspace.select_step(1)  # Active is Step 2
        self.assertEqual(len(workspace.current_step().shapes), 0)

        # Trigger Copy Prev
        workspace._on_copy_from_previous_step()
        curr_step = workspace.current_step()
        self.assertEqual(len(curr_step.shapes), 2)
        self.assertEqual(curr_step.shapes[0].name, "A")
        self.assertEqual(curr_step.shapes[1].name, "Edge")
        # Ensure new unique IDs
        self.assertNotEqual(curr_step.shapes[0].id, s1.shapes[0].id)
        # Ensure canvas is bound to curr_step
        self.assertEqual(workspace._canvas.get_step(), curr_step)
        workspace.close()

    def test_snap_to_grid_behavior(self):
        """Verifies Snap Grid toggle strictly controls coordinate snapping."""
        app = QApplication.instance() or QApplication(sys.argv)
        from playground.ui.builder_canvas import BuilderCanvas
        canvas = BuilderCanvas()
        canvas.grid_size = 0.5

        # With Snap ON
        canvas.set_snap_to_grid(True)
        self.assertTrue(canvas.snap_to_grid)
        sx, sy = canvas._snap(1.23, 1.77)
        self.assertEqual(sx, 1.0)
        self.assertEqual(sy, 2.0)

        sx2, sy2 = canvas._snap(0.24, 0.74)
        self.assertEqual(sx2, 0.0)
        self.assertEqual(sy2, 0.5)

        # With Snap OFF (continuous)
        canvas.set_snap_to_grid(False)
        self.assertFalse(canvas.snap_to_grid)
        fx, fy = canvas._snap(1.234, 1.776)
        self.assertEqual(fx, 1.234)
        self.assertEqual(fy, 1.776)
        canvas.close()

    def test_editable_text_shape(self):
        """Verifies text shapes are fully editable via inspector and canvas double-click."""
        app = QApplication.instance() or QApplication(sys.argv)
        from playground.ui.workspace_builder import WorkspaceBuilder
        workspace = WorkspaceBuilder()
        proof = BuilderProof(title="Text Test")
        step = proof.add_step()
        text_shape = BuilderShape(
            shape_type=ShapeType.TEXT.value,
            name="Formula",
            text="a² + b² = c²",
            coords=[0.0, 0.0],
            font_size=12,
            bold=True
        )
        step.shapes.append(text_shape)
        workspace._load_proof_into_editor(proof)

        # Select text shape
        workspace._canvas.set_selected_shape_id(text_shape.id)
        workspace._update_shape_inspector()
        self.assertFalse(workspace._text_group.isHidden())
        self.assertEqual(workspace._shape_text_edit.text(), "a² + b² = c²")

        # Edit text content
        workspace._shape_text_edit.setText("E = mc²")
        self.assertEqual(text_shape.text, "E = mc²")
        self.assertEqual(text_shape.name, "E = mc²")

        # Edit font size and bold
        workspace._text_font_size_spin.setValue(18)
        workspace._text_bold_check.setChecked(False)
        self.assertEqual(text_shape.font_size, 18)
        self.assertFalse(text_shape.bold)

        # Verify to_render_data preserves text
        rd = step.to_render_data()
        self.assertEqual(len(rd.texts), 1)
        self.assertEqual(rd.texts[0].text, "E = mc²")
        self.assertEqual(rd.texts[0].font_size, 18)
        workspace.close()

    def test_curve_shape_features(self):
        """Verifies Curve creation, translation, center calculation, and RenderData generation."""
        curve = BuilderShape(
            shape_type=ShapeType.CURVE.value,
            name="Smooth Arc",
            coords=[0.0, 0.0, 2.0, 4.0, 4.0, 0.0],
            stroke_width=2.5
        )
        self.assertEqual(curve.center(), (2.0, 1.333))

        # Translation
        curve.translate(1.0, 2.0)
        self.assertEqual(curve.coords, [1.0, 2.0, 3.0, 6.0, 5.0, 2.0])
        self.assertEqual(curve.center(), (3.0, 3.333))

        # RenderData conversion
        step = BuilderProofStep(index=1, shapes=[curve])
        rd = step.to_render_data()
        self.assertEqual(len(rd.lines), 24)  # 24 sampled segments for Bézier curve
        self.assertEqual(rd.lines[0].color, curve.color)

    def test_divided_shape_portion_selection(self):
        """Verifies automatic detection and isolation of portions in shapes divided by lines."""
        app = QApplication.instance() or QApplication(sys.argv)
        from playground.ui.builder_canvas import BuilderCanvas
        canvas = BuilderCanvas()
        step = BuilderProofStep(index=1)
        canvas.set_step(step)

        # 1. Circle divided by horizontal and vertical diameter lines (4 quadrants)
        circle = BuilderShape(shape_type=ShapeType.CIRCLE.value, coords=[0.0, 0.0, 2.0])
        line_h = BuilderShape(shape_type=ShapeType.LINE.value, coords=[-3.0, 0.0, 3.0, 0.0])
        line_v = BuilderShape(shape_type=ShapeType.LINE.value, coords=[0.0, -3.0, 0.0, 3.0])
        step.shapes.extend([circle, line_h, line_v])

        # Click inside Quadrant 1 (x=1.0, y=1.0 -> 45°)
        portion1 = canvas._detect_shape_portion(1.0, 1.0)
        self.assertIsNotNone(portion1)
        self.assertEqual(portion1.shape_type, ShapeType.SECTOR.value)
        self.assertEqual(portion1.coords[0], 0.0)  # Center cx
        self.assertEqual(portion1.coords[1], 0.0)  # Center cy
        self.assertEqual(portion1.coords[2], 2.0)  # Radius r
        self.assertEqual(portion1.coords[3], 0.0)  # Start angle 0°
        self.assertEqual(portion1.coords[4], 90.0) # Span 90°
        self.assertEqual(portion1.name, "Quadrant (90°)")

        # Verify portion can be translated independently
        portion1.translate(2.0, 2.0)
        self.assertEqual(portion1.coords[0], 2.0)
        self.assertEqual(portion1.coords[1], 2.0)

        # 2. Rectangle divided by diagonal line (creates 2 triangles)
        step.shapes.clear()
        rect = BuilderShape(
            shape_type=ShapeType.POLYGON.value,
            name="Rect",
            polygon_points=[(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)]
        )
        diagonal = BuilderShape(shape_type=ShapeType.LINE.value, coords=[0.0, 0.0, 4.0, 4.0])
        step.shapes.extend([rect, diagonal])

        # Click inside lower triangle (3.0, 1.0)
        portion2 = canvas._detect_shape_portion(3.0, 1.0)
        self.assertIsNotNone(portion2)
        self.assertEqual(portion2.shape_type, ShapeType.POLYGON.value)
        self.assertEqual(len(portion2.polygon_points), 3)

        canvas.close()

    def test_copy_previous_option_removed_from_ui(self):
        """Verifies 'Copy Prev' button is removed from the Proof Builder UI."""
        app = QApplication.instance() or QApplication(sys.argv)
        from playground.ui.workspace_builder import WorkspaceBuilder
        from PyQt5.QtWidgets import QPushButton
        workspace = WorkspaceBuilder()
        buttons = workspace.findChildren(QPushButton)
        copy_prev_buttons = [btn for btn in buttons if "Copy Prev" in btn.text()]
        self.assertEqual(len(copy_prev_buttons), 0)
        workspace.close()

    def test_canvas_free_panning_and_zooming(self):
        """Verifies canvas smooth panning in all directions, zoom levels, fit to content, and signals."""
        app = QApplication.instance() or QApplication(sys.argv)
        from playground.ui.builder_canvas import BuilderCanvas
        canvas = BuilderCanvas()
        canvas.resize(800, 600)

        # Initial pan and zoom
        self.assertEqual(canvas._pan, [0.0, 0.0])
        self.assertEqual(canvas._zoom, 1.0)

        # Pan freely left, right, up, down
        canvas.pan_by(50.0, -30.0)
        self.assertEqual(canvas._pan, [50.0, -30.0])
        canvas.pan_by(-20.0, 40.0)
        self.assertEqual(canvas._pan, [30.0, 10.0])

        # Zoom in and out with signal emission
        zoom_values = []
        canvas.zoomChanged.connect(lambda z: zoom_values.append(z))
        canvas.zoom_by(1.2)
        self.assertAlmostEqual(canvas._zoom, 1.2, places=4)
        self.assertTrue(len(zoom_values) > 0)

        # Zoom at specific screen point (mouse cursor position)
        canvas.zoom_at(1.5, QPoint(400, 300))
        self.assertAlmostEqual(canvas._zoom, 1.8, places=4)

        # Reset view
        canvas.reset_view()
        self.assertEqual(canvas._pan, [0.0, 0.0])
        self.assertEqual(canvas._zoom, 1.0)

        # Fit to content
        step = BuilderProofStep(index=1)
        step.shapes.append(BuilderShape(shape_type=ShapeType.POINT.value, coords=[-10.0, -10.0]))
        step.shapes.append(BuilderShape(shape_type=ShapeType.POINT.value, coords=[10.0, 10.0]))
        canvas.set_step(step)
        canvas.fit_to_content()
        self.assertTrue(canvas._zoom > 0.0)

        # Pan tool switching
        canvas.set_tool("pan")
        self.assertEqual(canvas.tool, "pan")
        self.assertEqual(canvas.cursor().shape(), Qt.OpenHandCursor)

        canvas.close()


if __name__ == "__main__":
    unittest.main()
