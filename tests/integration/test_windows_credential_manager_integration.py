import platform
import uuid

import pytest

from caleo_transcriber.adapters.credentials import WindowsCredentialStore
from caleo_transcriber.application import SecretValue

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(platform.system() != "Windows", reason="requer Windows Credential Manager"),
]


def test_windows_credential_manager_round_trip_and_cleanup() -> None:
    store = WindowsCredentialStore()
    service = f"caleo-transcriber-integration-{uuid.uuid4()}"
    account = "synthetic-openai-canary"
    first = "synthetic-first-value"
    replacement = "synthetic-replacement-value"

    try:
        assert store.get(service, account) is None

        store.set(service, account, SecretValue(first))
        saved = store.get(service, account)
        assert saved is not None
        assert saved.reveal() == first

        store.set(service, account, SecretValue(replacement))
        replaced = store.get(service, account)
        assert replaced is not None
        assert replaced.reveal() == replacement

        assert store.delete(service, account) is True
        assert store.get(service, account) is None
    finally:
        store.delete(service, account)
