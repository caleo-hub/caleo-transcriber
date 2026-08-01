# TASK-024 — Contraste do menu Limpar

## Objetivo

Tornar todas as opções do menu `Limpar…` legíveis sob tema escuro do Windows e publicar um patch
beta sem alterar o comportamento da fila.

## Contexto e fontes

Relato e screenshot do owner em 2026-08-01; TASK-021/023, FEAT-003, ADR-0002, gate UX e constituição.

## Escopo de arquivos

Estilo Qt do `QMenu`, teste pytest-qt, captura visual, versão `0.3.1`, notas, status e empacotamento
`v0.3.1-beta.1`.

## Restrições e autonomia

Não mudar semântica das ações, dados, rede, credenciais, mídia ou filesystem. Nenhuma chamada
OpenAI ou instalação local. Preservar a release anterior para rollback.

## Critérios de aceitação

1. Fundo do menu é claro e texto normal possui contraste explícito.
2. Hover/seleção mantém texto legível e indicação visível.
3. Itens desabilitados continuam distinguíveis e legíveis.
4. Separadores são visíveis sem depender do tema nativo.
5. A correção alcança o popup real, não apenas o botão `Limpar…`.
6. Screenshot determinístico demonstra o menu aberto.
7. `verify.cmd`, `audit.cmd`, CI, gitleaks, pacote e preflight passam.
8. `v0.3.1-beta.1` contém seis assets e o instalador baixado confere com o checksum.

## Validação e evidência

Teste de stylesheet/objeto do menu, captura `07-clear-menu.png`, checks locais/remotos,
build-evidence, checksum e preflight pós-download sem instalação.

## Rollback

Preservar e reinstalar `v0.3.0-beta.1`; nenhuma mídia, saída ou credencial é removida.
