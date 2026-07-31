# TASK-014 — Extração FFmpeg por chunks

## Objetivo

Extrair somente intervalos planejados, ajustar fronteiras e garantir cada MP3 abaixo de 24 MB.

## Contexto e fontes

TASK-012; FEAT-002 LM-CA-001–003/010/011; ADR-0006; T2-01/04.

## Escopo de arquivos

Portas de mídia, adapter FFmpeg, fixtures sintéticas e integração. Proibidos shell, upload e mídia
pessoal.

## Restrições e autonomia

Depende de GATE-SEC-002 e TASK-012. Argumentos em lista, timeout/cancelamento e tamanho pós-extração.

## Critérios de aceitação

Remove teto de duração; encontra silêncio quando disponível; mantém overlap; replaneja chunk grande;
limpa cada áudio em sucesso/falha/cancelamento/crash recuperado.

## Validação e evidência

`verify.cmd`; FFmpeg sintético; bordas de bytes simuladas; inspeção de argumentos e cleanup.

## Rollback

Restaurar extrator único e teto anterior; remover temporários do schema novo.
