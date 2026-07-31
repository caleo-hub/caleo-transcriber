from pathlib import Path
from threading import Event, Thread

import pytest
from tests.fakes.transcription_workflow import (
    FakeAudioExtractor,
    FakeMediaProbe,
    FakePreparedAudioLease,
    FakeTranscriptionProvider,
    FakeTxtOutputWriter,
    RecordingAttemptEvents,
)

from caleo_transcriber.application import (
    AttemptFailure,
    MediaError,
    MediaFailure,
    MediaInfo,
    OutputWriteCancelled,
    OutputWriteError,
    PreparedAudio,
    ProviderFailure,
    TranscribeSingleFile,
    TranscribeSingleFileCommand,
    TranscribeSingleFileFailure,
    TranscribeSingleFileSuccess,
    TranscriptionAlreadyRunningError,
    TranscriptionFailure,
    TranscriptionSegment,
    TranscriptionSuccess,
)
from caleo_transcriber.domain import AttemptState

pytestmark = pytest.mark.acceptance
CANARY_SOURCE = Path("C:/private/aula pessoal.mp4")
CANARY_AUDIO = Path("C:/controlled-temp/audio.mp3")


def _success(text: str = "Texto sintético.") -> TranscriptionSuccess:
    return TranscriptionSuccess(
        text=text,
        detected_language="pt",
        duration_ms=1_000,
        segments=(TranscriptionSegment(0, 1_000, text),) if text else (),
        warnings=("no_speech_detected",) if not text else (),
    )


def _command(attempt_id: str = "attempt-1") -> TranscribeSingleFileCommand:
    return TranscribeSingleFileCommand(
        attempt_id,
        CANARY_SOURCE,
        Path("C:/chosen-output"),
        Path("C:/controlled-temp"),
    )


def _workflow(
    *,
    probe_result: MediaInfo | MediaError | None = None,
    provider_result: (
        TranscriptionSuccess
        | TranscriptionFailure
        | list[TranscriptionSuccess | TranscriptionFailure]
        | None
    ) = None,
    writer_result: Path | Exception = Path("C:/chosen-output/aula pessoal.txt"),
    enter_error: MediaError | None = None,
    before_provider_return: object = None,
) -> tuple[
    TranscribeSingleFile,
    FakeMediaProbe,
    FakeAudioExtractor,
    FakeTranscriptionProvider,
    FakeTxtOutputWriter,
    RecordingAttemptEvents,
]:
    info = probe_result or MediaInfo(1.0, "mov,mp4", True, True)
    lease = FakePreparedAudioLease(PreparedAudio(CANARY_AUDIO, 1.0, 1234), enter_error)
    probe = FakeMediaProbe(info)
    extractor = FakeAudioExtractor(lease)
    provider = FakeTranscriptionProvider(
        provider_result or _success(),
        before_provider_return if callable(before_provider_return) else None,
    )
    writer = FakeTxtOutputWriter(writer_result)
    events = RecordingAttemptEvents()
    return (
        TranscribeSingleFile(probe, extractor, provider, writer, events),
        probe,
        extractor,
        provider,
        writer,
        events,
    )


def test_ca_001_and_002_happy_path_sends_prepared_audio_and_creates_txt() -> None:
    use_case, _, extractor, provider, writer, events = _workflow()

    result = use_case.execute(_command())

    assert isinstance(result, TranscribeSingleFileSuccess)
    assert result.output_path.name == "aula pessoal.txt"
    assert [event.state for event in events.events] == [
        AttemptState.READY,
        AttemptState.PREPARING,
        AttemptState.TRANSCRIBING,
        AttemptState.SAVING,
        AttemptState.COMPLETED,
    ]
    assert provider.calls[0].audio_path == CANARY_AUDIO
    assert provider.calls[0].media_type == "audio/mpeg"
    assert provider.calls[0].size_bytes == 1234
    assert provider.calls[0].audio_path != CANARY_SOURCE
    assert writer.calls == [(Path("C:/chosen-output"), CANARY_SOURCE.name, "Texto sintético.")]
    assert extractor.lease.exited is True


@pytest.mark.parametrize(
    ("reason", "category"),
    [
        (MediaFailure.MISSING, AttemptFailure.INVALID_INPUT),
        (MediaFailure.EMPTY, AttemptFailure.INVALID_INPUT),
        (MediaFailure.CORRUPT, AttemptFailure.INVALID_INPUT),
        (MediaFailure.NO_AUDIO, AttemptFailure.INVALID_INPUT),
        (MediaFailure.INVALID_DURATION, AttemptFailure.INVALID_INPUT),
        (MediaFailure.DURATION_LIMIT, AttemptFailure.INVALID_INPUT),
        (MediaFailure.UNSUPPORTED, AttemptFailure.UNSUPPORTED_MEDIA),
    ],
)
def test_ca_004_invalid_input_never_reaches_provider(
    reason: MediaFailure, category: AttemptFailure
) -> None:
    use_case, _, extractor, provider, writer, events = _workflow(probe_result=MediaError(reason))

    result = use_case.execute(_command())

    assert isinstance(result, TranscribeSingleFileFailure)
    assert result.category is category
    assert result.state is AttemptState.FAILED
    assert extractor.calls == []
    assert provider.calls == []
    assert writer.calls == []
    assert events.events[-1].failure is category


