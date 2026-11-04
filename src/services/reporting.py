from __future__ import annotations

from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


REPORT_DIR = Path("reports/generated")


def report_path(decision_id: int) -> Path:
    return REPORT_DIR / f"mangrove-lens-decision-{decision_id}.pdf"


def generate_monitoring_report(decision_id, observation, prediction, decision, images=None) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    output = report_path(decision_id)
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "TitleGreen", parent=styles["Title"], textColor=colors.HexColor("#0F766E"),
        alignment=TA_CENTER, spaceAfter=8,
    )
    heading = ParagraphStyle(
        "HeadingGreen", parent=styles["Heading2"], textColor=colors.HexColor("#0F766E"),
        spaceBefore=10, spaceAfter=6,
    )
    doc = SimpleDocTemplate(
        str(output), pagesize=A4, rightMargin=16 * mm, leftMargin=16 * mm,
        topMargin=14 * mm, bottomMargin=14 * mm,
        title=f"Mangrove Lens monitoring report {observation.period_start}",
        author="Mangrove Lens autonomous monitoring system",
    )
    story = [
        Paragraph("Mangrove Lens", title),
        Paragraph("Autonomous Sundarbans Monitoring Report", styles["Heading2"]),
        Paragraph(
            f"Operational AOI: full transboundary India–Bangladesh Sundarbans<br/>"
            f"Observation period: {observation.period_start} to {observation.period_end}<br/>"
            f"Decision ID: {decision_id}", styles["BodyText"],
        ),
        Spacer(1, 8),
    ]

    def add_table(label, rows):
        story.append(Paragraph(label, heading))
        table = Table(rows, colWidths=[58 * mm, 112 * mm], repeatRows=0)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E6F4F1")),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#0F766E")),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B7D8D2")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(table)

    add_table("Satellite observation", [
        ["Provider", observation.provider],
        ["NDVI mean / p10 / p90", f"{observation.ndvi_mean:.6f} / {observation.ndvi_p10:.6f} / {observation.ndvi_p90:.6f}"],
        ["NDMI mean", f"{observation.ndmi_mean:.6f}"],
        ["Sentinel-1 VV / VH", f"{observation.vv_mean:.6f} / {observation.vh_mean:.6f}"],
        ["Sentinel-5P CO", f"{observation.co_mean:.8f}"],
        ["Valid-pixel fraction", f"{observation.quality.valid_pixel_fraction:.2%}"],
        ["Optical / SAR / CO image counts", f"{observation.quality.optical_image_count} / {observation.quality.sar_image_count} / {observation.quality.co_image_count}"],
        ["Quality status", observation.quality.status],
    ])
    add_table("Model and decision", [
        ["Model version", prediction.model_version],
        ["Expected NDVI", f"{prediction.expected_ndvi:.6f}"],
        ["Actual − expected", f"{prediction.residual:+.6f}"],
        ["Uncertainty", f"{prediction.uncertainty:.6f}"],
        ["Anomaly score", f"{prediction.anomaly_score:.4f}"],
        ["Risk severity / score", f"{decision.severity.label.upper()} / {decision.score:.0f} of 100"],
        ["Human review required", "Yes" if decision.requires_human_review else "No"],
        ["Rule version", decision.rule_version],
    ])

    story.append(Paragraph("Evidence", heading))
    for item in decision.evidence:
        story.append(Paragraph(f"• {item}", styles["BodyText"]))
    story.append(Paragraph("Recommended actions", heading))
    for item in decision.recommendations:
        story.append(Paragraph(f"• {item}", styles["BodyText"]))

    provenance = observation.provenance
    add_table("Data provenance", [
        ["Earth Engine project", str(provenance.get("ee_project", "—"))],
        ["Query executed", str(provenance.get("query_executed_at", observation.acquired_at.isoformat()))],
        ["Filter window", f"{provenance.get('period_filter_start', observation.period_start)} to {provenance.get('period_filter_end_exclusive', observation.period_end)} (exclusive)"],
        ["Collections", Paragraph("<br/>".join(observation.source_collections), styles["BodyText"])],
        ["Aggregation scale", f"{provenance.get('aggregation_scale_m', '—')} m"],
        ["Mangrove reference year", str(provenance.get("mangrove_reference_year", "—"))],
    ])

    if images:
        story.append(PageBreak())
        story.append(Paragraph("Satellite evidence imagery", title))
        for label, image_bytes in images.items():
            story.append(Paragraph(label, heading))
            graphic = Image(BytesIO(image_bytes))
            max_width, max_height = 175 * mm, 105 * mm
            scale = min(max_width / graphic.imageWidth, max_height / graphic.imageHeight)
            graphic.drawWidth = graphic.imageWidth * scale
            graphic.drawHeight = graphic.imageHeight * scale
            story.extend([graphic, Spacer(1, 6)])
        story.append(Paragraph(
            "Imagery is generated dynamically from the collections and period listed above. "
            "Colors in the NDVI image range from red (low index) to dark green (high index).",
            styles["BodyText"],
        ))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Research-grade automated screening. Critical or high-risk findings require expert image review "
        "and field/reference verification before external conservation action.", styles["Italic"],
    ))
    doc.build(story)
    return output
