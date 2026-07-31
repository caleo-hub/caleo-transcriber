"""Caso de uso para configurar a chave OpenAI sem expor seu valor."""

from dataclasses import dataclass

from caleo_transcriber.application.credentials import CredentialStore, SecretValue

OPENAI_CREDENTIAL_SERVICE = "Caleo Transcriber"
OPENAI_CREDENTIAL_ACCOUNT = "openai-api-key"


@dataclass(frozen=True, slots=True)
class LocalKeyValidation:
    """Resultado não sensível de uma validação exclusivamente local."""

    valid: bool
    message: str


class ApiKeySettings:
    """Coordena a credencial OpenAI protegida pelo armazenamento do sistema."""

    def __init__(self, store: CredentialStore) -> None:
        self._store = store

    def is_configured(self) -> bool:
        return self._get() is not None

    def validate_candidate(self, candidate: str) -> LocalKeyValidation:
        if not candidate:
            return LocalKeyValidation(False, "Digite uma chave antes de testar.")
        if candidate != candidate.strip() or any(character.isspace() for character in candidate):
            return LocalKeyValidation(False, "A chave não pode conter espaços.")
        return LocalKeyValidation(
            True,
            "Formato local aceito. A validade na OpenAI será confirmada somente ao transcrever.",
        )

    def validate_saved(self) -> LocalKeyValidation:
        saved = self._get()
        if saved is None:
            return LocalKeyValidation(False, "Nenhuma chave está configurada.")
        return self.validate_candidate(saved.reveal())

    def save(self, candidate: str) -> LocalKeyValidation:
        validation = self.validate_candidate(candidate)
        if validation.valid:
            self._store.set(
                OPENAI_CREDENTIAL_SERVICE,
                OPENAI_CREDENTIAL_ACCOUNT,
                SecretValue(candidate),
            )
        return validation

    def remove(self) -> bool:
        return self._store.delete(OPENAI_CREDENTIAL_SERVICE, OPENAI_CREDENTIAL_ACCOUNT)

    def _get(self) -> SecretValue | None:
        return self._store.get(OPENAI_CREDENTIAL_SERVICE, OPENAI_CREDENTIAL_ACCOUNT)
