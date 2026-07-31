# TASK-011 — Specs, contratos e oráculos do segundo incremento

## Objetivo

Fixar comportamento, arquitetura proposta, riscos, gates e vetores verificáveis antes do código.

## Contexto e fontes

PRD RF-002/009–016; estratégia de mídia longa; constituição; FEAT-002/003; threat model.

## Escopo de arquivos

Somente `specs/`, `docs/`, `contracts/` e testes de contrato/arquitetura dos oráculos. Proibido
alterar comportamento de `src/`.

## Restrições e autonomia

Sem implementação. Decisões de retenção/custo e layout ficam pendentes nos gates SEC/UX.

## Critérios de aceitação

Critérios LM/BATCH completos; ADRs e tarefas 011–019; schemas válidos; vetores cobrem bordas,
deduplicação, retomada, falha, cancelamento e retry; manifesto de exemplo sem path/texto.

## Validação e evidência

`verify.cmd`; testes de contrato e arquitetura; revisão humana dos dois gates.

## Rollback

Reverter documentos/contratos/testes; nenhuma aplicação muda.
