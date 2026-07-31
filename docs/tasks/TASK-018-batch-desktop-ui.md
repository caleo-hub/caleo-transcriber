# TASK-018 — Interface de lote e retomada

## Objetivo

Entregar tabela acessível, multisseleção, estados/ações individuais e controles globais.

## Contexto e fontes

FEAT-003; GATE-UX-002; TASK-017; CA-008–010; UI existente.

## Escopo de arquivos

`presentation/`, worker, bootstrap e pytest-qt. Regra de fila e adapters diretos são proibidos na UI.

## Restrições e autonomia

Depende de aprovação GATE-UX-002 e TASK-017. UI thread responsiva; nenhum percentual temporal falso.

## Critérios de aceitação

Todos BATCH-CA; teclado/foco/labels; falha não abre modal bloqueador; banners de retomada/ambiguidade;
configurações bloqueadas somente durante execução; screenshots aprováveis.

## Validação e evidência

`verify.cmd`; pytest-qt; screenshots dos quatro estados; checklist humano de UX.

## Rollback

Restaurar janela de arquivo único; core de lote continua isolado e sem execução automática.
