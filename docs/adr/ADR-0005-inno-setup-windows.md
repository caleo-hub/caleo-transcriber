# ADR-0005 — Instalador Windows com Inno Setup

- **Status:** aprovado
- **Data:** 2026-07-31
- **Decisor:** `caleo-hub`

## Contexto

O pacote PyInstaller `onedir` precisa chegar ao usuário como um único instalador x64, sem exigir
Python, Qt ou FFmpeg externos. A instalação é por usuário e a primeira distribuição não possui
atualização automática.

## Decisão

Usar Inno Setup 6.7.3 para compilar o instalador do conteúdo `onedir`:

- origem oficial: release `is-6_7_3` de `jrsoftware/issrc`;
- instalador da ferramenta com SHA-256
  `9c73c3bae7ed48d44112a0f48e66742c00090bdb5bef71d9d3c056c66e97b732`;
- assinatura Authenticode válida de `Pyrsys B.V.` e atestação do GitHub verificadas antes da
  instalação da ferramenta;
- instalação do aplicativo em `%LOCALAPPDATA%`, sem privilégio administrativo;
- suporte somente a Windows 10 x64 build 19045 ou posterior;
- nenhum download, atualização automática ou alteração de dados do usuário no instalador;
- candidato e checksum são artefatos temporários até aprovação humana de publicação.

O owner autorizou expressamente o Inno Setup 6.7.3 em 2026-07-31. A licença permite o uso neste
projeto pessoal. Uma futura mudança de uso ou versão exige nova revisão de licença e cadeia de
suprimentos.

## Alternativas consideradas

- distribuir somente o diretório `onedir`: rejeitado por pior experiência de instalação;
- PyInstaller `onefile`: rejeitado inicialmente por extração temporária e diagnóstico mais difícil
  com Qt e FFmpeg;
- MSIX/WiX: adiados por aumentarem a infraestrutura e a complexidade de assinatura para este uso
  pessoal.

## Consequências

- o build precisa de uma versão exata e verificável do compilador Inno Setup;
- o instalador permanece sem Authenticode até decisão separada do owner;
- instalação/desinstalação em Windows 10 x64 limpo continua sendo gate de release, não evidência
  substituível pelo smoke do diretório empacotado;
- rollback da primeira versão significa retirar o candidato não publicado e desinstalá-lo sem
  remover saídas ou credenciais.
