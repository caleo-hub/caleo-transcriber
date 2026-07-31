import json
import re
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

PROJECT_ROOT = Path(__file__).parents[2]
CONTRACTS = PROJECT_ROOT / "contracts"
EXAMPLES = CONTRACTS / "examples"
FEATURES = PROJECT_ROOT / "specs" / "features"


def _load(path: Path) -> dict[str, Any]:
    value: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return value


@pytest.mark.contract
@pytest.mark.parametrize(
    ("schema_name", "example_name"),
    [
        ("long-media-checkpoint-v1.schema.json", "long-media-checkpoint.json"),
        ("batch-queue-event-v1.schema.json", "batch-queue-event.json"),
    ],
)
def test_increment_2_schemas_and_examples_are_valid(schema_name: str, example_name: str) -> None:
    schema = _load(CONTRACTS / schema_name)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(_load(EXAMPLES / example_name))


@pytest.mark.contract
def test_checkpoint_manifest_cannot_contain_sensitive_payload_fields() -> None:
    schema = _load(CONTRACTS / "long-media-checkpoint-v1.schema.json")
    manifest = _load(EXAMPLES / "long-media-checkpoint.json")
    manifest["source_path"] = "C:/private/video.mp4"

    assert list(Draft202012Validator(schema).iter_errors(manifest))
    serialized = json.dumps(_load(EXAMPLES / "long-media-checkpoint.json")).lower()
    for forbidden in ("source_path", "audio_path", "transcript", '"text"', "private"):
        assert forbidden not in serialized


@pytest.mark.contract
def test_checkpoint_result_reference_only_exists_for_confirmed_chunk() -> None:
    schema = _load(CONTRACTS / "long-media-checkpoint-v1.schema.json")
    manifest = _load(EXAMPLES / "long-media-checkpoint.json")
    manifest["chunks"][1]["result_ref"] = "chunk-1.dpapi"

    assert list(Draft202012Validator(schema).iter_errors(manifest))


@pytest.mark.contract
def test_batch_event_failure_matches_terminal_state() -> None:
    schema = _load(CONTRACTS / "batch-queue-event-v1.schema.json")
    event = _load(EXAMPLES / "batch-queue-event.json")
    validator = Draft202012Validator(schema)

    validator.validate(event)
    event["state"] = "completed"
    assert list(validator.iter_errors(event))


@pytest.mark.contract
@pytest.mark.parametrize(
    ("spec_name", "vectors_name", "prefix"),
    [
        ("FEAT-002-long-media.md", "long-media-cases.json", "LM-CA-"),
        ("FEAT-003-batch-processing.md", "batch-queue-cases.json", "BATCH-CA-"),
    ],
)
def test_every_acceptance_criterion_has_a_versioned_oracle(
    spec_name: str, vectors_name: str, prefix: str
) -> None:
    spec = (FEATURES / spec_name).read_text(encoding="utf-8")
    criteria = set(re.findall(rf"{prefix}\d{{3}}", spec))
    vectors = _load(EXAMPLES / vectors_name)

    assert criteria
    assert set(vectors["acceptance_coverage"]) == criteria


@pytest.mark.contract
def test_long_media_boundary_and_resume_oracles_are_conservative() -> None:
    cases = {case["id"]: case for case in _load(EXAMPLES / "long-media-cases.json")["cases"]}

    under = cases["duration-30m01-under-bytes"]
    over = cases["duration-under-30m-over-bytes"]
    ambiguous = cases["resume-ambiguous-upload"]
    assert under["duration_ms"] > 30 * 60 * 1000
    assert under["prepared_bytes"] < 24_000_000
    assert under["expected_request_count"] == 1
    assert over["duration_ms"] < 30 * 60 * 1000
    assert over["prepared_bytes"] >= 24_000_000
    assert over["expected_request_count"] > 1
    assert ambiguous["automatic_upload_ids"] == []


@pytest.mark.contract
def test_batch_oracle_retries_only_failures_and_never_more_than_one_active() -> None:
    cases = {case["id"]: case for case in _load(EXAMPLES / "batch-queue-cases.json")["cases"]}
    retry = cases["retry-only-failures"]
    active = cases["one-active-item"]

    failed_positions = [index for index, state in enumerate(retry["initial"]) if state == "failed"]
    assert retry["expected_requeued_positions"] == failed_positions
    assert (
        sum(state in {"preparing", "transcribing", "saving"} for state in active["observed"]) == 1
    )
    assert active["expected_active_count"] == 1
