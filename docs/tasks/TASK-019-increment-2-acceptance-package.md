# TASK-019 — Aceitação e candidato do segundo incremento

## Objetivo

Executar o gauntlet integrado, evidência visual e smoke do pacote com mídia sintética.

## Contexto e fontes

TASK-012–018; FEAT-002/003; gates aprovados; release runbook; TASK-010.

## Escopo de arquivos

Aceitação/E2E, fixtures geradas, docs de evidência e versão de candidato. GitHub Release proibida.

## Restrições e autonomia

Sem chave real, mídia pessoal, instalação ou publicação sem aprovação específica.

## Critérios de aceitação

LM/BATCH rastreados a testes; `verify`/audit/package verdes; canários limpos; screenshots aprovadas;
Windows 10 limpo e chamada real permanecem reportados como executados ou pendentes, nunca inferidos.

## Validação e evidência

`verify.cmd`, `audit.cmd`, workflow de pacote, evidence pack e aceite humano de UX/segurança.

## Rollback

Retirar candidato efêmero e reverter incremento; preservar versão anterior, saídas e credencial.
