"""Unit tests for flag resolution service."""
from __future__ import annotations

import pytest

from app.models.enums import JobStatus
from app.schemas.merge import Flag, FlagType, MergedJob
from app.services.job_flag_resolution import (
    FlagResolutionError,
    all_flags_resolved,
    apply_override_reasons,
    reasons_from_snapshots,
    status_after_resolution,
)


def _flag(ap_name: str, *, resolved: bool = False) -> Flag:
    return Flag(
        ap_name=ap_name,
        type=FlagType.MISSING_PHOTO,
        detail=f"Missing photos for {ap_name}",
        override_reason="Ceiling access denied" if resolved else None,
    )


def _merged(flags: list[Flag]) -> MergedJob:
    return MergedJob(flags=flags)


def test_all_flags_resolved_empty() -> None:
    assert all_flags_resolved(MergedJob()) is True


def test_all_flags_resolved_unresolved() -> None:
    flags = [_flag(f"AP-{i:02d}") for i in range(30)]
    assert all_flags_resolved(_merged(flags)) is False


def test_all_flags_resolved_all_overridden() -> None:
    flags = [_flag(f"AP-{i:02d}", resolved=True) for i in range(30)]
    assert all_flags_resolved(_merged(flags)) is True


def test_all_flags_resolved_partial() -> None:
    flags = [_flag("AP-01", resolved=True), _flag("AP-02")]
    assert all_flags_resolved(_merged(flags)) is False


def test_apply_override_reasons_bulk() -> None:
    flags = [_flag(f"AP-{i:02d}") for i in range(30)]
    merged = _merged(flags)
    indices = list(range(30))
    reason = "Ceiling access denied"

    result = apply_override_reasons(merged, indices, reason)

    assert len(result.flags) == 30
    assert all(f.override_reason == reason for f in result.flags)
    assert all(f.override_reason is None for f in merged.flags)


def test_apply_override_reasons_subset_unchanged() -> None:
    flags = [_flag(f"AP-{i:02d}") for i in range(5)]
    merged = _merged(flags)

    result = apply_override_reasons(merged, [0, 2], "Root cause A")

    assert result.flags[0].override_reason == "Root cause A"
    assert result.flags[1].override_reason is None
    assert result.flags[2].override_reason == "Root cause A"
    assert result.flags[3].override_reason is None


def test_apply_override_reasons_empty_reason() -> None:
    merged = _merged([_flag("AP-01")])
    with pytest.raises(FlagResolutionError, match="required"):
        apply_override_reasons(merged, [0], "   ")


def test_apply_override_reasons_no_selection() -> None:
    merged = _merged([_flag("AP-01")])
    with pytest.raises(FlagResolutionError, match="Select at least one"):
        apply_override_reasons(merged, [], "Reason")


def test_apply_override_reasons_out_of_range() -> None:
    merged = _merged([_flag("AP-01")])
    with pytest.raises(FlagResolutionError, match="Invalid flag index"):
        apply_override_reasons(merged, [5], "Reason")


def test_apply_override_reasons_already_resolved() -> None:
    merged = _merged([_flag("AP-01", resolved=True)])
    with pytest.raises(FlagResolutionError, match="already resolved"):
        apply_override_reasons(merged, [0], "New reason")


def test_status_after_resolution() -> None:
    assert status_after_resolution(MergedJob()) == JobStatus.FLAGS_RESOLVED
    assert status_after_resolution(_merged([_flag("AP-01")])) == JobStatus.MERGED
    resolved = _merged([_flag("AP-01", resolved=True)])
    assert status_after_resolution(resolved) == JobStatus.FLAGS_RESOLVED


def test_reasons_from_snapshots() -> None:
    snapshots = [
        {
            "aps": [],
            "flags": [
                {
                    "ap_name": "AP-01",
                    "type": "missing_photo",
                    "detail": "x",
                    "override_reason": "Ceiling access denied",
                },
                {
                    "ap_name": "AP-02",
                    "type": "missing_photo",
                    "detail": "y",
                    "override_reason": "AP swapped post-survey",
                },
            ],
        },
        {
            "aps": [],
            "flags": [
                {
                    "ap_name": "AP-03",
                    "type": "orphan_photo",
                    "detail": "z",
                    "override_reason": "Ceiling access denied",
                },
            ],
        },
        None,
    ]

    reasons = reasons_from_snapshots(snapshots)

    assert reasons == ["AP swapped post-survey", "Ceiling access denied"]


def test_reasons_from_snapshots_respects_limit() -> None:
    snapshots = [
        {
            "aps": [],
            "flags": [
                {
                    "ap_name": f"AP-{i}",
                    "type": "missing_photo",
                    "detail": "d",
                    "override_reason": f"Reason {i}",
                }
                for i in range(10)
            ],
        },
    ]
    reasons = reasons_from_snapshots(snapshots, limit=3)
    assert len(reasons) == 3
