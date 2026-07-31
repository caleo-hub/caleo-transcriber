from caleo_transcriber.application import ApiKeySettings
from fakes.credential_store import InMemoryCredentialStore


def test_key_can_be_saved_replaced_validated_and_removed() -> None:
    settings = ApiKeySettings(InMemoryCredentialStore())

    assert settings.is_configured() is False
    assert settings.save("synthetic-first-key").valid is True
    assert settings.is_configured() is True
    assert settings.validate_saved().valid is True

    assert settings.save("synthetic-replacement-key").valid is True
    assert settings.remove() is True
    assert settings.is_configured() is False
    assert settings.remove() is False


def test_blank_or_whitespace_key_is_rejected_without_saving() -> None:
    settings = ApiKeySettings(InMemoryCredentialStore())

    assert settings.save("").valid is False
    assert settings.save("synthetic key").valid is False
    assert settings.save(" synthetic-key").valid is False
    assert settings.is_configured() is False


def test_local_validation_does_not_claim_remote_validity() -> None:
    settings = ApiKeySettings(InMemoryCredentialStore())

    result = settings.validate_candidate("synthetic-key")

    assert result.valid is True
    assert "somente ao transcrever" in result.message
