"""CredentialStore baseado no Windows Credential Manager via keyring."""

from collections.abc import Callable
from typing import TypeVar

import keyring
from keyring import errors as keyring_errors

from caleo_transcriber.application.credentials import (
    CredentialStoreError,
    CredentialStoreFailure,
    SecretValue,
)

_T = TypeVar("_T")


class WindowsCredentialStore:
    """Persiste segredos no backend nativo selecionado pelo keyring no Windows."""

    def get(self, service: str, account: str) -> SecretValue | None:
        value = self._call(lambda: keyring.get_password(service, account))
        return None if value is None else SecretValue(value)

    def set(self, service: str, account: str, value: SecretValue) -> None:
        self._call(lambda: keyring.set_password(service, account, value.reveal()))

    def delete(self, service: str, account: str) -> bool:
        if self.get(service, account) is None:
            return False
        try:
            self._call(lambda: keyring.delete_password(service, account))
        except CredentialStoreError as error:
            if error.reason is CredentialStoreFailure.UNAVAILABLE:
                return False
            raise
        return True

    @staticmethod
    def _call(operation: Callable[[], _T]) -> _T:
        try:
            return operation()
        except PermissionError as error:
            raise CredentialStoreError(CredentialStoreFailure.ACCESS_DENIED) from error
        except OSError as error:
            reason = (
                CredentialStoreFailure.ACCESS_DENIED
                if getattr(error, "winerror", None) == 5
                else CredentialStoreFailure.UNKNOWN
            )
            raise CredentialStoreError(reason) from error
        except keyring_errors.PasswordDeleteError as error:
            raise CredentialStoreError(CredentialStoreFailure.UNAVAILABLE) from error
        except (keyring_errors.NoKeyringError, keyring_errors.InitError) as error:
            raise CredentialStoreError(CredentialStoreFailure.UNAVAILABLE) from error
        except keyring_errors.KeyringError as error:
            raise CredentialStoreError(CredentialStoreFailure.UNKNOWN) from error
