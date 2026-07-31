# TASK-012 — Planner e recomposição de mídia longa

## Objetivo

Implementar tipos e funções puras para plano por bytes, offsets, validação e deduplicação.

## Contexto e fontes

FEAT-002 LM-CA-001/003–005/012; ADR-0006; vetores long-media.

## Escopo de arquivos

`domain/`, testes unitários/propriedade e goldens. Proibidos filesystem, FFmpeg, SDK e PySide6.

## Restrições e autonomia

Depende de GATE-SEC-002. Constantes internas, determinismo e nenhuma heurística oculta na UI.

## Critérios de aceitação

Planos cobrem toda timeline; chunks ordenados/limitados; overlap exato; dedup somente na janela;
lacunas/inversões rejeitadas; repetição legítima preservada.

## Validação e evidência

`verify.cmd`; vetores canônicos; propriedades de cobertura/ordem/idempotência.

## Rollback

Reverter módulo puro sem tocar adapters ou saídas.
