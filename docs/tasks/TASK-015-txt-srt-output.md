# TASK-015 — Saídas consolidadas TXT e SRT

## Objetivo

Publicar TXT ou SRT da mesma transcrição consolidada, atomicamente e sem sobrescrever.

## Contexto e fontes

FEAT-002 LM-CA-004–006; TASK-012; PRD RF-009/013.

## Escopo de arquivos

Porta neutra de saída, adapter filesystem, parser/goldens. Proibida retranscrição por formato.

## Restrições e autonomia

Depende de TASK-012. UTF-8; SRT com timestamp global; política de nome existente preservada.

## Critérios de aceitação

TXT/SRT determinísticos; cues crescentes e não sobrepostos; silêncio válido; colisão segura; falha ou
cancelamento não publica parcial.

## Validação e evidência

`verify.cmd`; parser SRT independente; goldens Unicode e timestamps.

## Rollback

Reverter extensão do writer; TXT anterior permanece compatível e saídas do usuário intocadas.
