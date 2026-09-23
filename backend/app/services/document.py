"""DOCX generation from validated AI content + profile (PRD §10, §12).

Deterministic: the same stored data always produces the same document.
"""

from io import BytesIO
from typing import Any

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

DISCLAIMER = (
    "AI-generated draft — this document must be reviewed, amended where "
    "necessary, and approved by a competent person before use on a live project."
)


def _set_cell(cell, text: str, bold: bool = False, size: int = 9) -> None:
    cell.text = ""
    run = cell.paragraphs[0].add_run(str(text or "—"))
    run.bold = bold
    run.font.size = Pt(size)


def _add_table(doc: Document, headers: list[str], rows: list[list[Any]]) -> None:
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    for i, h in enumerate(headers):
        _set_cell(table.rows[0].cells[i], h, bold=True)
    for r, row in enumerate(rows, start=1):
        for c, value in enumerate(row):
            _set_cell(table.rows[r].cells[c], value)
    doc.add_paragraph()


def build_rams_docx(
    form_input: dict[str, Any],
    generated: dict[str, Any],
    profile: dict[str, Any] | None,
    document_number: str,
) -> bytes:
    """Build the full RAMS document. Raises ValueError on missing data."""
    if not generated.get("hazards"):
        raise ValueError("No generated hazards — refusing to build an empty document")

    profile = profile or {}
    doc = Document()

    # Core metadata
    core = doc.core_properties
    core.title = f"RAMS {document_number} — {form_input.get('project_name', '')}"
    core.author = str(profile.get("company_name") or "")
    core.comments = DISCLAIMER

    # --- 1. Cover page ---
    title = doc.add_heading("Risk Assessment and Method Statement", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = sub.add_run(str(form_input.get("project_name") or ""))
    run.bold = True
    run.font.size = Pt(16)
    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta.add_run(
        f"Document: {document_number}   |   Revision: 01\n" f"{profile.get('company_name') or ''}"
    )
    doc.add_page_break()

    # --- 2. Document control ---
    doc.add_heading("Document control", level=1)
    _add_table(
        doc,
        ["Field", "Detail"],
        [
            ["Document number", document_number],
            ["Revision", "01"],
            ["Project", form_input.get("project_name")],
            ["Site address", form_input.get("site_address")],
            ["Client", form_input.get("client_name")],
            ["Project reference", form_input.get("project_reference")],
            ["Prepared by", str(profile.get("full_name") or "")],
            ["Company", profile.get("company_name")],
        ],
    )

    # --- 3. Project details ---
    doc.add_heading("Project details", level=1)
    details = generated.get("project_summary") or ""
    doc.add_paragraph(details)
    for key in ("start_date", "planned_duration", "site_address"):
        if form_input.get(key):
            p = doc.add_paragraph()
            p.add_run(f"{key.replace('_', ' ').title()}: ").bold = True
            p.add_run(str(form_input[key]))

    # --- 4. Scope of works ---
    doc.add_heading("Scope of works", level=1)
    doc.add_paragraph(generated.get("scope_of_work") or "")
    seq = generated.get("sequence_of_works") or []
    if seq:
        doc.add_paragraph("Sequence of works:", style="Heading 3")
        for i, step in enumerate(seq, 1):
            doc.add_paragraph(f"{i}. {step}")

    # --- 5. Responsibilities ---
    doc.add_heading("Responsibilities", level=1)
    doc.add_paragraph(
        "The principal contractor retains overall responsibility for site safety. "
        "Supervisors must brief all operatives on this RAMS before work starts, "
        "and no work may begin until the briefing is recorded."
    )
    if form_input.get("personnel"):
        doc.add_paragraph(f"Personnel: {form_input['personnel']}")

    # --- 6. PPE ---
    doc.add_heading("Personal protective equipment", level=1)
    for item in generated.get("ppe") or []:
        doc.add_paragraph(str(item), style="List Bullet")

    # --- 7. Plant / equipment ---
    doc.add_heading("Plant and equipment", level=1)
    for key, label in (
        ("plant", "Plant"),
        ("equipment", "Equipment"),
        ("tools", "Tools"),
        ("materials", "Materials"),
    ):
        if form_input.get(key):
            p = doc.add_paragraph()
            p.add_run(f"{label}: ").bold = True
            p.add_run(str(form_input[key]))

    # --- 8. Risk assessment ---
    doc.add_heading("Risk assessment", level=1)
    hazards = generated.get("hazards") or []
    _add_table(
        doc,
        ["#", "Hazard", "Who harmed", "L", "S", "Risk", "Residual"],
        [
            [
                str(i),
                h.get("hazard"),
                h.get("who_might_be_harmed"),
                h.get("initial_likelihood"),
                h.get("initial_severity"),
                h.get("initial_risk_score"),
                h.get("residual_risk_score"),
            ]
            for i, h in enumerate(hazards, 1)
        ],
    )
    for i, h in enumerate(hazards, 1):
        doc.add_heading(f"Hazard {i}: {h.get('hazard')}", level=2)
        doc.add_paragraph(f"Existing controls: {h.get('existing_controls')}")
        doc.add_paragraph(f"Additional controls: {h.get('additional_controls')}")

    # --- 9. Method statement ---
    doc.add_heading("Method statement", level=1)
    ms = generated.get("method_statement") or {}
    for key, label in (
        ("preparation", "Preparation"),
        ("execution", "Execution"),
        ("completion", "Completion / handover"),
    ):
        doc.add_heading(label, level=2)
        doc.add_paragraph(str(ms.get(key) or "—"))

    # --- 10. Emergency arrangements ---
    doc.add_heading("Emergency arrangements", level=1)
    doc.add_paragraph(generated.get("emergency_procedure") or "")

    # --- 11. Environmental controls ---
    doc.add_heading("Environmental controls", level=1)
    doc.add_paragraph(generated.get("environmental_controls") or "")

    # --- 12. Sign-off / review ---
    doc.add_heading("Review and sign-off", level=1)
    doc.add_paragraph(DISCLAIMER)
    _add_table(
        doc,
        ["Role", "Name", "Signature", "Date"],
        [["Prepared by", "", "", ""], ["Reviewed by", "", "", ""], ["Approved by", "", "", ""]],
    )

    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()
