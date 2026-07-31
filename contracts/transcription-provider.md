# Contrato `TranscriptionProvider` v1

- **Status:** proposta
- **Consumidor:** `application.TranscribeSingleFile`
- **Implementação inicial:** `OpenAIWhisperAdapter`

## Request

```json
{
  "attempt_id": "UUID efêmero",
  "audio_path": "caminho temporário somente interno",
  "media_type": "audio/mpeg",
  "size_bytes": 123456,
  "language": null,
  "timestamps": "segment"
}
```

### Pré-condições

- arquivo existe, é legível e contém somente áudio;
- `0 < size_bytes < 25_000_000` como margem conservadora sob o limite externo de 25 MB;
- chave não integra o request; o adapter a obtém do `CredentialStore`;
- `audio_path` nunca é enviado como metadado.

## Success

```json
{
  "text": "Texto transcrito.",
  "detected_language": "pt",
  "duration_ms": 4200,
  "segments": [
    {"start_ms": 0, "end_ms": 4200, "text": "Texto transcrito."}
  ],
  "provider": "openai",
  "model": "whisper-1"
}
```

### Pós-condições

- segmentos estão em ordem, não possuem duração negativa e ficam dentro da duração retornada;
- `text` vazio é sucesso com aviso `no_speech_detected` quando o áudio é válido;
- nenhuma saída é persistida pelo provider;
- resposta externa desconhecida ou inválida vira erro tipado, nunca resultado parcial silencioso.

## Failure

```json
{
  "category": "credential | network | rate_limit | provider | provider_limit | cancelled",
  "retryable": false,
  "user_message_key": "transcription.error.credential",
  "diagnostic_code": "OPENAI_401"
}
```

`diagnostic_code` não contém mensagem bruta potencialmente sensível. O contrato não promete idempotência do serviço externo.

## Compatibilidade

Campos novos opcionais podem ser adicionados. Alterar significado, unidade, enum existente ou pré/pós-condição exige nova versão do contrato e ADR.

