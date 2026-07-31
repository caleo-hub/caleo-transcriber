from unittest.mock import patch

import pytest
from keyring import errors as keyring_errors

from caleo_transcriber.adapters.credentials import WindowsCredentialStore
from caleo_transcriber.application import CredentialStoreError, CredentialStoreFailure, SecretValue

SERVICE = "caleo-transcriber-tests"
ACCOUNT = "openai"
CANARY = "synthetic-unit-canary"


def test_get_wraps_password_as_redacted_secret() -> None:
    store = WindowsCredentialStore()

    with patch("keyring.get_password", return_value=CANARY):
        value = store.get(SERVICE, ACCOUNT)

    assert value is not None
    assert value.reveal() == CANARY
    assert CANARY not in repr(value)


def test_get_returns_none_when_password_is_absent() -> None:
    store = WindowsCredentialStore()

    with patch("keyring.get_password", return_value=None):
        assert store.get(SERVICE, ACCOUNT) is None


def test_set_reveals_secret_only_to_keyring_boundary() -> None:
    store = WindowsCredentialStore()

    with patch("keyring.set_password") as set_password:
        store.set(SERVICE, ACCOUNT, SecretValue(CANARY))

    set_password.assert_called_once_with(SERVICE, ACCOUNT, CANARY)


def test_delete_is_neutral_when_password_is_absent() -> None:
    store = WindowsCredentialStore()

    with (
        patch("keyring.get_password", return_value=None),
        patch("keyring.delete_password") as delete_password,
    ):
        assert store.delete(SERVICE, ACCOUNT) is False

    delete_password.assert_not_called()


def test_delete_reports_removed_password() -> None:
    store = WindowsCredentialStore()

    with (
        patch("keyring.get_password", return_value=CANARY),
        patch("keyring.delete_password") as delete_password,
    ):
        assert store.delete(SERVICE, ACCOUNT) is True

    delete_password.assert_called_once_with(SERVICE, ACCOUNT)


@pytest.mark.parametrize(
    ("native_error", "expected"),
    [
        (PermissionError(), CredentialStoreFailure.ACCESS_DENIED),
        (keyring_errors.NoKeyringError(), CredentialStoreFailure.UNAVAILABLE),
        (keyring_errors.PasswordSetError(), CredentialStoreFailure.UNKNOWN),
    ],
)
def test_native_errors_are_mapped_without_secret(
    native_error: Exception, expected: CredentialStoreFailure
) -> None:
    store = WindowsCredentialStore()

    with patch("keyring.set_password", side_effect=native_error):
        with pytest.raises(CredentialStoreError) as caught:
            store.set(SERVICE, ACCOUNT, SecretValue(CANARY))

    assert caught.value.reason is expected
    assert CANARY not in str(caught.value)
    assert CANARY not in repr(caught.value)
