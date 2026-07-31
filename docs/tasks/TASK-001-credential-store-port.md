# TASK-001 — Porta de credencial e fake em memória

## Objetivo

Definir a porta `CredentialStore`, seus erros neutros e um fake em memória para testes, sem acessar cofre real ou chave real.

## Contexto e fontes

RF-005; ADR-0001/0002; `modules.md`; T-01; constituição 1, 3, 5 e 7.

## Escopo de arquivos

Permitidos: `src/caleo_transcriber/application/`, `tests/unit/`, `tests/fakes/` e ajustes mínimos de exports. Proibidos: UI, `adapters/`, `.env*`, workflows, dependencies e specs.

## Restrições e autonomia

Baixo risco; edição/teste local autorizados. Não usar `keyring`, ambiente, filesystem, logs, rede ou secrets. Chave nos testes é canário curto não parecido com chave real.

## Critérios de aceitação

- protocolo oferece `get`, `set` e `delete` por serviço/conta;
- `get` distingue ausência sem exceção de infraestrutura;
- fake suporta round-trip, substituição e remoção;
- valor nunca aparece em `repr` de erro/objeto;
- core continua sem depender de adapters.

## Validação e evidência

`verify.cmd`; testes unitários de ausência/round-trip/substituição/remoção/redação; diff e relatório final.

## Rollback

Reverter o PR; nenhum dado externo ou migração existe.

