# TASK-010 — Pacote Windows `onedir` e smoke test

## Objetivo

Produzir artefato PyInstaller `onedir` não publicado e provar que abre em ambiente Windows limpo sem Python externo.

## Contexto e fontes

TASK-009; ADR-0002; `release-target.md`; THIRD_PARTY; CA-010/T-08.

## Escopo de arquivos

Permitidos: spec PyInstaller, scripts de build/smoke, workflow de artefato e documentação de licenças. Proibidos: GitHub Release, assinatura, auto-update e secret no pacote.

## Restrições e autonomia

Risco moderado. Pode criar artefato local/CI temporário. Publicação, FFmpeg não aprovado e assinatura exigem gate humano.

## Critérios de aceitação

Build determinístico; app abre; imports/Qt/keyring funcionam; pacote não contém chave/log/mídia; licenças presentes; checksum gerado; smoke em Windows runner e VM Windows 10 planejada.

## Validação e evidência

`verify.cmd`, `audit.cmd`, inspeção do pacote, checksum e log do smoke sem conteúdo sensível.

## Rollback

Excluir artefatos locais/CI e reverter scripts; nenhuma release pública existe.