@pytest.mark.parametrize(
    ("reason", "category", "retryable"),
    [
        (ProviderFailure.CREDENTIAL, AttemptFailure.CREDENTIAL, False),
        (ProviderFailure.NETWORK, AttemptFailure.NETWORK, True),
        (ProviderFailure.RATE_LIMIT, AttemptFailure.RATE_LIMIT, True),
        (ProviderFailure.PROVIDER, AttemptFailure.PROVIDER, True),
        (ProviderFailure.PROVIDER_LIMIT, AttemptFailure.PROVIDER, False),
    ],
)
def test_ca_005_provider_failure_is_isolated_and_creates_no_output(
    reason: ProviderFailure, category: AttemptFailure, retryable: bool
) -> None:
    failure = TranscriptionFailure(reason, retryable, "safe.message", "SAFE_CODE")
    use_case, _, extractor, _, writer, events = _workflow(provider_result=failure)

    result = use_case.execute(_command())

    assert isinstance(result, TranscribeSingleFileFailure)
    assert result.category is category
    assert result.retryable is retryable
    assert writer.calls == []
    assert extractor.lease.exited is True
    assert events.events[-1].state is AttemptState.FAILED


@pytest.mark.parametrize("boundary", ["before_probe", "prepare", "provider", "write"])
def test_ca_006_cancel_stops_new_steps_and_always_cleans_lease(boundary: str) -> None:
    cancel_calls = 0

    def cancel() -> bool:
        nonlocal cancel_calls
        cancel_calls += 1
        return boundary == "before_probe"

    provider_result: TranscriptionSuccess | TranscriptionFailure = _success()
    writer_result: Path | Exception = Path("C:/chosen-output/result.txt")
    enter_error = None
    if boundary == "prepare":
        enter_error = MediaError(MediaFailure.CANCELLED)
    elif boundary == "provider":
        provider_result = TranscriptionFailure(
            ProviderFailure.CANCELLED, False, "safe.message", "CANCELLED"
        )
    elif boundary == "write":
        writer_result = OutputWriteCancelled()
    use_case, probe, extractor, provider, writer, events = _workflow(
        provider_result=provider_result,
        writer_result=writer_result,
        enter_error=enter_error,
    )

    result = use_case.execute(_command(), cancel)

    assert isinstance(result, TranscribeSingleFileFailure)
    assert result.category is AttemptFailure.CANCELLED
    assert result.state is AttemptState.CANCELLED
    states = [event.state for event in events.events]
    assert states[-2:] == [AttemptState.CANCELLING, AttemptState.CANCELLED]
    assert AttemptState.COMPLETED not in states
    if boundary == "before_probe":
        assert probe.calls == []
    else:
        assert extractor.lease.exited is True
    if boundary in {"before_probe", "prepare"}:
        assert provider.calls == []
    if boundary != "write":
        assert writer.calls == []


def test_silence_creates_empty_txt_with_warning() -> None:
    use_case, _, _, _, writer, events = _workflow(provider_result=_success(""))

    result = use_case.execute(_command())

    assert isinstance(result, TranscribeSingleFileSuccess)
    assert writer.calls[0][2] == ""
    assert result.warnings == ("no_speech_detected",)
    assert events.events[-1].warnings == ("no_speech_detected",)


def test_output_failure_never_declares_success_and_releases_temporary() -> None:
    use_case, _, extractor, _, _, events = _workflow(writer_result=OutputWriteError())

    result = use_case.execute(_command())

    assert isinstance(result, TranscribeSingleFileFailure)
    assert result.category is AttemptFailure.OUTPUT
    assert AttemptState.COMPLETED not in [event.state for event in events.events]
    assert extractor.lease.exited is True


def test_retry_is_a_new_attempt_after_isolated_failure() -> None:
    responses: list[TranscriptionSuccess | TranscriptionFailure] = [
        TranscriptionFailure(ProviderFailure.NETWORK, True, "safe.message", "NETWORK"),
        _success(),
    ]
    use_case, _, _, provider, writer, _ = _workflow(provider_result=responses)

    first = use_case.execute(_command("attempt-1"))
    second = use_case.execute(_command("attempt-2"))

    assert isinstance(first, TranscribeSingleFileFailure)
    assert isinstance(second, TranscribeSingleFileSuccess)
    assert [call.attempt_id for call in provider.calls] == ["attempt-1", "attempt-2"]
    assert len(writer.calls) == 1


def test_only_one_attempt_can_be_active() -> None:
    entered = Event()
    release = Event()

    def block_provider() -> None:
        entered.set()
        assert release.wait(timeout=5)

    use_case, _, _, _, _, _ = _workflow(before_provider_return=block_provider)
    results: list[object] = []
    thread = Thread(target=lambda: results.append(use_case.execute(_command("active"))))
    thread.start()
    assert entered.wait(timeout=5)

    with pytest.raises(TranscriptionAlreadyRunningError):
        use_case.execute(_command("concurrent"))

    release.set()
    thread.join(timeout=5)
    assert not thread.is_alive()
    assert isinstance(results[0], TranscribeSingleFileSuccess)


def test_ca_007_to_009_events_have_no_fake_percentage_history_or_sensitive_content(
    caplog: pytest.LogCaptureFixture,
) -> None:
    use_case, _, _, _, _, events = _workflow()

    result = use_case.execute(_command())

    assert isinstance(result, TranscribeSingleFileSuccess)
    assert all(not hasattr(event, "percent") for event in events.events)
    assert "Texto sintético" not in caplog.text
    assert "aula pessoal" not in caplog.text
    fresh = _workflow()[-1]
    assert fresh.events == []
