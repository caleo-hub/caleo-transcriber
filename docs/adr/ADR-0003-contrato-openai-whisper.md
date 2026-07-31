# ADR-0003 — Contrato OpenAI `whisper-1`

- **Status:** aceito
- **Data:** 2026-07-31
- **Decisor:** `caleo-hub`

## Decisão proposta

O adapter usa `/v1/audio/transcriptions`, `model=whisper-1` e `response_format=verbose_json`, solicitando timestamps por segmento desde a primeira fatia. O TXT deriva do campo textual normalizado; segmentos são mantidos apenas em memória para permitir SRT posterior sem nova transcrição.

O áudio preparado deve ser MP3 mono, com parâmetros de qualidade definidos e verificados na prova técnica, e ter menos de 25 MB. Se exceder, a primeira fatia falha antes do envio com categoria `provider_limit`; chunking pertence à feature de mídia longa.

## Motivos

- timestamps de segmento não adicionam latência segundo a referência da API;
- o mesmo resultado conceitual sustenta TXT agora e SRT depois;
- a API aceita arquivos de até 25 MB e recomenda compressão ou divisão para maiores;
- o modelo fica encapsulado para permitir futuro `gpt-transcribe` ou Whisper local.

## Resiliência

- timeouts explícitos para conexão, leitura e total;
- sem retry automático em falhas ambíguas após upload nesta fatia, evitando custo duplicado;
- retry manual cria nova tentativa visível;
- 401/403 → `credential`; 429 → `rate_limit`; timeout/DNS → `network`; 5xx/resposta inválida → `provider`;
- nunca registrar headers, corpo, áudio ou texto.

## Alternativas

- **`response_format=text`:** mais simples, mas descartaria timestamps úteis ao SRT; rejeitada.
- **modelo geral recomendado mais novo:** potencial de melhor qualidade, mas não atende à decisão explícita pelo Whisper e ao mesmo contrato de timestamps; mantido como evolução possível.
- **retry automático:** pode duplicar cobrança quando não há certeza se a requisição foi processada; rejeitado inicialmente.
