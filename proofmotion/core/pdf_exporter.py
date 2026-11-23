"""
core/pdf_exporter.py
---------------------
Robust, modular PDF exporter for ProofMotion lessons.
Generates structured educational study notes containing:
1. ProofMotion branding & topic header (category, title, export date, step count).
2. Actual input parameters used during the lesson.
3. Complete step-by-step sequence in original order:
   - Step index & title
   - Mathematical formula / equation / pseudocode
   - Narrative explanation of why the state changed
   - Relevant step metrics and active values
   - High-resolution offscreen visualization snapshot (where supported)
4. Final result summary & time/space complexity analysis.

Compatible with Python 3.9+ and PyQt5 offscreen rendering.
"""

import os
import io
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
    KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt, QBuffer, QIODevice

from core.step_model import VisualizationStep
from graphics.visualization_widget import VisualizationWidget


# Algorithmic Complexity Catalog
COMPLEXITY_CATALOG = {
    "bubble_sort": {"time_best": "O(n)", "time_avg": "O(n²)", "time_worst": "O(n²)", "space": "O(1)"},
    "selection_sort": {"time_best": "O(n²)", "time_avg": "O(n²)", "time_worst": "O(n²)", "space": "O(1)"},
    "insertion_sort": {"time_best": "O(n)", "time_avg": "O(n²)", "time_worst": "O(n²)", "space": "O(1)"},
    "merge_sort": {"time_best": "O(n log n)", "time_avg": "O(n log n)", "time_worst": "O(n log n)", "space": "O(n)"},
    "quick_sort": {"time_best": "O(n log n)", "time_avg": "O(n log n)", "time_worst": "O(n²)", "space": "O(log n)"},
    "linear_search": {"time_best": "O(1)", "time_avg": "O(n)", "time_worst": "O(n)", "space": "O(1)"},
    "binary_search": {"time_best": "O(1)", "time_avg": "O(log n)", "time_worst": "O(log n)", "space": "O(1)"},
    "bfs": {"time_best": "O(V + E)", "time_avg": "O(V + E)", "time_worst": "O(V + E)", "space": "O(V)"},
    "dfs": {"time_best": "O(V + E)", "time_avg": "O(V + E)", "time_worst": "O(V + E)", "space": "O(V)"},
    "dijkstra": {"time_best": "O((V + E) log V)", "time_avg": "O((V + E) log V)", "time_worst": "O((V + E) log V)", "space": "O(V)"},
    "prim_mst": {"time_best": "O(E log V)", "time_avg": "O(E log V)", "time_worst": "O(E log V)", "space": "O(V)"},
    "kruskal_mst": {"time_best": "O(E log E)", "time_avg": "O(E log E)", "time_worst": "O(E log E)", "space": "O(V)"},
    "topological_sort": {"time_best": "O(V + E)", "time_avg": "O(V + E)", "time_worst": "O(V + E)", "space": "O(V)"},
    "bst_search": {"time_best": "O(1)", "time_avg": "O(log n)", "time_worst": "O(n)", "space": "O(h)"},
    "bst_insert": {"time_best": "O(1)", "time_avg": "O(log n)", "time_worst": "O(n)", "space": "O(h)"},
    "bst_delete": {"time_best": "O(1)", "time_avg": "O(log n)", "time_worst": "O(n)", "space": "O(h)"},
    "tree_inorder": {"time_best": "O(n)", "time_avg": "O(n)", "time_worst": "O(n)", "space": "O(h)"},
    "tree_preorder": {"time_best": "O(n)", "time_avg": "O(n)", "time_worst": "O(n)", "space": "O(h)"},
    "tree_postorder": {"time_best": "O(n)", "time_avg": "O(n)", "time_worst": "O(n)", "space": "O(h)"},
    "tree_levelorder": {"time_best": "O(n)", "time_avg": "O(n)", "time_worst": "O(n)", "space": "O(w)"},
    "clip_cohen_sutherland": {"time_best": "O(1)", "time_avg": "O(1)", "time_worst": "O(1)", "space": "O(1)"},
    "clip_sutherland_hodgman": {"time_best": "O(N × M)", "time_avg": "O(N × M)", "time_worst": "O(N × M)", "space": "O(N)"},
    "rast_dda_line": {"time_best": "O(max(Δx, Δy))", "time_avg": "O(max(Δx, Δy))", "time_worst": "O(max(Δx, Δy))", "space": "O(1)"},
    "rast_bresenham_line": {"time_best": "O(max(Δx, Δy))", "time_avg": "O(max(Δx, Δy))", "time_worst": "O(max(Δx, Δy))", "space": "O(1)"},
    "rast_bresenham_circle": {"time_best": "O(r)", "time_avg": "O(r)", "time_worst": "O(r)", "space": "O(1)"},
    "rast_midpoint_circle": {"time_best": "O(r)", "time_avg": "O(r)", "time_worst": "O(r)", "space": "O(1)"},
    "trans_translation": {"time_best": "O(N)", "time_avg": "O(N)", "time_worst": "O(N)", "space": "O(1)"},
    "trans_rotation": {"time_best": "O(N)", "time_avg": "O(N)", "time_worst": "O(N)", "space": "O(1)"},
    "trans_scaling": {"time_best": "O(N)", "time_avg": "O(N)", "time_worst": "O(N)", "space": "O(1)"},
    "trans_reflection": {"time_best": "O(N)", "time_avg": "O(N)", "time_worst": "O(N)", "space": "O(1)"},
    "trans_shear": {"time_best": "O(N)", "time_avg": "O(N)", "time_worst": "O(N)", "space": "O(1)"},
}


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute total pages and render clean,
    professional running headers and footers with ProofMotion branding.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.doc_title = "ProofMotion Study Notes"

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def _draw_page_decorations(self, total_pages: int):
        self.saveState()
        page_w = self._pagesize[0]
        page_h = self._pagesize[1]
        margin = 36

        # Top Header (Only on pages 2+)
        if self._pageNumber > 1:
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(margin, page_h - 26, f"ProofMotion  •  {self.doc_title}")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(margin, page_h - 30, page_w - margin, page_h - 30)

        # Bottom Footer (All pages)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(margin, 34, page_w - margin, 34)

        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#6C5CE7"))
        self.drawString(margin, 22, "ProofMotion")

        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(margin + 58, 22, "—  From Theory to Motion  •  Interactive Computer Science Reference")
        self.drawRightString(page_w - margin, 22, f"Page {self._pageNumber} of {total_pages}")

        self.restoreState()


