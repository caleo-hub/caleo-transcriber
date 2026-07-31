# TASK-020 — Ícone do aplicativo Windows

## Objetivo

Substituir o ícone padrão do Python por uma identidade visual original e legível no aplicativo,
executável, atalhos e instalador.

## Contexto e fontes

Solicitação do owner após TASK-018; identidade visual própria e remoção do ícone padrão do Python.

## Escopo de arquivos

- ativo PNG transparente para a janela Qt;
- ICO multirresolução para PyInstaller e Inno Setup;
- microfone e ondas como metáfora de transcrição, sem texto ou marca de terceiros;
- validação de transparência e presença das resoluções Windows.

## Restrições e autonomia

Ativo original, sem texto, marca de terceiro ou mídia pessoal. A geração não usa a chave do usuário;
PNG/ICO entram no repositório e no pacote Windows.

## Critérios de aceitação

1. A janela exibe o novo ícone durante desenvolvimento e no pacote.
2. `CaleoTranscriber.exe`, instalador, desinstalador e atalhos não usam o ícone do Python.
3. O ICO contém 16, 24, 32, 48, 64, 128 e 256 px.
4. O PNG tem cantos transparentes e o ativo continua reconhecível em 16 px.
5. O processo de build falha se os ativos estiverem ausentes.

## Validação e evidência

Ativos em `assets/`, testes de contrato do pacote, inspeção visual e smoke do instalador beta.

## Proveniência

Ícone original gerado em 2026-07-31 pelo recurso integrado de geração de imagem, usando a descrição:
“microfone simplificado com ondas, bloco arredondado azul-marinho, símbolo ciano e detalhe coral; estilo
vetorial mínimo; sem texto, marca ou watermark”. O fundo cromático foi removido localmente e não faz
parte do ativo final.

## Rollback

Remover as referências de PyInstaller, Inno Setup e Qt e excluir somente os dois ativos criados nesta
tarefa; nenhum arquivo de transcrição ou credencial é afetado.
