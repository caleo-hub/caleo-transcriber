import pytest

from caleo_transcriber.domain.long_media import (
    MAX_UPLOAD_BYTES,
    OVERLAP_MS,
    ChunkPlan,
    ChunkTranscript,
    InvalidChunkPlan,
    TimedText,
    merge_transcripts,
    plan_chunks,
    validate_plan,
)


def test_duration_above_thirty_minutes_uses_one_request_when_under_byte_limit() -> None:
    plan = plan_chunks(duration_ms=1_801_000, prepared_bytes=MAX_UPLOAD_BYTES - 1)

    assert plan == (ChunkPlan(0, 0, 1_801_000),)


def test_media_below_thirty_minutes_is_split_when_it_reaches_byte_limit() -> None:
    plan = plan_chunks(duration_ms=1_200_000, prepared_bytes=MAX_UPLOAD_BYTES)

    assert len(plan) == 2
    assert plan[0].start_ms == 0
    assert plan[-1].end_ms == 1_200_000
    assert plan[1].start_ms == plan[0].end_ms - OVERLAP_MS


def test_closest_silence_is_selected_near_estimated_boundary() -> None:
    plan = plan_chunks(
        duration_ms=3_000_000,
        prepared_bytes=30_000_000,
        silence_points_ms=(1_980_000, 2_005_000, 2_012_000),
    )

    assert plan[0].end_ms == 2_005_000
    assert plan[1].start_ms == 2_005_000 - OVERLAP_MS


def test_plan_covers_timeline_without_gaps_and_with_exact_overlap() -> None:
    plan = plan_chunks(duration_ms=7_200_000, prepared_bytes=72_000_000)

    validate_plan(plan, duration_ms=7_200_000)
    assert plan[0].start_ms == 0
    assert plan[-1].end_ms == 7_200_000
    assert all(
        current.start_ms == previous.end_ms - OVERLAP_MS
        for previous, current in zip(plan, plan[1:], strict=False)
    )


def test_validate_plan_rejects_a_gap() -> None:
    plan = (ChunkPlan(0, 0, 10_000), ChunkPlan(1, 11_000, 20_000))

    with pytest.raises(InvalidChunkPlan):
        validate_plan(plan, duration_ms=20_000)


def test_merge_offsets_local_timestamps_to_original_timeline() -> None:
    chunks = (
        ChunkTranscript(
            ChunkPlan(0, 0, 10_000),
            (TimedText(1_000, 4_000, "Primeiro trecho"),),
        ),
        ChunkTranscript(
            ChunkPlan(1, 8_000, 18_000),
            (TimedText(3_000, 6_000, "Segundo trecho"),),
        ),
    )

    assert merge_transcripts(chunks) == (
        TimedText(1_000, 4_000, "Primeiro trecho"),
        TimedText(11_000, 14_000, "Segundo trecho"),
    )


def test_merge_removes_phrase_duplicated_inside_overlap() -> None:
    chunks = (
        ChunkTranscript(
            ChunkPlan(0, 0, 10_000),
            (TimedText(6_000, 10_000, "Vamos revisar o próximo capítulo agora"),),
        ),
        ChunkTranscript(
            ChunkPlan(1, 8_000, 18_000),
            (TimedText(0, 5_000, "o próximo capítulo agora com exemplos"),),
        ),
    )

    assert merge_transcripts(chunks) == (
        TimedText(6_000, 10_000, "Vamos revisar o próximo capítulo agora"),
        TimedText(10_000, 13_000, "com exemplos"),
    )


def test_merge_preserves_legitimate_repetition_outside_overlap() -> None:
    chunks = (
        ChunkTranscript(
            ChunkPlan(0, 0, 10_000),
            (TimedText(1_000, 4_000, "sim sim sim"),),
        ),
        ChunkTranscript(
            ChunkPlan(1, 8_000, 18_000),
            (TimedText(4_000, 7_000, "sim sim sim"),),
        ),
    )

    assert [segment.text for segment in merge_transcripts(chunks)] == [
        "sim sim sim",
        "sim sim sim",
    ]
