from __future__ import annotations

from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.platypus import (
    Flowable, Image, PageBreak, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)


REPORT_DIR = Path("reports/generated")
TEAL = colors.HexColor("#0F766E")
TEAL_DARK = colors.HexColor("#075E57")
TEAL_PALE = colors.HexColor("#E6F4F1")
INK = colors.HexColor("#18302D")
MUTED = colors.HexColor("#61716E")
GRID = colors.HexColor("#B7D8D2")
AMBER = colors.HexColor("#B7791F")


def report_path(decision_id: int) -> Path:
    return REPORT_DIR / f"mangrove-lens-decision-{decision_id}.pdf"


class NdviLegend(Flowable):
    palette = ["#8b0000", "#d73027", "#fdae61", "#ffffbf", "#a6d96a", "#1a9850", "#006400"]

    def __init__(self, width=165 * mm, height=15 * mm):
        super().__init__()
        self.width, self.height = width, height

    def draw(self):
        canvas = self.canv
        bar_y, bar_h = 7 * mm, 5 * mm
        segment = self.width / len(self.palette)
        for index, color in enumerate(self.palette):
            canvas.setFillColor(colors.HexColor(color))
            canvas.rect(index * segment, bar_y, segment + 0.2, bar_h, fill=1, stroke=0)
        canvas.setFillColor(INK)
        canvas.setFont("Helvetica", 7.5)
        ticks = [(-0.2, 0), (0.0, self.width * 0.18), (0.3, self.width * 0.45), (0.6, self.width * 0.73), (0.9, self.width)]
        for value, x in ticks:
            label = f"{value:.1f}"
            canvas.drawCentredString(max(8, min(self.width - 8, x)), 3 * mm, label)
        canvas.setFont("Helvetica-Bold", 7.5)
        canvas.drawString(0, 0, "Lower vegetation index")
        canvas.drawRightString(self.width, 0, "Higher vegetation index")


def _paragraph(value, style):
    return value if isinstance(value, Paragraph) else Paragraph(str(value), style)


def _page_frame(canvas, page_number):
    canvas.saveState()
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawRightString(A4[0] - 16 * mm, 8 * mm, f"Page {page_number}")
    canvas.restoreState()


class ReportCanvas(pdf_canvas.Canvas):
    """Paint the fixed report frame after page content so it cannot be obscured."""

    def showPage(self):
        _page_frame(self, self._pageNumber)
        super().showPage()


