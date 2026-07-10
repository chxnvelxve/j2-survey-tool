"""Unit tests for the merge stage."""
from __future__ import annotations

from pathlib import Path

from app.models.enums import PhotoShotType
from app.schemas.merge import FlagType, MergedAPStatus, MergePhotoInput
from app.schemas.survey import SurveyAP, SurveyModel, SurveyProject
from app.services.merge.merge import merge
from app.services.parser.parser import parse_esx

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE_ESX = FIXTURES / "sample_survey.esx"


def _survey(
    aps: list[SurveyAP],
    *,
    source_filename: str = "floor1.esx",
) -> SurveyModel:
    return SurveyModel(
        project=SurveyProject(name="Test"),
        floors=[],
        aps=aps,
        source_filename=source_filename,
    )


def _ap(name: str, *, model: str | None = "C9136I") -> SurveyAP:
    return SurveyAP(name=name, model=model)


def _photo(
    photo_id: int,
    ap_name: str,
    shot_type: PhotoShotType,
    *,
    filename: str | None = None,
) -> MergePhotoInput:
    return MergePhotoInput(
        photo_id=photo_id,
        ap_name=ap_name,
        shot_type=shot_type,
        original_filename=filename or f"{ap_name}_{shot_type.value}.jpg",
    )


def test_exact_match() -> None:
    surveys = [
        _survey(
            [
                _ap("AP-01-NE"),
                _ap("AP-02-SW", model="MR46"),
            ],
        ),
    ]
    photos = [
        _photo(1, "AP-01-NE", PhotoShotType.CLOSE),
        _photo(2, "AP-01-NE", PhotoShotType.FAR),
        _photo(3, "AP-02-SW", PhotoShotType.CLOSE),
        _photo(4, "AP-02-SW", PhotoShotType.FAR),
    ]

    result = merge(surveys, photos)

    assert len(result.aps) == 2
    assert all(ap.status == MergedAPStatus.MATCHED for ap in result.aps)
    assert result.flags == []


def test_missing_photo() -> None:
    surveys = [_survey([_ap("AP-01-NE")])]
    photos = [_photo(1, "AP-01-NE", PhotoShotType.CLOSE)]

    result = merge(surveys, photos)

    assert len(result.aps) == 1
    assert result.aps[0].status == MergedAPStatus.INCOMPLETE
    assert result.aps[0].photos.close is not None
    assert result.aps[0].photos.far is None
    assert len(result.flags) == 1
    assert result.flags[0].type == FlagType.MISSING_PHOTO
    assert result.flags[0].ap_name == "AP-01-NE"
    assert "far" in result.flags[0].detail


def test_cross_file_disagreement() -> None:
    surveys = [
        _survey([_ap("AP-01-NE", model="C9136I")], source_filename="floor1.esx"),
        _survey([_ap("AP-01-NE", model="MR46")], source_filename="floor2.esx"),
    ]
    photos = [
        _photo(1, "AP-01-NE", PhotoShotType.CLOSE),
        _photo(2, "AP-01-NE", PhotoShotType.FAR),
    ]

    result = merge(surveys, photos)

    assert len(result.aps) == 1
    assert result.aps[0].status == MergedAPStatus.FLAGGED
    cross_flags = [f for f in result.flags if f.type == FlagType.CROSS_FILE_DISAGREEMENT]
    assert len(cross_flags) == 1
    assert cross_flags[0].ap_name == "AP-01-NE"
    assert "floor1.esx" in cross_flags[0].detail
    assert "floor2.esx" in cross_flags[0].detail


def test_name_mismatch() -> None:
    surveys = [_survey([_ap("AP-01-NE")])]
    photos = [_photo(1, "ap-01-ne", PhotoShotType.CLOSE)]

    result = merge(surveys, photos)

    assert result.aps[0].photos.close is None
    assert len(result.flags) == 2
    name_flags = [f for f in result.flags if f.type == FlagType.NAME_MISMATCH]
    assert len(name_flags) == 1
    assert name_flags[0].ap_name == "ap-01-ne"
    assert "capitalization" in name_flags[0].detail.lower()
    missing_flags = [f for f in result.flags if f.type == FlagType.MISSING_PHOTO]
    assert len(missing_flags) == 1


def test_orphan_photo() -> None:
    surveys = [_survey([_ap("AP-01-NE")])]
    photos = [_photo(1, "AP-UNKNOWN", PhotoShotType.CLOSE)]

    result = merge(surveys, photos)

    orphan_flags = [f for f in result.flags if f.type == FlagType.ORPHAN_PHOTO]
    assert len(orphan_flags) == 1
    assert orphan_flags[0].ap_name == "AP-UNKNOWN"


def test_whitespace_name_preserved() -> None:
    surveys = [_survey([_ap(" AP-02-SW ", model="MR46")])]
    photos_exact = [
        _photo(1, " AP-02-SW ", PhotoShotType.CLOSE),
        _photo(2, " AP-02-SW ", PhotoShotType.FAR),
    ]

    result = merge(surveys, photos_exact)
    assert result.aps[0].status == MergedAPStatus.MATCHED
    assert result.aps[0].photos.close is not None

    photos_stripped = [_photo(3, "AP-02-SW", PhotoShotType.CLOSE)]
    result_stripped = merge(surveys, photos_stripped)
    assert result_stripped.aps[0].photos.close is None
    name_flags = [f for f in result_stripped.flags if f.type == FlagType.NAME_MISMATCH]
    assert len(name_flags) == 1
    assert "spaces" in name_flags[0].detail.lower() or "space" in name_flags[0].detail.lower()


def test_sample_esx_integration() -> None:
    with SAMPLE_ESX.open("rb") as f:
        survey = parse_esx(f, source_name="sample_survey.esx")

    photos = [
        _photo(1, "AP-01-NE", PhotoShotType.CLOSE),
        _photo(2, "AP-01-NE", PhotoShotType.FAR),
        _photo(3, " AP-02-SW ", PhotoShotType.CLOSE),
        _photo(4, " AP-02-SW ", PhotoShotType.FAR),
    ]

    result = merge([survey], photos)

    assert len(result.aps) == 4
    matched = [ap for ap in result.aps if ap.status == MergedAPStatus.MATCHED]
    assert len(matched) == 2
    assert {ap.ap_name for ap in matched} == {"AP-01-NE", " AP-02-SW "}
    assert len(result.flags) == 2
