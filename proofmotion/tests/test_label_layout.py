"""
tests/test_label_layout.py
--------------------------
Unit and canvas tests for collision-aware label placement.
"""

import unittest
import sys

from graphics.label_layout import (
    LabelPlacer, LabelSpec, rects_intersect, inflate_rect,
    outward_from_centroid, leader_needed,
)


class TestLabelPlacer(unittest.TestCase):
    def test_labels_do_not_overlap_each_other(self):
        placer = LabelPlacer(viewport=(0, 0, 400, 300), margin=8, gap=12)
        cluster = [(200.0, 150.0), (208.0, 148.0), (196.0, 158.0)]
        for p in cluster:
            placer.add_point(p, radius=5)
        placed = []
        for i, p in enumerate(cluster):
            placed.append(placer.place(LabelSpec(
                text=f"A{i}(1.0, 2.0)",
                anchor=p,
                width=78,
                height=20,
                kind="point",
                outward=outward_from_centroid(p, (201.0, 152.0)),
            )))
        for i, a in enumerate(placed):
            for b in placed[i + 1:]:
                self.assertFalse(
                    rects_intersect(a.rect, b.rect, gap=1.0),
                    f"{a.text} overlaps {b.text}",
                )

    def test_polygon_title_avoids_shape(self):
        triangle = [(120.0, 180.0), (220.0, 180.0), (170.0, 90.0)]
        placer = LabelPlacer(viewport=(0, 0, 400, 300), margin=8, gap=14)
        placer.add_polygon(triangle)
        placed = placer.place(LabelSpec(
            text="Triangle ΔABC",
            anchor=(170.0, 90.0),
            width=130,
            height=24,
            kind="polygon",
            outward=(0.0, -1.0),
            priority=20,
        ))
        from graphics.label_layout import rect_hits_poly
        self.assertFalse(rect_hits_poly(placed.rect, triangle))

    def test_stays_inside_viewport(self):
        placer = LabelPlacer(viewport=(0, 0, 200, 160), margin=6, gap=10)
        placer.add_point((8.0, 8.0), radius=4)
        placed = placer.place(LabelSpec(
            text="A(-12.5, 18.0)",
            anchor=(8.0, 8.0),
            width=110,
            height=20,
            kind="point",
            outward=(-1.0, -1.0),
        ))
        x, y, w, h = placed.rect
        self.assertGreaterEqual(x, 6.0)
        self.assertGreaterEqual(y, 6.0)
        self.assertLessEqual(x + w, 194.0)
        self.assertLessEqual(y + h, 154.0)

    def test_leader_when_far(self):
        self.assertTrue(leader_needed((10.0, 10.0), (80.0, 10.0, 40.0, 16.0)))
        self.assertFalse(leader_needed((10.0, 10.0), (14.0, 4.0, 40.0, 16.0)))

    def test_inflate_keeps_separation(self):
        a = inflate_rect((10, 10, 20, 10), 3)
        self.assertEqual(a, (7, 7, 26, 16))


class TestGeometryCanvasLabels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PyQt5.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def _paint(self, widget, w=820, h=560):
        from PyQt5.QtGui import QImage, QPainter
        widget.resize(w, h)
        widget._anim_progress = 1.0
        image = QImage(w, h, QImage.Format_ARGB32)
        painter = QPainter(image)
        widget.render(painter)
        painter.end()
        return getattr(widget, "_last_placed_labels", [])

    def _assert_no_overlap(self, labels):
        for i, a in enumerate(labels):
            for b in labels[i + 1:]:
                self.assertFalse(
                    rects_intersect(a.rect, b.rect, gap=0.5),
                    f"Overlap: '{a.text}' vs '{b.text}'",
                )

    def test_default_2d_translation_labels(self):
        from graphics.visualization_widget import VisualizationWidget
        import cgip.transformations as trans
        widget = VisualizationWidget()
        steps = trans.generate_transformation_demo(
            "triangle", [{"type": "translate", "dx": 3.0, "dy": 2.0}]
        )
        for step in steps:
            widget.update_step(step.index, step.values, render_data=step.render_data)
            labels = self._paint(widget)
            self.assertGreater(len(labels), 0)
            self._assert_no_overlap(labels)

    def test_extreme_scale_and_rotation(self):
        from graphics.visualization_widget import VisualizationWidget
        import cgip.transformations as trans
        widget = VisualizationWidget()
        steps = trans.generate_transformation_demo("triangle", [
            {"type": "scale", "sx": 4.0, "sy": 0.3},
            {"type": "rotate", "angle": 135.0},
        ])
        widget.update_step(steps[-1].index, steps[-1].values, render_data=steps[-1].render_data)
        labels = self._paint(widget, 640, 420)
        self._assert_no_overlap(labels)

    def test_theorem_pythagorean_labels(self):
        from graphics.visualization_widget import VisualizationWidget
        from theorems.pythagorean import generate_proof_steps
        widget = VisualizationWidget()
        steps = generate_proof_steps({"side_a": 3.0, "side_b": 4.0})
        widget.update_step(steps[0].index, steps[0].values, render_data=steps[0].render_data)
        labels = self._paint(widget)
        self._assert_no_overlap(labels)

    def test_fullscreen_size(self):
        from graphics.visualization_widget import VisualizationWidget
        import cgip.transformations as trans
        widget = VisualizationWidget()
        steps = trans.generate_transformation_demo(
            "rectangle", [{"type": "reflect", "axis": "X-axis"}]
        )
        widget.update_step(steps[-1].index, steps[-1].values, render_data=steps[-1].render_data)
        labels = self._paint(widget, 1280, 800)
        self._assert_no_overlap(labels)

    def test_all_2d_transform_topics(self):
        from graphics.visualization_widget import VisualizationWidget
        import cgip.transformations as trans
        widget = VisualizationWidget()
        cases = [
            trans.generate_transformation_demo("triangle", [{"type": "translate", "dx": 8.0, "dy": -4.0}]),
            trans.generate_transformation_demo("rectangle", [{"type": "scale", "sx": 0.4, "sy": 3.2}]),
            trans.generate_transformation_demo("triangle", [{"type": "rotate", "angle": 270.0, "cx": 2.5, "cy": 2.0}]),
            trans.generate_transformation_demo("triangle", [
                {"type": "scale", "sx": 1.3, "sy": 1.3},
                {"type": "rotate", "angle": 30.0},
                {"type": "translate", "dx": 3.0, "dy": 2.0},
            ]),
        ]
        for steps in cases:
            for step in (steps[0], steps[-1]):
                widget.update_step(step.index, step.values, render_data=step.render_data)
                self._assert_no_overlap(self._paint(widget, 900, 600))

    def test_clipping_endpoint_labels(self):
        from graphics.visualization_widget import VisualizationWidget
        import cgip.clipping as clip
        widget = VisualizationWidget()
        steps = clip.cohen_sutherland_trace(-6, 5, 5, -2, -3, -2, 3, 2)
        widget.update_step(steps[-1].index, steps[-1].values, render_data=steps[-1].render_data)
        self._paint(widget)
        placed = getattr(widget._label_placer, "placed", [])
        texts = [p.text for p in placed]
        self.assertTrue(any(t.startswith("P1") for t in texts))
        self.assertTrue(any(t.startswith("P2") for t in texts))
        self._assert_no_overlap(placed)


if __name__ == "__main__":
    unittest.main()