def escape_pdf_text(text: str) -> str:
    """Escapes special XML characters so ReportLab Paragraphs render safely."""
    if not text:
        return ""
    # Clean latex math subscripts and slashes
    t = str(text)
    t = re.sub(r'_\{([^}]+)\}', r'[\1]', t)
    t = re.sub(r'\\([a-zA-Z]+)', r'\1', t)
    # XML escaping
    t = t.replace("&", "&amp;")
    t = t.replace("<", "&lt;")
    t = t.replace(">", "&gt;")
    # Convert newlines to breaks
    t = t.replace("\n", "<br/>")
    return t


class PDFExporter:
    """
    Orchestrates lesson data compilation and ReportLab document generation.
    """

    def __init__(self):
        self._viz_widget: Optional[VisualizationWidget] = None

    def _get_viz_widget(self) -> VisualizationWidget:
        if self._viz_widget is None:
            self._viz_widget = VisualizationWidget()
            self._viz_widget.resize(540, 200)
        return self._viz_widget

    def capture_step_snapshot(self, topic_key: str, display_name: str, step_index: int, step: VisualizationStep) -> Optional[bytes]:
        """
        Renders a single step using the offscreen VisualizationWidget and returns PNG bytes.
        Returns None gracefully if rendering is unsupported.
        """
        try:
            widget = self._get_viz_widget()
            widget.set_theorem(topic_key, display_name)
            widget.update_step(step_index, step.values, step.render_data)

            pixmap = QPixmap(540, 200)
            pixmap.fill(Qt.white)

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            widget.render(painter)
            painter.end()

            buffer = QBuffer()
            buffer.open(QIODevice.WriteOnly)
            pixmap.save(buffer, "PNG")
            img_bytes = bytes(buffer.data())
            buffer.close()

            if len(img_bytes) > 200:
                return img_bytes
        except Exception:
            pass
        return None

    def export_lesson(
        self,
        topic_key: str,
        display_name: str,
        category: str,
        parameters: Dict[str, Any],
        steps: List[VisualizationStep],
        output_path: str,
        final_result_text: str = ""
    ) -> str:
        """
        Compiles the complete lesson sequence into a PDF document at output_path.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=38,
            bottomMargin=44
        )

        # Style definitions
        base_styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "DocTitle",
            parent=base_styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0F172A"),
            spaceAfter=4
        )

        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=base_styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#475569"),
            spaceAfter=12
        )

        sec_heading_style = ParagraphStyle(
            "SectionHeading",
            parent=base_styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=14,
            spaceAfter=8
        )

        step_title_style = ParagraphStyle(
            "StepTitle",
            parent=base_styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=15,
            textColor=colors.HexColor("#0F172A")
        )

        step_badge_style = ParagraphStyle(
            "StepBadge",
            parent=base_styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            textColor=colors.HexColor("#6C5CE7")
        )

        body_style = ParagraphStyle(
            "BodyText",
            parent=base_styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14.5,
            textColor=colors.HexColor("#334155")
        )

        equation_style = ParagraphStyle(
            "EquationBox",
            parent=base_styles["Normal"],
            fontName="Courier-Bold",
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#4338CA")
        )

        meta_label_style = ParagraphStyle(
            "MetaLabel",
            parent=base_styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#64748B")
        )

        meta_val_style = ParagraphStyle(
            "MetaVal",
            parent=base_styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#0F172A")
        )

        story = []

        # -------------------------------------------------------------
        # 1. Header Banner
        # -------------------------------------------------------------
        cat_display = category.replace("_", " ").upper()
        cat_para = Paragraph(
            f"<font color='#6C5CE7'><b>{escape_pdf_text(cat_display)}</b></font>  •  PROOFMOTION STUDY NOTES",
            ParagraphStyle("CatHeader", fontName="Helvetica-Bold", fontSize=9, leading=11)
        )
        story.append(cat_para)
        story.append(Spacer(1, 4))

        story.append(Paragraph(escape_pdf_text(display_name), title_style))
        export_date = datetime.now().strftime("%B %d, %Y")
        story.append(Paragraph(
            f"Exported on {export_date}  |  Total Generated Steps: {len(steps)}",
            subtitle_style
        ))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=14))

        # -------------------------------------------------------------
        # 2. Input Parameters Section
        # -------------------------------------------------------------
        if parameters:
            story.append(Paragraph("Input Parameters", sec_heading_style))
            param_rows = []
            for k, v in parameters.items():
                clean_k = k.replace("_", " ").title()
                clean_v = str(v)
                param_rows.append([
                    Paragraph(f"<b>{escape_pdf_text(clean_k)}</b>", meta_label_style),
                    Paragraph(escape_pdf_text(clean_v), meta_val_style)
                ])

            if param_rows:
                param_table = Table(param_rows, colWidths=[160, 380])
                param_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F5F9")),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ]))
                story.append(param_table)
                story.append(Spacer(1, 14))

        # -------------------------------------------------------------
        # 3. Step-by-Step Sequence
        # -------------------------------------------------------------
        story.append(Paragraph("Step-by-Step Lesson Sequence", sec_heading_style))
        story.append(Spacer(1, 4))

        for idx, step in enumerate(steps):
            step_idx_1based = getattr(step, "index", idx + 1)
            title = getattr(step, "title", f"Step {step_idx_1based}")
            eq = getattr(step, "equation", "")
            expl = getattr(step, "explanation", "")
            metrics = getattr(step, "metrics", {}) or {}

            step_elements = []

            # Step Header Strip
            header_table = Table([
                [
                    Paragraph(f"STEP {step_idx_1based} OF {len(steps)}", step_badge_style),
                    Paragraph(escape_pdf_text(title), step_title_style)
                ]
            ], colWidths=[100, 440])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            step_elements.append(header_table)

            # Equation / Formula (if present)
            if eq and eq.strip():
                eq_clean = escape_pdf_text(eq.strip())
                eq_table = Table([[Paragraph(eq_clean, equation_style)]], colWidths=[540])
                eq_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F5F3FF")),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#DDD6FE")),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ]))
                step_elements.append(eq_table)

            # Step Explanation Narrative
            if expl and expl.strip():
                expl_clean = escape_pdf_text(expl.strip())
                expl_table = Table([[Paragraph(expl_clean, body_style)]], colWidths=[540])
                expl_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                step_elements.append(expl_table)

            # Step Metrics Row (if present)
            if metrics:
                metric_strs = []
                for mk, mv in metrics.items():
                    if isinstance(mv, (int, float, str, bool)):
                        metric_strs.append(f"<b>{escape_pdf_text(mk.replace('_', ' '))}:</b> {escape_pdf_text(str(mv))}")
                if metric_strs:
                    metric_html = "  &nbsp;&nbsp;•&nbsp;&nbsp; ".join(metric_strs)
                    m_table = Table([[Paragraph(metric_html, meta_val_style)]], colWidths=[540])
                    m_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                        ('LEFTPADDING', (0, 0), (-1, -1), 8),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ]))
                    step_elements.append(m_table)

            # Visualization Snapshot (clean image offscreen rendering)
            snapshot_bytes = self.capture_step_snapshot(topic_key, display_name, idx, step)
            if snapshot_bytes:
                img_io = io.BytesIO(snapshot_bytes)
                img_flowable = Image(img_io, width=540, height=180)
                step_elements.append(Spacer(1, 4))
                step_elements.append(img_flowable)

            step_elements.append(Spacer(1, 14))
            # Try to keep step header and its immediate content together
            story.append(KeepTogether(step_elements[:3]))
            for rem in step_elements[3:]:
                story.append(rem)

        # -------------------------------------------------------------
        # 4. Final Result & Complexity Summary
        # -------------------------------------------------------------
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=14))
        story.append(Paragraph("Final Result & Complexity Analysis", sec_heading_style))

        # Result Summary
        final_text = final_result_text
        if not final_text and steps:
            last_step = steps[-1]
            last_eq = getattr(last_step, "equation", "")
            last_expl = getattr(last_step, "explanation", "")
            last_vals = getattr(last_step, "values", {})
            if "sorted_array" in last_vals:
                final_text = f"Sorted Array: {last_vals['sorted_array']}"
            elif "current_array" in last_vals:
                final_text = f"Final Array: {last_vals['current_array']}"
            elif last_eq:
                final_text = last_eq
            elif last_expl:
                final_text = last_expl

        if final_text:
            res_table = Table([
                [
                    Paragraph("<b>Final Lesson Output:</b>", meta_label_style),
                    Paragraph(escape_pdf_text(final_text), body_style)
                ]
            ], colWidths=[140, 400])
            res_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F0FDF4")),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#BBF7D0")),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(res_table)
            story.append(Spacer(1, 10))

        # Complexity Table
        c_info = COMPLEXITY_CATALOG.get(topic_key)
        if not c_info and steps:
            # Check step metrics
            m = getattr(steps[-1], "metrics", None) or {}
            if "time_complexity" in m or "space_complexity" in m:
                c_info = {
                    "time_best": m.get("time_complexity", "O(1)"),
                    "time_avg": m.get("time_complexity", "N/A"),
                    "time_worst": m.get("time_complexity", "N/A"),
                    "space": m.get("space_complexity", "O(1)")
                }

        if c_info:
            c_rows = [
                [Paragraph("<b>Metric</b>", meta_label_style), Paragraph("<b>Theoretical Bound</b>", meta_label_style)],
                [Paragraph("Best-Case Time Complexity", body_style), Paragraph(escape_pdf_text(c_info.get("time_best", "N/A")), body_style)],
                [Paragraph("Average-Case Time Complexity", body_style), Paragraph(escape_pdf_text(c_info.get("time_avg", "N/A")), body_style)],
                [Paragraph("Worst-Case Time Complexity", body_style), Paragraph(escape_pdf_text(c_info.get("time_worst", "N/A")), body_style)],
                [Paragraph("Worst-Case Auxiliary Space", body_style), Paragraph(escape_pdf_text(c_info.get("space", "N/A")), body_style)],
            ]
            comp_table = Table(c_rows, colWidths=[240, 300])
            comp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EDE9FE")),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#FFFFFF")),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(comp_table)

        # Build document with custom numbered canvas
        def make_canvas(*args, **kwargs):
            canv = NumberedCanvas(*args, **kwargs)
            canv.doc_title = display_name
            return canv

        doc.build(story, canvasmaker=make_canvas)
        return output_path
