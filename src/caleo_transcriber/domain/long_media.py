"""Planejamento e recomposição determinísticos, sem efeitos externos."""

import re
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass

MAX_UPLOAD_BYTES = 24_000_000
TARGET_CHUNK_BYTES = 20_000_000
OVERLAP_MS = 2_000
SILENCE_SEARCH_MS = 15_000
_WORD = re.compile(r"\w+", re.UNICODE)


class InvalidChunkPlan(ValueError):
    """Indica lacuna, inversão ou intervalo inválido no plano."""


@dataclass(frozen=True, slots=True)
class ChunkPlan:
    id: int
    start_ms: int
    end_ms: int

    def __post_init__(self) -> None:
        if self.id < 0 or self.start_ms < 0 or self.end_ms <= self.start_ms:
            raise InvalidChunkPlan("Invalid chunk interval")


@dataclass(frozen=True, slots=True)
class TimedText:
    start_ms: int
    end_ms: int
    text: str

    def __post_init__(self) -> None:
        if self.start_ms < 0 or self.end_ms <= self.start_ms:
            raise InvalidChunkPlan("Invalid transcript interval")


@dataclass(frozen=True, slots=True)
class ChunkTranscript:
    plan: ChunkPlan
    segments: tuple[TimedText, ...]


def plan_chunks(
    *,
    duration_ms: int,
    prepared_bytes: int,
    silence_points_ms: Sequence[int] = (),
) -> tuple[ChunkPlan, ...]:
    if duration_ms <= 0 or prepared_bytes <= 0:
        raise InvalidChunkPlan("Duration and size must be positive")
    if prepared_bytes < MAX_UPLOAD_BYTES:
        return (ChunkPlan(0, 0, duration_ms),)

    estimated_duration = max(
        OVERLAP_MS + 1,
        (duration_ms * TARGET_CHUNK_BYTES) // prepared_bytes,
    )
    silences = tuple(sorted(point for point in silence_points_ms if 0 < point < duration_ms))
    chunks: list[ChunkPlan] = []
    start_ms = 0
    while start_ms < duration_ms:
        target_end = min(duration_ms, start_ms + estimated_duration)
        if target_end == duration_ms:
            end_ms = duration_ms
        else:
            candidates = [
                point
                for point in silences
                if abs(point - target_end) <= SILENCE_SEARCH_MS and point > start_ms + OVERLAP_MS
            ]
            end_ms = (
                min(candidates, key=lambda point: (abs(point - target_end), point))
                if candidates
                else target_end
            )
        chunks.append(ChunkPlan(len(chunks), start_ms, end_ms))
        if end_ms == duration_ms:
            break
        next_start = end_ms - OVERLAP_MS
        if next_start <= start_ms:
            raise InvalidChunkPlan("Chunk planner did not advance")
        start_ms = next_start

    result = tuple(chunks)
    validate_plan(result, duration_ms=duration_ms)
    return result


def validate_plan(plan: Sequence[ChunkPlan], *, duration_ms: int) -> None:
    if not plan or duration_ms <= 0:
        raise InvalidChunkPlan("Plan must cover a positive duration")
    if plan[0].id != 0 or plan[0].start_ms != 0 or plan[-1].end_ms != duration_ms:
        raise InvalidChunkPlan("Plan does not cover the complete timeline")
    for expected_id, chunk in enumerate(plan):
        if chunk.id != expected_id or chunk.end_ms > duration_ms:
            raise InvalidChunkPlan("Chunk order is invalid")
    for previous, current in zip(plan, plan[1:], strict=False):
        expected_start = max(0, previous.end_ms - OVERLAP_MS)
        if current.start_ms != expected_start:
            raise InvalidChunkPlan("Chunk overlap is invalid")


def merge_transcripts(chunks: Sequence[ChunkTranscript]) -> tuple[TimedText, ...]:
    if not chunks:
        return ()
    plans = tuple(chunk.plan for chunk in chunks)
    validate_plan(plans, duration_ms=plans[-1].end_ms)

    merged: list[TimedText] = []
    for chunk in chunks:
        previous_local_start = -1
        for local in chunk.segments:
            if (
                local.start_ms < previous_local_start
                or local.end_ms > chunk.plan.end_ms - chunk.plan.start_ms
            ):
                raise InvalidChunkPlan("Local transcript is outside its chunk")
            previous_local_start = local.start_ms
            candidate = TimedText(
                chunk.plan.start_ms + local.start_ms,
                chunk.plan.start_ms + local.end_ms,
                local.text,
            )
            _append_conservative(merged, candidate)
    return tuple(merged)


def _append_conservative(merged: list[TimedText], candidate: TimedText) -> None:
    if not merged:
        merged.append(candidate)
        return
    previous = merged[-1]
    if candidate.start_ms >= previous.end_ms:
        merged.append(candidate)
        return

    remaining = _remove_shared_phrase(previous.text, candidate.text)
    if candidate.end_ms <= previous.end_ms or not remaining:
        return
    merged.append(TimedText(previous.end_ms, candidate.end_ms, remaining))


def _remove_shared_phrase(left: str, right: str) -> str:
    left_tokens = [_normalized(match.group()) for match in _WORD.finditer(left)]
    right_matches = list(_WORD.finditer(right))
    right_tokens = [_normalized(match.group()) for match in right_matches]
    maximum = min(12, len(left_tokens), len(right_tokens))
    for count in range(maximum, 2, -1):
        if left_tokens[-count:] == right_tokens[:count]:
            return right[right_matches[count - 1].end() :].lstrip(" \t\r\n,.;:!?—–-")
    return right


def _normalized(token: str) -> str:
    return unicodedata.normalize("NFKC", token).casefold()
