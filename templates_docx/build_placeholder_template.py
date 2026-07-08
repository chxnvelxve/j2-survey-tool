"""Build templates_docx/survey_report.docx — run to regenerate the placeholder template.

Jinja tag inventory (🔒 layout assumptions until Josh's sample deliverable):
  company_name, primary_color, logo, job_name, project_name
  aps[]: name, model, vendor, floor, x, y, status, radios_summary,
         photo_close, photo_far, photo_close_label, photo_far_label
  attachments[]: filename, image, is_image
  overrides[]: ap_name, type_label, detail, reason
"""
from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.shared import Pt

OUT = Path(__file__).with_name("survey_report.docx")


def _heading(doc: Document, text: str, *, level: int = 1) -> None:
    doc.add_heading(text, level=level)


def _para(doc: Document, text: str) -> None:
    doc.add_paragraph(text)


def build() -> None:
    doc = Document()

    _para(doc, "{{ logo }}")
    _heading(doc, "{{ company_name }}", level=0)
    _para(doc, "Job: {{ job_name }}")
    _para(doc, "Project: {{ project_name }}")

    _heading(doc, "Executive Summary")
    _para(
        doc,
        "This report documents wireless access point installation and survey results "
        "for the site named above. Detailed RF configuration and field photos follow. "
        "(Placeholder text — replace when Josh's sample deliverable arrives.)",
    )

    _heading(doc, "Access Points")
    _para(doc, "{%p for ap in aps %}")
    _para(doc, "{{ ap.name }} — {{ ap.model }} — {{ ap.floor }} — {{ ap.status }}")
    _para(doc, "Vendor: {{ ap.vendor }}  |  Position: X={{ ap.x }} Y={{ ap.y }}")
    _para(doc, "Radios: {{ ap.radios_summary }}")
    _para(doc, "Close: {{ ap.photo_close_label }} {{ ap.photo_close }}")
    _para(doc, "Far: {{ ap.photo_far_label }} {{ ap.photo_far }}")
    _para(doc, "{%p endfor %}")

    _heading(doc, "Supporting Documents")
    _para(doc, "{%p for att in attachments %}")
    _para(doc, "{% if att.image %}{{ att.filename }}: {{ att.image }}{% else %}{{ att.filename }}{% endif %}")
    _para(doc, "{%p endfor %}")

    _heading(doc, "Override Audit")
    _para(doc, "{%p for ov in overrides %}")
    _para(doc, "{{ ov.ap_name }} — {{ ov.type_label }}: {{ ov.detail }} ({{ ov.reason }})")
    _para(doc, "{%p endfor %}")

    run = doc.add_paragraph().add_run("Prepared by {{ company_name }}")
    run.font.size = Pt(9)

    doc.save(OUT)
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
