import io
import os
import logging
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

logger = logging.getLogger(__name__)

class ReportPDFGenerator:
    """
    Generates professional, publication-quality executive evaluation report PDFs for Autergo hiring teams.
    """

    @classmethod
    def generate_evaluation_pdf_bytes(
        cls,
        candidate_name: str,
        job_title: str,
        overall_score: int,
        recommendation: str,
        summary: str,
        technical_score: int = 85,
        behavioral_score: int = 80,
        communication_score: int = 85,
        evidence: Optional[List[Dict[str, Any]]] = None,
    ) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#64748b"),
            spaceAfter=12,
        )
        section_style = ParagraphStyle(
            "ReportSection",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=12,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["Normal"],
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#334155"),
        )
        quote_style = ParagraphStyle(
            "ReportQuote",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#475569"),
            fontName="Helvetica-Oblique",
        )

        elements = []

        # 1. Header
        elements.append(Paragraph("Autergo AI Candidate Evaluation Report", title_style))
        elements.append(Paragraph(f"Candidate: <b>{candidate_name}</b> | Target Role: <b>{job_title}</b>", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0"), spaceAfter=14))

        # 2. Executive Score Card Table
        badge_color = "#10b981" if recommendation == "PASS" else ("#f59e0b" if recommendation == "HOLD" else "#ef4444")
        summary_table_data = [
            [
                Paragraph(f"<font size=11 color='#64748b'>COMPOSITE SCORE</font><br/><font size=28 color='#0284c7'><b>{overall_score}</b></font><font size=12 color='#64748b'> / 100</font>", body_style),
                Paragraph(f"<font size=11 color='#64748b'>RECOMMENDATION</font><br/><font size=22 color='{badge_color}'><b>{recommendation}</b></font>", body_style),
            ]
        ]
        summary_table = Table(summary_table_data, colWidths=[270, 270])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
            ("INNERGRID", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("LEFTPADDING", (0, 0), (-1, -1), 16),
            ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 14))

        # 3. Domain Multi-Agent Scores Table
        elements.append(Paragraph("Multi-Agent Domain Consensus Breakdown", section_style))
        breakdown_data = [
            ["Evaluation Dimension", "Weight", "Score", "Performance Band"],
            ["Technical Problem Solving & Architecture", "50%", f"{technical_score} / 100", "Strong" if technical_score >= 80 else "Proficient"],
            ["Behavioral Competencies & Ownership", "25%", f"{behavioral_score} / 100", "Strong" if behavioral_score >= 80 else "Proficient"],
            ["Communication Clarity & Structure", "25%", f"{communication_score} / 100", "Strong" if communication_score >= 80 else "Proficient"],
        ]
        breakdown_table = Table(breakdown_data, colWidths=[240, 80, 100, 120])
        breakdown_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(breakdown_table)
        elements.append(Spacer(1, 12))

        # 4. Executive Narrative Summary
        elements.append(Paragraph("Executive Summary & Synthesis", section_style))
        elements.append(Paragraph(summary or "The candidate demonstrated sound technical fundamentals and communicative articulation.", body_style))
        elements.append(Spacer(1, 12))

        # 5. Verbatim Evidence Citations
        if evidence:
            elements.append(Paragraph("Transcript Evidence Citations", section_style))
            evidence_rows = [["Agent", "Verbatim Candidate Quote", "Relevance"]]
            for ev in evidence[:5]:
                agent_name = ev.get("agent", "EVALUATOR")
                quote_text = ev.get("quote", "")
                relevance = ev.get("relevance", "High")
                evidence_rows.append([
                    Paragraph(f"<b>{agent_name}</b>", body_style),
                    Paragraph(f'"{quote_text}"', quote_style),
                    Paragraph(relevance, body_style),
                ])

            ev_table = Table(evidence_rows, colWidths=[100, 360, 80])
            ev_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            elements.append(ev_table)

        doc.build(elements)
        return buffer.getvalue()
