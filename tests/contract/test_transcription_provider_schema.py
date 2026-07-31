import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

PROJECT_ROOT = Path(__file__).parents[2]
SCHEMA_PATH = PROJECT_ROOT / "contracts" / "transcription-provider-v1.schema.json"
EXAMPLES_PATH = PROJECT_ROOT / "contracts" / "examples"


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value: dict[str, Any] = json.load(stream)
    return value


@pytest.mark.contract
def test_schema_is_valid_draft_2020_12() -> None:
    Draft202012Validator.check_schema(load_json(SCHEMA_PATH))


@pytest.mark.contract
@pytest.mark.parametrize("example", sorted(EXAMPLES_PATH.glob("*.json")))
def test_approved_examples_match_provider_schema(example: Path) -> None:
    Draft202012Validator(load_json(SCHEMA_PATH)).validate(load_json(example))


@pytest.mark.contract
def test_schema_rejects_unknown_fields_that_could_leak_data() -> None:
    result = load_json(EXAMPLES_PATH / "transcription-success.json")
    result["source_path"] = "C:/sensitive/video.mp4"
    assert list(Draft202012Validator(load_json(SCHEMA_PATH)).iter_errors(result))
