# TASK-023 — Controles de gerenciamento da fila

## Objetivo

Permitir que a pessoa organize e limpe a fila pela interface sem apagar mídia, transcrições ou
credenciais, mantendo um único item ativo e ordem determinística.

## Contexto e fontes

Solicitação do owner em 2026-07-31 após validar `v0.2.1-beta.1`; FEAT-003, ADR-0007, constituição,
módulos e gate UX do segundo incremento.

## Escopo de arquivos

Domínio e aplicação da fila, UI PySide6, testes unitários/aceitação/UX, spec e ADR, versão `0.3.0`,
notas, evidência visual e empacotamento `v0.3.0-beta.1`.

## Restrições e autonomia

Não apagar arquivos de origem ou saída. Não mover/remover item ativo. Não persistir histórico.
Nenhuma mídia real, chave ou chamada OpenAI é necessária. Manter processamento sequencial.

## Critérios de aceitação

1. Ctrl/Shift selecionam linhas e habilitam ações conforme os estados selecionados.
2. Remover selecionados ignora ativo e remove pendentes/terminais sem efeitos no filesystem.
3. Subir/descer altera somente a ordem relativa de pendentes e o scheduler a respeita.
4. Limpar concluídos, falhas/cancelados, pendentes e fila inativa preserva ativo e arquivos.
5. Repetir selecionados reenvia somente falhas selecionadas.
6. Pausar após o atual deixa os demais pendentes; cancelar atual não cancela pendentes.
7. Cancelar fila continua disponível como ação distinta.
8. Ações têm nomes acessíveis, atalhos e estados desabilitados compreensíveis.
9. `verify.cmd`, `audit.cmd`, CI, secret scan, pacote e preflight passam.
10. A prerelease contém instalador x64 e evidências; o download confere com o SHA-256 publicado.

## Validação e evidência

Testes de domínio, aceitação e UI, screenshot determinístico, checks GitHub, build-evidence,
checksum e preflight pós-download sem instalação.

## Rollback

Preservar `v0.2.1-beta.1`; reverter métodos de ordenação/remoção e barra de ações. Saídas e
credenciais permanecem intocadas.

## Resultado

Concluída em 2026-07-31 pela PR #19. O tag `v0.3.0-beta.1` aponta para `9227009`, contém os seis
assets previstos e o instalador baixado passou pelo preflight com SHA-256
`3175f209626c283ce2d5ef09bfbbc1da79aab0cd6fb34e05b58de2d5cd12acb5`. Nenhuma instalação, mídia
pessoal ou nova chamada OpenAI foi usada na validação da release.
