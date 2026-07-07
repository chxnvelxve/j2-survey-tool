"""Merge stage: [SurveyModel] + photos -> MergedJob + flags.
See .cursor/skills/photo-matching/SKILL.md.

Phase 3. Exact-name join. Hard-fail: flag mismatches, never silently merge.
Runs on manual push only.
"""
from __future__ import annotations

from app.models.enums import PhotoShotType
from app.schemas.merge import (
    Flag,
    FlagType,
    MergedAP,
    MergedAPStatus,
    MergedJob,
    MergedPhotoRef,
    MergedPhotoSlots,
    MergePhotoInput,
)
from app.schemas.survey import SurveyAP, SurveyModel


def _ap_comparable(ap: SurveyAP) -> dict[str, object]:
    return {
        "model": ap.model,
        "vendor": ap.vendor,
        "floor_id": ap.floor_id,
        "x": ap.x,
        "y": ap.y,
        "radios": [r.model_dump() for r in ap.radios],
    }


def _cross_file_detail(entries: list[tuple[str, SurveyAP]]) -> str:
    names = [src for src, _ in entries]
    ap_label = entries[0][1].name
    fields: set[str] = set()
    baseline = _ap_comparable(entries[0][1])
    for _, ap in entries[1:]:
        current = _ap_comparable(ap)
        for key, value in current.items():
            if baseline.get(key) != value:
                fields.add(key)
    field_list = ", ".join(sorted(fields)) if fields else "metadata"
    return (
        f"The access point “{ap_label}” appears in multiple survey files ({', '.join(names)}) "
        f"with different {field_list}. A drafter must resolve the conflict."
    )


def _whitespace_only_match(photo_name: str, survey_names: set[str]) -> str | None:
    stripped = photo_name.strip()
    for name in survey_names:
        if name != photo_name and name.strip() == stripped:
            return name
    return None


def _case_only_match(photo_name: str, survey_names: set[str]) -> str | None:
    lowered = photo_name.casefold()
    for name in survey_names:
        if name != photo_name and name.casefold() == lowered:
            return name
    return None


def _space_position_note(name: str) -> str:
    """Plain-English note about leading/trailing spaces in a survey AP name."""
    parts: list[str] = []
    leading = len(name) - len(name.lstrip())
    trailing = len(name) - len(name.rstrip())
    if leading:
        parts.append(f"{leading} space{'s' if leading != 1 else ''} before the name")
    if trailing:
        parts.append(f"{trailing} space{'s' if trailing != 1 else ''} after the name")
    return " and ".join(parts)


def _whitespace_mismatch_detail(photo_name: str, survey_name: str) -> str:
    space_note = _space_position_note(survey_name)
    return (
        f"This photo was uploaded for “{photo_name}”, but the survey names this access "
        f"point “{survey_name}” ({space_note}). "
        f"Re-upload using the exact name from the Parsed access points table — "
        f"including any spaces at the start or end."
    )


def _case_mismatch_detail(photo_name: str, survey_name: str) -> str:
    return (
        f"This photo was uploaded for “{photo_name}”, but the survey lists "
        f"“{survey_name}”. The names are the same except for upper/lowercase letters. "
        f"Re-upload using the exact capitalization from the Parsed access points table."
    )


def _missing_photo_detail(ap_name: str, missing: list[str], photos: list[MergePhotoInput]) -> str:
    slots = " and ".join(missing)
    detail = (
        f"The survey access point “{ap_name}” is missing its {slots} photo(s). "
        f"No uploaded photo used that exact name."
    )
    for photo in photos:
        if photo.ap_name == ap_name:
            continue
        if _whitespace_only_match(photo.ap_name, {ap_name}) is not None:
            detail += (
                f" You uploaded a photo labeled “{photo.ap_name}”, which is the same name "
                f"except for extra spaces — copy “{ap_name}” exactly from the "
                f"Parsed access points table."
            )
            break
    return detail


