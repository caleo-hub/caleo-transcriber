from caleo_transcriber import __version__
from caleo_transcriber.domain.attempt import AttemptState


def test_package_is_importable() -> None:
    assert __version__ == "0.0.0"


def test_attempt_state_uses_stable_wire_values() -> None:
    assert AttemptState.READY.value == "ready"
    assert AttemptState.CANCELLED.value == "cancelled"
