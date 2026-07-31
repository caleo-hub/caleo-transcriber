# TASK-017 — Fila sequencial e isolamento por item

## Objetivo

Implementar agregado e scheduler FIFO com um item ativo, cancelamento e retry apenas de falhas.

## Contexto e fontes

FEAT-003 BATCH-CA-001–007/009/010; ADR-0007; TASK-016.

## Escopo de arquivos

`domain/`, `application/`, fakes e aceitação sem UI. Proibidos PySide6 e persistência de fila.

## Restrições e autonomia

Depende de GATE-SEC-002 e TASK-016. Eventos por ID/estado; sucessos imutáveis.

## Critérios de aceitação

FIFO; máximo um ativo; falha avança; cancelamentos isolados; retry somente `failed`; resumo por
contagens; fechar descarta fila.

## Validação e evidência

`verify.cmd`; tabela de transições; falhas em cada posição; propriedade de concorrência máxima um.

## Rollback

Reverter scheduler e manter caso de uso de arquivo único operacional.
