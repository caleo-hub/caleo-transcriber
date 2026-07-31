from caleo_transcriber.application import (
    CredentialStore,
    CredentialStoreError,
    CredentialStoreFailure,
    SecretValue,
)
from fakes.credential_store import InMemoryCredentialStore

SERVICE = "caleo-transcriber-tests"
ACCOUNT = "openai"
CANARY = "unit-test-canary"


def test_fake_satisfies_credential_store_protocol() -> None:
    assert isinstance(InMemoryCredentialStore(), CredentialStore)


def test_get_returns_none_when_credential_is_absent() -> None:
    store = InMemoryCredentialStore()

    assert store.get(SERVICE, ACCOUNT) is None


def test_round_trip_returns_saved_secret() -> None:
    store = InMemoryCredentialStore()
    value = SecretValue(CANARY)

    store.set(SERVICE, ACCOUNT, value)

    stored = store.get(SERVICE, ACCOUNT)
    assert stored is not None
    assert stored.reveal() == CANARY


def test_set_replaces_existing_secret_for_same_service_and_account() -> None:
    store = InMemoryCredentialStore()
    store.set(SERVICE, ACCOUNT, SecretValue("old-canary"))

    store.set(SERVICE, ACCOUNT, SecretValue("new-canary"))

    stored = store.get(SERVICE, ACCOUNT)
    assert stored is not None
    assert stored.reveal() == "new-canary"


def test_delete_reports_presence_and_removes_secret() -> None:
    store = InMemoryCredentialStore()
    store.set(SERVICE, ACCOUNT, SecretValue(CANARY))

    assert store.delete(SERVICE, ACCOUNT) is True
    assert store.get(SERVICE, ACCOUNT) is None
    assert store.delete(SERVICE, ACCOUNT) is False


def test_secret_is_redacted_from_object_representations() -> None:
    value = SecretValue(CANARY)
    store = InMemoryCredentialStore()
    store.set(SERVICE, ACCOUNT, value)

    representations = (str(value), repr(value), repr(store))
    assert all(CANARY not in representation for representation in representations)
    assert all("redacted" in representation for representation in representations[:2])


def test_neutral_error_does_not_include_secret_value() -> None:
    error = CredentialStoreError(CredentialStoreFailure.UNAVAILABLE)

    assert CANARY not in str(error)
    assert CANARY not in repr(error)
    assert error.reason is CredentialStoreFailure.UNAVAILABLE