def _orphan_photo_detail(photo: MergePhotoInput, survey_names: set[str]) -> str:
    ws_match = _whitespace_only_match(photo.ap_name, survey_names)
    if ws_match is not None:
        return _whitespace_mismatch_detail(photo.ap_name, ws_match)
    case_match = _case_only_match(photo.ap_name, survey_names)
    if case_match is not None:
        return _case_mismatch_detail(photo.ap_name, case_match)
    return (
        f"This photo was uploaded for “{photo.ap_name}”, but no access point with that "
        f"name exists in the survey file. Check the Parsed access points table and "
        f"re-upload with the exact name shown there."
    )


def merge(surveys: list[SurveyModel], photos: list[MergePhotoInput]) -> MergedJob:
    """Join photos to survey APs by exact name; surface all mismatches as flags."""
    by_name: dict[str, list[tuple[str, SurveyAP]]] = {}
    for survey in surveys:
        for ap in survey.aps:
            by_name.setdefault(ap.name, []).append((survey.source_filename, ap))

    survey_names = set(by_name.keys())
    flags: list[Flag] = []
    aps: list[MergedAP] = []

    photos_by_ap: dict[str, dict[PhotoShotType, MergePhotoInput]] = {}
    for photo in photos:
        photos_by_ap.setdefault(photo.ap_name, {})[photo.shot_type] = photo

    for ap_name in sorted(by_name.keys()):
        entries = by_name[ap_name]
        survey_data = entries[0][1]
        status = MergedAPStatus.MATCHED

        if len(entries) > 1:
            baseline = _ap_comparable(entries[0][1])
            disagrees = any(_ap_comparable(ap) != baseline for _, ap in entries[1:])
            if disagrees:
                flags.append(
                    Flag(
                        ap_name=ap_name,
                        type=FlagType.CROSS_FILE_DISAGREEMENT,
                        detail=_cross_file_detail(entries),
                    ),
                )
                status = MergedAPStatus.FLAGGED

        slots = MergedPhotoSlots()
        ap_photos = photos_by_ap.get(ap_name, {})
        if PhotoShotType.CLOSE in ap_photos:
            p = ap_photos[PhotoShotType.CLOSE]
            slots.close = MergedPhotoRef(photo_id=p.photo_id, original_filename=p.original_filename)
        if PhotoShotType.FAR in ap_photos:
            p = ap_photos[PhotoShotType.FAR]
            slots.far = MergedPhotoRef(photo_id=p.photo_id, original_filename=p.original_filename)

        missing: list[str] = []
        if slots.close is None:
            missing.append("close")
        if slots.far is None:
            missing.append("far")
        if missing:
            flags.append(
                Flag(
                    ap_name=ap_name,
                    type=FlagType.MISSING_PHOTO,
                    detail=_missing_photo_detail(ap_name, missing, photos),
                ),
            )
            if status != MergedAPStatus.FLAGGED:
                status = MergedAPStatus.INCOMPLETE

        aps.append(
            MergedAP(
                ap_name=ap_name,
                survey_data=survey_data,
                photos=slots,
                status=status,
            ),
        )

    for photo in photos:
        if photo.ap_name in survey_names:
            continue
        case_match = _case_only_match(photo.ap_name, survey_names)
        ws_match = _whitespace_only_match(photo.ap_name, survey_names)
        if ws_match is not None:
            flags.append(
                Flag(
                    ap_name=photo.ap_name,
                    type=FlagType.NAME_MISMATCH,
                    detail=_whitespace_mismatch_detail(photo.ap_name, ws_match),
                ),
            )
        elif case_match is not None:
            flags.append(
                Flag(
                    ap_name=photo.ap_name,
                    type=FlagType.NAME_MISMATCH,
                    detail=_case_mismatch_detail(photo.ap_name, case_match),
                ),
            )
        else:
            flags.append(
                Flag(
                    ap_name=photo.ap_name,
                    type=FlagType.ORPHAN_PHOTO,
                    detail=_orphan_photo_detail(photo, survey_names),
                ),
            )

    return MergedJob(aps=aps, flags=flags)
