# TASK-016 — Orquestração longa, retomada e recomposição

## Objetivo

Coordenar plano, extração, provider, checkpoints, merge e saída final por um arquivo.

## Contexto e fontes

TASK-012–015; FEAT-002 completa; contrato provider v1; GATE-SEC-002.

## Escopo de arquivos

`application/`, fakes e aceitação. Adapters entram apenas por portas; UI fica proibida.

## Restrições e autonomia

Um upload ativo; sem retry ambíguo; chunks confirmados nunca reenviados; eventos sem conteúdo.

## Critérios de aceitação

Todos LM-CA; falha intermediária retoma; ambiguidade pausa; cancelamento não publica; sucesso limpa;
resultado inteiro e segmentado equivalentes nos goldens.

## Validação e evidência

`verify.cmd`; componente com falhas/crash injetados; contador de concorrência; canários.

## Rollback

Desabilitar rota longa e restaurar caso de uso anterior; cleanup remove checkpoints v1.
