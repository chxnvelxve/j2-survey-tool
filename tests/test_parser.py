"""Unit tests for the .esx parser."""
from __future__ import annotations

import json
import zipfile
from io import BytesIO
from pathlib import Path

import pytest

from app.services.parser.errors import ParseError
from app.services.parser.parser import parse_esx

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE_ESX = FIXTURES / "sample_survey.esx"


@pytest.fixture
def sample_esx_path() -> Path:
    return SAMPLE_ESX


def _build_esx(files: dict[str, str | bytes]) -> BytesIO:
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            if isinstance(content, str):
                zf.writestr(name, content)
            else:
                zf.writestr(name, content)
    buf.seek(0)
    return buf


def test_parse_sample_fixture_happy_path(sample_esx_path: Path) -> None:
    with sample_esx_path.open("rb") as f:
        survey = parse_esx(f, source_name="sample_survey.esx")

    assert survey.project.name == "Test Building Survey"
    assert len(survey.floors) == 1
    assert survey.floors[0].name == "Floor 1"
    assert len(survey.aps) == 2
    assert survey.aps[0].name == "AP-01-NE"
    assert survey.aps[0].model == "C9136I"
    assert survey.aps[0].floor_id == "fp1"
    assert survey.aps[0].radios[0].band == "5GHz"
    assert survey.aps[0].radios[0].channel == 36


def test_ap_name_preserved_exactly(sample_esx_path: Path) -> None:
    with sample_esx_path.open("rb") as f:
        survey = parse_esx(f, source_name="sample_survey.esx")

    assert survey.aps[1].name == " AP-02-SW "


def test_missing_access_points_json_raises() -> None:
    buf = _build_esx(
        {
            "project.json": json.dumps({"name": "P"}),
            "floorPlans.json": json.dumps([]),
        },
    )
    with pytest.raises(ParseError, match="Missing required file accessPoints.json"):
        parse_esx(buf, source_name="bad.esx")


def test_missing_ap_name_raises() -> None:
    buf = _build_esx(
        {
            "project.json": json.dumps({"name": "P"}),
            "floorPlans.json": json.dumps([]),
            "accessPoints.json": json.dumps([{"model": "X"}]),
        },
    )
    with pytest.raises(ParseError, match="missing required string key 'name'"):
        parse_esx(buf, source_name="bad.esx")


def test_non_zip_raises() -> None:
    buf = BytesIO(b"not a zip file")
    with pytest.raises(ParseError, match="Not a valid ZIP archive"):
        parse_esx(buf, source_name="fake.esx")


def test_phase1_placeholder_raises_helpful_message() -> None:
    buf = BytesIO(b"# sample.esx\n# placeholder for upload testing\n")
    with pytest.raises(ParseError, match="Phase 1 upload placeholder"):
        parse_esx(buf, source_name="sample.esx")


def test_empty_file_raises() -> None:
    buf = BytesIO(b"")
    with pytest.raises(ParseError, match="Empty file"):
        parse_esx(buf, source_name="empty.esx")
