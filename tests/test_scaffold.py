from itertools import pairwise

from caleo_transcriber import __version__
from caleo_transcriber.domain.attempt import ALLOWED_TRANSITIONS, AttemptState, can_transition


def test_package_is_importable() -> None:
    assert __version__ == "0.3.1"


def test_attempt_state_uses_stable_wire_values() -> None:
    assert AttemptState.READY.value == "ready"
    assert AttemptState.CANCELLED.value == "cancelled"


def test_every_state_has_an_explicit_transition_policy() -> None:
    assert set(ALLOWED_TRANSITIONS) == set(AttemptState)


def test_terminal_states_reject_all_transitions() -> None:
    terminal = {AttemptState.COMPLETED, AttemptState.FAILED, AttemptState.CANCELLED}
    assert all(not can_transition(state, target) for state in terminal for target in AttemptState)


def test_happy_path_is_permitted() -> None:
    path = [
        AttemptState.READY,
        AttemptState.PREPARING,
        AttemptState.TRANSCRIBING,
        AttemptState.SAVING,
        AttemptState.COMPLETED,
    ]
    assert all(can_transition(current, target) for current, target in pairwise(path))
