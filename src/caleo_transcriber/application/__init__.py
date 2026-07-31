"""Casos de uso e portas; sem detalhes de framework."""

from caleo_transcriber.application.credentials import (
    CredentialStore,
    CredentialStoreError,
    CredentialStoreFailure,
    SecretValue,
)

__all__ = [
    "CredentialStore",
    "CredentialStoreError",
    "CredentialStoreFailure",
    "SecretValue",
]
