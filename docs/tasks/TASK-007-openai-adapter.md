# TASK-007 — Adapter OpenAI `whisper-1`

## Objetivo

Implementar o contrato v1 contra transporte HTTP/SDK substituível, inicialmente apenas com respostas simuladas.

## Contexto e fontes

TASK-001; ADR-0003; schema v1; CA-001/CA-005/CA-009; documentação oficial OpenAI.

## Escopo de arquivos

Permitidos: porta do provider, `adapters/openai/`, transporte fake e testes de contrato. Proibidos: UI, FFmpeg, retry automático, chave em env e chamada real no CI.

## Restrições e autonomia

Risco moderado. Adapter obtém chave por porta; endpoint/model fixos; payload spy prova somente áudio. Chamada real exige autorização separada, áudio sintético e custo aceito.

## Critérios de aceitação

`whisper-1`, `verbose_json`, timestamp segment; mapeamento 401/403/429/timeout/5xx; schema válido; sem logs sensíveis; cancelamento/timeout; zero retry pós-upload.

## Validação e evidência

`verify.cmd`, `audit.cmd`, testes de contrato e captura do multipart fake.

## Rollback

Reverter adapter; nenhuma chamada/dado externo no fluxo padrão.