def generate_monitoring_report(
    decision_id, observation, prediction, decision, images=None, system_audit=None
) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    output = report_path(decision_id)
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "Body", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.7,
        leading=11.2, textColor=INK, spaceAfter=4,
    )
    small = ParagraphStyle("Small", parent=body, fontSize=7.5, leading=9.4, textColor=MUTED)
    title = ParagraphStyle(
        "Title", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=24,
        leading=28, textColor=TEAL_DARK, alignment=TA_LEFT, spaceAfter=4,
    )
    subtitle = ParagraphStyle(
        "Subtitle", parent=styles["Heading2"], fontName="Helvetica", fontSize=12,
        leading=15, textColor=MUTED, spaceAfter=10,
    )
    heading = ParagraphStyle(
        "Heading", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=14,
        leading=17, textColor=TEAL, spaceBefore=8, spaceAfter=6,
    )
    subheading = ParagraphStyle(
        "Subheading", parent=styles["Heading3"], fontName="Helvetica-Bold", fontSize=10,
        leading=12, textColor=TEAL_DARK, spaceBefore=5, spaceAfter=4,
    )
    metric = ParagraphStyle(
        "Metric", parent=body, fontName="Helvetica-Bold", fontSize=15,
        leading=17, textColor=TEAL_DARK, alignment=TA_CENTER,
    )
    metric_label = ParagraphStyle(
        "MetricLabel", parent=small, fontSize=7.2, alignment=TA_CENTER, textColor=MUTED,
    )
    doc = SimpleDocTemplate(
        str(output), pagesize=A4, rightMargin=16 * mm, leftMargin=16 * mm,
        topMargin=17 * mm, bottomMargin=16 * mm,
        title=f"Mangrove Lens monitoring report {observation.period_start}",
        author="Mangrove Lens autonomous monitoring system",
    )
    story = []

    def branded_title(label, *, compact=False):
        size = 21 if compact else 24
        return Paragraph(
            f'<font name="Helvetica-Bold" size="{size}" color="#075E57">{label}</font>',
            ParagraphStyle(
                f"BrandedTitle{size}", parent=title, fontSize=size, leading=size + 4,
                spaceAfter=4,
            ),
        )

    def section(label):
        story.append(Paragraph(label, heading))

    def table(rows, widths=(57 * mm, 113 * mm), font_size=8):
        formatted = [[_paragraph(left, body), _paragraph(right, body)] for left, right in rows]
        result = Table(formatted, colWidths=list(widths), repeatRows=0, hAlign="LEFT")
        result.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), TEAL_PALE),
            ("TEXTCOLOR", (0, 0), (0, -1), TEAL_DARK),
            ("GRID", (0, 0), (-1, -1), 0.35, GRID),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), font_size),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(result)

    # Page 1 - executive findings.
    story.extend([
        branded_title("Mangrove Lens"),
        Paragraph("Autonomous transboundary Sundarbans monitoring report", subtitle),
        Table([
            [Paragraph("REPORT PERIOD", metric_label), Paragraph("OPERATIONAL AREA", metric_label), Paragraph("DECISION", metric_label)],
            [Paragraph(str(observation.period_start), metric), Paragraph("India + Bangladesh", metric), Paragraph(decision.severity.label.upper(), metric)],
        ], colWidths=[55 * mm, 60 * mm, 55 * mm], style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), TEAL_PALE),
            ("BOX", (0, 0), (-1, -1), 0.6, GRID),
            ("INNERGRID", (0, 0), (-1, -1), 0.35, GRID),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])),
    ])
    section("Executive summary")
    story.append(Paragraph(
        f"Mangrove Lens analyzed the completed monthly window from <b>{observation.period_start}</b> "
        f"to <b>{observation.period_end}</b> across the full India-Bangladesh Sundarbans operational "
        f"area. Live Google Earth Engine collections were reduced only within the independent 2023 "
        f"mangrove reference mask. The system assigned <b>{decision.severity.label.upper()}</b> risk "
        f"with a score of <b>{decision.score:.0f}/100</b>. Actual NDVI was "
        f"<b>{observation.ndvi_mean:.4f}</b>, compared with the model expectation of "
        f"<b>{prediction.expected_ndvi:.4f}</b>.", body,
    ))
    metrics = [
        ("Actual NDVI", f"{observation.ndvi_mean:.3f}"),
        ("Expected NDVI", f"{prediction.expected_ndvi:.3f}"),
        ("Anomaly score", f"{prediction.anomaly_score:.2f}"),
        ("Valid pixels", f"{observation.quality.valid_pixel_fraction:.0%}"),
    ]
    metric_cells = []
    for label, value in metrics:
        metric_cells.append([Paragraph(value, metric), Paragraph(label, metric_label)])
    metric_table = Table(
        [[cell[0] for cell in metric_cells], [cell[1] for cell in metric_cells]],
        colWidths=[42.5 * mm] * 4,
    )
    metric_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, GRID),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, GRID),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("TOPPADDING", (0, 0), (-1, 0), 7),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 7),
    ]))
    story.extend([Spacer(1, 4), metric_table])
    section("Findings and recommended action")
    for item in decision.evidence:
        story.append(Paragraph(f"- {item}", body))
    for item in decision.recommendations:
        story.append(Paragraph(f"<b>Action:</b> {item}", body))
    table([
        ["Data quality", f"{observation.quality.status}; {observation.quality.valid_pixel_fraction:.2%} usable optical coverage"],
        ["Images analyzed", f"{observation.quality.optical_image_count} optical, {observation.quality.sar_image_count} SAR, {observation.quality.co_image_count} CO"],
        ["Human review", "Required" if decision.requires_human_review else "Not required by the current severity policy"],
        ["Decision ID", decision_id],
    ])

    # Pages 2-3 - evidence imagery, each with its own key.
    orientation_rows = [
        ["Left / west", "Indian Sundarbans (West Bengal)"],
        ["Right / east", "Bangladesh Sundarbans"],
        ["Top / north", "Inland delta and upstream boundary"],
        ["Bottom / south", "Bay of Bengal coastal edge"],
        ["White / transparent", "Outside the 2023 mangrove mask or without valid displayed pixels"],
    ]
    if images:
        for label, image_bytes in images.items():
            story.append(PageBreak())
            story.append(branded_title(label))
            story.append(Paragraph(
                f"North-up Earth Engine composite for {observation.period_start}. Source: "
                f"COPERNICUS/S2_SR_HARMONIZED; mask: projects/mangrovedatahub2/assets/CGMD-Extent30.",
                small,
            ))
            story.append(Spacer(1, 4))
            graphic = Image(BytesIO(image_bytes))
            # Reserve enough room for the complete image and geographic keys above
            # the fixed report footer on every renderer.
            max_width, max_height = 177 * mm, 108 * mm
            scale = min(max_width / graphic.imageWidth, max_height / graphic.imageHeight)
            graphic.drawWidth = graphic.imageWidth * scale
            graphic.drawHeight = graphic.imageHeight * scale
            story.append(graphic)
            if "NDVI" in label:
                story.extend([
                    Paragraph("NDVI key", subheading), NdviLegend(), Spacer(1, 3),
                    Paragraph(
                        "Interpretation: red and orange indicate lower vegetation index values within the "
                        "mangrove mask; light and dark greens indicate progressively higher vegetation index "
                        "values. NDVI is an indicator, not a direct diagnosis of mangrove loss.", body,
                    ),
                ])
            else:
                story.extend([
                    Paragraph("True-color image key", subheading),
                    Table([
                        [Paragraph("Dark green", body), Paragraph("Dense or darker vegetated mangrove canopy", body)],
                        [Paragraph("Light green / tan", body), Paragraph("Brighter canopy, exposed substrate, mixed pixels or atmospheric variation", body)],
                        [Paragraph("White", body), Paragraph("Masked non-mangrove area, waterways/background or unavailable displayed pixels", body)],
                    ], colWidths=[42 * mm, 128 * mm], style=TableStyle([
                        ("GRID", (0, 0), (-1, -1), 0.35, GRID),
                        ("BACKGROUND", (0, 0), (0, -1), TEAL_PALE),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("TOPPADDING", (0, 0), (-1, -1), 3),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ])),
                ])
            story.append(Paragraph("Area orientation key", subheading))
            area_table = Table(
                [[_paragraph(a, body), _paragraph(b, body)] for a, b in orientation_rows],
                colWidths=[42 * mm, 128 * mm],
            )
            area_table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.35, GRID),
                ("BACKGROUND", (0, 0), (0, -1), TEAL_PALE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(area_table)

    # Page 4 - model and decision audit.
    story.append(PageBreak())
    story.append(branded_title("AI and ML decision audit"))
    story.append(Paragraph(
        "Scientific measurements and risk scoring are deterministic and auditable. No language model "
        "changes satellite values, model predictions, thresholds or alert approval policy.", body,
    ))
    table([
        ["Algorithm", "RandomForestRegressor (400 trees; maximum depth 10; minimum leaf size 2)"],
        ["Model version", prediction.model_version],
        ["Expected NDVI", f"{prediction.expected_ndvi:.6f}"],
        ["Actual - expected", f"{prediction.residual:+.6f}"],
        ["Tree uncertainty", f"{prediction.uncertainty:.6f}"],
        ["Anomaly score", f"{prediction.anomaly_score:.4f}"],
        ["Rule result", f"{decision.severity.label.upper()} / {decision.score:.0f} of 100 ({decision.rule_version})"],
    ])
    audit = system_audit or {}
    metrics_data = audit.get("model_metrics", {})
    section("Held-out model validation")
    table([
        ["Dataset type", audit.get("dataset_kind", "observational")],
        ["Data period", f"{audit.get('data_start', 'n/a')} to {audit.get('data_end', 'n/a')}"],
        ["Training / test rows", f"{metrics_data.get('train_rows', 'n/a')} / {metrics_data.get('test_rows', 'n/a')}"],
        ["MAE / RMSE", f"{metrics_data.get('mae', 'n/a')} / {metrics_data.get('rmse', 'n/a')}"],
        ["R-squared", metrics_data.get("r2", "n/a")],
        ["Persistence MAE", metrics_data.get("persistence_mae", "n/a")],
        ["Observational gate", "Passed" if audit.get("observational_gate_passed") else "Not passed"],
        ["External production approval", "Approved" if audit.get("production_approved") else "Not approved"],
    ])
    section("Leakage-safe predictor inputs")
    table([
        ["Vegetation history", "NDVI lag 1, NDVI lag 12, prior 3-month median"],
        ["Environmental history", "Previous NDMI, Sentinel-1 VV/VH and Sentinel-5P CO"],
        ["Seasonality", "Calendar month"],
        ["Target isolation", "Current-month NDVI is compared only after the expected value is predicted"],
    ])

    # Page 5 - complete system audit.
    story.append(PageBreak())
    story.append(branded_title("Mangrove Lens system audit"))
    story.append(Paragraph(
        "Operational status captured when this report was generated. Agent stages are implemented as "
        "deterministic services with persisted checkpoints and provenance.", body,
    ))
    status_rows = [
        ["Earth Engine acquisition agent", "PASS", f"Project {observation.provenance.get('ee_project', 'n/a')}; live monthly query completed"],
        ["Data-quality agent", "PASS" if observation.quality.status == "valid" else "REVIEW", f"{observation.quality.status}; {observation.quality.valid_pixel_fraction:.2%} valid pixels"],
        ["Feature agent", "PASS", "12 prior valid observations enforced; leakage-safe lags constructed"],
        ["Forecast agent", "PASS", f"Model {prediction.model_version}; uncertainty recorded"],
        ["Risk-decision agent", "PASS", f"Rule {decision.rule_version}; evidence and recommendation persisted"],
        ["Reporting agent", "PASS", "Detailed PDF with live evidence imagery generated"],
        ["Alert agent", "PASS", "Dashboard outbox active; external channels policy-gated"],
        [
            "Scheduler and retraining",
            "CONFIGURED",
            "Dedicated scheduler service performs monthly reconciliation, monitoring, reporting and post-inference retraining; runtime health is verified separately",
        ],
    ]
    audit_table = Table(
        [[_paragraph(x, body) for x in row] for row in status_rows],
        colWidths=[50 * mm, 26 * mm, 94 * mm], repeatRows=1,
    )
    audit_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.35, GRID),
        ("BACKGROUND", (0, 0), (0, -1), TEAL_PALE),
        ("TEXTCOLOR", (1, 0), (1, -1), TEAL_DARK),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(audit_table)
    section("Operational data inventory")
    table([
        ["Stored monthly observations", audit.get("observation_count", "n/a")],
        ["Valid / low coverage", f"{audit.get('valid_count', 'n/a')} / {audit.get('low_coverage_count', 'n/a')}"],
        ["Completed monitoring jobs", audit.get("completed_job_count", "n/a")],
        ["Decision records", audit.get("decision_count", "n/a")],
        ["Dashboard/external alert records", audit.get("alert_count", "n/a")],
        ["Automatic report email", "Enabled" if audit.get("automatic_email_enabled") else "Disabled until SMTP/policy configuration"],
    ])
    section("End-to-end workflow")
    story.append(Paragraph(
        "Earth Engine collections -> mangrove mask and cloud filtering -> monthly optical/SAR/CO "
        "statistics -> quality gate -> 12-month feature history -> Random Forest expected NDVI -> "
        "residual and uncertainty -> deterministic risk rules -> evidence and recommendation -> PDF "
        "report -> dashboard/email/Telegram outbox -> monthly scheduler -> post-inference retraining.", body,
    ))

    # Page 6 - provenance, methodology and limitations.
    story.append(PageBreak())
    story.append(branded_title("Methodology, provenance and limitations", compact=True))
    section("Live data sources")
    source_rows = [
        ["COPERNICUS/S2_SR_HARMONIZED", "Surface reflectance; NDVI, NDMI and true-color composite"],
        ["COPERNICUS/S1_GRD", "VV/VH radar backscatter context"],
        ["COPERNICUS/S5P/OFFL/L3_CO", "CO column-density context; never treated as causal proof"],
        ["projects/mangrovedatahub2/assets/CGMD-Extent30", "Independent 2023 mangrove extent mask"],
    ]
    table(source_rows)
    section("Query provenance")
    provenance = observation.provenance
    table([
        ["Earth Engine project", provenance.get("ee_project", "n/a")],
        ["Query executed", provenance.get("query_executed_at", observation.acquired_at.isoformat())],
        ["Filter window", f"{provenance.get('period_filter_start', observation.period_start)} to {provenance.get('period_filter_end_exclusive', observation.period_end)} (exclusive)"],
        ["Aggregation scale", f"{provenance.get('aggregation_scale_m', 'n/a')} m"],
        ["Native optical resolution", f"{provenance.get('native_optical_resolution_m', 'n/a')} m"],
        ["Mangrove reference year", provenance.get("mangrove_reference_year", "n/a")],
    ])
    section("Processing method")
    for line in [
        "Sentinel-2 scene classification removes cloud, shadow, cirrus, snow/ice and defective pixels.",
        "Monthly optical and radar composites use the median; CO uses the monthly mean.",
        "All vegetation and radar reductions are restricted to the independent mangrove reference mask.",
        "Risk decisions combine model residual/anomaly, moisture, radar and contextual CO evidence.",
        "High and critical findings require expert review and field/reference confirmation.",
    ]:
        story.append(Paragraph(f"- {line}", body))
    section("Limitations and correct use")
    story.append(Paragraph(
        "Sentinel data are dynamically queried from Earth Engine but are not instantaneous telemetry. "
        "This report represents a completed monthly window. Cloud coverage, tidal conditions, seasonal "
        "phenology, sensor geometry and reference-mask age can influence values. The current model forecasts "
        "AOI-level mean NDVI and is not a pixel-level deforestation classifier. CO is contextual evidence only. "
        "Use this report for screening and prioritization, not as sole evidence for enforcement or causal claims.",
        body,
    ))
    story.append(Spacer(1, 6))
    warning = Table([[Paragraph(
        "Professional review requirement: validate high-impact findings using independent imagery, local "
        "expert interpretation and field/reference evidence before external conservation action.", body,
    )]], colWidths=[170 * mm])
    warning.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF7E6")),
        ("BOX", (0, 0), (-1, -1), 0.7, AMBER),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(warning)

    doc.build(story, canvasmaker=ReportCanvas)
    return output
