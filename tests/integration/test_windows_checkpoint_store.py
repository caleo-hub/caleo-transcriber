from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from caleo_transcriber.adapters.filesystem.checkpoints import (
    CheckpointCorrupt,
    DpapiProtector,
    WindowsCheckpointStore,
    fingerprint_source,
    hash_parameters,
)
from caleo_transcriber.application.checkpoints import (
    CheckpointChunk,
    ChunkCheckpointState,
    LongMediaCheckpoint,
)

ATTEMPT_ID = "12345678-1234-1234-1234-123456789abc"
CANARY_TEXT = b"transcricao pessoal que nao pode aparecer no manifesto"


def _checkpoint(now: datetime, state: ChunkCheckpointState) -> LongMediaCheckpoint:
    return LongMediaCheckpoint(
        attempt_id=ATTEMPT_ID,
        source_fingerprint="a" * 64,
        parameters_hash="b" * 64,
        created_at=now,
        expires_at=now + timedelta(days=7),
        chunks=(
            CheckpointChunk(
                id=0,
                start_ms=0,
                end_ms=10_000,
                state=state,
                attempts=1,
                result_ref="chunk-0.dpapi" if state is ChunkCheckpointState.CONFIRMED else None,
            ),
        ),
    )


@pytest.mark.integration
def test_dpapi_roundtrip_and_manifest_contains_no_content_or_path(tmp_path: Path) -> None:
    now = datetime(2026, 7, 31, tzinfo=UTC)
    store = WindowsCheckpointStore(tmp_path, DpapiProtector())
    checkpoint = _checkpoint(now, ChunkCheckpointState.CONFIRMED)

    store.save_result(ATTEMPT_ID, 0, CANARY_TEXT)
    store.save(checkpoint)

    manifest = (tmp_path / ATTEMPT_ID / "manifest.json").read_bytes()
    protected = (tmp_path / ATTEMPT_ID / "chunk-0.dpapi").read_bytes()
    assert CANARY_TEXT not in manifest
    assert CANARY_TEXT not in protected
    assert b"source_path" not in manifest
    assert b"audio_path" not in manifest
    assert store.load_result(ATTEMPT_ID, 0) == CANARY_TEXT


@pytest.mark.integration
def test_loading_interrupted_upload_marks_it_ambiguous(tmp_path: Path) -> None:
    now = datetime(2026, 7, 31, tzinfo=UTC)
    store = WindowsCheckpointStore(tmp_path, DpapiProtector())
    store.save(_checkpoint(now, ChunkCheckpointState.UPLOADING))

    recovered = store.load_matching("a" * 64, "b" * 64, now)

    assert recovered is not None
    assert recovered.chunks[0].state is ChunkCheckpointState.AMBIGUOUS


@pytest.mark.integration
def test_tampered_protected_result_fails_closed(tmp_path: Path) -> None:
    store = WindowsCheckpointStore(tmp_path, DpapiProtector())
    store.save_result(ATTEMPT_ID, 0, CANARY_TEXT)
    result_path = tmp_path / ATTEMPT_ID / "chunk-0.dpapi"
    payload = bytearray(result_path.read_bytes())
    payload[len(payload) // 2] ^= 0x01
    result_path.write_bytes(payload)

    with pytest.raises(CheckpointCorrupt):
        store.load_result(ATTEMPT_ID, 0)


@pytest.mark.integration
def test_expired_checkpoint_is_removed(tmp_path: Path) -> None:
    now = datetime(2026, 7, 31, tzinfo=UTC)
    store = WindowsCheckpointStore(tmp_path, DpapiProtector())
    expired = _checkpoint(now - timedelta(days=8), ChunkCheckpointState.FAILED)
    store.save(expired)

    assert store.load_matching("a" * 64, "b" * 64, now) is None
    assert not (tmp_path / ATTEMPT_ID).exists()


@pytest.mark.integration
def test_source_fingerprint_and_parameter_hash_change_with_inputs(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    source.write_bytes(b"a" * 1024)
    first = fingerprint_source(source)
    source.write_bytes(b"b" * 1024)
    second = fingerprint_source(source)

    assert first != second
    assert hash_parameters({"format": "txt"}) != hash_parameters({"format": "srt"})
