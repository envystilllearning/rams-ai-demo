"""PDF generation with ReportLab (no Docker needed, PRD §13 alternative).

Mirrors the DOCX structure from the same stored data. Pure Python.
"""

from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.services.document import DISCLAIMER

NAVY = colors.HexColor("#0B1F3A")
AMBER = colors.HexColor("#F59E0B")
GREY = colors.HexColor("#64748B")
LIGHT_GREY = colors.HexColor("#F1F5F9")


def _styles():
    ss = getSampleStyleSheet()
    title = ParagraphStyle("RamsTitle", parent=ss["Title"], textColor=NAVY, fontSize=22, spaceAfter=6)
    h1 = ParagraphStyle("RamsH1", parent=ss["Heading1"], textColor=NAVY, fontSize=14, spaceBefore=14, spaceAfter=6)
    h2 = ParagraphStyle("RamsH2", parent=ss["Heading2"], textColor=NAVY, fontSize=11, spaceBefore=10, spaceAfter=4)
    body = ParagraphStyle("RamsBody", parent=ss["BodyText"], fontSize=9.5, leading=13.5)
    small = ParagraphStyle("RamsSmall", parent=ss["BodyText"], fontSize=8.5, leading=11.5, textColor=GREY)
    center = ParagraphStyle("RamsCenter", parent=body, alignment=1)
    return title, h1, h2, body, small, center


TABLE_STYLE = TableStyle(
    [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
)


def _kv_table(body_style, pairs: list[tuple[str, Any]]) -> Table:
    rows = [[Paragraph(f"<b>{k}</b>", body_style), Paragraph(str(v or "—"), body_style)] for k, v in pairs]
    t = Table(rows, colWidths=[5 * cm, 11 * cm])
    t.setStyle(TABLE_STYLE)
    return t


def build_rams_pdf(
    form_input: dict[str, Any],
    generated: dict[str, Any],
    profile: dict[str, Any] | None,
    document_number: str,
) -> bytes:
    """Build the RAMS PDF. Raises ValueError when content is missing."""
    if not generated.get("hazards"):
        raise ValueError("No generated hazards — refusing to build an empty document")

    profile = profile or {}
    title, h1, h2, body, small, center = _styles()
    story: list = []
    P = lambda text: Paragraph(str(text or "—"), body)  # noqa: E731

    # --- Cover ---
    story.append(Spacer(1, 4 * cm))
    story.append(Paragraph("Risk Assessment and<br/>Method Statement", title))
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph(f"<b>{form_input.get('project_name') or ''}</b>", center))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(f"Document: {document_number} &nbsp;|&nbsp; Revision: 01", center))
    story.append(Paragraph(str(profile.get("company_name") or ""), center))
    story.append(PageBreak())

    # --- Document control ---
    story.append(Paragraph("Document control", h1))
    story.append(
        _kv_table(
            body,
            [
                ("Document number", document_number),
                ("Revision", "01"),
                ("Project", form_input.get("project_name")),
                ("Site address", form_input.get("site_address")),
                ("Client", form_input.get("client_name")),
                ("Project reference", form_input.get("project_reference")),
                ("Prepared by", profile.get("full_name")),
                ("Company", profile.get("company_name")),
            ],
        )
    )

    # --- Project / scope ---
    story.append(Paragraph("Project details", h1))
    story.append(P(generated.get("project_summary")))
    story.append(Paragraph("Scope of works", h1))
    story.append(P(generated.get("scope_of_work")))
    seq = generated.get("sequence_of_works") or []
    if seq:
        story.append(Paragraph("Sequence of works", h2))
        for i, step in enumerate(seq, 1):
            story.append(P(f"{i}. {step}"))

    # --- Responsibilities / PPE / plant ---
    story.append(Paragraph("Responsibilities", h1))
    story.append(
        P(
            "The principal contractor retains overall responsibility for site safety. "
            "Supervisors must brief all operatives on this RAMS before work starts."
        )
    )
    story.append(Paragraph("Personal protective equipment", h1))
    for item in generated.get("ppe") or []:
        story.append(P(f"•  {item}"))
    story.append(Paragraph("Plant and equipment", h1))
    for key, label in (("plant", "Plant"), ("equipment", "Equipment"), ("tools", "Tools"), ("materials", "Materials")):
        if form_input.get(key):
            story.append(P(f"<b>{label}:</b> {form_input[key]}"))

    # --- Risk assessment table ---
    story.append(Paragraph("Risk assessment", h1))
    hazards = generated.get("hazards") or []
    risk_rows = [
        [
            Paragraph(f"<b>{h.get('hazard')}</b><br/>{h.get('who_might_be_harmed')}", body),
            Paragraph(str(h.get("initial_likelihood")), body),
            Paragraph(str(h.get("initial_severity")), body),
            Paragraph(f"<b>{h.get('initial_risk_score')}</b>", body),
            Paragraph(f"<b>{h.get('residual_risk_score')}</b>", body),
        ]
        for h in hazards
    ]
    header = [Paragraph(f"<b>{h}</b>", body) for h in ["Hazard / who harmed", "L", "S", "Risk", "Residual"]]
    risk_table = Table([header, *risk_rows], colWidths=[8 * cm, 1.5 * cm, 1.5 * cm, 2 * cm, 2.5 * cm])
    risk_table.setStyle(TABLE_STYLE)
    risk_table.repeatRows = 1
    story.append(risk_table)

    for i, h in enumerate(hazards, 1):
        story.append(Paragraph(f"Hazard {i}: {h.get('hazard')}", h2))
        story.append(P(f"Existing controls: {h.get('existing_controls')}"))
        story.append(P(f"Additional controls: {h.get('additional_controls')}"))

    # --- Method statement ---
    story.append(Paragraph("Method statement", h1))
    ms = generated.get("method_statement") or {}
    for key, label in (("preparation", "Preparation"), ("execution", "Execution"), ("completion", "Completion / handover")):
        story.append(Paragraph(label, h2))
        story.append(P(ms.get(key)))

    # --- Emergency / environmental ---
    story.append(Paragraph("Emergency arrangements", h1))
    story.append(P(generated.get("emergency_procedure")))
    story.append(Paragraph("Environmental controls", h1))
    story.append(P(generated.get("environmental_controls")))

    # --- Sign-off ---
    story.append(Paragraph("Review and sign-off", h1))
    story.append(P(f"<i>{DISCLAIMER}</i>"))
    story.append(Spacer(1, 0.3 * cm))
    sign = Table(
        [
            [Paragraph("<b>Role</b>", body), Paragraph("<b>Name</b>", body), Paragraph("<b>Signature</b>", body), Paragraph("<b>Date</b>", body)],
            [P("Prepared by"), P(""), P(""), P("")],
            [P("Reviewed by"), P(""), P(""), P("")],
            [P("Approved by"), P(""), P(""), P("")],
        ],
        colWidths=[4 * cm, 4 * cm, 4 * cm, 4 * cm],
    )
    sign.setStyle(TABLE_STYLE)
    story.append(sign)
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(f"{document_number} · Rev 01", small))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(GREY)
        canvas.drawString(2 * cm, 1.2 * cm, f"{document_number} · Rev 01")
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
        # thin amber rule
        canvas.setStrokeColor(AMBER)
        canvas.setLineWidth(1.5)
        canvas.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
        canvas.restoreState()

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        title=f"RAMS {document_number}",
        author=str(profile.get("company_name") or ""),
        subject=DISCLAIMER,
        topMargin=2 * cm,
        bottomMargin=2.2 * cm,
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buf.getvalue()
