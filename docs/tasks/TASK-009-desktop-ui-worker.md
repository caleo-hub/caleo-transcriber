# TASK-009 — Interface principal e worker

## Objetivo

Entregar a jornada PySide6 para um arquivo: selecionar mídia/destino, ver cloud, iniciar, acompanhar etapa, cancelar, repetir e abrir destino.

## Contexto e fontes

TASK-003/008; CA-007/CA-010; PRD UX; decisão Q3.

## Escopo de arquivos

Permitidos: `presentation/`, worker, bootstrap e testes Qt/E2E controlados. Proibidos: regra de domínio na UI, chamada direta a adapters e percentual artificial.

## Restrições e autonomia

Risco moderado. UI thread nunca bloqueia; avisos não dependem de cor; sem chamada paga nos testes.

## Critérios de aceitação

Operável por teclado; foco/labels; indicador “OpenAI (cloud) — envia áudio e pode gerar custo”; estados textuais; worker sobrevive a erro; cancelamento/repetição; nenhum histórico após reinício.

## Validação e evidência

`verify.cmd`, pytest-qt, teste de responsividade, screenshots e checklist manual aprovado pelo owner.

## Rollback

Reverter UI/bootstrap; casos de uso e adapters permanecem testáveis.

