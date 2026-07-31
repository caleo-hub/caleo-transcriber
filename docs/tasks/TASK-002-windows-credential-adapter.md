# TASK-002 — Adapter Windows Credential Manager

## Objetivo

Implementar `CredentialStore` com `keyring` no backend nativo do Windows e provar round-trip com valor sintético.

## Contexto e fontes

TASK-001; RF-005; ADR-0002; T-01; `SECURITY.md`.

## Escopo de arquivos

Permitidos: `adapters/credentials/`, testes de integração e bootstrap mínimo de teste. Proibidos: UI, OpenAI, mídia e logs de valor.

## Restrições e autonomia

Risco moderado. Teste usa conta/serviço exclusivos e limpa em `finally`. Não ler credenciais existentes nem pedir chave ao usuário.

## Critérios de aceitação

Salvar, obter, substituir e remover funcionam; ausência é neutra; erro nativo é mapeado; nenhum valor aparece em stdout/log/trace; teste pula com motivo fora do Windows.

## Validação e evidência

`verify.cmd`, `audit.cmd` e teste de integração Windows com canário.

## Rollback

Remover adapter e entrada sintética de teste; porta/fake permanecem.

