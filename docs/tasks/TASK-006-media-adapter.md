# TASK-006 — Probe e extração de áudio

## Objetivo

Implementar adapters FFprobe/FFmpeg para validar MP4/MP3/WAV e produzir MP3 mono abaixo do limite contratado, sem vídeo.

## Contexto e fontes

TASK-005 aprovada; CA-002/CA-004; ADR-0003; T-02/T-05/T-06.

## Escopo de arquivos

Permitidos: portas de mídia, `adapters/media/`, gerador de mídia sintética e testes. Proibidos: provider, UI, download em runtime e `shell=True`.

## Restrições e autonomia

Risco moderado; apenas mídia sintética gerada. Argumentos em lista, timeout, cancelamento e diretório privado.

## Critérios de aceitação

Probe rejeita vazio/corrompido/sem áudio/>30 min; saída contém só áudio; tamanho <25.000.000; caminhos Unicode/metacaracteres; cleanup em toda terminação.

## Validação e evidência

`verify.cmd`, `audit.cmd`, inspeção ffprobe da saída e testes adversariais.

## Rollback

Reverter adapter; remover temporários/binários ignorados.

