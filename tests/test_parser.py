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
CLEAN_ESX = FIXTURES / "sample_survey_clean.esx"
EDGE_ESX = FIXTURES / "sample_survey_edge_cases.esx"
SAMPLE_ESX = FIXTURES / "sample_survey.esx"
DUP_A_ESX = FIXTURES / "sample_survey_dup_a.esx"
DUP_B_ESX = FIXTURES / "sample_survey_dup_b.esx"


@pytest.fixture
def clean_esx_path() -> Path:
    return CLEAN_ESX


@pytest.fixture
def edge_esx_path() -> Path:
    return EDGE_ESX


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


def test_parse_clean_fixture_happy_path(clean_esx_path: Path) -> None:
    with clean_esx_path.open("rb") as f:
        survey = parse_esx(f, source_name="sample_survey_clean.esx")

    assert survey.project.name == "Test Building Survey"
    assert len(survey.floors) == 1
    assert survey.floors[0].name == "Floor 1"
    assert survey.floors[0].heatmap_ref is None
    assert len(survey.aps) == 2
    assert survey.aps[0].name == "AP-01-NE"
    assert survey.aps[0].model == "C9136I"
    assert survey.aps[0].floor_id == "fp1"
    assert survey.aps[0].radios[0].band == "5GHz"
    assert survey.aps[0].radios[0].channel == 36
    assert survey.aps[1].name == "AP-02-SW"
    assert len(survey.aps[1].radios) == 1


def test_parse_edge_cases_fixture(edge_esx_path: Path) -> None:
    with edge_esx_path.open("rb") as f:
        survey = parse_esx(f, source_name="sample_survey_edge_cases.esx")

    assert survey.project.name == "Edge Case Survey"
    assert len(survey.aps) == 4
    assert survey.aps[1].name == " AP-02-SW "
    assert survey.aps[2].name == "AP-03-Café"


@pytest.mark.parametrize(
    ("fixture_path", "source_name", "expected_names"),
    [
        (
            CLEAN_ESX,
            "sample_survey_clean.esx",
            ["AP-01-NE", "AP-02-SW"],
        ),
        (
            EDGE_ESX,
            "sample_survey_edge_cases.esx",
            ["AP-01-NE", " AP-02-SW ", "AP-03-Café", "AP-04-NO-RADIO"],
        ),
    ],
)
def test_ap_name_preserved_exactly(
    fixture_path: Path,
    source_name: str,
    expected_names: list[str],
) -> None:
    with fixture_path.open("rb") as f:
        survey = parse_esx(f, source_name=source_name)

    assert [ap.name for ap in survey.aps] == expected_names


def test_missing_radio_ap_empty_radios(edge_esx_path: Path) -> None:
    with edge_esx_path.open("rb") as f:
        survey = parse_esx(f, source_name="sample_survey_edge_cases.esx")

    no_radio = next(ap for ap in survey.aps if ap.name == "AP-04-NO-RADIO")
    assert no_radio.radios == []


def test_heatmap_ref_parsed(edge_esx_path: Path) -> None:
    with edge_esx_path.open("rb") as f:
        survey = parse_esx(f, source_name="sample_survey_edge_cases.esx")

    assert survey.floors[0].heatmap_ref == "heatmap_fp1.png"


def test_sample_survey_alias_is_edge_cases(sample_esx_path: Path) -> None:
    with sample_esx_path.open("rb") as f:
        survey = parse_esx(f, source_name="sample_survey.esx")

    assert survey.project.name == "Edge Case Survey"
    assert survey.aps[1].name == " AP-02-SW "


@pytest.mark.parametrize(
    ("fixture_path", "source_name", "project_name"),
    [
        (DUP_A_ESX, "sample_survey_dup_a.esx", "Building A Survey"),
        (DUP_B_ESX, "sample_survey_dup_b.esx", "Building B Survey"),
    ],
)
def test_dup_fixtures_preserve_exact_ap_name(
    fixture_path: Path,
    source_name: str,
    project_name: str,
) -> None:
    with fixture_path.open("rb") as f:
        survey = parse_esx(f, source_name=source_name)

    assert survey.project.name == project_name
    assert [ap.name for ap in survey.aps] == ["AP-DUP-01"]


def test_schema_guard_unknown_project_key() -> None:
    buf = _build_esx(
        {
            "project.json": json.dumps({"name": "P", "unexpected": True}),
            "floorPlans.json": json.dumps([]),
            "accessPoints.json": json.dumps([]),
        },
    )
    with pytest.raises(ParseError, match=r"project\.json: unknown key\(s\)"):
        parse_esx(buf, source_name="bad.esx")


def test_schema_guard_unknown_ap_key() -> None:
    buf = _build_esx(
        {
            "project.json": json.dumps({"name": "P"}),
            "floorPlans.json": json.dumps([]),
            "accessPoints.json": json.dumps([{"name": "AP-1", "extraField": 1}]),
        },
    )
    with pytest.raises(ParseError, match=r"accessPoints\.json: unknown key\(s\)"):
        parse_esx(buf, source_name="bad.esx")


def test_schema_guard_known_fixtures_pass(
    clean_esx_path: Path,
    edge_esx_path: Path,
) -> None:
    for path, name in (
        (clean_esx_path, "sample_survey_clean.esx"),
        (edge_esx_path, "sample_survey_edge_cases.esx"),
    ):
        with path.open("rb") as f:
            survey = parse_esx(f, source_name=name)
        assert survey.project.name


def test_missing_access_points_json_raises() -> None:
    buf = _build_esx(
        {
            "project.json": json.dumps({"name": "P"}),
            "floorPlans.json": json.dumps([]),
        },
    )
    with pytest.raises(ParseError, match="missing required file accessPoints.json"):
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
