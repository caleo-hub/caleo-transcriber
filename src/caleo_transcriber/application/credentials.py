"""Porta neutra para armazenamento de credenciais da aplicação."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True, repr=False)
class SecretValue:
    """Valor sensível com representação textual sempre redigida."""

    _value: str = field(repr=False)

    def reveal(self) -> str:
        """Expõe o valor apenas no ponto explícito de integração autorizado."""
        return self._value

    def __repr__(self) -> str:
        return "SecretValue(<redacted>)"

    def __str__(self) -> str:
        return "<redacted>"


class CredentialStoreFailure(StrEnum):
    """Motivos estáveis, independentes da infraestrutura escolhida."""

    ACCESS_DENIED = "access_denied"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


class CredentialStoreError(RuntimeError):
    """Falha neutra que não incorpora dados sensíveis da infraestrutura."""

    def __init__(self, reason: CredentialStoreFailure) -> None:
        self.reason = reason
        super().__init__(f"Credential store operation failed: {reason.value}")


@runtime_checkable
class CredentialStore(Protocol):
    """Contrato de credenciais identificado por serviço e conta."""

    def get(self, service: str, account: str) -> SecretValue | None:
        """Retorna a credencial ou ``None`` quando ela não existe."""
        ...

    def set(self, service: str, account: str, value: SecretValue) -> None:
        """Cria ou substitui uma credencial."""
        ...

    def delete(self, service: str, account: str) -> bool:
        """Remove a credencial e informa se ela existia."""
        ...
