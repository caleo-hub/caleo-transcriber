# TASK-004 — Escrita TXT atômica

## Objetivo

Implementar porta/adapter de saída UTF-8 com sufixo de colisão, criação exclusiva e nenhuma saída parcial.

## Contexto e fontes

CA-003, CA-006, regras 2–4; T-04; `modules.md`.

## Escopo de arquivos

Permitidos: porta em `application`, `adapters/filesystem/` e testes de integração. Proibidos: UI, mídia, provider e histórico.

## Restrições e autonomia

Baixo/moderado risco; somente diretórios temporários de teste. Não apagar arquivo preexistente.

## Critérios de aceitação

UTF-8; `nome.txt`, `nome (1).txt` etc.; corrida não sobrescreve; falha/cancelamento remove temporário; caminho final só existe após sucesso.

## Validação e evidência

`verify.cmd`; testes de colisão, Unicode, falha injetada e concorrência de nome.

## Rollback

Reverter PR; testes usam apenas temporários.

