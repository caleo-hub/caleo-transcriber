"""Fake determinístico da porta de credenciais."""

from caleo_transcriber.application import SecretValue


class InMemoryCredentialStore:
    """Armazena credenciais apenas durante a vida do teste."""

    def __init__(self) -> None:
        self._values: dict[tuple[str, str], SecretValue] = {}

    def get(self, service: str, account: str) -> SecretValue | None:
        return self._values.get((service, account))

    def set(self, service: str, account: str, value: SecretValue) -> None:
        self._values[(service, account)] = value

    def delete(self, service: str, account: str) -> bool:
        return self._values.pop((service, account), None) is not None

    def __repr__(self) -> str:
        return f"InMemoryCredentialStore(entries={len(self._values)})"
