# TASK-013 — Checkpoints protegidos e recuperação

## Objetivo

Criar porta de checkpoint e adapter Windows DPAPI com integridade, expiração e cleanup.

## Contexto e fontes

FEAT-002 LM-CA-007–010; ADR-0006; T2-02–06; schema checkpoint v1.

## Escopo de arquivos

Porta em `application`, adapter `filesystem/windows`, fakes e testes controlados. Proibidos chave
OpenAI, texto claro persistente, caminho completo no manifesto e log de conteúdo.

## Restrições e autonomia

Depende de GATE-SEC-002. Sem dependência nova; writes atômicos; diretório confinado.

## Critérios de aceitação

Roundtrip DPAPI do usuário; outro escopo/adulteração falham fechado; `uploading` recupera como
`ambiguous`; TTL/cleanup; canários ausentes de manifesto/log; áudio nunca integra checkpoint.

## Validação e evidência

`verify.cmd`; integração Windows; schema; crash e corpus de referências adversariais.

## Rollback

Cleanup reconhece e remove schema v1; reverter adapter/porta sem tocar saídas finais.
