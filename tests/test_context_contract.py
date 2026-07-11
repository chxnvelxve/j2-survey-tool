"""Frozen context-contract test for the generator (Phase 9).

Fails if a documented top-level key (or nested shape) disappears from
build_template_context. See docs/template_map.md.
"""
from __future__ import annotations

from pathlib import Path

from docxtpl import DocxTemplate

from app.schemas.merge import (
    Flag,
    FlagType,
    MergedAP,
    MergedAPStatus,
    MergedJob,
    MergedPhotoRef,
    MergedPhotoSlots,
)
from app.schemas.survey import SurveyAP, SurveyRadio
from app.services.generator.context import build_template_context
from app.services.generator.types import AttachmentInput, BrandingConfig

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates_docx" / "survey_report.docx"
FIXTURES = Path(__file__).parent / "fixtures"
PHOTO_CLOSE = FIXTURES / "gen_photo_close.png"
PHOTO_FAR = FIXTURES / "gen_photo_far.png"

# Frozen top-level keys from docs/template_map.md
TOP_LEVEL_KEYS = frozenset(
    {
        "company_name",
        "primary_color",
        "logo",
        "job_name",
        "project_name",
        "survey_type",
        "location_vertical",
        "band_plan",
        "site_metadata",
        "success_criteria",
        "exec_summary",
        "scope_methodology",
        "findings",
        "ap_count",
        "override_count",
        "aps",
        "attachments",
        "overrides",
        "has_overrides",
    },
)

SUCCESS_CRITERIA_KEYS = frozenset(
    {
        "profile_key",
        "label",
        "min_rssi_dbm",
        "min_snr_db",
        "min_data_rate_mbps",
        "max_co_channel_aps",
        "is_override",
    },
)

AP_KEYS = frozenset(
    {
        "name",
        "model",
        "vendor",
        "floor",
        "x",
        "y",
        "radios",
        "radios_summary",
        "status",
        "photo_close",
        "photo_far",
        "photo_close_label",
        "photo_far_label",
    },
)

ATTACHMENT_KEYS = frozenset({"filename", "image", "is_image"})
OVERRIDE_KEYS = frozenset({"ap_name", "type_label", "detail", "reason"})


def _ensure_photos() -> None:
    if not PHOTO_CLOSE.exists():
        from tests.fixtures.build_gen_photos import MINIMAL_PNG

        PHOTO_CLOSE.write_bytes(MINIMAL_PNG)
        PHOTO_FAR.write_bytes(MINIMAL_PNG)


def _merged() -> MergedJob:
    return MergedJob(
        aps=[
            MergedAP(
                ap_name="AP-01-NE",
                survey_data=SurveyAP(
                    name="AP-01-NE",
                    model="C9136I",
                    vendor="Cisco",
                    floor_id="fp1",
                    x=1.0,
                    y=2.0,
                    radios=[SurveyRadio(band="5GHz", channel=36, tx_power=17.0)],
                ),
                photos=MergedPhotoSlots(
                    close=MergedPhotoRef(photo_id=1, original_filename="close.png"),
                    far=MergedPhotoRef(photo_id=2, original_filename="far.png"),
                ),
                status=MergedAPStatus.MATCHED,
            ),
        ],
        flags=[
            Flag(
                ap_name="AP-02",
                type=FlagType.MISSING_PHOTO,
                detail="Missing far",
                override_reason="Ceiling access denied",
            ),
        ],
    )


def _attachments(tmp_path: Path) -> list[AttachmentInput]:
    from tests.fixtures.build_gen_photos import MINIMAL_PNG

    path = tmp_path / "idf.png"
    path.write_bytes(MINIMAL_PNG)
    return [
        AttachmentInput(
            attachment_id=1,
            filename="idf.png",
            path=path,
            content_type="image/png",
        ),
    ]


def test_context_contract_top_level_and_nested(tmp_path: Path) -> None:
    _ensure_photos()
    tpl = DocxTemplate(str(TEMPLATE))
    ctx = build_template_context(
        tpl,
        _merged(),
        branding=BrandingConfig(
            company_name="Test Co",
            logo_path=None,
            primary_color="#1F4E79",
        ),
        job_name="Job",
        project_name="Project",
        floor_name_for=lambda _fid: "Floor 1",
        photo_paths={1: PHOTO_CLOSE, 2: PHOTO_FAR},
        attachments=_attachments(tmp_path),
        location_vertical="warehouse",
        survey_type="validation",
        band_plan="5GHz primary",
        site_metadata="Building A",
    )

    missing = TOP_LEVEL_KEYS - set(ctx)
    assert not missing, f"Missing top-level context keys: {sorted(missing)}"

    criteria = ctx["success_criteria"]
    assert isinstance(criteria, dict)
    missing_sc = SUCCESS_CRITERIA_KEYS - set(criteria)
    assert not missing_sc, f"Missing success_criteria keys: {sorted(missing_sc)}"
    assert criteria["profile_key"] == "warehouse"
    assert criteria["min_rssi_dbm"] == -67

    assert isinstance(ctx["aps"], list) and ctx["aps"]
    missing_ap = AP_KEYS - set(ctx["aps"][0])
    assert not missing_ap, f"Missing ap keys: {sorted(missing_ap)}"

    assert isinstance(ctx["attachments"], list) and ctx["attachments"]
    missing_att = ATTACHMENT_KEYS - set(ctx["attachments"][0])
    assert not missing_att, f"Missing attachment keys: {sorted(missing_att)}"

    assert isinstance(ctx["overrides"], list) and ctx["overrides"]
    missing_ov = OVERRIDE_KEYS - set(ctx["overrides"][0])
    assert not missing_ov, f"Missing override keys: {sorted(missing_ov)}"

    assert ctx["ap_count"] == 1
    assert ctx["override_count"] == 1
    assert ctx["has_overrides"] is True
    assert isinstance(ctx["exec_summary"], str) and ctx["exec_summary"]
    assert isinstance(ctx["scope_methodology"], str) and ctx["scope_methodology"]
    assert isinstance(ctx["findings"], str) and ctx["findings"]
