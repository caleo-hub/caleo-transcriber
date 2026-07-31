# Módulos, responsabilidades e dependências

- **Status:** aprovado
- **Data:** 2026-07-31

## Módulos

| Módulo | Responsabilidade | Pode depender de |
|---|---|---|
| `domain` | estados, invariantes, valores e erros neutros | biblioteca padrão |
| `application` | caso de uso `TranscribeSingleFile`, coordenação e portas | `domain` |
| `presentation` | view models, mapeamento de estados e UI PySide6 | `application`, `domain` |
| `adapters.media` | probe e extração de áudio via FFmpeg | portas de `application`, `domain` |
| `adapters.openai` | mapear contrato interno para SDK/API OpenAI | portas de `application`, `domain` |
| `adapters.credentials` | Windows Credential Manager | porta de `application` |
| `adapters.filesystem` | temporários, nomes e escrita atômica | portas de `application`, `domain` |
| `bootstrap` | composição concreta e configuração | todos os módulos |

## Direção obrigatória

```text
presentation ----> application ----> domain
adapters --------> application ----> domain
bootstrap -------> presentation + application + adapters
```

## Dependências proibidas

- `domain` ou `application` importar PySide6, OpenAI SDK, FFmpeg, keyring ou APIs concretas do filesystem;
- `presentation` chamar SDK OpenAI, subprocesso FFmpeg ou cofre diretamente;
- adapters importarem a UI;
- chave, áudio ou transcrição atravessarem o logger;
- uso de `shell=True` para FFmpeg/ffprobe;
- porcentagem inventada a partir de timers.

## Portas mínimas

- `MediaInspector.probe(source) -> MediaInfo`
- `AudioExtractor.extract(source, destination, cancellation) -> PreparedAudio`
- `TranscriptionProvider.transcribe(request, cancellation) -> Transcript`
- `CredentialStore.get/set/delete(service, account)`
- `OutputWriter.write_atomic(request) -> OutputArtifact`
- `AttemptEvents.publish(event)`

Não serão criadas interfaces para funções puras internas. Portas existem apenas em efeitos externos, variabilidade futura ou isolamento de testes.

## Estados e erros

O estado canônico pertence a `domain`; a UI apenas o projeta. Erros externos são traduzidos na fronteira para categorias estáveis: `invalid_input`, `unsupported_media`, `credential`, `network`, `rate_limit`, `provider`, `cancelled`, `insufficient_disk` e `output`.
