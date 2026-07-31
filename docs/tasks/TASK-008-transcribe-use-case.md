# TASK-008 — Caso de uso da primeira fatia

## Objetivo

Orquestrar probe, extração, credencial, provider, escrita, eventos e cleanup sem importar adapters.

## Contexto e fontes

TASK-004/006/007; FEAT-001 completa; máquina de estados; plano de testes.

## Escopo de arquivos

Permitidos: `domain/`, `application/`, fakes e testes de componente/aceitação. Proibidos: PySide6, OpenAI SDK, keyring, subprocesso e filesystem concreto no core.

## Restrições e autonomia

Risco moderado. Todos os efeitos por portas; uma tentativa ativa; sem paralelismo/chunking/SRT.

## Critérios de aceitação

Happy path e CA-001–CA-009 com fakes; estados válidos; falha isolada; cancelamento não conclui; silêncio produz warning; cleanup em todas as fronteiras.

## Validação e evidência

`verify.cmd`; testes de componente e aceitação parametrizados; rastreabilidade CA → teste.

## Rollback

Reverter caso de uso; adapters independentes permanecem sem efeito externo automático.

