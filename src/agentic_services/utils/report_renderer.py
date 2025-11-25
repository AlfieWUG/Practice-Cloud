"""Utility helpers for composing branded PDF assessment reports."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any, Dict, List

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.spider import SpiderChart
from reportlab.graphics.shapes import Drawing, Line, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

PRIMARY = colors.HexColor("#00D9C1")
SECONDARY = colors.HexColor("#00313C")


class ReportRenderer:
    """Generates PDF reports from structured assessment data."""

    def __init__(self, logo_path: str | None = None):
        self.logo_path = Path(logo_path or "assets/images/nagarro_logo.png")
        self.styles = getSampleStyleSheet()
        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                fontSize=16,
                leading=20,
                spaceAfter=12,
                textColor=SECONDARY,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="SubHeader",
                fontSize=13,
                leading=16,
                textColor=PRIMARY,
                spaceAfter=8,
            )
        )
        # Add Bullet style if it doesn't exist
        if "Bullet" not in self.styles.byName:
            self.styles.add(
                ParagraphStyle(
                    name="Bullet",
                    fontSize=11,
                    leading=14,
                    leftIndent=18,
                )
            )
        else:
            # Update existing Bullet style
            self.styles["Bullet"].fontSize = 11
            self.styles["Bullet"].leading = 14
            self.styles["Bullet"].leftIndent = 18

    def build_pdf(self, report: Dict[str, Any]) -> bytes:
        """Render the assessment report into PDF bytes."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=LETTER,
            leftMargin=0.75 * inch,
            rightMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
            title="AIMS Quick Assess Report",
        )

        story = []
        story.extend(self._build_cover(report))
        story.extend(self._build_executive_summary(report))
        story.append(PageBreak())
        story.extend(self._build_inventory_section(report))
        story.append(PageBreak())
        story.extend(self._build_technology_stack(report))
        story.append(PageBreak())
        story.extend(self._build_architecture_section(report))
        story.append(PageBreak())
        story.extend(self._build_cloud_readiness(report))
        story.append(PageBreak())
        story.extend(self._build_risk_section(report))
        story.append(PageBreak())
        story.extend(self._build_recommendations(report))

        doc.build(
            story,
            onFirstPage=self._draw_header_footer,
            onLaterPages=self._draw_header_footer,
        )

        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    # Section builders -------------------------------------------------
    def _build_cover(self, report: Dict[str, Any]) -> List:
        story: List = []
        if self.logo_path.exists():
            story.append(Image(str(self.logo_path), width=2.5 * inch, height=0.75 * inch))
        story.append(Spacer(1, 0.5 * inch))
        story.append(
            Paragraph(
                "Quick Assess Environment Report",
                self.styles["Title"],
            )
        )
        project = report.get("metadata", {}).get("project_name", "Assessment")
        story.append(Paragraph(project, self.styles["Heading2"]))
        story.append(Spacer(1, 0.3 * inch))
        story.append(
            Paragraph(
                f"Overall Score: {report.get('cloud_readiness', {}).get('score', 'N/A')}",
                self.styles["Heading2"],
            )
        )
        story.append(Spacer(1, 0.5 * inch))
        return story

    def _build_executive_summary(self, report: Dict[str, Any]) -> List:
        summary = report.get("executive_summary", {})
        story: List = [
            Paragraph("1. Executive Summary", self.styles["SectionHeader"]),
            Paragraph(summary.get("overview", "Summary unavailable."), self.styles["BodyText"]),
        ]
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("Key Findings", self.styles["SubHeader"]))
        for item in summary.get("key_findings", [])[:5]:
            story.append(Paragraph(f"• {item}", self.styles["Bullet"]))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("Recommended Next Steps", self.styles["SubHeader"]))
        for step in summary.get("next_steps", [])[:5]:
            story.append(Paragraph(f"• {step}", self.styles["Bullet"]))
        return story

    def _build_inventory_section(self, report: Dict[str, Any]) -> List:
        inventory = report.get("infrastructure_inventory", {})
        counts = inventory.get("counts", {})
        story: List = [
            Paragraph("2. Infrastructure Inventory", self.styles["SectionHeader"]),
            Paragraph("Component Breakdown", self.styles["SubHeader"]),
        ]

        table_data = [["Component Type", "Count"]]
        for comp_type, value in counts.items():
            table_data.append([comp_type.title(), value])
        table = Table(table_data, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 0.2 * inch))
        story.append(self._component_chart(counts))

        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph("Sample Connections", self.styles["SubHeader"]))
        connections = inventory.get("connections", [])[:10]
        if connections:
            for conn in connections:
                story.append(
                    Paragraph(
                        f"{conn.get('from')} → {conn.get('to')} ({conn.get('type')})",
                        self.styles["BodyText"],
                    )
                )
        else:
            story.append(Paragraph("Connection data unavailable.", self.styles["BodyText"]))
        return story

    def _build_technology_stack(self, report: Dict[str, Any]) -> List:
        stack = report.get("technology_stack", {})
        story: List = [
            Paragraph("3. Technology Stack Analysis", self.styles["SectionHeader"]),
            Paragraph(stack.get("summary", "No technology summary provided."), self.styles["BodyText"]),
            Spacer(1, 0.2 * inch),
        ]
        for heading in ["languages", "frameworks", "cloud_services", "databases", "storage"]:
            if stack.get(heading):
                story.append(Paragraph(heading.replace("_", " ").title(), self.styles["SubHeader"]))
                story.append(Paragraph(", ".join(stack[heading]), self.styles["BodyText"]))
                story.append(Spacer(1, 0.1 * inch))
        story.append(self._tech_distribution_chart(stack))
        return story

    def _build_architecture_section(self, report: Dict[str, Any]) -> List:
        arch = report.get("architecture_assessment", {})
        story: List = [
            Paragraph("4. Architecture Assessment", self.styles["SectionHeader"]),
            Paragraph(f"Pattern Identified: {arch.get('pattern', 'Unknown')}", self.styles["BodyText"]),
            Spacer(1, 0.2 * inch),
            Paragraph("Scalability & Redundancy", self.styles["SubHeader"]),
            Paragraph(
                f"Scalability Score: {arch.get('scalability', {}).get('score', 'N/A')}",
                self.styles["BodyText"],
            ),
            Paragraph(
                f"Redundancy Score: {arch.get('redundancy', {}).get('score', 'N/A')}",
                self.styles["BodyText"],
            ),
            Spacer(1, 0.2 * inch),
            Paragraph("Single Points of Failure", self.styles["SubHeader"]),
        ]
        spof = arch.get("single_points_of_failure", [])
        if spof:
            for item in spof:
                story.append(Paragraph(f"• {item}", self.styles["Bullet"]))
        else:
            story.append(Paragraph("No obvious single points identified.", self.styles["BodyText"]))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("Dependencies", self.styles["SubHeader"]))
        deps = arch.get("dependencies", [])[:15]
        if deps:
            for dep in deps:
                story.append(
                    Paragraph(
                        f"{dep.get('from')} → {dep.get('to')} ({dep.get('type', 'flow')})",
                        self.styles["BodyText"],
                    )
                )
        else:
            story.append(Paragraph("No dependency map available.", self.styles["BodyText"]))
        return story

    def _build_cloud_readiness(self, report: Dict[str, Any]) -> List:
        readiness = report.get("cloud_readiness", {})
        story: List = [
            Paragraph("5. Cloud Readiness Score", self.styles["SectionHeader"]),
            Paragraph(
                f"Overall Score: {readiness.get('score', 'N/A')}",
                self.styles["BodyText"],
            ),
            Paragraph("Scoring Breakdown", self.styles["SubHeader"]),
        ]
        story.append(self._cloud_radar_chart(readiness))
        story.append(Spacer(1, 0.2 * inch))
        story.append(
            Paragraph(
                readiness.get("explanation", "Detailed scoring explanation not provided."),
                self.styles["BodyText"],
            )
        )
        return story

    def _build_risk_section(self, report: Dict[str, Any]) -> List:
        risks = report.get("risk_assessment", {})
        story: List = [
            Paragraph("6. Risk Assessment", self.styles["SectionHeader"]),
            Paragraph(f"Overall Risk: {risks.get('overall_risk', 'Unknown')}", self.styles["BodyText"]),
            Spacer(1, 0.1 * inch),
        ]
        for heading in ["outdated_technologies", "missing_redundancy", "security_concerns", "complexity_indicators"]:
            story.append(Paragraph(heading.replace("_", " ").title(), self.styles["SubHeader"]))
            if risks.get(heading):
                for item in risks[heading]:
                    story.append(Paragraph(f"• {item}", self.styles["Bullet"]))
            else:
                story.append(Paragraph("None identified.", self.styles["BodyText"]))
        return story

    def _build_recommendations(self, report: Dict[str, Any]) -> List:
        recs = report.get("recommendations", {})
        story: List = [
            Paragraph("7. Recommendations", self.styles["SectionHeader"]),
            Paragraph("Prioritized Actions", self.styles["SubHeader"]),
        ]
        for action in recs.get("actions", []):
            story.append(
                Paragraph(
                    f"• {action.get('priority', 'Normal')}: {action.get('description', '')}",
                    self.styles["Bullet"],
                )
            )
        story.append(Spacer(1, 0.1 * inch))
        if timelines := recs.get("timeline"):
            story.append(Paragraph(f"Estimated Timeline: {timelines}", self.styles["BodyText"]))
        if cost := recs.get("cost_estimate"):
            story.append(Paragraph(f"Rough Cost Estimate: {cost}", self.styles["BodyText"]))
        return story

    # Charts ------------------------------------------------------------
    def _component_chart(self, counts: Dict[str, int]) -> Drawing:
        drawing = Drawing(400, 220)
        data = [list(counts.values()) or [0]]
        chart = VerticalBarChart()
        chart.x = 30
        chart.y = 40
        chart.width = 340
        chart.height = 150
        chart.data = data
        chart.barSpacing = 4
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueStep = max(1, int(max(counts.values() or [1]) / 4))
        chart.categoryAxis.categoryNames = [label.title() for label in counts.keys()] or ["N/A"]
        chart.bars[0].fillColor = PRIMARY
        drawing.add(chart)
        drawing.add(String(150, 200, "Component Distribution", fontSize=12, fillColor=SECONDARY))
        return drawing

    def _tech_distribution_chart(self, stack: Dict[str, Any]) -> Drawing:
        counts = [len(stack.get("languages", [])), len(stack.get("frameworks", [])), len(stack.get("cloud_services", []))]
        drawing = Drawing(400, 200)
        chart = VerticalBarChart()
        chart.x = 30
        chart.y = 40
        chart.width = 340
        chart.height = 140
        chart.data = [counts or [0, 0, 0]]
        chart.categoryAxis.categoryNames = ["Languages", "Frameworks", "Cloud"]
        chart.bars[0].fillColor = SECONDARY
        drawing.add(chart)
        drawing.add(String(120, 190, "Technology Coverage", fontSize=12, fillColor=SECONDARY))
        return drawing

    def _cloud_radar_chart(self, readiness: Dict[str, Any]) -> Drawing:
        metrics = readiness.get("metrics", {"legacy": 0, "modularity": 0, "dependencies": 0, "statefulness": 0, "security": 0})
        values = list(metrics.values()) or [0, 0, 0, 0, 0]
        labels = list(metrics.keys()) or ["Metric"]

        drawing = Drawing(300, 220)
        chart = SpiderChart()
        chart.x = 150
        chart.y = 100
        chart.width = 160
        chart.height = 160
        chart.data = [values]
        chart.labels = labels
        chart.spokes.strokeColor = SECONDARY
        chart.strands[0].strokeColor = PRIMARY
        chart.strands[0].fillColor = colors.HexColor("#00D9C133")
        chart.strands[0].strokeWidth = 2
        chart.startAngle = 90
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = 100
        chart.valueAxis.valueStep = 20
        drawing.add(chart)
        drawing.add(String(80, 200, "Cloud Readiness Radar", fontSize=12, fillColor=SECONDARY))
        return drawing

    # Header/footer -----------------------------------------------------
    def _draw_header_footer(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(PRIMARY)
        canvas.setLineWidth(1)
        canvas.line(0.75 * inch, 10.65 * inch, 7.75 * inch, 10.65 * inch)
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(SECONDARY)
        canvas.drawString(0.75 * inch, 10.75 * inch, "Nagarro AIMS Quick Assess")
        canvas.drawRightString(7.75 * inch, 10.75 * inch, f"Page {doc.page}")
        canvas.setFillColor(colors.grey)
        canvas.drawString(0.75 * inch, 0.5 * inch, "Confidential | For internal planning use only")
        canvas.restoreState()

